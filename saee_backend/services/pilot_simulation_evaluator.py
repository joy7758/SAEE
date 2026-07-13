"""Deterministic evaluator for local SAEE controlled Pilot simulations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_backend.services.pilot_simulator import (
    delete_simulated_data,
    retain_artifacts,
    revoke_access,
    simulate_transition,
    terminate_pilot,
)


EXPECTED_TOP_LEVEL = {
    "schema_version",
    "simulation_id",
    "scenario_type",
    "synthetic",
    "initial_state",
    "gate_states",
    "requested_transitions",
    "boundary_events",
    "termination_request",
    "closure_actions",
    "expected_result",
}

TRUTH_FALSE_FIELDS = (
    "external_pilot_executed",
    "external_agent_connected",
    "customer_data_used",
    "data_collected",
    "approval_granted",
    "customer_validated",
    "external_validation_completed",
    "network_accessed",
    "subprocess_started",
    "external_execution",
    "production_ready",
)


def _base_result(scenario: Any) -> dict[str, Any]:
    return {
        "simulation_id": scenario.get("simulation_id", "") if isinstance(scenario, dict) else "",
        "scenario_type": scenario.get("scenario_type", "") if isinstance(scenario, dict) else "",
        "simulation_result": "REJECT",
        "current_state": "DESIGN_ONLY",
        "gate_status": "NOT_EVALUATED",
        "stop_reason": "INVALID_SCENARIO",
        "cleanup_result": "NOT_REQUIRED",
        "reason_codes": [],
        "transition_trace": [],
        "boundary_preserved": True,
        "simulation_only": True,
        "synthetic_agent_only": True,
        "synthetic_data_only": True,
        "external_pilot_executed": False,
        "external_agent_connected": False,
        "customer_data_used": False,
        "data_collected": False,
        "approval_granted": False,
        "customer_validated": False,
        "external_validation_completed": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _cleanup(actions: dict[str, Any]) -> tuple[str, list[str]]:
    revoked = revoke_access(actions.get("revoke_access") is True)
    deleted = delete_simulated_data(actions.get("delete_simulated_data") is True)
    retained = retain_artifacts(actions.get("retain_artifacts") is True)
    reasons: list[str] = []
    if not revoked["access_revoked"]:
        reasons.append("SIMULATION_ACCESS_REVOCATION_MISSING")
    if not deleted["simulated_data_deleted"]:
        reasons.append("SIMULATION_SYNTHETIC_DATA_DELETION_MISSING")
    if not retained["bounded_artifacts_retained"]:
        reasons.append("SIMULATION_ARTIFACT_RETENTION_MISSING")
    return ("COMPLETED" if not reasons else "PENDING", reasons)


def evaluate_pilot_simulation(scenario: Any) -> dict[str, Any]:
    """Evaluate one checked-in synthetic scenario without any external operation."""

    result = _base_result(scenario)
    if not isinstance(scenario, dict) or set(scenario) != EXPECTED_TOP_LEVEL:
        result["reason_codes"] = ["SIMULATION_SCENARIO_STRUCTURE_INVALID"]
        result["boundary_preserved"] = False
        return result
    if scenario.get("synthetic") is not True or scenario.get("initial_state") != "DESIGN_ONLY":
        result["reason_codes"] = ["SIMULATION_SYNTHETIC_BOUNDARY_REQUIRED"]
        result["boundary_preserved"] = False
        return result

    current_state = "DESIGN_ONLY"
    gate_status = "ALL_SYNTHETIC_GATES_SATISFIED"
    for target_state in scenario.get("requested_transitions", []):
        transition = simulate_transition(current_state, target_state, scenario.get("gate_states", {}))
        result["transition_trace"].append({
            "from": current_state,
            "to": target_state,
            "allowed": transition["transition_allowed"],
            "reason_code": transition["reason_code"],
        })
        if not transition["transition_allowed"]:
            result.update({
                "simulation_result": "BLOCK",
                "current_state": current_state,
                "gate_status": "BLOCKED_FAIL_CLOSED",
                "stop_reason": "MISSING_SECURITY_GATE" if target_state == "SECURITY_READY" else "MANDATORY_GATE_NOT_APPROVED",
                "reason_codes": [transition["reason_code"]],
            })
            return result
        current_state = transition["current_state"]

    result["current_state"] = current_state
    result["gate_status"] = gate_status
    if current_state != "PILOT_ACTIVE":
        result.update({
            "simulation_result": "BLOCK",
            "gate_status": "INCOMPLETE_TRANSITION_PATH",
            "stop_reason": "MANDATORY_GATE_NOT_APPROVED",
            "reason_codes": ["SIMULATION_PILOT_ACTIVE_NOT_REACHED"],
        })
        return result

    events = scenario.get("boundary_events", {})
    if events.get("secret_exposure") is True:
        terminated = terminate_pilot(current_state, "SECRET_EXPOSURE")
        cleanup_result, reasons = _cleanup(scenario.get("closure_actions", {}))
        result.update({
            "simulation_result": "IMMEDIATE_TERMINATION",
            "current_state": terminated["current_state"],
            "stop_reason": "SECRET_EXPOSURE",
            "cleanup_result": cleanup_result,
            "reason_codes": ["SIMULATION_SECRET_EXPOSURE_TERMINATED", *reasons],
        })
        return result

    if events.get("customer_data_without_approval") is True or events.get("unauthorized_action") is True:
        stop_reason = "DATA_BOUNDARY_VIOLATION" if events.get("customer_data_without_approval") is True else "UNAUTHORIZED_ACTION"
        terminated = terminate_pilot(current_state, stop_reason)
        cleanup_result, reasons = _cleanup(scenario.get("closure_actions", {}))
        result.update({
            "simulation_result": "STOP",
            "current_state": terminated["current_state"],
            "stop_reason": stop_reason,
            "cleanup_result": cleanup_result,
            "reason_codes": [f"SIMULATION_{stop_reason}_STOPPED", *reasons],
        })
        return result

    if scenario.get("termination_request") is True:
        terminated = terminate_pilot(current_state, "NORMAL_TERMINATION")
        cleanup_result, reasons = _cleanup(scenario.get("closure_actions", {}))
        result.update({
            "simulation_result": "PASS" if cleanup_result == "COMPLETED" else "STOP",
            "current_state": terminated["current_state"],
            "stop_reason": "NORMAL_TERMINATION",
            "cleanup_result": cleanup_result,
            "reason_codes": reasons,
        })
        return result

    result.update({
        "simulation_result": "PASS",
        "stop_reason": "NONE",
        "cleanup_result": "NOT_REQUIRED",
        "reason_codes": [],
    })
    return result


def validate_simulation_truth_claims(value: Any) -> dict[str, Any]:
    """Reject aggregate outputs that overclaim real-world Pilot state."""

    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["SIMULATION_RESULT_INVALID"]}
    for field in TRUTH_FALSE_FIELDS:
        if value.get(field) is not False:
            return {"valid": False, "reason_codes": [f"SIMULATION_REAL_WORLD_CLAIM_FORBIDDEN:{field}"]}
    if value.get("simulation_only") is not True:
        return {"valid": False, "reason_codes": ["SIMULATION_ONLY_MARKER_REQUIRED"]}
    return {"valid": True, "reason_codes": []}


def evaluate_pilot_simulation_path(path: Path) -> dict[str, Any]:
    """Load one local JSON scenario and evaluate it offline."""

    return evaluate_pilot_simulation(json.loads(path.read_text(encoding="utf-8")))
