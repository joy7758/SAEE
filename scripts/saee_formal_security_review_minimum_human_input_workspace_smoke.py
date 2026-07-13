#!/usr/bin/env python3
"""Smoke test for formal-security-review minimum human-input workspace."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "formal_security_review_minimum_human_input_workspace"
)
OUT_JSON = OUT_DIR / "formal_security_review_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "formal_security_review_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "formal_security_review_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "formal_security_review_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "formal_security_review_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
)
GATE = ROOT / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: FAIL: "
        + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_formal_security_review_minimum_human_input_workspace.py",
        ],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "formal_security_review_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_formal_security_review_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "formal_security_review",
        "minimum_required_field_count": 40,
        "minimum_required_human_value_count": 40,
        "filled_value_count": 0,
        "blank_value_count": 40,
        "metadata_field_count": 5,
        "formal_security_review_evidence_key_count": 7,
        "evidence_review_field_count": 7,
        "source_note_field_count": 7,
        "review_artifact_field_count": 21,
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
        "formal_security_review_approved",
        "formal_security_review_completed",
        "formal_security_review_report_approved",
        "formal_security_review_available",
        "formal_security_review_claim_published",
        "security_review_claim_published",
        "production_security_claim_published",
        "production_security_enabled",
        "dependency_review_completed",
        "vulnerability_management_operational",
        "private_core_inspected_by_codex",
        "penetration_test_run_by_codex",
        "codex_performed_security_review",
        "codex_contacted_security_reviewer",
        "codex_contacted_vendor",
        "codex_ran_penetration_test",
        "codex_inspected_private_core",
        "security_vendor_contacted",
        "legal_counsel_contacted",
        "customer_data_processed",
        "customer_data_processing_started",
        "dpa_sent_to_customer",
        "terms_published",
        "privacy_notice_published",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    require(len(payload.get("field_rows", [])) == 40, "field row count")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 40, "CSV must include 40 rows")

    required_field_ids = [
        "formal_security_review_evidence_input.human_reviewer_name",
        "formal_security_review_evidence_input.evidence_review.formal_security_review_report",
        "formal_security_review_evidence_input.source_notes_by_key.formal_security_review_report",
        "formal_security_review_evidence_input.review_artifacts[formal_security_review_report].artifact_reference",
        "formal_security_review_evidence_input.review_artifacts[formal_security_review_report].owner_named",
        "formal_security_review_evidence_input.review_artifacts[formal_security_review_report].reviewed_by_human",
        "formal_security_review_evidence_input.evidence_review.private_core_non_exposure_review_completed",
    ]
    for field_id in required_field_ids:
        require(any(row["field_id"] == field_id for row in rows), "missing " + field_id)

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]
    )
    required_tokens = [
        "formal_security_review_minimum_human_input_workspace_v0_1",
        "status: hold_minimum_human_input_required",
        "minimum_required_field_count: 40",
        "blank_value_count: 40",
        "formal_security_review_completed: false",
        "formal_security_review_approved: false",
        "values_saved_by_workspace: false",
        "form_submission_enabled: false",
        "blocker_closure_authorized: false",
        "private_core_inspected_by_codex: false",
        "penetration_test_run_by_codex: false",
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
        "formal_security_review_completed: true",
        '"formal_security_review_completed": true',
        "formal_security_review_approved: true",
        '"formal_security_review_approved": true',
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
        "SAEE_FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: PASS "
        f"status={payload['status']} fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
