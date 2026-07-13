"""Pure in-memory lifecycle primitives for the SAEE controlled Pilot simulation.

Synthetic gate approval models dependency satisfaction only. No function in this
module grants real approval, persists state, or executes an external action.
"""

from __future__ import annotations

from typing import Any


STATES = (
    "DESIGN_ONLY",
    "TECHNICAL_READY",
    "SECURITY_READY",
    "DATA_READY",
    "HUMAN_OWNER_ASSIGNED",
    "EXECUTION_AUTHORIZED",
    "PILOT_ACTIVE",
    "PILOT_TERMINATED",
)

GATE_FOR_TARGET = {
    "TECHNICAL_READY": "TECHNICAL_READINESS",
    "SECURITY_READY": "SECURITY_REVIEW",
    "DATA_READY": "DATA_APPROVAL",
    "HUMAN_OWNER_ASSIGNED": "HUMAN_RESPONSIBILITY_ASSIGNMENT",
    "EXECUTION_AUTHORIZED": "EXECUTION_AUTHORIZATION",
    "PILOT_ACTIVE": "EXECUTION_AUTHORIZATION",
}


def validate_gate(gate_id: str, gate: Any) -> dict[str, Any]:
    """Validate one synthetic gate without treating it as real approval."""

    valid = (
        isinstance(gate, dict)
        and gate.get("status") == "APPROVED"
        and isinstance(gate.get("evidence_reference"), str)
        and gate["evidence_reference"].startswith("synthetic:")
        and isinstance(gate.get("approval_reference"), str)
        and gate["approval_reference"].startswith("synthetic:")
    )
    return {
        "gate_id": gate_id,
        "gate_valid": valid,
        "synthetic_approval_only": True,
        "real_approval_granted": False,
        "reason_code": "" if valid else f"SIMULATION_GATE_{gate_id}_NOT_APPROVED",
    }


def simulate_transition(current_state: str, target_state: str, gates: dict[str, Any]) -> dict[str, Any]:
    """Attempt one adjacent transition and fail closed on any skipped or missing gate."""

    if current_state not in STATES or target_state not in STATES:
        return {"transition_allowed": False, "current_state": current_state, "reason_code": "SIMULATION_STATE_UNKNOWN"}
    if current_state == "PILOT_TERMINATED":
        return {"transition_allowed": False, "current_state": current_state, "reason_code": "SIMULATION_TERMINAL_STATE_IMMUTABLE"}
    expected_index = STATES.index(current_state) + 1
    if expected_index >= len(STATES) or STATES[expected_index] != target_state:
        return {"transition_allowed": False, "current_state": current_state, "reason_code": "SIMULATION_MANDATORY_GATE_SKIP_REJECTED"}
    if target_state == "PILOT_TERMINATED":
        return {"transition_allowed": False, "current_state": current_state, "reason_code": "SIMULATION_TERMINATION_API_REQUIRED"}

    gate_id = GATE_FOR_TARGET[target_state]
    gate_result = validate_gate(gate_id, gates.get(gate_id))
    if not gate_result["gate_valid"]:
        return {"transition_allowed": False, "current_state": current_state, "reason_code": gate_result["reason_code"]}
    return {
        "transition_allowed": True,
        "current_state": target_state,
        "reason_code": "",
        "synthetic_transition": True,
        "real_authorization_granted": False,
    }


def terminate_pilot(current_state: str, reason: str) -> dict[str, Any]:
    """Terminate an active synthetic lifecycle without touching an external Pilot."""

    if current_state != "PILOT_ACTIVE":
        return {"terminated": False, "current_state": current_state, "reason_code": "SIMULATION_PILOT_NOT_ACTIVE"}
    return {
        "terminated": True,
        "current_state": "PILOT_TERMINATED",
        "stop_reason": reason,
        "external_pilot_terminated": False,
    }


def revoke_access(requested: bool) -> dict[str, Any]:
    """Model revocation; no account or credential exists."""

    return {"access_revoked": requested is True, "real_access_changed": False}


def delete_simulated_data(requested: bool) -> dict[str, Any]:
    """Model deletion of ephemeral synthetic state only."""

    return {"simulated_data_deleted": requested is True, "customer_data_deleted": False, "persistence_used": False}


def retain_artifacts(requested: bool) -> dict[str, Any]:
    """Model retention of bounded result metadata, never raw customer data."""

    return {
        "bounded_artifacts_retained": requested is True,
        "raw_customer_data_retained": False,
        "secret_values_retained": False,
        "persistence_used": False,
    }
