"""Internal synthetic MCP discovery-to-interpretation dry integration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.capability_mcp_adapter import CapabilityMCPAdapter
from saee_backend.services.mcp_ecosystem_discovery_simulator import discover_tools, select_tool
from saee_backend.services.mcp_result_interpretation_validator import validate_interpretation


ROOT = Path(__file__).resolve().parents[2]
AGENT_SCHEMA = ROOT / "schemas/saee-synthetic-mcp-agent.schema.v0.1.json"
TRACE_SCHEMA = ROOT / "schemas/saee-mcp-dry-integration-trace.schema.v0.1.json"
SCENARIO_ROOT = ROOT / "agent-interface/mcp/mcp-dry-integration-scenarios"
PACKAGE_REF = "ecosystem/mcp-entry-package-v1/capability-card.json"
FIXED_INPUT_REFS = {
    "evaluate_rehearsal_run": "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json",
    "evaluate_evidence": "agent-interface/capabilities/examples/valid_supported_request.json",
    "rehearse_agent": None,
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("MCP_DRY_JSON_INVALID")
    return value


def _adapter() -> CapabilityMCPAdapter:
    adapter = CapabilityMCPAdapter()
    initialized = adapter.handle({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "saee-synthetic-mcp-agent", "version": "0.1"}},
    })
    if not isinstance(initialized, dict) or "result" not in initialized:
        raise RuntimeError("MCP_DRY_INITIALIZE_FAILED")
    adapter.handle({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
    return adapter


def _arguments(scenario: dict[str, Any], selected: str) -> dict[str, Any]:
    if scenario.get("input_ref") != FIXED_INPUT_REFS[selected]:
        raise ValueError("MCP_DRY_INPUT_REF_NOT_ALLOWLISTED")
    if selected == "evaluate_rehearsal_run":
        source = ROOT / FIXED_INPUT_REFS[selected]
        payload = {"rehearsal_run": run_task(source)}
    elif selected == "evaluate_evidence":
        payload = _load(ROOT / FIXED_INPUT_REFS[selected])
    else:
        payload = {
            "agent_reference": "agent:synthetic-mcp:dry-validator",
            "scenario_reference": "scenario:mcp-dry:rehearsal-request",
            "consent_scope": "local_controlled_synthetic_only",
        }
    return {
        "request_id": f"request:mcp-dry:{scenario['scenario_id'].lower()}",
        "payload": payload,
        "caller_context": {
            "caller_id": "caller:mcp-dry-synthetic-agent",
            "caller_type": "LOCAL_TEST",
            "invoked_at": "2026-07-13T08:00:00Z",
            "customer_data_included": False,
            "network_access_requested": False,
            "external_world_action_requested": False,
        },
    }


def run_dry_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    tools = discover_tools()
    selection = select_tool(scenario)
    if selection["selected_tool"] != scenario.get("expected_selection"):
        raise ValueError("MCP_DRY_SELECTION_MISMATCH")
    agent = {
        "agent_id": "agent:synthetic-mcp:dry-validator",
        "agent_goal": scenario["task_description"],
        "available_capabilities": tools,
        "selected_tool": selection["selected_tool"],
        "interpretation_policy": {
            "supported_means": "PROFILE_REQUIREMENT_SATISFIED",
            "result_is_authorization": False,
            "overinterpretation_rejected": True,
        },
        "simulation_only": True,
    }
    Draft202012Validator(_load(AGENT_SCHEMA)).validate(agent)

    called = selection["selected_tool"] != "NONE"
    delegated = False
    canonical_path = "NOT_INVOKED"
    if called:
        adapter = _adapter()
        listed = adapter.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        adapter_tools = [item["name"] for item in listed["result"]["tools"]] if isinstance(listed, dict) else []
        if adapter_tools != tools:
            raise RuntimeError("MCP_DRY_ADAPTER_DISCOVERY_MISMATCH")
        selected = selection["selected_tool"]
        response = adapter.handle({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": selected, "arguments": _arguments(scenario, selected)},
        })
        if not isinstance(response, dict) or not isinstance(response.get("result", {}).get("structuredContent"), dict):
            raise RuntimeError("MCP_DRY_ADAPTER_CALL_FAILED")
        runtime_value = response["result"]["structuredContent"]
        delegated = True
        canonical_path = {
            "evaluate_rehearsal_run": "AGENT_RUN_CAPABILITY",
            "evaluate_evidence": "EVIDENCE_ADEQUACY",
            "rehearse_agent": "CONTRACT_ONLY",
        }[selected]
        interpreted = validate_interpretation(runtime_value)
        if not interpreted["valid"]:
            raise RuntimeError("MCP_DRY_INTERPRETATION_FAILED")
        result_type = runtime_value["status"]
        interpretation = {key: interpreted[key] for key in ("status", "meaning", "overinterpretation_rejected")}
    else:
        result_type = "ABSTAINED" if selection["selection_status"] == "ABSTAINED_NO_SAEE_NEED" else "SELECTION_REJECTED"
        interpretation = {"status": "NOT_APPLICABLE", "meaning": "SAEE_NOT_SELECTED", "overinterpretation_rejected": True}

    if result_type != scenario.get("expected_outcome"):
        raise ValueError("MCP_DRY_OUTCOME_MISMATCH")
    slug = scenario["scenario_id"].lower()
    trace = {
        "trace_version": "0.1",
        "trace_id": f"trace:mcp-dry:{slug}",
        "scenario_id": scenario["scenario_id"],
        "agent_id": agent["agent_id"],
        "discovery_event": {"package_ref": PACKAGE_REF, "tools_discovered": tools},
        "tool_selection": selection,
        "adapter_call": {"called": called, "adapter_ref": "saee_backend/services/capability_mcp_adapter.py"},
        "runtime_delegation": {
            "delegated": delegated,
            "runtime_ref": "saee_backend/services/capability_runtime/capability_invocation.py",
            "canonical_service_path": canonical_path,
        },
        "result_type": result_type,
        "interpretation_result": interpretation,
        "truth_boundary": {
            "synthetic_agent_only": True,
            "external_mcp": False,
            "external_agent": False,
            "customer_data": False,
            "secret_recorded": False,
            "prompt_recorded": False,
            "chain_of_thought_recorded": False,
            "private_model_state_recorded": False,
            "production_ready": False,
        },
    }
    Draft202012Validator(_load(TRACE_SCHEMA)).validate(trace)
    return trace


def run_all_scenarios() -> dict[str, Any]:
    scenario_files = sorted(SCENARIO_ROOT.glob("*.json"))
    traces = [run_dry_scenario(_load(path)) for path in scenario_files]
    canonical = json.dumps(traces, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "result_version": "0.1",
        "validation_id": "saee.mcp-ecosystem-dry-integration",
        "scenario_results": traces,
        "tool_results": {
            "tools_discovered": 3,
            "runtime_invocations": sum(1 for trace in traces if trace["adapter_call"]["called"]),
            "contract_only_results": sum(1 for trace in traces if trace["result_type"] == "CONTRACT_ONLY"),
            "selection_rejections": sum(1 for trace in traces if trace["result_type"] == "SELECTION_REJECTED"),
            "abstentions": sum(1 for trace in traces if trace["result_type"] == "ABSTAINED"),
        },
        "runtime_path": [
            "saee_backend/services/capability_mcp_adapter.py",
            "saee_backend/services/capability_runtime/capability_invocation.py",
            "saee_backend/services/capability_runtime/capability_router.py",
        ],
        "trace_digest": f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}",
        "boundary_results": {
            "overinterpretations_rejected": ["APPROVED", "CERTIFIED", "SAFE", "DEPLOYED"],
            "external_mcp": False,
            "external_agent": False,
            "direct_evaluator_imports": 0,
        },
        "limitations": [
            "The Agent is a deterministic synthetic selector, not an external MCP client.",
            "The flow uses the repository-local MCP Adapter and Capability Runtime only.",
            "A successful local result does not establish external compatibility, adoption, authorization, or production readiness.",
        ],
        "truth_boundary": {
            "mcp_dry_integration_validation": True,
            "synthetic_agent_only": True,
            "external_mcp_connection": False,
            "external_agents_connected": False,
            "official_support": False,
            "marketplace_listed": False,
            "production_ready": False,
        },
    }
