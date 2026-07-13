#!/usr/bin/env python3
"""Smoke check for SAEE local tryout readiness card."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD_DIR = ROOT / "phase_b_product/commercial_readiness/local_tryout_readiness_card"
CARD_JSON = CARD_DIR / "local_tryout_readiness_card.local.json"
CARD_MD = CARD_DIR / "local_tryout_readiness_card.md"
BOUNDARY_MD = CARD_DIR / "boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/LOCAL_TRYOUT_READINESS_CARD_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRYOUT_READINESS_CARD_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_LOCAL_TRYOUT_READINESS_CARD_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [CARD_JSON, CARD_MD, BOUNDARY_MD, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(CARD_JSON.read_text(encoding="utf-8"))
    expected_true = {
        "local_tryout_readiness_card_v0_1": True,
        "human_tryout_allowed": True,
        "human_review_required": True,
    }
    expected_values = {
        "card_type": "commercial_local_tryout_readiness_card",
        "card_scope": "local_human_tryout_status_and_commands_only",
        "status": "ready_for_local_human_tryout",
        "commercial_status": "hold",
        "commercial_readiness_status": "ready_for_separate_evidence_builder_request",
        "commercial_active_stage": "separate_evidence_builder_request",
        "production_launch_status": "hold",
        "source_count": 6,
        "source_ready_count": 6,
        "missing_source_count": 0,
        "commercial_status_snapshot_available": True,
        "source_commercial_readiness_status": (
            "phase_b_product/commercial_readiness/commercial_readiness_status.local.json"
        ),
        "source_commercial_human_action_board": (
            "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.local.json"
        ),
        "source_commercial_human_action_board_html": (
            "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.html"
        ),
        "commercial_human_action_board_available": True,
        "commercial_human_action_board_ready_for_human_review_count": 9,
        "commercial_human_action_board_dependency_blocked_count": 15,
        "commercial_human_action_board_active_sprint_blocker_count": 5,
        "commercial_human_action_board_active_sprint_ready_action_count": 5,
        "commercial_human_action_board_blockers_closed": 0,
        "commercial_human_action_board_execution_authorized": False,
        "commercial_human_action_board_evidence_collection_authorized": False,
        "production_blocker_count": 24,
        "satisfied_production_checks": 0,
        "missing_commercial_human_input_value_count": 0,
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "preferred_human_input_path": "separate_evidence_builder_request",
        "source_begin_here_html": "phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html",
        "source_review_batch_quality_guide_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_entry_quality_guide.html",
        "source_review_batch_template_preflight_markdown": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.md",
        "template_preflight_passed": False,
        "source_post_fill_validation_runbook_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_validation_runbook.html",
        "post_fill_validation_ready": False,
        "commercial_human_input_required": True,
        "commercial_ready_for_human_fill": False,
        "commercial_ready_for_safety_preflight": True,
        "commercial_ready_for_workbook_import": True,
        "commercial_workbook_import_authorized": False,
        "source_workbook_import_performed": True,
        "source_workbook_written": True,
        "ready_for_template_transfer_request": True,
        "ready_for_template_transfer_execution": True,
        "human_template_transfer_execution_request_recorded": True,
        "human_template_transfer_execution_authorized": True,
        "separate_template_transfer_execution_request_required": False,
        "template_transfer_authorized": True,
        "template_transfer_execution_allowed": False,
        "validators_run": True,
        "validators_run_on_real_input": True,
        "local_validators_run": True,
        "validator_execution_run_status": "completed_all_validators_passed",
        "validator_hold_output_review_completed": False,
        "validator_outputs_review_required": False,
        "validator_missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "validators_run_count": 5,
        "validator_hold_count": 0,
        "validator_pass_count": 5,
        "validator_stop_count": 0,
        "builder_ready_count": 5,
        "blockers_closed_by_validator_run": 0,
        "requires_validator_output_review": False,
        "requires_validator_input_completion": False,
        "requires_validator_rerun_after_completion": False,
        "requires_separate_evidence_builder_request": True,
        "blockers_closed_by_card": 0,
        "demo_url": "http://127.0.0.1:8765/",
        "api_endpoint": "http://127.0.0.1:8000/experiment/run",
    }
    for key, expected in expected_true.items():
        require(payload.get(key) is expected, f"{key} must be {expected}")
    for key, expected in expected_values.items():
        require(payload.get(key) == expected, f"{key} must be {expected}")
    next_required_action = str(payload.get("commercial_next_required_action", ""))
    require(
        "All five local input validators pass" in next_required_action,
        "commercial_next_required_action must point to evidence builder request",
    )
    require(
        "close blockers" in next_required_action
        and "production readiness" in next_required_action,
        "commercial_next_required_action must preserve evidence-builder and closure stop boundary",
    )
    require(
        "Fill commercial_sprint_human_input_quick_fill_packet.csv" not in next_required_action,
        "commercial_next_required_action must not point to the old full quick-fill first step",
    )

    false_flags = [
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "landing_page_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "customer_validated",
        "customer_data_collected",
        "production_ready",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "external_validation_claim",
        "browser_automation_used",
        "browser_opened_by_script",
        "dependencies_installed_by_script",
        "task_candidates_executed",
        "development_permission_granted",
        "evidence_collection_authorized",
        "blockers_closed",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for key in false_flags:
        require(payload.get(key) is False, f"{key} must be false")

    checks = payload.get("required_ready_checks", {})
    required_checks = {
        "tryout_guide_available",
        "preflight_passed",
        "cold_start_preflight_passed",
        "http_e2e_passed",
        "handoff_packet_ready",
        "local_observation_recorded",
    }
    require(set(checks) == required_checks, "required_ready_checks drifted")
    for key in sorted(required_checks):
        require(checks.get(key) is True, f"{key} must be true")
    require(payload.get("missing_or_blocking_items") == [], "missing_or_blocking_items must be []")

    commands = payload.get("make_commands", {})
    for command in [
        "make local-trial-preflight",
        "make try-local",
        "make local-trial-status",
        "make local-trial-stop",
        "make check-local-trial-http-e2e",
        "make check-local-trial-handoff-packet",
    ]:
        require(command in commands.values(), f"missing command {command}")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [CARD_MD, BOUNDARY_MD, TOP_DOC, GATE]
    )
    required_tokens = [
        "local_tryout_readiness_card_v0_1: true",
        "card_scope: local_human_tryout_status_and_commands_only",
        "status: ready_for_local_human_tryout",
        "commercial_status: hold",
        "commercial_readiness_status: ready_for_separate_evidence_builder_request",
        "commercial_active_stage: separate_evidence_builder_request",
        "production_launch_status: hold",
        "human_tryout_allowed: true",
        "production_blocker_count: 24",
        "satisfied_production_checks: 0",
        "missing_commercial_human_input_value_count: 0",
        "commercial_human_action_board_available: true",
        "commercial_human_action_board_ready_for_human_review_count: 9",
        "commercial_human_action_board_dependency_blocked_count: 15",
        "commercial_human_action_board_active_sprint_blocker_count: 5",
        "commercial_human_action_board_execution_authorized: false",
        "commercial_human_action_board_evidence_collection_authorized: false",
        "preferred_template_missing_value_row_count: 0",
        "full_quick_fill_missing_value_row_count: 0",
        "preferred_human_input_path: separate_evidence_builder_request",
        "source_workbook_import_performed: `true`",
        "source_workbook_written: `true`",
        "ready_for_template_transfer_request: true",
        "ready_for_template_transfer_execution: true",
        "human_template_transfer_execution_request_recorded: true",
        "human_template_transfer_execution_authorized: true",
        "separate_template_transfer_execution_request_required: false",
        "template_transfer_authorized: true",
        "template_transfer_execution_allowed: false",
        "validators_run: true",
        "validators_run_on_real_input: true",
        "local_validators_run: `true`",
        "validator_execution_run_status: completed_all_validators_passed",
        "validator_hold_output_review_completed: false",
        "validator_outputs_review_required: false",
        "validator_missing_input_completion_required: false",
        "rerun_validators_after_completion_required: false",
        "total_missing_metadata_field_count: 0",
        "total_missing_evidence_item_count: 0",
        "total_missing_source_note_count: 0",
        "validator_hold_count: 0",
        "validator_pass_count: 5",
        "builder_ready_count: 5",
        "blockers_closed_by_validator_run: 0",
        "source_review_batch_template_preflight_markdown",
        "template_preflight_passed: false",
        "post_fill_validation_ready: false",
        "commercial_workbook_import_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "external_validation_claim: false",
        "private_core_exposed: false",
        "blockers_closed_by_card: 0",
        "recommend_for_local_tryout_handoff: true",
        "recommend_for_customer_validation_claim: false",
        "recommend_for_external_validation_claim: false",
        "recommend_for_production: false",
        "recommend_for_product_launch: false",
        "recommend_for_blocker_closure: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "external_validation_claim: true",
        '"external_validation_claim": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "commercial_workbook_import_authorized: true",
        '"commercial_workbook_import_authorized": true',
        "blockers_closed_by_card: 1",
        '"blockers_closed_by_card": 1',
        "recommend_for_customer_validation_claim: true",
        "recommend_for_external_validation_claim: true",
        "recommend_for_production: true",
        "recommend_for_product_launch: true",
        "recommend_for_blocker_closure: true",
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/LOCAL_TRYOUT_READINESS_CARD_V0_1.md",
        "/phase_b_product/commercial_readiness/local_tryout_readiness_card/local_tryout_readiness_card.local.json",
        "/phase_b_product/commercial_readiness/local_tryout_readiness_card/local_tryout_readiness_card.md",
        "/phase_b_product/commercial_readiness/local_tryout_readiness_card/boundary_audit.md",
        "/docs/strategy/SAEE_LOCAL_TRYOUT_READINESS_CARD_RECOMMENDATION_GATE.md",
        "/scripts/saee_local_tryout_readiness_card.py",
        "/scripts/saee_local_tryout_readiness_card_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("local_tryout_readiness_card_v0_1", {})
    for key, expected in {**expected_true, **expected_values}.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")
    for key in false_flags:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    print(
        "SAEE_LOCAL_TRYOUT_READINESS_CARD_SMOKE: PASS "
        "status=ready_for_local_human_tryout source_ready_count=6 "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
