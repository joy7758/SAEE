"""Offline validator for SAEE controlled ecosystem validation preparation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "agent-interface/ecosystem/saee-ecosystem-validation-preparation.v0.1.json"
PROTOCOL_SCHEMA_PATH = ROOT / "schemas/saee-ecosystem-validation-protocol.schema.v0.1.json"
FEEDBACK_SCHEMA_PATH = ROOT / "schemas/saee-ecosystem-validation-feedback.schema.v0.1.json"
PROTOCOL_PATH = ROOT / "agent-interface/ecosystem/saee-controlled-ecosystem-validation-protocol.v0.1.json"
MATRIX_PATH = ROOT / "agent-interface/ecosystem/saee-ecosystem-compatibility-matrix.v0.1.json"
PARTICIPANT_PACKAGE = ROOT / "ecosystem/participant-package-v0.1"
PACKAGE_FILES = {"README.md", "quick-start.md", "capability-reference.json", "test-scenarios.json", "feedback-template.json", "limitations.md"}
EXPECTED_MATRIX = {
    "MCP stdio": "local_tested",
    "HTTP local": "local_tested",
    "LangGraph": "not_tested",
    "CrewAI": "not_tested",
    "OpenAI Agents": "not_tested",
    "Claude ecosystem": "not_tested",
    "Cloud marketplace": "not_tested",
}
FORBIDDEN_FEEDBACK_FIELDS = {"name", "email", "customer_data", "private_prompt", "credentials", "chain_of_thought", "raw_prompt", "personal_data"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"ECOSYSTEM_PREPARATION_JSON_INVALID:{path.name}")
    return value


def load_preparation_state() -> dict[str, Any]:
    return _load(STATE_PATH)


def _result(valid: bool, reason_codes: list[str]) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reason_codes,
        "protocol_exists": valid,
        "participant_package_exists": valid,
        "matrix_exists": valid,
        "feedback_schema_exists": valid,
        "boundary_document_exists": valid,
        "ecosystem_validation_preparation": valid,
        "external_validation": False,
        "external_agents_connected": False,
        "customer_validated": False,
        "marketplace_listed": False,
        "adoption_validated": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _safe_ref(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or ref.startswith("/") or "://" in ref or ".." in Path(ref).parts:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def validate_ecosystem_preparation(value: Any) -> dict[str, Any]:
    """Validate preparation artifacts without contacting an external participant."""

    if not isinstance(value, dict):
        return _result(False, ["ECOSYSTEM_PREPARATION_INVALID"])
    expected_keys = {
        "preparation_version", "status", "protocol_reference", "participant_package_reference",
        "compatibility_matrix_reference", "feedback_schema_reference", "evidence_boundary_reference",
        "ecosystem_dry_run_reference",
        "external_validation_design_reference",
        "external_validation_simulation_reference",
        "external_validation_readiness_review_reference",
        "participant_types", "validation_dimensions", "truth_boundary",
    }
    if set(value) != expected_keys or value.get("preparation_version") != "0.1" or value.get("status") != "PREPARATION_ONLY":
        return _result(False, ["ECOSYSTEM_PREPARATION_CONTRACT_INVALID"])
    refs = (
        value.get("protocol_reference"), value.get("participant_package_reference"),
        value.get("compatibility_matrix_reference"), value.get("feedback_schema_reference"),
        value.get("evidence_boundary_reference"), value.get("ecosystem_dry_run_reference"),
        value.get("external_validation_design_reference"),
        value.get("external_validation_simulation_reference"),
        value.get("external_validation_readiness_review_reference"),
    )
    if not all(_safe_ref(ref) for ref in refs):
        return _result(False, ["ECOSYSTEM_PREPARATION_REFERENCE_INVALID"])
    if set(value.get("participant_types", [])) != {"agent_framework", "cloud_platform", "developer", "research_group"}:
        return _result(False, ["ECOSYSTEM_PREPARATION_PARTICIPANT_TYPES_INVALID"])
    if set(value.get("validation_dimensions", [])) != {"DISCOVERY_COMPATIBILITY", "CAPABILITY_UNDERSTANDING", "INVOCATION_COMPATIBILITY", "RESULT_INTERPRETATION", "BOUNDARY_PRESERVATION"}:
        return _result(False, ["ECOSYSTEM_PREPARATION_DIMENSIONS_INVALID"])

    truth = value.get("truth_boundary", {})
    if not isinstance(truth, dict) or truth.get("ecosystem_validation_preparation") is not True:
        return _result(False, ["ECOSYSTEM_PREPARATION_BOUNDARY_INVALID"])
    false_fields = ("external_validation_completed", "external_agents_connected", "customer_validated", "market_validation", "marketplace_listed", "adoption_validated", "production_ready", "external_parties_contacted")
    if any(truth.get(field) is not False for field in false_fields) or truth.get("participants_invited") != 0:
        return _result(False, ["ECOSYSTEM_PREPARATION_EXTERNAL_STATE_FORBIDDEN"])

    if not PARTICIPANT_PACKAGE.is_dir() or {path.name for path in PARTICIPANT_PACKAGE.iterdir() if path.is_file()} != PACKAGE_FILES:
        return _result(False, ["ECOSYSTEM_PREPARATION_PACKAGE_INVALID"])
    protocol_schema = _load(PROTOCOL_SCHEMA_PATH)
    feedback_schema = _load(FEEDBACK_SCHEMA_PATH)
    protocol = _load(PROTOCOL_PATH)
    feedback = _load(PARTICIPANT_PACKAGE / "feedback-template.json")
    if list(Draft202012Validator(protocol_schema).iter_errors(protocol)):
        return _result(False, ["ECOSYSTEM_PREPARATION_PROTOCOL_INVALID"])
    if list(Draft202012Validator(feedback_schema).iter_errors(feedback)):
        return _result(False, ["ECOSYSTEM_PREPARATION_FEEDBACK_INVALID"])
    feedback_fields = set(feedback_schema.get("properties", {})) | set(feedback)
    if feedback_fields & FORBIDDEN_FEEDBACK_FIELDS:
        return _result(False, ["ECOSYSTEM_PREPARATION_SENSITIVE_FEEDBACK_FIELD"])

    matrix = _load(MATRIX_PATH)
    matrix_values = {item.get("integration"): item.get("status") for item in matrix.get("integrations", []) if isinstance(item, dict)}
    if matrix_values != EXPECTED_MATRIX or matrix.get("external_tested_count") != 0 or matrix.get("marketplace_listed") is not False or matrix.get("external_validation") is not False or matrix.get("production_ready") is not False:
        return _result(False, ["ECOSYSTEM_PREPARATION_MATRIX_OVERCLAIM"])
    if any(item.get("external_participant_connected") is not False for item in matrix.get("integrations", [])):
        return _result(False, ["ECOSYSTEM_PREPARATION_PARTICIPANT_CONNECTED"])
    return _result(True, [])


def validate_current_ecosystem_preparation() -> dict[str, Any]:
    return validate_ecosystem_preparation(load_preparation_state())
