"""Closed persistence contract for public SAEE experiment results."""

from __future__ import annotations

import math
from dataclasses import asdict, is_dataclass
from typing import Any

from saee_backend.services.public_input_contract import (
    FORBIDDEN_CONFIG_KEYS,
    contains_high_confidence_credential,
    validate_public_identifier,
)


EXPERIMENT_RESULT_FIELDS = {
    "summary",
    "stability_reports",
    "failure_reports",
    "survival_curves",
    "ranking",
    "runs",
    "metrics",
    "agent_outputs",
}
KNOWN_DATACLASSES = {
    ("saee_backend.storage.memory_db", "AgentRunRecord"),
    ("saee_backend.storage.memory_db", "AgentMetricRecord"),
    ("saee_backend.storage.memory_db", "ExperimentResult"),
}
KNOWN_RESPONSE_MODELS = {
    "AgentScore",
    "OverallStats",
    "EvaluationRunSummary",
    "StabilityReport",
    "FailureMode",
    "FailureModeReport",
    "SurvivalPoint",
    "SurvivalCurve",
    "RankingItem",
    "ComparisonRanking",
    "DecisionResult",
}
AGENT_OUTPUT_FIELDS = {
    "aggregate_scores",
    "aggregate_alive",
    "risk_score",
    "drift_index",
}


def _walk_secret_free(value: Any, *, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("persistable result nesting exceeds the public boundary")
    if isinstance(value, str):
        if contains_high_confidence_credential(value):
            raise ValueError("persistable result contains credential material")
        return
    if value is None or type(value) is bool or type(value) is int:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("persistable result contains a non-finite number")
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError("persistable result keys must be strings")
            if key.strip().lower().replace("-", "_") in FORBIDDEN_CONFIG_KEYS:
                raise ValueError("persistable result contains a credential field")
            _walk_secret_free(nested, depth=depth + 1)
        return
    if isinstance(value, list):
        for nested in value:
            _walk_secret_free(nested, depth=depth + 1)
        return
    if is_dataclass(value):
        type_key = (type(value).__module__, type(value).__name__)
        if type_key not in KNOWN_DATACLASSES:
            raise ValueError("persistable result contains an unknown dataclass")
        _walk_secret_free(asdict(value), depth=depth + 1)
        return
    if hasattr(value, "model_dump"):
        if type(value).__module__ != "saee_backend.models.response" or type(
            value
        ).__name__ not in KNOWN_RESPONSE_MODELS:
            raise ValueError("persistable result contains an unknown model")
        _walk_secret_free(value.model_dump(mode="json"), depth=depth + 1)
        return
    raise ValueError("persistable result contains an unsupported value type")


def _finite_number(value: Any, *, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"persistable agent output {field} must be numeric")
    if not math.isfinite(float(value)):
        raise ValueError(f"persistable agent output {field} must be finite")


def validate_identifier_not_tenant(value: str, tenant_id: str | None) -> None:
    validate_public_identifier(value, field_name="persistable_identifier")
    if tenant_id is not None and value == tenant_id:
        raise ValueError("persistable identifier must not equal the raw tenant ID")


def validate_persistable_experiment_result(
    result: Any,
    *,
    tenant_id: str | None = None,
) -> None:
    if set(vars(result)) != EXPERIMENT_RESULT_FIELDS:
        raise ValueError("experiment result contains unknown persistence fields")

    summary = result.summary
    validate_identifier_not_tenant(summary.experiment_id, tenant_id)
    validate_identifier_not_tenant(summary.run_id, tenant_id)
    for score in summary.agents:
        validate_identifier_not_tenant(score.agent_id, tenant_id)
    if summary.recommended_agent is not None:
        validate_identifier_not_tenant(summary.recommended_agent, tenant_id)
    if summary.decision_result is not None:
        if summary.decision_result.recommended_agent is not None:
            validate_identifier_not_tenant(
                summary.decision_result.recommended_agent,
                tenant_id,
            )
        for item in summary.decision_result.ranking:
            validate_identifier_not_tenant(item.agent_id, tenant_id)
        for agent_id in summary.decision_result.failure_modes_summary:
            validate_identifier_not_tenant(agent_id, tenant_id)
    for collection in (
        result.stability_reports,
        result.failure_reports,
        result.survival_curves,
        result.ranking.ranking,
        result.runs,
        result.metrics,
    ):
        for item in collection:
            agent_id = getattr(item, "agent_id", None)
            if agent_id is not None:
                validate_identifier_not_tenant(agent_id, tenant_id)
    validate_identifier_not_tenant(result.ranking.experiment_id, tenant_id)

    for run in result.runs:
        if type(run.run_index) is not int or run.run_index < 0:
            raise ValueError("persistable run_index must be a non-negative integer")
        if not isinstance(run.scores, list) or not run.scores:
            raise ValueError("persistable run scores must be a non-empty list")
        for score in run.scores:
            _finite_number(score, field="run.scores")
        if (
            not isinstance(run.alive, list)
            or len(run.alive) != len(run.scores)
            or any(type(item) is not bool for item in run.alive)
        ):
            raise ValueError("persistable run alive values must match scores")
        if run.collapse_step is not None and (
            type(run.collapse_step) is not int or run.collapse_step < 0
        ):
            raise ValueError("persistable collapse_step is invalid")
    for metric in result.metrics:
        for field in (
            "stability_score",
            "survival_score",
            "failure_rate",
            "drift_index",
            "risk_score",
            "ranking_score",
        ):
            _finite_number(getattr(metric, field), field="metric." + field)
        if type(metric.collapse_events) is not int or metric.collapse_events < 0:
            raise ValueError("persistable collapse_events is invalid")

    if not isinstance(result.agent_outputs, dict):
        raise ValueError("agent_outputs must be an object")
    for agent_id, output in result.agent_outputs.items():
        validate_identifier_not_tenant(agent_id, tenant_id)
        if not isinstance(output, dict) or set(output) != AGENT_OUTPUT_FIELDS:
            raise ValueError("agent_outputs must use the closed numeric schema")
        scores = output["aggregate_scores"]
        alive = output["aggregate_alive"]
        if not isinstance(scores, list) or not scores:
            raise ValueError("aggregate_scores must be a non-empty list")
        for score in scores:
            _finite_number(score, field="aggregate_scores")
        if not isinstance(alive, list) or not alive or any(type(item) is not bool for item in alive):
            raise ValueError("aggregate_alive must be a non-empty boolean list")
        _finite_number(output["risk_score"], field="risk_score")
        _finite_number(output["drift_index"], field="drift_index")

    _walk_secret_free(result)
