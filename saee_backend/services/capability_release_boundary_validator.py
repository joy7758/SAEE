"""Offline validator for the SAEE Capability Alpha release boundary v0.1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/saee-capability-release-boundary.schema.v0.1.json"
FALSE_BOUNDARY_FIELDS = (
    "public_release",
    "public_api",
    "public_service",
    "marketplace_listed",
    "external_adoption",
    "customer_validated",
    "production_ready",
    "certified",
    "approved",
    "trusted_by_all_agents",
)


def _result(valid: bool, reason_codes: list[str], value: Any = None) -> dict[str, Any]:
    truth = value.get("truth_boundary", {}) if isinstance(value, dict) else {}
    return {
        "valid": valid,
        "reason_codes": reason_codes,
        "release_id": value.get("release_id", "") if isinstance(value, dict) else "",
        "version": value.get("version", "") if isinstance(value, dict) else "",
        "release_status": value.get("release_status", "") if isinstance(value, dict) else "",
        "alpha_preparation": truth.get("alpha_preparation", False) is True,
        "public_release": False,
        "public_api": False,
        "public_service": False,
        "marketplace_listed": False,
        "customer_validated": False,
        "production_ready": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
    }


def validate_release_boundary(value: Any) -> dict[str, Any]:
    """Validate a release boundary without accessing external resources."""

    if not isinstance(value, dict):
        return _result(False, ["ALPHA_RELEASE_BOUNDARY_INVALID"], value)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        return _result(False, ["ALPHA_RELEASE_BOUNDARY_SCHEMA_INVALID"], value)
    requirements = value["requirements"]
    if any(requirements[field] is not True for field in ("limitations_present", "version_present", "capability_identity_present")):
        return _result(False, ["ALPHA_RELEASE_REQUIREMENT_MISSING"], value)
    truth = value["truth_boundary"]
    if truth["alpha_preparation"] is not True or any(truth[field] is not False for field in FALSE_BOUNDARY_FIELDS):
        return _result(False, ["ALPHA_RELEASE_BOUNDARY_OVERCLAIM"], value)
    return _result(True, [], value)
