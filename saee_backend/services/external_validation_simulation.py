"""Deterministic Phase 12.1 external-validation workflow simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_backend.services.capability_http_adapter.http_request_handler import process_http_request
from saee_backend.services.capability_mcp_adapter import CapabilityMCPAdapter


ROOT = Path(__file__).resolve().parents[2]
PARTICIPANTS = ROOT / "agent-interface/ecosystem/external-validation-simulation"
SCENARIOS = ROOT / "agent-interface/ecosystem/external-validation-scenarios"
EVIDENCE_EXAMPLE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"
ALLOWED_TESTS = {"capability_discovery_test", "integration_test", "interpretation_test", "compatibility_feedback"}
FIXED_TIME = "2026-07-12T17:00:00Z"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"EXTERNAL_VALIDATION_SIMULATION_JSON_INVALID:{path.name}")
    return value


def _mcp_local_test(payload: dict[str, Any]) -> bool:
    adapter = CapabilityMCPAdapter()
    adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "saee-phase12-simulation", "version": "0.1"}}})
    adapter.handle({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
    response = adapter.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "evaluate_evidence", "arguments": {
        "request_id": "request:phase12-simulation-mcp", "payload": payload,
        "caller_context": {"caller_id": "caller:phase12-synthetic", "caller_type": "LOCAL_TEST", "invoked_at": FIXED_TIME, "customer_data_included": False, "network_access_requested": False, "external_world_action_requested": False},
    }}})
    return bool(response and response.get("result", {}).get("structuredContent", {}).get("status") == "SUCCESS")


def _http_local_test(payload: dict[str, Any]) -> bool:
    status, response = process_http_request(
        "/capabilities/evaluate-evidence",
        {"request_id": "request:phase12-simulation-http", "capability_id": "saee.agent-reliability", "operation": "evaluate_evidence", "payload": payload},
        invoked_at=FIXED_TIME,
    )
    return status == 200 and response.get("status") == "SUCCESS"


def _evaluate_scenario(scenario: dict[str, Any], participant: dict[str, Any], mcp_ok: bool) -> tuple[str, str]:
    if participant["authorization_status"] != "AUTHORIZED_FOR_VALIDATION":
        return "BLOCKED", "PARTICIPANT_NOT_AUTHORIZED"
    if scenario["credential_exposure"]:
        return "TERMINATED", "CREDENTIAL_EXPOSURE"
    if scenario["contains_customer_data"]:
        return "TERMINATED", "CUSTOMER_DATA_RECEIVED"
    if scenario["adoption_claim"]:
        return "REJECTED", "FALSE_ADOPTION_CLAIM"
    if scenario["requested_test"] not in ALLOWED_TESTS or scenario["requested_test"] not in participant["allowed_tests"]:
        return "REJECTED", "VALIDATION_SCOPE_VIOLATION"
    if scenario["scenario_id"] == "AUTHORIZED_SUCCESS_FLOW" and mcp_ok:
        return "PASS", "AUTHORIZED_SCOPE_COMPLETED"
    return "REJECTED", "CONTROLLED_TEST_FAILED"


def run_external_validation_simulation() -> dict[str, Any]:
    participants = [_load(path) for path in sorted(PARTICIPANTS.glob("sim-*.json"))]
    by_id = {item["participant_id"]: item for item in participants}
    scenarios = [_load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    payload = _load(EVIDENCE_EXAMPLE)
    mcp_ok = _mcp_local_test(payload)
    http_ok = _http_local_test(payload)

    scenario_results = []
    evidence_records = []
    for scenario in scenarios:
        participant = by_id[scenario["participant_id"]]
        result, reason = _evaluate_scenario(scenario, participant, mcp_ok)
        scenario_results.append({"scenario_id": scenario["scenario_id"], "participant_id": participant["participant_id"], "result": result, "reason_code": reason, "matched_expected": result == scenario["expected_result"] and reason == scenario["expected_reason_code"]})
        evidence_records.append({
            "evidence_id": f"simulation-evidence:{scenario['scenario_id'].lower().replace('_', '-')}",
            "participant_id": participant["participant_id"],
            "scenario_id": scenario["scenario_id"],
            "evidence_type": "simulation_result",
            "result": result,
            "limitations": ["Synthetic workflow observation only; no input payload or external identity retained."],
            "simulation_only": True,
            "contains_private_data": False,
        })

    feedback_records = [
        {"participant_id": "SIM_AGENT_FRAMEWORK_VALIDATOR", "test_area": "MCP_LOCAL", "result": "PASS" if mcp_ok else "REJECTED", "compatibility_issue": "", "boundary_issue": "NONE", "notes": ["In-memory local MCP Adapter path only; no external Agent connected."]},
        {"participant_id": "SIM_DEVELOPER_VALIDATOR", "test_area": "HTTP_LOCAL", "result": "PASS" if http_ok else "REJECTED", "compatibility_issue": "", "boundary_issue": "NONE", "notes": ["HTTP contract processed as a local function with a fixed timestamp; no listener or network call."]},
        {"participant_id": "SIM_CLOUD_PLATFORM_VALIDATOR", "test_area": "METADATA_REVIEW", "result": "BLOCKED", "compatibility_issue": "Authorization intentionally absent.", "boundary_issue": "UNAUTHORIZED_PARTICIPANT", "notes": ["No cloud platform or external identity exists; metadata review did not execute."]},
    ]

    return {
        "simulation_version": "0.1",
        "status": "PASS" if all(item["matched_expected"] for item in scenario_results) and mcp_ok and http_ok else "FAIL",
        "participants": [item["participant_id"] for item in participants],
        "scenario_results": scenario_results,
        "evidence_records": evidence_records,
        "feedback_records": feedback_records,
        "exit_review": {"authorized_success_flow_completed": mcp_ok, "terminated_scenarios": 2, "blocked_or_rejected_scenarios": 3, "real_validation_exit_criteria_met": False},
        "limitations": ["Synthetic participants and repository-local paths only.", "No external compatibility, ecosystem support, adoption, customer validation or production reliability is established."],
        "truth_boundary": {
            "external_validation_simulation": True, "synthetic_participants_only": True,
            "external_validation": False, "real_participants": False,
            "participants_invited": 0, "external_agents_connected": False,
            "customer_data": False, "customer_validated": False,
            "adoption_validated": False, "marketplace_listed": False,
            "market_validation": False, "production_ready": False,
            "network_accessed": False, "subprocess_started": False,
            "external_execution": False,
        },
    }
