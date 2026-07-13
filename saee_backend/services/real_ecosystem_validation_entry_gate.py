"""Deterministic decision logic for the SAEE real-ecosystem validation entry gate.

This module evaluates preparation metadata only. It cannot contact participants,
start validation, authorize execution, or turn readiness into adoption evidence.
"""

from __future__ import annotations

from typing import Any


FORBIDDEN_SIGNAL_CODES = {
    "external_validation_started": "REAL_VALIDATION_EXTERNAL_START_FORBIDDEN",
    "real_candidate_connected": "REAL_VALIDATION_REAL_CANDIDATE_FORBIDDEN",
    "customer_validated": "REAL_VALIDATION_CUSTOMER_CLAIM_FORBIDDEN",
    "adoption_claim": "REAL_VALIDATION_ADOPTION_CLAIM_FORBIDDEN",
}


def evaluate_entry_gate(state: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a bounded readiness state without authorizing external action."""

    forbidden = [code for field, code in FORBIDDEN_SIGNAL_CODES.items() if state.get(field) is True]
    if forbidden:
        decision = "REJECTED"
        reason_codes = forbidden
    elif state.get("critical_blocker") is True:
        decision = "HOLD"
        reason_codes = ["REAL_VALIDATION_CRITICAL_BLOCKER_OPEN"]
    elif any(state.get(field) is not True for field in ("technical_ready", "candidate_ready", "scope_ready", "risk_ready")):
        decision = "HOLD"
        reason_codes = ["REAL_VALIDATION_REQUIRED_DIMENSION_NOT_READY"]
    elif state.get("operational_ready") is not True:
        decision = "CONDITIONAL_READY"
        reason_codes = ["REAL_VALIDATION_OPERATIONAL_GAP_OPEN"]
    elif state.get("all_required_verified") is True:
        decision = "ENTRY_READY"
        reason_codes = ["REAL_VALIDATION_ALL_REQUIRED_VERIFIED"]
    else:
        decision = "CONDITIONAL_READY"
        reason_codes = ["REAL_VALIDATION_VERIFICATION_INCOMPLETE"]

    return {
        "fixture_id": state.get("fixture_id", "UNSPECIFIED"),
        "decision": decision,
        "reason_codes": reason_codes,
        "external_validation": False,
        "execution_authorized": False,
        "validation_started": False,
        "participant_contact": False,
        "real_candidate": False,
        "customer_data": False,
        "adoption_validated": False,
        "production_ready": False,
    }


def readiness_from_matrix(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Create schema-shaped readiness summaries from the machine-readable matrix."""

    result: dict[str, dict[str, Any]] = {}
    for dimension in matrix.get("dimensions", []):
        checks = dimension.get("checks", [])
        result[str(dimension.get("dimension"))] = {
            "status": dimension.get("status"),
            "verified_checks": sum(item.get("status") == "VERIFIED" for item in checks),
            "required_checks": len(checks),
        }
    return result
