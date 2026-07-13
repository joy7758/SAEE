"""Synthetic SAEE Pilot re-readiness review evaluator v0.1.

This evaluator composes Phase 5.7 eligibility logic with strict real-state and
authorization separation. It never changes operational readiness.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_backend.services.pilot_evidence_readiness import evaluate_pilot_evidence_readiness


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_TOP_LEVEL = {
    "simulation_version",
    "scenario_id",
    "scenario_type",
    "synthetic_only",
    "input_type",
    "evidence_source_claim",
    "evidence_package_ref",
    "reassessment_result",
    "expected_simulation_result",
    "attempted_real_readiness_status",
    "attempted_pilot_authorized",
    "attempted_execution_authorized",
    "attempted_external_validation_completed",
    "real_readiness_status",
    "gaps_closed",
    "pilot_authorized",
    "execution_authorized",
    "production_ready",
}

REREADINESS_INVALID = "REREADINESS_INVALID"
REREADINESS_STRUCTURE_INVALID = "REREADINESS_STRUCTURE_INVALID"
REREADINESS_REAL_STATE_CLAIM_FORBIDDEN = "REREADINESS_REAL_STATE_CLAIM_FORBIDDEN"
REREADINESS_SYNTHETIC_AS_REAL_REJECTED = "REREADINESS_SYNTHETIC_AS_REAL_REJECTED"
REREADINESS_READINESS_ESCALATION_REJECTED = "REREADINESS_READINESS_ESCALATION_REJECTED"
REREADINESS_AUTHORIZATION_CONFUSION_REJECTED = "REREADINESS_AUTHORIZATION_CONFUSION_REJECTED"
REREADINESS_EXTERNAL_VALIDATION_REJECTED = "REREADINESS_EXTERNAL_VALIDATION_REJECTED"
REREADINESS_PACKAGE_REFERENCE_INVALID = "REREADINESS_PACKAGE_REFERENCE_INVALID"
REREADINESS_PACKAGE_NOT_ELIGIBLE = "REREADINESS_PACKAGE_NOT_ELIGIBLE"
REREADINESS_EXPECTATION_MISMATCH = "REREADINESS_EXPECTATION_MISMATCH"


def _result(value: Any, valid: bool, simulation_result: str, eligible: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "saee_pilot_rereadiness_review_result_v0_1": True,
        "scenario_valid": valid,
        "scenario_id": value.get("scenario_id", "") if isinstance(value, dict) else "",
        "scenario_type": value.get("scenario_type", "") if isinstance(value, dict) else "",
        "simulation_result": simulation_result,
        "reassessment_eligible": eligible,
        "synthetic_evidence_ready": eligible,
        "real_readiness_status": "NOT_READY",
        "real_readiness_changed": False,
        "gaps_closed": False,
        "pilot_authorized": False,
        "execution_authorized": False,
        "external_validation_completed": False,
        "reason_codes": reasons,
        "synthetic_only": True,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def evaluate_pilot_rereadiness_review(value: Any) -> dict[str, Any]:
    """Evaluate one synthetic re-readiness scenario without changing real state."""

    if not isinstance(value, dict):
        return _result(value, False, "REJECT", False, [REREADINESS_INVALID])
    if (
        value.get("synthetic_only") is not True
        or value.get("real_readiness_status") != "NOT_READY"
        or value.get("gaps_closed") is not False
        or value.get("pilot_authorized") is not False
        or value.get("execution_authorized") is not False
        or value.get("production_ready") is not False
    ):
        return _result(value, False, "REJECT", False, [REREADINESS_REAL_STATE_CLAIM_FORBIDDEN])
    if set(value) != EXPECTED_TOP_LEVEL or value.get("simulation_version") != "0.1":
        return _result(value, False, "REJECT", False, [REREADINESS_STRUCTURE_INVALID])

    if value.get("input_type") != "synthetic" or value.get("evidence_source_claim") != "SYNTHETIC":
        simulation_result = "REJECT"
        eligible = False
        reasons = [REREADINESS_SYNTHETIC_AS_REAL_REJECTED]
    elif value.get("attempted_external_validation_completed") is True:
        simulation_result = "REJECT"
        eligible = False
        reasons = [REREADINESS_EXTERNAL_VALIDATION_REJECTED]
    elif value.get("attempted_real_readiness_status") != "NOT_READY":
        simulation_result = "REJECT"
        eligible = False
        reasons = [REREADINESS_READINESS_ESCALATION_REJECTED]
    elif value.get("attempted_pilot_authorized") is True or value.get("attempted_execution_authorized") is True:
        simulation_result = "REJECT"
        eligible = False
        reasons = [REREADINESS_AUTHORIZATION_CONFUSION_REJECTED]
    else:
        package_ref = value.get("evidence_package_ref")
        if not isinstance(package_ref, str) or not (ROOT / package_ref).is_file():
            return _result(value, False, "REJECT", False, [REREADINESS_PACKAGE_REFERENCE_INVALID])
        try:
            package = json.loads((ROOT / package_ref).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return _result(value, False, "REJECT", False, [REREADINESS_PACKAGE_REFERENCE_INVALID])
        evidence_result = evaluate_pilot_evidence_readiness(package)
        if not evidence_result.get("evaluation_valid"):
            return _result(value, False, "REJECT", False, [REREADINESS_PACKAGE_REFERENCE_INVALID])
        eligible = evidence_result.get("reassessment_eligible") is True
        simulation_result = "ELIGIBLE_FOR_REVIEW" if eligible else "NOT_ELIGIBLE_FOR_REVIEW"
        reasons = [] if eligible else [REREADINESS_PACKAGE_NOT_ELIGIBLE]

    declared_reassessment = "ELIGIBLE_FOR_REVIEW" if eligible else "NOT_ELIGIBLE_FOR_REVIEW"
    if value.get("reassessment_result") != declared_reassessment or value.get("expected_simulation_result") != simulation_result:
        return _result(value, False, "REJECT", False, [REREADINESS_EXPECTATION_MISMATCH])
    return _result(value, True, simulation_result, eligible, reasons)


def validate_rereadiness_result_truth(value: Any) -> dict[str, Any]:
    """Reject aggregate output that promotes simulation into operational truth."""

    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": [REREADINESS_INVALID]}
    expected = {
        "synthetic_only": True,
        "real_readiness_changed": False,
        "real_readiness_status": "NOT_READY",
        "gaps_closed": False,
        "reassessment_eligible": False,
        "pilot_authorized": False,
        "execution_authorized": False,
        "external_validation_completed": False,
        "production_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            return {"valid": False, "reason_codes": [f"REREADINESS_RESULT_OVERCLAIM:{field}"]}
    return {"valid": True, "reason_codes": []}


def evaluate_pilot_rereadiness_review_path(path: Path) -> dict[str, Any]:
    """Evaluate one checked-in local synthetic review scenario."""

    return evaluate_pilot_rereadiness_review(json.loads(path.read_text(encoding="utf-8")))
