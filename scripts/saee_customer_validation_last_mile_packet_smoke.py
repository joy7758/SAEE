#!/usr/bin/env python3
"""Smoke test the customer validation last-mile packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet"
SUMMARY = OUT / "customer_validation_last_mile_packet.local.json"
PACKET = OUT / "customer_validation_last_mile_packet.md"
QUESTIONS = OUT / "customer_validation_required_questions.md"
BLANK_DRAFT = OUT / "external_customer_validation_session_entry.blank_draft.local.json"
BOUNDARY = OUT / "customer_validation_last_mile_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_SMOKE: FAIL " + message)


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
    for path in [SUMMARY, PACKET, QUESTIONS, BLANK_DRAFT, BOUNDARY, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "customer_validation_last_mile_packet_v0_1": True,
        "packet_type": "human_external_customer_validation_last_mile_handoff",
        "status": "ready_for_real_external_customer_session_entry",
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "recommended_form": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "recommended_questions": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
        "reference_result_entry_workbench": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html",
        "target_human_output": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json",
        "post_session_processor_command": "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        "required_question_count": 16,
        "required_review_checkbox_count": 25,
        "required_boundary_confirmation_count": 5,
        "human_session_entry_exists": False,
        "ready_for_post_session_processor": False,
        "codex_may_contact_customer": False,
        "codex_may_run_external_session": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_run_post_session_processor_after_human_file_exists": True,
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
        "blockers_closed_by_last_mile_packet": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(
        payload.get("current_actionable_blockers_after_local_human_evidence")
        == ["customer_validated"],
        "current blocker list must be customer_validated only",
    )

    draft = read_json(BLANK_DRAFT)
    require(draft.get("human_entry_confirmed") is False, "blank draft must not be confirmed")
    require(draft.get("customer_validated") is False, "blank draft must not validate customer")
    require(draft.get("production_ready") is False, "blank draft must not be production ready")
    session = draft.get("session", {})
    require(isinstance(session, dict), "blank draft session must be object")
    for key in [
        "session_id",
        "session_date",
        "participant_role",
        "team_type",
        "current_evaluation_method",
        "candidate_count",
        "understanding_score",
        "trust_score",
        "decision_influence_score",
        "repeat_usage_intent_score",
        "time_to_value_minutes",
        "willing_to_test_own_candidates",
        "top_objection",
        "evidence_missing",
        "notes",
    ]:
        require(key in session, f"blank draft missing session.{key}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [PACKET, QUESTIONS, BOUNDARY, GATE])
    for token in [
        "customer_validation_last_mile_packet_v0_1: true",
        "recommended_path_locked: true",
        "recommended_path_id: minimum_session_packet",
        "minimum_session_form.html",
        "MINIMUM_SESSION_QUESTIONS.md",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_last_mile_packet: 0",
        "Do not answer them from internal self-review.",
        "answer: ready_for_real_external_customer_session_entry",
    ]:
        require(token in combined, f"missing text token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_packet.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_packet.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_required_questions.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/external_customer_validation_session_entry.blank_draft.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_GATE.md",
        "/scripts/saee_customer_validation_last_mile_packet.py",
        "/scripts/saee_customer_validation_last_mile_packet_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("customer_validation_last_mile_packet_v0_1")
    require(isinstance(entry, dict), "agent-index missing customer_validation_last_mile_packet_v0_1")
    for key, value in expected.items():
        if key in entry:
            require(entry.get(key) == value, f"agent-index {key} must be {value}")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Customer Validation Last-Mile Packet v0.1",
        "customer_validation_last_mile_packet_v0_1",
        "Current blocker: `customer_validated`",
        "customer_validated=false",
        "production_ready=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_SMOKE: PASS "
        "questions=16 customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
