#!/usr/bin/env python3
"""Offline integrity gate for SAEE Phase 1.98 termination records."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/run-termination"
EVALUATION_RUN_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json"
REPLAY_EVALUATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json"
REPLAY_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
EVIDENCE_CASE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
FINAL_ARCHITECTURE_PATH = ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT_RECOMMENDATION_GATE.md"

FINAL_ARCHITECTURE_SHA256 = "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3"
EVIDENCE_CASE_SCHEMA_SHA256 = "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e"
OBSERVATION_SCHEMA_SHA256 = "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2"
REPLAY_SCHEMA_SHA256 = "aa7fcdcf7908a1f6f2bcd530ba7a8edfab1aa41d32fa964c422680dd36f61db1"
REPLAY_EVALUATION_SCHEMA_SHA256 = "4c2e9c483a26b477163a14296bd5d505b8176cf5c4c242c4c9e2aa46d8aeb30d"
EVALUATION_RUN_SCHEMA_SHA256 = "80847a94737a88f84a2f4f4c0b266b7b230c177ec01950375aa628bafe4b4a6d"

EXPECTED_EXAMPLES = {
    "manual-abort-termination.json": "manual_abort",
    "runtime-failure-termination.json": "runtime_failed",
    "input-rejected-termination.json": "input_rejected",
}

FALSE_BOUNDARIES = (
    "real_evaluator_runtime_executed",
    "real_agent_executed",
    "external_tool_executed",
    "network_accessed",
    "customer_data_processed",
    "partial_result_is_evidence",
    "partial_result_authenticity_independently_verified",
    "evidence_case_produced",
    "risk_probability_measured",
    "automatic_decision",
    "deployment_authorized",
    "architecture_implemented",
    "risk_model_implemented",
    "external_validation_completed",
    "customer_validated",
    "production_ready",
)


class TerminationContractError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise TerminationContractError("TERMINATION_CHECK_FAILED", detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def assert_strict_objects(node: Any, location: str = "root") -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            require(node.get("additionalProperties") is False, f"open object at {location}")
        for key, value in node.items():
            assert_strict_objects(value, f"{location}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            assert_strict_objects(value, f"{location}/{index}")


def resolve_allowlisted(ref: str, directory: Path, code: str) -> Path:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(directory.resolve())
    except ValueError as exc:
        raise TerminationContractError(code, ref) from exc
    if not path.is_file():
        raise TerminationContractError(code, ref)
    return path


def required_edges(record: dict[str, Any], replay_evaluation_id: str, case_id: str) -> set[tuple[str, str, str, str, str]]:
    run_id = record["evaluation_run_id"]
    termination_id = record["termination_id"]
    required = {
        ("replay_evaluation_contract", replay_evaluation_id, "evaluation_run", run_id, "governs"),
        ("evaluation_input", case_id, "evaluation_run", run_id, "consumed_or_rejected_by"),
        ("evaluation_run", run_id, "run_termination", termination_id, "terminated_by"),
        ("run_termination", termination_id, "evaluation_run", run_id, "reverse_lookup_anchor"),
    }
    if record["partial_result_present"]:
        partial_ref = record["partial_result_ref"]
        required.update({
            ("evaluation_run", run_id, "partial_result", partial_ref, "produced_partial"),
            ("partial_result", partial_ref, "run_termination", termination_id, "captured_by"),
        })
    return required


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    input_path = resolve_allowlisted(
        record["evaluation_input_ref"],
        ROOT / "agent-interface/architecture/examples/phase1_5_cases",
        "TERMINATION_INPUT_MISSING",
    )
    if sha256_path(input_path) != record["evaluation_input_digest"]:
        raise TerminationContractError("TERMINATION_INPUT_DIGEST_INVALID", record["termination_id"])

    replay_evaluation_path = resolve_allowlisted(
        record["replay_evaluation_contract_ref"],
        ROOT / "agent-interface/architecture/examples/replay-evaluation",
        "TERMINATION_REPLAY_EVALUATION_MISSING",
    )
    if sha256_path(replay_evaluation_path) != record["replay_evaluation_contract_digest"]:
        raise TerminationContractError("TERMINATION_REPLAY_EVALUATION_DIGEST_INVALID", record["termination_id"])

    evaluation_input = json.loads(input_path.read_text(encoding="utf-8"))
    replay_evaluation = json.loads(replay_evaluation_path.read_text(encoding="utf-8"))
    if replay_evaluation["evaluation_input_ref"] != record["evaluation_input_ref"]:
        raise TerminationContractError("TERMINATION_INPUT_LINEAGE_MISMATCH", record["termination_id"])
    if replay_evaluation["evaluation_input_digest"] != record["evaluation_input_digest"]:
        raise TerminationContractError("TERMINATION_INPUT_LINEAGE_MISMATCH", record["termination_id"])

    if not record["stop_authority_ref"]:
        raise TerminationContractError("TERMINATION_STOP_AUTHORITY_REQUIRED", record["termination_id"])
    if record["run_completed"] is not False:
        raise TerminationContractError("TERMINATION_CANNOT_BE_COMPLETED_RUN", record["termination_id"])
    if record["evidence_case_produced"] is not False:
        raise TerminationContractError("TERMINATION_FAKE_EVIDENCE_FORBIDDEN", record["termination_id"])
    if record["evidence_case_ref"] is not None or record["evidence_case_digest"] is not None:
        raise TerminationContractError("TERMINATION_FAKE_EVIDENCE_FORBIDDEN", record["termination_id"])
    if record["partial_result_present"]:
        if not record["partial_result_ref"] or not record["partial_result_digest"]:
            raise TerminationContractError("TERMINATION_PARTIAL_RESULT_UNBOUND", record["termination_id"])
    elif record["partial_result_ref"] is not None or record["partial_result_digest"] is not None:
        raise TerminationContractError("TERMINATION_PARTIAL_RESULT_UNBOUND", record["termination_id"])

    actual_edges = {
        (edge["from_type"], edge["from_ref"], edge["to_type"], edge["to_ref"], edge["relationship"])
        for edge in record["lineage_edges"]
    }
    if not required_edges(record, replay_evaluation["replay_evaluation_id"], evaluation_input["case_id"]).issubset(actual_edges):
        raise TerminationContractError("TERMINATION_LINEAGE_INCOMPLETE", record["termination_id"])

    boundary = record["truth_boundary"]
    require(boundary["contract_only"] is True, f"{record['termination_id']}: contract marker")
    require(boundary["synthetic_termination_record"] is True, f"{record['termination_id']}: synthetic record marker")
    require(all(boundary[field] is False for field in FALSE_BOUNDARIES), f"{record['termination_id']}: truth boundary")

    return {
        "termination_id": record["termination_id"],
        "evaluation_run_id": record["evaluation_run_id"],
        "termination_status": record["termination_status"],
        "run_started": record["run_started"],
        "partial_result_present": record["partial_result_present"],
        "partial_result_is_evidence": False,
        "evidence_case_produced": False,
        "lineage_complete": True,
        "deployment_authorized": False,
    }


def assert_semantic_negative(record: dict[str, Any], expected_code: str) -> None:
    try:
        validate_record(record)
    except TerminationContractError as exc:
        require(exc.code == expected_code, f"expected {expected_code}, got {exc.code}")
    else:
        raise TerminationContractError("TERMINATION_NEGATIVE_ACCEPTED", expected_code)


def main() -> None:
    frozen = {
        FINAL_ARCHITECTURE_PATH: FINAL_ARCHITECTURE_SHA256,
        EVIDENCE_CASE_SCHEMA_PATH: EVIDENCE_CASE_SCHEMA_SHA256,
        OBSERVATION_SCHEMA_PATH: OBSERVATION_SCHEMA_SHA256,
        REPLAY_SCHEMA_PATH: REPLAY_SCHEMA_SHA256,
        REPLAY_EVALUATION_SCHEMA_PATH: REPLAY_EVALUATION_SCHEMA_SHA256,
        EVALUATION_RUN_SCHEMA_PATH: EVALUATION_RUN_SCHEMA_SHA256,
    }
    for path in (SCHEMA_PATH, EXAMPLE_DIRECTORY, DOC_PATH, GATE_PATH, *frozen):
        require(path.exists(), f"missing required path: {path}")
    for path, digest in frozen.items():
        require(sha256_path(path) == digest, f"frozen file changed: {path.name}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    replay_evaluation_schema = json.loads(REPLAY_EVALUATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    evidence_case_schema = json.loads(EVIDENCE_CASE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert_strict_objects(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    replay_evaluation_validator = Draft202012Validator(replay_evaluation_schema, format_checker=FormatChecker())
    evidence_case_validator = Draft202012Validator(evidence_case_schema, format_checker=FormatChecker())

    paths = sorted(EXAMPLE_DIRECTORY.glob("*.json"))
    require({path.name for path in paths} == set(EXPECTED_EXAMPLES), "expected exactly three Phase 1.98 examples")
    records: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(record)
        require(record["termination_status"] == EXPECTED_EXAMPLES[path.name], f"{path.name}: status")
        replay_evaluation_validator.validate(json.loads((ROOT / record["replay_evaluation_contract_ref"]).read_text(encoding="utf-8")))
        evidence_case_validator.validate(json.loads((ROOT / record["evaluation_input_ref"]).read_text(encoding="utf-8")))
        reports.append(validate_record(record))
        records.append(record)

    require(len({item["termination_id"] for item in records}) == len(records), "duplicate termination ID")
    require(len({item["evaluation_run_id"] for item in records}) == len(records), "duplicate evaluation run ID")
    manual = next(item for item in records if item["termination_status"] == "manual_abort")
    runtime = next(item for item in records if item["termination_status"] == "runtime_failed")
    rejected = next(item for item in records if item["termination_status"] == "input_rejected")
    require(manual["partial_result_present"] is True, "manual abort partial-result coverage")
    require(runtime["partial_result_present"] is False, "runtime failure fake partial result")
    require(rejected["run_started"] is False, "rejected input claims run start")

    base = records[0]
    schema_negatives = []
    no_stop = copy.deepcopy(base); no_stop.pop("stop_authority_ref"); schema_negatives.append(no_stop)
    partial_unbound = copy.deepcopy(base); partial_unbound["partial_result_present"] = True; partial_unbound["partial_result_ref"] = None; schema_negatives.append(partial_unbound)
    fake_partial = copy.deepcopy(runtime); fake_partial["partial_result_ref"] = "partial-result:fake"; schema_negatives.append(fake_partial)
    fake_evidence = copy.deepcopy(base); fake_evidence["evidence_case_produced"] = True; schema_negatives.append(fake_evidence)
    fake_evidence_ref = copy.deepcopy(base); fake_evidence_ref["evidence_case_ref"] = "evidence-case:fake"; schema_negatives.append(fake_evidence_ref)
    deploy = copy.deepcopy(base); deploy["truth_boundary"]["deployment_authorized"] = True; schema_negatives.append(deploy)
    automatic = copy.deepcopy(base); automatic["truth_boundary"]["automatic_decision"] = True; schema_negatives.append(automatic)
    partial_evidence = copy.deepcopy(base); partial_evidence["truth_boundary"]["partial_result_is_evidence"] = True; schema_negatives.append(partial_evidence)
    rejected_started = copy.deepcopy(rejected); rejected_started["run_started"] = True; schema_negatives.append(rejected_started)
    bad_reason = copy.deepcopy(manual); bad_reason["termination_reason_code"] = "RUNTIME_ERROR"; schema_negatives.append(bad_reason)
    require(all(not validator.is_valid(item) for item in schema_negatives), "schema accepted a boundary negative")

    bad_input_digest = copy.deepcopy(base); bad_input_digest["evaluation_input_digest"] = "0" * 64
    assert_semantic_negative(bad_input_digest, "TERMINATION_INPUT_DIGEST_INVALID")
    bad_replay_digest = copy.deepcopy(base); bad_replay_digest["replay_evaluation_contract_digest"] = "0" * 64
    assert_semantic_negative(bad_replay_digest, "TERMINATION_REPLAY_EVALUATION_DIGEST_INVALID")
    bad_lineage = copy.deepcopy(base); bad_lineage["lineage_edges"] = bad_lineage["lineage_edges"][:-1]
    assert_semantic_negative(bad_lineage, "TERMINATION_LINEAGE_INCOMPLETE")
    bad_partial_lineage = copy.deepcopy(manual); bad_partial_lineage["lineage_edges"] = bad_partial_lineage["lineage_edges"][:-1]
    assert_semantic_negative(bad_partial_lineage, "TERMINATION_LINEAGE_INCOMPLETE")
    input_mismatch = copy.deepcopy(base); input_mismatch["evaluation_input_ref"] = runtime["evaluation_input_ref"]; input_mismatch["evaluation_input_digest"] = runtime["evaluation_input_digest"]
    assert_semantic_negative(input_mismatch, "TERMINATION_INPUT_LINEAGE_MISMATCH")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")
    canonical = json.dumps(reports, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = [validate_record(record) for record in records]
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic validation")

    print("SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT_SMOKE: PASS")
    print("schema_valid_cases=3/3")
    print("schema_negative_cases=10/10")
    print("semantic_negative_cases=5/5")
    print("termination_status_coverage=3/3")
    print("termination_lineage_integrity=3/3")
    print("input_digest_integrity=3/3")
    print("replay_evaluation_digest_integrity=3/3")
    print("stop_authority_required=3/3")
    print("no_fake_evidence=3/3")
    print("partial_result_boundary=3/3")
    print("input_rejected_before_start=1/1")
    print("deterministic_runs=5/5")
    print("real_evaluator_runtime_executed=false")
    print("real_agent_executed=false")
    print("network_calls=0")
    print("partial_result_is_evidence=false")
    print("evidence_case_produced=false")
    print("automatic_decision=false")
    print("deployment_authorized=false")
    print("architecture_implemented=false")
    print("risk_model_implemented=false")
    print("customer_data_processed=false")
    print("production_ready=false")
    print("final_architecture_modified=false")
    print("evidence_case_schema_modified=false")
    print("observation_schema_modified=false")
    print("replay_contract_schema_modified=false")
    print("replay_evaluation_schema_modified=false")
    print("evaluation_run_schema_modified=false")


if __name__ == "__main__":
    main()
