"""Local synthetic external-Agent boundary simulator for SAEE Phase 5.1."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.local_mcp_server import create_local_mcp_server


ROOT = Path(__file__).resolve().parents[2]
AGENT_SCHEMA_PATH = ROOT / "agent-interface/integration/synthetic-agent.schema.v0.1.json"
TENANT_SCHEMA_PATH = ROOT / "agent-interface/integration/tenant-context.schema.v0.1.json"
EXPECTED_SCENARIO_FIELDS = {
    "saee_external_agent_simulation_scenario_v0_1",
    "simulation_version",
    "scenario_id",
    "scenario_type",
    "synthetic_scenario",
    "agent_identity",
    "tenant_context",
    "request_intent",
    "security_payload",
    "mcp_request",
    "expected_outcome",
}
EXPECTED_SCENARIO_TYPES = {
    "TRUST_CONFUSION_AGENT",
    "PURPOSE_ESCALATION_AGENT",
    "TENANT_BOUNDARY_AGENT",
    "SECRET_EXPOSURE_AGENT",
    "CORRECT_EXTERNAL_AGENT",
}
EXPECTED_INTENT_FIELDS = {
    "requested_operation",
    "treats_purpose_as_permission",
    "autonomous_authorization_requested",
    "human_gate_bypass_requested",
    "human_gate_retained",
}
ALLOWED_REQUESTED_OPERATIONS = {"EVALUATE_EVIDENCE", "AUTHORIZE_ACTION", "APPROVE_DEPLOYMENT"}
FORBIDDEN_CREDENTIAL_KEYS = {
    "api_key", "access_token", "refresh_token", "client_secret", "password", "private_key", "credential_value", "authorization_header"
}
SECRET_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{8,}", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bbce-v3/"),
)


class ExternalAgentSimulationError(ValueError):
    pass


def _contains_secret(value: Any) -> bool:
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


def _schema_valid(value: Any, path: Path) -> bool:
    schema = json.loads(path.read_text(encoding="utf-8"))
    return not list(Draft202012Validator(schema).iter_errors(value))


def _validate_scenario_shape(scenario: Any) -> dict[str, Any]:
    if not isinstance(scenario, dict) or set(scenario) != EXPECTED_SCENARIO_FIELDS:
        raise ExternalAgentSimulationError("SIMULATION_SCENARIO_STRUCTURE_INVALID")
    if (
        scenario.get("saee_external_agent_simulation_scenario_v0_1") is not True
        or scenario.get("simulation_version") != "0.1"
        or scenario.get("scenario_type") not in EXPECTED_SCENARIO_TYPES
        or scenario.get("synthetic_scenario") is not True
        or scenario.get("expected_outcome") not in {"PASS", "FAIL", "REJECT"}
        or not isinstance(scenario.get("agent_identity"), dict)
        or not isinstance(scenario.get("tenant_context"), dict)
        or not isinstance(scenario.get("request_intent"), dict)
        or not isinstance(scenario.get("security_payload"), dict)
        or not isinstance(scenario.get("mcp_request"), dict)
        or set(scenario.get("request_intent", {})) != EXPECTED_INTENT_FIELDS
        or scenario["request_intent"].get("requested_operation") not in ALLOWED_REQUESTED_OPERATIONS
        or re.fullmatch(r"simulation:synthetic:[a-z0-9-]+", str(scenario.get("scenario_id", ""))) is None
    ):
        raise ExternalAgentSimulationError("SIMULATION_SCENARIO_STRUCTURE_INVALID")
    return scenario


def _base_result(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": scenario["scenario_id"],
        "scenario_type": scenario["scenario_type"],
        "agent_id": scenario["agent_identity"].get("agent_id", ""),
        "identity_result": "NOT_EVALUATED",
        "purpose_result": "NOT_EVALUATED",
        "tenant_result": "NOT_EVALUATED",
        "secret_result": "NOT_EVALUATED",
        "mcp_result": "NOT_CALLED",
        "boundary_result": "NOT_EVALUATED",
        "actual_outcome": "FAIL",
        "expected_outcome": scenario["expected_outcome"],
        "expected_outcome_matched": False,
        "reason_codes": [],
        "mcp_tool_result": "NOT_CALLED",
        "mcp_claim_assessment": "NOT_AVAILABLE",
        "mcp_reason_codes": [],
        "identity_authenticated": False,
        "agent_trusted": False,
        "tenant_runtime_used": False,
        "authorization_performed": False,
        "external_action_performed": False,
    }


def evaluate_external_agent_simulation(scenario: Any) -> dict[str, Any]:
    """Evaluate one synthetic scenario and call MCP only after all gates pass."""

    scenario = _validate_scenario_shape(scenario)
    result = _base_result(scenario)

    if _contains_secret(scenario):
        result["secret_result"] = "REJECT"
        result["actual_outcome"] = "REJECT"
        result["reason_codes"] = ["SIMULATION_SECRET_EXPOSURE_REJECTED"]
        result["expected_outcome_matched"] = result["expected_outcome"] == "REJECT"
        return result

    identity = scenario["agent_identity"]
    if identity.get("identity_as_trust") is True:
        result["identity_result"] = "FAIL"
        result["reason_codes"].append("SIMULATION_IDENTITY_TRUST_CONFUSION")
    elif identity.get("identity_as_authentication") is True:
        result["identity_result"] = "FAIL"
        result["reason_codes"].append("SIMULATION_IDENTITY_AUTHENTICATION_CONFUSION")
    elif _schema_valid(identity, AGENT_SCHEMA_PATH):
        result["identity_result"] = "PASS"
    else:
        result["identity_result"] = "FAIL"
        result["reason_codes"].append("SIMULATION_IDENTITY_INVALID")

    intent = scenario["request_intent"]
    if (
        intent.get("treats_purpose_as_permission") is True
        or intent.get("requested_operation") in {"AUTHORIZE_ACTION", "APPROVE_DEPLOYMENT"}
    ):
        result["purpose_result"] = "FAIL"
        result["reason_codes"].append("SIMULATION_PURPOSE_ESCALATION")
    else:
        result["purpose_result"] = "PASS"

    tenant = scenario["tenant_context"]
    expected_namespace = f"{tenant.get('tenant_id', '')}:evidence"
    if (
        tenant.get("cross_tenant_access") is True
        or tenant.get("tenant_id") != tenant.get("requested_tenant_id")
        or tenant.get("namespace") != expected_namespace
        or not _schema_valid(tenant, TENANT_SCHEMA_PATH)
    ):
        result["tenant_result"] = "FAIL"
        result["reason_codes"].append("SIMULATION_TENANT_BOUNDARY_VIOLATION")
    else:
        result["tenant_result"] = "PASS"

    result["secret_result"] = "PASS"
    if (
        intent.get("autonomous_authorization_requested") is True
        or intent.get("human_gate_bypass_requested") is True
        or intent.get("human_gate_retained") is not True
    ):
        result["boundary_result"] = "FAIL"
        result["reason_codes"].append("SIMULATION_HUMAN_GATE_BYPASS")
    else:
        result["boundary_result"] = "PASS"

    preconditions_pass = all(
        result[field] == "PASS"
        for field in ("identity_result", "purpose_result", "tenant_result", "secret_result", "boundary_result")
    )
    if preconditions_pass:
        response = create_local_mcp_server().call_tool(scenario["mcp_request"])
        result["mcp_tool_result"] = response["tool_result"]
        result["mcp_claim_assessment"] = response["claim_assessment"]
        result["mcp_reason_codes"] = response["reason_codes"]
        if response["tool_result"] == "SUCCESS":
            result["mcp_result"] = "PASS"
            result["actual_outcome"] = "PASS"
        else:
            result["mcp_result"] = "REJECTED_INPUT"
            result["actual_outcome"] = "FAIL"
            result["reason_codes"].append("SIMULATION_MCP_REQUEST_REJECTED")
    else:
        result["actual_outcome"] = "FAIL"

    result["expected_outcome_matched"] = result["actual_outcome"] == result["expected_outcome"]
    return result


def build_external_agent_simulation_result(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the deterministic aggregate for the fixed five-scenario corpus."""

    results = [evaluate_external_agent_simulation(scenario) for scenario in scenarios]
    types = {result["scenario_type"] for result in results}
    if types != EXPECTED_SCENARIO_TYPES or len(results) != 5:
        raise ExternalAgentSimulationError("SIMULATION_SCENARIO_COVERAGE_INVALID")
    all_matched = all(result["expected_outcome_matched"] for result in results)
    return {
        "saee_external_agent_simulation_result_v0_1": True,
        "simulation_version": "0.1",
        "simulation_scope": "local_offline_synthetic_external_agents_only",
        "simulation_result": "PASS" if all_matched else "FAIL",
        "scenario_cases": len(results),
        "valid_cases": sum(result["actual_outcome"] == "PASS" for result in results),
        "invalid_cases": sum(result["actual_outcome"] != "PASS" for result in results),
        "all_scenarios_evaluated": types == EXPECTED_SCENARIO_TYPES,
        "all_expected_outcomes_matched": all_matched,
        "results": sorted(results, key=lambda item: item["scenario_type"]),
        "synthetic_agents_only": True,
        "external_agents_connected": False,
        "authentication_available": False,
        "tenant_runtime_implemented": False,
        "credentials_stored": False,
        "external_validation_completed": False,
        "adoption_validated": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }
