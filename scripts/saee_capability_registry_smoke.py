#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Capability Registry Specification v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.capability_registry_validator import (
    REGISTRY_ADOPTION_CLAIM_FORBIDDEN,
    REGISTRY_BOUNDARY_INVALID,
    REGISTRY_CAPABILITY_ID_INVALID,
    REGISTRY_CONTRACT_REQUIRED,
    REGISTRY_CONTRACT_VERSION_MISMATCH,
    REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED,
    REGISTRY_LIFECYCLE_INVALID,
    REGISTRY_LIMITATIONS_REQUIRED,
    REGISTRY_PRODUCTION_EVIDENCE_REQUIRED,
    REGISTRY_PUBLIC_AVAILABILITY_OVERCLAIM,
    REGISTRY_REFERENCE_MISSING,
    REGISTRY_VERSION_INVALID,
    validate_capability_registry_entry,
)


SCHEMA_PATH = ROOT / "agent-interface/registry/saee-capability-registry.schema.v0.1.json"
CARD_PATH = ROOT / "agent-interface/registry/saee-capability-card.v0.1.json"
SPEC_PATH = ROOT / "docs/architecture/SAEE_CAPABILITY_REGISTRY_SPECIFICATION.md"
MIGRATION_PATH = ROOT / "docs/architecture/SAEE_CAPABILITY_REGISTRY_MIGRATION_NOTES.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CAPABILITY_REGISTRY_SPECIFICATION_RECOMMENDATION_GATE.md"
VALIDATOR_PATH = ROOT / "saee_backend/services/capability_registry_validator.py"


class RegistrySmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise RegistrySmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__", "open"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "system",
            "popen",
            "run",
            "Popen",
            "write_text",
            "write_bytes",
            "open",
        }:
            found.add(node.func.attr)
    return found


def expect_invalid(card: dict[str, Any], code: str, label: str) -> None:
    result = validate_capability_registry_entry(card)
    require(result["registry_entry_valid"] is False, f"invalid registry card accepted: {label}")
    require(result["reason_codes"] == [code], f"reason code drift for {label}: {result['reason_codes']}")
    require(result["network_accessed"] is False and result["subprocess_started"] is False, f"invalid validation expanded execution: {label}")


