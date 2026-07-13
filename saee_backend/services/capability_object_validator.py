"""Offline validator for SAEE Agent Capability Object Specification v0.1."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/registry/saee-capability-object.schema.v0.1.json"
OBJECT_ID_PATTERN = re.compile(r"^saee:capability:[a-z][a-z0-9-]*:0\.[1-9][0-9]*$")
MARKETING_OR_TRUST_PATTERN = re.compile(r"\b(?:best|guaranteed|secure|certified|approved|compliant)\b", re.I)

CAPABILITY_OBJECT_INVALID = "CAPABILITY_OBJECT_INVALID"
CAPABILITY_OBJECT_IDENTITY_REQUIRED = "CAPABILITY_OBJECT_IDENTITY_REQUIRED"
CAPABILITY_OBJECT_IDENTITY_INVALID = "CAPABILITY_OBJECT_IDENTITY_INVALID"
CAPABILITY_OBJECT_SCHEMA_INVALID = "CAPABILITY_OBJECT_SCHEMA_INVALID"
CAPABILITY_OBJECT_LIFECYCLE_EVIDENCE_REQUIRED = "CAPABILITY_OBJECT_LIFECYCLE_EVIDENCE_REQUIRED"
CAPABILITY_OBJECT_PROVENANCE_REQUIRED = "CAPABILITY_OBJECT_PROVENANCE_REQUIRED"
CAPABILITY_OBJECT_CONTRACTS_REQUIRED = "CAPABILITY_OBJECT_CONTRACTS_REQUIRED"
CAPABILITY_OBJECT_REFERENCE_MISSING = "CAPABILITY_OBJECT_REFERENCE_MISSING"
CAPABILITY_OBJECT_CONTRACT_VERSION_MISMATCH = "CAPABILITY_OBJECT_CONTRACT_VERSION_MISMATCH"
CAPABILITY_OBJECT_BOUNDARY_INVALID = "CAPABILITY_OBJECT_BOUNDARY_INVALID"
CAPABILITY_OBJECT_METADATA_OVERCLAIM = "CAPABILITY_OBJECT_METADATA_OVERCLAIM"


def _result(value: Any, valid: bool, reason_codes: list[str], resolved_reference_count: int = 0) -> dict[str, Any]:
    identity = value.get("identity", {}) if isinstance(value, dict) else {}
    lifecycle = value.get("lifecycle", {}) if isinstance(value, dict) else {}
    if not isinstance(identity, dict):
        identity = {}
    if not isinstance(lifecycle, dict):
        lifecycle = {}
    return {
        "saee_capability_object_validation_result_v0_1": True,
        "object_valid": valid,
        "object_id": value.get("object_id", "") if isinstance(value, dict) else "",
        "capability_id": identity.get("capability_id", ""),
        "version": identity.get("version", ""),
        "lifecycle_state": lifecycle.get("state", ""),
        "reason_codes": reason_codes,
        "resolved_reference_count": resolved_reference_count,
        "fdo_compliance_claimed": False,
        "external_trust_established": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "mcp_available": False,
        "api_available": False,
        "production_ready": False,
    }


def _expected_object_id(identity: dict[str, Any]) -> str | None:
    capability_id = identity.get("capability_id")
    version = identity.get("version")
    if not isinstance(capability_id, str) or not capability_id.startswith("saee.") or not isinstance(version, str):
        return None
    return f"saee:capability:{capability_id.removeprefix('saee.')}:{version}"


def _metadata_strings(metadata: Any) -> list[str]:
    if isinstance(metadata, str):
        return [metadata]
    if isinstance(metadata, list):
        return [text for value in metadata for text in _metadata_strings(value)]
    if isinstance(metadata, dict):
        return [text for value in metadata.values() for text in _metadata_strings(value)]
    return []


def _local_refs(value: dict[str, Any]) -> list[str]:
    return [
        *value["lifecycle"]["state_evidence_refs"],
        *(record["evidence_ref"] for record in value["provenance"]["change_history"]),
        value["discovery"]["registry_reference"],
        value["discovery"]["capability_card_ref"],
        value["discovery"]["recommendation_reference"],
        value["discovery"]["benchmark_reference"],
        value["discovery"]["stateful_rehearsal_runtime_reference"],
        value["discovery"]["rehearsal_mvp_reference"],
        value["discovery"]["scenario_library_reference"],
        value["discovery"]["multi_agent_rehearsal_reference"],
        value["discovery"]["reliability_study_reference"],
        value["discovery"]["research_agent_study_reference"],
        value["discovery"]["security_boundary_study_reference"],
        value["discovery"]["reliability_framework_reference"],
        value["discovery"]["internal_reliability_benchmark_reference"],
        value["discovery"]["methodology_review_reference"],
        value["discovery"]["extended_internal_reliability_benchmark_reference"],
        value["discovery"]["reliability_research_manifest_reference"],
        value["discovery"]["agent_native_design_partner_validation_reference"],
        value["discovery"]["commercial_assessment_service_status_reference"],
        value["discovery"]["local_runtime_reference"],
        value["discovery"]["local_mcp_adapter_reference"],
        value["discovery"]["local_http_adapter_reference"],
        value["discovery"]["integration_examples_reference"],
        value["discovery"]["public_capability_surface_reference"],
        value["discovery"]["discovery_validation_reference"],
        value["discovery"]["alpha_release_reference"],
        value["discovery"]["alpha_release_position_reference"],
        value["discovery"]["cloud_ecosystem_strategy_reference"],
        value["discovery"]["ecosystem_entry_package_reference"],
        value["discovery"]["mcp_dry_integration_reference"],
        value["discovery"]["ecosystem_demo_reference"],
        value["discovery"]["first_validation_candidate_reference"],
        value["discovery"]["first_external_validation_simulation_reference"],
        value["discovery"]["real_validation_entry_gate_reference"],
        value["discovery"]["internal_agent_pilot_reference"],
        value["discovery"]["internal_agent_pilot_execution_reference"],
        value["discovery"]["truth_consistency_validation_reference"],
        value["discovery"]["ecosystem_validation_preparation_reference"],
        value["discovery"]["ecosystem_dry_run_reference"],
        value["discovery"]["external_validation_design_reference"],
        value["discovery"]["external_validation_simulation_reference"],
        value["discovery"]["external_validation_readiness_review_reference"],
        value["discovery"]["execution_simulation_reference"],
        value["discovery"]["entry_decision_reference"],
        value["discovery"]["entry_decision_simulation_reference"],
        value["discovery"]["agent_native_adoption_strategy_reference"],
        value["discovery"]["marketplace_position_reference"],
        value["discovery"]["capability_composition_reference"],
        value["discovery"]["research_report_reference"],
        value["contracts"]["input"]["schema_ref"],
        value["contracts"]["output"]["schema_ref"],
    ]


def _reference_exists(ref: str) -> bool:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def _contract_versions_match(value: dict[str, Any]) -> bool:
    version = value["identity"]["version"]
    if value["contracts"]["contract_version"] != version:
        return False
    for side in ("input", "output"):
        contract = value["contracts"][side]
        if contract["schema_version"] != version or f"v{version}.schema.json" not in contract["schema_ref"]:
            return False
        try:
            schema = json.loads((ROOT / contract["schema_ref"]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        if schema.get("$id") != Path(contract["schema_ref"]).name:
            return False
    return True


def validate_capability_object(value: Any) -> dict[str, Any]:
    """Validate one checked-in capability object without network resolution."""

    if not isinstance(value, dict):
        return _result(value, False, [CAPABILITY_OBJECT_INVALID])
    identity = value.get("identity")
    if not isinstance(identity, dict):
        return _result(value, False, [CAPABILITY_OBJECT_IDENTITY_REQUIRED])
    expected_id = _expected_object_id(identity)
    if (
        expected_id is None
        or value.get("object_id") != expected_id
        or identity.get("object_id") != expected_id
        or OBJECT_ID_PATTERN.fullmatch(expected_id) is None
    ):
        return _result(value, False, [CAPABILITY_OBJECT_IDENTITY_INVALID])

    lifecycle = value.get("lifecycle")
    if isinstance(lifecycle, dict) and lifecycle.get("state") in {"EXTERNAL_VALIDATION", "PRODUCTION_CAPABILITY"}:
        external_ready = lifecycle.get("external_validation_completed") is True
        production_ready = lifecycle.get("production_validation_completed") is True
        if not external_ready or (lifecycle.get("state") == "PRODUCTION_CAPABILITY" and not production_ready):
            return _result(value, False, [CAPABILITY_OBJECT_LIFECYCLE_EVIDENCE_REQUIRED])
    if not isinstance(value.get("provenance"), dict):
        return _result(value, False, [CAPABILITY_OBJECT_PROVENANCE_REQUIRED])
    if not isinstance(value.get("contracts"), dict):
        return _result(value, False, [CAPABILITY_OBJECT_CONTRACTS_REQUIRED])

    boundaries = value.get("boundaries")
    if not isinstance(boundaries, dict) or any(
        boundaries.get(field) is not False
        for field in (
            "metadata_is_verification",
            "discovery_authorizes_use",
            "capability_evaluation_is_autonomous_decision",
            "fdo_compliance_claimed",
        )
    ) or boundaries.get("human_authority_required") is not True:
        return _result(value, False, [CAPABILITY_OBJECT_BOUNDARY_INVALID])
    if any(MARKETING_OR_TRUST_PATTERN.search(text) for text in _metadata_strings(value.get("metadata"))):
        return _result(value, False, [CAPABILITY_OBJECT_METADATA_OVERCLAIM])

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        return _result(value, False, [CAPABILITY_OBJECT_SCHEMA_INVALID])

    refs = _local_refs(value)
    if not all(_reference_exists(ref) for ref in refs):
        return _result(value, False, [CAPABILITY_OBJECT_REFERENCE_MISSING])
    if not _contract_versions_match(value):
        return _result(value, False, [CAPABILITY_OBJECT_CONTRACT_VERSION_MISMATCH])
    return _result(value, True, [], resolved_reference_count=len(refs))


def validate_capability_object_json(text: str) -> dict[str, Any]:
    """Parse and validate one capability object JSON document."""

    try:
        value = json.loads(text)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return _result({}, False, [CAPABILITY_OBJECT_INVALID])
    return validate_capability_object(value)
