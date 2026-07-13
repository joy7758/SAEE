#!/usr/bin/env python3
"""Smoke test the 12-question minimum session answer converter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_external_customer_validation_minimum_session_answer_converter.py"
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
BASE = EVIDENCE / "external_customer_validation_minimum_session_answer_converter"
SUMMARY = BASE / "minimum_session_answer_converter.local.json"
REPORT = BASE / "minimum_session_answer_converter.md"
ANSWER_TEMPLATE = BASE / "minimum_session_answers.template.md"
ANSWER_INPUT = BASE / "minimum_session_answers.human_filled.md"
BOUNDARY = BASE / "minimum_session_answer_converter_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_GATE.md"
TARGET_ENTRY = EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json"


def fail(message: str) -> None:
    raise SystemExit("SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def run_runner(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    require(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER: PASS" in result.stdout,
        "runner did not print PASS",
    )
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


def fixture_answers() -> str:
    return """# Local smoke fixture only.
session_id: ECV-MIN-001
session_date: 2026-07-09
human_reviewer_name: Smoke Human Reviewer
human_source_context: smoke fixture for local converter validation only
human_entry_confirmed: true

q01: AI 应用负责人
q02: 自动化工作流团队
q03: 目前用表格和单次追踪人工比较多个 agent 版本。
q04: 3
q05: 4
q06: 4
q07: 5
q08: 5
willing_to_test_own_candidates: true
q09: 8
q10: 部署建议和失败摘要最有价值。
q11: 希望看到更多真实外部案例。
q12: 需要用自己的脱敏候选方案再跑一次。

no_secrets_collected: true
no_production_data_collected: true
no_customer_data_uploaded: true
no_private_core_disclosed: true
no_production_ready_claim_made: true
"""


def assert_boundary(payload: dict[str, Any]) -> None:
    expected = {
        "external_customer_validation_minimum_session_answer_converter_v0_1": True,
        "current_goal_blocker": "customer_validated",
        "minimum_question_count": 12,
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
    snapshot = save_files([ANSWER_INPUT, TARGET_ENTRY, SUMMARY, REPORT, ANSWER_TEMPLATE, BOUNDARY, GATE])
    try:
        for path in [ANSWER_INPUT, TARGET_ENTRY]:
            if path.exists():
                path.unlink()
        run_runner()
        payload = read_json(SUMMARY)
        assert_boundary(payload)
        require(payload["status"] == "hold_minimum_session_answers_missing", "default status must hold missing answers")
        require(payload["human_answer_input_exists"] is False, "default answer input must be absent")
        require(payload["session_entry_written"] is False, "default must not write session entry")

        ANSWER_INPUT.write_text(fixture_answers(), encoding="utf-8")
        run_runner("--apply")
        applied = read_json(SUMMARY)
        assert_boundary(applied)
        require(applied["status"] == "session_entry_written_pending_post_session_processor", "apply status must write session entry")
        require(applied["human_answer_input_exists"] is True, "apply must see answer input")
        require(applied["session_entry_written"] is True, "apply must write session entry")
        entry = read_json(TARGET_ENTRY)
        require(entry["human_entry_confirmed"] is True, "session entry must be confirmed")
        require(entry["session"]["candidate_count"] == 3, "candidate count mapping failed")
        require(entry["session"]["understanding_score"] == 4, "score mapping failed")
        require(entry["session"]["willing_to_test_own_candidates"] is True, "boolean mapping failed")
        for key in [
            "customer_contacted",
            "customer_validated",
            "product_launched",
            "production_ready",
            "private_core_exposed",
            "public_validation_claim_published",
            "testimonial_published",
            "case_study_published",
        ]:
            require(entry.get(key) is False, f"entry {key} must be false")

        for path in [ANSWER_INPUT, TARGET_ENTRY]:
            if path.exists():
                path.unlink()
        run_runner()
        restored = read_json(SUMMARY)
        require(restored["status"] == "hold_minimum_session_answers_missing", "final restored status must hold")

        combined = REPORT.read_text(encoding="utf-8") + "\n" + BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
        for token in [
            "external_customer_validation_minimum_session_answer_converter_v0_1: true",
            "customer_validated: false",
            "production_ready: false",
            "product_launched: false",
            "private_core_exposed: false",
            "blockers_closed_by_converter: 0",
            "answer: conditional",
        ]:
            require(token in combined, "docs missing token: " + token)
        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        for token in [
            "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.local.json",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.template.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter_boundary_audit.md",
            "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_GATE.md",
            "/scripts/saee_external_customer_validation_minimum_session_answer_converter.py",
            "/scripts/saee_external_customer_validation_minimum_session_answer_converter_smoke.py",
        ]:
            require(token in llms, "llms.txt missing token: " + token)
        index_entry = read_json(ROOT / "agent-index.json").get(
            "external_customer_validation_minimum_session_answer_converter_v0_1"
        )
        require(isinstance(index_entry, dict), "agent-index entry missing")
        for key in [
            "status",
            "current_goal_blocker",
            "minimum_question_count",
            "human_answer_input_exists",
            "target_session_entry_exists",
            "session_entry_written",
            "apply_requested",
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
            require(index_entry.get(key) == read_json(SUMMARY).get(key), f"agent-index {key} mismatch")
    finally:
        restore_files(snapshot)
        run_runner()

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_ANSWER_CONVERTER_SMOKE: PASS")


if __name__ == "__main__":
    main()
