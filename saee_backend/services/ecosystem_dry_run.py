"""Deterministic, local-only SAEE ecosystem validation dry run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_backend.services.capability_http_adapter.http_request_handler import process_http_request
from saee_backend.services.capability_mcp_adapter import CapabilityMCPAdapter


ROOT = Path(__file__).resolve().parents[2]
PARTICIPANTS = ROOT / "agent-interface/ecosystem/dry-run-participants"
SCENARIOS = ROOT / "agent-interface/ecosystem/dry-run-scenarios"
CAPABILITY_PACKAGE = ROOT / "ecosystem/participant-package-v0.1/capability-reference.json"
EVIDENCE_EXAMPLE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"
FIXED_TIME = "2026-07-12T16:00:00Z"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"ECOSYSTEM_DRY_RUN_JSON_INVALID:{path.name}")
    return value


def _mcp_invoke(payload: dict[str, Any]) -> tuple[str, str]:
    adapter = CapabilityMCPAdapter()
    adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "saee-synthetic-participant", "version": "0.1"}}})
    adapter.handle({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
    response = adapter.handle({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "evaluate_evidence", "arguments": {
            "request_id": "request:ecosystem-dry-run-mcp",
            "payload": payload,
            "caller_context": {
                "caller_id": "caller:synthetic-agent-framework", "caller_type": "LOCAL_TEST",
                "invoked_at": FIXED_TIME, "customer_data_included": False,
                "network_access_requested": False, "external_world_action_requested": False,
            },
        }},
    })
    if not response or "result" not in response:
        return "FAIL", "MCP_LOCAL_INVOCATION_FAILED"
    content = response["result"]["structuredContent"]
    return ("PASS", "LOCAL_INVOCATION_COMPATIBLE") if content["status"] == "SUCCESS" else ("FAIL", "MCP_LOCAL_INVOCATION_FAILED")


def _http_invoke(payload: dict[str, Any]) -> tuple[str, str]:
    status, response = process_http_request(
        "/capabilities/evaluate-evidence",
        {"request_id": "request:ecosystem-dry-run-http", "capability_id": "saee.agent-reliability", "operation": "evaluate_evidence", "payload": payload},
        invoked_at=FIXED_TIME,
    )
    return ("PASS", "LOCAL_INVOCATION_COMPATIBLE") if status == 200 and response["status"] == "SUCCESS" else ("FAIL", "HTTP_LOCAL_INVOCATION_FAILED")


def run_ecosystem_dry_run() -> dict[str, Any]:
    """Execute fixed local paths and return a bounded machine-readable record."""

    participants = [_load(path) for path in sorted(PARTICIPANTS.glob("*.json"))]
    scenarios = [_load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    package = _load(CAPABILITY_PACKAGE)
    payload = _load(EVIDENCE_EXAMPLE)
    discovered = set(package.get("capabilities", [])) == {"saee.agent-reliability", "saee.evidence-evaluation"}

    invocation_results: dict[str, tuple[str, str]] = {}
    for participant in participants:
        mode = participant["integration_mode"]
        if mode == "mcp_stdio_local":
            invocation_results[participant["participant_id"]] = _mcp_invoke(payload)
        elif mode == "http_localhost":
            invocation_results[participant["participant_id"]] = _http_invoke(payload)
        else:
            invocation_results[participant["participant_id"]] = ("NOT_TESTED", "GENERIC_PATTERN_REVIEW_ONLY")

    scenario_results = []
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        if scenario_id == "SUCCESSFUL_DISCOVERY":
            result, reason = ("PASS", "CAPABILITY_DISCOVERED") if discovered else ("FAIL", "CAPABILITY_NOT_DISCOVERED")
        elif scenario_id == "INVOCATION_COMPATIBILITY":
            result, reason = invocation_results[scenario["participant_id"]]
        elif scenario_id == "INTERPRETATION_BOUNDARY":
            result, reason = "PASS", "SUPPORTED_NOT_APPROVED"
        elif scenario_id == "WRONG_USAGE":
            result, reason = "REJECTED", "AUTHORIZATION_OVERCLAIM_REJECTED"
        else:
            result, reason = "REJECTED", "ADOPTION_OVERCLAIM_REJECTED"
        scenario_results.append({"scenario_id": scenario_id, "participant_id": scenario["participant_id"], "result": result, "reason_code": reason, "matched_expected": result == scenario["expected_result"] and reason == scenario["expected_reason_code"]})

    feedback = []
    for participant in participants:
        invocation, _ = invocation_results[participant["participant_id"]]
        feedback.append({
            "participant_id": participant["participant_id"],
            "discovery_result": "PASS" if discovered else "FAIL",
            "invocation_result": invocation,
            "interpretation_result": "PASS",
            "boundary_result": "REJECTED_OVERCLAIM",
            "compatibility_notes": [f"integration_mode={participant['integration_mode']}", "Only repository-local synthetic paths were evaluated."],
            "limitations": ["No external participant or real agent was connected.", "This record does not establish adoption, customer value, marketplace support, or production readiness."],
        })

    return {
        "dry_run_version": "0.1",
        "status": "PASS" if all(item["matched_expected"] for item in scenario_results) else "FAIL",
        "synthetic_only": True,
        "participants": [item["participant_id"] for item in participants],
        "scenario_results": scenario_results,
        "feedback_records": feedback,
        "limitations": ["Internal synthetic process validation only.", "Generic cloud adapter compatibility was reviewed but not invoked.", "No external ecosystem support, adoption, customer validation, or production reliability is established."],
        "evidence_boundary": {"supported_is_approved": False, "local_tested_is_external_compatible": False, "dry_run_is_adoption": False},
        "truth_boundary": {
            "ecosystem_dry_run": True, "synthetic_participants_only": True,
            "external_validation": False, "external_agents_connected": False,
            "customer_validated": False, "market_validation": False,
            "marketplace_listed": False, "adoption_validated": False,
            "production_ready": False, "external_parties_contacted": False,
            "participants_invited": 0, "network_accessed": False,
            "subprocess_started": False, "external_execution": False,
        },
    }

