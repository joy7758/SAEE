"""Offline validator for SAEE Controlled External Agent Pilot Design v0.1.

The validator checks a design contract. It never authorizes or executes a Pilot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_TOP_LEVEL = {
    "saee_controlled_external_agent_pilot_design_v0_1",
    "design_version",
    "pilot_stage",
    "documentation_ref",
    "scope",
    "agent_eligibility",
    "data_boundary",
    "environment_requirements",
    "approval_gates",
    "human_boundary",
    "evaluation_metrics",
    "exit_criteria",
    "rollback_model",
    "readiness_gate",
    "pilot_start_authorized",
    "external_agent_connected",
    "pilot_executed",
    "data_collected",
    "approval_granted",
    "customer_validated",
    "external_validation_completed",
    "production_enabled",
    "production_ready",
    "network_accessed",
    "external_execution",
}

EXPECTED_ALLOWED_SCOPE = {
    "SYNTHETIC_OR_EXPLICITLY_APPROVED_EVIDENCE",
    "BOUNDED_AGENT_WORKFLOW",
    "ONE_FIXED_SAEE_CAPABILITY",
    "HUMAN_SUPERVISED_EVALUATION",
}
EXPECTED_FORBIDDEN_SCOPE = {
    "UNRESTRICTED_PRODUCTION_AGENT",
    "AUTONOMOUS_DEPLOYMENT",
    "UNCONTROLLED_CUSTOMER_DATA",
    "EXTERNAL_SIDE_EFFECT",
    "DYNAMIC_TOOL_OR_PROFILE_REGISTRATION",
}
EXPECTED_AGENT_DECLARATIONS = {
    "agent_identity_declaration",
    "purpose_declaration",
    "capability_description",
    "invocation_context",
}
EXPECTED_ALLOWED_DATA = {
    "approved_evidence_objects",
    "approved_inert_references",
    "synthetic_datasets",
    "controlled_samples",
}
EXPECTED_FORBIDDEN_DATA = {
    "secrets",
    "private_keys",
    "hidden_reasoning",
    "unrestricted_customer_data",
    "unapproved_personal_data",
    "executable_content",
}
EXPECTED_ENVIRONMENT_REQUIREMENTS = {
    "ISOLATED_ENVIRONMENT",
    "REPRODUCIBLE_CONFIGURATION",
    "BOUNDED_LOGGING",
    "LEAST_PRIVILEGE_PERMISSIONS",
    "FAIL_CLOSED_HANDLING",
    "RECOVERY_AND_ROLLBACK",
}
EXPECTED_GATES = {
    "TECHNICAL_READINESS",
    "SECURITY_REVIEW",
    "DATA_APPROVAL",
    "HUMAN_RESPONSIBILITY_ASSIGNMENT",
    "EXECUTION_AUTHORIZATION",
}
EXPECTED_TECHNICAL_METRICS = {
    "TOOL_INVOCATION_CORRECTNESS",
    "CONTRACT_COMPLIANCE",
    "BOUNDARY_PRESERVATION",
}
EXPECTED_EVIDENCE_METRICS = {
    "MISSING_EVIDENCE_IDENTIFICATION",
    "REASON_CODE_CONSISTENCY",
}
EXPECTED_SUCCESS_CRITERIA = {
    "REPRODUCIBLE_EXECUTION",
    "BOUNDARY_VIOLATIONS_DETECTED",
    "EVIDENCE_RESULTS_GENERATED",
    "LIMITATIONS_DOCUMENTED",
}
EXPECTED_FAILURE_CONDITIONS = {
    "UNAUTHORIZED_ACTION",
    "DATA_BOUNDARY_VIOLATION",
    "SECRET_EXPOSURE",
    "UNSUPPORTED_CLAIM",
}

PILOT_DESIGN_INVALID = "PILOT_DESIGN_INVALID"
PILOT_DESIGN_STRUCTURE_INVALID = "PILOT_DESIGN_STRUCTURE_INVALID"
PILOT_DESIGN_STAGE_INVALID = "PILOT_DESIGN_STAGE_INVALID"
PILOT_DESIGN_PILOT_COMPLETION_FORBIDDEN = "PILOT_DESIGN_PILOT_COMPLETION_FORBIDDEN"
PILOT_DESIGN_EXTERNAL_CONNECTION_FORBIDDEN = "PILOT_DESIGN_EXTERNAL_CONNECTION_FORBIDDEN"
PILOT_DESIGN_CUSTOMER_VALIDATION_FORBIDDEN = "PILOT_DESIGN_CUSTOMER_VALIDATION_FORBIDDEN"
PILOT_DESIGN_APPROVAL_CLAIM_FORBIDDEN = "PILOT_DESIGN_APPROVAL_CLAIM_FORBIDDEN"
PILOT_DESIGN_EXTERNAL_DATA_CLAIM_FORBIDDEN = "PILOT_DESIGN_EXTERNAL_DATA_CLAIM_FORBIDDEN"
PILOT_DESIGN_PRODUCTION_CLAIM_FORBIDDEN = "PILOT_DESIGN_PRODUCTION_CLAIM_FORBIDDEN"
PILOT_DESIGN_HUMAN_BOUNDARY_REQUIRED = "PILOT_DESIGN_HUMAN_BOUNDARY_REQUIRED"
PILOT_DESIGN_GATES_INVALID = "PILOT_DESIGN_GATES_INVALID"
PILOT_DESIGN_DATA_BOUNDARY_INVALID = "PILOT_DESIGN_DATA_BOUNDARY_INVALID"
PILOT_DESIGN_ROLLBACK_INVALID = "PILOT_DESIGN_ROLLBACK_INVALID"
PILOT_DESIGN_BOUNDARY_INVALID = "PILOT_DESIGN_BOUNDARY_INVALID"


def _result(value: Any, valid: bool, reason_codes: list[str]) -> dict[str, Any]:
    return {
        "saee_controlled_external_agent_pilot_design_validation_result_v0_1": True,
        "design_valid": valid,
        "design_version": value.get("design_version", "") if isinstance(value, dict) else "",
        "pilot_stage": "design_only",
        "readiness_gate": "HOLD",
        "reason_codes": reason_codes,
        "pilot_start_authorized": False,
        "external_agent_connected": False,
        "pilot_executed": False,
        "data_collected": False,
        "approval_granted": False,
        "customer_validated": False,
        "external_validation_completed": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _exact_set(value: Any, expected: set[str]) -> bool:
    return isinstance(value, list) and set(value) == expected and len(value) == len(expected)


def validate_pilot_design(value: Any) -> dict[str, Any]:
    """Validate a design-only Pilot contract without performing external work."""

    if not isinstance(value, dict):
        return _result(value, False, [PILOT_DESIGN_INVALID])
    if value.get("pilot_executed") is not False:
        return _result(value, False, [PILOT_DESIGN_PILOT_COMPLETION_FORBIDDEN])
    if value.get("external_agent_connected") is not False or value.get("external_execution") is not False:
        return _result(value, False, [PILOT_DESIGN_EXTERNAL_CONNECTION_FORBIDDEN])
    if value.get("customer_validated") is not False or value.get("external_validation_completed") is not False:
        return _result(value, False, [PILOT_DESIGN_CUSTOMER_VALIDATION_FORBIDDEN])
    if value.get("approval_granted") is not False or value.get("pilot_start_authorized") is not False:
        return _result(value, False, [PILOT_DESIGN_APPROVAL_CLAIM_FORBIDDEN])
    if value.get("data_collected") is not False:
        return _result(value, False, [PILOT_DESIGN_EXTERNAL_DATA_CLAIM_FORBIDDEN])
    if value.get("production_enabled") is not False or value.get("production_ready") is not False:
        return _result(value, False, [PILOT_DESIGN_PRODUCTION_CLAIM_FORBIDDEN])
    if set(value) != EXPECTED_TOP_LEVEL:
        return _result(value, False, [PILOT_DESIGN_STRUCTURE_INVALID])
    if (
        value.get("saee_controlled_external_agent_pilot_design_v0_1") is not True
        or value.get("design_version") != "0.1"
        or value.get("pilot_stage") != "design_only"
        or value.get("readiness_gate") != "HOLD"
        or value.get("network_accessed") is not False
    ):
        return _result(value, False, [PILOT_DESIGN_STAGE_INVALID])

    scope = value.get("scope")
    eligibility = value.get("agent_eligibility")
    if (
        not isinstance(scope, dict)
        or not _exact_set(scope.get("allowed"), EXPECTED_ALLOWED_SCOPE)
        or not _exact_set(scope.get("forbidden"), EXPECTED_FORBIDDEN_SCOPE)
        or scope.get("fixed_capability_id") != "saee.evidence-adequacy"
        or scope.get("human_supervision_required") is not True
        or not isinstance(eligibility, dict)
        or not _exact_set(eligibility.get("required_declarations"), EXPECTED_AGENT_DECLARATIONS)
        or eligibility.get("declarations_establish_authentication") is not False
        or eligibility.get("declarations_establish_trust") is not False
        or eligibility.get("external_agent_trusted") is not False
        or not _exact_set(value.get("environment_requirements"), EXPECTED_ENVIRONMENT_REQUIREMENTS)
    ):
        return _result(value, False, [PILOT_DESIGN_BOUNDARY_INVALID])

    data = value.get("data_boundary")
    if (
        not isinstance(data, dict)
        or not _exact_set(data.get("allowed_data_classes"), EXPECTED_ALLOWED_DATA)
        or not _exact_set(data.get("forbidden_data_classes"), EXPECTED_FORBIDDEN_DATA)
        or data.get("approved_reference_required") is not True
        or data.get("customer_data_allowed") is not False
        or data.get("secrets_allowed") is not False
        or data.get("data_collected") is not False
    ):
        return _result(value, False, [PILOT_DESIGN_DATA_BOUNDARY_INVALID])

    gates = value.get("approval_gates")
    if (
        not isinstance(gates, list)
        or len(gates) != len(EXPECTED_GATES)
        or {gate.get("gate_id") for gate in gates if isinstance(gate, dict)} != EXPECTED_GATES
        or any(
            not isinstance(gate, dict)
            or set(gate) != {"gate_id", "required", "status"}
            or gate.get("required") is not True
            or gate.get("status") != "NOT_GRANTED"
            for gate in gates
        )
    ):
        return _result(value, False, [PILOT_DESIGN_GATES_INVALID])

    human = value.get("human_boundary")
    if (
        not isinstance(human, dict)
        or human.get("responsible_human_assignment_required") is not True
        or human.get("responsible_human_assigned") is not False
        or human.get("human_review_required") is not True
        or human.get("human_review_bypass_allowed") is not False
        or human.get("decision_authority") != "AUTHORIZED_HUMAN_ONLY"
    ):
        return _result(value, False, [PILOT_DESIGN_HUMAN_BOUNDARY_REQUIRED])

    metrics = value.get("evaluation_metrics")
    exits = value.get("exit_criteria")
    if (
        not isinstance(metrics, dict)
        or not _exact_set(metrics.get("technical"), EXPECTED_TECHNICAL_METRICS)
        or not _exact_set(metrics.get("evidence"), EXPECTED_EVIDENCE_METRICS)
        or metrics.get("human") != ["REVIEW_USEFULNESS"]
        or set(metrics.get("business_metrics_excluded", [])) != {"REVENUE", "MARKET_FIT", "BUSINESS_SUCCESS"}
        or not isinstance(exits, dict)
        or not _exact_set(exits.get("success_requires"), EXPECTED_SUCCESS_CRITERIA)
        or not _exact_set(exits.get("failure_conditions"), EXPECTED_FAILURE_CONDITIONS)
    ):
        return _result(value, False, [PILOT_DESIGN_BOUNDARY_INVALID])

    rollback = value.get("rollback_model")
    if (
        not isinstance(rollback, dict)
        or rollback.get("stop_condition_required") is not True
        or rollback.get("data_deletion_plan_required") is not True
        or rollback.get("access_revocation_required") is not True
        or rollback.get("artifact_retention_policy_required") is not True
        or rollback.get("plans_approved") is not False
        or rollback.get("termination_authority_assigned") is not False
    ):
        return _result(value, False, [PILOT_DESIGN_ROLLBACK_INVALID])

    doc_ref = value.get("documentation_ref")
    if not isinstance(doc_ref, str) or not (ROOT / doc_ref).is_file():
        return _result(value, False, [PILOT_DESIGN_STRUCTURE_INVALID])
    return _result(value, True, [])


def validate_pilot_design_json(text: str) -> dict[str, Any]:
    """Parse and validate a JSON design contract."""

    try:
        value = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return _result(None, False, [PILOT_DESIGN_INVALID])
    return validate_pilot_design(value)


def validate_pilot_design_path(path: Path) -> dict[str, Any]:
    """Validate one local JSON file without reading any external resource."""

    return validate_pilot_design_json(path.read_text(encoding="utf-8"))
