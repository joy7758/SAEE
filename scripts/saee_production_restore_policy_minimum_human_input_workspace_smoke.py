#!/usr/bin/env python3
"""Smoke test for production-restore-policy minimum human-input workspace."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_restore_policy_minimum_human_input_workspace"
)
OUT_JSON = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "production_restore_policy_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
)
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: FAIL: "
        + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_production_restore_policy_minimum_human_input_workspace.py",
        ],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "production_restore_policy_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_production_restore_policy_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "production_restore_policy",
        "minimum_required_field_count": 37,
        "minimum_required_human_value_count": 37,
        "filled_value_count": 0,
        "blank_value_count": 37,
        "metadata_field_count": 7,
        "production_restore_policy_evidence_key_count": 6,
        "policy_evidence_review_field_count": 6,
        "source_note_field_count": 6,
        "policy_evidence_slot_field_count": 18,
        "human_review_required": True,
        "human_input_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected_values.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    false_flags = [
        "production_ready",
        "product_launched",
        "customer_validated",
        "customer_contacted",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "workbook_import_authorized",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "development_permission_granted",
        "production_ready_claim",
        "customer_validation_claim",
        "human_values_generated_by_codex",
        "human_input_filled_by_codex",
        "validator_inputs_exported",
        "validators_run",
        "values_saved_by_workspace",
        "form_submission_enabled",
        "production_restore_policy_approved",
        "production_restore_policy_available",
        "production_restore_policy_claim_published",
        "production_restore_policy_effective_for_customers",
        "restore_policy_published_by_codex",
        "policy_approved_by_codex",
        "restore_tested",
        "restore_to_live_path_enabled",
        "live_restore_performed",
        "live_restore_authorized_by_codex",
        "production_data_path_modified",
        "customer_notification_sent_by_codex",
        "credentials_restored",
        "private_core_restored",
        "codex_contacted_customer",
        "codex_contacted_vendor",
        "codex_inferred_missing_evidence",
        "public_sdk_released",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    require(len(payload.get("field_rows", [])) == 37, "field row count")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 37, "CSV must include 37 rows")

    required_field_ids = [
        "production_restore_policy_approval_input.human_reviewer_name",
        "production_restore_policy_approval_input.policy_evidence_review.production_restore_policy_approved",
        "production_restore_policy_approval_input.source_notes_by_key.production_restore_policy_approved",
        "production_restore_policy_approval_input.policy_evidence_slots[production_restore_policy_approved].evidence_reference",
        "production_restore_policy_approval_input.policy_evidence_slots[production_restore_policy_approved].owner_named",
        "production_restore_policy_approval_input.policy_evidence_slots[production_restore_policy_approved].reviewed_by_human",
        "production_restore_policy_approval_input.policy_evidence_review.tenant_restore_boundary_approved",
    ]
    for field_id in required_field_ids:
        require(any(row["field_id"] == field_id for row in rows), "missing " + field_id)

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]
    )
    required_tokens = [
        "production_restore_policy_minimum_human_input_workspace_v0_1",
        "status: hold_minimum_human_input_required",
        "minimum_required_field_count: 37",
        "blank_value_count: 37",
        "production_restore_policy_approved: false",
        "production_restore_policy_available: false",
        "live_restore_performed: false",
        "production_data_path_modified: false",
        "values_saved_by_workspace: false",
        "form_submission_enabled: false",
        "blocker_closure_authorized: false",
        "customer_contacted: false",
        "private_core_exposed: false",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
    ]
    for token in required_tokens:
        require(token in combined, "missing token " + token)

    forbidden_tokens = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "production_restore_policy_approved: true",
        '"production_restore_policy_approved": true',
        "production_restore_policy_available: true",
        '"production_restore_policy_available": true',
        "live_restore_performed: true",
        '"live_restore_performed": true',
        "production_data_path_modified: true",
        '"production_data_path_modified": true',
        "values_saved_by_workspace: true",
        '"values_saved_by_workspace": true',
        "form_submission_enabled: true",
        '"form_submission_enabled": true',
        "production_ready: true",
        '"production_ready": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
    ]
    for token in forbidden_tokens:
        require(token not in combined, "forbidden token " + token)

    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: PASS "
        f"status={payload['status']} fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
