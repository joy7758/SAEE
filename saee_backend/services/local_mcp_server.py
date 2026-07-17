"""Dependency-free, in-memory MCP-compatible abstraction for one SAEE Tool.

This module is intentionally not a network or stdio listener. It models fixed
Tool discovery and invocation semantics for local protocol validation only.
"""

from __future__ import annotations

from typing import Any

from saee_backend.services.mcp_evidence_tool_handler import TOOL_NAME, handle_mcp_evidence_tool
from saee_backend.services.mcp_agent_run_tool_handler import (
    TOOL_NAME as REHEARSAL_RUN_TOOL_NAME,
    handle_mcp_agent_run_tool,
)


class LocalMCPServer:
    """Single-tool local prototype with no transport side effects."""

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": TOOL_NAME,
                "description": "Evaluate evidence sufficiency for defined accountability claims.",
                "input_schema_ref": "agent-interface/mcp/saee-mcp-local-request.schema.v0.1.json#/properties/arguments",
                "output_schema_ref": "agent-interface/mcp/saee-mcp-local-response.schema.v0.1.json",
                "read_only_intent": True,
                "side_effects_allowed": False,
            },
            {
                "name": REHEARSAL_RUN_TOOL_NAME,
                "description": "Evaluate evidence adequacy for a strict SAEE Agent Rehearsal Run.",
                "input_schema_ref": "agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json#/properties/arguments",
                "output_schema_ref": "agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json",
                "read_only_intent": True,
                "side_effects_allowed": False,
            },
        ]

    def call_tool(self, request: Any) -> dict[str, Any]:
        if isinstance(request, dict) and request.get("tool_name") == REHEARSAL_RUN_TOOL_NAME:
            return handle_mcp_agent_run_tool(request)
        return handle_mcp_evidence_tool(request)

    def runtime_status(self) -> dict[str, bool | str | int]:
        return {
            "implementation_status": "local_prototype",
            "mcp_local_prototype": True,
            "tool_count": 2,
            "evaluate_rehearsal_run_tool_available": True,
            "network_accessed": False,
            "subprocess_started": False,
            "persistence_performed": False,
            "public_endpoint_available": False,
            "authentication_available": False,
            "external_agents_connected": False,
            "production_ready": False,
        }


def create_local_mcp_server() -> LocalMCPServer:
    """Create an isolated in-memory prototype instance."""

    return LocalMCPServer()
