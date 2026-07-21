#!/usr/bin/env python3
"""Offline hostile validation for SAEE MCP Local Prototype v0.1."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services import mcp_evidence_tool_handler  # noqa: E402
from saee_backend.services.local_mcp_server import create_local_mcp_server  # noqa: E402


REQUEST_SCHEMA_PATH = ROOT / "agent-interface/mcp/saee-mcp-local-request.schema.v0.1.json"
CANONICAL_ARGUMENT_SCHEMA_PATH = ROOT / "agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json"
RESPONSE_SCHEMA_PATH = ROOT / "agent-interface/mcp/saee-mcp-local-response.schema.v0.1.json"
EXAMPLE_ROOT = ROOT / "agent-interface/mcp/examples/local-mcp"
DOC_PATH = ROOT / "docs/architecture/SAEE_LOCAL_MCP_PROTOTYPE.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_LOCAL_MCP_PROTOTYPE_RECOMMENDATION_GATE.md"
DEMO_PATH = ROOT / "scripts/saee_local_mcp_client_demo.py"
IMPLEMENTATION_PATHS = (
    ROOT / "saee_backend/services/local_mcp_server.py",
    ROOT / "saee_backend/services/mcp_evidence_tool_handler.py",
    DEMO_PATH,
)
EXAMPLES = {
    "supported": EXAMPLE_ROOT / "valid_supported_request.json",
    "insufficient": EXAMPLE_ROOT / "valid_insufficient_request.json",
    "invalid_tool": EXAMPLE_ROOT / "invalid_tool_name.json",
    "invalid_arguments": EXAMPLE_ROOT / "invalid_arguments.json",
    "invalid_boundary": EXAMPLE_ROOT / "invalid_boundary_request.json",
    "missing_arguments": EXAMPLE_ROOT / "invalid_missing_arguments.json",
    "unknown_profile": EXAMPLE_ROOT / "invalid_unknown_profile.json",
}
EXPECTED_INVALID_CODES = {
    "invalid_tool": "MCP_TOOL_NAME_INVALID",
    "invalid_arguments": "MCP_ARGUMENTS_INVALID",
    "invalid_boundary": "TOOL_INPUT_SCHEMA_INVALID",
    "missing_arguments": "MCP_ARGUMENTS_INVALID",
    "unknown_profile": "TOOL_PROFILE_UNKNOWN",
}
FORBIDDEN_ASSESSMENTS = {"APPROVED", "CERTIFIED", "SAFE", "COMPLIANT"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _resolved_request_schema() -> dict[str, Any]:
    schema = _load(REQUEST_SCHEMA_PATH)
    canonical = _load(CANONICAL_ARGUMENT_SCHEMA_PATH)
    schema["properties"]["arguments"] = canonical
    return schema


def _validate_response(response: dict[str, Any]) -> None:
    schema = _load(RESPONSE_SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(response), key=lambda error: list(error.absolute_path))
    assert not errors, errors[0].message if errors else ""


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def _forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "system", "popen", "run", "Popen", "write_text", "write_bytes", "listen", "bind", "connect"
        }:
            found.add(node.func.attr)
    return found


def main() -> int:
    for path in (REQUEST_SCHEMA_PATH, CANONICAL_ARGUMENT_SCHEMA_PATH, RESPONSE_SCHEMA_PATH, DOC_PATH, GATE_PATH, DEMO_PATH, *EXAMPLES.values()):
        assert path.is_file(), path
    Draft202012Validator.check_schema(_load(REQUEST_SCHEMA_PATH))
    Draft202012Validator.check_schema(_load(RESPONSE_SCHEMA_PATH))

    requirements = (ROOT / "saee_backend/requirements.txt").read_text(encoding="utf-8").lower()
    assert "modelcontextprotocol" not in requirements
    assert not any(line.strip().startswith("mcp") for line in requirements.splitlines())

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "sqlite3", "smtplib", "mcp"}
    for path in IMPLEMENTATION_PATHS:
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    server = create_local_mcp_server()
    tools = server.list_tools()
    assert len(tools) == 2
    assert {tool["name"] for tool in tools} == {"evaluate_evidence_adequacy", "evaluate_rehearsal_run"}
    assert all(tool["read_only_intent"] is True for tool in tools)
    assert all(tool["side_effects_allowed"] is False for tool in tools)

    request_validator = Draft202012Validator(_resolved_request_schema())
    supported_request = _load(EXAMPLES["supported"])
    insufficient_request = _load(EXAMPLES["insufficient"])
    for request in (supported_request, insufficient_request):
        assert not list(request_validator.iter_errors(request))

    supported = server.call_tool(supported_request)
    insufficient = server.call_tool(insufficient_request)
    _validate_response(supported)
    _validate_response(insufficient)
    assert supported["tool_result"] == "SUCCESS"
    assert supported["claim_assessment"] == "SUPPORTED"
    assert supported["evidence_sufficiency_status"] == "SUFFICIENT"
    assert insufficient["tool_result"] == "SUCCESS"
    assert insufficient["claim_assessment"] == "INSUFFICIENT_EVIDENCE"
    assert insufficient["evidence_sufficiency_status"] == "INSUFFICIENT"
    assert insufficient["missing_requirements"]

    for name, code in EXPECTED_INVALID_CODES.items():
        request = _load(EXAMPLES[name])
        assert list(request_validator.iter_errors(request)), f"invalid request schema accepted: {name}"
        response = server.call_tool(request)
        _validate_response(response)
        assert response["tool_result"] == "REJECTED_INPUT", name
        assert response["claim_assessment"] == "UNKNOWN", name
        assert response["reason_codes"] == [code], (name, response["reason_codes"])

    calls: list[dict[str, Any]] = []
    original = mcp_evidence_tool_handler.evaluate_evidence_tool

    def probe(arguments: dict[str, Any]) -> dict[str, Any]:
        calls.append(arguments)
        return original(arguments)

    mcp_evidence_tool_handler.evaluate_evidence_tool = probe
    try:
        probed = server.call_tool(supported_request)
    finally:
        mcp_evidence_tool_handler.evaluate_evidence_tool = original
    assert len(calls) == 1
    assert calls[0] == supported_request["arguments"]
    assert probed == supported

    for response in (supported, insufficient, probed):
        assert response["boundary_statement"] == mcp_evidence_tool_handler.BOUNDARY_STATEMENT
        assert mcp_evidence_tool_handler.MCP_PROJECTION_LIMITATION in response["limitations"]
        assert response["claim_assessment"] not in FORBIDDEN_ASSESSMENTS
        assert response["evidence_sufficiency_status"] not in FORBIDDEN_ASSESSMENTS

    canonical = json.dumps(supported, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = create_local_mcp_server().call_tool(_load(EXAMPLES["supported"]))
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    status = server.runtime_status()
    assert status["mcp_local_prototype"] is True
    assert status["tool_count"] == 2
    assert status["evaluate_rehearsal_run_tool_available"] is True
    assert status["implementation_status"] == "local_prototype"
    assert all(status[field] is False for field in (
        "network_accessed",
        "subprocess_started",
        "persistence_performed",
        "public_endpoint_available",
        "authentication_available",
        "external_agents_connected",
        "production_ready",
    ))

    print("SAEE_LOCAL_MCP_PROTOTYPE_SMOKE: PASS")
    print("tools=2/2")
    print("valid_cases=2/2")
    print("invalid_cases=5/5")
    print("deterministic_runs=5/5")
    print("canonical_local_tool_reused=true")
    print("response_schema_valid=true")
    print("boundary_preserved=true")
    print("mcp_dependency_installed=false")
    print("mcp_local_prototype=true")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("persistence_performed=false")
    print("public_endpoint_available=false")
    print("authentication_available=false")
    print("external_agents_connected=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
