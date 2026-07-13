#!/usr/bin/env python3
"""Smoke test for pricing-page minimum human-input workspace."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "pricing_page_minimum_human_input_workspace"
)
OUT_JSON = OUT_DIR / "pricing_page_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "pricing_page_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "pricing_page_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "pricing_page_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "pricing_page_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: FAIL: " + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_pricing_page_minimum_human_input_workspace.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "pricing_page_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_pricing_page_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "pricing_page",
        "minimum_required_field_count": 34,
        "minimum_required_human_value_count": 34,
        "filled_value_count": 0,
        "blank_value_count": 34,
        "metadata_field_count": 9,
        "pricing_page_evidence_key_count": 5,
        "evidence_review_field_count": 5,
        "source_note_field_count": 5,
        "review_artifact_field_count": 15,
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
        "pricing_page_approved",
        "pricing_page_published",
        "pricing_page_claim_published",
        "pricing_page_publication_approved",
        "pricing_page_completed",
        "customer_facing_pricing_page_created",
        "sales_offer_generated",
        "sales_offer_sent",
        "payment_provider_configured",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "production_billing_enabled",
        "paid_product_launched",
        "enterprise_contract_signed",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")

    field_rows = payload.get("field_rows", [])
    require(len(field_rows) == 34, "field row count")
    required_field_ids = [
        "pricing_page_evidence_input.human_reviewer_name",
        "pricing_page_evidence_input.evidence_review.human_approved_pricing_page_copy",
        "pricing_page_evidence_input.source_notes_by_key.human_approved_pricing_page_copy",
        "pricing_page_evidence_input.review_artifacts[human_approved_pricing_page_copy].artifact_reference",
        "pricing_page_evidence_input.review_artifacts[human_approved_pricing_page_copy].owner_named",
        "pricing_page_evidence_input.review_artifacts[human_approved_pricing_page_copy].reviewed_by_human",
    ]
    for field_id in required_field_ids:
        require(any(row["field_id"] == field_id for row in field_rows), "missing " + field_id)

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 34, "CSV must include 34 rows")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]
    )
    required_tokens = [
        "pricing_page_minimum_human_input_workspace_v0_1",
        "status: hold_minimum_human_input_required",
        "minimum_required_field_count: 34",
        "blank_value_count: 34",
        "pricing_page_approved: false",
        "pricing_page_published: false",
        "values_saved_by_workspace: false",
        "form_submission_enabled: false",
        "blocker_closure_authorized: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_contacted: false",
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
        "pricing_page_published: true",
        '"pricing_page_published": true',
        "pricing_page_approved: true",
        '"pricing_page_approved": true',
        "values_saved_by_workspace: true",
        '"values_saved_by_workspace": true',
        "form_submission_enabled: true",
        '"form_submission_enabled": true',
        "production_ready: true",
        '"production_ready": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
    ]
    for token in forbidden_tokens:
        require(token not in combined, "forbidden token " + token)

    print(
        "SAEE_PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE_SMOKE: PASS "
        f"status={payload['status']} fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
