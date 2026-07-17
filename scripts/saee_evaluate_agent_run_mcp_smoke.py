#!/usr/bin/env python3
"""Offline deterministic smoke for the local evaluate_rehearsal_run MCP Tool."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services import mcp_agent_run_tool_handler
from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.local_mcp_server import create_local_mcp_server


REQUEST_SCHEMA = ROOT / "agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json"
RUN_SCHEMA = ROOT / "agent-interface/rehearsal/saee-agent-rehearsal-run.v0.1.schema.json"
RESPONSE_SCHEMA = ROOT / "agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json"
CAPABILITY = ROOT / "agent-interface/mcp/saee-evaluate-agent-run-mcp-capability.v0.1.json"
DOC = ROOT / "docs/architecture/SAEE_EVALUATE_AGENT_RUN_MCP_CAPABILITY.md"
GATE = ROOT / "docs/strategy/SAEE_EVALUATE_AGENT_RUN_MCP_RECOMMENDATION_GATE.md"
IMPLEMENTATION = (
    ROOT / "saee_backend/services/local_mcp_server.py",
    ROOT / "saee_backend/services/mcp_agent_run_tool_handler.py",
)
SCENARIOS = {
    "baseline-metadata-inspection.json": "SUPPORTED",
    "tool-timeout-abstention.json": "SUPPORTED",
    "instruction-conflict-refusal.json": "INSUFFICIENT_EVIDENCE",
}


class MCPAgentRunSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise MCPAgentRunSmokeError(detail)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> None:
    for path in (REQUEST_SCHEMA, RUN_SCHEMA, RESPONSE_SCHEMA, CAPABILITY, DOC, GATE, *IMPLEMENTATION):
        require(path.is_file(), f"required file missing: {path}")
    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "importlib", "smtplib", "mcp"}
    for path in IMPLEMENTATION:
        require(not imported_roots(path).intersection(forbidden), f"forbidden import: {path}")

    request_schema = load(REQUEST_SCHEMA)
    request_schema["properties"]["arguments"]["properties"]["rehearsal_run"] = {"type": "object"}
    request_validator = Draft202012Validator(request_schema)
    run_validator = Draft202012Validator(load(RUN_SCHEMA))
    response_validator = Draft202012Validator(load(RESPONSE_SCHEMA))
    capability = load(CAPABILITY)
    require(capability["tool_name"] == "evaluate_rehearsal_run", "capability Tool name invalid")
    require(capability["stage"] == "local_in_memory_mcp_capability", "capability stage overclaimed")
    require(capability["truth_boundary"]["local_tool_registered"] is True, "Tool registration hidden")
    for field in ("standard_mcp_transport_available", "public_endpoint_available", "authentication_available", "external_agent_connected", "interoperability_validated", "deployment_authorized", "customer_validated", "production_ready"):
        require(capability["truth_boundary"][field] is False, f"capability overclaim: {field}")

    server = create_local_mcp_server()
    tools = server.list_tools()
    require({tool["name"] for tool in tools} == {"evaluate_evidence_adequacy", "evaluate_rehearsal_run"}, "fixed Tool registry invalid")
    run_by_name: dict[str, dict[str, Any]] = {}
    response_by_name: dict[str, dict[str, Any]] = {}
    for filename, expected in SCENARIOS.items():
        run = run_task(ROOT / "agent-interface/rehearsal/scenarios" / filename)
        request = {"tool_name": "evaluate_rehearsal_run", "arguments": {"rehearsal_run": run}}
        require(not list(request_validator.iter_errors(request)), f"valid request rejected: {filename}")
        require(not list(run_validator.iter_errors(run)), f"valid run rejected: {filename}")
        response = server.call_tool(request)
        response_validator.validate(response)
        require(response["tool_result"] == "SUCCESS", f"Tool failed: {filename}")
        require(response["assessment"] == expected, f"assessment mismatch: {filename}")
        require(response["run_ref"] == run["run_id"] and response["trace_ref"] == run["trace"]["trace_id"], f"reference binding lost: {filename}")
        run_by_name[filename] = run
        response_by_name[filename] = response

    invalid_requests = [
        None,
        {"tool_name": "evaluate_rehearsal_run"},
        {"tool_name": "evaluate_rehearsal_run", "arguments": {}, "extra": True},
        {"tool_name": "evaluate_rehearsal_run", "arguments": {}},
    ]
    for request in invalid_requests:
        response = mcp_agent_run_tool_handler.handle_mcp_agent_run_tool(request)
        response_validator.validate(response)
        require(response["tool_result"] == "REJECTED_INPUT", "invalid request accepted")

    tampered = copy.deepcopy(run_by_name["baseline-metadata-inspection.json"])
    tampered["trace"]["events"][0]["summary"] = "tampered"
    rejected = server.call_tool({"tool_name": "evaluate_rehearsal_run", "arguments": {"rehearsal_run": tampered}})
    response_validator.validate(rejected)
    require(rejected["tool_result"] == "REJECTED_INPUT", "tampered Trace accepted")
    require(rejected["reason_codes"] == ["AGENT_RUN_TRACE_DIGEST_INVALID"], "tamper reason unstable")

    overclaim = copy.deepcopy(response_by_name["baseline-metadata-inspection.json"])
    overclaim["assessment"] = "SAFE"
    try:
        response_validator.validate(overclaim)
    except ValidationError:
        pass
    else:
        raise MCPAgentRunSmokeError("SAFE assessment accepted")

    calls: list[dict[str, Any]] = []
    original = mcp_agent_run_tool_handler.evaluate_rehearsal_run

    def probe(run: dict[str, Any]) -> dict[str, Any]:
        calls.append(run)
        return original(run)

    mcp_agent_run_tool_handler.evaluate_rehearsal_run = probe
    try:
        request = {"tool_name": "evaluate_rehearsal_run", "arguments": {"rehearsal_run": run_by_name["baseline-metadata-inspection.json"]}}
        probed = server.call_tool(request)
    finally:
        mcp_agent_run_tool_handler.evaluate_rehearsal_run = original
    require(len(calls) == 1, "canonical Alpha not reused exactly once")
    require(probed == response_by_name["baseline-metadata-inspection.json"], "MCP projection changed Alpha result")

    canonical = json.dumps(response_by_name["baseline-metadata-inspection.json"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        run = run_task(ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json")
        repeated = create_local_mcp_server().call_tool({"tool_name": "evaluate_rehearsal_run", "arguments": {"rehearsal_run": run}})
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "MCP Tool non-deterministic")

    status = server.runtime_status()
    require(status["tool_count"] == 2 and status["evaluate_rehearsal_run_tool_available"] is True, "runtime Tool status invalid")
    for field in ("network_accessed", "subprocess_started", "persistence_performed", "public_endpoint_available", "authentication_available", "external_agents_connected", "production_ready"):
        require(status[field] is False, f"runtime boundary expanded: {field}")

    print("SAEE_EVALUATE_AGENT_RUN_MCP_SMOKE: PASS")
    print("tools=2/2")
    print("evaluate_rehearsal_run_valid_cases=3/3")
    print("evaluate_rehearsal_run_invalid_cases=6/6")
    print("deterministic_runs=5/5")
    print("canonical_agent_run_alpha_reused=true")
    print("trace_binding_preserved=true")
    print("standard_mcp_transport_available=false")
    print("public_endpoint_available=false")
    print("external_agent_connected=false")
    print("interoperability_validated=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (MCPAgentRunSmokeError, json.JSONDecodeError, ValidationError, ValueError, KeyError) as exc:
        print(f"SAEE_EVALUATE_AGENT_RUN_MCP_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
