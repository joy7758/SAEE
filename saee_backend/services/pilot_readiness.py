"""Deterministic offline readiness review for a future SAEE pilot.

This module makes no external calls and does not execute or approve a pilot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DIMENSIONS = ("dataset", "privacy", "technical", "annotation", "safety")
DECISIONS = {"GO", "CONDITIONAL_GO", "NO_GO"}


class PilotReadinessError(ValueError):
    """Stable readiness-contract failure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise PilotReadinessError(code, detail)


def _requirements(document: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    dimensions = document.get("dimensions")
    _require(isinstance(dimensions, dict), "PILOT_READINESS_DIMENSIONS_INVALID", "dimensions object required")
    _require(set(dimensions) == set(DIMENSIONS), "PILOT_READINESS_DIMENSIONS_INVALID", "exact five dimensions required")
    collected: list[tuple[str, dict[str, Any]]] = []
    seen: set[str] = set()
    for dimension_name in DIMENSIONS:
        dimension = dimensions[dimension_name]
        _require(isinstance(dimension, dict), "PILOT_READINESS_DIMENSION_INVALID", dimension_name)
        _require(dimension.get("status") in {"READY", "NOT_READY"}, "PILOT_READINESS_DIMENSION_INVALID", f"{dimension_name}.status")
        items = dimension.get("requirements")
        _require(isinstance(items, list) and items, "PILOT_READINESS_REQUIREMENTS_INVALID", dimension_name)
        for item in items:
            _require(isinstance(item, dict), "PILOT_READINESS_REQUIREMENT_INVALID", dimension_name)
            requirement_id = item.get("requirement_id")
            _require(isinstance(requirement_id, str) and requirement_id, "PILOT_READINESS_REQUIREMENT_INVALID", "requirement_id")
            _require(requirement_id not in seen, "PILOT_READINESS_REQUIREMENT_INVALID", f"duplicate {requirement_id}")
            seen.add(requirement_id)
            for flag in ("mandatory", "critical", "conditional_go_allowed", "satisfied"):
                _require(type(item.get(flag)) is bool, "PILOT_READINESS_REQUIREMENT_INVALID", f"{requirement_id}.{flag}")
            _require(isinstance(item.get("evidence_refs"), list), "PILOT_READINESS_REQUIREMENT_INVALID", f"{requirement_id}.evidence_refs")
            if item["satisfied"]:
                _require(bool(item["evidence_refs"]), "PILOT_READINESS_EVIDENCE_REQUIRED", requirement_id)
            _require(not (item["critical"] and item["conditional_go_allowed"]), "PILOT_READINESS_REQUIREMENT_INVALID", f"critical deferral {requirement_id}")
            collected.append((dimension_name, item))
        expected_status = "READY" if all(not item["mandatory"] or item["satisfied"] for item in items) else "NOT_READY"
        _require(dimension["status"] == expected_status, "PILOT_READINESS_DIMENSION_STATUS_MISMATCH", dimension_name)
    return collected


def evaluate_pilot_readiness(document: dict[str, Any]) -> dict[str, Any]:
    """Validate a readiness matrix and compute its decision from requirements."""

    _require(isinstance(document, dict), "PILOT_READINESS_INPUT_INVALID", "JSON object required")
    _require(document.get("saee_pilot_readiness_review_v0_1") is True, "PILOT_READINESS_IDENTITY_INVALID", "root marker")
    _require(document.get("review_version") == "0.1", "PILOT_READINESS_VERSION_INVALID", "version")
    _require(document.get("pilot_status") in {"ready", "conditionally_ready", "not_ready"}, "PILOT_READINESS_STATUS_INVALID", "pilot_status")
    _require(document.get("decision") in DECISIONS, "PILOT_READINESS_DECISION_INVALID", "decision")
    _require(type(document.get("execution_started")) is bool, "PILOT_READINESS_EXECUTION_STATE_INVALID", "execution_started")
    _require(type(document.get("execution_approval_recorded")) is bool, "PILOT_READINESS_EXECUTION_STATE_INVALID", "execution_approval_recorded")
    _require(type(document.get("external_validation_completed")) is bool, "PILOT_READINESS_EXTERNAL_VALIDATION_INVALID", "external_validation_completed")
    if document["execution_started"] and not document["execution_approval_recorded"]:
        raise PilotReadinessError("PILOT_EXECUTION_WITHOUT_APPROVAL", "execution_started=true without approval")
    _require(document["execution_started"] is False, "PILOT_EXECUTION_ALREADY_STARTED", "readiness review must precede execution")
    _require(document["external_validation_completed"] is False, "PILOT_EXTERNAL_VALIDATION_UNSUPPORTED", "readiness review is not external validation")

    requirements = _requirements(document)
    missing = [item["requirement_id"] for _, item in requirements if item["mandatory"] and not item["satisfied"]]
    critical_missing = [item["requirement_id"] for _, item in requirements if item["mandatory"] and item["critical"] and not item["satisfied"]]
    nondeferrable_missing = [item["requirement_id"] for _, item in requirements if item["mandatory"] and not item["satisfied"] and not item["conditional_go_allowed"]]

    if critical_missing or nondeferrable_missing:
        decision = "NO_GO"
        pilot_status = "not_ready"
    elif missing:
        decision = "CONDITIONAL_GO"
        pilot_status = "conditionally_ready"
    else:
        decision = "GO"
        pilot_status = "ready"

    _require(document["decision"] == decision, "PILOT_READINESS_DECLARED_DECISION_MISMATCH", f"declared {document['decision']}, computed {decision}")
    _require(document["pilot_status"] == pilot_status, "PILOT_READINESS_DECLARED_STATUS_MISMATCH", f"declared {document['pilot_status']}, computed {pilot_status}")
    _require(document.get("missing_requirements") == missing, "PILOT_READINESS_MISSING_REQUIREMENTS_MISMATCH", "missing_requirements")
    _require(isinstance(document.get("decision_reason"), str) and document["decision_reason"], "PILOT_READINESS_REASON_REQUIRED", "decision_reason")
    _require(isinstance(document.get("limitations"), list) and document["limitations"], "PILOT_READINESS_LIMITATIONS_REQUIRED", "limitations")

    return {
        "result_type": "SAEE_PILOT_READINESS_RESULT",
        "review_version": "0.1",
        "valid_review": True,
        "decision": decision,
        "pilot_status": pilot_status,
        "decision_reason": document["decision_reason"],
        "missing_requirements": missing,
        "critical_missing_requirements": critical_missing,
        "dimension_statuses": {name: document["dimensions"][name]["status"] for name in DIMENSIONS},
        "execution_started": False,
        "execution_authorized_by_review": False,
        "experiment_executed": False,
        "external_validation_completed": False,
        "scientific_result_claimed": False,
        "production_ready": False,
    }


def review_pilot_readiness_path(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return evaluate_pilot_readiness(raw)

