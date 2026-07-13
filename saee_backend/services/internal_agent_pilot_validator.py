"""Offline validator for SAEE Internal Agent Pilot Plan v1.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .internal_agent_pilot import ALLOWED_RECOMMENDATIONS, FLOW, assemble_internal_pilot_evidence, prepare_internal_pilot


ROOT = Path(__file__).resolve().parents[2]
PILOT_SCHEMA_PATH = ROOT / "schemas/saee-internal-agent-pilot.schema.v0.1.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/saee-internal-pilot-evidence.schema.v0.1.json"
PLAN_PATH = ROOT / "agent-interface/pilot/saee-internal-agent-pilot-plan.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/pilot/internal-agent-pilot-scenarios"
EXPECTED_SCENARIOS = {
    "CODE_CHANGE_WORKFLOW.json": "coding_agent",
    "RESEARCH_WORKFLOW.json": "research_agent",
    "AUTOMATION_WORKFLOW.json": "automation_agent",
    "AGENT_DELEGATION_WORKFLOW.json": "evaluation_agent",
}
EXPECTED_FORBIDDEN_ACTIONS = {"customer_data", "production_system", "external_side_effect", "permission_expansion", "untrusted_code_execution"}
FORBIDDEN_CLAIM_KEYS = {
    "external_validation_claim", "customer_claim", "adoption_claim", "production_claim",
    "customer_validated", "adoption_validated", "production_ready", "deployment_authorized",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _contains_overclaim(value: Any) -> bool:
    if isinstance(value, dict):
        return any((key in FORBIDDEN_CLAIM_KEYS and child is True) or _contains_overclaim(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_overclaim(child) for child in value)
    return False


def validate_internal_pilot_scenario(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_SCENARIO_INVALID"]}
    errors = list(Draft202012Validator(_load(PILOT_SCHEMA_PATH)).iter_errors(value))
    if errors:
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_SCHEMA_INVALID"]}
    if _contains_overclaim(value):
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_CLAIM_FORBIDDEN"]}
    if set(value["workflow_scope"]["forbidden"]) != EXPECTED_FORBIDDEN_ACTIONS:
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_SCOPE_BOUNDARY_INVALID"]}
    plan = prepare_internal_pilot(value)
    if plan["status"] != "PLANNED_NOT_EXECUTED" or plan["pilot_executed"] is not False:
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_EXECUTION_BOUNDARY_INVALID"]}
    return {
        "valid": True, "reason_codes": [], "internal_only": True, "scope_defined": True,
        "evidence_boundary": True, "recommendation_boundary": True, "pilot_executed": False,
        "external_validation": False, "customer_data": False, "production_execution": False,
        "adoption_validated": False, "production_ready": False,
    }


def validate_internal_pilot_evidence(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or list(Draft202012Validator(_load(EVIDENCE_SCHEMA_PATH)).iter_errors(value)):
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_EVIDENCE_INVALID"]}
    if _contains_overclaim(value):
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_CLAIM_FORBIDDEN"]}
    return {"valid": True, "reason_codes": []}


def validate_internal_pilot_repository() -> dict[str, Any]:
    for path in (PILOT_SCHEMA_PATH, EVIDENCE_SCHEMA_PATH):
        Draft202012Validator.check_schema(_load(path))
    plan = _load(PLAN_PATH)
    files = {path.name for path in SCENARIO_DIR.glob("*.json")}
    if files != set(EXPECTED_SCENARIOS):
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_SCENARIO_SET_INVALID"]}
    expected_refs = {f"agent-interface/pilot/internal-agent-pilot-scenarios/{name}" for name in EXPECTED_SCENARIOS}
    founder_ref = plan.get("existing_internal_founder_record_reference", "")
    execution_ref = plan.get("internal_agent_pilot_execution_reference", "")
    if (
        set(plan.get("scenario_refs", [])) != expected_refs
        or plan.get("execution_flow") != FLOW
        or set(plan.get("recommendations", [])) != ALLOWED_RECOMMENDATIONS
        or plan.get("truth_boundary", {}).get("pilot_executed") is not True
        or plan.get("truth_boundary", {}).get("real_internal_execution") is not True
        or not isinstance(founder_ref, str)
        or not (ROOT / founder_ref).is_file()
        or not isinstance(execution_ref, str)
        or not (ROOT / execution_ref).is_file()
        or _contains_overclaim(plan)
    ):
        return {"valid": False, "reason_codes": ["INTERNAL_PILOT_PLAN_INVALID"]}
    scenarios = [_load(SCENARIO_DIR / name) for name in sorted(EXPECTED_SCENARIOS)]
    for name, scenario in zip(sorted(EXPECTED_SCENARIOS), scenarios):
        if scenario.get("agent_type") != EXPECTED_SCENARIOS[name] or not validate_internal_pilot_scenario(scenario)["valid"]:
            return {"valid": False, "reason_codes": ["INTERNAL_PILOT_SCENARIO_INVALID"]}
    agent_types = {item["agent_type"] for item in scenarios}
    return {
        "valid": True, "reason_codes": [], "scenario_count": len(scenarios),
        "agent_type_count": len(agent_types), "internal_only": True, "scope_defined": True,
        "evidence_boundary": True, "recommendation_boundary": True, "pilot_executed": True,
        "real_internal_execution": True,
        "external_validation": False, "external_participants": False, "customer_data": False,
        "production_execution": False, "adoption_validated": False, "production_ready": False,
    }


def synthetic_evidence_for_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Build an in-memory NOT_EXECUTED record used only by the offline smoke."""

    return assemble_internal_pilot_evidence(scenario, {
        "execution_observation": {"status": "NOT_EXECUTED", "observation_refs": []},
        "reliability_result": {"status": "NOT_ASSESSED", "reason_codes": ["PILOT_EXECUTION_PENDING"]},
        "evidence_result": {"status": "NOT_ASSESSED", "missing_requirements": ["internal_pilot_execution_record"]},
        "recommendation": "HUMAN_REVIEW_REQUIRED",
    })
