#!/usr/bin/env python3
"""Smoke test the customer-validation answer-to-evidence pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_customer_validation_answer_to_evidence_pipeline.py"
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_answer_to_evidence_pipeline"
SUMMARY = OUT / "customer_validation_answer_to_evidence_pipeline.local.json"
REPORT = OUT / "customer_validation_answer_to_evidence_pipeline.md"
BOUNDARY = OUT / "customer_validation_answer_to_evidence_pipeline_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_GATE.md"
ANSWER_INPUT = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
SESSION_ENTRY = EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json"
IMPORTED_INPUT = EVIDENCE / "customer_validation_evidence_input.human_filled.local.json"
PROCESSOR_OUT = EVIDENCE / "external_customer_validation_post_session_processor"
PROCESSOR_FILES = [
    PROCESSOR_OUT / "external_customer_validation_post_session_processor.local.json",
    PROCESSOR_OUT / "external_customer_validation_post_session_processor.md",
    PROCESSOR_OUT / "BOUNDARY_AUDIT.md",
    PROCESSOR_OUT / "customer_validation_evidence.from_external_session.local.json",
    PROCESSOR_OUT / "customer_validation_approval_input_validation.local.json",
    PROCESSOR_OUT / "production_customer_validation_evidence_readiness.local.json",
    PROCESSOR_OUT / "commercial_go_no_go.from_external_customer_validation.local.json",
]
IMPORT_FILES = [
    EVIDENCE / "external_customer_validation_session_entry_import_summary.local.json",
    EVIDENCE / "external_customer_validation_session_entry_import_report.md",
    EVIDENCE / "external_customer_validation_session_entry_import_boundary_audit.md",
]


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def run_runner(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    require("SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE: PASS" in result.stdout, "runner did not print PASS")
    return result.stdout


def save_files(paths: list[Path]) -> dict[Path, str | None]:
    return {path: path.read_text(encoding="utf-8") if path.exists() else None for path in paths}


def restore_files(snapshot: dict[Path, str | None]) -> None:
    for path, text in snapshot.items():
        if text is None:
            if path.exists():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


def fixture_answer_sheet() -> str:
    review_keys = sorted(read_json(EVIDENCE / "external_customer_validation_session_entry.template.json")["evidence_review"])
    lines = [
        "session_id: ECV-PIPELINE-SMOKE-001",
        "session_date: 2026-07-09",
        "human_reviewer_name: Smoke Human Reviewer",
        "participant_role: AI 产品负责人",
        "team_type: 初创团队",
        "current_evaluation_method: 目前用人工表格比较多个 agent 版本。",
        "candidate_count: 3",
        "understanding_score: 4",
        "trust_score: 4",
        "decision_influence_score: 4",
        "repeat_usage_intent_score: 4",
        "time_to_value_minutes: 8",
        "willing_to_test_own_candidates: true",
        "top_objection: 希望看到更多真实案例。",
        "evidence_missing: 需要一次自己的候选方案复测。",
        "notes: 对方理解长期稳定性比较的价值。",
        "human_source_context: smoke fixture for local pipeline validation only",
        "human_entry_confirmed: true",
        "no_secrets_collected: true",
        "no_production_data_collected: true",
        "no_customer_data_uploaded: true",
        "no_private_core_disclosed: true",
        "no_production_ready_claim_made: true",
    ]
    lines.extend(f"{key}: true" for key in review_keys)
    return "\n".join(lines) + "\n"


def assert_boundary_payload(payload: dict[str, Any]) -> None:
    for key, value in {
        "customer_validation_answer_to_evidence_pipeline_v0_1": True,
        "current_goal_blocker": "customer_validated",
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
        "blockers_closed_by_pipeline": 0,
    }.items():
        require(payload.get(key) == value, f"{key} must be {value}")


def main() -> None:
    mutable_files = [ANSWER_INPUT, SESSION_ENTRY, IMPORTED_INPUT, SUMMARY, REPORT, BOUNDARY, GATE] + PROCESSOR_FILES + IMPORT_FILES
    snapshot = save_files(mutable_files)
    try:
        for path in [ANSWER_INPUT, SESSION_ENTRY, IMPORTED_INPUT]:
            if path.exists():
                path.unlink()
        run_runner()
        payload = read_json(SUMMARY)
        assert_boundary_payload(payload)
        require(payload.get("status") == "hold_human_answer_sheet_missing", "default status must hold missing answer sheet")
        require(payload.get("apply_requested") is False, "default apply_requested must be false")
        require(payload.get("human_answer_input_exists") is False, "default answer input must be absent")

        ANSWER_INPUT.write_text(fixture_answer_sheet(), encoding="utf-8")
        run_runner("--apply")
        applied = read_json(SUMMARY)
        assert_boundary_payload(applied)
        require(applied.get("apply_requested") is True, "apply payload must record apply")
        require(applied.get("converter_session_entry_written") is True, "converter must write session entry for complete fixture")
        require(applied.get("session_entry_exists") is True, "session entry must exist for complete fixture")
        require(applied.get("processor_status") in {
            "processed_customer_validation_evidence_ready_for_go_no_go_review",
            "hold_customer_validation_evidence_not_ready",
        }, "processor must run for complete fixture")

        for path in [ANSWER_INPUT, SESSION_ENTRY, IMPORTED_INPUT]:
            if path.exists():
                path.unlink()
        run_runner()
        restored = read_json(SUMMARY)
        require(restored.get("status") == "hold_human_answer_sheet_missing", "final restored status must hold")

        combined = REPORT.read_text(encoding="utf-8") + "\n" + BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
        for token in [
            "customer_validation_answer_to_evidence_pipeline_v0_1: true",
            "customer_validated: false",
            "production_ready: false",
            "product_launched: false",
            "private_core_exposed: false",
            "blockers_closed_by_pipeline: 0",
            "answer: local_pipeline_ready_explicit_apply_required",
        ]:
            require(token in combined, f"pipeline docs missing token: {token}")

        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        for token in [
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline.local.json",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline_boundary_audit.md",
            "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_GATE.md",
            "/scripts/saee_customer_validation_answer_to_evidence_pipeline.py",
            "/scripts/saee_customer_validation_answer_to_evidence_pipeline_smoke.py",
        ]:
            require(token in llms, f"llms.txt missing {token}")

        entry = read_json(ROOT / "agent-index.json").get("customer_validation_answer_to_evidence_pipeline_v0_1")
        require(isinstance(entry, dict), "agent-index missing pipeline entry")
        for key in [
            "status",
            "current_goal_blocker",
            "human_answer_input_exists",
            "session_entry_exists",
            "apply_requested",
            "preflight_status",
            "converter_status",
            "processor_status",
            "customer_validated",
            "production_ready",
            "product_launched",
            "customer_contacted_by_codex",
            "private_core_exposed",
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
            "external_calls_made",
            "blockers_closed_by_pipeline",
        ]:
            require(entry.get(key) == read_json(SUMMARY).get(key), f"agent-index {key} mismatch")

        status_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
        )
        for token in [
            "Customer Validation Answer-to-Evidence Pipeline v0.1",
            "customer_validation_answer_to_evidence_pipeline_v0_1",
            "Current blocker: `customer_validated`",
            "python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply",
            "customer_validated=false",
            "production_ready=false",
            "private_core_exposed=false",
        ]:
            require(token in status_text, f"status surface missing {token}")
    finally:
        restore_files(snapshot)
        run_runner()

    print("SAEE_CUSTOMER_VALIDATION_ANSWER_TO_EVIDENCE_PIPELINE_SMOKE: PASS customer_validated=false")


if __name__ == "__main__":
    main()
