#!/usr/bin/env python3
"""Smoke test for the external customer validation action board."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board"
SUMMARY = BASE / "external_customer_validation_action_board.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    BASE / "README.md",
    BASE / "external_customer_validation_action_board.md",
    BASE / "external_customer_validation_action_board.html",
    BASE / "BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_ACTION_BOARD_GATE.md",
]


EXPECTED_FALSE = [
    "human_session_performed",
    "human_result_entered",
    "ready_for_import_after_human_entry",
    "ready_for_validator_after_import",
    "codex_may_contact_customer",
    "codex_may_run_external_session",
    "codex_may_infer_customer_feedback",
    "customer_contacted_by_codex",
    "customer_validated",
    "production_ready",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "external_model_api_called",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    for path in REQUIRED:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if data.get("external_customer_validation_action_board_v0_1") is not True:
        fail("action board flag missing")
    if data.get("status") != "ready_for_human_customer_validation_session_sequence":
        fail("unexpected action board status")
    if data.get("current_goal_blocker") != "customer_validated":
        fail("current_goal_blocker must be customer_validated")
    if data.get("recommended_path_locked") is not True:
        fail("recommended_path_locked must be true")
    if data.get("recommended_path_id") != "minimum_session_packet":
        fail("recommended_path_id must be minimum_session_packet")
    if data.get("alternative_paths_reference_only") is not True:
        fail("alternative_paths_reference_only must be true")
    if data.get("recommended_form") != (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_minimum_session_packet/minimum_session_form.html"
    ):
        fail("recommended_form must point to minimum_session_form.html")
    if data.get("recommended_questions") != (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md"
    ):
        fail("recommended_questions must point to MINIMUM_SESSION_QUESTIONS.md")
    if data.get("action_count") != 6:
        fail("action_count must be 6")
    if data.get("first_action_id") != "ECV-001":
        fail("first_action_id must be ECV-001")
    if data.get("human_action_required") is not True:
        fail("human_action_required must be true")
    if data.get("blockers_closed_by_action_board") != 0:
        fail("blockers_closed_by_action_board must be 0")
    for key in EXPECTED_FALSE:
        if data.get(key) is not False:
            fail(f"{key} must be false")

    actions = data.get("actions", [])
    if len(actions) != 6:
        fail("actions must contain 6 items")
    if any(action.get("codex_executable") is not False for action in actions):
        fail("all actions must keep codex_executable=false")
    action_by_id = {action.get("action_id"): action for action in actions}
    if "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md" not in action_by_id["ECV-004"].get("entrypoint", ""):
        fail("ECV-004 must use the minimum session questions")
    if "external_customer_validation_minimum_session_packet/minimum_session_form.html" not in action_by_id["ECV-005"].get("entrypoint", ""):
        fail("ECV-005 must use the minimum session form")
    if "external_customer_validation_session_entry_workbench.html" in action_by_id["ECV-005"].get("entrypoint", ""):
        fail("ECV-005 must not default to the older workbench")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_action_board_v0_1")
    if not entry:
        fail("agent-index missing external_customer_validation_action_board_v0_1")
    for key in EXPECTED_FALSE:
        if entry.get(key) is not False:
            fail(f"agent-index {key} must be false")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/BOUNDARY_AUDIT.md",
    ]:
        if item not in llms:
            fail(f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED if path.suffix in {".md", ".html"})
    for needle in [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "Codex may contact",
        "Codex runs the external session",
        "推荐路径已锁定",
        "minimum_session_form.html",
        "reference-only",
    ]:
        if needle in {
            "推荐路径已锁定",
            "minimum_session_form.html",
            "reference-only",
        }:
            if needle not in combined:
                fail(f"required text missing: {needle}")
        elif needle in combined:
            fail(f"forbidden claim found: {needle}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_ACTION_BOARD_SMOKE: PASS")


if __name__ == "__main__":
    main()
