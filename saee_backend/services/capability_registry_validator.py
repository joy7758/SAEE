"""Offline validator for SAEE Capability Registry Specification v0.1."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_SCHEMA_PATH = ROOT / "agent-interface/registry/saee-capability-registry.schema.v0.1.json"
ALLOWED_LIFECYCLE_STATES = {
    "RESEARCH_PROTOTYPE",
    "LOCAL_PROTOTYPE",
    "EXTERNAL_VALIDATION",
    "PRODUCTION_CAPABILITY",
}
CAPABILITY_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^0\.[1-9][0-9]*$")

REGISTRY_ENTRY_INVALID = "REGISTRY_ENTRY_INVALID"
REGISTRY_CAPABILITY_ID_INVALID = "REGISTRY_CAPABILITY_ID_INVALID"
REGISTRY_VERSION_INVALID = "REGISTRY_VERSION_INVALID"
REGISTRY_LIFECYCLE_INVALID = "REGISTRY_LIFECYCLE_INVALID"
REGISTRY_CONTRACT_REQUIRED = "REGISTRY_CONTRACT_REQUIRED"
REGISTRY_LIMITATIONS_REQUIRED = "REGISTRY_LIMITATIONS_REQUIRED"
REGISTRY_ADOPTION_CLAIM_FORBIDDEN = "REGISTRY_ADOPTION_CLAIM_FORBIDDEN"
REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED = "REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED"
REGISTRY_PRODUCTION_EVIDENCE_REQUIRED = "REGISTRY_PRODUCTION_EVIDENCE_REQUIRED"
REGISTRY_PUBLIC_AVAILABILITY_OVERCLAIM = "REGISTRY_PUBLIC_AVAILABILITY_OVERCLAIM"
REGISTRY_BOUNDARY_INVALID = "REGISTRY_BOUNDARY_INVALID"
REGISTRY_SCHEMA_INVALID = "REGISTRY_SCHEMA_INVALID"
REGISTRY_REFERENCE_MISSING = "REGISTRY_REFERENCE_MISSING"
REGISTRY_CONTRACT_VERSION_MISMATCH = "REGISTRY_CONTRACT_VERSION_MISMATCH"


def _result(entry: Any, valid: bool, reason_codes: list[str], *, resolved_reference_count: int = 0) -> dict[str, Any]:
    validation = entry.get("validation_state", {}) if isinstance(entry, dict) else {}
    discovery = entry.get("discovery_endpoint", {}) if isinstance(entry, dict) else {}
    return {
        "saee_capability_registry_validation_result_v0_1": True,
        "registry_entry_valid": valid,
        "capability_id": entry.get("capability_id", "") if isinstance(entry, dict) else "",
        "version": entry.get("version", "") if isinstance(entry, dict) else "",
        "lifecycle_state": entry.get("lifecycle_state", "") if isinstance(entry, dict) else "",
        "reason_codes": reason_codes,
        "resolved_reference_count": resolved_reference_count,
        "external_validation_completed": validation.get("external_validation_completed", False) is True,
        "production_validation_completed": validation.get("production_validation_completed", False) is True,
        "adoption_validated": validation.get("adoption_validated", False) is True,
        "public_registry_available": discovery.get("public_registry_available", False) is True,
        "public_tool_available": discovery.get("public_tool_available", False) is True,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _semantic_error(entry: Any) -> str | None:
    if not isinstance(entry, dict):
        return REGISTRY_ENTRY_INVALID
    capability_id = entry.get("capability_id")
    if not isinstance(capability_id, str) or CAPABILITY_ID_PATTERN.fullmatch(capability_id) is None:
        return REGISTRY_CAPABILITY_ID_INVALID
    version = entry.get("version")
    if not isinstance(version, str) or VERSION_PATTERN.fullmatch(version) is None:
        return REGISTRY_VERSION_INVALID
    lifecycle = entry.get("lifecycle_state")
    if lifecycle not in ALLOWED_LIFECYCLE_STATES:
        return REGISTRY_LIFECYCLE_INVALID
    validation = entry.get("validation_state")
    if isinstance(validation, dict) and validation.get("adoption_validated") is not False:
        return REGISTRY_ADOPTION_CLAIM_FORBIDDEN
    limitations = entry.get("limitations")
    if not isinstance(limitations, list) or len(limitations) < 6:
        return REGISTRY_LIMITATIONS_REQUIRED
    if not isinstance(entry.get("input_contract"), dict) or not isinstance(entry.get("output_contract"), dict):
        return REGISTRY_CONTRACT_REQUIRED
    if lifecycle == "EXTERNAL_VALIDATION" and (
        not isinstance(validation, dict)
        or validation.get("external_validation_completed") is not True
        or not validation.get("validation_evidence_refs")
    ):
        return REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED
    if lifecycle == "PRODUCTION_CAPABILITY" and (
        not isinstance(validation, dict)
        or validation.get("external_validation_completed") is not True
        or validation.get("production_validation_completed") is not True
        or not validation.get("validation_evidence_refs")
    ):
        return REGISTRY_PRODUCTION_EVIDENCE_REQUIRED
    discovery = entry.get("discovery_endpoint")
    if lifecycle in {"RESEARCH_PROTOTYPE", "LOCAL_PROTOTYPE"} and (
        not isinstance(discovery, dict)
        or discovery.get("public_registry_available") is not False
        or discovery.get("public_tool_available") is not False
    ):
        return REGISTRY_PUBLIC_AVAILABILITY_OVERCLAIM
    boundary = entry.get("boundary_contract")
    if not isinstance(boundary, dict) or any(
        boundary.get(field) is not False
        for field in (
            "registry_entry_authorizes_use",
            "capability_description_is_trust",
            "availability_implies_production",
        )
    ) or boundary.get("human_authority_required") is not True:
        return REGISTRY_BOUNDARY_INVALID
    return None


def _local_refs(entry: dict[str, Any]) -> list[str]:
    return [
        entry["discovery_endpoint"]["local_manifest_ref"],
        entry["invocation"]["function_ref"],
        entry["input_contract"]["schema_ref"],
        entry["output_contract"]["schema_ref"],
        entry["boundary_contract"]["contract_ref"],
        entry["validation_state"]["benchmark_reference"],
        entry["validation_state"]["stateful_rehearsal_runtime_reference"],
        entry["validation_state"]["rehearsal_mvp_reference"],
        entry["validation_state"]["scenario_library_reference"],
        entry["validation_state"]["multi_agent_rehearsal_reference"],
        entry["validation_state"]["reliability_study_reference"],
        entry["validation_state"]["research_agent_study_reference"],
        entry["validation_state"]["security_boundary_study_reference"],
        entry["validation_state"]["reliability_framework_reference"],
        entry["validation_state"]["internal_reliability_benchmark_reference"],
        entry["validation_state"]["methodology_review_reference"],
        entry["validation_state"]["extended_internal_reliability_benchmark_reference"],
        entry["validation_state"]["reliability_research_manifest_reference"],
        entry["validation_state"]["agent_native_design_partner_validation_reference"],
        entry["validation_state"]["commercial_assessment_service_status_reference"],
        entry["validation_state"]["local_runtime_reference"],
        entry["validation_state"]["local_mcp_adapter_reference"],
        entry["validation_state"]["local_http_adapter_reference"],
        entry["validation_state"]["integration_examples_reference"],
        entry["validation_state"]["public_capability_surface_reference"],
        entry["validation_state"]["discovery_validation_reference"],
        entry["validation_state"]["alpha_release_reference"],
        entry["validation_state"]["alpha_release_position_reference"],
        entry["validation_state"]["cloud_ecosystem_strategy_reference"],
        entry["validation_state"]["ecosystem_entry_package_reference"],
        entry["validation_state"]["mcp_dry_integration_reference"],
        entry["validation_state"]["ecosystem_demo_reference"],
        entry["validation_state"]["first_validation_candidate_reference"],
        entry["validation_state"]["first_external_validation_simulation_reference"],
        entry["validation_state"]["truth_consistency_validation_reference"],
        entry["validation_state"]["ecosystem_validation_preparation_reference"],
        entry["validation_state"]["ecosystem_dry_run_reference"],
        entry["validation_state"]["external_validation_design_reference"],
        entry["validation_state"]["external_validation_simulation_reference"],
        entry["validation_state"]["external_validation_readiness_review_reference"],
        entry["validation_state"]["execution_simulation_reference"],
        entry["validation_state"]["entry_decision_reference"],
        entry["validation_state"]["entry_decision_simulation_reference"],
        entry["validation_state"]["agent_native_adoption_strategy_reference"],
        entry["validation_state"]["marketplace_position_reference"],
        entry["validation_state"]["capability_composition_reference"],
        *entry["validation_state"]["validation_evidence_refs"],
        entry["migration_state"]["migration_notes_ref"],
    ]


def _reference_exists(ref: str) -> bool:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def _contracts_match_version(entry: dict[str, Any]) -> bool:
    version = entry["version"]
    for contract_name in ("input_contract", "output_contract"):
        contract = entry[contract_name]
        if contract.get("schema_version") != version:
            return False
        ref = contract.get("schema_ref", "")
        if f"v{version}.schema.json" not in ref:
            return False
        schema_path = ROOT / ref
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        if f"v{version}.schema.json" not in schema.get("$id", ""):
            return False
    return True


def validate_capability_registry_entry(entry: Any) -> dict[str, Any]:
    """Validate one local registry entry without resolving remote resources."""

    semantic_error = _semantic_error(entry)
    if semantic_error is not None:
        return _result(entry, False, [semantic_error])

    schema = json.loads(REGISTRY_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(entry), key=lambda error: list(error.absolute_path))
    if errors:
        return _result(entry, False, [REGISTRY_SCHEMA_INVALID])

    refs = _local_refs(entry)
    if not all(_reference_exists(ref) for ref in refs):
        return _result(entry, False, [REGISTRY_REFERENCE_MISSING])
    if not _contracts_match_version(entry):
        return _result(entry, False, [REGISTRY_CONTRACT_VERSION_MISMATCH])
    return _result(entry, True, [], resolved_reference_count=len(refs))


def validate_capability_registry_json(text: str) -> dict[str, Any]:
    """Parse and validate one registry entry JSON string."""

    try:
        entry = json.loads(text)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return _result({}, False, [REGISTRY_ENTRY_INVALID])
    return validate_capability_registry_entry(entry)
