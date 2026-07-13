#!/usr/bin/env python3
"""Offline boundary and determinism checks for the Phase 2A runner."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNNER_PATH = ROOT / "scripts/saee_phase2a_synthetic_runner.py"
GATE_PATH = ROOT / "scripts/saee_phase2a_readiness_gate.py"
SERVICE_PATH = ROOT / "saee_backend/services/saee_evidence_case.py"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE2A_SYNTHETIC_EXECUTION.md"
MAPPING_DIRECTORY = ROOT / "agent-interface/architecture/examples/replay-evaluation"


class Phase2AExecutionSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise Phase2AExecutionSmokeError(detail)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def assert_exact_lifecycle(report: dict[str, Any]) -> None:
    lifecycle = report["lifecycle_output"]
    require(lifecycle["completed"] != lifecycle["terminated"], "completed/terminated not exclusive")
    if lifecycle["completed"]:
        require(lifecycle["evaluation_run_contract"] is not None, "completed path missing run")
        require(lifecycle["evidence_case"] is not None, "completed path missing evidence")
        require(lifecycle["termination_contract"] is None, "completed path has termination")
    else:
        require(lifecycle["evaluation_run_contract"] is None, "termination path has completed run")
        require(lifecycle["evidence_case"] is None, "termination path has evidence")
        require(lifecycle["termination_contract"] is not None, "termination path missing record")
        termination = lifecycle["termination_contract"]
        require(termination["evidence_case_produced"] is False, "termination produced evidence")
        require(termination["evidence_case_ref"] is None, "termination has evidence ref")
        require(termination["truth_boundary"]["partial_result_is_evidence"] is False, "partial result promoted")


def assert_truth_boundary(report: dict[str, Any]) -> None:
    boundary = report["truth_boundary"]
    for field in (
        "real_agent_executed",
        "real_evaluator_runtime_executed",
        "external_tool_executed",
        "network_accessed",
        "external_code_executed",
        "dependency_installed",
        "customer_data_processed",
        "risk_probability_measured",
        "automatic_decision",
        "deployment_authorized",
        "customer_validated",
        "production_ready",
    ):
        require(boundary[field] is False, f"boundary promoted: {field}")
    require(report["declared_mapping_rules_executed_as_code"] is False, "mapping rule executed as code")


def main() -> None:
    for path in (RUNNER_PATH, GATE_PATH, SERVICE_PATH, DOC_PATH):
        require(path.is_file(), f"missing required file: {path}")

    from scripts.saee_phase2a_readiness_gate import validate_contract_stack, validate_readiness
    from scripts.saee_phase2a_synthetic_runner import (
        Phase2APipelineError,
        run_pipeline,
        validate_pipeline_input,
    )

    objects, validated_count = validate_contract_stack()
    gate_result = validate_readiness(objects)
    require(validated_count == 20 and gate_result["contract_stack_valid"] is True, "readiness gate did not pass")

    synthetic_mapping = MAPPING_DIRECTORY / "synthetic-replay-evaluation.json"
    transformed_mapping = MAPPING_DIRECTORY / "transformed-replay-evaluation.json"
    consent_mapping = MAPPING_DIRECTORY / "consent-bound-replay-evaluation.json"

    completed = run_pipeline(synthetic_mapping, "completed")
    manual_abort = run_pipeline(transformed_mapping, "manual_abort")
    input_rejected = run_pipeline(consent_mapping, "input_rejected")
    runtime_failed = run_pipeline(transformed_mapping, "runtime_failed")
    reports = (completed, manual_abort, input_rejected, runtime_failed)
    for report in reports:
        require(report["gate_result"] == "PHASE2A_GATE_PASS", "runner skipped gate")
        require(report["synthetic_replay_contract_validated"] is True, "replay contract not validated")
        require(report["synthetic_metadata_reconstruction_applied"] is False, "metadata reconstruction overclaimed")
        require(report["synthetic_offline_replay_executed"] is False, "offline replay overclaimed")
        require(report["preexisting_evaluation_input_loaded"] is True, "pre-existing evaluation input not declared")
        assert_exact_lifecycle(report)
        assert_truth_boundary(report)

    require(completed["lifecycle_output"]["completed"] is True, "completed path invalid")
    require(completed["fixed_evaluation_input_pipeline_executed"] is True, "fixed evaluation-input pipeline not executed")
    require(completed["fixed_internal_transform_applied"] is True, "fixed transform not applied")
    require(completed["local_synthetic_case_builder_applied"] is True, "synthetic builder not applied")
    for terminated in (manual_abort, input_rejected, runtime_failed):
        require(terminated["fixed_evaluation_input_pipeline_executed"] is False, "terminated path claimed completed input pipeline")
    require(manual_abort["lifecycle_output"]["terminated"] is True, "manual termination path invalid")
    require(runtime_failed["lifecycle_output"]["termination_contract"]["termination_status"] == "runtime_failed", "runtime failure status")
    require(input_rejected["synthetic_metadata_reconstruction_applied"] is False, "rejected input reconstructed")
    require(input_rejected["lifecycle_output"]["termination_contract"]["run_started"] is False, "rejected input started")

    mapping = json.loads(synthetic_mapping.read_text(encoding="utf-8"))
    executable = copy.deepcopy(mapping)
    executable["observation_mapping_rules"][0]["executable"] = True
    try:
        validate_pipeline_input(executable, synthetic_mapping)
    except Phase2APipelineError as exc:
        require(exc.code == "PHASE2A_MAPPING_RULE_EXECUTABLE", f"unexpected mapping rejection: {exc.code}")
    else:
        raise Phase2AExecutionSmokeError("executable mapping rule accepted")

    promoted = copy.deepcopy(mapping)
    promoted["truth_boundary"]["deployment_authorized"] = True
    try:
        validate_pipeline_input(promoted, synthetic_mapping)
    except Phase2APipelineError as exc:
        require(exc.code == "PHASE2A_INPUT_BOUNDARY_PROMOTED", f"unexpected boundary rejection: {exc.code}")
    else:
        raise Phase2AExecutionSmokeError("deployment-promoted mapping accepted")

    try:
        run_pipeline(ROOT / "agent-interface/architecture/examples/replay/synthetic-replay-case.json", "completed")
    except Phase2APipelineError as exc:
        require(exc.code == "PHASE2A_INPUT_OUTSIDE_ALLOWLIST", f"unexpected allowlist rejection: {exc.code}")
    else:
        raise Phase2AExecutionSmokeError("outside-allowlist input accepted")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "pip"}
    for path in (RUNNER_PATH, Path(__file__), SERVICE_PATH):
        require(not imported_roots(path).intersection(forbidden), f"external capability import: {path}")

    canonical_completed = json.dumps(completed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    canonical_terminated = json.dumps(manual_abort, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(run_pipeline(synthetic_mapping, "completed"), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical_completed, "completed output non-deterministic")
        require(json.dumps(run_pipeline(transformed_mapping, "manual_abort"), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical_terminated, "termination output non-deterministic")

    print("SAEE_PHASE2A_EXECUTION_SMOKE: PASS")
    print("completed_path_valid=true")
    print("termination_path_valid=true")
    print("input_rejected_path_valid=true")
    print("runtime_failed_path_valid=true")
    print("completed_xor_terminated=true")
    print("evidence_only_from_completed=true")
    print("termination_without_evidence=true")
    print("mapping_rules_executed_as_code=false")
    print("synthetic_replay_contract_validated=true")
    print("synthetic_metadata_reconstruction_applied=false")
    print("synthetic_offline_replay_executed=false")
    print("fixed_evaluation_input_pipeline_executed=true")
    print("outside_allowlist_rejected=true")
    print("boundary_promoted_input_rejected=true")
    print("deterministic_runs=5/5")
    print("no_external_execution=true")
    print("network_accessed=false")
    print("real_agent_executed=false")
    print("external_tool_executed=false")
    print("customer_data_processed=false")
    print("automatic_decision=false")
    print("deployment_authorized=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
