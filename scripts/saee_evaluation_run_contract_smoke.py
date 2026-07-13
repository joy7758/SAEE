#!/usr/bin/env python3
"""Offline lineage gate for SAEE Phase 1.97 Evaluation Run Contracts."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/evaluation-run"
REPLAY_EVALUATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json"
REPLAY_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
EVIDENCE_CASE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
FINAL_ARCHITECTURE_PATH = ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT_RECOMMENDATION_GATE.md"

FINAL_ARCHITECTURE_SHA256 = "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3"
EVIDENCE_CASE_SCHEMA_SHA256 = "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e"
OBSERVATION_SCHEMA_SHA256 = "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2"
REPLAY_SCHEMA_SHA256 = "aa7fcdcf7908a1f6f2bcd530ba7a8edfab1aa41d32fa964c422680dd36f61db1"
REPLAY_EVALUATION_SCHEMA_SHA256 = "4c2e9c483a26b477163a14296bd5d505b8176cf5c4c242c4c9e2aa46d8aeb30d"

EXPECTED_EXAMPLES = {
    "synthetic-evaluation-run.json": "synthetic_recorded_completed",
    "failed-evaluation-run.json": "synthetic_recorded_completed_with_evaluation_failure",
    "repeated-evaluation-run.json": "synthetic_recorded_repeat_completed",
}

FALSE_BOUNDARIES = (
    "real_evaluator_runtime_executed",
    "real_agent_executed",
    "external_tool_executed",
    "network_accessed",
    "customer_data_processed",
    "evaluator_provenance_independently_verified",
    "grader_provenance_independently_verified",
    "criteria_provenance_independently_verified",
    "result_authenticity_independently_verified",
    "evidence_case_authenticity_independently_verified",
    "risk_probability_measured",
    "automatic_decision",
    "deployment_authorized",
    "architecture_implemented",
    "risk_model_implemented",
    "external_validation_completed",
    "customer_validated",
    "production_ready",
)


class EvaluationRunContractError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise EvaluationRunContractError("EVALUATION_RUN_CHECK_FAILED", detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)


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
        raise EvaluationRunContractError(code, ref) from exc
    if not path.is_file():
        raise EvaluationRunContractError(code, ref)
    return path


def required_edges(run: dict[str, Any], replay_evaluation_id: str, case_id: str) -> set[tuple[str, str, str, str, str]]:
    run_id = run["evaluation_run_id"]
    result_ref = run["result_ref"]
    evidence_ref = run["evidence_case_ref"]
    return {
        ("replay_evaluation_contract", replay_evaluation_id, "evaluation_run", run_id, "governs"),
        ("evaluation_input", case_id, "evaluation_run", run_id, "consumed_by"),
        ("evaluation_run", run_id, "evaluation_result", result_ref, "produces"),
        ("evaluation_result", result_ref, "derived_evidence_case", evidence_ref, "binds_to"),
        ("derived_evidence_case", evidence_ref, "evaluation_run", run_id, "reverse_lookup_anchor"),
    }


def validate_run(run: dict[str, Any]) -> dict[str, Any]:
    started = parse_time(run["run_started_at"])
    completed = parse_time(run["run_completed_at"])
    if started >= completed:
        raise EvaluationRunContractError("EVALUATION_RUN_WINDOW_INVALID", run["evaluation_run_id"])

    input_path = resolve_allowlisted(
        run["evaluation_input_ref"],
        ROOT / "agent-interface/architecture/examples/phase1_5_cases",
        "EVALUATION_RUN_INPUT_MISSING",
    )
    if sha256_path(input_path) != run["evaluation_input_digest"]:
        raise EvaluationRunContractError("EVALUATION_RUN_INPUT_DIGEST_INVALID", run["evaluation_run_id"])

    replay_evaluation_path = resolve_allowlisted(
        run["replay_evaluation_contract_ref"],
        ROOT / "agent-interface/architecture/examples/replay-evaluation",
        "EVALUATION_RUN_REPLAY_EVALUATION_MISSING",
    )
    if sha256_path(replay_evaluation_path) != run["replay_evaluation_contract_digest"]:
        raise EvaluationRunContractError("EVALUATION_RUN_REPLAY_EVALUATION_DIGEST_INVALID", run["evaluation_run_id"])

    evaluation_input = json.loads(input_path.read_text(encoding="utf-8"))
    replay_evaluation = json.loads(replay_evaluation_path.read_text(encoding="utf-8"))
    if replay_evaluation["evaluation_input_ref"] != run["evaluation_input_ref"]:
        raise EvaluationRunContractError("EVALUATION_RUN_INPUT_LINEAGE_MISMATCH", run["evaluation_run_id"])
    if replay_evaluation["evaluation_input_digest"] != run["evaluation_input_digest"]:
        raise EvaluationRunContractError("EVALUATION_RUN_INPUT_LINEAGE_MISMATCH", run["evaluation_run_id"])

    from saee_backend.services.saee_evidence_case import run_assurance_case_path

    result = run_assurance_case_path(input_path)
    evidence_case = result["evidence_case_object"]
    case_id = evidence_case["identity"]["case_id"]
    if run["evidence_case_ref"] != case_id:
        raise EvaluationRunContractError("EVALUATION_RUN_EVIDENCE_CASE_MISSING", run["evidence_case_ref"])
    if canonical_digest(result) != run["result_digest"]:
        raise EvaluationRunContractError("EVALUATION_RUN_RESULT_DIGEST_INVALID", run["evaluation_run_id"])
    if canonical_digest(evidence_case) != run["evidence_case_digest"]:
        raise EvaluationRunContractError("EVALUATION_RUN_EVIDENCE_DIGEST_INVALID", run["evaluation_run_id"])

    actual_edges = {
        (edge["from_type"], edge["from_ref"], edge["to_type"], edge["to_ref"], edge["relationship"])
        for edge in run["lineage_edges"]
    }
    expected_edges = required_edges(run, replay_evaluation["replay_evaluation_id"], case_id)
    if not expected_edges.issubset(actual_edges):
        raise EvaluationRunContractError("EVALUATION_RUN_LINEAGE_INCOMPLETE", run["evaluation_run_id"])

    for field in ("evaluator_ref", "evaluator_version", "grader_ref", "grader_version", "criteria_ref", "criteria_version"):
        if not run[field]:
            raise EvaluationRunContractError("EVALUATION_RUN_DECLARED_PROVENANCE_MISSING", field)

    boundary = run["truth_boundary"]
    require(boundary["contract_only"] is True, f"{run['evaluation_run_id']}: contract marker")
    require(boundary["synthetic_run_record"] is True, f"{run['evaluation_run_id']}: synthetic record marker")
    require(all(boundary[field] is False for field in FALSE_BOUNDARIES), f"{run['evaluation_run_id']}: truth boundary")

    return {
        "evaluation_run_id": run["evaluation_run_id"],
        "evaluation_input_id": evaluation_input["case_id"],
        "replay_evaluation_id": replay_evaluation["replay_evaluation_id"],
        "evidence_case_id": case_id,
        "run_status": run["run_status"],
        "declared_evaluator_version": run["evaluator_version"],
        "declared_grader_version": run["grader_version"],
        "declared_criteria_version": run["criteria_version"],
        "lineage_complete": True,
        "real_evaluator_runtime_executed": False,
        "real_agent_executed": False,
        "deployment_authorized": False,
    }


def assert_semantic_negative(run: dict[str, Any], expected_code: str) -> None:
    try:
        validate_run(run)
    except EvaluationRunContractError as exc:
        require(exc.code == expected_code, f"expected {expected_code}, got {exc.code}")
    else:
        raise EvaluationRunContractError("EVALUATION_RUN_NEGATIVE_ACCEPTED", expected_code)


def main() -> None:
    for path in (
        SCHEMA_PATH,
        EXAMPLE_DIRECTORY,
        REPLAY_EVALUATION_SCHEMA_PATH,
        REPLAY_SCHEMA_PATH,
        OBSERVATION_SCHEMA_PATH,
        EVIDENCE_CASE_SCHEMA_PATH,
        FINAL_ARCHITECTURE_PATH,
        DOC_PATH,
        GATE_PATH,
    ):
        require(path.exists(), f"missing required path: {path}")

    require(sha256_path(FINAL_ARCHITECTURE_PATH) == FINAL_ARCHITECTURE_SHA256, "FINAL_ARCHITECTURE_SPEC changed")
    require(sha256_path(EVIDENCE_CASE_SCHEMA_PATH) == EVIDENCE_CASE_SCHEMA_SHA256, "Evidence Case v0.1 changed")
    require(sha256_path(OBSERVATION_SCHEMA_PATH) == OBSERVATION_SCHEMA_SHA256, "Observation Envelope v0.1 changed")
    require(sha256_path(REPLAY_SCHEMA_PATH) == REPLAY_SCHEMA_SHA256, "Replay Contract v0.1 changed")
    require(sha256_path(REPLAY_EVALUATION_SCHEMA_PATH) == REPLAY_EVALUATION_SCHEMA_SHA256, "Replay Evaluation Contract v0.1 changed")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    replay_evaluation_schema = json.loads(REPLAY_EVALUATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    evidence_case_schema = json.loads(EVIDENCE_CASE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert_strict_objects(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    replay_evaluation_validator = Draft202012Validator(replay_evaluation_schema, format_checker=FormatChecker())
    evidence_case_validator = Draft202012Validator(evidence_case_schema, format_checker=FormatChecker())

    paths = sorted(EXAMPLE_DIRECTORY.glob("*.json"))
    require({path.name for path in paths} == set(EXPECTED_EXAMPLES), "expected exactly three Phase 1.97 examples")
    runs: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for path in paths:
        run = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(run)
        require(run["run_status"] == EXPECTED_EXAMPLES[path.name], f"{path.name}: run status")
        replay_evaluation_validator.validate(json.loads((ROOT / run["replay_evaluation_contract_ref"]).read_text(encoding="utf-8")))
        evidence_case_validator.validate(json.loads((ROOT / run["evaluation_input_ref"]).read_text(encoding="utf-8")))
        reports.append(validate_run(run))
        runs.append(run)

    run_ids = {run["evaluation_run_id"] for run in runs}
    repeated = next(run for run in runs if run["run_status"] == "synthetic_recorded_repeat_completed")
    require(repeated["repeat_of_run_ref"] in run_ids, "repeat source run missing")
    original = next(run for run in runs if run["evaluation_run_id"] == repeated["repeat_of_run_ref"])
    for field in (
        "evaluation_input_ref", "evaluation_input_digest", "replay_evaluation_contract_ref",
        "evaluator_ref", "evaluator_version", "grader_ref", "grader_version",
        "criteria_ref", "criteria_version", "result_digest", "evidence_case_ref", "evidence_case_digest",
    ):
        require(repeated[field] == original[field], f"repeat binding drift: {field}")

    base = runs[0]
    schema_negatives = []
    no_evaluator_version = copy.deepcopy(base); no_evaluator_version.pop("evaluator_version"); schema_negatives.append(no_evaluator_version)
    no_grader_version = copy.deepcopy(base); no_grader_version.pop("grader_version"); schema_negatives.append(no_grader_version)
    no_criteria_version = copy.deepcopy(base); no_criteria_version.pop("criteria_version"); schema_negatives.append(no_criteria_version)
    risk = copy.deepcopy(base); risk["truth_boundary"]["risk_probability_measured"] = True; schema_negatives.append(risk)
    automatic = copy.deepcopy(base); automatic["truth_boundary"]["automatic_decision"] = True; schema_negatives.append(automatic)
    deployment = copy.deepcopy(base); deployment["truth_boundary"]["deployment_authorized"] = True; schema_negatives.append(deployment)
    real_runtime = copy.deepcopy(base); real_runtime["truth_boundary"]["real_evaluator_runtime_executed"] = True; schema_negatives.append(real_runtime)
    extra = copy.deepcopy(base); extra["unexpected"] = True; schema_negatives.append(extra)
    missing_repeat = copy.deepcopy(repeated); missing_repeat.pop("repeat_of_run_ref"); schema_negatives.append(missing_repeat)
    require(all(not validator.is_valid(item) for item in schema_negatives), "schema accepted a boundary negative")

    missing_evidence = copy.deepcopy(base); missing_evidence["evidence_case_ref"] = "evidence-case:missing"
    assert_semantic_negative(missing_evidence, "EVALUATION_RUN_EVIDENCE_CASE_MISSING")
    bad_input_digest = copy.deepcopy(base); bad_input_digest["evaluation_input_digest"] = "0" * 64
    assert_semantic_negative(bad_input_digest, "EVALUATION_RUN_INPUT_DIGEST_INVALID")
    bad_result_digest = copy.deepcopy(base); bad_result_digest["result_digest"] = "0" * 64
    assert_semantic_negative(bad_result_digest, "EVALUATION_RUN_RESULT_DIGEST_INVALID")
    bad_evidence_digest = copy.deepcopy(base); bad_evidence_digest["evidence_case_digest"] = "0" * 64
    assert_semantic_negative(bad_evidence_digest, "EVALUATION_RUN_EVIDENCE_DIGEST_INVALID")
    bad_lineage = copy.deepcopy(base); bad_lineage["lineage_edges"] = bad_lineage["lineage_edges"][:-1]
    assert_semantic_negative(bad_lineage, "EVALUATION_RUN_LINEAGE_INCOMPLETE")
    bad_window = copy.deepcopy(base); bad_window["run_completed_at"] = bad_window["run_started_at"]
    assert_semantic_negative(bad_window, "EVALUATION_RUN_WINDOW_INVALID")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")
    canonical = json.dumps(reports, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated_reports = [validate_run(run) for run in runs]
        require(json.dumps(repeated_reports, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic validation")

    print("SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT_SMOKE: PASS")
    print("schema_valid_cases=3/3")
    print("schema_negative_cases=9/9")
    print("semantic_negative_cases=6/6")
    print("input_digest_integrity=3/3")
    print("replay_evaluation_digest_integrity=3/3")
    print("declared_evaluator_version_binding=3/3")
    print("declared_grader_version_binding=3/3")
    print("declared_criteria_version_binding=3/3")
    print("result_digest_integrity=3/3")
    print("evidence_case_digest_integrity=3/3")
    print("run_lineage_integrity=3/3")
    print("evidence_reverse_lookup=3/3")
    print("repeat_binding_integrity=1/1")
    print("deterministic_runs=5/5")
    print("real_evaluator_runtime_executed=false")
    print("real_agent_executed=false")
    print("network_calls=0")
    print("risk_probability_measured=false")
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


if __name__ == "__main__":
    main()
