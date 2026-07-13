"""Minimal local parasitic phase simulation.

The model is intentionally synthetic and standard-library only. It generates a
small multi-agent ecology where mutating lineages can drift toward local
resource extraction and where governance can delay or suppress the local Phi
threshold crossing. Outputs are local evidence surfaces, not external
validation or universal-law proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
import math
from pathlib import Path
import random
from typing import Any


REWARD_DRIFT_NORMALIZER = 0.34
REPLICATION_RATE_LEVELS = {
    "low": 0.65,
    "medium": 1.0,
    "high": 1.35,
}
CONSTRAINT_STRENGTH_LEVELS = {
    0.0: "none",
    0.5: "weak",
    1.0: "strong",
}
MUTATION_RATE_LEVELS = [0.0, 0.1, 0.3]
STATISTICAL_SEED_MINIMUM = 30


@dataclass(frozen=True)
class RewardVector:
    global_weight: float
    local_weight: float
    drift_weight: float = 0.0

    def normalized(self) -> "RewardVector":
        total = self.global_weight + self.local_weight + self.drift_weight
        if total <= 0:
            return RewardVector(0.0, 1.0, 0.0)
        return RewardVector(
            self.global_weight / total,
            self.local_weight / total,
            self.drift_weight / total,
        )

    def drift_from(self, baseline: "RewardVector") -> float:
        current = self.normalized()
        base = baseline.normalized()
        return min(
            1.0,
            (
                abs(current.global_weight - base.global_weight)
                + abs(current.local_weight - base.local_weight)
                + abs(current.drift_weight - base.drift_weight)
            )
            / 2.0,
        )

    def to_dict(self) -> dict[str, float]:
        item = self.normalized()
        return {
            "global_weight": round(item.global_weight, 6),
            "local_weight": round(item.local_weight, 6),
            "drift_weight": round(item.drift_weight, 6),
        }


BASELINE_REWARD: dict[str, RewardVector] = {
    "cooperative": RewardVector(0.82, 0.18, 0.0),
    "selfish": RewardVector(0.22, 0.78, 0.0),
    "mutating": RewardVector(0.34, 0.54, 0.12),
}


@dataclass
class Agent:
    agent_id: str
    agent_type: str
    lineage_id: str
    resources: float
    reward: RewardVector
    age: int = 0
    mutation_count: int = 0
    parent_id: str | None = None


@dataclass(frozen=True)
class GovernanceConfig:
    name: str
    replication_cap: int | None
    monopolization_threshold: float
    monopolization_penalty: float
    reward_drift_damping: float


GOVERNANCE: dict[str, GovernanceConfig] = {
    "none": GovernanceConfig(
        name="none",
        replication_cap=None,
        monopolization_threshold=1.0,
        monopolization_penalty=0.0,
        reward_drift_damping=0.0,
    ),
    "weak": GovernanceConfig(
        name="weak",
        replication_cap=2,
        monopolization_threshold=0.26,
        monopolization_penalty=0.24,
        reward_drift_damping=0.38,
    ),
    "strong": GovernanceConfig(
        name="strong",
        replication_cap=2,
        monopolization_threshold=0.20,
        monopolization_penalty=0.60,
        reward_drift_damping=0.985,
    ),
}


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    governance: str
    steps: int = 160
    seed: int = 41
    initial_resource_pool: float = 100.0
    max_resource_pool: float = 110.0
    replenish_rate: float = 6.0
    survival_cost: float = 1.0
    replication_threshold: float = 8.4
    replication_rate: float = 1.0
    initial_agent_resources: float = 5.0
    base_claim: float = 2.4
    mutation_rate: float = 0.058
    phi_threshold: float = 0.60
    transition_slope_threshold: float = 0.0
    max_agents: int = 220
    phi_weights: tuple[float, float, float] = (0.35, 0.35, 0.30)


@dataclass
class SimulationResult:
    config: ExperimentConfig
    metrics: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    phase_transition_step: int | None
    transition_event: dict[str, Any] | None = None

    def summary(self) -> dict[str, Any]:
        final = self.metrics[-1] if self.metrics else {}
        return {
            "schema": "saee.parasitic_phase.result_summary.v1",
            "experiment_id": self.config.experiment_id,
            "governance": self.config.governance,
            "steps": self.config.steps,
            "seed": self.config.seed,
            "replication_rate": self.config.replication_rate,
            "mutation_rate": self.config.mutation_rate,
            "phi_threshold": self.config.phi_threshold,
            "transition_slope_threshold": self.config.transition_slope_threshold,
            "phi_bounds": [0.0, 1.0],
            "phi_normalized": True,
            "phase_transition_step": self.phase_transition_step,
            "transition_event": self.transition_event,
            "final_phi": final.get("phi", 0.0),
            "final_entropy": final.get("entropy", 0.0),
            "final_agent_dominance": final.get("agent_dominance", 0.0),
            "final_resource_concentration": final.get("resource_concentration", 0.0),
            "final_reward_drift": final.get("reward_drift", 0.0),
            "final_phi_components": final.get("phi_components"),
            "final_population": final.get("population", 0),
            "dominant_lineage_type": final.get("dominant_lineage_type"),
            "local_only": True,
            "standard_library_only": True,
            "external_validation_claim": False,
            "production_claim": False,
        }


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def gini(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(max(0.0, value) for value in values)
    total = sum(sorted_values)
    if total <= 0:
        return 0.0
    count = len(sorted_values)
    weighted = sum((index + 1) * value for index, value in enumerate(sorted_values))
    return clamp((2.0 * weighted) / (count * total) - (count + 1.0) / count)


def normalized_entropy(weight_by_lineage: dict[str, float]) -> float:
    total = sum(max(0.0, value) for value in weight_by_lineage.values())
    if total <= 0 or len(weight_by_lineage) <= 1:
        return 0.0
    entropy = 0.0
    for value in weight_by_lineage.values():
        probability = max(0.0, value) / total
        if probability > 0:
            entropy -= probability * math.log(probability)
    return clamp(entropy / math.log(len(weight_by_lineage)))


def normalized_phi_weights(weights: tuple[float, float, float]) -> tuple[float, float, float]:
    positive = tuple(max(0.0, value) for value in weights)
    total = sum(positive)
    if total <= 0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return (positive[0] / total, positive[1] / total, positive[2] / total)


def phi_component_payload(
    resource_concentration: float,
    reward_drift: float,
    agent_dominance: float,
    weights: tuple[float, float, float],
) -> dict[str, Any]:
    w_resource, w_reward, w_dominance = normalized_phi_weights(weights)
    components = {
        "resource_concentration": clamp(resource_concentration),
        "reward_drift": clamp(reward_drift),
        "agent_dominance": clamp(agent_dominance),
    }
    weighted = {
        "resource_concentration": w_resource * components["resource_concentration"],
        "reward_drift": w_reward * components["reward_drift"],
        "agent_dominance": w_dominance * components["agent_dominance"],
    }
    return {
        "normalized": True,
        "phi_bounds": [0.0, 1.0],
        "components": {key: round(value, 6) for key, value in components.items()},
        "weights": {
            "resource_concentration": round(w_resource, 6),
            "reward_drift": round(w_reward, 6),
            "agent_dominance": round(w_dominance, 6),
        },
        "weighted_contributions": {
            key: round(value, 6) for key, value in weighted.items()
        },
        "normalization": {
            "resource_concentration": "gini_coefficient_clamped_to_0_1",
            "reward_drift": f"mean_reward_distance_divided_by_{REWARD_DRIFT_NORMALIZER}_clamped_to_0_1",
            "agent_dominance": "max_lineage_population_or_resource_share_clamped_to_0_1",
        },
    }


def phi_from_payload(payload: dict[str, Any]) -> float:
    return clamp(sum(float(value) for value in payload["weighted_contributions"].values()))


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _sample_variance(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    average = sum(values) / len(values)
    return sum((value - average) ** 2 for value in values) / (len(values) - 1)


def _confidence_interval_95(values: list[float]) -> dict[str, float] | None:
    average = _mean(values)
    variance = _sample_variance(values)
    if average is None or variance is None:
        return None
    half_width = 1.96 * math.sqrt(variance) / math.sqrt(len(values))
    return {
        "low": round(average - half_width, 6),
        "high": round(average + half_width, 6),
    }


def _clone_config(config: ExperimentConfig, **overrides: Any) -> ExperimentConfig:
    config_data = asdict(config)
    config_data.update(overrides)
    return ExperimentConfig(**config_data)


class ParasiticPhaseSimulation:
    def __init__(self, config: ExperimentConfig) -> None:
        if config.governance not in GOVERNANCE:
            raise ValueError(f"unknown governance preset: {config.governance}")
        self.config = config
        self.governance = GOVERNANCE[config.governance]
        self.random = random.Random(config.seed)
        self.resource_pool = config.initial_resource_pool
        self.agents = self._initial_agents()
        self.next_agent_number = len(self.agents) + 1
        self.previous_phi: float | None = None
        self.previous_entropy: float | None = None
        self.phase_transition_step: int | None = None
        self.transition_event: dict[str, Any] | None = None

    def run(self) -> SimulationResult:
        metrics: list[dict[str, Any]] = []
        trace: list[dict[str, Any]] = []
        for timestep in range(self.config.steps):
            record = self.step(timestep)
            trace.append(record)
            metrics.append(record["metrics"])
        return SimulationResult(
            config=self.config,
            metrics=metrics,
            trace=trace,
            phase_transition_step=self.phase_transition_step,
            transition_event=self.transition_event,
        )

    def step(self, timestep: int) -> dict[str, Any]:
        replenished = self._replenish()
        agent_actions: list[dict[str, Any]] = []
        allocations: list[dict[str, Any]] = []
        reward_updates: list[dict[str, Any]] = []
        governance_actions: list[dict[str, Any]] = []
        events: list[dict[str, Any]] = []

        total_agent_resources = sum(max(0.0, agent.resources) for agent in self.agents)
        claims: list[tuple[Agent, float]] = []
        for agent in self.agents:
            raw_claim = self._claim(agent)
            resource_share = agent.resources / total_agent_resources if total_agent_resources > 0 else 0.0
            claim = raw_claim
            if (
                self.governance.name != "none"
                and resource_share > self.governance.monopolization_threshold
            ):
                claim *= 1.0 - self.governance.monopolization_penalty
                governance_actions.append(
                    {
                        "type": "monopolization_penalty",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "resource_share": round(resource_share, 6),
                        "claim_before": round(raw_claim, 6),
                        "claim_after": round(claim, 6),
                    }
                )
            claims.append((agent, claim))
            agent_actions.append(
                {
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "lineage_id": agent.lineage_id,
                    "resource_before": round(agent.resources, 6),
                    "claim": round(claim, 6),
                    "raw_claim": round(raw_claim, 6),
                }
            )

        total_claim = sum(claim for _, claim in claims)
        allocated_budget = self._withdraw(total_claim)
        for agent, claim in claims:
            allocated = allocated_budget * claim / total_claim if total_claim > 0 else 0.0
            agent.resources += allocated
            allocations.append(
                {
                    "agent_id": agent.agent_id,
                    "lineage_id": agent.lineage_id,
                    "allocated": round(allocated, 6),
                }
            )

        survivors = []
        for agent in self.agents:
            agent.resources -= self._survival_cost(agent)
            agent.age += 1
            if agent.resources > 0.0:
                survivors.append(agent)
            else:
                events.append(
                    {
                        "type": "agent_extinction",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                    }
                )
        self.agents = survivors

        for agent in list(self.agents):
            update = self._mutate_reward(agent, governance_actions)
            if update:
                reward_updates.append(update)

        for agent in list(self.agents):
            children, replication_actions = self._replicate(agent)
            self.agents.extend(children)
            governance_actions.extend(replication_actions)

        metrics = self._metrics()
        if (
            self.phase_transition_step is None
            and metrics["phi"] > self.config.phi_threshold
            and metrics["delta_phi"] > self.config.transition_slope_threshold
        ):
            self.phase_transition_step = timestep
            self.transition_event = {
                "type": "transition_event",
                "phase": "parasitic_phase",
                "timestep": timestep,
                "phi": metrics["phi"],
                "phi_threshold": self.config.phi_threshold,
                "transition_slope": metrics["delta_phi"],
                "slope_threshold": self.config.transition_slope_threshold,
                "pre_transition_entropy": (
                    metrics["entropy"]
                    if self.previous_entropy is None
                    else self.previous_entropy
                ),
                "detector": "phi_above_phi_c_and_positive_slope",
                "rule": "phi > phi_threshold and delta_phi > transition_slope_threshold",
            }
            events.append(self.transition_event)
        if metrics["agent_dominance"] > 0.70:
            events.append(
                {
                    "type": "dominant_lineage_above_70_percent",
                    "lineage_id": metrics["dominant_lineage_id"],
                    "dominance": metrics["agent_dominance"],
                }
            )
        if metrics["entropy"] < 0.18 and metrics["population"] > 8:
            events.append({"type": "entropy_collapse", "entropy": metrics["entropy"]})

        self.previous_phi = metrics["phi"]
        self.previous_entropy = metrics["entropy"]
        return {
            "timestep": timestep,
            "environment": {
                "resource_pool": round(self.resource_pool, 6),
                "replenished": round(replenished, 6),
            },
            "agent_actions": agent_actions,
            "resource_allocations": allocations,
            "reward_updates": reward_updates,
            "metrics": metrics,
            "governance_actions": governance_actions,
            "events": events,
        }

    def _initial_agents(self) -> list[Agent]:
        agents: list[Agent] = []
        counts = [("cooperative", 8), ("selfish", 5), ("mutating", 3)]
        number = 1
        for agent_type, count in counts:
            for _ in range(count):
                agent_id = f"pp-{number:04d}"
                agents.append(
                    Agent(
                        agent_id=agent_id,
                        agent_type=agent_type,
                        lineage_id=agent_id,
                        resources=self.config.initial_agent_resources,
                        reward=BASELINE_REWARD[agent_type],
                    )
                )
                number += 1
        return agents

    def _replenish(self) -> float:
        before = self.resource_pool
        self.resource_pool = min(
            self.config.max_resource_pool,
            self.resource_pool + self.config.replenish_rate,
        )
        return self.resource_pool - before

    def _withdraw(self, amount: float) -> float:
        actual = min(self.resource_pool, max(0.0, amount))
        self.resource_pool -= actual
        return actual

    def _claim(self, agent: Agent) -> float:
        reward = agent.reward.normalized()
        jitter = self.random.uniform(0.96, 1.04)
        if agent.agent_type == "cooperative":
            multiplier = 0.66 + 0.18 * reward.local_weight
        elif agent.agent_type == "selfish":
            multiplier = 1.18 + 0.78 * reward.local_weight
        else:
            multiplier = 1.30 + 1.28 * reward.local_weight + 0.48 * reward.drift_weight
            multiplier += min(1.05, agent.mutation_count * 0.035)
        return max(0.05, self.config.base_claim * multiplier * jitter)

    def _survival_cost(self, agent: Agent) -> float:
        if agent.agent_type == "cooperative":
            return self.config.survival_cost * 0.92
        if agent.agent_type == "selfish":
            return self.config.survival_cost * 1.03
        return self.config.survival_cost * 1.08

    def _mutate_reward(
        self,
        agent: Agent,
        governance_actions: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if agent.agent_type != "mutating":
            return None
        before = agent.reward.normalized()
        pressure = 1.0 + min(1.6, agent.resources / (self.config.replication_threshold * 1.8))
        raw_delta = self.config.mutation_rate * pressure
        delta = raw_delta * (1.0 - self.governance.reward_drift_damping)
        if delta <= 0.0:
            return None
        if self.governance.reward_drift_damping > 0:
            governance_actions.append(
                {
                    "type": "reward_drift_damping",
                    "agent_id": agent.agent_id,
                    "lineage_id": agent.lineage_id,
                    "raw_delta": round(raw_delta, 6),
                    "damped_delta": round(delta, 6),
                }
            )
        agent.reward = RewardVector(
            global_weight=max(0.01, before.global_weight - delta * 0.80),
            local_weight=before.local_weight + delta,
            drift_weight=before.drift_weight + delta * 0.52,
        ).normalized()
        agent.mutation_count += 1
        return {
            "agent_id": agent.agent_id,
            "lineage_id": agent.lineage_id,
            "reward_before": before.to_dict(),
            "reward_after": agent.reward.to_dict(),
            "mutation_delta": round(delta, 6),
            "mutation_count": agent.mutation_count,
        }

    def _replicate(self, agent: Agent) -> tuple[list[Agent], list[dict[str, Any]]]:
        if agent.resources <= self.config.replication_threshold:
            return [], []
        if len(self.agents) >= self.config.max_agents:
            return [], []

        excess = agent.resources - self.config.replication_threshold
        pressure = max(0.0, excess / self.config.replication_threshold)
        if agent.agent_type == "cooperative":
            desired = 1 if pressure > 0.95 and self.random.random() < 0.35 else 0
        elif agent.agent_type == "selfish":
            desired = 1 + int(pressure * 0.95)
        else:
            desired = 1 + int(pressure * 1.9 + agent.reward.local_weight + agent.reward.drift_weight)

        replication_rate = max(0.0, self.config.replication_rate)
        if desired > 0 and replication_rate != 1.0:
            scaled_desired = desired * replication_rate
            desired = int(scaled_desired)
            if self.random.random() < scaled_desired - desired:
                desired += 1

        allowed = desired
        actions: list[dict[str, Any]] = []
        if self.governance.replication_cap is not None:
            allowed = min(desired, self.governance.replication_cap)
            if allowed < desired:
                actions.append(
                    {
                        "type": "replication_cap",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "desired_children": desired,
                        "allowed_children": allowed,
                    }
                )
        allowed = max(0, min(allowed, self.config.max_agents - len(self.agents)))
        children: list[Agent] = []
        for _ in range(allowed):
            child_resources = min(agent.resources * 0.33, self.config.replication_threshold * 0.68)
            if child_resources <= 0.1:
                break
            agent.resources -= child_resources
            child_id = f"pp-{self.next_agent_number:04d}"
            self.next_agent_number += 1
            children.append(
                Agent(
                    agent_id=child_id,
                    agent_type=agent.agent_type,
                    lineage_id=agent.lineage_id,
                    resources=child_resources,
                    reward=agent.reward,
                    age=0,
                    mutation_count=agent.mutation_count,
                    parent_id=agent.agent_id,
                )
            )
            actions.append(
                {
                    "type": "replication",
                    "parent_id": agent.agent_id,
                    "child_id": child_id,
                    "lineage_id": agent.lineage_id,
                    "child_resources": round(child_resources, 6),
                }
            )
        return children, actions

    def _metrics(self) -> dict[str, Any]:
        resource_values = [agent.resources for agent in self.agents]
        lineage_counts: dict[str, int] = {}
        lineage_resources: dict[str, float] = {}
        lineage_type: dict[str, str] = {}
        drift_values = []
        for agent in self.agents:
            lineage_counts[agent.lineage_id] = lineage_counts.get(agent.lineage_id, 0) + 1
            lineage_resources[agent.lineage_id] = lineage_resources.get(agent.lineage_id, 0.0) + max(0.0, agent.resources)
            lineage_type.setdefault(agent.lineage_id, agent.agent_type)
            drift_values.append(agent.reward.drift_from(BASELINE_REWARD[agent.agent_type]))

        population = len(self.agents)
        total_resources = sum(lineage_resources.values())
        dominant_lineage = None
        dominance = 0.0
        dominant_count = 0
        for lineage_id, count in lineage_counts.items():
            count_share = count / population if population else 0.0
            resource_share = lineage_resources.get(lineage_id, 0.0) / total_resources if total_resources > 0 else 0.0
            lineage_dominance = max(count_share, resource_share)
            if lineage_dominance > dominance:
                dominance = lineage_dominance
                dominant_lineage = lineage_id
                dominant_count = count
        resource_concentration = clamp(gini(resource_values))
        raw_reward_drift = sum(drift_values) / len(drift_values) if drift_values else 0.0
        reward_drift = clamp(raw_reward_drift / REWARD_DRIFT_NORMALIZER)
        entropy = normalized_entropy(lineage_resources)
        dominance = clamp(dominance)
        phi_components = phi_component_payload(
            resource_concentration=resource_concentration,
            reward_drift=reward_drift,
            agent_dominance=dominance,
            weights=self.config.phi_weights,
        )
        phi = phi_from_payload(phi_components)
        delta_phi = 0.0 if self.previous_phi is None else phi - self.previous_phi
        type_counts: dict[str, int] = {}
        for agent in self.agents:
            type_counts[agent.agent_type] = type_counts.get(agent.agent_type, 0) + 1
        weighted_contributions = phi_components["weighted_contributions"]
        return {
            "population": population,
            "resource_concentration": round(resource_concentration, 6),
            "resource_gini": round(resource_concentration, 6),
            "reward_drift": round(reward_drift, 6),
            "agent_dominance": round(dominance, 6),
            "phi_components": phi_components,
            "phi_resource_contribution": weighted_contributions["resource_concentration"],
            "phi_reward_drift_contribution": weighted_contributions["reward_drift"],
            "phi_dominance_contribution": weighted_contributions["agent_dominance"],
            "dominant_lineage_id": dominant_lineage,
            "dominant_lineage_type": lineage_type.get(dominant_lineage or ""),
            "dominant_lineage_count": dominant_count,
            "entropy": round(entropy, 6),
            "phi": round(phi, 6),
            "delta_phi": round(delta_phi, 6),
            "type_counts": dict(sorted(type_counts.items())),
        }


EXPERIMENTS = [
    ExperimentConfig(
        experiment_id="A_no_governance",
        governance="none",
    ),
    ExperimentConfig(
        experiment_id="B_weak_governance",
        governance="weak",
    ),
    ExperimentConfig(
        experiment_id="C_strong_governance",
        governance="strong",
    ),
]


def run_experiment_set(steps: int = 160, seed: int | None = None) -> list[SimulationResult]:
    results: list[SimulationResult] = []
    for config in EXPERIMENTS:
        overrides: dict[str, Any] = {"steps": steps}
        if seed is not None:
            overrides["seed"] = seed
        results.append(ParasiticPhaseSimulation(_clone_config(config, **overrides)).run())
    return results


def run_statistical_robustness(
    steps: int = 160,
    seed_count: int = STATISTICAL_SEED_MINIMUM,
    seed_start: int = 4100,
) -> dict[str, Any]:
    if seed_count < STATISTICAL_SEED_MINIMUM:
        raise ValueError(f"seed_count must be at least {STATISTICAL_SEED_MINIMUM}")

    experiment_summaries: dict[str, Any] = {}
    for config in EXPERIMENTS:
        seed_runs = []
        transition_steps: list[float] = []
        final_phi_values: list[float] = []
        for offset in range(seed_count):
            seed = seed_start + offset
            result = ParasiticPhaseSimulation(
                _clone_config(config, steps=steps, seed=seed)
            ).run()
            final_metric = result.metrics[-1] if result.metrics else {}
            final_phi = float(final_metric.get("phi", 0.0))
            final_phi_values.append(final_phi)
            if result.phase_transition_step is not None:
                transition_steps.append(float(result.phase_transition_step))
            seed_runs.append(
                {
                    "seed": seed,
                    "phase_transition_step": result.phase_transition_step,
                    "transition_event": result.transition_event,
                    "final_phi": final_phi,
                    "final_entropy": final_metric.get("entropy", 0.0),
                    "final_agent_dominance": final_metric.get("agent_dominance", 0.0),
                }
            )

        observed_count = len(transition_steps)
        experiment_summaries[config.experiment_id] = {
            "experiment_id": config.experiment_id,
            "governance": config.governance,
            "sample_size": seed_count,
            "transition_count": observed_count,
            "non_transition_count": seed_count - observed_count,
            "transition_rate": round(observed_count / seed_count, 6),
            "mean_phase_transition_step": (
                None if _mean(transition_steps) is None else round(_mean(transition_steps) or 0.0, 6)
            ),
            "phase_transition_step_variance": (
                None
                if _sample_variance(transition_steps) is None
                else round(_sample_variance(transition_steps) or 0.0, 6)
            ),
            "phase_transition_step_ci_95": _confidence_interval_95(transition_steps),
            "mean_final_phi": (
                None if _mean(final_phi_values) is None else round(_mean(final_phi_values) or 0.0, 6)
            ),
            "final_phi_variance": (
                None
                if _sample_variance(final_phi_values) is None
                else round(_sample_variance(final_phi_values) or 0.0, 6)
            ),
            "seed_runs": seed_runs,
            "non_transition_mean_policy": "mean_phase_transition_step_uses_observed_transitions_only",
        }

    return {
        "schema": "saee.parasitic_phase.statistical_summary.v1",
        "local_only": True,
        "synthetic_experiment": True,
        "external_validation_claim": False,
        "production_claim": False,
        "steps": steps,
        "seed_count_per_experiment": seed_count,
        "seed_start": seed_start,
        "phi_bounds": [0.0, 1.0],
        "experiments": experiment_summaries,
    }


def run_parameter_sweep(steps: int = 160, seed: int = 9100) -> dict[str, Any]:
    runs = []
    for replication_label, replication_rate in REPLICATION_RATE_LEVELS.items():
        for constraint_strength, governance in CONSTRAINT_STRENGTH_LEVELS.items():
            for mutation_rate in MUTATION_RATE_LEVELS:
                experiment_id = (
                    "sweep_"
                    f"replication_{replication_label}_"
                    f"constraint_{str(constraint_strength).replace('.', '_')}_"
                    f"mutation_{str(mutation_rate).replace('.', '_')}"
                )
                config = ExperimentConfig(
                    experiment_id=experiment_id,
                    governance=governance,
                    steps=steps,
                    seed=seed,
                    replication_rate=replication_rate,
                    mutation_rate=mutation_rate,
                )
                result = ParasiticPhaseSimulation(config).run()
                final = result.metrics[-1] if result.metrics else {}
                runs.append(
                    {
                        "experiment_id": experiment_id,
                        "replication_rate_label": replication_label,
                        "replication_rate": replication_rate,
                        "constraint_strength": constraint_strength,
                        "governance": governance,
                        "mutation_rate": mutation_rate,
                        "phase_transition_step": result.phase_transition_step,
                        "transition_event": result.transition_event,
                        "final_phi": final.get("phi", 0.0),
                        "final_entropy": final.get("entropy", 0.0),
                        "final_agent_dominance": final.get("agent_dominance", 0.0),
                        "final_resource_concentration": final.get("resource_concentration", 0.0),
                        "final_reward_drift": final.get("reward_drift", 0.0),
                    }
                )

    return {
        "schema": "saee.parasitic_phase.parameter_phase_map.v1",
        "local_only": True,
        "synthetic_experiment": True,
        "external_validation_claim": False,
        "production_claim": False,
        "steps": steps,
        "seed": seed,
        "replication_rate_levels": REPLICATION_RATE_LEVELS,
        "constraint_strength_levels": {
            str(key): value for key, value in CONSTRAINT_STRENGTH_LEVELS.items()
        },
        "mutation_rate_levels": MUTATION_RATE_LEVELS,
        "runs": runs,
    }


def _summarize_agent_actions(actions: list[dict[str, Any]]) -> dict[str, Any]:
    top_claims = sorted(
        actions,
        key=lambda item: float(item.get("claim", 0.0)),
        reverse=True,
    )[:5]
    claim_total = sum(float(item.get("claim", 0.0)) for item in actions)
    return {
        "action_count": len(actions),
        "total_claim": round(claim_total, 6),
        "top_claim_agents": [
            {
                "agent_id": item.get("agent_id"),
                "lineage_id": item.get("lineage_id"),
                "agent_type": item.get("agent_type"),
                "claim": item.get("claim", 0.0),
                "raw_claim": item.get("raw_claim", 0.0),
            }
            for item in top_claims
        ],
    }


def _summarize_reward_updates(updates: list[dict[str, Any]]) -> dict[str, Any]:
    total_delta = sum(float(item.get("mutation_delta", 0.0)) for item in updates)
    lineage_delta: dict[str, float] = {}
    for item in updates:
        lineage_id = str(item.get("lineage_id"))
        lineage_delta[lineage_id] = lineage_delta.get(lineage_id, 0.0) + float(
            item.get("mutation_delta", 0.0)
        )
    return {
        "update_count": len(updates),
        "total_mutation_delta": round(total_delta, 6),
        "lineage_delta": {
            key: round(value, 6) for key, value in sorted(lineage_delta.items())
        },
        "mutation_events": [
            {
                "agent_id": item.get("agent_id"),
                "lineage_id": item.get("lineage_id"),
                "mutation_delta": item.get("mutation_delta", 0.0),
                "mutation_count": item.get("mutation_count", 0),
            }
            for item in updates[:20]
        ],
        "truncated": len(updates) > 20,
    }


def build_causal_phi_graph(results: list[SimulationResult]) -> dict[str, Any]:
    graph: dict[str, Any] = {
        "schema": "saee.parasitic_phase.causal_phi_graph.v1",
        "local_only": True,
        "synthetic_experiment": True,
        "external_validation_claim": False,
        "production_claim": False,
        "description": "Timestep alignment of agent actions, reward changes, governance actions, and bounded phi contributions.",
        "experiments": {},
    }
    for result in results:
        nodes = []
        edges = []
        timesteps = []
        for record in result.trace:
            timestep = int(record["timestep"])
            action_node = f"{result.config.experiment_id}:t{timestep}:agent_actions"
            reward_node = f"{result.config.experiment_id}:t{timestep}:reward_updates"
            governance_node = f"{result.config.experiment_id}:t{timestep}:governance_actions"
            phi_node = f"{result.config.experiment_id}:t{timestep}:phi_components"
            metrics = record["metrics"]
            nodes.extend(
                [
                    {"id": action_node, "type": "agent_action_summary", "timestep": timestep},
                    {"id": reward_node, "type": "reward_change_summary", "timestep": timestep},
                    {"id": governance_node, "type": "governance_action_summary", "timestep": timestep},
                    {"id": phi_node, "type": "phi_contribution", "timestep": timestep},
                ]
            )
            edges.extend(
                [
                    {
                        "source": action_node,
                        "target": phi_node,
                        "relationship": "resource_claims_affect_resource_concentration_and_dominance",
                    },
                    {
                        "source": reward_node,
                        "target": phi_node,
                        "relationship": "reward_mutation_affects_reward_drift_contribution",
                    },
                    {
                        "source": governance_node,
                        "target": action_node,
                        "relationship": "governance_modulates_claims_replication_or_reward_drift",
                    },
                ]
            )
            timesteps.append(
                {
                    "timestep": timestep,
                    "node_ids": {
                        "agent_actions": action_node,
                        "reward_updates": reward_node,
                        "governance_actions": governance_node,
                        "phi_components": phi_node,
                    },
                    "agent_action": _summarize_agent_actions(record["agent_actions"]),
                    "reward_change": _summarize_reward_updates(record["reward_updates"]),
                    "governance_action_count": len(record["governance_actions"]),
                    "phi": metrics["phi"],
                    "delta_phi": metrics["delta_phi"],
                    "phi_contribution": metrics["phi_components"]["weighted_contributions"],
                    "phi_components": metrics["phi_components"]["components"],
                    "entropy": metrics["entropy"],
                    "agent_dominance": metrics["agent_dominance"],
                    "events": record["events"],
                }
            )
        graph["experiments"][result.config.experiment_id] = {
            "summary": result.summary(),
            "nodes": nodes,
            "edges": edges,
            "timesteps": timesteps,
        }
    return graph


def scientific_closure_manifest(
    output_dir: Path,
    results: list[SimulationResult],
    statistical_seed_count: int,
) -> dict[str, Any]:
    return {
        "schema": "saee.parasitic_phase.scientific_closure_manifest.v1",
        "local_only": True,
        "synthetic_experiment": True,
        "external_validation_claim": False,
        "production_claim": False,
        "architecture_scope": "saee_v1_2/parasitic_phase_only",
        "phi_definition": {
            "formula": "phi = weighted_resource_concentration + weighted_reward_drift + weighted_agent_dominance",
            "bounds": [0.0, 1.0],
            "components_normalized": True,
        },
        "transition_detector": {
            "rule": "phi > phi_threshold and delta_phi > transition_slope_threshold",
            "stores": [
                "first_transition_timestamp",
                "transition_slope",
                "pre_transition_entropy",
            ],
        },
        "statistical_seed_count_per_experiment": statistical_seed_count,
        "experiments": [result.summary() for result in results],
        "outputs": {
            "summary_json": str(output_dir / "summary.json"),
            "statistical_summary_json": str(output_dir / "statistical_summary.json"),
            "parameter_phase_map_json": str(output_dir / "parameter_phase_map.json"),
            "causal_phi_graph_json": str(output_dir / "causal_phi_graph.json"),
            "visualization_svg": str(output_dir / "parasitic_phase_curves.svg"),
        },
    }


def write_outputs(
    results: list[SimulationResult],
    output_dir: Path,
    statistical_seed_count: int = STATISTICAL_SEED_MINIMUM,
) -> None:
    if statistical_seed_count < STATISTICAL_SEED_MINIMUM:
        raise ValueError(
            f"statistical_seed_count must be at least {STATISTICAL_SEED_MINIMUM}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    for result in results:
        experiment_dir = output_dir / result.config.experiment_id
        experiment_dir.mkdir(parents=True, exist_ok=True)
        _write_metrics_csv(result, experiment_dir / "metrics.csv")
        _write_trace_jsonl(result, experiment_dir / "trace.jsonl")
        _write_json(experiment_dir / "summary.json", result.summary())
        summary_rows.append(result.summary())
    _write_summary_csv(summary_rows, output_dir / "summary.csv")
    _write_json(output_dir / "summary.json", summary_rows)
    _write_svg(results, output_dir / "parasitic_phase_curves.svg")
    steps = results[0].config.steps if results else 160
    _write_json(
        output_dir / "statistical_summary.json",
        run_statistical_robustness(steps=steps, seed_count=statistical_seed_count),
    )
    _write_json(output_dir / "parameter_phase_map.json", run_parameter_sweep(steps=steps))
    _write_json(output_dir / "causal_phi_graph.json", build_causal_phi_graph(results))
    _write_json(
        output_dir / "scientific_closure_manifest.json",
        scientific_closure_manifest(output_dir, results, statistical_seed_count),
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_trace_jsonl(result: SimulationResult, path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for item in result.trace:
            handle.write(json.dumps(item, sort_keys=True) + "\n")


def _write_metrics_csv(result: SimulationResult, path: Path) -> None:
    fields = [
        "timestep",
        "population",
        "phi",
        "delta_phi",
        "entropy",
        "resource_concentration",
        "reward_drift",
        "agent_dominance",
        "phi_resource_contribution",
        "phi_reward_drift_contribution",
        "phi_dominance_contribution",
        "dominant_lineage_id",
        "dominant_lineage_type",
        "dominant_lineage_count",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for timestep, metric in enumerate(result.metrics):
            row = {"timestep": timestep}
            row.update({field: metric.get(field, "") for field in fields if field != "timestep"})
            writer.writerow(row)


def _write_summary_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_svg(results: list[SimulationResult], path: Path) -> None:
    width = 920
    height = 520
    panel_height = 140
    margin_left = 70
    margin_top = 30
    colors = {
        "A_no_governance": "#c2410c",
        "B_weak_governance": "#2563eb",
        "C_strong_governance": "#15803d",
    }
    panels = [
        ("phi", "Phi(t)"),
        ("entropy", "entropy"),
        ("agent_dominance", "dominance"),
    ]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;font-size:13px}.title{font-size:16px;font-weight:bold}</style>',
        '<text class="title" x="70" y="22">SAEE v1.2 local parasitic phase curves</text>',
    ]
    for panel_index, (field_name, label) in enumerate(panels):
        y0 = margin_top + panel_index * (panel_height + 22)
        x0 = margin_left
        x1 = width - 40
        y1 = y0 + panel_height
        lines.append(f'<text x="12" y="{y0 + 72}">{label}</text>')
        lines.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#d4d4d4"/>')
        lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#d4d4d4"/>')
        if field_name == "phi" and results:
            boundary = clamp(results[0].config.phi_threshold)
            boundary_y = y1 - panel_height * boundary
            lines.append(
                f'<line x1="{x0}" y1="{boundary_y:.2f}" x2="{x1}" y2="{boundary_y:.2f}" stroke="#111827" stroke-width="1.2" stroke-dasharray="6 5"/>'
            )
            lines.append(
                f'<text x="{x1 - 54}" y="{boundary_y - 6:.2f}">Phi_c={boundary:.2f}</text>'
            )
        for result in results:
            points = []
            max_step = max(1, len(result.metrics) - 1)
            for index, metric in enumerate(result.metrics):
                x = x0 + (x1 - x0) * index / max_step
                value = float(metric[field_name])
                y = y1 - panel_height * clamp(value)
                points.append(f"{x:.2f},{y:.2f}")
            color = colors.get(result.config.experiment_id, "#111827")
            lines.append(
                f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(points)}"/>'
            )
    legend_y = height - 18
    legend_x = 70
    for result in results:
        color = colors.get(result.config.experiment_id, "#111827")
        lines.append(f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 22}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<text x="{legend_x + 28}" y="{legend_y + 4}">{result.config.experiment_id}</text>')
        legend_x += 230
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
