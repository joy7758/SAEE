"""Strict offline validator for SAEE Phase 11.1 dry-run records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-ecosystem-dry-run-result.v0.1.json"
PARTICIPANT_SCHEMA = ROOT / "schemas/saee-synthetic-ecosystem-participant.schema.v0.1.json"
FEEDBACK_SCHEMA = ROOT / "schemas/saee-ecosystem-dry-run-feedback.schema.v0.1.json"
PARTICIPANTS = ROOT / "agent-interface/ecosystem/dry-run-participants"
FORBIDDEN_FIELDS = {"credentials", "private_prompts", "private_prompt", "customer_data", "chain_of_thought", "real_company", "real_customer", "real_contact", "external_identity"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def validate_ecosystem_dry_run(value: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not isinstance(value, dict):
        return {"valid": False, "reason_codes": ["ECOSYSTEM_DRY_RUN_INVALID"]}
    required = {"dry_run_version", "status", "synthetic_only", "participants", "scenario_results", "feedback_records", "limitations", "evidence_boundary", "truth_boundary"}
    if set(value) != required or value.get("dry_run_version") != "0.1" or value.get("status") != "PASS" or value.get("synthetic_only") is not True:
        reasons.append("ECOSYSTEM_DRY_RUN_CONTRACT_INVALID")
    if len(value.get("participants", [])) < 3 or len(set(value.get("participants", []))) < 3:
        reasons.append("ECOSYSTEM_DRY_RUN_PARTICIPANTS_INCOMPLETE")
    scenarios = value.get("scenario_results", [])
    if len(scenarios) < 5 or not all(isinstance(item, dict) and item.get("matched_expected") is True for item in scenarios):
        reasons.append("ECOSYSTEM_DRY_RUN_WORKFLOW_INCOMPLETE")
    feedback = value.get("feedback_records", [])
    feedback_schema = _load(FEEDBACK_SCHEMA)
    if len(feedback) < 3 or any(list(Draft202012Validator(feedback_schema).iter_errors(item)) for item in feedback):
        reasons.append("ECOSYSTEM_DRY_RUN_FEEDBACK_INVALID")
    serialized = json.dumps(value, ensure_ascii=False).lower()
    if any(f'"{field}"' in serialized for field in FORBIDDEN_FIELDS):
        reasons.append("ECOSYSTEM_DRY_RUN_SENSITIVE_FIELD_FORBIDDEN")
    truth = value.get("truth_boundary", {})
    if not isinstance(truth, dict) or truth.get("ecosystem_dry_run") is not True or truth.get("synthetic_participants_only") is not True:
        reasons.append("ECOSYSTEM_DRY_RUN_BOUNDARY_INVALID")
    false_fields = ("external_validation", "external_agents_connected", "customer_validated", "market_validation", "marketplace_listed", "adoption_validated", "production_ready", "external_parties_contacted", "network_accessed", "subprocess_started", "external_execution")
    if any(truth.get(field) is not False for field in false_fields) or truth.get("participants_invited") != 0:
        reasons.append("ECOSYSTEM_DRY_RUN_EXTERNAL_STATE_FORBIDDEN")
    boundary = value.get("evidence_boundary", {})
    if set(boundary) != {"supported_is_approved", "local_tested_is_external_compatible", "dry_run_is_adoption"} or any(boundary.values()):
        reasons.append("ECOSYSTEM_DRY_RUN_EVIDENCE_OVERCLAIM")
    return {"valid": not reasons, "reason_codes": list(dict.fromkeys(reasons)), "participant_schema": not reasons, "workflow_complete": not reasons, "feedback_valid": not reasons, "boundary_preserved": not reasons}


def validate_current_ecosystem_dry_run() -> dict[str, Any]:
    participant_schema = _load(PARTICIPANT_SCHEMA)
    for path in PARTICIPANTS.glob("*.json"):
        if list(Draft202012Validator(participant_schema).iter_errors(_load(path))):
            return {"valid": False, "reason_codes": ["ECOSYSTEM_DRY_RUN_PARTICIPANT_INVALID"]}
    return validate_ecosystem_dry_run(_load(RESULT_PATH))

