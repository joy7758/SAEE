#!/usr/bin/env python3
"""Smoke check for the local commercial readiness status snapshot."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"

GO_NO_GO_JSON = COMMERCIAL_DIR / "commercial_go_no_go.local.json"
STATUS_JSON = COMMERCIAL_DIR / "commercial_readiness_status.local.json"
STATUS_MD = COMMERCIAL_DIR / "commercial_readiness_status.md"
STATUS_CSV = COMMERCIAL_DIR / "commercial_readiness_status.csv"
STATUS_HTML = COMMERCIAL_DIR / "commercial_readiness_status.html"
BOUNDARY_MD = COMMERCIAL_DIR / "commercial_readiness_status_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_READINESS_STATUS_SNAPSHOT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_STATUS_SNAPSHOT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_COMMERCIAL_READINESS_STATUS_SNAPSHOT_SMOKE: FAIL: {message}")


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_readiness_status_snapshot.py"],
        cwd=ROOT,
        check=True,
    )
    go_no_go = json.loads(GO_NO_GO_JSON.read_text(encoding="utf-8"))
    snapshot = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    for path in [STATUS_MD, STATUS_CSV, STATUS_HTML, BOUNDARY_MD, TOP_DOC, GATE]:
        require(path.exists(), f"{path.relative_to(ROOT)} must exist")

    expected = {
        "commercial_readiness_status_snapshot_v0_1": True,
        "snapshot_type": "local_default_commercial_readiness_status",
        "status": "ready_for_separate_evidence_builder_request",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "unsatisfied_blocker_count": 24,
        "active_stage": "separate_evidence_builder_request",
        "next_action_summary_status": "ready_for_separate_evidence_builder_request",
        "begin_here_status": "ready_for_separate_evidence_builder_request",
        "preferred_human_input_path": "separate_evidence_builder_request",
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "completed_value_row_count": 64,
        "missing_value_row_count": 0,
        "source_workbook_import_performed": True,
        "source_workbook_written": True,
        "template_transfer_performed": True,
        "template_transfer_values_transferred": True,
        "template_transfer_human_filled_templates_written": True,
        "template_transfer_values_transferred_count": 64,
        "template_transfer_templates_written_count": 5,
        "template_transfer_execution_allowed": False,
        "template_transfer_applier_execution_allowed": False,
        "post_transfer_validator_sequence_status": "ready_for_separate_validator_approval",
        "validator_execution_run_status": "completed_all_validators_passed",
        "validator_hold_output_review_status": "validators_passed_evidence_builder_request_required",
        "validator_hold_output_review_completed": False,
        "validator_outputs_review_required": False,
        "validator_missing_input_completion_required": False,
        "rerun_validators_after_completion_required": False,
        "total_missing_metadata_field_count": 0,
        "total_missing_evidence_item_count": 0,
        "total_missing_source_note_count": 0,
        "planned_validator_count": 5,
        "ready_validator_count": 5,
        "validator_hold_count": 0,
        "validator_pass_count": 5,
        "builder_ready_count": 5,
        "approval_request_count": 5,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "ready_for_validator_approval": False,
        "ready_for_validator_execution": False,
        "validators_run": True,
        "separate_validator_execution_request_required": False,
        "separate_evidence_builder_request_required": True,
        "boundary_violation_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "validators_run_on_real_input": True,
        "real_evidence_created": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
    }
    for key, value in expected.items():
        require(snapshot.get(key) == value, f"{key} must be {value}")
    require(snapshot.get("boundary_violations") == [], "boundary violations must be empty")
    require(go_no_go.get("production_ready") is False, "go/no-go must stay not production-ready")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [STATUS_MD, STATUS_HTML, BOUNDARY_MD, TOP_DOC, GATE]
    )
    for token in [
        "commercial_readiness_status_snapshot_v0_1: true",
        "status: ready_for_separate_evidence_builder_request",
        "active_stage: separate_evidence_builder_request",
        "preferred_human_input_path: separate_evidence_builder_request",
        "preferred_template_missing_value_row_count: 0",
        "template_transfer_performed: true",
        "template_transfer_execution_allowed: false",
        "post_transfer_validator_sequence_status: ready_for_separate_validator_approval",
        "validator_execution_run_status: completed_all_validators_passed",
        "validator_hold_output_review_status: validators_passed_evidence_builder_request_required",
        "validator_hold_output_review_completed: false",
        "validator_outputs_review_required: false",
        "validator_missing_input_completion_required: false",
        "rerun_validators_after_completion_required: false",
        "total_missing_metadata_field_count: 0",
        "total_missing_evidence_item_count: 0",
        "total_missing_source_note_count: 0",
        "ready_validator_count: 5",
        "validator_hold_count: 0",
        "validator_pass_count: 5",
        "builder_ready_count: 5",
        "approved_validator_count: 0",
        "validator_execution_authorized_count: 0",
        "ready_for_validator_approval: false",
        "ready_for_validator_execution: false",
        "separate_evidence_builder_request_required: true",
        "validators_run_on_real_input: true",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]:
        require(token in combined, f"missing doc token: {token}")
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "ready_for_validator_execution: true",
        '"ready_for_validator_execution": true',
    ]:
        require(token not in combined, f"forbidden token found: {token}")

    print(
        "SAEE_COMMERCIAL_READINESS_STATUS_SNAPSHOT_SMOKE: PASS "
        f"status={snapshot['status']} "
        f"production_blocker_count={snapshot['production_blocker_count']} "
        f"missing_value_row_count={snapshot['missing_value_row_count']} "
        "production_ready=false product_launched=false"
    )


if __name__ == "__main__":
    main()
