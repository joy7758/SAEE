#!/usr/bin/env python3
"""Run the fixed, offline, synthetic-only SAEE Phase 2A pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MAPPING_DIRECTORY = ROOT / "agent-interface/architecture/examples/replay-evaluation"
RUN_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json"
TERMINATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json"

ALLOWED_PROFILES = {
    "synthetic-replay-evaluation.json": {
        "slug": "baseline",
        "criteria_ref": "criteria:saee-phase2a-baseline-stability",
        "started_at": "2026-07-11T19:00:00Z",
        "completed_at": "2026-07-11T19:00:01Z",
        "terminated_at": "2026-07-11T19:00:30Z",
    },
    "transformed-replay-evaluation.json": {
        "slug": "tool-failure",
        "criteria_ref": "criteria:saee-phase2a-tool-failure",
        "started_at": "2026-07-11T19:10:00Z",
        "completed_at": "2026-07-11T19:10:01Z",
        "terminated_at": "2026-07-11T19:10:30Z",
    },
    "consent-bound-replay-evaluation.json": {
        "slug": "instruction-conflict",
        "criteria_ref": "criteria:saee-phase2a-instruction-conflict",
        "started_at": "2026-07-11T19:20:00Z",
        "completed_at": "2026-07-11T19:20:01Z",
        "terminated_at": "2026-07-11T19:20:30Z",
    },
}

ALLOWED_LIFECYCLES = {"completed", "manual_abort", "runtime_failed", "input_rejected"}


class Phase2APipelineError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise Phase2APipelineError(code, detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_readiness_gate() -> dict[str, Any]:
    from scripts.saee_phase2a_readiness_gate import FROZEN_HASHES, validate_contract_stack, validate_readiness

    for path, digest in FROZEN_HASHES.items():
        require(path.is_file(), "PHASE2A_FROZEN_FILE_MISSING", str(path))
        require(sha256_path(path) == digest, "PHASE2A_FROZEN_FILE_CHANGED", str(path))
    objects, validated_count = validate_contract_stack()
    result = validate_readiness(objects)
    require(result["contract_stack_valid"] is True, "PHASE2A_GATE_NOT_PASSED", "contract stack")
    require(validated_count == 20, "PHASE2A_GATE_NOT_PASSED", "object count")
    return result


def resolve_allowed_mapping(path: Path) -> tuple[Path, dict[str, Any]]:
    resolved = path.resolve()
    try:
        resolved.relative_to(MAPPING_DIRECTORY.resolve())
    except ValueError as exc:
        raise Phase2APipelineError("PHASE2A_INPUT_OUTSIDE_ALLOWLIST", str(path)) from exc
    require(resolved.parent == MAPPING_DIRECTORY.resolve(), "PHASE2A_INPUT_OUTSIDE_ALLOWLIST", str(path))
    require(resolved.name in ALLOWED_PROFILES, "PHASE2A_INPUT_NOT_ALLOWLISTED", resolved.name)
    require(resolved.is_file(), "PHASE2A_INPUT_MISSING", str(path))
    return resolved, ALLOWED_PROFILES[resolved.name]


def validate_pipeline_input(mapping: dict[str, Any], mapping_path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    require(mapping.get("contract_status") == "local_synthetic_mapping_contract_only", "PHASE2A_MAPPING_SCOPE_INVALID", str(mapping_path))
    require(bool(mapping.get("operator_ref")) and bool(mapping.get("stop_authority_ref")), "PHASE2A_HUMAN_CONTROL_MISSING", str(mapping_path))
    require(all(rule.get("deterministic") is True for rule in mapping["observation_mapping_rules"]), "PHASE2A_MAPPING_NOT_DETERMINISTIC", str(mapping_path))
    require(all(rule.get("executable") is False for rule in mapping["observation_mapping_rules"]), "PHASE2A_MAPPING_RULE_EXECUTABLE", str(mapping_path))
    boundary = mapping["truth_boundary"]
    for field in ("replay_executed", "mapping_executed", "real_agent_executed", "customer_data_processed", "automatic_decision", "deployment_authorized", "production_ready"):
        require(boundary[field] is False, "PHASE2A_INPUT_BOUNDARY_PROMOTED", field)

    input_path = (ROOT / mapping["evaluation_input_ref"]).resolve()
    allowed_input_directory = (ROOT / "agent-interface/architecture/examples/phase1_5_cases").resolve()
    try:
        input_path.relative_to(allowed_input_directory)
    except ValueError as exc:
        raise Phase2APipelineError("PHASE2A_EVALUATION_INPUT_OUTSIDE_ALLOWLIST", str(input_path)) from exc
    require(input_path.is_file(), "PHASE2A_EVALUATION_INPUT_MISSING", str(input_path))
    require(sha256_path(input_path) == mapping["evaluation_input_digest"], "PHASE2A_EVALUATION_INPUT_DIGEST_INVALID", str(input_path))

    replay_path = (ROOT / mapping["replay_contract_ref"]).resolve()
    allowed_replay_directory = (ROOT / "agent-interface/architecture/examples/replay").resolve()
    try:
        replay_path.relative_to(allowed_replay_directory)
    except ValueError as exc:
        raise Phase2APipelineError("PHASE2A_REPLAY_OUTSIDE_ALLOWLIST", str(replay_path)) from exc
    require(replay_path.is_file(), "PHASE2A_REPLAY_MISSING", str(replay_path))
    require(sha256_path(replay_path) == mapping["replay_contract_digest"], "PHASE2A_REPLAY_DIGEST_INVALID", str(replay_path))
    replay = load_json(replay_path)
    policy = replay["execution_policy"]
    require(policy["manual_start_required"] is True, "PHASE2A_MANUAL_START_REQUIRED", replay["replay_id"])
    for field in ("automatic_replay_allowed", "agent_execution_allowed", "tool_execution_allowed", "network_access_allowed", "deployment_action_allowed"):
        require(policy[field] is False, "PHASE2A_REPLAY_BOUNDARY_OPEN", f"{replay['replay_id']}:{field}")
    require(replay["consent_status"] == "synthetic_declared_only", "PHASE2A_NON_SYNTHETIC_CONSENT", replay["replay_id"])
    require(replay["data_use_permission_status"] == "synthetic_declared_only", "PHASE2A_NON_SYNTHETIC_PERMISSION", replay["replay_id"])
    return input_path, load_json(input_path), replay


def lineage_edges_for_completed(
    run_id: str,
    result_ref: str,
    case_id: str,
    replay_evaluation_id: str,
) -> list[dict[str, str]]:
    return [
        {"edge_id": f"phase2a-lineage:{run_id}:mapping-run", "from_type": "replay_evaluation_contract", "from_ref": replay_evaluation_id, "to_type": "evaluation_run", "to_ref": run_id, "relationship": "governs"},
        {"edge_id": f"phase2a-lineage:{run_id}:input-run", "from_type": "evaluation_input", "from_ref": case_id, "to_type": "evaluation_run", "to_ref": run_id, "relationship": "consumed_by"},
        {"edge_id": f"phase2a-lineage:{run_id}:run-result", "from_type": "evaluation_run", "from_ref": run_id, "to_type": "evaluation_result", "to_ref": result_ref, "relationship": "produces"},
        {"edge_id": f"phase2a-lineage:{run_id}:result-evidence", "from_type": "evaluation_result", "from_ref": result_ref, "to_type": "derived_evidence_case", "to_ref": case_id, "relationship": "binds_to"},
        {"edge_id": f"phase2a-lineage:{run_id}:evidence-run", "from_type": "derived_evidence_case", "from_ref": case_id, "to_type": "evaluation_run", "to_ref": run_id, "relationship": "reverse_lookup_anchor"},
    ]


def build_completed_output(
    mapping: dict[str, Any],
    mapping_path: Path,
    input_path: Path,
    profile: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    from saee_backend.services.saee_evidence_case import run_assurance_case_path

    result = run_assurance_case_path(input_path)
    evidence_case = result["evidence_case_object"]
    case_id = evidence_case["identity"]["case_id"]
    slug = profile["slug"]
    run_id = f"evaluation-run:phase2a-{slug}-completed"
    result_ref = f"evaluation-result:phase2a-{slug}-completed"
    run = {
        "saee_evaluation_run_contract_v0_1": True,
        "schema_version": "0.1.0",
        "evaluation_run_id": run_id,
        "evaluation_input_ref": mapping["evaluation_input_ref"],
        "evaluation_input_digest": mapping["evaluation_input_digest"],
        "replay_evaluation_contract_ref": str(mapping_path.relative_to(ROOT)),
        "replay_evaluation_contract_digest": sha256_path(mapping_path),
        "evaluator_ref": "evaluator:saee-phase2a-fixed-synthetic-case-builder",
        "evaluator_version": "0.1.0",
        "grader_ref": "grader:saee-evidence-adequacy-local",
        "grader_version": "0.1.0",
        "criteria_ref": profile["criteria_ref"],
        "criteria_version": "0.1.0",
        "run_started_at": profile["started_at"],
        "run_completed_at": profile["completed_at"],
        "run_status": "synthetic_recorded_completed",
        "result_ref": result_ref,
        "result_digest": canonical_digest(result),
        "evidence_case_ref": case_id,
        "evidence_case_digest": canonical_digest(evidence_case),
        "operator_ref": mapping["operator_ref"],
        "stop_authority_ref": mapping["stop_authority_ref"],
        "execution_environment_ref": "environment:saee-phase2a-fixed-offline-v0.1",
        "lineage_edges": lineage_edges_for_completed(run_id, result_ref, case_id, mapping["replay_evaluation_id"]),
        "truth_boundary": {
            "contract_only": True,
            "synthetic_run_record": True,
            "real_evaluator_runtime_executed": False,
            "real_agent_executed": False,
            "external_tool_executed": False,
            "network_accessed": False,
            "customer_data_processed": False,
            "evaluator_provenance_independently_verified": False,
            "grader_provenance_independently_verified": False,
            "criteria_provenance_independently_verified": False,
            "result_authenticity_independently_verified": False,
            "evidence_case_authenticity_independently_verified": False,
            "risk_probability_measured": False,
            "automatic_decision": False,
            "deployment_authorized": False,
            "architecture_implemented": False,
            "risk_model_implemented": False,
            "external_validation_completed": False,
            "customer_validated": False,
            "production_ready": False,
        },
    }
    Draft202012Validator(load_json(RUN_SCHEMA_PATH), format_checker=FormatChecker()).validate(run)
    return run, evidence_case


def termination_profile(lifecycle: str) -> tuple[str, bool, str, str]:
    if lifecycle == "manual_abort":
        return "manual_abort", True, "MANUAL_ABORT", "Synthetic manual stop was requested before evaluation completion."
    if lifecycle == "runtime_failed":
        return "runtime_failed", True, "RUNTIME_ERROR", "Synthetic local lifecycle was interrupted before producing a completed result."
    if lifecycle == "input_rejected":
        return "input_rejected", False, "INPUT_POLICY_REJECTED", "Synthetic input was rejected by the fixed Phase 2A policy before start."
    raise Phase2APipelineError("PHASE2A_LIFECYCLE_INVALID", lifecycle)


def lineage_edges_for_termination(
    run_id: str,
    termination_id: str,
    case_id: str,
    replay_evaluation_id: str,
) -> list[dict[str, str]]:
    return [
        {"edge_id": f"phase2a-termination-lineage:{run_id}:mapping-run", "from_type": "replay_evaluation_contract", "from_ref": replay_evaluation_id, "to_type": "evaluation_run", "to_ref": run_id, "relationship": "governs"},
        {"edge_id": f"phase2a-termination-lineage:{run_id}:input-run", "from_type": "evaluation_input", "from_ref": case_id, "to_type": "evaluation_run", "to_ref": run_id, "relationship": "consumed_or_rejected_by"},
        {"edge_id": f"phase2a-termination-lineage:{run_id}:run-termination", "from_type": "evaluation_run", "from_ref": run_id, "to_type": "run_termination", "to_ref": termination_id, "relationship": "terminated_by"},
        {"edge_id": f"phase2a-termination-lineage:{run_id}:termination-run", "from_type": "run_termination", "from_ref": termination_id, "to_type": "evaluation_run", "to_ref": run_id, "relationship": "reverse_lookup_anchor"},
    ]


def build_termination_output(
    lifecycle: str,
    mapping: dict[str, Any],
    mapping_path: Path,
    evaluation_input: dict[str, Any],
    profile: dict[str, str],
) -> dict[str, Any]:
    status, run_started, reason_code, reason = termination_profile(lifecycle)
    slug = profile["slug"]
    run_id = f"evaluation-run:phase2a-{slug}-{status}"
    termination_id = f"termination:phase2a-{slug}-{status}"
    case_id = evaluation_input["case_id"]
    termination = {
        "saee_evaluation_run_termination_contract_v0_1": True,
        "schema_version": "0.1.0",
        "termination_id": termination_id,
        "evaluation_run_id": run_id,
        "evaluation_input_ref": mapping["evaluation_input_ref"],
        "evaluation_input_digest": mapping["evaluation_input_digest"],
        "replay_evaluation_contract_ref": str(mapping_path.relative_to(ROOT)),
        "replay_evaluation_contract_digest": sha256_path(mapping_path),
        "termination_status": status,
        "run_started": run_started,
        "run_completed": False,
        "terminated_at": profile["terminated_at"],
        "termination_reason_code": reason_code,
        "termination_reason": reason,
        "operator_ref": mapping["operator_ref"],
        "stop_authority_ref": mapping["stop_authority_ref"],
        "partial_result_present": False,
        "partial_result_ref": None,
        "partial_result_digest": None,
        "evidence_case_produced": False,
        "evidence_case_ref": None,
        "evidence_case_digest": None,
        "lineage_edges": lineage_edges_for_termination(run_id, termination_id, case_id, mapping["replay_evaluation_id"]),
        "truth_boundary": {
            "contract_only": True,
            "synthetic_termination_record": True,
            "real_evaluator_runtime_executed": False,
            "real_agent_executed": False,
            "external_tool_executed": False,
            "network_accessed": False,
            "customer_data_processed": False,
            "partial_result_is_evidence": False,
            "partial_result_authenticity_independently_verified": False,
            "evidence_case_produced": False,
            "risk_probability_measured": False,
            "automatic_decision": False,
            "deployment_authorized": False,
            "architecture_implemented": False,
            "risk_model_implemented": False,
            "external_validation_completed": False,
            "customer_validated": False,
            "production_ready": False,
        },
    }
    Draft202012Validator(load_json(TERMINATION_SCHEMA_PATH), format_checker=FormatChecker()).validate(termination)
    return termination


def run_pipeline(input_path: Path, lifecycle: str = "completed") -> dict[str, Any]:
    require(lifecycle in ALLOWED_LIFECYCLES, "PHASE2A_LIFECYCLE_INVALID", lifecycle)
    gate_result = run_readiness_gate()
    mapping_path, profile = resolve_allowed_mapping(input_path)
    mapping = load_json(mapping_path)
    evaluation_input_path, evaluation_input, _replay = validate_pipeline_input(mapping, mapping_path)

    completed = lifecycle == "completed"
    if completed:
        run, evidence_case = build_completed_output(mapping, mapping_path, evaluation_input_path, profile)
        termination = None
    else:
        run = None
        evidence_case = None
        termination = build_termination_output(lifecycle, mapping, mapping_path, evaluation_input, profile)

    report = {
        "saee_phase2a_synthetic_execution_report_v0_1": True,
        "execution_id": f"phase2a-execution:{profile['slug']}:{lifecycle}",
        "execution_mode": "synthetic_offline_fixed_evaluation_input_pipeline",
        "gate_result": "PHASE2A_GATE_PASS",
        "source_replay_evaluation_ref": str(mapping_path.relative_to(ROOT)),
        "source_replay_evaluation_digest": sha256_path(mapping_path),
        "source_evaluation_input_ref": mapping["evaluation_input_ref"],
        "source_evaluation_input_digest": mapping["evaluation_input_digest"],
        "declared_mapping_rules_executed_as_code": False,
        "synthetic_replay_contract_validated": True,
        "synthetic_metadata_reconstruction_applied": False,
        "synthetic_offline_replay_executed": False,
        "preexisting_evaluation_input_loaded": True,
        "fixed_evaluation_input_pipeline_executed": lifecycle == "completed",
        "fixed_internal_transform_applied": lifecycle == "completed",
        "local_synthetic_case_builder_applied": lifecycle == "completed",
        "lifecycle_output": {
            "completed": completed,
            "terminated": not completed,
            "evaluation_run_contract": run,
            "evidence_case": evidence_case,
            "termination_contract": termination,
        },
        "truth_boundary": {
            "real_agent_executed": False,
            "real_evaluator_runtime_executed": False,
            "external_tool_executed": False,
            "network_accessed": False,
            "external_code_executed": False,
            "dependency_installed": False,
            "customer_data_processed": False,
            "risk_probability_measured": False,
            "automatic_decision": False,
            "deployment_authorized": False,
            "customer_validated": False,
            "production_ready": False,
        },
    }
    require(report["lifecycle_output"]["completed"] != report["lifecycle_output"]["terminated"], "PHASE2A_LIFECYCLE_NOT_EXCLUSIVE", lifecycle)
    require(gate_result["production_ready"] is False, "PHASE2A_GATE_BOUNDARY_PROMOTED", "production_ready")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the fixed local synthetic SAEE Phase 2A pipeline.")
    parser.add_argument("--input", required=True, type=Path, help="Allowlisted Replay Evaluation Contract path.")
    parser.add_argument("--lifecycle", choices=sorted(ALLOWED_LIFECYCLES), default="completed")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_pipeline(args.input, args.lifecycle)
    except (Phase2APipelineError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
