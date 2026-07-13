#!/usr/bin/env python3
"""Smoke test the customer-validation next-step router."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router"
SUMMARY = OUT / "customer_validation_next_step_router.local.json"
REPORT = OUT / "customer_validation_next_step_router.md"
BOUNDARY = OUT / "customer_validation_next_step_router_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_GATE.md"
ANSWER_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.human_filled.md"
)
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, REPORT, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_next_step_router_v0_1": True,
        "router_type": "local_read_only_customer_validation_next_step_router",
        "status": "waiting_for_real_external_customer_session",
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "recommended_form": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "recommended_questions": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
        "recommended_text_answer_template": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.template.md",
        "recommended_text_answer_input": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.human_filled.md",
        "minimum_answer_converter_summary": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.local.json",
        "minimum_answer_converter_status": "hold_minimum_session_answers_missing",
        "reference_one_page_run_card": "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.md",
        "human_answer_input_exists": False,
        "target_session_entry_exists": False,
        "current_preflight_status": "hold_human_answer_sheet_missing",
        "current_preflight_missing_field_count": 47,
        "ready_for_explicit_apply_request": False,
        "post_session_summary_exists": True,
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
        "blockers_closed_by_router": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(not ANSWER_INPUT.exists(), "router must not create human-filled answers")
    require(not TARGET_ENTRY.exists(), "router must not write final session entry")

    require(
        payload.get("next_command")
        == "open phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "next command must point to the minimum session form in current state",
    )

    report_text = REPORT.read_text(encoding="utf-8")
    for token in [
        "SAEE Customer Validation Next Step Router",
        "waiting_for_real_external_customer_session",
        "minimum_session_form.html",
        "MINIMUM_SESSION_QUESTIONS.md",
        "recommended_path_locked: true",
        "recommended_path_id: minimum_session_packet",
        "customer_validated: false",
        "production_ready: false",
        "blockers_closed_by_router: 0",
    ]:
        require(token in report_text, f"report missing token: {token}")

    combined = BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
    for token in [
        "customer_validation_next_step_router_v0_1: true",
        "answer: local_next_step_route_ready",
        "recommended_path_locked: true",
        "recommended_path_id: minimum_session_packet",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_router: 0",
    ]:
        require(token in combined, f"boundary/gate missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_GATE.md",
        "/scripts/saee_customer_validation_next_step_router.py",
        "/scripts/saee_customer_validation_next_step_router_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_next_step_router_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_next_step_router_v0_1")
    for key in [
        "status",
        "current_goal_blocker",
        "recommended_path_locked",
        "recommended_path_id",
        "recommended_form",
        "recommended_questions",
        "recommended_text_answer_template",
        "recommended_text_answer_input",
        "minimum_answer_converter_summary",
        "minimum_answer_converter_status",
        "reference_one_page_run_card",
        "human_answer_input_exists",
        "target_session_entry_exists",
        "current_preflight_status",
        "current_preflight_missing_field_count",
        "ready_for_explicit_apply_request",
        "next_action",
        "next_command",
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
        "blockers_closed_by_router",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "SAEE Customer Validation Next Step Router v0.1",
        "customer_validation_next_step_router_v0_1",
        "Current blocker: `customer_validated`",
        "Recommended form:",
        "minimum_session_form.html",
        "Recommended 12-question text template:",
        "minimum_session_answers.template.md",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_NEXT_STEP_ROUTER_SMOKE: PASS "
        "status=waiting_for_real_external_customer_session customer_validated=false"
    )


if __name__ == "__main__":
    main()
