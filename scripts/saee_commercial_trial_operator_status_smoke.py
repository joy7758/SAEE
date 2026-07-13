#!/usr/bin/env python3
"""Smoke check for the SAEE commercial trial operator status card."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_trial_operator_status.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_trial_operator_status"
OUTPUT_JSON = OUTPUT_DIR / "commercial_trial_operator_status.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_trial_operator_status.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_trial_operator_status.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_TRIAL_OPERATOR_STATUS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS_SMOKE: FAIL " + message)


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"{path.relative_to(ROOT)} missing")

    data = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_trial_operator_status_v0_1": True,
        "status_type": "local_trial_and_commercial_readiness_operator_card",
        "status_version": "v0.1",
        "commercial_status": "hold",
        "controlled_preview_status": "hold",
        "production_launch_status": "hold",
        "commercial_readiness_status": "hold_external_customer_validation_required",
        "production_blocker_count": 24,
        "selected_blocker_count": 5,
        "missing_value_row_count": 0,
        "preferred_human_input_path": "external_customer_validation_session",
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "next_action_count": 1,
        "first_action_id": "NEXT-CV-001",
        "first_blocker_id": "customer_validated",
        "final_human_inspection_recorded": True,
        "local_evidence_lanes_passed": True,
        "local_evidence_lane_count": 7,
        "remaining_production_blocker_count_after_local_human_evidence": 1,
        "external_customer_validation_required": True,
        "external_customer_validation_performed": False,
        "current_goal_blocker": "customer_validated",
        "source_workbook_import_performed": True,
        "source_workbook_written": True,
        "ready_for_template_transfer_request": True,
        "ready_for_template_transfer_execution": False,
        "template_transfer_authorized": True,
        "template_transfer_performed": True,
        "template_transfer_execution_allowed": False,
        "template_transfer_applier_execution_allowed": False,
        "ready_for_validator_approval": False,
        "ready_for_validator_execution": False,
        "planned_validator_count": 5,
        "ready_validator_count": 5,
        "validator_hold_count": 0,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "validators_run": True,
        "validator_execution_run_status": "completed_all_validators_passed",
        "validator_hold_output_review_completed": False,
        "validator_outputs_review_required": False,
        "validator_missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "local_validators_run": True,
        "validators_run_count": 5,
        "validator_pass_count": 5,
        "validator_stop_count": 0,
        "builder_ready_count": 5,
        "blockers_closed_by_validator_run": 0,
        "requires_validator_approval_review": False,
        "requires_validator_output_review": False,
        "requires_validator_input_completion": False,
        "requires_validator_rerun_after_completion": False,
        "requires_separate_evidence_builder_request": False,
        "requires_separate_validator_execution_request": False,
        "cloud_package_status": "local_package_ready_for_human_review",
        "cloud_target_id": "i-8xOwPKN3",
        "cloud_clear_required_before_sync": True,
        "human_cloud_clear_confirmation_required": True,
        "human_cloud_upload_confirmation_required": True,
        "destructive_cloud_operation_requires_separate_confirmation": True,
        "cloud_sync_allowed_by_status_card": False,
        "evidence_collection_allowed_by_status_card": False,
        "blocker_closure_allowed_by_status_card": False,
        "product_launch_allowed_by_status_card": False,
        "human_review_required": True,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_data_allowed": False,
        "paid_trial_enabled": False,
        "payment_provider_configured": False,
        "product_launched": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "validators_run_on_real_input": True,
        "real_evidence_created": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "cloud_clear_performed": False,
        "cloud_sync_performed": False,
        "cloud_delete_authorized": False,
        "cloud_upload_authorized": False,
    }
    for key, value in expected.items():
        require(data.get(key) == value, f"{key} must be {value}")
    require(
        data.get("status")
        in {"local_trial_running_commercial_hold", "local_trial_not_running_commercial_hold"},
        "status must be local trial running/not running commercial hold",
    )
    require(
        data.get("local_trial_landing_url", "").startswith("http://127.0.0.1:8765"),
        "landing URL must be localhost",
    )
    require(
        "remaining commercial gate is one real external customer or target-user validation session"
        in data.get("operator_recommendation", ""),
        "operator recommendation missing customer validation guidance",
    )
    require(
        "Run one real external customer or target-user validation session"
        in data.get("next_human_action", ""),
        "next human action missing customer validation instruction",
    )
    require(
        data.get("remaining_production_blockers_after_local_human_evidence")
        == ["customer_validated"],
        "remaining blocker must be customer_validated",
    )

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 1, "CSV must contain one row")
    require(rows[0]["first_action_id"] == "NEXT-CV-001", "CSV first action changed")
    require(rows[0]["cloud_sync_performed"] == "false", "CSV cloud sync must be false")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, README_PATH, DOC_PATH, GATE_PATH]
    )
    for token in [
        "commercial_trial_operator_status_v0_1: true",
        "commercial_readiness_status: hold_external_customer_validation_required",
        "first_action_id: NEXT-CV-001",
        "first_blocker_id: customer_validated",
        "preferred_human_input_path: external_customer_validation_session",
        "final_human_inspection_recorded: true",
        "local_evidence_lanes_passed: true",
        "remaining_production_blocker_count_after_local_human_evidence: 1",
        "remaining_production_blockers_after_local_human_evidence: customer_validated",
        "external_customer_validation_required: true",
        "current_goal_blocker: customer_validated",
        "template_transfer_performed: true",
        "template_transfer_execution_allowed: false",
        "ready_for_validator_approval: false",
        "ready_for_validator_execution: false",
        "approved_validator_count: 0",
        "validator_execution_authorized_count: 0",
        "validator_execution_run_status: completed_all_validators_passed",
        "validator_hold_output_review_completed: false",
        "validator_outputs_review_required: false",
        "validator_missing_input_completion_required: false",
        "rerun_validators_after_completion_required: false",
        "total_missing_metadata_field_count: 0",
        "total_missing_evidence_item_count: 0",
        "total_missing_source_note_count: 0",
        "local_validators_run: true",
        "validators_run_count: 5",
        "validator_hold_count: 0",
        "validator_pass_count: 5",
        "validator_stop_count: 0",
        "builder_ready_count: 5",
        "blockers_closed_by_validator_run: 0",
        "requires_validator_output_review: false",
        "requires_validator_input_completion: false",
        "requires_validator_rerun_after_completion: false",
        "requires_separate_evidence_builder_request: false",
        "validators_run_on_real_input: true",
        "cloud_sync_performed: false",
        "workbook_import_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: recommend",
        "recommend_for_local_trial_operator_status: true",
        "recommend_for_cloud_sync_execution: false",
        "recommend_for_production: false",
    ]:
        require(token in combined, "missing doc token: " + token)
    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "cloud_clear_performed: true",
        '"cloud_clear_performed": true',
        "cloud_sync_performed: true",
        '"cloud_sync_performed": true',
        "ready_for_validator_execution: true",
        '"ready_for_validator_execution": true',
        "recommend_for_cloud_sync_execution: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_product_launch: true",
        "recommend_for_production: true",
    ]
    text = "\n".join([json.dumps(data), combined])
    found = [token for token in forbidden if token in text]
    require(not found, "forbidden claims found: " + ", ".join(found))
    print(
        "SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS_SMOKE: PASS "
        "commercial_readiness_status=hold_external_customer_validation_required "
        "cloud_sync_performed=false production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
