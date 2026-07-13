#!/usr/bin/env python3
"""Smoke test the customer validation answer intake helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper"
SUMMARY = OUT / "customer_validation_answer_intake_helper.local.json"
REPORT = OUT / "customer_validation_answer_intake_helper.md"
ANSWER_TEMPLATE = OUT / "customer_validation_answers.template.md"
ANSWER_INPUT = OUT / "customer_validation_answers.human_filled.md"
BOUNDARY = OUT / "customer_validation_answer_intake_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_RECOMMENDATION_GATE.md"
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, REPORT, ANSWER_TEMPLATE, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_answer_intake_helper_v0_1": True,
        "helper_type": "human_answer_sheet_to_session_entry_helper",
        "status": "hold_human_answer_sheet_missing",
        "current_goal_blocker": "customer_validated",
        "human_answer_input_exists": False,
        "target_session_entry_written": False,
        "apply_requested": False,
        "missing_field_count": 0,
        "required_question_count": 16,
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
        "blockers_closed_by_answer_intake_helper": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(payload.get("answer_template") == str(ANSWER_TEMPLATE.relative_to(ROOT)), "answer template path changed")
    require(payload.get("human_answer_input") == str(ANSWER_INPUT.relative_to(ROOT)), "answer input path changed")
    require(payload.get("target_session_entry") == str(TARGET_ENTRY.relative_to(ROOT)), "target entry path changed")
    require(not ANSWER_INPUT.exists(), "human answer input must not be prefilled by Codex")
    require(not TARGET_ENTRY.exists(), "target customer validation session entry must not be written in default mode")

    template_text = ANSWER_TEMPLATE.read_text(encoding="utf-8")
    for token in [
        "Only fill this after a real external customer or target-user session.",
        "session_id:",
        "candidate_count:",
        "understanding_score:",
        "willing_to_test_own_candidates:",
        "human_entry_confirmed:",
        "no_private_core_disclosed:",
        "no_production_ready_claim_made:",
    ]:
        require(token in template_text, f"answer template missing {token}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, GATE])
    for token in [
        "customer_validation_answer_intake_helper_v0_1: true",
        "status: hold_human_answer_sheet_missing",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_answer_intake_helper: 0",
        "answer: conditional",
    ]:
        require(token in combined, f"helper docs missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_helper.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_helper.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.template.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_RECOMMENDATION_GATE.md",
        "/scripts/saee_customer_validation_answer_intake_helper.py",
        "/scripts/saee_customer_validation_answer_intake_helper_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_answer_intake_helper_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_answer_intake_helper_v0_1")
    for key in [
        "status",
        "current_goal_blocker",
        "answer_template",
        "human_answer_input",
        "human_answer_input_exists",
        "target_session_entry",
        "target_session_entry_written",
        "post_session_processor_command",
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
        "blockers_closed_by_answer_intake_helper",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Customer Validation Answer Intake Helper v0.1",
        "customer_validation_answer_intake_helper_v0_1",
        "Current blocker: `customer_validated`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_ANSWER_INTAKE_HELPER_SMOKE: PASS "
        "status=hold_human_answer_sheet_missing customer_validated=false"
    )


if __name__ == "__main__":
    main()
