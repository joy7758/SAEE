"""Offline validator for the SAEE Phase 12 external-validation design."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "agent-interface/ecosystem/saee-controlled-external-validation-design.v0.1.json"
PARTICIPANT_SCHEMA = ROOT / "schemas/saee-external-validation-participant.schema.v0.1.json"
SCOPE_SCHEMA = ROOT / "schemas/saee-external-validation-scope.schema.v0.1.json"
EVIDENCE_SCHEMA = ROOT / "schemas/saee-external-validation-evidence.schema.v0.1.json"
EXIT_CRITERIA = ROOT / "docs/ecosystem/SAEE_EXTERNAL_VALIDATION_EXIT_CRITERIA.md"
TERMINATION_POLICY = ROOT / "docs/ecosystem/SAEE_EXTERNAL_VALIDATION_TERMINATION_POLICY.md"
DESIGN_DOCUMENT = ROOT / "docs/ecosystem/SAEE_CONTROLLED_EXTERNAL_VALIDATION_DESIGN.md"
ALLOWED_TYPES = {"agent_framework", "developer", "research_group", "cloud_platform"}
ALLOWED_SCOPE = {"capability_discovery_test", "integration_test", "interpretation_test", "compatibility_feedback"}
FORBIDDEN_SCOPE = {"production_execution", "customer_data_access", "private_system_access", "external_side_effects"}
ALLOWED_EVIDENCE = {"test_execution_record", "compatibility_result", "structured_feedback", "version_information"}
FORBIDDEN_EVIDENCE = {"customer_success_claim", "adoption_claim", "security_certification", "production_reliability_claim", "private_logs", "private_prompts", "credentials"}
STOP_CONDITIONS = {"CREDENTIAL_EXPOSURE", "CUSTOMER_DATA_RECEIVED", "UNAUTHORIZED_EXECUTION", "FALSE_ADOPTION_CLAIM", "BOUNDARY_VIOLATION"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"EXTERNAL_VALIDATION_DESIGN_JSON_INVALID:{path.name}")
    return value


def _safe_ref(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or ref.startswith("/") or "://" in ref or ".." in Path(ref).parts:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def _result(valid: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": list(dict.fromkeys(reasons)),
        "participant_model_exists": valid,
        "scope_model_exists": valid,
        "evidence_model_exists": valid,
        "exit_criteria_exists": valid,
        "termination_policy_exists": valid,
        "external_validation_design": valid,
        "external_validation": False,
        "participants_invited": 0,
        "participants_authorized": 0,
        "customer_validated": False,
        "adoption_validated": False,
        "production_ready": False,
    }


def validate_external_validation_design(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _result(False, ["EXTERNAL_VALIDATION_DESIGN_INVALID"])
    expected_keys = {"design_version", "status", "external_validation_simulation_reference", "external_validation_readiness_review_reference", "execution_simulation_reference", "entry_decision_reference", "participant_model", "scope_model", "evidence_model", "exit_criteria", "termination_policy", "limitations", "truth_boundary"}
    if set(value) != expected_keys or value.get("design_version") != "0.1" or value.get("status") != "DESIGN_ONLY":
        return _result(False, ["EXTERNAL_VALIDATION_DESIGN_CONTRACT_INVALID"])
    reasons: list[str] = []
    if not _safe_ref(value.get("external_validation_simulation_reference")):
        reasons.append("EXTERNAL_VALIDATION_SIMULATION_REFERENCE_INVALID")
    if not _safe_ref(value.get("external_validation_readiness_review_reference")):
        reasons.append("EXTERNAL_VALIDATION_READINESS_REVIEW_REFERENCE_INVALID")
    if not _safe_ref(value.get("execution_simulation_reference")):
        reasons.append("EXTERNAL_VALIDATION_EXECUTION_SIMULATION_REFERENCE_INVALID")
    if not _safe_ref(value.get("entry_decision_reference")):
        reasons.append("EXTERNAL_VALIDATION_ENTRY_DECISION_REFERENCE_INVALID")
    participant = value.get("participant_model", {})
    if set(participant.get("allowed_types", [])) != ALLOWED_TYPES or set(participant.get("allowed_authorization_statuses", [])) != {"NOT_AUTHORIZED", "AUTHORIZED_FOR_VALIDATION"} or participant.get("participants_authorized") != 0 or not _safe_ref(participant.get("schema_reference")):
        reasons.append("EXTERNAL_VALIDATION_PARTICIPANT_MODEL_INVALID")
    scope = value.get("scope_model", {})
    if set(scope.get("allowed", [])) != ALLOWED_SCOPE or set(scope.get("forbidden", [])) != FORBIDDEN_SCOPE or not _safe_ref(scope.get("schema_reference")):
        reasons.append("EXTERNAL_VALIDATION_SCOPE_MODEL_INVALID")
    evidence = value.get("evidence_model", {})
    if set(evidence.get("allowed", [])) != ALLOWED_EVIDENCE or set(evidence.get("forbidden", [])) != FORBIDDEN_EVIDENCE or not _safe_ref(evidence.get("schema_reference")):
        reasons.append("EXTERNAL_VALIDATION_EVIDENCE_MODEL_INVALID")
    exit_criteria = value.get("exit_criteria", {})
    if not _safe_ref(exit_criteria.get("reference")) or exit_criteria.get("criteria_met") is not False or len(set(exit_criteria.get("criteria", []))) != 5:
        reasons.append("EXTERNAL_VALIDATION_EXIT_CRITERIA_INVALID")
    termination = value.get("termination_policy", {})
    if not _safe_ref(termination.get("reference")) or set(termination.get("immediate_stop_conditions", [])) != STOP_CONDITIONS:
        reasons.append("EXTERNAL_VALIDATION_TERMINATION_POLICY_INVALID")
    if not DESIGN_DOCUMENT.is_file() or not EXIT_CRITERIA.is_file() or not TERMINATION_POLICY.is_file() or len(value.get("limitations", [])) < 3:
        reasons.append("EXTERNAL_VALIDATION_DOCUMENTATION_INCOMPLETE")
    truth = value.get("truth_boundary", {})
    if not isinstance(truth, dict) or truth.get("external_validation_design") is not True:
        reasons.append("EXTERNAL_VALIDATION_DESIGN_BOUNDARY_INVALID")
    false_fields = ("external_validation", "external_agents_connected", "customer_validated", "market_validation", "adoption_validated", "production_ready", "external_parties_contacted", "customer_data_received", "external_execution")
    if any(truth.get(field) is not False for field in false_fields) or truth.get("participants_invited") != 0 or truth.get("participants_authorized") != 0:
        reasons.append("EXTERNAL_VALIDATION_DESIGN_EXTERNAL_STATE_FORBIDDEN")
    return _result(not reasons, reasons)


def validate_current_external_validation_design() -> dict[str, Any]:
    for path in (PARTICIPANT_SCHEMA, SCOPE_SCHEMA, EVIDENCE_SCHEMA):
        Draft202012Validator.check_schema(_load(path))
    return validate_external_validation_design(_load(DESIGN_PATH))
