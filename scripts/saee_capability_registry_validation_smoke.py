#!/usr/bin/env python3
"""Offline smoke test for SAEE Capability Registry Validation v0.1."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.capability_registry_validation import (  # noqa: E402
    materialize_validation_fixture,
    validate_registry_declaration,
)


CARD_PATH = ROOT / "agent-interface/registry/saee-capability-card.v0.1.json"
FIXTURE_DIR = ROOT / "agent-interface/registry/validation-fixtures"
RESULT_SCHEMA_PATH = ROOT / "agent-interface/registry/saee-registry-validation-result.schema.v0.1.json"
MACHINE_RESULT_PATH = ROOT / "agent-interface/registry/saee-capability-registry-validation-result.v0.1.json"
SERVICE_PATH = ROOT / "saee_backend/services/capability_registry_validation.py"
EXPECTED_FIXTURES = {
    "valid-registry-entry.json",
    "invalid-production-without-evidence.json",
    "invalid-version-mismatch.json",
    "invalid-missing-contract.json",
    "invalid-boundary-overclaim.json",
    "invalid-broken-reference.json",
    "invalid-state-adoption-claim.json",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
    base = _load(CARD_PATH)
    schema = _load(RESULT_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    files = {path.name for path in FIXTURE_DIR.glob("*.json")}
    assert files == EXPECTED_FIXTURES, f"fixture set mismatch: {sorted(files)}"

    results = []
    valid_cases = 0
    invalid_cases = 0
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        fixture = _load(path)
        assert fixture["base_entry_ref"] == "agent-interface/registry/saee-capability-card.v0.1.json"
        entry = materialize_validation_fixture(base, fixture)
        result = validate_registry_declaration(entry)
        errors = sorted(validator.iter_errors(result), key=lambda error: list(error.absolute_path))
        assert not errors, f"result schema failure for {path.name}: {errors[0].message if errors else ''}"
        assert result["validation_status"] == fixture["expected_status"], path.name
        assert result["errors"] == fixture["expected_errors"], path.name
        if result["validation_status"] == "PASS":
            valid_cases += 1
        else:
            invalid_cases += 1
        results.append({
            "fixture_id": fixture["fixture_id"],
            "validation_status": result["validation_status"],
            "errors": result["errors"],
        })

    canonical = validate_registry_declaration(base)
    serialized = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        rerun = validate_registry_declaration(base)
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == serialized

    machine = _load(MACHINE_RESULT_PATH)
    machine_errors = sorted(validator.iter_errors(machine), key=lambda error: list(error.absolute_path))
    assert not machine_errors, machine_errors[0].message if machine_errors else ""
    assert machine["validation_status"] == "PASS"
    assert machine["fixture_summary"] == {
        "fixture_cases": 7,
        "valid_cases": 1,
        "invalid_cases": 6,
        "expected_outcomes_matched": True,
        "deterministic_runs": 5,
    }
    assert machine["fixture_results"] == results
    assert all(value is False for value in machine["truth_boundary"].values())
    _assert_no_forbidden_runtime_imports()

    print("SAEE_CAPABILITY_REGISTRY_VALIDATION_SMOKE: PASS")
    print("fixture_cases=7/7")
    print(f"valid_cases={valid_cases}/1")
    print(f"invalid_cases={invalid_cases}/6")
    print("deterministic_runs=5/5")
    print("version_consistent=true")
    print("reference_chain_valid=true")
    print("boundary_overclaim_rejected=true")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("registry_service_available=false")
    print("trust_authority=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
