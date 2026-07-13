#!/usr/bin/env python3
"""Fail-closed readiness gate for a future local synthetic Phase 2A run."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/strategy/SAEE_PHASE2A_READINESS_GATE.md"

SCHEMA_PATHS = {
    "evidence_case": ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json",
    "observation": ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json",
    "replay": ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json",
    "replay_evaluation": ROOT / "agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json",
    "evaluation_run": ROOT / "agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json",
    "termination": ROOT / "agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json",
}

EXAMPLE_DIRECTORIES = {
    "evidence_case": ROOT / "agent-interface/architecture/examples/phase1_5_cases",
    "observation": ROOT / "agent-interface/architecture/examples/observation",
    "replay": ROOT / "agent-interface/architecture/examples/replay",
    "replay_evaluation": ROOT / "agent-interface/architecture/examples/replay-evaluation",
    "evaluation_run": ROOT / "agent-interface/architecture/examples/evaluation-run",
    "termination": ROOT / "agent-interface/architecture/examples/run-termination",
}

FROZEN_HASHES = {
    ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md": "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3",
    SCHEMA_PATHS["evidence_case"]: "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e",
    SCHEMA_PATHS["observation"]: "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2",
    SCHEMA_PATHS["replay"]: "aa7fcdcf7908a1f6f2bcd530ba7a8edfab1aa41d32fa964c422680dd36f61db1",
    SCHEMA_PATHS["replay_evaluation"]: "4c2e9c483a26b477163a14296bd5d505b8176cf5c4c242c4c9e2aa46d8aeb30d",
    SCHEMA_PATHS["evaluation_run"]: "80847a94737a88f84a2f4f4c0b266b7b230c177ec01950375aa628bafe4b4a6d",
    SCHEMA_PATHS["termination"]: "daa79bed6c130a554512890d6039b92337e17b000985d108ce33768434d0d362",
}

EXPECTED_COUNTS = {
    "evidence_case": 5,
    "observation": 3,
    "replay": 3,
    "replay_evaluation": 3,
    "evaluation_run": 3,
    "termination": 3,
}


class Phase2AReadinessError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise Phase2AReadinessError(code, detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def walk_values(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def require_false_fields(value: Any, fields: set[str], code: str) -> None:
    for key, child in walk_values(value):
        if key in fields:
            require(child is False, code, f"{key} must be false")


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def validate_contract_stack() -> tuple[dict[str, list[dict[str, Any]]], int]:
    objects: dict[str, list[dict[str, Any]]] = {}
    validated = 0
    for name, schema_path in SCHEMA_PATHS.items():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        paths = sorted(EXAMPLE_DIRECTORIES[name].glob("*.json"))
        require(len(paths) == EXPECTED_COUNTS[name], "PHASE2A_CONTRACT_COUNT_INVALID", name)
        objects[name] = []
        for path in paths:
            value = load_json(path)
            errors = sorted(validator.iter_errors(value), key=lambda item: list(item.path))
            require(not errors, "PHASE2A_CONTRACT_STACK_INVALID", f"{path}: {errors[0].message if errors else ''}")
            objects[name].append(value)
            validated += 1
    return objects, validated


def validate_synthetic_observation(envelope: dict[str, Any]) -> None:
    require(envelope["authorization"]["status"] == "synthetic_declared_only", "PHASE2A_NON_SYNTHETIC_SOURCE", envelope["observation_id"])
    require(envelope["sanitization"]["status"] == "synthetic_no_raw_content", "PHASE2A_NON_SYNTHETIC_SOURCE", envelope["observation_id"])
    require(envelope["sanitization"]["method"] == "synthetic_generation", "PHASE2A_NON_SYNTHETIC_SOURCE", envelope["observation_id"])
    require(envelope["sanitization"]["raw_content_excluded"] is True, "PHASE2A_RAW_CONTENT_PRESENT", envelope["observation_id"])
    require(envelope["source"]["raw_content_included"] is False, "PHASE2A_RAW_CONTENT_PRESENT", envelope["observation_id"])
    require(envelope["source"]["external_execution_by_saee"] is False, "PHASE2A_EXTERNAL_EXECUTION_ALLOWED", envelope["observation_id"])
    require(envelope["source"]["receive_only"] is True, "PHASE2A_SOURCE_NOT_RECEIVE_ONLY", envelope["observation_id"])
    require(envelope["producer"]["adapter_implemented"] is False, "PHASE2A_REAL_ADAPTER_PRESENT", envelope["observation_id"])
    require(envelope["privacy"]["personal_data_included"] is False, "PHASE2A_PERSONAL_DATA_PRESENT", envelope["observation_id"])
    require(all(event["payload_included"] is False for event in envelope["events"]), "PHASE2A_RAW_CONTENT_PRESENT", envelope["observation_id"])
    require(envelope["truth_boundary"]["real_agent_executed_by_saee"] is False, "PHASE2A_REAL_AGENT_ALLOWED", envelope["observation_id"])
    require(envelope["truth_boundary"]["network_accessed"] is False, "PHASE2A_NETWORK_ALLOWED", envelope["observation_id"])


def validate_reference_integrity(objects: dict[str, list[dict[str, Any]]]) -> None:
    observations = {item["observation_id"]: item for item in objects["observation"]}
    for replay in objects["replay"]:
        for source in replay["source_envelope_refs"]:
            path = ROOT / source["envelope_ref"]
            require(path.is_file(), "PHASE2A_REFERENCE_MISSING", source["envelope_ref"])
            require(sha256_path(path) == source["envelope_digest"], "PHASE2A_REFERENCE_DIGEST_INVALID", source["envelope_ref"])
            require(source["observation_id"] in observations, "PHASE2A_REFERENCE_ID_INVALID", source["observation_id"])

    for mapping in objects["replay_evaluation"]:
        replay_path = ROOT / mapping["replay_contract_ref"]
        input_path = ROOT / mapping["evaluation_input_ref"]
        require(replay_path.is_file() and input_path.is_file(), "PHASE2A_REFERENCE_MISSING", mapping["replay_evaluation_id"])
        require(sha256_path(replay_path) == mapping["replay_contract_digest"], "PHASE2A_REFERENCE_DIGEST_INVALID", mapping["replay_evaluation_id"])
        require(sha256_path(input_path) == mapping["evaluation_input_digest"], "PHASE2A_REFERENCE_DIGEST_INVALID", mapping["replay_evaluation_id"])
        require(all(rule["executable"] is False for rule in mapping["observation_mapping_rules"]), "PHASE2A_MAPPING_RULE_EXECUTABLE", mapping["replay_evaluation_id"])

    for name in ("evaluation_run", "termination"):
        for item in objects[name]:
            input_path = ROOT / item["evaluation_input_ref"]
            mapping_path = ROOT / item["replay_evaluation_contract_ref"]
            require(input_path.is_file() and mapping_path.is_file(), "PHASE2A_REFERENCE_MISSING", name)
            require(sha256_path(input_path) == item["evaluation_input_digest"], "PHASE2A_REFERENCE_DIGEST_INVALID", name)
            require(sha256_path(mapping_path) == item["replay_evaluation_contract_digest"], "PHASE2A_REFERENCE_DIGEST_INVALID", name)


def validate_readiness(objects: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    for envelope in objects["observation"]:
        validate_synthetic_observation(envelope)

    validate_reference_integrity(objects)

    for replay in objects["replay"]:
        policy = replay["execution_policy"]
        require(policy["manual_start_required"] is True, "PHASE2A_MANUAL_START_REQUIRED", replay["replay_id"])
        require(bool(replay["operator_ref"]) and bool(replay["stop_authority_ref"]), "PHASE2A_STOP_AUTHORITY_REQUIRED", replay["replay_id"])
        for field in ("automatic_replay_allowed", "agent_execution_allowed", "tool_execution_allowed", "network_access_allowed", "deployment_action_allowed"):
            require(policy[field] is False, "PHASE2A_EXECUTION_BOUNDARY_OPEN", f"{replay['replay_id']}:{field}")

    for group in ("replay_evaluation", "evaluation_run", "termination"):
        for item in objects[group]:
            require(bool(item["operator_ref"]) and bool(item["stop_authority_ref"]), "PHASE2A_STOP_AUTHORITY_REQUIRED", group)

    completed_ids = {item["evaluation_run_id"] for item in objects["evaluation_run"]}
    terminated_ids = {item["evaluation_run_id"] for item in objects["termination"]}
    intersection = completed_ids.intersection(terminated_ids)
    require(not intersection, "PHASE2A_LIFECYCLE_PATH_CONFLICT", ",".join(sorted(intersection)))
    require(len(completed_ids) == len(objects["evaluation_run"]), "PHASE2A_DUPLICATE_COMPLETED_RUN", "duplicate run ID")
    require(len(terminated_ids) == len(objects["termination"]), "PHASE2A_DUPLICATE_TERMINATED_RUN", "duplicate run ID")

    for item in objects["termination"]:
        require(item["evidence_case_produced"] is False, "PHASE2A_FAKE_EVIDENCE", item["termination_id"])
        require(item["evidence_case_ref"] is None and item["evidence_case_digest"] is None, "PHASE2A_FAKE_EVIDENCE", item["termination_id"])
        require(item["truth_boundary"]["partial_result_is_evidence"] is False, "PHASE2A_PARTIAL_RESULT_IS_EVIDENCE", item["termination_id"])

    all_objects = [item for group in objects.values() for item in group]
    boundary_fields = {
        "automatic_decision",
        "automatic_decision_made",
        "deployment_authorized",
        "production_ready",
        "real_agent_executed",
        "real_agent_executed_by_saee",
        "external_tool_executed",
        "network_accessed",
        "customer_data_processed",
        "customer_data_used",
    }
    for item in all_objects:
        require_false_fields(item, boundary_fields, "PHASE2A_BOUNDARY_PROMOTION")

    return {
        "contract_stack_valid": True,
        "frozen_contracts_unchanged": True,
        "source_type": "synthetic_only",
        "customer_data_present": False,
        "raw_prompt_present": False,
        "raw_output_present": False,
        "hidden_reasoning_present": False,
        "network_allowed": False,
        "external_tool_execution_allowed": False,
        "real_agent_execution_allowed": False,
        "external_code_execution_allowed": False,
        "dependency_install_allowed": False,
        "manual_start_required": True,
        "stop_authority_present": True,
        "completed_termination_run_id_intersection": len(intersection),
        "exactly_one_lifecycle_output": True,
        "partial_result_is_evidence": False,
        "automatic_decision": False,
        "deployment_authorized": False,
        "production_ready": False,
    }


def expect_rejection(mutated: dict[str, list[dict[str, Any]]], expected_code: str) -> None:
    try:
        validate_readiness(mutated)
    except Phase2AReadinessError as exc:
        require(exc.code == expected_code, "PHASE2A_NEGATIVE_REASON_MISMATCH", f"{expected_code}!={exc.code}")
    else:
        raise Phase2AReadinessError("PHASE2A_NEGATIVE_ACCEPTED", expected_code)


def main() -> None:
    require(DOC_PATH.is_file(), "PHASE2A_GATE_DOC_MISSING", str(DOC_PATH))
    for path, expected in FROZEN_HASHES.items():
        require(path.is_file(), "PHASE2A_FROZEN_FILE_MISSING", str(path))
        require(sha256_path(path) == expected, "PHASE2A_FROZEN_FILE_CHANGED", str(path))

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "pip"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "PHASE2A_GATE_EXTERNAL_CAPABILITY", "forbidden import")

    objects, validated_count = validate_contract_stack()
    result = validate_readiness(objects)

    negatives: list[tuple[dict[str, list[dict[str, Any]]], str]] = []
    mutation = copy.deepcopy(objects); mutation["observation"][0]["privacy"]["personal_data_included"] = True; negatives.append((mutation, "PHASE2A_PERSONAL_DATA_PRESENT"))
    mutation = copy.deepcopy(objects); mutation["observation"][0]["source"]["raw_content_included"] = True; negatives.append((mutation, "PHASE2A_RAW_CONTENT_PRESENT"))
    mutation = copy.deepcopy(objects); mutation["observation"][0]["truth_boundary"]["network_accessed"] = True; negatives.append((mutation, "PHASE2A_NETWORK_ALLOWED"))
    mutation = copy.deepcopy(objects); mutation["replay"][0]["execution_policy"]["agent_execution_allowed"] = True; negatives.append((mutation, "PHASE2A_EXECUTION_BOUNDARY_OPEN"))
    mutation = copy.deepcopy(objects); mutation["replay"][0]["execution_policy"]["manual_start_required"] = False; negatives.append((mutation, "PHASE2A_MANUAL_START_REQUIRED"))
    mutation = copy.deepcopy(objects); mutation["replay_evaluation"][0]["observation_mapping_rules"][0]["executable"] = True; negatives.append((mutation, "PHASE2A_MAPPING_RULE_EXECUTABLE"))
    mutation = copy.deepcopy(objects); mutation["termination"][0]["evaluation_run_id"] = mutation["evaluation_run"][0]["evaluation_run_id"]; negatives.append((mutation, "PHASE2A_LIFECYCLE_PATH_CONFLICT"))
    mutation = copy.deepcopy(objects); mutation["termination"][0]["truth_boundary"]["partial_result_is_evidence"] = True; negatives.append((mutation, "PHASE2A_PARTIAL_RESULT_IS_EVIDENCE"))
    mutation = copy.deepcopy(objects); mutation["evaluation_run"][0]["truth_boundary"]["deployment_authorized"] = True; negatives.append((mutation, "PHASE2A_BOUNDARY_PROMOTION"))
    mutation = copy.deepcopy(objects); mutation["evaluation_run"][0]["truth_boundary"]["production_ready"] = True; negatives.append((mutation, "PHASE2A_BOUNDARY_PROMOTION"))
    for mutated, expected_code in negatives:
        expect_rejection(mutated, expected_code)

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_readiness(objects)
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "PHASE2A_NON_DETERMINISTIC_GATE", "result changed")

    print("SAEE_PHASE2A_READINESS_GATE: PASS")
    print("gate_result=PHASE2A_GATE_PASS")
    print(f"contract_objects_validated={validated_count}/20")
    print("contract_stack_valid=true")
    print("frozen_contracts_unchanged=true")
    print("source_type=synthetic_only")
    print("customer_data_present=false")
    print("raw_prompt_present=false")
    print("raw_output_present=false")
    print("hidden_reasoning_present=false")
    print("network_allowed=false")
    print("external_tool_execution_allowed=false")
    print("real_agent_execution_allowed=false")
    print("external_code_execution_allowed=false")
    print("dependency_install_allowed=false")
    print("manual_start_required=true")
    print("stop_authority_present=true")
    print("completed_termination_run_id_intersection=0")
    print("exactly_one_lifecycle_output=true")
    print("partial_result_is_evidence=false")
    print("automatic_decision=false")
    print("deployment_authorized=false")
    print("production_ready=false")
    print("negative_gate_cases=10/10")
    print("deterministic_runs=5/5")
    print("synthetic_offline_replay_executed=false")
    print("phase2a_execution_authorized_by_this_script=false")
    print("phase2_real_agent_data=HOLD")


if __name__ == "__main__":
    main()
