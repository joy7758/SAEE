"""Offline validator for SAEE Phase 13.1 execution-control simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from saee_backend.services.external_validation_execution_simulator import run_execution_simulation_suite


ROOT = Path(__file__).resolve().parents[2]
RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-external-validation-execution-simulation-result.v0.1.json"
SIMULATION_SCHEMA = ROOT / "schemas/saee-external-validation-execution-simulation.schema.v0.1.json"
REQUEST_SCHEMA = ROOT / "schemas/saee-external-validation-execution-request.schema.v0.1.json"
EVIDENCE_SCHEMA = ROOT / "schemas/saee-external-validation-execution-evidence.schema.v0.1.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def validate_execution_simulation(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["EXECUTION_SIMULATION_INVALID"]}
    reasons: list[str] = []
    required = {"execution_simulation_version", "entry_decision_reference", "status", "scenario_results", "evidence_records", "limitations", "truth_boundary"}
    if set(value) != required or value.get("execution_simulation_version") != "0.1" or value.get("status") != "PASS":
        reasons.append("EXECUTION_SIMULATION_CONTRACT_INVALID")
    if value.get("entry_decision_reference") != "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json":
        reasons.append("EXECUTION_SIMULATION_ENTRY_DECISION_REFERENCE_INVALID")
    request_schema, simulation_schema, evidence_schema = _load(REQUEST_SCHEMA), _load(SIMULATION_SCHEMA), _load(EVIDENCE_SCHEMA)
    registry = Registry().with_resource(request_schema["$id"], Resource.from_contents(request_schema))
    simulation_validator = Draft202012Validator(simulation_schema, registry=registry)
    scenarios = value.get("scenario_results", [])
    if len(scenarios) < 6:
        reasons.append("EXECUTION_SIMULATION_SCENARIOS_INCOMPLETE")
    for item in scenarios:
        projected = {key: item[key] for key in ("simulation_id", "readiness_decision", "execution_request", "authorization_state", "result", "reason_code", "limitations", "truth_boundary") if key in item}
        if list(simulation_validator.iter_errors(projected)) or item.get("matched_expected") is not True:
            reasons.append("EXECUTION_SIMULATION_SCENARIO_INVALID"); break
    evidence = value.get("evidence_records", [])
    if len(evidence) < 6 or any(list(Draft202012Validator(evidence_schema).iter_errors(item)) for item in evidence):
        reasons.append("EXECUTION_SIMULATION_EVIDENCE_INVALID")
    truth = value.get("truth_boundary", {})
    false_fields = ("external_validation", "execution_authorized", "real_participants", "customer_data", "adoption_validated", "production_ready", "network_accessed", "subprocess_started", "external_execution")
    if not isinstance(truth, dict) or truth.get("execution_simulation") is not True or any(truth.get(field) is not False for field in false_fields) or truth.get("participants_invited") != 0:
        reasons.append("EXECUTION_SIMULATION_EXTERNAL_STATE_FORBIDDEN")
    if any(item.get("result") == "SIMULATION_ALLOWED" and item.get("truth_boundary", {}).get("execution_authorized") is not False for item in scenarios):
        reasons.append("EXECUTION_SIMULATION_FAKE_AUTHORIZATION")
    return {"valid": not reasons, "reason_codes": list(dict.fromkeys(reasons)), "decision_gate_connected": not reasons, "authorization_check": not reasons, "termination_check": not reasons, "evidence_boundary": not reasons}


def validate_current_execution_simulation() -> dict[str, Any]:
    stored = _load(RESULT_PATH)
    if stored != run_execution_simulation_suite():
        return {"valid": False, "reason_codes": ["EXECUTION_SIMULATION_RESULT_DRIFT"]}
    return validate_execution_simulation(stored)
