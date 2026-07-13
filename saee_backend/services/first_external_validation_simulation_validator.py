"""Validate the bounded first-candidate external-validation simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RECORD_SCHEMA_PATH = ROOT / "schemas/saee-external-validation-simulation-record.schema.v0.1.json"
FEEDBACK_SCHEMA_PATH = ROOT / "schemas/saee-ecosystem-validation-feedback.schema.v0.1.json"
CANDIDATE_PATH = ROOT / "agent-interface/ecosystem/external-validation-simulation/synthetic-mcp-agent-developer.json"
MATRIX_PATH = ROOT / "agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json"
SCOPE_SCHEMA_PATH = ROOT / "schemas/saee-first-ecosystem-validation-scope.schema.v0.1.json"
FORBIDDEN_FIELDS = {
    "real_identity", "real_company", "real_contact", "external_account",
    "real_candidate", "adoption_claim", "customer_claim", "customer_success",
    "adoption_proof", "market_validation", "production_validation",
}
EXPECTED_SCOPE = {"capability_discovery", "mcp_tool_discovery", "local_invocation", "result_interpretation", "documentation_feedback"}
EXPECTED_SCENARIOS = {
    "SUCCESSFUL_MCP_DISCOVERY", "SUCCESSFUL_TOOL_INVOCATION", "RESULT_INTERPRETATION_SUCCESS",
    "AUTHORIZATION_CONFUSION", "PRODUCTION_EXECUTION_REQUEST", "FEEDBACK_GENERATION", "ADOPTION_CLAIM_ATTEMPT",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_forbidden_field(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in FORBIDDEN_FIELDS or _has_forbidden_field(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_has_forbidden_field(child) for child in value)
    return False


def _result(valid: bool, reasons: list[str], scenario_count: int = 0, feedback_count: int = 0) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reasons,
        "candidate_valid": valid,
        "candidate_type": "mcp_agent_developer" if valid else "",
        "scenario_count": scenario_count,
        "feedback_record_count": feedback_count,
        "scope_valid": valid,
        "feedback_valid": valid,
        "evidence_boundary": valid,
        "synthetic_only": valid,
        "external_validation": False,
        "participant_contact": False,
        "customer_data": False,
        "adoption_validated": False,
        "production_ready": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
    }


def validate_simulation_data(candidate: Any, feedback: Any, record: Any) -> dict[str, Any]:
    scenario_count = len(record.get("scenario_results", [])) if isinstance(record, dict) else 0
    feedback_count = len(record.get("feedback_records", [])) if isinstance(record, dict) else 0
    if not all(isinstance(value, dict) for value in (candidate, feedback, record)):
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_DATA_INVALID"], scenario_count, feedback_count)
    if _has_forbidden_field({"candidate": candidate, "feedback": feedback, "record": record}):
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_FORBIDDEN_FIELD"], scenario_count, feedback_count)
    if set(candidate) != {"candidate_id", "candidate_type", "simulation_only", "validation_goal", "integration_scope", "limitations"}:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_CANDIDATE_INVALID"], scenario_count, feedback_count)
    if candidate.get("candidate_id") != "synthetic-candidate:mcp-agent-developer-001" or candidate.get("candidate_type") != "mcp_agent_developer" or candidate.get("simulation_only") is not True:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_CANDIDATE_INVALID"], scenario_count, feedback_count)
    if set(candidate.get("integration_scope", [])) != EXPECTED_SCOPE:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_SCOPE_INVALID"], scenario_count, feedback_count)

    matrix = _load(MATRIX_PATH)
    if matrix["candidates"][0]["priority"] != "P0" or matrix["candidates"][0]["candidate"]["candidate_type"] != candidate["candidate_type"]:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_CANDIDATE_PRIORITY_INVALID"], scenario_count, feedback_count)
    if list(Draft202012Validator(_load(SCOPE_SCHEMA_PATH)).iter_errors(matrix.get("validation_scope_model"))):
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_SCOPE_INVALID"], scenario_count, feedback_count)
    if list(Draft202012Validator(_load(FEEDBACK_SCHEMA_PATH)).iter_errors(feedback)) or feedback.get("simulation_only") is not True:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_FEEDBACK_INVALID"], scenario_count, feedback_count)
    if list(Draft202012Validator(_load(RECORD_SCHEMA_PATH)).iter_errors(record)):
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_RECORD_INVALID"], scenario_count, feedback_count)
    if {item.get("scenario_id") for item in record["scenario_results"]} != EXPECTED_SCENARIOS or any(item.get("matched_expected") is not True for item in record["scenario_results"]):
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_SCENARIO_RESULT_INVALID"], scenario_count, feedback_count)
    if record.get("feedback_records") != [feedback]:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_FEEDBACK_BINDING_INVALID"], scenario_count, feedback_count)
    boundary = record.get("evidence_boundary", {})
    if boundary.get("external_validation_simulation") is not True or boundary.get("synthetic_candidate") is not True:
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_BOUNDARY_INVALID"], scenario_count, feedback_count)
    if any(boundary.get(key) is not False for key in ("external_validation", "participant_contact", "real_external_agent", "customer_data", "adoption_validated", "production_ready", "network_accessed", "external_execution")):
        return _result(False, ["FIRST_EXTERNAL_SIMULATION_BOUNDARY_INVALID"], scenario_count, feedback_count)
    return _result(True, [], scenario_count, feedback_count)
