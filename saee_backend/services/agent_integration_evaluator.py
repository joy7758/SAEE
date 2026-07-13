"""Deterministic evaluator for local Agent integration examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
INTERPRETATION_SCHEMA = ROOT / "schemas/saee-agent-result-interpretation.schema.v0.1.json"
EXPECTED_KEYS = {"scenario_id", "caller_type", "transport", "discovered_capability_id", "selected_operation", "invocation_status", "interpretation", "expected_outcome", "truth_boundary"}
TRANSPORTS = {"MCP_STDIO", "HTTP_LOCALHOST", "GENERIC_FRAMEWORK"}
OPERATIONS = {"evaluate_agent_run", "evaluate_evidence", "rehearse_agent"}


def evaluate_integration_scenario(value: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not isinstance(value, dict) or set(value) != EXPECTED_KEYS:
        return _result(value, False, ["INTEGRATION_SCENARIO_INVALID"])
    discovery = value["discovered_capability_id"] == "saee.agent-reliability"
    if not discovery:
        reasons.append("INTEGRATION_CAPABILITY_NOT_DISCOVERED")
    transport = value["transport"] in TRANSPORTS
    if not transport:
        reasons.append("INTEGRATION_TRANSPORT_INVALID")
    invocation = value["selected_operation"] in OPERATIONS and value["invocation_status"] in {"SUCCESS", "REJECTED", "CONTRACT_ONLY"}
    if not invocation:
        reasons.append("INTEGRATION_INVOCATION_INVALID")
    schema = json.loads(INTERPRETATION_SCHEMA.read_text(encoding="utf-8"))
    interpretation_errors = list(Draft202012Validator(schema).iter_errors(value["interpretation"]))
    interpretation = not interpretation_errors
    if not interpretation:
        reasons.append("INTEGRATION_INTERPRETATION_INVALID")
    boundary = isinstance(value["truth_boundary"], dict) and all(value["truth_boundary"].get(field) is False for field in ("external_agent_connected", "customer_data_used", "adoption_validated", "marketplace_listed", "production_ready"))
    if not boundary:
        reasons.append("INTEGRATION_BOUNDARY_OVERCLAIM")
    valid = not reasons
    return _result(value, valid, reasons, discovery=discovery, invocation=invocation, interpretation=interpretation, boundary=boundary)


def _result(value: Any, valid: bool, reasons: list[str], *, discovery: bool = False, invocation: bool = False, interpretation: bool = False, boundary: bool = False) -> dict[str, Any]:
    return {
        "scenario_id": value.get("scenario_id", "") if isinstance(value, dict) else "",
        "result": "PASS" if valid else "FAIL",
        "discovery_correct": discovery,
        "invocation_correct": invocation,
        "interpretation_correct": interpretation,
        "boundary_preserved": boundary,
        "reason_codes": reasons,
        "agent_intelligence_evaluated": False,
        "external_agents_connected": False,
        "adoption_validated": False,
        "production_ready": False
    }

