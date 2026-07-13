#!/usr/bin/env python3
"""Smoke test the customer validation answer sheet preflight."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight"
SUMMARY = OUT / "customer_validation_answer_sheet_preflight.local.json"
REPORT = OUT / "customer_validation_answer_sheet_preflight.md"
MISSING_FIELDS = OUT / "customer_validation_answer_sheet_missing_fields.md"
BOUNDARY = OUT / "customer_validation_answer_sheet_preflight_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_GATE.md"
ANSWER_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
)
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, REPORT, MISSING_FIELDS, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_answer_sheet_preflight_v0_1": True,
        "preflight_type": "real_external_customer_answer_sheet_preflight",
        "status": "hold_human_answer_sheet_missing",
        "current_goal_blocker": "customer_validated",
        "human_answer_input_exists": False,
        "target_session_entry_exists": False,
        "ready_for_explicit_apply_request": False,
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
        "blockers_closed_by_preflight": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(payload.get("missing_field_count", 0) >= 40, "missing field count should reflect absent answer sheet")
    require(payload.get("invalid_field_count") == 0, "invalid field count should be zero when answer sheet is absent")
    for field in [
        "session_id",
        "candidate_count",
        "understanding_score",
        "willing_to_test_own_candidates",
        "human_entry_confirmed",
        "no_private_core_disclosed",
        "real_customer_or_target_user_feedback_recorded",
    ]:
        require(field in payload.get("missing_fields", []), f"missing_fields must include {field}")

    require(not ANSWER_INPUT.exists(), "human answer sheet must still be missing")
    require(not TARGET_ENTRY.exists(), "target session entry must still be missing")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, MISSING_FIELDS, BOUNDARY, GATE])
    for token in [
        "customer_validation_answer_sheet_preflight_v0_1: true",
        "human_answer_input_exists: false",
        "ready_for_explicit_apply_request: false",
        "explicit_apply_required: true",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_preflight: 0",
        "answer: hold_until_real_external_answer_sheet_ready",
    ]:
        require(token in combined, f"preflight docs missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_missing_fields.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_GATE.md",
        "/scripts/saee_customer_validation_answer_sheet_preflight.py",
        "/scripts/saee_customer_validation_answer_sheet_preflight_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_answer_sheet_preflight_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_answer_sheet_preflight_v0_1")
    for key in [
        "status",
        "current_goal_blocker",
        "human_answer_input_exists",
        "target_session_entry_exists",
        "ready_for_explicit_apply_request",
        "explicit_apply_required",
        "missing_field_count",
        "invalid_field_count",
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
        "blockers_closed_by_preflight",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Customer Validation Answer Sheet Preflight v0.1",
        "customer_validation_answer_sheet_preflight_v0_1",
        "Current blocker: `customer_validated`",
        "Ready for explicit apply request: `false`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_ANSWER_SHEET_PREFLIGHT_SMOKE: PASS "
        "status=hold_human_answer_sheet_missing customer_validated=false"
    )


if __name__ == "__main__":
    main()
