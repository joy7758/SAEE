#!/usr/bin/env python3
"""Smoke test the 3-minute customer validation worksheet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet"
SUMMARY = OUT / "customer_validation_3_minute_worksheet.local.json"
WORKSHEET = OUT / "customer_validation_3_minute_worksheet.md"
FIELD_MAP = OUT / "customer_validation_3_minute_field_map.md"
OUTPUT_GUIDE = OUT / "customer_validation_3_minute_output_guide.md"
BOUNDARY = OUT / "customer_validation_3_minute_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_GATE.md"
ANSWER_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
)
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [SUMMARY, WORKSHEET, FIELD_MAP, OUTPUT_GUIDE, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_3_minute_worksheet_v0_1": True,
        "worksheet_type": "plain_chinese_3_minute_customer_validation_capture",
        "status": "ready_for_short_real_external_customer_interview_input",
        "current_goal_blocker": "customer_validated",
        "minimum_question_count": 8,
        "boundary_confirmation_count": 3,
        "required_full_answer_sheet_missing_field_count": 47,
        "full_answer_sheet_still_required": True,
        "current_preflight_status": "hold_human_answer_sheet_missing",
        "ready_for_explicit_apply_request": False,
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
        "blockers_closed_by_worksheet": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(not ANSWER_INPUT.exists(), "3-minute worksheet must not create human-filled answers")
    require(not TARGET_ENTRY.exists(), "3-minute worksheet must not write final session entry")

    worksheet_text = WORKSHEET.read_text(encoding="utf-8")
    for token in [
        "SAEE 3 分钟真实客户验证最小表",
        "这不是完整客户验证证据",
        "`participant_role`",
        "`current_evaluation_method`",
        "`candidate_count`",
        "`understanding_score`",
        "`decision_influence_score`",
        "`willing_to_test_own_candidates`",
        "`no_private_core_disclosed`",
        "`no_production_ready_claim_made`",
        "Short capture only",
    ]:
        require(token in worksheet_text, f"worksheet missing token: {token}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [FIELD_MAP, OUTPUT_GUIDE, BOUNDARY, GATE])
    for token in [
        "customer_validation_3_minute_worksheet_v0_1: true",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_worksheet: 0",
        "answer: ready_for_short_real_external_customer_interview_input",
        "customer_validation_answers.human_filled.md",
    ]:
        require(token in combined, f"worksheet docs missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_field_map.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_output_guide.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_GATE.md",
        "/scripts/saee_customer_validation_3_minute_worksheet.py",
        "/scripts/saee_customer_validation_3_minute_worksheet_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_3_minute_worksheet_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_3_minute_worksheet_v0_1")
    for key in [
        "status",
        "current_goal_blocker",
        "minimum_question_count",
        "boundary_confirmation_count",
        "required_full_answer_sheet_missing_field_count",
        "full_answer_sheet_still_required",
        "target_human_answer_input",
        "current_preflight_status",
        "ready_for_explicit_apply_request",
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
        "blockers_closed_by_worksheet",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "SAEE 3-Minute Customer Validation Worksheet v0.1",
        "customer_validation_3_minute_worksheet_v0_1",
        "Current blocker: `customer_validated`",
        "Full answer sheet still required: `True`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_SMOKE: PASS "
        "questions=8 customer_validated=false"
    )


if __name__ == "__main__":
    main()
