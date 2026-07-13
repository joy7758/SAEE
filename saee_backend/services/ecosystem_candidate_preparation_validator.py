"""Offline validator for SAEE first ecosystem candidate preparation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_SCHEMA_PATH = ROOT / "schemas/saee-ecosystem-validation-candidate.schema.v0.1.json"
SCOPE_SCHEMA_PATH = ROOT / "schemas/saee-first-ecosystem-validation-scope.schema.v0.1.json"
FEEDBACK_SCHEMA_PATH = ROOT / "schemas/saee-ecosystem-validation-feedback.schema.v0.1.json"
MATRIX_PATH = ROOT / "agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json"
SUCCESS_PATH = ROOT / "agent-interface/ecosystem/saee-first-validation-success-criteria.v0.1.json"
PACKAGE_ROOT = ROOT / "ecosystem/first-validation-candidate-package-v1"
PACKAGE_FILES = {"README.md", "candidate-profile.md", "validation-plan.md", "success-criteria.md", "feedback-template.json", "limitations.md"}
EXPECTED_PRIORITY = {
    "mcp_agent_developer": "P0",
    "agent_framework_developer": "P1",
    "cloud_platform": "P2",
}
EXPECTED_ALLOWED = {"capability_discovery", "mcp_tool_discovery", "local_invocation", "result_interpretation", "documentation_feedback"}
EXPECTED_FORBIDDEN = {"production_execution", "customer_data", "private_system_access", "external_side_effects"}
EXPECTED_TECHNICAL = {"capability_discovered", "tool_invocation_works", "result_interpreted_correctly"}
EXPECTED_DOCUMENTATION = {"purpose_understood", "limitations_understood"}
EXPECTED_EXCLUDED = {"adoption", "revenue", "market_success", "partnership", "production_approval"}
FORBIDDEN_KEYS = {
    "real_participant",
    "participant_identity",
    "company_name",
    "person_name",
    "contact_completed",
    "participant_contacted",
    "external_validation_completed",
    "adoption_claim",
    "customer_data",
    "private_prompt",
    "credentials",
    "chain_of_thought",
    "business_confidential_data",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _result(valid: bool, reasons: list[str], candidate_count: int = 0) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reasons,
        "candidate_model": valid,
        "candidate_type_count": candidate_count,
        "scope_defined": valid,
        "success_defined": valid,
        "feedback_defined": valid,
        "boundary_defined": valid,
        "candidate_preparation": True,
        "candidate_selected": False,
        "external_validation": False,
        "participant_contact": False,
        "customer_validated": False,
        "adoption_validated": False,
        "production_ready": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
    }


def _has_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in FORBIDDEN_KEYS or _has_forbidden_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_has_forbidden_key(child) for child in value)
    return False


def validate_preparation_data(matrix: Any, success: Any, feedback: Any) -> dict[str, Any]:
    """Validate candidate categories and contracts without external activity."""

    if not all(isinstance(value, dict) for value in (matrix, success, feedback)):
        return _result(False, ["CANDIDATE_PREPARATION_DATA_INVALID"])
    if _has_forbidden_key({"matrix": matrix, "success": success, "feedback": feedback}):
        return _result(False, ["CANDIDATE_PREPARATION_FORBIDDEN_FIELD"])
    simulation_ref = matrix.get("first_external_validation_simulation_reference")
    if simulation_ref != "agent-interface/ecosystem/saee-first-external-validation-simulation-result.v0.1.json" or not (ROOT / simulation_ref).is_file():
        return _result(False, ["CANDIDATE_PREPARATION_SIMULATION_REFERENCE_INVALID"])
    gate_ref = matrix.get("real_validation_entry_gate_reference")
    if gate_ref != "agent-interface/ecosystem/saee-real-ecosystem-validation-entry-decision.v0.1.json" or not (ROOT / gate_ref).is_file():
        return _result(False, ["CANDIDATE_PREPARATION_REAL_GATE_REFERENCE_INVALID"])
    candidates = matrix.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        return _result(False, ["CANDIDATE_PREPARATION_CANDIDATE_COUNT_INVALID"])
    candidate_schema = _load(CANDIDATE_SCHEMA_PATH)
    candidate_validator = Draft202012Validator(candidate_schema)
    candidate_types: set[str] = set()
    for entry in candidates:
        if not isinstance(entry, dict) or list(candidate_validator.iter_errors(entry.get("candidate"))) or entry.get("priority") not in {"P0", "P1", "P2"}:
            return _result(False, ["CANDIDATE_PREPARATION_CANDIDATE_INVALID"])
        candidate_type = entry["candidate"]["candidate_type"]
        candidate_types.add(candidate_type)
        if entry["priority"] != EXPECTED_PRIORITY.get(candidate_type):
            return _result(False, ["CANDIDATE_PREPARATION_PRIORITY_INVALID"])
    if candidate_types != set(EXPECTED_PRIORITY):
        return _result(False, ["CANDIDATE_PREPARATION_CANDIDATE_SET_INVALID"], len(candidate_types))

    scope = matrix.get("validation_scope_model")
    if list(Draft202012Validator(_load(SCOPE_SCHEMA_PATH)).iter_errors(scope)):
        return _result(False, ["CANDIDATE_PREPARATION_SCOPE_INVALID"], len(candidate_types))
    if set(scope["allowed"]) != EXPECTED_ALLOWED or set(scope["forbidden"]) != EXPECTED_FORBIDDEN:
        return _result(False, ["CANDIDATE_PREPARATION_SCOPE_INVALID"], len(candidate_types))

    truth = matrix.get("truth_boundary")
    if not isinstance(truth, dict) or truth.get("candidate_preparation") is not True or any(
        truth.get(key) is not False for key in (
            "candidate_selected", "real_participant_identified", "participant_contact",
            "external_validation", "customer_validated", "adoption_validated", "production_ready",
        )
    ):
        return _result(False, ["CANDIDATE_PREPARATION_BOUNDARY_INVALID"], len(candidate_types))

    if success.get("candidate_category") != "mcp_agent_developer":
        return _result(False, ["CANDIDATE_PREPARATION_SUCCESS_INVALID"], len(candidate_types))
    technical = success.get("technical_success")
    documentation = success.get("documentation_success")
    if not isinstance(technical, list) or {item.get("criterion") for item in technical if isinstance(item, dict)} != EXPECTED_TECHNICAL:
        return _result(False, ["CANDIDATE_PREPARATION_SUCCESS_INVALID"], len(candidate_types))
    if not isinstance(documentation, list) or {item.get("criterion") for item in documentation if isinstance(item, dict)} != EXPECTED_DOCUMENTATION:
        return _result(False, ["CANDIDATE_PREPARATION_SUCCESS_INVALID"], len(candidate_types))
    if any(item.get("required") is not True for item in technical + documentation) or set(success.get("excluded_outcomes", [])) != EXPECTED_EXCLUDED:
        return _result(False, ["CANDIDATE_PREPARATION_SUCCESS_INVALID"], len(candidate_types))
    success_truth = success.get("truth_boundary")
    if not isinstance(success_truth, dict) or success_truth.get("success_criteria_defined") is not True or any(
        success_truth.get(key) is not False for key in ("success_observed", "feedback_collected", "external_validation", "adoption_validated", "production_ready")
    ):
        return _result(False, ["CANDIDATE_PREPARATION_SUCCESS_BOUNDARY_INVALID"], len(candidate_types))

    feedback_errors = list(Draft202012Validator(_load(FEEDBACK_SCHEMA_PATH)).iter_errors(feedback))
    if feedback_errors or any(value != "NOT_COLLECTED" for value in feedback.values()):
        return _result(False, ["CANDIDATE_PREPARATION_FEEDBACK_INVALID"], len(candidate_types))
    return _result(True, [], len(candidate_types))


def validate_candidate_preparation() -> dict[str, Any]:
    for schema_path in (CANDIDATE_SCHEMA_PATH, SCOPE_SCHEMA_PATH, FEEDBACK_SCHEMA_PATH):
        if not schema_path.is_file():
            return _result(False, ["CANDIDATE_PREPARATION_SCHEMA_MISSING"])
        try:
            Draft202012Validator.check_schema(_load(schema_path))
        except Exception:
            return _result(False, ["CANDIDATE_PREPARATION_SCHEMA_INVALID"])
    if not MATRIX_PATH.is_file() or not SUCCESS_PATH.is_file() or not PACKAGE_ROOT.is_dir():
        return _result(False, ["CANDIDATE_PREPARATION_PACKAGE_INCOMPLETE"])
    if any(not (PACKAGE_ROOT / name).is_file() for name in PACKAGE_FILES):
        return _result(False, ["CANDIDATE_PREPARATION_PACKAGE_INCOMPLETE"])
    try:
        matrix = _load(MATRIX_PATH)
        success = _load(SUCCESS_PATH)
        feedback = _load(PACKAGE_ROOT / "feedback-template.json")
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _result(False, ["CANDIDATE_PREPARATION_JSON_INVALID"])
    return validate_preparation_data(matrix, success, feedback)
