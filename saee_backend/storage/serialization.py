"""Serialization helpers for public-shell experiment persistence."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from saee_backend.models.response import (
    ComparisonRanking,
    EvaluationRunSummary,
    FailureModeReport,
    StabilityReport,
    SurvivalCurve,
)
from saee_backend.storage.memory_db import AgentMetricRecord, AgentRunRecord, ExperimentResult
from saee_backend.storage.secret_boundary import validate_persistable_experiment_result


def serialize_experiment_result(result: ExperimentResult) -> dict[str, Any]:
    validate_persistable_experiment_result(result)
    return {
        "summary": result.summary.model_dump(mode="json"),
        "stability_reports": [item.model_dump(mode="json") for item in result.stability_reports],
        "failure_reports": [item.model_dump(mode="json") for item in result.failure_reports],
        "survival_curves": [item.model_dump(mode="json") for item in result.survival_curves],
        "ranking": result.ranking.model_dump(mode="json"),
        "runs": [asdict(item) for item in result.runs],
        "metrics": [asdict(item) for item in result.metrics],
        "agent_outputs": result.agent_outputs,
    }


def deserialize_experiment_result(payload: dict[str, Any]) -> ExperimentResult:
    result = ExperimentResult(
        summary=EvaluationRunSummary.model_validate(payload["summary"]),
        stability_reports=[
            StabilityReport.model_validate(item) for item in payload.get("stability_reports", [])
        ],
        failure_reports=[
            FailureModeReport.model_validate(item) for item in payload.get("failure_reports", [])
        ],
        survival_curves=[
            SurvivalCurve.model_validate(item) for item in payload.get("survival_curves", [])
        ],
        ranking=ComparisonRanking.model_validate(payload["ranking"]),
        runs=[AgentRunRecord(**item) for item in payload.get("runs", [])],
        metrics=[AgentMetricRecord(**item) for item in payload.get("metrics", [])],
        agent_outputs=payload.get("agent_outputs", {}),
    )
    validate_persistable_experiment_result(result)
    return result
