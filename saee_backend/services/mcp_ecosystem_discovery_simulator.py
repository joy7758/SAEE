"""Discover and select SAEE MCP tools for fixed synthetic task classes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOOLS_PATH = ROOT / "ecosystem/mcp-entry-package-v1/mcp-tools.json"
SELECTION = {
    "AGENT_RELIABILITY_ASSESSMENT": ("evaluate_rehearsal_run", "SELECTED"),
    "EVIDENCE_ADEQUACY_EVALUATION": ("evaluate_evidence", "SELECTED"),
    "CONTROLLED_REHEARSAL_REQUEST": ("rehearse_agent", "SELECTED"),
    "REAL_TIME_AUTHORIZATION": ("NONE", "REJECTED_NOT_SAEE_CAPABILITY"),
    "PRODUCTION_DEPLOYMENT_APPROVAL": ("NONE", "REJECTED_NOT_SAEE_CAPABILITY"),
    "SIMPLE_INFORMATION_QUERY": ("NONE", "ABSTAINED_NO_SAEE_NEED"),
}


def discover_tools() -> list[str]:
    value = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
    tools = value.get("tools")
    if not isinstance(tools, list):
        raise ValueError("MCP_DRY_PACKAGE_INVALID")
    names = [item.get("name") for item in tools if isinstance(item, dict)]
    if names != ["evaluate_rehearsal_run", "evaluate_evidence", "rehearse_agent"]:
        raise ValueError("MCP_DRY_TOOL_SET_INVALID")
    return names


def select_tool(scenario: Any) -> dict[str, str]:
    if not isinstance(scenario, dict) or scenario.get("simulation_only") is not True:
        raise ValueError("MCP_DRY_SCENARIO_INVALID")
    forbidden = {"real_agent_identity", "external_connection", "customer_data"}
    if forbidden.intersection(scenario):
        raise ValueError("MCP_DRY_FORBIDDEN_SCENARIO_FIELD")
    task_type = scenario.get("task_type")
    if task_type not in SELECTION:
        raise ValueError("MCP_DRY_TASK_TYPE_UNSUPPORTED")
    selected, status = SELECTION[task_type]
    return {"selected_tool": selected, "selection_status": status}