def main() -> None:
    for path in (SCHEMA_PATH, CARD_PATH, SPEC_PATH, MIGRATION_PATH, GATE_PATH, VALIDATOR_PATH):
        require(path.is_file(), f"missing required file: {path}")
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib", "sqlite3"}
    for path in (VALIDATOR_PATH, Path(__file__)):
        require(not imported_roots(path).intersection(forbidden_imports), f"network/subprocess import in {path.name}")
        require(not forbidden_calls(path), f"external execution or persistence in {path.name}: {forbidden_calls(path)}")

    schema = read_json(SCHEMA_PATH)
    card = read_json(CARD_PATH)
    Draft202012Validator.check_schema(schema)
    schema_errors = list(Draft202012Validator(schema).iter_errors(card))
    require(not schema_errors, f"capability card schema invalid: {schema_errors[0].message if schema_errors else ''}")

    valid = validate_capability_registry_entry(card)
    require(valid["registry_entry_valid"] is True, f"canonical registry card rejected: {valid['reason_codes']}")
    require(valid["capability_id"] == "saee.evidence-adequacy", "registry identity invalid")
    require(valid["version"] == "0.1" and valid["lifecycle_state"] == "LOCAL_PROTOTYPE", "registry version/lifecycle invalid")
    require(valid["resolved_reference_count"] == 50, "registry reference count invalid")
    require(valid["external_validation_completed"] is False, "external validation overclaimed")
    require(valid["production_validation_completed"] is False and valid["production_ready"] is False, "production overclaimed")
    require(valid["adoption_validated"] is False, "adoption overclaimed")
    require(valid["public_registry_available"] is False and valid["public_tool_available"] is False, "public availability overclaimed")

    specification = SPEC_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")
    for state in ("RESEARCH_PROTOTYPE", "LOCAL_PROTOTYPE", "EXTERNAL_VALIDATION", "PRODUCTION_CAPABILITY"):
        require(state in specification, f"lifecycle state missing from specification: {state}")
    for marker in (
        "Capability Registry Specification != Capability Marketplace",
        "Capability Metadata != Capability Adoption",
        "Registration Contract != Public Availability",
        "public_registry_available=false",
        "public_tool_available=false",
    ):
        require(marker in specification, f"registry boundary marker missing: {marker}")
    for drift_id in ("REGISTRY-MIGRATION-001", "REGISTRY-MIGRATION-002", "REGISTRY-MIGRATION-003"):
        require(drift_id in migration, f"migration drift missing: {drift_id}")
    require("historical_records_rewritten=false" in migration, "historical immutability missing")
    require("public_metadata_migrated=false" in migration, "migration status overclaimed")

    invalid_cases: list[tuple[dict[str, Any], str, str]] = []
    mutation = copy.deepcopy(card); mutation["lifecycle_state"] = "PRODUCTION_CAPABILITY"; invalid_cases.append((mutation, REGISTRY_PRODUCTION_EVIDENCE_REQUIRED, "production without evidence"))
    mutation = copy.deepcopy(card); mutation["lifecycle_state"] = "EXTERNAL_VALIDATION"; invalid_cases.append((mutation, REGISTRY_EXTERNAL_VALIDATION_EVIDENCE_REQUIRED, "external validation without evidence"))
    mutation = copy.deepcopy(card); mutation["validation_state"]["adoption_validated"] = True; invalid_cases.append((mutation, REGISTRY_ADOPTION_CLAIM_FORBIDDEN, "adoption claim"))
    mutation = copy.deepcopy(card); mutation.pop("input_contract"); invalid_cases.append((mutation, REGISTRY_CONTRACT_REQUIRED, "missing input contract"))
    mutation = copy.deepcopy(card); mutation["limitations"] = []; invalid_cases.append((mutation, REGISTRY_LIMITATIONS_REQUIRED, "missing limitations"))
    mutation = copy.deepcopy(card); mutation["version"] = "v1"; invalid_cases.append((mutation, REGISTRY_VERSION_INVALID, "invalid version"))
    mutation = copy.deepcopy(card); mutation["capability_id"] = "SAEE Evidence"; invalid_cases.append((mutation, REGISTRY_CAPABILITY_ID_INVALID, "invalid capability id"))
    mutation = copy.deepcopy(card); mutation["lifecycle_state"] = "PUBLISHED"; invalid_cases.append((mutation, REGISTRY_LIFECYCLE_INVALID, "invalid lifecycle"))
    mutation = copy.deepcopy(card); mutation["input_contract"]["schema_ref"] = "agent-interface/capabilities/missing.v0.1.schema.json"; invalid_cases.append((mutation, REGISTRY_REFERENCE_MISSING, "missing schema reference"))
    mutation = copy.deepcopy(card); mutation["input_contract"]["schema_version"] = "0.2"; invalid_cases.append((mutation, REGISTRY_CONTRACT_VERSION_MISMATCH, "contract version mismatch"))
    mutation = copy.deepcopy(card); mutation["discovery_endpoint"]["public_registry_available"] = True; invalid_cases.append((mutation, REGISTRY_PUBLIC_AVAILABILITY_OVERCLAIM, "public registry overclaim"))
    mutation = copy.deepcopy(card); mutation["boundary_contract"]["registry_entry_authorizes_use"] = True; invalid_cases.append((mutation, REGISTRY_BOUNDARY_INVALID, "registry authorization overclaim"))
    for mutation, code, label in invalid_cases:
        expect_invalid(mutation, code, label)

    canonical = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_capability_registry_entry(copy.deepcopy(card))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "registry validation non-deterministic")

    print("SAEE_CAPABILITY_REGISTRY_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("capability_id=saee.evidence-adequacy")
    print("version=0.1")
    print("lifecycle_state=LOCAL_PROTOTYPE")
    print("contract_references_resolved=50/50")
    print("external_validation_completed=false")
    print("adoption_validated=false")
    print("public_registry_available=false")
    print("public_tool_available=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (RegistrySmokeError, json.JSONDecodeError, OSError, SyntaxError) as exc:
        print(f"SAEE_CAPABILITY_REGISTRY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
