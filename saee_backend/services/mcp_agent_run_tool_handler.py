"""Bounded local MCP projection for evaluate_agent_run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.agent_run_capability import AgentRunCapabilityError, evaluate_agent_run


ROOT = Path(__file__).resolve().parents[2]
RESPONSE_SCHEMA = ROOT / "agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json"
TOOL_NAME = "evaluate_agent_run"
BOUNDARY_STATEMENT = "Evidence adequacy assessment is not task success, safety certification, compliance determination, or deployment authority."
BASE_LIMITATIONS = [
    "The MCP projection evaluates only a strict SAEE Rehearsal Run.",
    "SUPPORTED means fixed profile requirements were satisfied, not task success.",
    "The result does not establish Agent safety, compliance, certification, or production readiness.",
    "The result does not authorize deployment or another external action.",
    "This local in-memory MCP abstraction is not a standardized public MCP transport.",
]


def _validate(response: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(response), key=lambda item: list(item.absolute_path))
    if errors:
        raise RuntimeError("SAEE evaluate_agent_run MCP handler produced an invalid response")
    return response


def _rejected(code: str) -> dict[str, Any]:
    return _validate({
        "tool_result": "REJECTED_INPUT",
        "run_ref": None,
        "trace_ref": None,
        "claim_type": "UNKNOWN",
        "assessment": "UNKNOWN",
        "profile_result": "UNKNOWN",
        "missing_requirements": [],
        "failed_relationships": [],
        "reason_codes": [code],
        "limitations": list(BASE_LIMITATIONS),
        "boundary_statement": BOUNDARY_STATEMENT,
    })


def handle_mcp_agent_run_tool(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        return _rejected("MCP_REQUEST_INVALID")
    if set(request) != {"tool_name", "arguments"}:
        return _rejected("MCP_REQUEST_SCHEMA_INVALID")
    if request.get("tool_name") != TOOL_NAME:
        return _rejected("MCP_TOOL_NAME_INVALID")
    arguments = request.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {"rehearsal_run"} or not isinstance(arguments.get("rehearsal_run"), dict):
        return _rejected("MCP_ARGUMENTS_INVALID")
    try:
        result = evaluate_agent_run(arguments["rehearsal_run"])
    except AgentRunCapabilityError as exc:
        return _rejected(exc.code)
    return _validate({
        "tool_result": "SUCCESS",
        "run_ref": result["run_ref"],
        "trace_ref": result["trace_ref"],
        "claim_type": result["claim_type"],
        "assessment": result["assessment"],
        "profile_result": result["profile_result"],
        "missing_requirements": list(result["missing_requirements"]),
        "failed_relationships": list(result["failed_relationships"]),
        "reason_codes": list(result["reason_codes"]),
        "limitations": list(result["limitations"]),
        "boundary_statement": result["boundary_statement"],
    })
