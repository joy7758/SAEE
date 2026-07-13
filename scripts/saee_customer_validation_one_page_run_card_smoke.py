#!/usr/bin/env python3
"""Smoke test the one-page customer validation run card."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card"
SUMMARY = OUT / "customer_validation_one_page_run_card.local.json"
CARD = OUT / "customer_validation_one_page_run_card.md"
HTML = OUT / "customer_validation_one_page_run_card.html"
BOUNDARY = OUT / "customer_validation_one_page_run_card_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_GATE.md"
ANSWER_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
)
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, CARD, HTML, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_one_page_run_card_v0_1": True,
        "card_type": "one_page_human_customer_validation_navigation",
        "status": "ready_for_human_external_customer_validation_run",
        "current_goal_blocker": "customer_validated",
        "uses_existing_materials_only": True,
        "new_questions_added": False,
        "human_execution_required": True,
        "human_answer_input_exists": False,
        "target_session_entry_exists": False,
        "current_preflight_status": "hold_human_answer_sheet_missing",
        "ready_for_explicit_apply_request": False,
        "step_count": 6,
        "browser_readable_card_available": True,
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
        "blockers_closed_by_run_card": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(not ANSWER_INPUT.exists(), "run card must not create human-filled answers")
    require(not TARGET_ENTRY.exists(), "run card must not write final session entry")

    card_text = CARD.read_text(encoding="utf-8")
    for token in [
        "SAEE 真实客户验证一页执行卡",
        "`customer_validated`",
        "PARTICIPANT_SCREENING_CHECKLIST.md",
        "INVITATION_MESSAGE_DRAFT.md",
        "CONSENT_AND_BOUNDARY_SCRIPT.md",
        "customer_validation_3_minute_worksheet.md",
        "customer_validation_plain_chinese_worksheet.md",
        "customer_validation_answers.human_filled.md",
        "saee_customer_validation_answer_to_evidence_pipeline.py --apply",
        "external_customer_validation_session_entry_workbench.html",
        "external_customer_validation_session_entry.human_filled.local.json",
        "blockers_closed_by_run_card: 0",
    ]:
        require(token in card_text, f"card missing token: {token}")

    html_text = HTML.read_text(encoding="utf-8")
    for token in [
        "<html lang=\"zh-CN\">",
        "真实客户验证，一页走完",
        "按这 6 步做",
        "最终 JSON 录入入口",
        "必须保存到这里",
        "customer_validated",
        "production_ready",
        "private_core_exposed",
        "external_customer_validation_session_entry_workbench.html",
        "saee_customer_validation_answer_to_evidence_pipeline.py --apply",
        "external_customer_validation_session_entry.human_filled.local.json",
    ]:
        require(token in html_text, f"html missing token: {token}")

    combined = BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
    for token in [
        "customer_validation_one_page_run_card_v0_1: true",
        "uses_existing_materials_only: true",
        "new_questions_added: false",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_run_card: 0",
        "answer: ready_for_human_external_customer_validation_run",
    ]:
        require(token in combined, f"boundary/gate missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_GATE.md",
        "/scripts/saee_customer_validation_one_page_run_card.py",
        "/scripts/saee_customer_validation_one_page_run_card_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_one_page_run_card_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_one_page_run_card_v0_1")
    for key in [
        "status",
        "current_goal_blocker",
        "uses_existing_materials_only",
        "new_questions_added",
        "human_execution_required",
        "human_answer_input_exists",
        "target_session_entry_exists",
        "current_preflight_status",
        "ready_for_explicit_apply_request",
        "step_count",
        "browser_readable_card_available",
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
        "blockers_closed_by_run_card",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "SAEE Customer Validation One-Page Run Card v0.1",
        "customer_validation_one_page_run_card_v0_1",
        "Current blocker: `customer_validated`",
        "Browser card:",
        "Human execution required: `True`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_SMOKE: PASS "
        "steps=6 customer_validated=false"
    )


if __name__ == "__main__":
    main()
