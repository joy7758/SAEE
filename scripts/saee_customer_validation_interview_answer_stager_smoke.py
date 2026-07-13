#!/usr/bin/env python3
"""Smoke test the customer-validation interview answer stager."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_customer_validation_interview_answer_stager.py"
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
CARD = EVIDENCE / "customer_validation_live_interview_card"
INPUT = CARD / "customer_validation_live_interview_answers.human_filled.md"
OUT = EVIDENCE / "customer_validation_interview_answer_stager"
SUMMARY = OUT / "customer_validation_interview_answer_stager.local.json"
REPORT = OUT / "customer_validation_interview_answer_stager.md"
INPUT_TEMPLATE = OUT / "customer_validation_live_interview_answers.template.md"
STAGED_DRAFT = OUT / "customer_validation_answers.staged_from_interview.local.md"
BOUNDARY = OUT / "customer_validation_interview_answer_stager_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_GATE.md"
OFFICIAL_ANSWER = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_SMOKE: FAIL " + message)


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


def run_runner() -> str:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    require("SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER: PASS" in result.stdout, "runner did not print PASS")
    return result.stdout


def fixture_answers() -> str:
    return """# real customer interview fixture for local stager smoke only
participant_role: AI 产品负责人
team_type: 初创团队
current_evaluation_method: 目前用人工表格和 LangSmith traces 比较版本。
candidate_count: 3
understanding_score: 4
trust_score: 4
decision_influence_score: 5
repeat_usage_intent_score: 4
time_to_value_minutes: 8
willing_to_test_own_candidates: true
top_objection: 希望看到一次自己的候选方案测试结果。
evidence_missing: 需要更多真实场景样例。
notes: 对方认可部署前长期稳定性比较的价值。
"""


def assert_boundary(payload: dict[str, Any]) -> None:
    for key, value in {
        "customer_validation_interview_answer_stager_v0_1": True,
        "current_goal_blocker": "customer_validated",
        "customer_field_count": 13,
        "official_answer_sheet_written": False,
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
        "blockers_closed_by_stager": 0,
    }.items():
        require(payload.get(key) == value, f"{key} must be {value}")


def main() -> None:
    input_snapshot = INPUT.read_text(encoding="utf-8") if INPUT.exists() else None
    official_snapshot = OFFICIAL_ANSWER.read_text(encoding="utf-8") if OFFICIAL_ANSWER.exists() else None
    try:
        if INPUT.exists():
            INPUT.unlink()
        if STAGED_DRAFT.exists():
            STAGED_DRAFT.unlink()
        run_runner()
        default = read_json(SUMMARY)
        assert_boundary(default)
        require(default.get("status") == "hold_interview_answers_missing_or_incomplete", "default status must hold")
        require(default.get("input_exists") is False, "input must be absent in default smoke")
        require(default.get("staged_draft_written") is False, "default must not write staged draft")
        require(INPUT_TEMPLATE.is_file(), "input template must exist")
        require("participant_role:" in INPUT_TEMPLATE.read_text(encoding="utf-8"), "input template missing participant_role")

        INPUT.write_text(fixture_answers(), encoding="utf-8")
        run_runner()
        staged = read_json(SUMMARY)
        assert_boundary(staged)
        require(staged.get("status") == "ready_staged_draft_from_customer_answers", "fixture must create staged draft")
        require(staged.get("answered_customer_field_count") == 13, "fixture must answer 13 fields")
        require(staged.get("missing_customer_field_count") == 0, "fixture must have no missing customer fields")
        require(staged.get("staged_draft_written") is True, "fixture must write staged draft")
        require(STAGED_DRAFT.is_file(), "staged draft must exist")
        draft = STAGED_DRAFT.read_text(encoding="utf-8")
        for token in [
            "participant_role: AI 产品负责人",
            "current_evaluation_method: 目前用人工表格和 LangSmith traces 比较版本。",
            "no_private_core_disclosed:",
            "This is a staged draft, not official customer validation evidence.",
        ]:
            require(token in draft, f"staged draft missing {token}")
        require(not OFFICIAL_ANSWER.exists() or OFFICIAL_ANSWER.read_text(encoding="utf-8") == official_snapshot, "stager must not modify official answer sheet")

        combined = REPORT.read_text(encoding="utf-8") + "\n" + BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
        for token in [
            "customer_validation_interview_answer_stager_v0_1: true",
            "official_answer_sheet_written: false",
            "customer_validated: false",
            "production_ready: false",
            "private_core_exposed: false",
            "answer: staged_customer_answers_only_no_validation_claim",
        ]:
            require(token in combined, f"docs missing token: {token}")

        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        for token in [
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager.local.json",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_live_interview_answers.template.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_answers.staged_from_interview.local.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager_boundary_audit.md",
            "/docs/strategy/SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_GATE.md",
            "/scripts/saee_customer_validation_interview_answer_stager.py",
            "/scripts/saee_customer_validation_interview_answer_stager_smoke.py",
        ]:
            require(token in llms, f"llms.txt missing {token}")

        entry = read_json(ROOT / "agent-index.json").get("customer_validation_interview_answer_stager_v0_1")
        require(isinstance(entry, dict), "agent-index missing stager entry")
        for key in [
            "status",
            "current_goal_blocker",
            "input_exists",
            "customer_field_count",
            "answered_customer_field_count",
            "missing_customer_field_count",
            "staged_draft_written",
            "official_answer_sheet_written",
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
            "blockers_closed_by_stager",
        ]:
            require(entry.get(key) == read_json(SUMMARY).get(key), f"agent-index {key} mismatch")

        status_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
        )
        for token in [
            "Customer Validation Interview Answer Stager v0.1",
            "customer_validation_interview_answer_stager_v0_1",
            "Current blocker: `customer_validated`",
            "customer_validated=false",
            "production_ready=false",
            "private_core_exposed=false",
        ]:
            require(token in status_text, f"status surfaces missing {token}")
    finally:
        if input_snapshot is None:
            if INPUT.exists():
                INPUT.unlink()
        else:
            INPUT.write_text(input_snapshot, encoding="utf-8")
        if official_snapshot is None:
            if OFFICIAL_ANSWER.exists():
                OFFICIAL_ANSWER.unlink()
        else:
            OFFICIAL_ANSWER.write_text(official_snapshot, encoding="utf-8")
        run_runner()

    print("SAEE_CUSTOMER_VALIDATION_INTERVIEW_ANSWER_STAGER_SMOKE: PASS official_answer_sheet_written=false")


if __name__ == "__main__":
    main()
