#!/usr/bin/env python3
"""Smoke test the customer-validation answer-to-session-entry converter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_customer_validation_answer_to_session_entry_converter.py"
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter"
SUMMARY = OUT / "customer_validation_answer_to_session_entry_converter.local.json"
REPORT = OUT / "customer_validation_answer_to_session_entry_converter.md"
BOUNDARY = OUT / "customer_validation_answer_to_session_entry_converter_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_GATE.md"
ANSWER_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
)
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_SMOKE: FAIL " + message)


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
    require("SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER: PASS" in result.stdout, "runner did not print PASS")
    return result.stdout


def fixture_answer_sheet() -> str:
    review_keys = sorted(read_json(ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.template.json")["evidence_review"])
    lines = [
        "session_id: ECV-SMOKE-001",
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
        "human_source_context: smoke fixture for local converter validation only",
        "human_entry_confirmed: true",
        "no_secrets_collected: true",
        "no_production_data_collected: true",
        "no_customer_data_uploaded: true",
        "no_private_core_disclosed: true",
        "no_production_ready_claim_made: true",
    ]
    lines.extend(f"{key}: true" for key in review_keys)
    return "\n".join(lines) + "\n"


def assert_hold_payload() -> None:
    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_answer_to_session_entry_converter_v0_1": True,
        "converter_type": "local_human_answer_sheet_to_session_entry_json",
        "status": "hold_human_answer_sheet_missing",
        "human_answer_input_exists": False,
        "target_session_entry_exists": False,
        "apply_requested": False,
        "session_entry_written": False,
        "ready_for_importer": False,
        "explicit_apply_required": True,
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
        "blockers_closed_by_converter": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")


def main() -> None:
    original_answer = ANSWER_INPUT.read_text(encoding="utf-8") if ANSWER_INPUT.exists() else None
    original_target = TARGET_ENTRY.read_text(encoding="utf-8") if TARGET_ENTRY.exists() else None
    try:
        if ANSWER_INPUT.exists():
            ANSWER_INPUT.unlink()
        if TARGET_ENTRY.exists():
            TARGET_ENTRY.unlink()
        run_runner()
        for path in [SUMMARY, REPORT, BOUNDARY, GATE]:
            require(path.is_file(), f"missing {path.relative_to(ROOT)}")
        assert_hold_payload()

        ANSWER_INPUT.write_text(fixture_answer_sheet(), encoding="utf-8")
        run_runner("--apply")
        applied = read_json(SUMMARY)
        require(applied.get("status") == "session_entry_written_pending_importer", "apply status must write session entry")
        require(applied.get("session_entry_written") is True, "session entry must be written in fixture apply")
        require(TARGET_ENTRY.exists(), "target session entry must exist after fixture apply")
        target = read_json(TARGET_ENTRY)
        require(target.get("human_entry_confirmed") is True, "target human_entry_confirmed must be true")
        require(target.get("customer_validated") is False, "target must not claim customer validation")
        require(target.get("production_ready") is False, "target must not claim production readiness")
        require(target.get("private_core_exposed") is False, "target must not expose private core")

        ANSWER_INPUT.unlink()
        TARGET_ENTRY.unlink()
        run_runner()
        assert_hold_payload()

        combined = REPORT.read_text(encoding="utf-8") + "\n" + BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
        for token in [
            "customer_validation_answer_to_session_entry_converter_v0_1: true",
            "customer_validated: false",
            "production_ready: false",
            "private_core_exposed: false",
            "blockers_closed_by_converter: 0",
            "answer: local_converter_ready_explicit_apply_required",
        ]:
            require(token in combined, f"docs missing token: {token}")

        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        for token in [
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter.local.json",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter_boundary_audit.md",
            "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_GATE.md",
            "/scripts/saee_customer_validation_answer_to_session_entry_converter.py",
            "/scripts/saee_customer_validation_answer_to_session_entry_converter_smoke.py",
        ]:
            require(token in llms, f"llms.txt missing {token}")

        entry = read_json(ROOT / "agent-index.json").get("customer_validation_answer_to_session_entry_converter_v0_1")
        require(isinstance(entry, dict), "agent-index missing converter entry")
        for key in [
            "status",
            "current_goal_blocker",
            "human_answer_input_exists",
            "target_session_entry_exists",
            "session_entry_written",
            "ready_for_importer",
            "explicit_apply_required",
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
            "blockers_closed_by_converter",
        ]:
            require(entry.get(key) == read_json(SUMMARY).get(key), f"agent-index {key} mismatch")

        status_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
        )
        for token in [
            "Customer Validation Answer-to-Session-Entry Converter v0.1",
            "customer_validation_answer_to_session_entry_converter_v0_1",
            "Current blocker: `customer_validated`",
            "Explicit apply required: `true`",
            "customer_validated=false",
            "production_ready=false",
            "private_core_exposed=false",
        ]:
            require(token in status_text, f"status surface missing {token}")
    finally:
        if original_answer is not None:
            ANSWER_INPUT.write_text(original_answer, encoding="utf-8")
        elif ANSWER_INPUT.exists():
            ANSWER_INPUT.unlink()
        if original_target is not None:
            TARGET_ENTRY.write_text(original_target, encoding="utf-8")
        elif TARGET_ENTRY.exists():
            TARGET_ENTRY.unlink()
        run_runner()

    print("SAEE_CUSTOMER_VALIDATION_ANSWER_TO_SESSION_ENTRY_CONVERTER_SMOKE: PASS customer_validated=false")


if __name__ == "__main__":
    main()
