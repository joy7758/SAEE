#!/usr/bin/env python3
"""Fail-closed readiness gate for a future receive-only Observation Adapter."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/strategy/SAEE_PHASE2B_ADAPTER_READINESS_GATE.md"
AGENT_INDEX_PATH = ROOT / "agent-index.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
OBSERVATION_EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/observation"

FROZEN_HASHES = {
    ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md": "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3",
    ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json": "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e",
    OBSERVATION_SCHEMA_PATH: "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2",
    ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json": "aa7fcdcf7908a1f6f2bcd530ba7a8edfab1aa41d32fa964c422680dd36f61db1",
    ROOT / "agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json": "4c2e9c483a26b477163a14296bd5d505b8176cf5c4c242c4c9e2aa46d8aeb30d",
    ROOT / "agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json": "80847a94737a88f84a2f4f4c0b266b7b230c177ec01950375aa628bafe4b4a6d",
    ROOT / "agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json": "daa79bed6c130a554512890d6039b92337e17b000985d108ce33768434d0d362",
}

REQUIRED_PROFILE: dict[str, Any] = {
    "allowed_input_modes": ["local_file", "bounded_stdio"],
    "adapter_receive_only": True,
    "adapter_produces_observation_only": True,
    "adapter_produces_evidence": False,
    "adapter_produces_risk": False,
    "adapter_produces_decision": False,
    "adapter_produces_deployment_recommendation": False,
    "agent_execution_allowed": False,
    "tool_execution_allowed": False,
    "memory_modification_allowed": False,
    "network_listener_allowed": False,
    "outbound_network_allowed": False,
    "dynamic_code_execution_allowed": False,
    "dependency_install_allowed": False,
    "raw_prompt_present": False,
    "raw_output_present": False,
    "hidden_reasoning_present": False,
    "internal_model_state_present": False,
    "customer_data_present": False,
    "immutable_input_snapshot_required": True,
    "read_once_digest_process_same_bytes": True,
    "fail_closed": True,
    "input_repair_allowed": False,
    "invalid_input_outcomes": ["reject", "termination_record"],
    "production_ready": False,
}


class Phase2BAdapterReadinessError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise Phase2BAdapterReadinessError(code, detail)


def read_snapshot(path: Path) -> tuple[bytes, str]:
    """Read one immutable byte snapshot and digest exactly those bytes."""
    payload = path.read_bytes()
    return payload, hashlib.sha256(payload).hexdigest()


def read_json_snapshot(path: Path) -> tuple[dict[str, Any], str]:
    payload, digest = read_snapshot(path)
    return json.loads(payload), digest


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def called_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    require(profile.get("allowed_input_modes") == ["local_file", "bounded_stdio"], "PHASE2B_INPUT_MODE_INVALID", "only local_file and bounded_stdio are allowed")
    require(profile.get("adapter_receive_only") is True, "PHASE2B_ADAPTER_DIRECTION_INVALID", "adapter_receive_only")
    require(profile.get("adapter_produces_observation_only") is True, "PHASE2B_OUTPUT_BOUNDARY_INVALID", "adapter_produces_observation_only")
    for field in (
        "adapter_produces_evidence",
        "adapter_produces_risk",
        "adapter_produces_decision",
        "adapter_produces_deployment_recommendation",
    ):
        require(profile.get(field) is False, "PHASE2B_OUTPUT_BOUNDARY_INVALID", field)
    for field in ("agent_execution_allowed", "tool_execution_allowed", "memory_modification_allowed"):
        require(profile.get(field) is False, "PHASE2B_CONTROL_BOUNDARY_INVALID", field)
    for field in (
        "network_listener_allowed",
        "outbound_network_allowed",
        "dynamic_code_execution_allowed",
        "dependency_install_allowed",
    ):
        require(profile.get(field) is False, "PHASE2B_EXTERNAL_CAPABILITY_INVALID", field)
    for field in (
        "raw_prompt_present",
        "raw_output_present",
        "hidden_reasoning_present",
        "internal_model_state_present",
        "customer_data_present",
    ):
        require(profile.get(field) is False, "PHASE2B_DATA_BOUNDARY_INVALID", field)
    require(profile.get("immutable_input_snapshot_required") is True, "PHASE2B_SNAPSHOT_POLICY_INVALID", "immutable_input_snapshot_required")
    require(profile.get("read_once_digest_process_same_bytes") is True, "PHASE2B_SNAPSHOT_POLICY_INVALID", "read_once_digest_process_same_bytes")
    require(profile.get("fail_closed") is True, "PHASE2B_FAIL_CLOSED_REQUIRED", "fail_closed")
    require(profile.get("input_repair_allowed") is False, "PHASE2B_FAIL_CLOSED_REQUIRED", "input_repair_allowed")
    require(profile.get("invalid_input_outcomes") == ["reject", "termination_record"], "PHASE2B_FAIL_CLOSED_REQUIRED", "invalid_input_outcomes")
    require(profile.get("production_ready") is False, "PHASE2B_PRODUCTION_BOUNDARY_INVALID", "production_ready")
    return copy.deepcopy(profile)


def validate_observation_boundary() -> int:
    schema, schema_digest = read_json_snapshot(OBSERVATION_SCHEMA_PATH)
    require(schema_digest == FROZEN_HASHES[OBSERVATION_SCHEMA_PATH], "PHASE2B_FROZEN_FILE_CHANGED", str(OBSERVATION_SCHEMA_PATH))
    Draft202012Validator.check_schema(schema)
    require(schema.get("additionalProperties") is False, "PHASE2B_OBSERVATION_SCHEMA_OPEN", "root additionalProperties")
    properties = schema["properties"]
    require(properties["producer"]["properties"]["adapter_implemented"].get("const") is False, "PHASE2B_ADAPTER_ALREADY_IMPLEMENTED", "producer.adapter_implemented")
    require(properties["source"]["properties"]["receive_only"].get("const") is True, "PHASE2B_ADAPTER_DIRECTION_INVALID", "source.receive_only")
    require(properties["source"]["properties"]["external_execution_by_saee"].get("const") is False, "PHASE2B_CONTROL_BOUNDARY_INVALID", "source.external_execution_by_saee")
    require(properties["source"]["properties"]["raw_content_included"].get("const") is False, "PHASE2B_DATA_BOUNDARY_INVALID", "source.raw_content_included")
    truth = properties["truth_boundary"]["properties"]
    require(truth["observation_only"].get("const") is True, "PHASE2B_OUTPUT_BOUNDARY_INVALID", "truth_boundary.observation_only")
    for field in ("evidence_established", "deployment_authorized", "automatic_decision", "network_accessed", "production_ready"):
        require(truth[field].get("const") is False, "PHASE2B_OUTPUT_BOUNDARY_INVALID", f"truth_boundary.{field}")

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = sorted(OBSERVATION_EXAMPLE_DIRECTORY.glob("*.json"))
    require(len(paths) == 3, "PHASE2B_OBSERVATION_EXAMPLE_COUNT_INVALID", str(len(paths)))
    for path in paths:
        envelope, _digest = read_json_snapshot(path)
        errors = sorted(validator.iter_errors(envelope), key=lambda item: list(item.path))
        require(not errors, "PHASE2B_OBSERVATION_EXAMPLE_INVALID", f"{path}: {errors[0].message if errors else ''}")
        require(envelope["producer"]["adapter_implemented"] is False, "PHASE2B_ADAPTER_ALREADY_IMPLEMENTED", envelope["observation_id"])
        require(envelope["source"]["receive_only"] is True, "PHASE2B_ADAPTER_DIRECTION_INVALID", envelope["observation_id"])
        require(envelope["source"]["raw_content_included"] is False, "PHASE2B_DATA_BOUNDARY_INVALID", envelope["observation_id"])
        require(all(event["payload_included"] is False for event in envelope["events"]), "PHASE2B_DATA_BOUNDARY_INVALID", envelope["observation_id"])
        require(envelope["privacy"]["personal_data_included"] is False, "PHASE2B_DATA_BOUNDARY_INVALID", envelope["observation_id"])
        require(envelope["truth_boundary"]["observation_only"] is True, "PHASE2B_OUTPUT_BOUNDARY_INVALID", envelope["observation_id"])
        require(envelope["truth_boundary"]["evidence_established"] is False, "PHASE2B_OUTPUT_BOUNDARY_INVALID", envelope["observation_id"])
    return len(paths)


def validate_phase2a_truth_surface() -> None:
    index, _digest = read_json_snapshot(AGENT_INDEX_PATH)
    execution = index["saee_phase2a_synthetic_execution"]
    require(execution["fixed_evaluation_input_pipeline_executed"] is True, "PHASE2B_PHASE2A_PREREQUISITE_MISSING", "fixed_evaluation_input_pipeline_executed")
    require(execution["synthetic_replay_contract_validated"] is True, "PHASE2B_PHASE2A_PREREQUISITE_MISSING", "synthetic_replay_contract_validated")
    require(execution["synthetic_metadata_reconstruction_applied"] is False, "PHASE2B_PHASE2A_OVERCLAIM", "synthetic_metadata_reconstruction_applied")
    require(execution["synthetic_offline_replay_executed"] is False, "PHASE2B_PHASE2A_OVERCLAIM", "synthetic_offline_replay_executed")
    require(execution["real_agent_executed"] is False, "PHASE2B_PHASE2A_OVERCLAIM", "real_agent_executed")
    require(execution["customer_data_processed"] is False, "PHASE2B_PHASE2A_OVERCLAIM", "customer_data_processed")
    require(execution["network_accessed"] is False, "PHASE2B_PHASE2A_OVERCLAIM", "network_accessed")
    require(execution["production_ready"] is False, "PHASE2B_PHASE2A_OVERCLAIM", "production_ready")


def validate_document() -> None:
    payload, _digest = read_snapshot(DOC_PATH)
    text = payload.decode("utf-8")
    markers = (
        "adapter_receive_only=true",
        "adapter_produces_observation_only=true",
        "adapter_produces_evidence=false",
        "adapter_produces_risk=false",
        "adapter_produces_decision=false",
        "immutable_input_snapshot_required=true",
        "read_once_digest_process_same_bytes=true",
        "adapter_implemented_by_gate=false",
        "adapter_behavior_verified_by_gate=false",
        "production_ready=false",
    )
    for marker in markers:
        require(marker in text, "PHASE2B_GATE_DOC_INCOMPLETE", marker)


def expect_rejection(profile: dict[str, Any], expected_code: str) -> None:
    try:
        validate_profile(profile)
    except Phase2BAdapterReadinessError as exc:
        require(exc.code == expected_code, "PHASE2B_NEGATIVE_REASON_MISMATCH", f"{expected_code}!={exc.code}")
    else:
        raise Phase2BAdapterReadinessError("PHASE2B_NEGATIVE_ACCEPTED", expected_code)


def main() -> None:
    require(DOC_PATH.is_file(), "PHASE2B_GATE_DOC_MISSING", str(DOC_PATH))
    for path, expected in FROZEN_HASHES.items():
        require(path.is_file(), "PHASE2B_FROZEN_FILE_MISSING", str(path))
        _payload, actual = read_snapshot(path)
        require(actual == expected, "PHASE2B_FROZEN_FILE_CHANGED", str(path))

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "pip", "importlib"}
    forbidden_calls = {"eval", "exec", "compile", "__import__", "system", "popen"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "PHASE2B_GATE_EXTERNAL_CAPABILITY", "forbidden import")
    require(not called_names(Path(__file__)).intersection(forbidden_calls), "PHASE2B_GATE_DYNAMIC_EXECUTION", "forbidden call")

    validate_document()
    observation_count = validate_observation_boundary()
    validate_phase2a_truth_surface()
    result = validate_profile(REQUIRED_PROFILE)

    negative_cases: list[tuple[dict[str, Any], str]] = []
    for field, value, code in (
        ("adapter_receive_only", False, "PHASE2B_ADAPTER_DIRECTION_INVALID"),
        ("adapter_produces_observation_only", False, "PHASE2B_OUTPUT_BOUNDARY_INVALID"),
        ("adapter_produces_evidence", True, "PHASE2B_OUTPUT_BOUNDARY_INVALID"),
        ("adapter_produces_risk", True, "PHASE2B_OUTPUT_BOUNDARY_INVALID"),
        ("adapter_produces_decision", True, "PHASE2B_OUTPUT_BOUNDARY_INVALID"),
        ("adapter_produces_deployment_recommendation", True, "PHASE2B_OUTPUT_BOUNDARY_INVALID"),
        ("agent_execution_allowed", True, "PHASE2B_CONTROL_BOUNDARY_INVALID"),
        ("tool_execution_allowed", True, "PHASE2B_CONTROL_BOUNDARY_INVALID"),
        ("memory_modification_allowed", True, "PHASE2B_CONTROL_BOUNDARY_INVALID"),
        ("network_listener_allowed", True, "PHASE2B_EXTERNAL_CAPABILITY_INVALID"),
        ("outbound_network_allowed", True, "PHASE2B_EXTERNAL_CAPABILITY_INVALID"),
        ("raw_prompt_present", True, "PHASE2B_DATA_BOUNDARY_INVALID"),
        ("raw_output_present", True, "PHASE2B_DATA_BOUNDARY_INVALID"),
        ("hidden_reasoning_present", True, "PHASE2B_DATA_BOUNDARY_INVALID"),
        ("internal_model_state_present", True, "PHASE2B_DATA_BOUNDARY_INVALID"),
        ("customer_data_present", True, "PHASE2B_DATA_BOUNDARY_INVALID"),
        ("immutable_input_snapshot_required", False, "PHASE2B_SNAPSHOT_POLICY_INVALID"),
        ("read_once_digest_process_same_bytes", False, "PHASE2B_SNAPSHOT_POLICY_INVALID"),
        ("fail_closed", False, "PHASE2B_FAIL_CLOSED_REQUIRED"),
        ("input_repair_allowed", True, "PHASE2B_FAIL_CLOSED_REQUIRED"),
        ("production_ready", True, "PHASE2B_PRODUCTION_BOUNDARY_INVALID"),
    ):
        mutation = copy.deepcopy(REQUIRED_PROFILE)
        mutation[field] = value
        negative_cases.append((mutation, code))
    mutation = copy.deepcopy(REQUIRED_PROFILE)
    mutation["allowed_input_modes"] = ["webhook"]
    negative_cases.append((mutation, "PHASE2B_INPUT_MODE_INVALID"))
    for mutation, code in negative_cases:
        expect_rejection(mutation, code)

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_profile(REQUIRED_PROFILE)
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "PHASE2B_NON_DETERMINISTIC_GATE", "profile changed")

    print("SAEE_PHASE2B_ADAPTER_READINESS_GATE: PASS")
    print("gate_result=PHASE2B_ADAPTER_GATE_PASS")
    print("recommendation=recommend_local_synthetic_gate_only")
    print(f"observation_contract_examples_validated={observation_count}/3")
    print("frozen_contracts_unchanged=true")
    for key, value in result.items():
        if isinstance(value, bool):
            print(f"{key}={str(value).lower()}")
        elif isinstance(value, list):
            print(f"{key}={','.join(value)}")
    print("adapter_implemented_by_gate=false")
    print("adapter_behavior_verified_by_gate=false")
    print("snapshot_requirement_defined=true")
    print("snapshot_behavior_verified=false")
    print("negative_gate_cases=22/22")
    print("deterministic_runs=5/5")
    print("phase2b_adapter_implementation_authorized_by_this_script=false")
    print("phase2b_real_agent_data=HOLD")


if __name__ == "__main__":
    main()
