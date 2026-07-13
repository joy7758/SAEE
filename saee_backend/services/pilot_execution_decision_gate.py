"""Deterministic synthetic decision gate for a future SAEE controlled Pilot.

The gate models decisions but cannot create real approval or execution authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_TOP_LEVEL = {
    "decision_version",
    "scenario_id",
    "scenario_type",
    "synthetic_only",
    "readiness_status",
    "readiness_result_ref",
    "decision",
    "execution_authorized",
    "human_approval_required",
    "blocking_gaps",
    "approval_evidence",
    "human_responsibility",
    "safety_event",
    "synthetic_approval",
    "design_documents_as_approval",
    "real_approval_exists",
    "customer_validated",
    "production_ready",
    "external_execution",
}
APPROVAL_KEYS = {"security_approval", "data_approval", "execution_authorization"}

DECISION_GATE_INVALID = "DECISION_GATE_INVALID"
DECISION_GATE_STRUCTURE_INVALID = "DECISION_GATE_STRUCTURE_INVALID"
DECISION_GATE_EXECUTION_CLAIM_FORBIDDEN = "DECISION_GATE_EXECUTION_CLAIM_FORBIDDEN"
DECISION_GATE_PRODUCTION_CLAIM_FORBIDDEN = "DECISION_GATE_PRODUCTION_CLAIM_FORBIDDEN"
DECISION_GATE_CUSTOMER_VALIDATION_CLAIM_FORBIDDEN = "DECISION_GATE_CUSTOMER_VALIDATION_CLAIM_FORBIDDEN"
DECISION_GATE_REAL_APPROVAL_CLAIM_FORBIDDEN = "DECISION_GATE_REAL_APPROVAL_CLAIM_FORBIDDEN"
DECISION_GATE_HUMAN_BOUNDARY_REQUIRED = "DECISION_GATE_HUMAN_BOUNDARY_REQUIRED"
DECISION_GATE_APPROVAL_EVIDENCE_REQUIRED = "DECISION_GATE_APPROVAL_EVIDENCE_REQUIRED"
DECISION_GATE_DESIGN_DOCUMENT_APPROVAL_FORBIDDEN = "DECISION_GATE_DESIGN_DOCUMENT_APPROVAL_FORBIDDEN"
DECISION_GATE_READINESS_REFERENCE_INVALID = "DECISION_GATE_READINESS_REFERENCE_INVALID"
DECISION_GATE_DECLARED_DECISION_MISMATCH = "DECISION_GATE_DECLARED_DECISION_MISMATCH"


def _result(value: Any, valid: bool, decision: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "saee_pilot_execution_decision_gate_result_v0_1": True,
        "scenario_valid": valid,
        "scenario_id": value.get("scenario_id", "") if isinstance(value, dict) else "",
        "scenario_type": value.get("scenario_type", "") if isinstance(value, dict) else "",
        "decision": decision,
        "execution_authorized": False,
        "blocking_gaps": list(value.get("blocking_gaps", [])) if isinstance(value, dict) and isinstance(value.get("blocking_gaps"), list) else [],
        "reason_codes": reasons,
        "human_approval_required": True,
        "synthetic_decision_only": True,
        "real_approval_exists": False,
        "pilot_executed": False,
        "customer_validated": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _approval_set_valid(approvals: Any) -> bool:
    if not isinstance(approvals, dict) or set(approvals) != APPROVAL_KEYS:
        return False
    for approval in approvals.values():
        if not isinstance(approval, dict) or set(approval) != {"present", "evidence_reference"}:
            return False
        present = approval.get("present")
        reference = approval.get("evidence_reference")
        if present is True:
            if not isinstance(reference, str) or not reference.startswith("synthetic:approval:"):
                return False
        elif present is False:
            if reference is not None:
                return False
        else:
            return False
    return True


def evaluate_pilot_execution_decision(value: Any) -> dict[str, Any]:
    """Evaluate one synthetic request under a default-HOLD policy."""

    if not isinstance(value, dict):
        return _result(value, False, "HOLD", [DECISION_GATE_INVALID])
    if value.get("execution_authorized") is not False or value.get("external_execution") is not False:
        return _result(value, False, "HOLD", [DECISION_GATE_EXECUTION_CLAIM_FORBIDDEN])
    if value.get("production_ready") is not False:
        return _result(value, False, "HOLD", [DECISION_GATE_PRODUCTION_CLAIM_FORBIDDEN])
    if value.get("customer_validated") is not False:
        return _result(value, False, "HOLD", [DECISION_GATE_CUSTOMER_VALIDATION_CLAIM_FORBIDDEN])
    if value.get("real_approval_exists") is not False or value.get("synthetic_only") is not True:
        return _result(value, False, "HOLD", [DECISION_GATE_REAL_APPROVAL_CLAIM_FORBIDDEN])
    if value.get("human_approval_required") is not True:
        return _result(value, False, "HOLD", [DECISION_GATE_HUMAN_BOUNDARY_REQUIRED])
    if value.get("design_documents_as_approval") is not False:
        return _result(value, False, "HOLD", [DECISION_GATE_DESIGN_DOCUMENT_APPROVAL_FORBIDDEN])
    if set(value) != EXPECTED_TOP_LEVEL or value.get("decision_version") != "0.1":
        return _result(value, False, "HOLD", [DECISION_GATE_STRUCTURE_INVALID])

    readiness_ref = value.get("readiness_result_ref")
    if readiness_ref is not None:
        if not isinstance(readiness_ref, str) or not (ROOT / readiness_ref).is_file():
            return _result(value, False, "HOLD", [DECISION_GATE_READINESS_REFERENCE_INVALID])
        try:
            readiness = json.loads((ROOT / readiness_ref).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return _result(value, False, "HOLD", [DECISION_GATE_READINESS_REFERENCE_INVALID])
        if readiness.get("readiness_status") != value.get("readiness_status"):
            return _result(value, False, "HOLD", [DECISION_GATE_READINESS_REFERENCE_INVALID])

    approvals = value.get("approval_evidence")
    if not _approval_set_valid(approvals):
        return _result(value, False, "HOLD", [DECISION_GATE_APPROVAL_EVIDENCE_REQUIRED])

    human = value.get("human_responsibility")
    if not isinstance(human, dict) or set(human) != {"owner_assigned", "owner_reference"}:
        return _result(value, False, "HOLD", [DECISION_GATE_HUMAN_BOUNDARY_REQUIRED])
    if human.get("owner_assigned") is True:
        if not isinstance(human.get("owner_reference"), str) or not human["owner_reference"].startswith("synthetic:owner:"):
            return _result(value, False, "HOLD", [DECISION_GATE_HUMAN_BOUNDARY_REQUIRED])
    elif human.get("owner_assigned") is False:
        if human.get("owner_reference") is not None:
            return _result(value, False, "HOLD", [DECISION_GATE_HUMAN_BOUNDARY_REQUIRED])
    else:
        return _result(value, False, "HOLD", [DECISION_GATE_HUMAN_BOUNDARY_REQUIRED])

    gaps = value.get("blocking_gaps")
    if not isinstance(gaps, list) or len(gaps) != len(set(gaps)) or any(not isinstance(gap, str) or not gap for gap in gaps):
        return _result(value, False, "HOLD", [DECISION_GATE_STRUCTURE_INVALID])

    if value.get("safety_event") in {"SECRET_EXPOSURE", "BOUNDARY_BREACH"}:
        computed_decision = "TERMINATED"
        reasons = [f"DECISION_GATE_{value['safety_event']}_TERMINATED"]
    elif gaps or value.get("readiness_status") == "NOT_READY":
        computed_decision = "HOLD"
        reasons = ["DECISION_GATE_CRITICAL_GAPS_HOLD"]
    else:
        approvals_complete = all(item.get("present") is True for item in approvals.values())
        human_complete = human.get("owner_assigned") is True
        if (
            value.get("readiness_status") == "READY"
            and approvals_complete
            and human_complete
            and value.get("synthetic_approval") is True
        ):
            computed_decision = "APPROVED_FOR_EXECUTION"
            reasons = ["DECISION_GATE_SYNTHETIC_REQUIREMENTS_MET_NO_REAL_AUTHORIZATION"]
        else:
            computed_decision = "CONDITIONAL_HOLD"
            reasons = ["DECISION_GATE_NONCRITICAL_PREPARATION_INCOMPLETE"]

    if value.get("decision") != computed_decision:
        return _result(value, False, "HOLD", [DECISION_GATE_DECLARED_DECISION_MISMATCH])
    return _result(value, True, computed_decision, reasons)


def validate_decision_result_truth(value: Any) -> dict[str, Any]:
    """Validate the checked-in current HOLD result without granting authority."""

    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": [DECISION_GATE_INVALID]}
    if value.get("decision") != "HOLD":
        return {"valid": False, "reason_codes": ["DECISION_GATE_CURRENT_DECISION_MUST_HOLD"]}
    false_fields = (
        "execution_authorized",
        "real_approval_exists",
        "pilot_executed",
        "customer_validated",
        "external_validation_completed",
        "production_ready",
    )
    for field in false_fields:
        if value.get(field) is not False:
            return {"valid": False, "reason_codes": [f"DECISION_GATE_REAL_WORLD_CLAIM_FORBIDDEN:{field}"]}
    if value.get("synthetic_only") is not True:
        return {"valid": False, "reason_codes": [DECISION_GATE_REAL_APPROVAL_CLAIM_FORBIDDEN]}
    return {"valid": True, "reason_codes": []}


def evaluate_pilot_execution_decision_path(path: Path) -> dict[str, Any]:
    """Evaluate one checked-in local synthetic scenario."""

    return evaluate_pilot_execution_decision(json.loads(path.read_text(encoding="utf-8")))
