#!/usr/bin/env python3
"""Offline smoke test for SAEE Agent Capability Object v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.capability_object_validator import (  # noqa: E402
    CAPABILITY_OBJECT_BOUNDARY_INVALID,
    CAPABILITY_OBJECT_CONTRACTS_REQUIRED,
    CAPABILITY_OBJECT_IDENTITY_INVALID,
    CAPABILITY_OBJECT_IDENTITY_REQUIRED,
    CAPABILITY_OBJECT_LIFECYCLE_EVIDENCE_REQUIRED,
    CAPABILITY_OBJECT_PROVENANCE_REQUIRED,
    CAPABILITY_OBJECT_REFERENCE_MISSING,
    validate_capability_object,
)


SCHEMA_PATH = ROOT / "agent-interface/registry/saee-capability-object.schema.v0.1.json"
OBJECT_PATH = ROOT / "agent-interface/registry/objects/saee-evidence-adequacy-capability-object.v0.1.json"
SERVICE_PATH = ROOT / "saee_backend/services/capability_object_validator.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(value: dict, reason: str) -> None:
    result = validate_capability_object(value)
    assert result["object_valid"] is False, reason
    assert result["reason_codes"] == [reason], result


def _assert_no_forbidden_runtime_imports() -> None:
    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    forbidden = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & forbidden), f"forbidden runtime import: {sorted(imported & forbidden)}"


def main() -> int:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    value = _load(OBJECT_PATH)
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    assert not schema_errors, schema_errors[0].message if schema_errors else ""

    valid_result = validate_capability_object(value)
    assert valid_result["object_valid"] is True
    assert valid_result["reason_codes"] == []
    assert valid_result["resolved_reference_count"] == 54

    missing_identity = copy.deepcopy(value)
    del missing_identity["identity"]
    _expect_invalid(missing_identity, CAPABILITY_OBJECT_IDENTITY_REQUIRED)

    malformed_identity = copy.deepcopy(value)
    malformed_identity["identity"] = "not-an-identity-object"
    _expect_invalid(malformed_identity, CAPABILITY_OBJECT_IDENTITY_REQUIRED)

    invalid_object_id = copy.deepcopy(value)
    invalid_object_id["object_id"] = "saee:capability:other:0.1"
    _expect_invalid(invalid_object_id, CAPABILITY_OBJECT_IDENTITY_INVALID)

    fake_production = copy.deepcopy(value)
    fake_production["lifecycle"]["state"] = "PRODUCTION_CAPABILITY"
    _expect_invalid(fake_production, CAPABILITY_OBJECT_LIFECYCLE_EVIDENCE_REQUIRED)

    missing_provenance = copy.deepcopy(value)
    del missing_provenance["provenance"]
    _expect_invalid(missing_provenance, CAPABILITY_OBJECT_PROVENANCE_REQUIRED)

    missing_contracts = copy.deepcopy(value)
    del missing_contracts["contracts"]
    _expect_invalid(missing_contracts, CAPABILITY_OBJECT_CONTRACTS_REQUIRED)

    broken_contract = copy.deepcopy(value)
    broken_contract["contracts"]["input"]["schema_ref"] = "agent-interface/capabilities/missing.v0.1.schema.json"
    _expect_invalid(broken_contract, CAPABILITY_OBJECT_REFERENCE_MISSING)

    unsupported_trust = copy.deepcopy(value)
    unsupported_trust["boundaries"]["metadata_is_verification"] = True
    _expect_invalid(unsupported_trust, CAPABILITY_OBJECT_BOUNDARY_INVALID)

    serialized = json.dumps(valid_result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        rerun = validate_capability_object(value)
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == serialized

    _assert_no_forbidden_runtime_imports()
    assert all(valid_result[field] is False for field in (
        "fdo_compliance_claimed",
        "external_trust_established",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "mcp_available",
        "api_available",
        "production_ready",
    ))

    print("SAEE_CAPABILITY_OBJECT_SMOKE: PASS")
    print("valid_objects=1/1")
    print("invalid_objects=8/8")
    print("deterministic_runs=5/5")
    print("resolved_references=54/54")
    print("identity_stable=true")
    print("lifecycle_evidence_required=true")
    print("provenance_present=true")
    print("contract_references_valid=true")
    print("fdo_compliance_claimed=false")
    print("external_trust_established=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("mcp_available=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
