"""Strict offline validator for Phase 12.1 simulation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-simulation-result.v0.1.json"
PARTICIPANT_SCHEMA = ROOT / "schemas/saee-external-validation-simulation-participant.schema.v0.1.json"
EVIDENCE_SCHEMA = ROOT / "schemas/saee-external-validation-simulation-evidence.schema.v0.1.json"
FEEDBACK_SCHEMA = ROOT / "schemas/saee-external-validation-simulation-feedback.schema.v0.1.json"
PARTICIPANTS = ROOT / "agent-interface/ecosystem/external-validation-simulation"
FORBIDDEN_FIELDS = {"credentials", "private_prompts", "private_prompt", "customer_data_value", "chain_of_thought", "real_identity", "real_company", "real_customer", "external_contact"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def validate_external_validation_simulation(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["EXTERNAL_VALIDATION_SIMULATION_INVALID"]}
    reasons: list[str] = []
    required = {"simulation_version", "status", "participants", "scenario_results", "evidence_records", "feedback_records", "exit_review", "limitations", "truth_boundary"}
    if set(value) != required or value.get("simulation_version") != "0.1" or value.get("status") != "PASS":
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_CONTRACT_INVALID")
    if len(value.get("participants", [])) < 3 or len(set(value.get("participants", []))) < 3:
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_PARTICIPANTS_INCOMPLETE")
    scenarios = value.get("scenario_results", [])
    if len(scenarios) < 6 or not all(isinstance(item, dict) and item.get("matched_expected") is True for item in scenarios):
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_WORKFLOW_INCOMPLETE")
    evidence_schema, feedback_schema = _load(EVIDENCE_SCHEMA), _load(FEEDBACK_SCHEMA)
    if len(value.get("evidence_records", [])) < 6 or any(list(Draft202012Validator(evidence_schema).iter_errors(item)) for item in value.get("evidence_records", [])):
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_EVIDENCE_INVALID")
    if len(value.get("feedback_records", [])) < 3 or any(list(Draft202012Validator(feedback_schema).iter_errors(item)) for item in value.get("feedback_records", [])):
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_FEEDBACK_INVALID")
    serialized = json.dumps(value, ensure_ascii=False).lower()
    if any(f'"{field}"' in serialized for field in FORBIDDEN_FIELDS):
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_SENSITIVE_FIELD_FORBIDDEN")
    exit_review = value.get("exit_review", {})
    if exit_review != {"authorized_success_flow_completed": True, "terminated_scenarios": 2, "blocked_or_rejected_scenarios": 3, "real_validation_exit_criteria_met": False}:
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_EXIT_REVIEW_INVALID")
    truth = value.get("truth_boundary", {})
    if not isinstance(truth, dict) or truth.get("external_validation_simulation") is not True or truth.get("synthetic_participants_only") is not True:
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_BOUNDARY_INVALID")
    false_fields = ("external_validation", "real_participants", "external_agents_connected", "customer_data", "customer_validated", "adoption_validated", "marketplace_listed", "market_validation", "production_ready", "network_accessed", "subprocess_started", "external_execution")
    if any(truth.get(field) is not False for field in false_fields) or truth.get("participants_invited") != 0:
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_EXTERNAL_STATE_FORBIDDEN")
    return {"valid": not reasons, "reason_codes": list(dict.fromkeys(reasons)), "authorization_flow": not reasons, "scope_control": not reasons, "evidence_boundary": not reasons, "termination_control": not reasons, "feedback_valid": not reasons}


def validate_current_external_validation_simulation() -> dict[str, Any]:
    schema = _load(PARTICIPANT_SCHEMA)
    for path in PARTICIPANTS.glob("sim-*.json"):
        if list(Draft202012Validator(schema).iter_errors(_load(path))):
            return {"valid": False, "reason_codes": ["EXTERNAL_VALIDATION_SIMULATION_PARTICIPANT_INVALID"]}
    return validate_external_validation_simulation(_load(RESULT_PATH))
