"""Offline validator for the Phase 14.1 entry-decision simulation result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_backend.services.entry_decision_simulation import ENTRY_REFERENCE, run_entry_decision_simulation


ROOT = Path(__file__).resolve().parents[2]
RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-entry-decision-simulation-result.v0.1.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def validate_entry_decision_simulation(value: Any) -> dict[str, Any]:
    reasons: list[str] = []
    required = {"simulation_version", "entry_decision_reference", "scenario_results", "decision_distribution", "authorization_distribution", "limitations", "truth_boundary"}
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["ENTRY_DECISION_SIMULATION_INVALID"]}
    if set(value) != required or value.get("simulation_version") != "0.1" or value.get("entry_decision_reference") != ENTRY_REFERENCE:
        reasons.append("ENTRY_DECISION_SIMULATION_CONTRACT_INVALID")
    results = value.get("scenario_results", [])
    if not isinstance(results, list) or len(results) < 7 or any(item.get("matched_expected") is not True for item in results if isinstance(item, dict)):
        reasons.append("ENTRY_DECISION_SIMULATION_SCENARIOS_INCOMPLETE")
    if not {"HOLD", "CONDITIONAL_ENTRY_REVIEW", "ENTRY_READY"}.issubset({item.get("decision_result") for item in results if isinstance(item, dict)}):
        reasons.append("ENTRY_DECISION_SIMULATION_BRANCHES_INCOMPLETE")
    if any(item.get("execution_authorized") is not False for item in results if isinstance(item, dict)):
        reasons.append("ENTRY_DECISION_SIMULATION_AUTHORIZATION_SEPARATION_FAILED")
    distribution = value.get("decision_distribution", {})
    if not isinstance(distribution, dict) or set(distribution) != {"HOLD", "CONDITIONAL_ENTRY_REVIEW", "ENTRY_READY", "REJECTED"} or sum(distribution.values()) != len(results):
        reasons.append("ENTRY_DECISION_SIMULATION_DISTRIBUTION_INVALID")
    authorization = value.get("authorization_distribution", {})
    if authorization.get("execution_authorized_count") != 0 or authorization.get("execution_not_authorized_count") != len(results):
        reasons.append("ENTRY_DECISION_SIMULATION_AUTHORIZATION_COUNT_INVALID")
    truth = value.get("truth_boundary", {})
    expected_truth = {"entry_decision_simulation", "external_validation", "execution_authorized", "real_participants", "participants_invited", "customer_validated", "adoption_validated", "production_ready", "network_accessed", "subprocess_started", "external_execution"}
    false_fields = ("external_validation", "execution_authorized", "real_participants", "customer_validated", "adoption_validated", "production_ready", "network_accessed", "subprocess_started", "external_execution")
    if not isinstance(truth, dict) or set(truth) != expected_truth or truth.get("entry_decision_simulation") is not True or truth.get("participants_invited") != 0 or any(truth.get(field) is not False for field in false_fields):
        reasons.append("ENTRY_DECISION_SIMULATION_EXTERNAL_STATE_FORBIDDEN")
    if not isinstance(value.get("limitations"), list) or len(value["limitations"]) < 3:
        reasons.append("ENTRY_DECISION_SIMULATION_LIMITATIONS_REQUIRED")
    valid = not reasons
    return {
        "valid": valid,
        "reason_codes": list(dict.fromkeys(reasons)),
        "decision_logic_connected": valid,
        "gap_logic": valid,
        "evidence_logic": valid,
        "authorization_separation": valid,
    }


def validate_current_entry_decision_simulation() -> dict[str, Any]:
    stored = _load(RESULT_PATH)
    if stored != run_entry_decision_simulation():
        return {"valid": False, "reason_codes": ["ENTRY_DECISION_SIMULATION_RESULT_DRIFT"]}
    return validate_entry_decision_simulation(stored)
