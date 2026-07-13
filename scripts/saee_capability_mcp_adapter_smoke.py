#!/usr/bin/env python3
"""Offline protocol smoke for SAEE Capability Runtime MCP Adapter Alpha."""

from __future__ import annotations

import ast
import copy
import io
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services import capability_mcp_adapter as adapter_module
from saee_backend.services.capability_mcp_adapter import CapabilityMCPAdapter, serve, tool_definitions


SCENARIO = ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json"
EVIDENCE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"
ADAPTER_SOURCE = ROOT / "saee_backend/services/capability_mcp_adapter.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def message(request_id: int, method: str, params: Any = None) -> dict[str, Any]:
    value: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        value["params"] = params
    return value


def initialize(request_id: int = 1) -> dict[str, Any]:
    return message(request_id, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "saee-local-smoke", "version": "0.1.0"}})


def arguments(request_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "payload": payload,
        "caller_context": {
            "caller_id": "caller:mcp-smoke",
            "caller_type": "LOCAL_TEST",
            "invoked_at": "2026-07-12T14:00:00Z",
            "customer_data_included": False,
            "network_access_requested": False,
            "external_world_action_requested": False,
        },
    }


def ready_adapter() -> CapabilityMCPAdapter:
    adapter = CapabilityMCPAdapter()
    init = adapter.handle(initialize())
    require(init is not None and init["result"]["protocolVersion"] == "2025-11-25", "initialize failed")
    require(adapter.handle({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) is None, "initialized notification failed")
    return adapter


def main() -> int:
    tools = tool_definitions()
    require([item["name"] for item in tools] == ["evaluate_agent_run", "evaluate_evidence", "rehearse_agent"], "Tool list drift")
    require(all(item["annotations"] == {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False} for item in tools), "Tool annotations invalid")
    require(all(item["execution"] == {"taskSupport": "forbidden"} for item in tools), "task support must be forbidden")
    for item in tools:
        Draft202012Validator.check_schema(item["inputSchema"])
        Draft202012Validator.check_schema(item["outputSchema"])

    run = run_task(SCENARIO)
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    calls = {
        "run": message(10, "tools/call", {"name": "evaluate_agent_run", "arguments": arguments("request:mcp-run", {"rehearsal_run": run})}),
        "evidence": message(11, "tools/call", {"name": "evaluate_evidence", "arguments": arguments("request:mcp-evidence", evidence)}),
        "rehearse": message(12, "tools/call", {"name": "rehearse_agent", "arguments": arguments("request:mcp-rehearse", {"agent_reference": "agent:synthetic", "scenario_reference": "scenario:synthetic", "consent_scope": "local_controlled_synthetic_only"})}),
    }

    original_invoke = adapter_module.invoke_capability
    invocation_count = 0

    def probe(value: Any) -> dict[str, Any]:
        nonlocal invocation_count
        invocation_count += 1
        return original_invoke(value)

    adapter_module.invoke_capability = probe
    try:
        adapter = ready_adapter()
        listed = adapter.handle(message(2, "tools/list", {}))
        responses = {name: adapter.handle(value) for name, value in calls.items()}
    finally:
        adapter_module.invoke_capability = original_invoke
    require(listed is not None and len(listed["result"]["tools"]) == 3, "Tool discovery failed")
    require(invocation_count == 3, "MCP Adapter bypassed or duplicated Runtime invocation")
    require(responses["run"]["result"]["structuredContent"]["status"] == "SUCCESS", "run Tool failed")
    require(responses["evidence"]["result"]["structuredContent"]["status"] == "SUCCESS", "evidence Tool failed")
    require(responses["rehearse"]["result"]["structuredContent"]["status"] == "CONTRACT_ONLY", "rehearse boundary failed")
    require(responses["rehearse"]["result"]["isError"] is True, "contract-only Tool must be visible as unavailable")

    invalid: list[dict[str, Any] | None] = []
    invalid.append(CapabilityMCPAdapter().handle(message(20, "tools/list", {})))
    invalid.append(ready_adapter().handle({"id": 21, "method": "ping"}))
    invalid.append(ready_adapter().handle({"jsonrpc": "2.0", "id": 22, "params": {}}))
    invalid.append(CapabilityMCPAdapter().handle(message(23, "initialize", {"protocolVersion": 3})))
    invalid.append(ready_adapter().handle(message(24, "tools/list", {"cursor": "bad"})))
    invalid.append(ready_adapter().handle(message(25, "unknown/method", {})))
    invalid.append(ready_adapter().handle(message(26, "tools/call", {"name": "unknown", "arguments": {}})))
    invalid.append(ready_adapter().handle(message(27, "tools/call", [])))
    invalid.append(ready_adapter().handle(message(28, "tools/call", {"name": "evaluate_evidence", "arguments": {}})))
    bad_customer = arguments("request:bad-customer", copy.deepcopy(evidence)); bad_customer["caller_context"]["customer_data_included"] = True
    invalid.append(ready_adapter().handle(message(29, "tools/call", {"name": "evaluate_evidence", "arguments": bad_customer})))
    bad_secret = arguments("request:bad-secret", copy.deepcopy(evidence)); bad_secret["payload"]["api_key"] = "synthetic-forbidden"
    invalid.append(ready_adapter().handle(message(30, "tools/call", {"name": "evaluate_evidence", "arguments": bad_secret})))
    invalid.append(ready_adapter().handle(message(31, "tools/call", {"name": "evaluate_agent_run", "arguments": arguments("request:bad-run", {})})))
    require(all(item is not None for item in invalid), "invalid request produced no response")
    require(all("error" in item or item.get("result", {}).get("isError") is True for item in invalid if item is not None), "invalid request accepted")

    baseline_adapter = ready_adapter()
    baseline = baseline_adapter.handle(calls["evidence"])
    canonical = json.dumps(baseline, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(ready_adapter().handle(calls["evidence"]), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "MCP mapping not deterministic")

    transcript = b'{bad json}\n' + json.dumps(initialize(40), separators=(",", ":")).encode() + b"\n" + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, separators=(",", ":")).encode() + b"\n" + json.dumps(message(41, "tools/list", {}), separators=(",", ":")).encode() + b"\n"
    output = io.BytesIO()
    require(serve(io.BytesIO(transcript), output) == 0, "stdio serve failed")
    stdio_responses = [json.loads(line) for line in output.getvalue().decode().splitlines()]
    require(stdio_responses[0]["error"]["code"] == -32700 and len(stdio_responses[2]["result"]["tools"]) == 3, "stdio framing failed")

    source = ADAPTER_SOURCE.read_text(encoding="utf-8")
    require("from saee_backend.services.capability_runtime import invoke_capability" in source, "Runtime delegation missing")
    tree = ast.parse(source)
    imported_modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    require(not any(module.endswith(("agent_run_capability", "evidence_adequacy", "local_evidence_tool")) for module in imported_modules), "direct evaluator import detected")
    for forbidden in ("import socket", "import subprocess", "import requests", "os.system", "Popen("):
        require(forbidden not in source, f"forbidden Adapter dependency: {forbidden}")

    print("SAEE_CAPABILITY_MCP_ADAPTER_SMOKE: PASS")
    print("protocol_revision=2025-11-25")
    print("tool_discovery=3/3")
    print("runtime_delegation=3/3")
    print("supported_tools=2/2")
    print("contract_only_tools=1/1")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("stdio_transport_local=true")
    print("direct_evaluator_imports=0")
    print("network_listener_available=false")
    print("public_service=false")
    print("external_agent_connected=false")
    print("external_mcp_interoperability_validated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
