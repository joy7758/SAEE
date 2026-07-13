#!/usr/bin/env python3
"""Smoke test the human confirmation boundary record."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record"
SUMMARY = OUT / "customer_validation_human_confirmation_boundary_record.local.json"
REPORT = OUT / "customer_validation_human_confirmation_boundary_record.md"
NEXT_INPUT = OUT / "customer_validation_next_required_input.md"
BOUNDARY = OUT / "customer_validation_human_confirmation_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_GATE.md"
ANSWER_INPUT = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
)
TARGET_ENTRY = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, REPORT, NEXT_INPUT, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_human_confirmation_boundary_record_v0_1": True,
        "record_type": "local_human_confirmation_boundary_record",
        "status": "local_human_confirmation_recorded_customer_validation_still_missing",
        "human_confirmation_text": "人工检查完毕，没有问题，确认",
        "confirmation_classification": "local_human_inspection_confirmation_not_external_customer_validation",
        "current_goal_blocker": "customer_validated",
        "customer_validation_acceptance": False,
        "human_answer_input_exists": False,
        "target_session_entry_exists": False,
        "answer_intake_helper_status": "hold_human_answer_sheet_missing",
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
        "blockers_closed_by_confirmation_record": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(not ANSWER_INPUT.exists(), "human answer sheet must still be missing")
    require(not TARGET_ENTRY.exists(), "target session entry must still be missing")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, NEXT_INPUT, BOUNDARY, GATE])
    for token in [
        "customer_validation_human_confirmation_boundary_record_v0_1: true",
        "人工检查完毕，没有问题，确认",
        "customer_validation_acceptance: false",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_confirmation_record: 0",
        "answer: local_confirmation_recorded_customer_validation_still_missing",
        "Do not use internal self-review",
    ]:
        require(token in combined, f"record docs missing token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_record.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_record.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_next_required_input.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_GATE.md",
        "/scripts/saee_customer_validation_human_confirmation_boundary_record.py",
        "/scripts/saee_customer_validation_human_confirmation_boundary_record_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_human_confirmation_boundary_record_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_human_confirmation_boundary_record_v0_1")
    for key in [
        "status",
        "confirmation_classification",
        "current_goal_blocker",
        "customer_validation_acceptance",
        "human_answer_input_exists",
        "target_session_entry_exists",
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
        "blockers_closed_by_confirmation_record",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match summary")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Customer Validation Human Confirmation Boundary Record v0.1",
        "customer_validation_human_confirmation_boundary_record_v0_1",
        "local_human_inspection_confirmation_not_external_customer_validation",
        "Current blocker: `customer_validated`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_HUMAN_CONFIRMATION_BOUNDARY_RECORD_SMOKE: PASS "
        "customer_validated=false confirmation_not_external_validation=true"
    )


if __name__ == "__main__":
    main()
