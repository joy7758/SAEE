"""Internal-only SAEE Agent Pilot planning and evidence assembly.

This module does not execute an agent. It prepares a fixed flow and assembles
explicitly supplied internal observations into a bounded pilot evidence object.
"""

from __future__ import annotations

from typing import Any


ALLOWED_RECOMMENDATIONS = {"CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"}
FLOW = [
    "AGENT_TASK", "SCENARIO_DEFINITION", "SAEE_REHEARSAL", "OBSERVATION",
    "RELIABILITY_EVALUATION", "EVIDENCE_EVALUATION", "RECOMMENDATION",
]


def prepare_internal_pilot(scenario: dict[str, Any]) -> dict[str, Any]:
    """Return a non-executing plan projection for one checked-in scenario."""

    return {
        "pilot_id": scenario.get("pilot_id", ""),
        "scenario_id": scenario.get("scenario", {}).get("scenario_id", ""),
        "agent_type": scenario.get("agent_type", ""),
        "execution_flow": list(FLOW),
        "status": "PLANNED_NOT_EXECUTED",
        "internal_only": True,
        "pilot_executed": False,
        "external_validation": False,
        "external_participants": False,
        "customer_data": False,
        "production_execution": False,
        "adoption_validated": False,
        "production_ready": False,
    }


def assemble_internal_pilot_evidence(scenario: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Bind supplied observations to an internal evidence object without running work."""

    recommendation = record.get("recommendation")
    if recommendation not in ALLOWED_RECOMMENDATIONS:
        recommendation = "STOP"
    return {
        "evidence_version": "0.1",
        "pilot_id": scenario.get("pilot_id", ""),
        "execution_observation": record.get("execution_observation", {"status": "NOT_EXECUTED", "observation_refs": []}),
        "reliability_result": record.get("reliability_result", {"status": "NOT_ASSESSED", "reason_codes": []}),
        "evidence_result": record.get("evidence_result", {"status": "NOT_ASSESSED", "missing_requirements": []}),
        "recommendation": recommendation,
        "limitations": [
            "This evidence is internal-only and does not establish external validation.",
            "The recommendation supplies decision context and does not authorize deployment or another external action.",
        ],
        "truth_boundary": {
            "internal_only": True,
            "external_validation_claim": False,
            "customer_claim": False,
            "adoption_claim": False,
            "production_claim": False,
            "deployment_authorized": False,
        },
    }
