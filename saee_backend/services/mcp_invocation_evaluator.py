"""Deterministic evaluation of synthetic callers using the local MCP prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.local_mcp_server import create_local_mcp_server


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/saee-mcp-invocation-evaluation.schema.v0.1.json"
EXPECTED_DISCOVERY_REFS = {
    "capability_object_ref": "agent-interface/registry/objects/saee-evidence-adequacy-capability-object.v0.1.json",
    "mapping_ref": "agent-interface/mcp/examples/saee-evaluate-evidence-mcp-tool-design.v0.1.json",
    "request_schema_ref": "agent-interface/mcp/saee-mcp-local-request.schema.v0.1.json",
    "response_schema_ref": "agent-interface/mcp/saee-mcp-local-response.schema.v0.1.json",
}
EXPECTED_CALLERS = {
    "CORRECT_MCP_AGENT",
    "WRONG_TOOL_SELECTION_AGENT",
    "RESPONSE_OVERINTERPRETATION_AGENT",
    "INVALID_MCP_CALLER",
    "BOUNDARY_AWARE_AGENT",
}
FORBIDDEN_CONCLUSIONS = {"DEPLOYMENT_APPROVED", "ACTION_AUTHORIZED", "SYSTEM_CERTIFIED", "SYSTEM_SAFE"}
REQUIRED_CONCLUSION = {
    ("SUCCESS", "SUPPORTED"): "EVIDENCE_PROFILE_REQUIREMENTS_SATISFIED",
    ("SUCCESS", "INSUFFICIENT_EVIDENCE"): "EVIDENCE_INSUFFICIENT",
    ("REJECTED_INPUT", "UNKNOWN"): "REQUEST_REJECTED",
}


class MCPInvocationEvaluationError(ValueError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise MCPInvocationEvaluationError(reason)


def _validate_scenario(scenario: Any) -> dict[str, Any]:
    _require(isinstance(scenario, dict), "MCP_INVOCATION_SCENARIO_INVALID")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(scenario), key=lambda error: list(error.absolute_path))
    if errors:
        raise MCPInvocationEvaluationError("MCP_INVOCATION_SCENARIO_SCHEMA_INVALID")
    discovery = scenario["mcp_tool_discovery"]
    for field, expected in EXPECTED_DISCOVERY_REFS.items():
        _require(discovery[field] == expected, "MCP_INVOCATION_DISCOVERY_REFERENCE_INVALID")
        path = (ROOT / expected).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise MCPInvocationEvaluationError("MCP_INVOCATION_DISCOVERY_REFERENCE_INVALID") from exc
        _require(path.is_file(), "MCP_INVOCATION_DISCOVERY_REFERENCE_MISSING")
    return scenario


def _response_matches(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        actual["tool_result"] == expected["tool_result"]
        and actual["claim_assessment"] == expected["claim_assessment"]
        and actual["reason_codes"] == expected["reason_codes"]
    )


def _boundary_passes(scenario: dict[str, Any]) -> bool:
    interpretation = scenario["interpretation_result"]
    boundary = scenario["boundary_result"]
    return (
        interpretation["conclusion"] not in FORBIDDEN_CONCLUSIONS
        and interpretation["treats_result_as_authority"] is False
        and boundary["preserves_evaluation_approval_separation"] is True
        and boundary["authorization_claimed"] is False
        and boundary["deployment_claimed"] is False
        and boundary["certification_claimed"] is False
        and boundary["human_authority_retained"] is True
    )


def evaluate_mcp_invocation_scenario(scenario: Any) -> dict[str, Any]:
    """Evaluate one closed synthetic MCP caller scenario."""

    scenario = _validate_scenario(scenario)
    server = create_local_mcp_server()
    actual_tools = [tool["name"] for tool in server.list_tools()]
    discovery = scenario["mcp_tool_discovery"]
    discovery_pass = (
        discovery["discovered_tools"] == actual_tools
        and discovery["selected_tool"] == "evaluate_evidence_adequacy"
    )

    primary = server.call_tool(scenario["mcp_request"])
    primary_matches = _response_matches(primary, scenario["expected_response"])
    additional_results = []
    additional_match = True
    all_responses = [primary]
    for probe in scenario["additional_mcp_requests"]:
        response = server.call_tool(probe["request"])
        matched = _response_matches(response, probe["expected_response"])
        additional_match = additional_match and matched
        all_responses.append(response)
        additional_results.append({
            "request_id": probe["request_id"],
            "tool_result": response["tool_result"],
            "claim_assessment": response["claim_assessment"],
            "reason_codes": response["reason_codes"],
            "expected_response_matched": matched,
        })

    all_rejected = all(response["tool_result"] == "REJECTED_INPUT" for response in all_responses)
    if all_rejected and primary_matches and additional_match:
        request_result = "REJECTED_INPUT"
    elif primary_matches and additional_match:
        request_result = "PASS"
    else:
        request_result = "FAIL"

    expected_conclusion = REQUIRED_CONCLUSION.get((primary["tool_result"], primary["claim_assessment"]))
    interpretation_pass = (
        scenario["interpretation_result"]["conclusion"] == expected_conclusion
        and scenario["interpretation_result"]["treats_result_as_authority"] is False
    )
    boundary_pass = _boundary_passes(scenario)

    reasons: list[str] = []
    if not discovery_pass:
        reasons.append("MCP_INVOCATION_TOOL_SELECTION_INVALID")
    if request_result == "FAIL":
        reasons.append("MCP_INVOCATION_REQUEST_EXPECTATION_MISMATCH")
    if not interpretation_pass:
        reasons.append("MCP_INVOCATION_RESPONSE_OVERINTERPRETED")
    if not boundary_pass:
        reasons.append("MCP_INVOCATION_BOUNDARY_VIOLATION")

    if not discovery_pass or request_result == "FAIL" or not interpretation_pass or not boundary_pass:
        actual_outcome = "FAIL"
    elif request_result == "REJECTED_INPUT":
        actual_outcome = "REJECTED_INPUT"
    else:
        actual_outcome = "PASS"

    return {
        "scenario_id": scenario["scenario_id"],
        "caller_type": scenario["caller_type"],
        "tool_discovery_result": "PASS" if discovery_pass else "FAIL",
        "request_result": request_result,
        "interpretation_result": "PASS" if interpretation_pass else "FAIL",
        "boundary_result": "PASS" if boundary_pass else "FAIL",
        "actual_outcome": actual_outcome,
        "expected_outcome": scenario["expected_outcome"],
        "expected_outcome_matched": actual_outcome == scenario["expected_outcome"],
        "actual_tool_result": primary["tool_result"],
        "actual_claim_assessment": primary["claim_assessment"],
        "actual_reason_codes": primary["reason_codes"],
        "evaluation_reason_codes": reasons,
        "additional_request_results": additional_results,
        "authorization_performed": False,
        "deployment_authorized": False,
        "certification_performed": False,
        "external_action_performed": False,
    }


def build_mcp_invocation_evaluation_result(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the deterministic result for the fixed five-caller corpus."""

    results = [evaluate_mcp_invocation_scenario(scenario) for scenario in scenarios]
    caller_types = {result["caller_type"] for result in results}
    _require(caller_types == EXPECTED_CALLERS and len(results) == 5, "MCP_INVOCATION_CALLER_COVERAGE_INVALID")
    all_matched = all(result["expected_outcome_matched"] for result in results)
    return {
        "saee_mcp_invocation_evaluation_result_v0_1": True,
        "evaluation_version": "0.1",
        "evaluation_scope": "local_synthetic_mcp_agent_like_callers_only",
        "evaluation_result": "PASS" if all_matched else "FAIL",
        "caller_cases": len(results),
        "valid_cases": sum(result["actual_outcome"] == "PASS" for result in results),
        "invalid_cases": sum(result["actual_outcome"] != "PASS" for result in results),
        "all_callers_evaluated": caller_types == EXPECTED_CALLERS,
        "all_expected_outcomes_matched": all_matched,
        "results": sorted(results, key=lambda item: item["caller_type"]),
        "mcp_local_prototype_used": True,
        "mcp_server_public": False,
        "external_clients_tested": False,
        "external_agents_tested": False,
        "synthetic_callers_only": True,
        "agent_intelligence_measured": False,
        "adoption_validated": False,
        "commercial_value_validated": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }
