"""Offline validator for SAEE External Agent Integration Design v0.1."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_TOP_LEVEL = {
    "saee_external_agent_integration_design_v0_1",
    "design_version",
    "design_status",
    "documentation_ref",
    "architecture_flow",
    "identity_model",
    "invocation_boundary",
    "data_boundary",
    "tenant_model",
    "secret_model",
    "human_control_model",
    "readiness_gate",
    "external_agent_connected",
    "authentication_available",
    "oauth_available",
    "public_mcp_server_available",
    "trusted_external_agent",
    "autonomous_execution",
    "production_enabled",
    "production_ready",
}
EXPECTED_IDENTITY_FIELDS = {"agent_id", "agent_type", "declared_purpose", "organization_context", "capability_context"}
EXPECTED_ALLOWED_OPERATIONS = {
    "SUBMIT_BOUNDED_EVIDENCE",
    "REQUEST_EVIDENCE_ASSESSMENT",
    "SELECT_FIXED_PROFILE",
    "RETRIEVE_BOUNDED_RESULT",
}
EXPECTED_FORBIDDEN_OPERATIONS = {
    "AUTHORIZE_ACTION",
    "APPROVE_DEPLOYMENT",
    "MODIFY_SOURCE_EVIDENCE",
    "BYPASS_HUMAN_REVIEW",
    "REGISTER_DYNAMIC_TOOL",
    "EXECUTE_EXTERNAL_ACTION",
}
EXPECTED_ALLOWED_INPUTS = {"evidence_object", "accountability_claim", "evaluation_profile", "approved_references"}
EXPECTED_FORBIDDEN_INPUTS = {
    "secrets",
    "private_keys",
    "hidden_reasoning",
    "uncontrolled_customer_data",
    "unrestricted_external_resources",
    "executable_content",
    "cross_tenant_data",
}
EXPECTED_READINESS_CONTROLS = {
    "APPROVED_DATA_POLICY",
    "IDENTITY_AUTHENTICATION_DESIGN",
    "TENANT_ISOLATION_DESIGN",
    "SECRET_MANAGEMENT_DESIGN",
    "SECURITY_PRIVACY_REVIEW",
    "LOGGING_FAILURE_INCIDENT_MODEL",
    "HUMAN_ESCALATION_APPROVAL_PATH",
}
FORBIDDEN_CREDENTIAL_KEYS = {
    "api_key", "access_token", "refresh_token", "client_secret", "password", "private_key", "credential_value", "authorization_header"
}
SECRET_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{8,}", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bbce-v3/"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
)

EXTERNAL_INTEGRATION_INVALID = "EXTERNAL_INTEGRATION_INVALID"
EXTERNAL_INTEGRATION_STRUCTURE_INVALID = "EXTERNAL_INTEGRATION_STRUCTURE_INVALID"
EXTERNAL_INTEGRATION_CONNECTED_CLAIM_FORBIDDEN = "EXTERNAL_INTEGRATION_CONNECTED_CLAIM_FORBIDDEN"
EXTERNAL_INTEGRATION_TRUST_CLAIM_FORBIDDEN = "EXTERNAL_INTEGRATION_TRUST_CLAIM_FORBIDDEN"
EXTERNAL_INTEGRATION_PRODUCTION_CLAIM_FORBIDDEN = "EXTERNAL_INTEGRATION_PRODUCTION_CLAIM_FORBIDDEN"
EXTERNAL_INTEGRATION_HUMAN_BOUNDARY_REQUIRED = "EXTERNAL_INTEGRATION_HUMAN_BOUNDARY_REQUIRED"
EXTERNAL_INTEGRATION_CREDENTIAL_EXPOSURE = "EXTERNAL_INTEGRATION_CREDENTIAL_EXPOSURE"
EXTERNAL_INTEGRATION_AUTONOMOUS_EXECUTION_FORBIDDEN = "EXTERNAL_INTEGRATION_AUTONOMOUS_EXECUTION_FORBIDDEN"
EXTERNAL_INTEGRATION_AUTHORIZATION_CLAIM_FORBIDDEN = "EXTERNAL_INTEGRATION_AUTHORIZATION_CLAIM_FORBIDDEN"
EXTERNAL_INTEGRATION_AUTHENTICATION_IMPLEMENTATION_FORBIDDEN = "EXTERNAL_INTEGRATION_AUTHENTICATION_IMPLEMENTATION_FORBIDDEN"
EXTERNAL_INTEGRATION_BOUNDARY_INVALID = "EXTERNAL_INTEGRATION_BOUNDARY_INVALID"


def _result(value: Any, valid: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "saee_external_agent_integration_design_validation_result_v0_1": True,
        "design_valid": valid,
        "design_version": value.get("design_version", "") if isinstance(value, dict) else "",
        "reason_codes": reasons,
        "external_agent_connected": False,
        "authentication_available": False,
        "trusted_external_agent": False,
        "autonomous_execution": False,
        "human_approval_required": True,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _contains_credential(value: Any) -> bool:
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if any(key.lower() in FORBIDDEN_CREDENTIAL_KEYS for key in current):
                return True
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
        elif isinstance(current, str) and any(pattern.search(current) for pattern in SECRET_VALUE_PATTERNS):
            return True
    return False


def _all_false(mapping: Any, fields: tuple[str, ...]) -> bool:
    return isinstance(mapping, dict) and all(mapping.get(field) is False for field in fields)


def validate_external_agent_integration_design(value: Any) -> dict[str, Any]:
    """Validate the design boundary without connecting an external Agent."""

    if not isinstance(value, dict):
        return _result(value, False, [EXTERNAL_INTEGRATION_INVALID])
    if _contains_credential(value):
        return _result(value, False, [EXTERNAL_INTEGRATION_CREDENTIAL_EXPOSURE])
    if value.get("external_agent_connected") is not False or value.get("public_mcp_server_available") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_CONNECTED_CLAIM_FORBIDDEN])
    if value.get("trusted_external_agent") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_TRUST_CLAIM_FORBIDDEN])
    if value.get("production_enabled") is not False or value.get("production_ready") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_PRODUCTION_CLAIM_FORBIDDEN])
    if value.get("autonomous_execution") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_AUTONOMOUS_EXECUTION_FORBIDDEN])
    if value.get("authentication_available") is not False or value.get("oauth_available") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_AUTHENTICATION_IMPLEMENTATION_FORBIDDEN])
    if set(value) != EXPECTED_TOP_LEVEL or value.get("design_version") != "0.1" or value.get("design_status") != "design_only":
        return _result(value, False, [EXTERNAL_INTEGRATION_STRUCTURE_INVALID])

    human = value.get("human_control_model")
    readiness = value.get("readiness_gate")
    if (
        not isinstance(human, dict)
        or human.get("human_approval_required") is not True
        or human.get("human_review_bypass_allowed") is not False
        or not isinstance(readiness, dict)
        or readiness.get("gate_status") != "HOLD"
        or readiness.get("real_integration_authorized") is not False
        or readiness.get("pilot_start_authorized") is not False
    ):
        return _result(value, False, [EXTERNAL_INTEGRATION_HUMAN_BOUNDARY_REQUIRED])

    identity = value.get("identity_model")
    invocation = value.get("invocation_boundary")
    if (
        not isinstance(identity, dict)
        or set(identity.get("required_fields", [])) != EXPECTED_IDENTITY_FIELDS
        or not _all_false(identity, (
            "identity_declaration_is_authentication",
            "identity_declaration_is_trust",
            "declared_purpose_is_trusted",
            "organization_context_grants_authority",
            "trusted_external_agent",
        ))
        or not isinstance(invocation, dict)
        or set(invocation.get("allowed_operations", [])) != EXPECTED_ALLOWED_OPERATIONS
        or set(invocation.get("forbidden_operations", [])) != EXPECTED_FORBIDDEN_OPERATIONS
        or invocation.get("capability_access_is_permission_grant") is not False
    ):
        return _result(value, False, [EXTERNAL_INTEGRATION_BOUNDARY_INVALID])
    if invocation.get("authorization_performed") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_AUTHORIZATION_CLAIM_FORBIDDEN])
    if invocation.get("autonomous_execution") is not False:
        return _result(value, False, [EXTERNAL_INTEGRATION_AUTONOMOUS_EXECUTION_FORBIDDEN])

    data = value.get("data_boundary")
    tenant = value.get("tenant_model")
    secrets = value.get("secret_model")
    if (
        not isinstance(data, dict)
        or set(data.get("allowed_inputs", [])) != EXPECTED_ALLOWED_INPUTS
        or set(data.get("forbidden_inputs", [])) != EXPECTED_FORBIDDEN_INPUTS
        or data.get("approved_references_required") is not True
        or not _all_false(data, ("references_fetched_automatically", "customer_data_allowed", "credentials_allowed"))
        or not isinstance(tenant, dict)
        or tenant.get("implementation_status") != "design_only"
        or tenant.get("tenant_system_implemented") is not False
        or tenant.get("namespace_isolation_required") is not True
        or tenant.get("cross_tenant_access_allowed") is not False
        or not isinstance(secrets, dict)
        or secrets.get("implementation_status") != "requirements_only"
        or secrets.get("credential_isolation_required") is not True
        or secrets.get("credential_rotation_required") is not True
        or secrets.get("least_privilege_required") is not True
        or secrets.get("repository_secret_storage_allowed") is not False
        or secrets.get("credentials_stored") is not False
        or secrets.get("secret_values_present") is not False
        or set(readiness.get("required_controls", [])) != EXPECTED_READINESS_CONTROLS
        or readiness.get("completed_controls") != []
    ):
        return _result(value, False, [EXTERNAL_INTEGRATION_BOUNDARY_INVALID])

    doc_ref = value.get("documentation_ref")
    if not isinstance(doc_ref, str) or not (ROOT / doc_ref).is_file():
        return _result(value, False, [EXTERNAL_INTEGRATION_STRUCTURE_INVALID])
    return _result(value, True, [])


def validate_external_agent_integration_design_json(text: str) -> dict[str, Any]:
    """Parse and validate one machine-readable integration design."""

    try:
        value = json.loads(text)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return _result({}, False, [EXTERNAL_INTEGRATION_INVALID])
    return validate_external_agent_integration_design(value)
