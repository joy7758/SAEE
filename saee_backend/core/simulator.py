"""Deterministic simulation helpers for the SAEE MVP API shell.

This module intentionally avoids private SAEE kernel imports. It turns opaque
agent descriptors into reproducible public report-layer traces for product
evaluation development.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

from saee_backend.models.request import AgentConfig, EnvironmentConfig


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def stable_unit_float(payload: Any, salt: str) -> float:
    raw = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(f"{salt}:{raw}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def stable_id(prefix: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=True)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:16]}"


@dataclass(frozen=True)
class AgentTrace:
    agent_id: str
    run_index: int
    scores: list[float]
    alive: list[bool]
    collapse_step: int | None
    drift: list[float] | None = None
    risk: list[float] | None = None


@dataclass(frozen=True)
class AgentState:
    agent_id: str
    stability: float
    survival_score: float
    drift: float
    risk: float
    active: bool = True


def _descriptor_text(agent: AgentConfig) -> str:
    return json.dumps(agent.config, sort_keys=True, default=str, ensure_ascii=True).lower()


def _descriptor_adjustments(agent: AgentConfig) -> tuple[float, float, float]:
    text = _descriptor_text(agent)
    stable_terms = ["guard", "stable", "conservative", "monitor", "retry", "bounded", "safe"]
    risky_terms = ["risky", "unstable", "aggressive", "experimental", "fast", "unguarded", "fragile"]
    stability_bias = sum(term in text for term in stable_terms) * 0.035
    risk_bias = sum(term in text for term in risky_terms) * 0.04
    workflow_bias = 0.03 if agent.type == "workflow" else 0.0
    rule_bias = 0.015 if agent.type == "rule" else 0.0
    resilience_bonus = clamp(stability_bias + workflow_bias + rule_bias - risk_bias, -0.18, 0.18)
    volatility_bonus = clamp(risk_bias - stability_bias * 0.5, -0.08, 0.14)
    baseline_bonus = clamp((stability_bias * 0.5 + workflow_bias) - risk_bias * 0.35, -0.08, 0.12)
    return baseline_bonus, resilience_bonus, volatility_bonus


def _initial_state(agent: AgentConfig, environment: EnvironmentConfig, run_index: int) -> tuple[AgentState, float, float]:
    payload = {
        "agent_id": agent.agent_id,
        "config": agent.config,
        "type": agent.type,
        "scenario_type": environment.scenario_type,
        "run_index": run_index,
    }
    baseline_bonus, resilience_bonus, volatility_bonus = _descriptor_adjustments(agent)
    base = clamp(0.22 + 0.58 * stable_unit_float(payload, "base") + baseline_bonus)
    resilience = clamp(stable_unit_float(payload, "resilience") + resilience_bonus)
    volatility = clamp(
        0.025 + 0.085 * environment.noise_level + volatility_bonus,
        0.005,
        0.2,
    )
    return (
        AgentState(
            agent_id=agent.agent_id,
            stability=base,
            survival_score=1.0,
            drift=0.0,
            risk=clamp(0.08 + environment.noise_level * 0.18 + environment.competition_intensity * 0.14),
            active=True,
        ),
        resilience,
        volatility,
    )


def simulate_competition_run(
    agents: list[AgentConfig],
    environment: EnvironmentConfig,
    run_index: int = 0,
) -> dict[str, AgentTrace]:
    """Run one deterministic interaction loop across all agents.

    The loop is intentionally public-shell only: opaque descriptors become
    agent states, states interact through simple stability pressure, and traces
    are recorded for report-layer scoring.
    """

    horizon = min(environment.time_horizon, 1_000)
    if not agents:
        return {}

    state_by_agent: dict[str, AgentState] = {}
    resilience_by_agent: dict[str, float] = {}
    volatility_by_agent: dict[str, float] = {}
    phase_by_agent: dict[str, float] = {}
    initial_stability: dict[str, float] = {}
    scores: dict[str, list[float]] = {agent.agent_id: [] for agent in agents}
    alive: dict[str, list[bool]] = {agent.agent_id: [] for agent in agents}
    drift_series: dict[str, list[float]] = {agent.agent_id: [] for agent in agents}
    risk_series: dict[str, list[float]] = {agent.agent_id: [] for agent in agents}
    collapse_step: dict[str, int | None] = {agent.agent_id: None for agent in agents}

    for agent in agents:
        state, resilience, volatility = _initial_state(agent, environment, run_index)
        state_by_agent[agent.agent_id] = state
        resilience_by_agent[agent.agent_id] = resilience
        volatility_by_agent[agent.agent_id] = volatility
        phase_by_agent[agent.agent_id] = stable_unit_float(
            {
                "agent_id": agent.agent_id,
                "config": agent.config,
                "scenario_type": environment.scenario_type,
                "run_index": run_index,
            },
            "phase",
        ) * math.tau
        initial_stability[agent.agent_id] = state.stability

    stress = 0.55 * environment.noise_level + 0.45 * environment.competition_intensity
    denominator = max(horizon - 1, 1)
    for t in range(horizon):
        active_states = [state for state in state_by_agent.values() if state.active]
        active_mean = mean_state_stability(active_states)
        next_states: dict[str, AgentState] = {}
        for agent in agents:
            state = state_by_agent[agent.agent_id]
            if not state.active:
                scores[agent.agent_id].append(round(state.stability, 6))
                alive[agent.agent_id].append(False)
                drift_series[agent.agent_id].append(round(state.drift, 6))
                risk_series[agent.agent_id].append(round(state.risk, 6))
                next_states[agent.agent_id] = state
                continue

            progress = t / denominator
            resilience = resilience_by_agent[agent.agent_id]
            volatility = volatility_by_agent[agent.agent_id]
            competitive_gap = state.stability - active_mean
            reinforcement = max(competitive_gap, 0.0) * environment.competition_intensity * 0.022
            penalty = max(-competitive_gap, 0.0) * environment.competition_intensity * 0.045
            adaptation = (resilience - 0.5) * 0.011
            fatigue = stress * (0.006 + progress * 0.006)
            wave = math.sin(phase_by_agent[agent.agent_id] + t * 0.37) * volatility * 0.055
            new_stability = clamp(state.stability + adaptation + reinforcement - penalty - fatigue + wave)
            new_drift = clamp(abs(new_stability - initial_stability[agent.agent_id]), 0.0, 1.0)
            risk_delta = stress * 0.012 + max(0.0, 0.48 - new_stability) * 0.045 + new_drift * 0.01
            risk_recovery = max(resilience - 0.62, 0.0) * 0.016 + max(competitive_gap, 0.0) * 0.008
            new_risk = clamp(state.risk + risk_delta - risk_recovery)
            collapse_threshold = 0.12 + 0.11 * environment.competition_intensity + 0.05 * environment.noise_level
            risk_threshold = 0.78 - min(resilience * 0.12, 0.08)
            active = new_stability > collapse_threshold and new_risk < risk_threshold
            if not active and collapse_step[agent.agent_id] is None:
                collapse_step[agent.agent_id] = t
            new_survival = (sum(alive[agent.agent_id]) + int(active)) / (t + 1)
            next_state = AgentState(
                agent_id=agent.agent_id,
                stability=new_stability,
                survival_score=new_survival,
                drift=new_drift,
                risk=new_risk,
                active=active,
            )
            scores[agent.agent_id].append(round(new_stability, 6))
            alive[agent.agent_id].append(active)
            drift_series[agent.agent_id].append(round(new_drift, 6))
            risk_series[agent.agent_id].append(round(new_risk, 6))
            next_states[agent.agent_id] = next_state
        state_by_agent = next_states

    return {
        agent.agent_id: AgentTrace(
            agent_id=agent.agent_id,
            run_index=run_index,
            scores=scores[agent.agent_id],
            alive=alive[agent.agent_id],
            collapse_step=collapse_step[agent.agent_id],
            drift=drift_series[agent.agent_id],
            risk=risk_series[agent.agent_id],
        )
        for agent in agents
    }


def mean_state_stability(states: list[AgentState]) -> float:
    if not states:
        return 0.0
    return sum(state.stability for state in states) / len(states)


def simulate_competition_runs(
    agents: list[AgentConfig],
    environment: EnvironmentConfig,
    repeat_runs: int,
) -> dict[str, list[AgentTrace]]:
    traces_by_agent: dict[str, list[AgentTrace]] = {agent.agent_id: [] for agent in agents}
    for run_index in range(repeat_runs):
        run_traces = simulate_competition_run(agents, environment, run_index)
        for agent_id, trace in run_traces.items():
            traces_by_agent[agent_id].append(trace)
    return traces_by_agent


def simulate_agent(agent: AgentConfig, environment: EnvironmentConfig, run_index: int = 0) -> AgentTrace:
    horizon = min(environment.time_horizon, 1_000)
    payload = {
        "agent_id": agent.agent_id,
        "config": agent.config,
        "type": agent.type,
        "scenario_type": environment.scenario_type,
        "run_index": run_index,
    }
    baseline_bonus, resilience_bonus, volatility_bonus = _descriptor_adjustments(agent)
    base = clamp(0.22 + 0.58 * stable_unit_float(payload, "base") + baseline_bonus)
    resilience = clamp(stable_unit_float(payload, "resilience") + resilience_bonus)
    phase = stable_unit_float(payload, "phase") * math.tau
    stress = 0.55 * environment.noise_level + 0.45 * environment.competition_intensity
    run_pressure = (stable_unit_float(payload, "pressure") - 0.5) * 0.08
    slope = (resilience - 0.5) * 0.38 - stress * 0.24 + run_pressure
    oscillation_size = clamp(0.025 + 0.085 * environment.noise_level + volatility_bonus, 0.005, 0.2)
    collapse_threshold = 0.16 + 0.10 * environment.competition_intensity + 0.05 * environment.noise_level

    scores: list[float] = []
    alive: list[bool] = []
    collapsed = False
    collapse_step: int | None = None
    denominator = max(horizon - 1, 1)
    for t in range(horizon):
        progress = t / denominator
        oscillation = math.sin(phase + progress * math.tau * 3.0) * oscillation_size
        short_cycle = math.sin(phase * 0.5 + progress * math.tau * 11.0) * oscillation_size * 0.25
        fatigue = stress * progress * (0.15 + (1.0 - resilience) * 0.16)
        recovery = max(resilience - 0.62, 0.0) * progress * 0.12
        score = clamp(base + slope * progress + oscillation + short_cycle - fatigue + recovery)
        if not collapsed and score < collapse_threshold:
            collapsed = True
            collapse_step = t
        scores.append(round(score, 6))
        alive.append(not collapsed)
    return AgentTrace(
        agent_id=agent.agent_id,
        run_index=run_index,
        scores=scores,
        alive=alive,
        collapse_step=collapse_step,
    )


def simulate_agent_runs(
    agent: AgentConfig,
    environment: EnvironmentConfig,
    repeat_runs: int,
) -> list[AgentTrace]:
    return [simulate_agent(agent, environment, run_index=index) for index in range(repeat_runs)]
