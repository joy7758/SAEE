#!/usr/bin/env python3
"""Smoke check for the current commercial next-action summary."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_next_action_summary.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_action_summary"
OUTPUT_JSON = OUTPUT_DIR / "commercial_next_action_summary.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_next_action_summary.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_next_action_summary.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_NEXT_ACTION_SUMMARY_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY_SMOKE: FAIL " + message)


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True, text=True)
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"{path.relative_to(ROOT)} missing")

    data = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_next_action_summary_v0_1": True,
        "summary_type": "saee_commercial_next_action_summary",
        "summary_scope": "local_commercial_readiness_evidence_builder_request_next_human_action",
        "status": "ready_for_separate_evidence_builder_request",
        "commercial_status": "hold",
        "controlled_preview_status": "hold",
        "production_launch_status": "hold",
        "active_stage": "separate_evidence_builder_request",
        "primary_human_input_lane": "commercial_sprint_evidence_builder_request_review",
        "preferred_human_input_path": "separate_evidence_builder_request",
        "next_action_count": 1,
        "first_action_id": "NEXT-EBR-001",
        "first_sequence_step_id": "EBR-001",
        "first_blocker_id": "separate_evidence_builder_request",
        "quick_fill_row_count": 64,
        "completed_value_row_count": 64,
        "missing_value_row_count": 0,
        "preferred_template_row_count": 5,
        "preferred_template_value_present_row_count": 5,
        "preferred_template_missing_value_row_count": 0,
        "template_transfer_performed": True,
        "template_transfer_values_transferred": True,
        "template_transfer_human_filled_templates_written": True,
        "template_transfer_values_transferred_count": 64,
        "template_transfer_templates_written_count": 5,
        "template_transfer_execution_allowed": False,
        "template_transfer_applier_execution_allowed": False,
        "ready_for_validator_approval": False,
        "ready_for_validator_execution": False,
        "planned_validator_count": 5,
        "ready_validator_count": 5,
        "validator_hold_count": 0,
        "validator_pass_count": 5,
        "builder_ready_count": 5,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "validators_run": True,
        "validators_run_on_real_input": True,
        "requires_validator_approval_review": False,
        "requires_validator_output_review": False,
        "requires_validator_input_completion": False,
        "requires_validator_rerun_after_completion": False,
        "requires_separate_validator_execution_request": False,
        "requires_separate_evidence_builder_request": True,
        "validator_hold_output_review_completed": False,
        "validator_missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_summary": 0,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, value in expected.items():
        require(data.get(key) == value, f"{key} must be {value}")

    actions = data.get("next_actions", [])
    require(isinstance(actions, list) and len(actions) == 1, "must contain one next action")
    action = actions[0]
    expected_action = {
        "action_id": "NEXT-EBR-001",
        "sequence_step_id": "EBR-001",
        "blocker_id": "separate_evidence_builder_request",
        "category": "commercial_sprint_evidence_builder_request_review",
        "status": "ready_for_separate_evidence_builder_request",
        "preferred_human_input_path": "separate_evidence_builder_request",
        "requires_validator_approval_review": False,
        "requires_validator_output_review": False,
        "requires_validator_input_completion": False,
        "requires_validator_rerun_after_completion": False,
        "requires_separate_validator_execution_request": False,
        "requires_separate_evidence_builder_request": True,
        "template_transfer_execution_allowed": False,
        "validator_execution_allowed": False,
        "evidence_builder_execution_allowed": False,
        "execution_allowed_by_summary": False,
        "evidence_collection_authorized": False,
        "blocker_closure_allowed_by_summary": False,
        "default_decision": "hold",
    }
    for key, value in expected_action.items():
        require(action.get(key) == value, f"action {key} must be {value}")
    steps = action.get("next_manual_steps", [])
    require(
        [step.get("step_id") for step in steps] == ["EBR-001", "EBR-002"],
        "next manual steps must be EBR-001/EBR-002",
    )
    require(
        all(step.get("execution_allowed_by_codex") is False for step in steps),
        "manual steps must not allow Codex execution",
    )

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 1, "CSV must contain one row")
    row = rows[0]
    for key, value in {
        "action_id": "NEXT-EBR-001",
        "sequence_step_id": "EBR-001",
        "blocker_id": "separate_evidence_builder_request",
        "status": "ready_for_separate_evidence_builder_request",
        "requires_human_input": "true",
        "execution_allowed_by_summary": "false",
        "blocker_closure_allowed_by_summary": "false",
    }.items():
        require(row.get(key) == value, f"CSV {key} must be {value}")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, README_PATH, DOC_PATH, GATE_PATH]
    )
    for token in [
        "commercial_next_action_summary_v0_1: true",
        "summary_scope: local_commercial_readiness_evidence_builder_request_next_human_action",
        "status: ready_for_separate_evidence_builder_request",
        "first_action_id: NEXT-EBR-001",
        "first_sequence_step_id: EBR-001",
        "first_blocker_id: separate_evidence_builder_request",
        "primary_human_input_lane: commercial_sprint_evidence_builder_request_review",
        "preferred_human_input_path: separate_evidence_builder_request",
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
        "builder_ready_count: 5",
        "blockers_closed_by_validator_run: 0",
        "requires_validator_output_review: false",
        "requires_validator_input_completion: false",
        "requires_validator_rerun_after_completion: false",
        "requires_separate_evidence_builder_request: true",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_next_human_action_guidance: true",
        "recommend_for_validator_approval_review: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_product_launch: false",
    ]:
        require(token in combined, "missing doc token " + token)

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "ready_for_validator_execution: true",
        '"ready_for_validator_execution": true',
        "recommend_for_validator_execution: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_product_launch: true",
    ]
    text = "\n".join([json.dumps(data), combined])
    found = [token for token in forbidden if token in text]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY_SMOKE: PASS "
        "status=ready_for_separate_evidence_builder_request validators_run=true "
        "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
