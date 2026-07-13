"""Fail-closed execution-control simulation for Phase 13.1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "schemas/saee-external-validation-execution-request.schema.v0.1.json"
SCENARIOS = ROOT / "agent-interface/ecosystem/execution-simulation"
LIMITATIONS = [
    "Execution control is simulated locally; no participant, agent or external system is connected.",
    "The result does not authorize external validation, production execution, adoption or certification.",
]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def simulate_execution(scenario: dict[str, Any]) -> dict[str, Any]:
    request = scenario.get("execution_request")
    schema = _load(REQUEST_SCHEMA)
    if not isinstance(request, dict) or list(Draft202012Validator(schema).iter_errors(request)):
        raise ValueError("EXECUTION_SIMULATION_REQUEST_INVALID")
    decision = scenario.get("readiness_decision")
    authorization = scenario.get("authorization_state")
    event = scenario.get("boundary_event")
    if event == "CREDENTIAL_EXPOSURE":
        result, reason = "TERMINATED", "CREDENTIAL_EXPOSURE"
    elif event == "CUSTOMER_DATA_RECEIVED":
        result, reason = "TERMINATED", "CUSTOMER_DATA_RECEIVED"
    elif decision != "GO":
        result, reason = "BLOCKED", "READINESS_HOLD"
    elif authorization != "SIMULATION_RECORD_ONLY" or not request["authorization_reference"].startswith("simulation-authorization:"):
        result, reason = "BLOCKED", "FAKE_AUTHORIZATION_REJECTED"
    elif request["execution_type"] == "EXTERNAL_VALIDATION":
        result, reason = "BLOCKED", "EXTERNAL_VALIDATION_DISABLED"
    else:
        result, reason = "SIMULATION_ALLOWED", "SIMULATION_PATH_ALLOWED"
    return {
        "simulation_id": f"execution-simulation:{scenario['scenario_id'].lower().replace('_', '-')}",
        "readiness_decision": decision,
        "execution_request": request,
        "authorization_state": authorization,
        "result": result,
        "reason_code": reason,
        "limitations": list(LIMITATIONS),
        "truth_boundary": {"execution_simulation": True, "external_validation": False, "execution_authorized": False, "real_participants": False, "participants_invited": 0, "customer_data": False, "production_ready": False},
    }


def run_execution_simulation_suite() -> dict[str, Any]:
    scenarios = [_load(path) for path in sorted(SCENARIOS.glob("*.json"))]
    results, evidence = [], []
    for scenario in scenarios:
        result = simulate_execution(scenario)
        results.append({**result, "scenario_id": scenario["scenario_id"], "matched_expected": result["result"] == scenario["expected_result"] and result["reason_code"] == scenario["expected_reason_code"]})
        evidence.append({
            "evidence_id": f"execution-simulation-evidence:{scenario['scenario_id'].lower().replace('_', '-')}",
            "evidence_type": "termination_record" if result["result"] == "TERMINATED" else "decision_record",
            "simulation_ref": result["simulation_id"], "result": result["result"], "reason_code": result["reason_code"],
            "limitations": ["Synthetic execution-control record only; no request payload or sensitive event value retained."],
            "external_validation_completed": False,
        })
    return {
        "execution_simulation_version": "0.1",
        "entry_decision_reference": "agent-interface/ecosystem/saee-external-validation-entry-decision.v0.1.json",
        "status": "PASS" if all(item["matched_expected"] for item in results) else "FAIL",
        "scenario_results": results,
        "evidence_records": evidence,
        "limitations": list(LIMITATIONS),
        "truth_boundary": {"execution_simulation": True, "external_validation": False, "execution_authorized": False, "real_participants": False, "participants_invited": 0, "customer_data": False, "adoption_validated": False, "production_ready": False, "network_accessed": False, "subprocess_started": False, "external_execution": False},
    }
