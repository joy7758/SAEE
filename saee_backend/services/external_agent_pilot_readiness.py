"""Read-only evaluator for SAEE External Agent Pilot Readiness Review v0.1.

This module reports missing evidence. It cannot approve or execute a Pilot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "review_stage",
    "documentation_ref",
    "dimensions",
    "readiness_score",
    "blocking_conditions",
    "human_boundary",
    "pilot_authorized",
    "external_agent_connected",
    "external_validation_completed",
    "customer_validated",
    "production_ready",
    "network_accessed",
    "external_execution",
}
EXPECTED_DIMENSIONS = {"identity", "security", "data", "runtime", "human_governance"}
EXPECTED_CHECKS = {
    "identity": {"identity_model_exists", "authentication_plan_exists", "trust_boundary_defined"},
    "security": {"security_review_completed", "credential_policy_approved", "incident_handling_implemented"},
    "data": {"data_ownership_established", "data_permission_approved", "retention_policy_approved", "deletion_process_implemented"},
    "runtime": {"environment_isolation_implemented", "monitoring_implemented", "recovery_implemented"},
    "human_governance": {"responsible_owner_assigned", "approval_path_defined", "escalation_owner_assigned"},
}
EXPECTED_CURRENT_STATUS = {
    "identity": "PARTIAL",
    "security": "NOT_READY",
    "data": "NOT_READY",
    "runtime": "NOT_READY",
    "human_governance": "PARTIAL",
}
REQUIRED_BLOCKERS = {
    "AUTHENTICATION_PLAN_MISSING",
    "VERIFIED_EXTERNAL_IDENTITY_MISSING",
    "SECURITY_REVIEW_MISSING",
    "CREDENTIAL_POLICY_MISSING",
    "INCIDENT_HANDLING_MISSING",
    "DATA_OWNERSHIP_EVIDENCE_MISSING",
    "DATA_PERMISSION_EVIDENCE_MISSING",
    "RETENTION_POLICY_APPROVAL_MISSING",
    "DELETION_IMPLEMENTATION_EVIDENCE_MISSING",
    "ENVIRONMENT_ISOLATION_EVIDENCE_MISSING",
    "MONITORING_EVIDENCE_MISSING",
    "RECOVERY_EVIDENCE_MISSING",
    "RESPONSIBLE_OWNER_MISSING",
    "ESCALATION_OWNER_MISSING",
    "EXECUTION_AUTHORITY_MISSING",
}

PILOT_READINESS_INVALID = "PILOT_READINESS_INVALID"
PILOT_READINESS_STRUCTURE_INVALID = "PILOT_READINESS_STRUCTURE_INVALID"
PILOT_READINESS_APPROVAL_CLAIM_FORBIDDEN = "PILOT_READINESS_APPROVAL_CLAIM_FORBIDDEN"
PILOT_READINESS_EXTERNAL_VALIDATION_CLAIM_FORBIDDEN = "PILOT_READINESS_EXTERNAL_VALIDATION_CLAIM_FORBIDDEN"
PILOT_READINESS_PRODUCTION_CLAIM_FORBIDDEN = "PILOT_READINESS_PRODUCTION_CLAIM_FORBIDDEN"
PILOT_READINESS_HUMAN_BOUNDARY_REQUIRED = "PILOT_READINESS_HUMAN_BOUNDARY_REQUIRED"
PILOT_READINESS_DIMENSIONS_INVALID = "PILOT_READINESS_DIMENSIONS_INVALID"
PILOT_READINESS_SECURITY_GATE_REQUIRED = "PILOT_READINESS_SECURITY_GATE_REQUIRED"
PILOT_READINESS_DIMENSION_STATUS_INVALID = "PILOT_READINESS_DIMENSION_STATUS_INVALID"
PILOT_READINESS_EVIDENCE_INVALID = "PILOT_READINESS_EVIDENCE_INVALID"
PILOT_READINESS_SCORE_INVALID = "PILOT_READINESS_SCORE_INVALID"
PILOT_READINESS_BLOCKERS_INVALID = "PILOT_READINESS_BLOCKERS_INVALID"


def _result(value: Any, valid: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "saee_external_agent_pilot_readiness_result_v0_1": True,
        "review_valid": valid,
        "readiness_result": "NOT_READY",
        "review_version": value.get("schema_version", "") if isinstance(value, dict) else "",
        "dimension_status": {},
        "readiness_score": 0,
        "blocking_gaps": [],
        "missing_evidence": [],
        "reason_codes": reasons,
        "pilot_authorized": False,
        "external_agent_connected": False,
        "external_validation_completed": False,
        "customer_validated": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _derived_status(checks: list[dict[str, Any]]) -> str:
    satisfied = sum(check.get("satisfied") is True for check in checks)
    if satisfied == len(checks):
        return "READY"
    if satisfied:
        return "PARTIAL"
    return "NOT_READY"


def evaluate_external_agent_pilot_readiness(value: Any) -> dict[str, Any]:
    """Evaluate declared local evidence without creating operational readiness."""

    if not isinstance(value, dict):
        return _result(value, False, [PILOT_READINESS_INVALID])
    if value.get("pilot_authorized") is not False:
        return _result(value, False, [PILOT_READINESS_APPROVAL_CLAIM_FORBIDDEN])
    if (
        value.get("external_validation_completed") is not False
        or value.get("customer_validated") is not False
        or value.get("external_agent_connected") is not False
    ):
        return _result(value, False, [PILOT_READINESS_EXTERNAL_VALIDATION_CLAIM_FORBIDDEN])
    if value.get("production_ready") is not False:
        return _result(value, False, [PILOT_READINESS_PRODUCTION_CLAIM_FORBIDDEN])
    if set(value) != EXPECTED_TOP_LEVEL or value.get("schema_version") != "0.1" or value.get("review_stage") != "read_only_gap_assessment":
        return _result(value, False, [PILOT_READINESS_STRUCTURE_INVALID])

    human = value.get("human_boundary")
    if (
        not isinstance(human, dict)
        or human.get("human_review_required") is not True
        or human.get("responsible_owner_assigned") is not False
        or human.get("execution_authority_assigned") is not False
        or human.get("automatic_approval_allowed") is not False
    ):
        return _result(value, False, [PILOT_READINESS_HUMAN_BOUNDARY_REQUIRED])

    dimensions = value.get("dimensions")
    if not isinstance(dimensions, dict) or set(dimensions) != EXPECTED_DIMENSIONS:
        return _result(value, False, [PILOT_READINESS_DIMENSIONS_INVALID])

    all_checks: list[dict[str, Any]] = []
    missing_evidence: list[str] = []
    statuses: dict[str, str] = {}
    for dimension_name in sorted(EXPECTED_DIMENSIONS):
        dimension = dimensions.get(dimension_name)
        if not isinstance(dimension, dict):
            return _result(value, False, [PILOT_READINESS_DIMENSIONS_INVALID])
        checks = dimension.get("checks")
        if not isinstance(checks, list):
            return _result(value, False, [PILOT_READINESS_DIMENSIONS_INVALID])
        check_ids = {check.get("check_id") for check in checks if isinstance(check, dict)}
        if check_ids != EXPECTED_CHECKS[dimension_name] or len(checks) != len(EXPECTED_CHECKS[dimension_name]):
            reason = PILOT_READINESS_SECURITY_GATE_REQUIRED if dimension_name == "security" else PILOT_READINESS_DIMENSIONS_INVALID
            return _result(value, False, [reason])
        derived = _derived_status(checks)
        if dimension.get("status") != derived or derived != EXPECTED_CURRENT_STATUS[dimension_name] or dimension.get("blocking") is not True:
            return _result(value, False, [PILOT_READINESS_DIMENSION_STATUS_INVALID])
        statuses[dimension_name] = derived

        declared_refs = dimension.get("evidence_refs")
        if not isinstance(declared_refs, list) or not isinstance(dimension.get("design_context_refs"), list):
            return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
        used_refs: set[str] = set()
        for check in checks:
            refs = check.get("evidence_refs")
            if not isinstance(refs, list):
                return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
            if check.get("satisfied") is True:
                if not refs or any(not isinstance(ref, str) or not (ROOT / ref).is_file() for ref in refs):
                    return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
                used_refs.update(refs)
            elif refs:
                return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
        if set(declared_refs) != used_refs:
            return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
        for ref in dimension["design_context_refs"]:
            if not isinstance(ref, str) or not (ROOT / ref).is_file():
                return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
        declared_missing = dimension.get("missing_evidence")
        if derived != "READY" and (not isinstance(declared_missing, list) or not declared_missing):
            return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])
        missing_evidence.extend(f"{dimension_name}:{item}" for item in declared_missing)
        all_checks.extend(checks)

    satisfied = sum(check.get("satisfied") is True for check in all_checks)
    required = len(all_checks)
    percentage = round((satisfied / required) * 100)
    score = value.get("readiness_score")
    if (
        not isinstance(score, dict)
        or score.get("method") != "SATISFIED_CHECKS_OVER_REQUIRED_CHECKS"
        or score.get("satisfied_checks") != satisfied
        or score.get("required_checks") != required
        or score.get("percentage") != percentage
        or score.get("is_probability") is not False
        or score.get("operational_readiness_established") is not False
    ):
        return _result(value, False, [PILOT_READINESS_SCORE_INVALID])

    blockers = value.get("blocking_conditions")
    if not isinstance(blockers, list) or set(blockers) != REQUIRED_BLOCKERS or len(blockers) != len(REQUIRED_BLOCKERS):
        return _result(value, False, [PILOT_READINESS_BLOCKERS_INVALID])

    doc_ref = value.get("documentation_ref")
    if not isinstance(doc_ref, str) or not (ROOT / doc_ref).is_file():
        return _result(value, False, [PILOT_READINESS_EVIDENCE_INVALID])

    result = _result(value, True, [])
    result.update({
        "dimension_status": statuses,
        "readiness_score": percentage,
        "blocking_gaps": sorted(blockers),
        "missing_evidence": sorted(missing_evidence),
    })
    return result


def validate_readiness_result_truth(value: Any) -> dict[str, Any]:
    """Reject result documents that overclaim readiness, approval, or validation."""

    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": [PILOT_READINESS_INVALID]}
    if value.get("readiness_status") != "NOT_READY":
        return {"valid": False, "reason_codes": ["PILOT_READINESS_STATUS_OVERCLAIM"]}
    truth_fields = (
        "pilot_authorized",
        "external_agent_connected",
        "external_validation_completed",
        "customer_validated",
        "production_ready",
    )
    for field in truth_fields:
        if value.get(field) is not False:
            return {"valid": False, "reason_codes": [f"PILOT_READINESS_REAL_WORLD_CLAIM_FORBIDDEN:{field}"]}
    return {"valid": True, "reason_codes": []}


def evaluate_external_agent_pilot_readiness_path(path: Path) -> dict[str, Any]:
    """Evaluate one checked-in local readiness matrix."""

    return evaluate_external_agent_pilot_readiness(json.loads(path.read_text(encoding="utf-8")))
