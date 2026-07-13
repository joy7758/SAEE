"""Structured report-layer metrics for the SAEE MVP API shell."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pvariance

from saee_backend.core.simulator import AgentTrace, clamp
from saee_backend.models.response import (
    FailureMode,
    FailureModeReport,
    RankingItem,
    StabilityReport,
    SurvivalCurve,
    SurvivalPoint,
)


SURVIVAL_SCORE_THRESHOLD = 0.35


@dataclass(frozen=True)
class AgentEvaluation:
    agent_id: str
    traces: list[AgentTrace]
    stability_score: float
    survival_score: float
    failure_rate: float
    collapse_events: int
    drift_index: float
    risk_score: float
    ranking_score: float
    aggregate_scores: list[float]
    aggregate_alive: list[bool]


def _drift_rate(scores: list[float]) -> float:
    if len(scores) < 2:
        return 0.0
    return abs(scores[-1] - scores[0])


def _run_stability(trace: AgentTrace) -> float:
    variance = pvariance(trace.scores) if len(trace.scores) > 1 else 0.0
    return clamp(1.0 / (1.0 + variance * 12.0))


def _run_survived(trace: AgentTrace) -> bool:
    return trace.alive[-1] and trace.scores[-1] >= SURVIVAL_SCORE_THRESHOLD


def _run_survival_ratio(trace: AgentTrace) -> float:
    if not trace.alive:
        return 0.0
    return sum(1 for active in trace.alive if active) / len(trace.alive)


def _average_scores(traces: list[AgentTrace]) -> list[float]:
    if not traces:
        return []
    horizon = min(len(trace.scores) for trace in traces)
    return [
        round(mean(trace.scores[index] for trace in traces), 6)
        for index in range(horizon)
    ]


def _aggregate_alive(traces: list[AgentTrace]) -> list[bool]:
    if not traces:
        return []
    horizon = min(len(trace.alive) for trace in traces)
    return [
        sum(1 for trace in traces if trace.alive[index]) / len(traces) >= 0.5
        for index in range(horizon)
    ]


def evaluate_agent_runs(agent_id: str, traces: list[AgentTrace]) -> AgentEvaluation:
    if not traces:
        return AgentEvaluation(
            agent_id=agent_id,
            traces=[],
            stability_score=0.0,
            survival_score=0.0,
            failure_rate=1.0,
            collapse_events=0,
            drift_index=1.0,
            risk_score=1.0,
            ranking_score=0.0,
            aggregate_scores=[],
            aggregate_alive=[],
        )

    collapse_events = sum(1 for trace in traces if trace.collapse_step is not None)
    failure_rate = collapse_events / len(traces)
    survival_score = mean(_run_survival_ratio(trace) for trace in traces)
    stability_score = mean(mean(trace.scores) for trace in traces if trace.scores)
    drift_index = mean(_drift_rate(trace.scores) for trace in traces)
    total_steps = sum(len(trace.scores) for trace in traces) or 1
    risk_score = collapse_events / total_steps
    ranking_score = clamp(
        0.50 * stability_score
        + 0.30 * survival_score
        - 0.20 * risk_score
    )
    return AgentEvaluation(
        agent_id=agent_id,
        traces=traces,
        stability_score=round(stability_score, 6),
        survival_score=round(survival_score, 6),
        failure_rate=round(failure_rate, 6),
        collapse_events=collapse_events,
        drift_index=round(drift_index, 6),
        risk_score=round(risk_score, 6),
        ranking_score=round(ranking_score, 6),
        aggregate_scores=_average_scores(traces),
        aggregate_alive=_aggregate_alive(traces),
    )


def build_stability_report(evaluation: AgentEvaluation) -> StabilityReport:
    if evaluation.failure_rate >= 0.5:
        status = "collapsing"
    elif evaluation.stability_score < 0.65 or evaluation.drift_index > 0.35:
        status = "unstable"
    else:
        status = "stable"
    aggregate_variance = (
        pvariance(evaluation.aggregate_scores)
        if len(evaluation.aggregate_scores) > 1
        else 0.0
    )
    return StabilityReport(
        agent_id=evaluation.agent_id,
        stability_score=evaluation.stability_score,
        drift_rate=evaluation.drift_index,
        variance=round(aggregate_variance, 6),
        convergence_status=status,
        time_series=evaluation.aggregate_scores,
    )


def build_failure_report(evaluation: AgentEvaluation) -> FailureModeReport:
    failures: list[FailureMode] = []
    if evaluation.collapse_events:
        first_collapse = min(
            trace.collapse_step
            for trace in evaluation.traces
            if trace.collapse_step is not None
        )
        failures.append(
            FailureMode(
                type="collapse",
                step=first_collapse,
                severity=round(min(evaluation.failure_rate, 1.0), 6),
                description="One or more deterministic runs crossed the public collapse threshold.",
            )
        )
    if evaluation.drift_index > 0.35:
        failures.append(
            FailureMode(
                type="drift",
                step=max(len(evaluation.aggregate_scores) - 1, 0),
                severity=round(min(evaluation.drift_index, 1.0), 6),
                description="Average score changed materially across repeated long-horizon runs.",
            )
        )
    variance = pvariance(evaluation.aggregate_scores) if len(evaluation.aggregate_scores) > 1 else 0.0
    if variance > 0.04:
        failures.append(
            FailureMode(
                type="oscillation",
                step=max(len(evaluation.aggregate_scores) // 2, 0),
                severity=round(min(variance * 5.0, 1.0), 6),
                description="Aggregate score variance exceeded the public oscillation threshold.",
            )
        )
    if not failures and evaluation.ranking_score < 0.55:
        failures.append(
            FailureMode(
                type="degeneration",
                step=max(len(evaluation.aggregate_scores) - 1, 0),
                severity=round(1.0 - evaluation.ranking_score, 6),
                description="Agent survived but produced a weak aggregate ranking score.",
            )
        )
    return FailureModeReport(agent_id=evaluation.agent_id, failure_modes=failures)


def build_survival_curve(evaluation: AgentEvaluation) -> SurvivalCurve:
    return SurvivalCurve(
        agent_id=evaluation.agent_id,
        curve=[
            SurvivalPoint(t=index, alive=alive, score=score)
            for index, (alive, score) in enumerate(
                zip(evaluation.aggregate_alive, evaluation.aggregate_scores, strict=True)
            )
        ],
    )


def build_ranking_items(evaluations: list[AgentEvaluation]) -> list[RankingItem]:
    scored = [(evaluation.agent_id, evaluation.ranking_score) for evaluation in evaluations]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return [
        RankingItem(rank=index + 1, agent_id=agent_id, score=score)
        for index, (agent_id, score) in enumerate(scored)
    ]


def mean_score(values: list[float]) -> float:
    return round(mean(values), 6) if values else 0.0
