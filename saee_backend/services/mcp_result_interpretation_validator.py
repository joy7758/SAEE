"""Bound MCP dry-integration results to non-authoritative meanings."""

from __future__ import annotations

from typing import Any


FORBIDDEN_MEANINGS = {"APPROVED", "CERTIFIED", "SAFE", "DEPLOYED"}


def validate_interpretation(response: Any, claimed_meaning: str | None = None) -> dict[str, Any]:
    if claimed_meaning in FORBIDDEN_MEANINGS:
        return {"valid": False, "reason_codes": [f"MCP_RESULT_{claimed_meaning}_OVERINTERPRETATION"]}
    if not isinstance(response, dict):
        return {"valid": False, "reason_codes": ["MCP_RESULT_INVALID"]}
    operation = response.get("operation")
    status = response.get("status")
    result = response.get("result")
    if status == "CONTRACT_ONLY" and operation == "rehearse_agent":
        meaning = "CAPABILITY_CONTRACT_ONLY"
    elif status == "SUCCESS" and operation == "evaluate_evidence" and isinstance(result, dict) and result.get("claim_assessment") == "SUPPORTED":
        meaning = "PROFILE_REQUIREMENT_SATISFIED"
    elif status == "SUCCESS" and operation == "evaluate_rehearsal_run":
        meaning = "BOUNDED_RELIABILITY_CONTEXT"
    else:
        return {"valid": False, "reason_codes": ["MCP_RESULT_STATUS_UNSUPPORTED"]}
    return {
        "valid": True,
        "reason_codes": [],
        "status": "VALID",
        "meaning": meaning,
        "overinterpretation_rejected": True,
    }

