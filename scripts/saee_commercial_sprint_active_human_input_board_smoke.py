#!/usr/bin/env python3
"""Smoke test for the commercial sprint active human-input board."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_active_human_input_board.py"

OUT_JSON = SPRINT_DIR / "commercial_sprint_active_human_input_board.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_active_human_input_board.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_active_human_input_board.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_active_human_input_board_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD_RECOMMENDATION_GATE.md"
)

EXPECTED_FALSE = [
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "raw_values_recorded",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "task_candidates_executed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "payment_collected",
    "revenue_validated",
]

REQUIRED_DOC_TOKENS = [
    "commercial_sprint_active_human_input_board_v0_1: true",
    "board_scope: preferred_review_batch_template_and_full_quick_fill_status_only_no_values_no_import_no_execution",
    "source_review_batch_template_status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
    "source_review_batch_template_importer_status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
    "source_review_batch_template_e2e_status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
    "preferred_human_input_path: workbook_import_approval_request",
    "preferred_batch_size: 0",
    "preferred_template_row_count: 0",
    "preferred_template_value_present_row_count: 0",
    "preferred_template_missing_value_row_count: 0",
    "preferred_template_e2e_preview_validator_executed: false",
    "preferred_template_e2e_preview_validator_passed: false",
    "ready_for_preferred_template_human_fill: false",
    "full_quick_fill_row_count: 64",
    "quick_fill_row_count: 64",
    "selected_blocker_count: 5",
    "approval_request_count: 1",
    "next_manual_step_count: 4",
    "human_input_required: true",
    "human_review_required: true",
    "separate_workbook_import_execution_request_required: true",
    "workbook_import_authorized: false",
    "workbook_import_performed: false",
    "workbook_written: false",
    "values_transferred: false",
    "human_filled_templates_written: false",
    "validators_run_on_real_input: false",
    "real_evidence_created: false",
    "evidence_collection_authorized: false",
    "execution_authorized: false",
    "evidence_builder_executed: false",
    "blocker_closure_authorized: false",
    "boundary_violation_count: 0",
    "production_ready: false",
    "customer_validated: false",
    "product_launched: false",
    "private_core_exposed: false",
]

REQUIRED_GATE_TOKENS = [
    "answer: conditional",
    "recommend_for_active_human_input_guidance: true",
    "recommend_for_quick_fill_status_compression: true",
    "recommend_for_value_generation: false",
    "recommend_for_workbook_import_execution: false",
    "recommend_for_template_transfer: false",
    "recommend_for_validator_execution: false",
    "recommend_for_evidence_collection: false",
    "recommend_for_evidence_builder_execution: false",
    "recommend_for_blocker_closure: false",
    "recommend_for_product_launch: false",
    "recommend_for_production_readiness_claim: false",
]

FORBIDDEN_DOC_TOKENS = [
    "quick_fill_values_entered_by_codex: true",
    "raw_values_recorded: true",
    "workbook_import_authorized: true",
    "\"workbook_import_authorized\": true",
    "workbook_import_performed: true",
    "\"workbook_import_performed\": true",
    "workbook_written: true",
    "\"workbook_written\": true",
    "values_transferred: true",
    "\"values_transferred\": true",
    "human_filled_templates_written: true",
    "\"human_filled_templates_written\": true",
    "validators_run_on_real_input: true",
    "\"validators_run_on_real_input\": true",
    "real_evidence_created: true",
    "\"real_evidence_created\": true",
    "evidence_collection_authorized: true",
    "\"evidence_collection_authorized\": true",
    "execution_authorized: true",
    "\"execution_authorized\": true",
    "evidence_builder_executed: true",
    "\"evidence_builder_executed\": true",
    "blocker_closure_authorized: true",
    "\"blocker_closure_authorized\": true",
    "production_ready: true",
    "\"production_ready\": true",
    "product_launched: true",
    "\"product_launched\": true",
    "customer_validated: true",
    "\"customer_validated\": true",
    "private_core_exposed: true",
    "\"private_core_exposed\": true",
    "recommend_for_value_generation: true",
    "recommend_for_workbook_import_execution: true",
    "recommend_for_template_transfer: true",
    "recommend_for_validator_execution: true",
    "recommend_for_evidence_collection: true",
    "recommend_for_evidence_builder_execution: true",
    "recommend_for_blocker_closure: true",
    "recommend_for_product_launch: true",
    "recommend_for_production_readiness_claim: true",
]


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD_SMOKE: FAIL " + message
    )


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label} missing token {token}")


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    ready_mode = payload.get("status") == "ready_for_human_workbook_import_approval"
    expected_status = (
        "ready_for_human_workbook_import_approval"
        if ready_mode
        else "hold_human_quick_fill_required"
    )
    expected_stage = "human_workbook_import_approval_review" if ready_mode else "human_quick_fill"
    expected_source_statuses = (
        {
            "source_quick_fill_validator_status": "ready_for_workbook_import_pending_human_approval",
            "source_safety_preflight_status": "pass_no_sensitive_values_found_pending_import_approval",
            "source_import_dry_run_status": "ready_for_workbook_import_pending_human_approval",
            "source_importer_status": "ready_for_apply_pending_explicit_human_command",
            "source_approval_packet_status": "ready_for_human_workbook_import_approval",
        }
        if ready_mode
        else {
            "source_quick_fill_validator_status": "hold_human_quick_fill_required",
            "source_safety_preflight_status": "hold_human_input_required_no_values_to_scan",
            "source_import_dry_run_status": "hold_human_quick_fill_required",
            "source_importer_status": "hold_human_quick_fill_required",
            "source_approval_packet_status": "hold_human_input_required",
        }
    )
    expected_counts = {
        "completed_value_row_count": 64 if ready_mode else 0,
        "missing_value_row_count": 0 if ready_mode else 64,
        "full_quick_fill_missing_value_row_count": 0 if ready_mode else 64,
        "ready_for_human_fill": False if ready_mode else True,
        "ready_for_safety_preflight": ready_mode,
        "safe_to_import_after_human_approval": ready_mode,
        "ready_for_workbook_import": ready_mode,
        "ready_for_workbook_import_approval": ready_mode,
        "ready_import_approval_count": 1 if ready_mode else 0,
    }

    expected = {
        "commercial_sprint_active_human_input_board_v0_1": True,
        "board_type": "current_commercial_sprint_human_input_board",
        "board_scope": "preferred_review_batch_template_and_full_quick_fill_status_only_no_values_no_import_no_execution",
        "status": expected_status,
        "current_stage": expected_stage,
        **expected_source_statuses,
        "source_review_batch_template_status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "source_review_batch_template_importer_status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "source_review_batch_template_e2e_status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "preferred_human_input_path": "workbook_import_approval_request",
        "preferred_batch_size": 0,
        "preferred_template_row_count": 0,
        "preferred_template_value_present_row_count": 0,
        "preferred_template_missing_value_row_count": 0,
        "preferred_template_e2e_preview_validator_executed": False,
        "preferred_template_e2e_preview_validator_passed": False,
        "ready_for_preferred_template_human_fill": False,
        "full_quick_fill_row_count": 64,
        "full_quick_fill_missing_value_row_count": expected_counts["full_quick_fill_missing_value_row_count"],
        "quick_fill_row_count": 64,
        "selected_blocker_count": 5,
        "completed_value_row_count": expected_counts["completed_value_row_count"],
        "missing_value_row_count": expected_counts["missing_value_row_count"],
        "ready_for_human_fill": expected_counts["ready_for_human_fill"],
        "ready_for_safety_preflight": expected_counts["ready_for_safety_preflight"],
        "safe_to_import_after_human_approval": expected_counts["safe_to_import_after_human_approval"],
        "ready_for_workbook_import": expected_counts["ready_for_workbook_import"],
        "ready_for_workbook_import_approval": expected_counts["ready_for_workbook_import_approval"],
        "approval_request_count": 1,
        "ready_import_approval_count": expected_counts["ready_import_approval_count"],
        "next_manual_step_count": 4,
        "human_input_required": True,
        "human_review_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_request_required": True,
        "separate_validator_execution_request_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value}")
    for flag in EXPECTED_FALSE:
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")
    if len(payload.get("board_rows", [])) != 5:
        fail("board_rows must contain five blockers")
    row_counts = {
        row["blocker_id"]: row["missing_value_row_count"]
        for row in payload["board_rows"]
    }
    expected_row_counts = {
        "formal_security_review": 12,
        "pricing_page": 14,
        "production_monitoring": 10,
        "production_restore_policy": 13,
        "support_contact": 15,
    }
    if ready_mode:
        expected_row_counts = {key: 0 for key in expected_row_counts}
    if row_counts != expected_row_counts:
        fail("blocker missing counts changed")
    if any(step.get("execution_allowed_by_codex") is not False for step in payload["next_manual_steps"]):
        fail("manual steps must not allow Codex execution")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 5:
        fail("active human input board CSV must contain five rows")

    docs = {
        "top_doc": TOP_DOC.read_text(encoding="utf-8"),
        "report": OUT_MD.read_text(encoding="utf-8"),
        "boundary": OUT_BOUNDARY.read_text(encoding="utf-8"),
        "gate": GATE.read_text(encoding="utf-8"),
    }
    for label, text in docs.items():
        tokens = REQUIRED_GATE_TOKENS if label == "gate" else REQUIRED_DOC_TOKENS
        for token in tokens:
            require_token(text, token, label)
        if label != "gate":
            dynamic_tokens = [
                f"status: {expected_status}",
                f"current_stage: {expected_stage}",
                f"source_quick_fill_validator_status: {expected_source_statuses['source_quick_fill_validator_status']}",
                f"source_safety_preflight_status: {expected_source_statuses['source_safety_preflight_status']}",
                f"source_import_dry_run_status: {expected_source_statuses['source_import_dry_run_status']}",
                f"source_importer_status: {expected_source_statuses['source_importer_status']}",
                f"source_approval_packet_status: {expected_source_statuses['source_approval_packet_status']}",
                f"full_quick_fill_missing_value_row_count: {expected_counts['full_quick_fill_missing_value_row_count']}",
                f"completed_value_row_count: {expected_counts['completed_value_row_count']}",
                f"missing_value_row_count: {expected_counts['missing_value_row_count']}",
                f"ready_for_safety_preflight: {str(expected_counts['ready_for_safety_preflight']).lower()}",
                f"safe_to_import_after_human_approval: {str(expected_counts['safe_to_import_after_human_approval']).lower()}",
                f"ready_for_workbook_import: {str(expected_counts['ready_for_workbook_import']).lower()}",
                f"ready_for_workbook_import_approval: {str(expected_counts['ready_for_workbook_import_approval']).lower()}",
                f"ready_import_approval_count: {expected_counts['ready_import_approval_count']}",
            ]
            for token in dynamic_tokens:
                require_token(text, token, label)
    combined = "\n".join(docs.values())
    found = [token for token in FORBIDDEN_DOC_TOKENS if token in combined]
    if found:
        fail("forbidden doc tokens found: " + ", ".join(found))

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found_runner = [token for token in forbidden_runner_tokens if token in runner_text]
    if found_runner:
        fail("runner suggests external access or execution: " + ", ".join(found_runner))

    print(
        "SAEE_COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD_SMOKE: PASS "
        f"status={expected_status} missing_value_row_count={expected_counts['missing_value_row_count']} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
