"""Cross-object, offline validation for SAEE capability registry declarations.

The validator checks internal consistency only. It does not contact a registry,
establish trust, certify a capability, or authorize deployment.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from saee_backend.services.capability_registry_validator import (
    REGISTRY_ADOPTION_CLAIM_FORBIDDEN,
    REGISTRY_BOUNDARY_INVALID,
    REGISTRY_CAPABILITY_ID_INVALID,
    REGISTRY_CONTRACT_REQUIRED,
    REGISTRY_CONTRACT_VERSION_MISMATCH,
    REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED,
    REGISTRY_LIFECYCLE_INVALID,
    REGISTRY_PRODUCTION_EVIDENCE_REQUIRED,
    REGISTRY_REFERENCE_MISSING,
    REGISTRY_SCHEMA_INVALID,
    REGISTRY_VERSION_INVALID,
    validate_capability_registry_entry,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "agent-interface/capabilities/saee-capability-manifest.v0.1.json"

REGISTRY_BOUNDARY_OVERCLAIM = "REGISTRY_BOUNDARY_OVERCLAIM"
REGISTRY_REFERENCE_CHAIN_INVALID = "REGISTRY_REFERENCE_CHAIN_INVALID"
REGISTRY_FIXTURE_INVALID = "REGISTRY_FIXTURE_INVALID"

_AFFIRMATIVE_OVERCLAIMS = (
    re.compile(r"\b(?:saee|the capability|the system)\s+(?:is|has been)\s+(?:certified|guaranteed|approved|compliant)\b", re.I),
    re.compile(r"\bdeployment\s+(?:is\s+|has been\s+)?approved\b", re.I),
    re.compile(r"\b(?:certification|approval)\s+(?:is\s+|has been\s+)?granted\b", re.I),
    re.compile(r"\bguarantees?\s+(?:security|safety|compliance)\b", re.I),
    re.compile(r"(?:SAEE|本能力|本系统|系统)(?:已经|已)(?:通过)?(?:安全|合规)?认证"),
    re.compile(r"(?:部署|上线)(?:已经|已)(?:获得)?批准"),
    re.compile(r"保证(?:安全|合规|符合监管要求)"),
)

_MUTATION_PATHS = {
    "lifecycle_state": ("lifecycle_state",),
    "input_contract.schema_version": ("input_contract", "schema_version"),
    "input_contract": ("input_contract",),
    "description.english": ("description", "english"),
    "input_contract.schema_ref": ("input_contract", "schema_ref"),
    "validation_state.adoption_validated": ("validation_state", "adoption_validated"),
}


def _truth_boundary() -> dict[str, bool]:
    return {
        "registry_service_available": False,
        "external_registry": False,
        "trust_authority": False,
        "capability_certified": False,
        "adoption_validated": False,
        "production_ready": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
    }


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    return []


def _has_boundary_overclaim(entry: dict[str, Any]) -> bool:
    surfaces = {
        "name": entry.get("name"),
        "description": entry.get("description"),
        "limitations": entry.get("limitations"),
    }
    return any(pattern.search(text) for text in _strings(surfaces) for pattern in _AFFIRMATIVE_OVERCLAIMS)


def _load_local_json(ref: str) -> dict[str, Any] | None:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _reference_chain_valid(entry: dict[str, Any]) -> tuple[bool, int]:
    manifest_ref = entry["discovery_endpoint"]["local_manifest_ref"]
    manifest = _load_local_json(manifest_ref)
    input_schema = _load_local_json(entry["input_contract"]["schema_ref"])
    output_schema = _load_local_json(entry["output_contract"]["schema_ref"])
    if manifest is None or input_schema is None or output_schema is None:
        return False, 0

    registry = manifest.get("capability_registry_specification", {})
    tool = manifest.get("local_tool_prototype", {})
    version = entry["version"]
    alias_match = manifest.get("capability_id") in entry.get("capability_aliases", [])
    versions_match = (
        manifest.get("capability_version") == version
        and registry.get("registry_specification_version") == version
        and registry.get("capability_version") == version
        and entry["input_contract"].get("schema_version") == version
        and entry["output_contract"].get("schema_version") == version
    )
    identity_match = (
        registry.get("registry_capability_id") == entry.get("capability_id")
        and registry.get("capability_card") == "agent-interface/registry/saee-capability-card.v0.1.json"
    )
    tool_refs_match = (
        tool.get("request_schema") == entry["input_contract"]["schema_ref"]
        and tool.get("output_schema") == entry["output_contract"]["schema_ref"]
    )
    schema_ids_match = (
        input_schema.get("$id") == Path(entry["input_contract"]["schema_ref"]).name
        and output_schema.get("$id") == Path(entry["output_contract"]["schema_ref"]).name
    )
    input_shape_matches = (
        set(input_schema.get("required", [])) == set(entry["input_contract"].get("required_fields", []))
        and set(entry["input_contract"].get("optional_fields", [])) <= set(input_schema.get("properties", {}))
    )
    output_shape_matches = set(entry["output_contract"].get("output_fields", [])) <= set(output_schema.get("properties", {}))
    valid = all((alias_match, versions_match, identity_match, tool_refs_match, schema_ids_match, input_shape_matches, output_shape_matches))
    return valid, 3


def _dimensions_for_base_errors(errors: list[str]) -> dict[str, bool]:
    identity_valid = not any(code in errors for code in (REGISTRY_CAPABILITY_ID_INVALID, REGISTRY_VERSION_INVALID))
    version_consistent = not any(code in errors for code in (REGISTRY_VERSION_INVALID, REGISTRY_CONTRACT_VERSION_MISMATCH))
    contract_references_valid = not any(
        code in errors for code in (REGISTRY_CONTRACT_REQUIRED, REGISTRY_REFERENCE_MISSING, REGISTRY_CONTRACT_VERSION_MISMATCH)
    )
    lifecycle_valid = not any(
        code in errors
        for code in (
            REGISTRY_LIFECYCLE_INVALID,
            REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED,
            REGISTRY_PRODUCTION_EVIDENCE_REQUIRED,
            REGISTRY_ADOPTION_CLAIM_FORBIDDEN,
        )
    )
    boundary_valid = REGISTRY_BOUNDARY_INVALID not in errors
    reference_chain_valid = contract_references_valid and REGISTRY_SCHEMA_INVALID not in errors
    return {
        "identity_valid": identity_valid,
        "version_consistent": version_consistent,
        "contract_references_valid": contract_references_valid,
        "lifecycle_valid": lifecycle_valid,
        "boundary_valid": boundary_valid,
        "reference_chain_valid": reference_chain_valid,
    }


def validate_registry_declaration(entry: Any) -> dict[str, Any]:
    """Validate one declaration and its checked-in reference chain offline."""

    base = validate_capability_registry_entry(entry)
    errors = list(base["reason_codes"])
    checked_reference_count = base["resolved_reference_count"]
    dimensions = _dimensions_for_base_errors(errors)

    if not errors and _has_boundary_overclaim(entry):
        errors.append(REGISTRY_BOUNDARY_OVERCLAIM)
        dimensions["boundary_valid"] = False
    if not errors:
        chain_valid, chain_count = _reference_chain_valid(entry)
        checked_reference_count += chain_count
        if not chain_valid:
            errors.append(REGISTRY_REFERENCE_CHAIN_INVALID)
            dimensions["reference_chain_valid"] = False

    return {
        "saee_registry_validation_result_v0_1": True,
        "validation_version": "0.1",
        "validation_status": "PASS" if not errors else "FAIL",
        "capability_id": entry.get("capability_id", "") if isinstance(entry, dict) else "",
        "capability_version": entry.get("version", "") if isinstance(entry, dict) else "",
        "lifecycle_state": entry.get("lifecycle_state", "") if isinstance(entry, dict) else "",
        **dimensions,
        "checked_reference_count": checked_reference_count,
        "errors": errors,
        "truth_boundary": _truth_boundary(),
    }


def materialize_validation_fixture(base_entry: dict[str, Any], fixture: Any) -> dict[str, Any]:
    """Apply a strictly allowlisted synthetic fixture recipe to a copied entry."""

    if not isinstance(fixture, dict) or fixture.get("synthetic") is not True:
        raise ValueError(REGISTRY_FIXTURE_INVALID)
    entry = deepcopy(base_entry)
    for mutation in fixture.get("mutations", []):
        if not isinstance(mutation, dict) or mutation.get("field") not in _MUTATION_PATHS:
            raise ValueError(REGISTRY_FIXTURE_INVALID)
        path = _MUTATION_PATHS[mutation["field"]]
        target: dict[str, Any] = entry
        for key in path[:-1]:
            if not isinstance(target.get(key), dict):
                raise ValueError(REGISTRY_FIXTURE_INVALID)
            target = target[key]
        operation = mutation.get("operation")
        if operation == "SET" and "value" in mutation:
            target[path[-1]] = deepcopy(mutation["value"])
        elif operation == "DELETE" and path[-1] in target:
            del target[path[-1]]
        else:
            raise ValueError(REGISTRY_FIXTURE_INVALID)
    return entry
