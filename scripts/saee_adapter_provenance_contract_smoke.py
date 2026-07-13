#!/usr/bin/env python3
"""Offline validation for the SAEE Adapter Provenance Contract v0.1."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-adapter-provenance-contract.v0.1.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/adapter-provenance"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE2B0_ADAPTER_PROVENANCE_CONTRACT.md"
EXPECTED_EXAMPLES = {
    "declared-adapter.json": "declared",
    "prototype-adapter.json": "prototype",
    "validated-adapter.json": "validated",
}


class AdapterProvenanceSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AdapterProvenanceSmokeError(detail)


def read_snapshot(path: Path) -> tuple[bytes, str]:
    payload = path.read_bytes()
    return payload, hashlib.sha256(payload).hexdigest()


def parse_snapshot(path: Path) -> tuple[dict[str, Any], str]:
    payload, digest = read_snapshot(path)
    return json.loads(payload), digest


def resolve_local_ref(ref: str) -> Path:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise AdapterProvenanceSmokeError(f"REFERENCE_OUTSIDE_REPOSITORY: {ref}") from exc
    require(path.is_file(), f"REFERENCE_MISSING: {ref}")
    return path


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def validate_semantics(record: dict[str, Any]) -> None:
    require(record["adapter_receive_only"] is True, "ADAPTER_NOT_RECEIVE_ONLY")
    require(record["produces_observation"] is True, "OBSERVATION_OUTPUT_REQUIRED")
    require(record["produces_evidence"] is False, "ADAPTER_EVIDENCE_FORBIDDEN")
    require(record["produces_risk"] is False, "ADAPTER_RISK_FORBIDDEN")
    require(record["produces_decision"] is False, "ADAPTER_DECISION_FORBIDDEN")
    require(record["network_accessed"] is False, "ADAPTER_NETWORK_FORBIDDEN")
    require(record["external_execution"] is False, "ADAPTER_EXTERNAL_EXECUTION_FORBIDDEN")
    truth = record["truth_boundary"]
    require(truth["termination_authority"] is False, "ADAPTER_TERMINATION_AUTHORITY_FORBIDDEN")
    require(truth["observation_is_evidence"] is False, "OBSERVATION_PROMOTED_TO_EVIDENCE")
    require(truth["risk_probability_measured"] is False, "RISK_MEASUREMENT_OVERCLAIM")
    require(truth["decision_authorized"] is False, "DECISION_AUTHORITY_OVERCLAIM")
    require(truth["customer_data_processed"] is False, "CUSTOMER_DATA_FORBIDDEN")
    require(truth["production_ready"] is False, "PRODUCTION_OVERCLAIM")


def validate_binding(record: dict[str, Any], observation_validator: Draft202012Validator) -> None:
    status = record["implementation_status"]
    if status == "declared":
        require(record["input_snapshot_ref"] is None and record["input_snapshot_digest"] is None, "DECLARATION_HAS_FAKE_INPUT_BINDING")
        require(record["output_envelope_ref"] is None and record["output_envelope_digest"] is None, "DECLARATION_HAS_FAKE_OUTPUT_BINDING")
        require(record["process_same_bytes"] is False and record["read_once_verified"] is False, "DECLARATION_HAS_FAKE_SNAPSHOT_VERIFICATION")
        return

    input_path = resolve_local_ref(record["input_snapshot_ref"])
    input_payload, input_digest = read_snapshot(input_path)
    require(input_digest == record["input_snapshot_digest"], "INPUT_SNAPSHOT_DIGEST_MISMATCH")
    input_value = json.loads(input_payload)
    boundary = input_value.get("content_boundary", input_value)
    for field in ("raw_prompt_present", "raw_output_present", "hidden_reasoning_present", "private_chain_of_thought_present", "internal_model_state_present", "customer_data_present"):
        require(boundary.get(field) is False, f"INPUT_CONTENT_BOUNDARY_INVALID: {field}")
    if "content_boundary" in input_value:
        require(boundary.get("observable_behavior_summary_only") is True, "INPUT_CONTENT_BOUNDARY_INVALID: observable_behavior_summary_only")
    require(record["process_same_bytes"] is True and record["read_once_verified"] is True, "SNAPSHOT_SAME_BYTES_NOT_VERIFIED")

    output_path = resolve_local_ref(record["output_envelope_ref"])
    output_payload, output_digest = read_snapshot(output_path)
    require(output_digest == record["output_envelope_digest"], "OUTPUT_ENVELOPE_DIGEST_MISMATCH")
    output_value = json.loads(output_payload)
    errors = sorted(observation_validator.iter_errors(output_value), key=lambda item: list(item.path))
    require(not errors, f"OUTPUT_ENVELOPE_INVALID: {errors[0].message if errors else ''}")
    require(output_value["truth_boundary"]["observation_only"] is True, "OUTPUT_NOT_OBSERVATION_ONLY")
    require(output_value["truth_boundary"]["evidence_established"] is False, "OUTPUT_ESTABLISHES_EVIDENCE")


def expect_schema_rejection(validator: Draft202012Validator, record: dict[str, Any], detail: str) -> None:
    require(bool(list(validator.iter_errors(record))), f"NEGATIVE_SCHEMA_ACCEPTED: {detail}")


def expect_semantic_rejection(record: dict[str, Any], detail: str, observation_validator: Draft202012Validator) -> None:
    try:
        validate_semantics(record)
        validate_binding(record, observation_validator)
    except AdapterProvenanceSmokeError:
        return
    raise AdapterProvenanceSmokeError(f"NEGATIVE_SEMANTIC_ACCEPTED: {detail}")


def main() -> None:
    for path in (SCHEMA_PATH, OBSERVATION_SCHEMA_PATH, DOC_PATH):
        require(path.is_file(), f"missing required file: {path}")
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "pip", "importlib"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "FORBIDDEN_EXTERNAL_CAPABILITY_IMPORT")

    schema, _schema_digest = parse_snapshot(SCHEMA_PATH)
    observation_schema, _observation_schema_digest = parse_snapshot(OBSERVATION_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    observation_validator = Draft202012Validator(observation_schema, format_checker=FormatChecker())

    records: dict[str, dict[str, Any]] = {}
    for filename, expected_status in EXPECTED_EXAMPLES.items():
        path = EXAMPLE_DIRECTORY / filename
        require(path.is_file(), f"missing example: {filename}")
        record, _digest = parse_snapshot(path)
        errors = sorted(validator.iter_errors(record), key=lambda item: list(item.path))
        require(not errors, f"schema invalid {filename}: {errors[0].message if errors else ''}")
        require(record["implementation_status"] == expected_status, f"implementation state mismatch: {filename}")
        require(record["truth_boundary"]["record_scope"] == "synthetic_example_only", f"non-synthetic example: {filename}")
        validate_semantics(record)
        validate_binding(record, observation_validator)
        records[filename] = record

    require(len({record["implementation_status"] for record in records.values()}) == 3, "IMPLEMENTATION_STATES_NOT_SEPARATED")

    negative_count = 0
    base = records["prototype-adapter.json"]
    for field, value in (
        ("adapter_receive_only", False),
        ("produces_observation", False),
        ("produces_evidence", True),
        ("produces_risk", True),
        ("produces_decision", True),
        ("network_accessed", True),
        ("external_execution", True),
        ("process_same_bytes", False),
        ("read_once_verified", False),
    ):
        mutation = copy.deepcopy(base)
        mutation[field] = value
        expect_schema_rejection(validator, mutation, field)
        negative_count += 1
    for field in ("termination_authority", "observation_is_evidence", "risk_probability_measured", "decision_authorized", "customer_data_processed", "production_ready"):
        mutation = copy.deepcopy(base)
        mutation["truth_boundary"][field] = True
        expect_schema_rejection(validator, mutation, field)
        negative_count += 1
    mutation = copy.deepcopy(base); mutation["input_snapshot_digest"] = "0" * 64
    expect_semantic_rejection(mutation, "input digest", observation_validator); negative_count += 1
    mutation = copy.deepcopy(base); mutation["output_envelope_digest"] = "0" * 64
    expect_semantic_rejection(mutation, "output digest", observation_validator); negative_count += 1
    mutation = copy.deepcopy(base); mutation["input_snapshot_ref"] = "../outside.json"
    expect_schema_rejection(validator, mutation, "path traversal"); negative_count += 1
    mutation = copy.deepcopy(base); mutation["unexpected"] = True
    expect_schema_rejection(validator, mutation, "additional property"); negative_count += 1
    mutation = copy.deepcopy(records["declared-adapter.json"]); mutation["process_same_bytes"] = True
    expect_schema_rejection(validator, mutation, "declared fake verification"); negative_count += 1

    canonical = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = {name: parse_snapshot(EXAMPLE_DIRECTORY / name)[0] for name in EXPECTED_EXAMPLES}
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "NON_DETERMINISTIC_EXAMPLES")

    print("SAEE_ADAPTER_PROVENANCE_CONTRACT_SMOKE: PASS")
    print("schema_valid=true")
    print("implementation_states=declared,prototype,validated")
    print("implementation_state_separation=3/3")
    print("snapshot_binding=2/2")
    print("output_binding=2/2")
    print("receive_only=3/3")
    print("produces_observation=3/3")
    print("produces_evidence=false")
    print("produces_risk=false")
    print("produces_decision=false")
    print("termination_authority=false")
    print(f"negative_cases={negative_count}/{negative_count}")
    print("deterministic_runs=5/5")
    print("network_accessed=false")
    print("external_execution=false")
    print("real_agent_executed=false")
    print("customer_data_processed=false")
    print("adapter_implemented_by_contract_task=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (AdapterProvenanceSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_ADAPTER_PROVENANCE_CONTRACT_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
