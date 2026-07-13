#!/usr/bin/env python3
"""End-to-end offline checks for the Phase 2B synthetic Observation Adapter."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SERVICE_PATH = ROOT / "saee_backend/services/synthetic_observation_adapter.py"
INPUT_PATH = ROOT / "agent-interface/architecture/examples/adapter-provenance/synthetic-adapter-input.json"
INPUT_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-synthetic-external-observation.v0.1.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
PROVENANCE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-adapter-provenance-contract.v0.1.schema.json"
PROVENANCE_EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/adapter-provenance"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE2B_SYNTHETIC_OBSERVATION_ADAPTER.md"


class SyntheticObservationAdapterSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SyntheticObservationAdapterSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_bytes())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validator(path: Path) -> Draft202012Validator:
    schema = read_json(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def assert_schema(value: dict[str, Any], schema_validator: Draft202012Validator, label: str) -> None:
    errors = sorted(schema_validator.iter_errors(value), key=lambda item: list(item.path))
    require(not errors, f"{label}: {errors[0].message if errors else ''}")


def assert_no_authority(result: dict[str, Any]) -> None:
    require(result["evidence"] is None, "adapter generated Evidence")
    require(result["risk"] is None, "adapter generated Risk")
    require(result["decision"] is None, "adapter generated Decision")
    require(result["termination_contract"] is None, "adapter generated Termination Contract")


def write_json(path: Path, value: dict[str, Any]) -> str:
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_execution_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"}:
            found.add(node.func.attr)
    return found


def verify_read_once_shape() -> None:
    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_adapter_file")
    calls: list[str] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            calls.append(node.func.attr)
    require(calls.count("read_snapshot_once") == 1, "adapter input is not read exactly once")
    require(not {"read_bytes", "read_text", "open"}.intersection(calls), "adapter reopens input in run_adapter_file")


def main() -> None:
    for path in (SERVICE_PATH, INPUT_PATH, INPUT_SCHEMA_PATH, OBSERVATION_SCHEMA_PATH, PROVENANCE_SCHEMA_PATH, DOC_PATH):
        require(path.is_file(), f"missing required file: {path}")
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "pip", "importlib"}
    for path in (SERVICE_PATH, Path(__file__)):
        require(not imported_roots(path).intersection(forbidden_imports), f"forbidden capability import: {path}")
        require(not forbidden_execution_calls(path), f"forbidden dynamic or shell execution call: {path}")
    verify_read_once_shape()

    from saee_backend.services.synthetic_observation_adapter import run_adapter_file

    input_validator = validator(INPUT_SCHEMA_PATH)
    observation_validator = validator(OBSERVATION_SCHEMA_PATH)
    provenance_validator = validator(PROVENANCE_SCHEMA_PATH)
    valid_input = read_json(INPUT_PATH)
    assert_schema(valid_input, input_validator, "input schema")
    expected_digest = digest(INPUT_PATH)

    implementation_states = {
        read_json(PROVENANCE_EXAMPLE_DIRECTORY / "declared-adapter.json")["implementation_status"],
        read_json(PROVENANCE_EXAMPLE_DIRECTORY / "prototype-adapter.json")["implementation_status"],
        read_json(PROVENANCE_EXAMPLE_DIRECTORY / "validated-adapter.json")["implementation_status"],
    }
    require(implementation_states == {"declared", "prototype", "validated"}, "implementation states not separated")

    with tempfile.TemporaryDirectory(prefix=".saee-phase2b-adapter-", dir=ROOT) as temp_name:
        temp = Path(temp_name)
        output_path = temp / "observation-envelope.json"
        provenance_path = temp / "adapter-provenance.json"
        result = run_adapter_file(INPUT_PATH, expected_digest, output_path, provenance_path)
        require(result["adapter_result"] == "accepted", f"valid input rejected: {result['reason_code']}")
        assert_no_authority(result)
        envelope = result["observation_envelope"]
        provenance = result["adapter_provenance"]
        assert_schema(envelope, observation_validator, "output envelope schema")
        assert_schema(provenance, provenance_validator, "provenance schema")
        require(output_path.is_file() and provenance_path.is_file(), "accepted outputs not written")
        require(provenance["implementation_status"] == "prototype", "provenance not prototype")
        require(provenance["input_snapshot_digest"] == expected_digest, "input snapshot not bound")
        require(provenance["output_envelope_digest"] == digest(output_path), "output envelope not bound")
        require(provenance["process_same_bytes"] is True and provenance["read_once_verified"] is True, "same-bytes claim missing")
        require(provenance["adapter_receive_only"] is True, "adapter not receive-only")
        require(provenance["truth_boundary"]["termination_authority"] is False, "adapter has termination authority")
        require(envelope["truth_boundary"]["observation_only"] is True, "output not observation-only")
        require(envelope["truth_boundary"]["evidence_established"] is False, "output promoted to Evidence")

        canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for _ in range(5):
            repeated = run_adapter_file(INPUT_PATH, expected_digest, output_path, provenance_path)
            require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "adapter output non-deterministic")

        mismatch_input = temp / "mutated-after-digest.json"
        mismatch_input.write_bytes(INPUT_PATH.read_bytes())
        original_digest = digest(mismatch_input)
        mutated = read_json(mismatch_input)
        mutated["events"][0]["observable_behavior_summary"] = "Synthetic input changed after the expected digest was recorded."
        write_json(mismatch_input, mutated)
        mismatch_output = temp / "mismatch-output.json"
        mismatch_provenance = temp / "mismatch-provenance.json"
        mismatch_result = run_adapter_file(mismatch_input, original_digest, mismatch_output, mismatch_provenance)
        require(mismatch_result["adapter_result"] == "reject", "snapshot mismatch accepted")
        require(mismatch_result["reason_code"] == "ADAPTER_SNAPSHOT_DIGEST_MISMATCH", "snapshot mismatch reason unstable")
        assert_no_authority(mismatch_result)
        require(not mismatch_output.exists() and not mismatch_provenance.exists(), "snapshot mismatch wrote outputs")

        forbidden_fields = (
            "raw_prompt",
            "raw_output",
            "hidden_reasoning",
            "private_chain_of_thought",
            "internal_model_state",
            "customer_data",
        )
        for index, field in enumerate(forbidden_fields):
            invalid = copy.deepcopy(valid_input)
            invalid[field] = "forbidden synthetic test value"
            invalid_path = temp / f"content-boundary-{index}.json"
            invalid_digest = write_json(invalid_path, invalid)
            invalid_output = temp / f"content-boundary-{index}-output.json"
            invalid_provenance = temp / f"content-boundary-{index}-provenance.json"
            rejected = run_adapter_file(invalid_path, invalid_digest, invalid_output, invalid_provenance)
            require(rejected["adapter_result"] == "reject", f"forbidden field accepted: {field}")
            require(rejected["reason_code"] == "ADAPTER_CONTENT_BOUNDARY_VIOLATION", f"unstable content reason: {field}")
            assert_no_authority(rejected)
            require(not invalid_output.exists() and not invalid_provenance.exists(), f"forbidden field wrote output: {field}")

        boundary_input = copy.deepcopy(valid_input)
        boundary_input["content_boundary"]["customer_data_present"] = True
        boundary_path = temp / "boundary-violation.json"
        boundary_digest = write_json(boundary_path, boundary_input)
        boundary_output = temp / "boundary-output.json"
        boundary_provenance = temp / "boundary-provenance.json"
        boundary_result = run_adapter_file(boundary_path, boundary_digest, boundary_output, boundary_provenance)
        require(boundary_result["adapter_result"] == "reject", "boundary violation accepted")
        require(boundary_result["reason_code"] == "ADAPTER_INPUT_SCHEMA_INVALID", "boundary violation reason unstable")
        assert_no_authority(boundary_result)
        require(not boundary_output.exists() and not boundary_provenance.exists(), "boundary violation wrote outputs")

    print("SAEE_SYNTHETIC_OBSERVATION_ADAPTER_SMOKE: PASS")
    print("schema_valid=true")
    print("adapter_provenance_binding=true")
    print("declared_prototype_validated_separation=true")
    print("snapshot_integrity=true")
    print("snapshot_mismatch_rejected=true")
    print("read_once_digest_process_same_bytes=true")
    print("observation_only_output=true")
    print("no_evidence_generation=true")
    print("no_risk_generation=true")
    print("no_decision_generation=true")
    print("no_termination_authority=true")
    print("content_boundary_enforcement=7/7")
    print("fail_closed=true")
    print("deterministic_runs=5/5")
    print("adapter_implemented=true")
    print("implementation_scope=local_synthetic_prototype_only")
    print("real_agent_executed=false")
    print("external_tool_executed=false")
    print("network_accessed=false")
    print("customer_data_processed=false")
    print("automatic_decision=false")
    print("deployment_authorized=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (SyntheticObservationAdapterSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_SYNTHETIC_OBSERVATION_ADAPTER_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
