"""Safe file-backed evaluation of sanitized observed agent traces.

This module consumes numerical, allowlisted trace evidence only. It never
captures traces, executes candidate code, calls the synthetic simulator, opens
URLs, or contacts external systems.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from statistics import mean, pvariance
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from saee_backend.core.evaluator import (
    AgentEvaluation,
    build_ranking_items,
    build_stability_report,
    build_survival_curve,
)
from saee_backend.core.simulator import AgentTrace, clamp
from saee_backend.models.response import (
    AgentScore,
    ComparisonRanking,
    DecisionResult,
    EvaluationRunSummary,
    FailureMode,
    FailureModeReport,
    OverallStats,
)


SCHEMA_VERSION = "0.1.0"
MODE = "observed_trace_bundle_evaluation"
FORMULA = "0.50 * stability_score + 0.30 * survival_score - 0.20 * risk_score"
FailureCode = Literal[
    "none",
    "timeout",
    "tool_error",
    "policy_violation",
    "invalid_output",
    "resource_exhaustion",
    "other",
]


class SourceAttestation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    producer_id: str = Field(pattern=r"^[A-Za-z0-9._-]{1,80}$")
    capture_method: Literal["exported_trace", "replay_log", "benchmark_run"]
    sanitization_attested: Literal[True]
    source_authorized: Literal[True]
    raw_content_excluded: Literal[True]


class EvidenceContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str = Field(pattern=r"^[A-Za-z0-9._-]{1,80}$")
    metric_name: str = Field(pattern=r"^[A-Za-z0-9._-]{1,80}$")
    metric_min: Literal[0.0]
    metric_max: Literal[1.0]
    higher_is_better: Literal[True]
    horizon_unit: Literal["step", "turn", "episode"]
    expected_horizon: int = Field(ge=2, le=100_000)
    failure_definition: Literal["alive_false_or_normalized_failure_code"]


class ObservedStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=0)
    quality_score: float = Field(ge=0.0, le=1.0)
    alive: bool
    failure_code: FailureCode
    failure_severity: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def failure_fields_agree(self) -> "ObservedStep":
        if self.failure_code == "none" and self.failure_severity != 0.0:
            raise ValueError("failure_severity must be 0 when failure_code is none")
        if self.failure_code != "none" and self.failure_severity <= 0.0:
            raise ValueError("failure_severity must be positive when failure_code is not none")
        if not self.alive and self.failure_code == "none":
            raise ValueError("alive=false requires a normalized failure_code")
        return self


class ObservedRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(pattern=r"^[A-Za-z0-9._-]{1,80}$")
    censored: bool
    steps: list[ObservedStep] = Field(min_length=2, max_length=100_000)

    @model_validator(mode="after")
    def validate_sequence(self) -> "ObservedRun":
        indices = [point.step for point in self.steps]
        if indices != list(range(len(indices))):
            raise ValueError("steps must be contiguous and ordered from 0")
        seen_dead = False
        for point in self.steps:
            if seen_dead and point.alive:
                raise ValueError("alive state cannot recover after alive=false")
            seen_dead = seen_dead or not point.alive
        return self


class ObservedCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(pattern=r"^[A-Za-z0-9._-]{1,80}$")
    context: EvidenceContext
    runs: list[ObservedRun] = Field(min_length=1, max_length=10_000)


class ObservedTraceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_ref: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["0.1.0"]
    bundle_id: str = Field(pattern=r"^[A-Za-z0-9._-]{1,80}$")
    source: SourceAttestation
    candidates: list[ObservedCandidate] = Field(min_length=2, max_length=100)

    @model_validator(mode="after")
    def validate_comparability(self) -> "ObservedTraceBundle":
        candidate_ids = [candidate.candidate_id for candidate in self.candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidate_id values must be unique")
        baseline = self.candidates[0].context.model_dump(mode="json")
        for candidate in self.candidates:
            if candidate.context.model_dump(mode="json") != baseline:
                raise ValueError("all candidates must share the same evidence context")
            run_ids = [run.run_id for run in candidate.runs]
            if len(run_ids) != len(set(run_ids)):
                raise ValueError(f"run_id values must be unique for {candidate.candidate_id}")
            horizon = candidate.context.expected_horizon
            for run in candidate.runs:
                if len(run.steps) > horizon:
                    raise ValueError("observed steps exceed expected_horizon")
                if not run.censored and len(run.steps) != horizon:
                    raise ValueError("uncensored run length must equal expected_horizon")
        return self


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalized_bundle(bundle: ObservedTraceBundle) -> dict[str, Any]:
    data = bundle.model_dump(mode="json")
    data.pop("schema_ref", None)
    data["candidates"] = sorted(data["candidates"], key=lambda item: item["candidate_id"])
    for candidate in data["candidates"]:
        candidate["runs"] = sorted(candidate["runs"], key=lambda item: item["run_id"])
    return data


def _average_scores(traces: list[AgentTrace]) -> list[float]:
    horizon = min((len(trace.scores) for trace in traces), default=0)
    return [round(mean(trace.scores[index] for trace in traces), 6) for index in range(horizon)]


def _aggregate_alive(traces: list[AgentTrace]) -> list[bool]:
    horizon = min((len(trace.alive) for trace in traces), default=0)
    return [
        sum(1 for trace in traces if trace.alive[index]) / len(traces) >= 0.5
        for index in range(horizon)
    ]


def _to_trace(candidate_id: str, run: ObservedRun, run_index: int) -> AgentTrace:
    collapse_step = next((point.step for point in run.steps if not point.alive), None)
    scores = [point.quality_score for point in run.steps]
    return AgentTrace(
        agent_id=candidate_id,
        run_index=run_index,
        scores=scores,
        alive=[point.alive for point in run.steps],
        collapse_step=collapse_step,
        drift=[round(abs(score - scores[0]), 6) for score in scores],
        risk=[point.failure_severity for point in run.steps],
    )


def _evaluate_candidate(candidate: ObservedCandidate) -> AgentEvaluation:
    ordered_runs = sorted(candidate.runs, key=lambda item: item.run_id)
    traces = [_to_trace(candidate.candidate_id, run, index) for index, run in enumerate(ordered_runs)]
    run_stability = []
    for trace in traces:
        variance = pvariance(trace.scores) if len(trace.scores) > 1 else 0.0
        run_stability.append(clamp(mean(trace.scores) / (1.0 + 12.0 * variance)))
    stability_score = mean(run_stability)
    survival_score = mean(sum(trace.alive) / len(trace.alive) for trace in traces)
    risk_score = mean(mean(trace.risk or [0.0]) for trace in traces)
    failure_rate = mean(
        any(point.failure_code != "none" for point in run.steps) for run in ordered_runs
    )
    collapse_events = sum(trace.collapse_step is not None for trace in traces)
    drift_index = mean(abs(trace.scores[-1] - trace.scores[0]) for trace in traces)
    ranking_score = clamp(0.50 * stability_score + 0.30 * survival_score - 0.20 * risk_score)
    return AgentEvaluation(
        agent_id=candidate.candidate_id,
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


def _build_observed_failure_report(evaluation: AgentEvaluation) -> FailureModeReport:
    failures: list[FailureMode] = []
    if evaluation.collapse_events:
        first_collapse = min(
            trace.collapse_step for trace in evaluation.traces if trace.collapse_step is not None
        )
        failures.append(
            FailureMode(
                type="collapse",
                step=first_collapse,
                severity=round(min(evaluation.failure_rate, 1.0), 6),
                description="One or more supplied observed runs recorded alive=false.",
            )
        )
    if evaluation.drift_index > 0.35:
        failures.append(
            FailureMode(
                type="drift",
                step=max(len(evaluation.aggregate_scores) - 1, 0),
                severity=round(min(evaluation.drift_index, 1.0), 6),
                description="Observed quality changed materially across the supplied horizon.",
            )
        )
    variance = pvariance(evaluation.aggregate_scores) if len(evaluation.aggregate_scores) > 1 else 0.0
    if variance > 0.04:
        failures.append(
            FailureMode(
                type="oscillation",
                step=max(len(evaluation.aggregate_scores) // 2, 0),
                severity=round(min(variance * 5.0, 1.0), 6),
                description="Observed aggregate quality variance exceeded the declared threshold.",
            )
        )
    if not failures and evaluation.ranking_score < 0.55:
        failures.append(
            FailureMode(
                type="degeneration",
                step=max(len(evaluation.aggregate_scores) - 1, 0),
                severity=round(1.0 - evaluation.ranking_score, 6),
                description="Supplied observed evidence produced a weak aggregate ranking score.",
            )
        )
    return FailureModeReport(agent_id=evaluation.agent_id, failure_modes=failures)


def evaluate_observed_trace_bundle(bundle: ObservedTraceBundle) -> dict[str, Any]:
    normalized = normalized_bundle(bundle)
    request_hash = sha256_json(normalized)
    ordered_candidates = sorted(bundle.candidates, key=lambda item: item.candidate_id)
    evaluations = [_evaluate_candidate(candidate) for candidate in ordered_candidates]
    stability_reports = [build_stability_report(item) for item in evaluations]
    failure_reports = [_build_observed_failure_report(item) for item in evaluations]
    survival_curves = [build_survival_curve(item) for item in evaluations]
    ranking_items = build_ranking_items(evaluations)
    ranking = ComparisonRanking(experiment_id=bundle.bundle_id, ranking=ranking_items)
    failure_summary = {
        report.agent_id: [mode.type for mode in report.failure_modes]
        for report in failure_reports
    }
    recommended_agent = ranking_items[0].agent_id if ranking_items else None
    confidence_score = ranking_items[0].score if ranking_items else 0.0
    decision = DecisionResult(
        recommended_agent=recommended_agent,
        confidence_score=confidence_score,
        ranking=ranking_items,
        failure_modes_summary=failure_summary,
    )
    score_by_agent = {item.agent_id: item.score for item in ranking_items}
    agent_scores = [
        AgentScore(agent_id=item.candidate_id, final_score=score_by_agent[item.candidate_id])
        for item in ordered_candidates
    ]
    divergence = max(score_by_agent.values(), default=0.0) - min(score_by_agent.values(), default=0.0)
    summary = EvaluationRunSummary(
        experiment_id=bundle.bundle_id,
        run_id=f"observed-run-{request_hash[:16]}",
        status="completed",
        agents=agent_scores,
        overall_stats=OverallStats(
            mean_stability=round(mean(item.stability_score for item in evaluations), 6),
            mean_survival=round(mean(item.survival_score for item in evaluations), 6),
            divergence_index=round(divergence, 6),
        ),
        decision_result=decision,
        recommended_agent=recommended_agent,
        confidence_score=confidence_score,
    )
    observed_failure_code_counts = {
        candidate.candidate_id: dict(
            sorted(
                Counter(
                    point.failure_code
                    for run in candidate.runs
                    for point in run.steps
                    if point.failure_code != "none"
                ).items()
            )
        )
        for candidate in ordered_candidates
    }
    trace_quality = {
        candidate.candidate_id: {
            "run_count": len(candidate.runs),
            "observed_step_count": sum(len(run.steps) for run in candidate.runs),
            "censored_run_count": sum(run.censored for run in candidate.runs),
        }
        for candidate in ordered_candidates
    }
    reports = {
        "evaluation_summary": summary.model_dump(mode="json"),
        "stability_reports": [item.model_dump(mode="json") for item in stability_reports],
        "failure_mode_reports": [item.model_dump(mode="json") for item in failure_reports],
        "survival_curves": [item.model_dump(mode="json") for item in survival_curves],
        "comparison_ranking": ranking.model_dump(mode="json"),
        "observed_failure_code_counts": observed_failure_code_counts,
        "trace_quality": trace_quality,
    }
    content_hash = sha256_json(reports)
    return {
        "saee_observed_trace_receipt_v0_1": True,
        "schema_version": SCHEMA_VERSION,
        "receipt_id": f"saee-observed-receipt-{request_hash[:16]}",
        "evaluation_mode": MODE,
        "request_sha256": request_hash,
        "content_sha256": content_hash,
        "provenance": {
            "input_kind": "sanitized_observed_agent_trace_bundle",
            "trace_capture_by_saee": False,
            "source_sanitization_attested": bundle.source.sanitization_attested,
            "source_authorized_attested": bundle.source.source_authorized,
            "raw_content_excluded_attested": bundle.source.raw_content_excluded,
            "allowlist_validation_passed": True,
            "trace_authenticity_verified": False,
            "candidate_code_executed": False,
            "external_calls_made": False,
            "simulator_called": False,
            "private_core_loaded": False,
            "scoring_formula": FORMULA,
            "stability_formula": "mean_over_runs(mean_quality / (1 + 12 * population_variance_quality))",
            "survival_formula": "mean_over_runs(alive_step_count / observed_step_count)",
            "risk_formula": "mean_over_runs(mean_normalized_failure_severity)",
            "tie_break": "descending ranking score, then ascending candidate_id",
            "censoring": "censored runs use observed steps only and are not imputed",
        },
        **reports,
        "truth_boundary": {
            "observed_agent_trace_evidence_evaluated": True,
            "trace_authenticity_verified": False,
            "pii_absence_verified_by_saee": False,
            "real_world_generalization_validated": False,
            "production_ready": False,
            "product_launched": False,
            "customer_validated": False,
            "external_agent_execution": False,
            "private_core_exposed": False,
        },
    }
