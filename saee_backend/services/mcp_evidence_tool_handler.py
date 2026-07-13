"""Bounded request/response adapter for the local SAEE MCP prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.local_evidence_tool import (
    BOUNDARY_STATEMENT,
    LIMITATIONS,
    evaluate_evidence_tool,
)


ROOT = Path(__file__).resolve().parents[2]
RESPONSE_SCHEMA_PATH = ROOT / "agent-interface/mcp/saee-mcp-local-response.schema.v0.1.json"
TOOL_NAME = "evaluate_evidence_adequacy"
MCP_PROJECTION_LIMITATION = (
    "The canonical local Tool has no built-in MCP runtime; this response is projected "
    "by a separate dependency-free in-memory protocol prototype."
)


def _projected_limitations(limitations: list[str]) -> list[str]:
    return [*limitations, MCP_PROJECTION_LIMITATION]


def _validate_response(response: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(RESPONSE_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(response), key=lambda error: list(error.absolute_path))
    if errors:
        raise RuntimeError("SAEE local MCP prototype produced an invalid response")
    return response


def _rejected(code: str) -> dict[str, Any]:
    return _validate_response({
        "tool_result": "REJECTED_INPUT",
        "claim_assessment": "UNKNOWN",
        "evidence_sufficiency_status": "UNKNOWN",
        "missing_requirements": [],
        "reason_codes": [code],
        "limitations": _projected_limitations(list(LIMITATIONS)),
        "boundary_statement": BOUNDARY_STATEMENT,
    })


def _project_tool_response(result: dict[str, Any]) -> dict[str, Any]:
    return _validate_response({
        "tool_result": result["tool_result"],
        "claim_assessment": result["claim_assessment"],
        "evidence_sufficiency_status": result["evidence_sufficiency_status"],
        "missing_requirements": list(result["missing_requirements"]),
        "reason_codes": list(result["reason_codes"]),
        "limitations": _projected_limitations(list(result["limitations"])),
        "boundary_statement": result["boundary_statement"],
    })


def handle_mcp_evidence_tool(request: Any) -> dict[str, Any]:
    """Handle one in-memory request and reuse the canonical local Tool adapter."""

    if not isinstance(request, dict):
        return _rejected("MCP_REQUEST_INVALID")
    if set(request) - {"tool_name", "arguments"}:
        return _rejected("MCP_REQUEST_SCHEMA_INVALID")
    if request.get("tool_name") != TOOL_NAME:
        return _rejected("MCP_TOOL_NAME_INVALID")
    arguments = request.get("arguments")
    if not isinstance(arguments, dict):
        return _rejected("MCP_ARGUMENTS_INVALID")
    return _project_tool_response(evaluate_evidence_tool(arguments))
