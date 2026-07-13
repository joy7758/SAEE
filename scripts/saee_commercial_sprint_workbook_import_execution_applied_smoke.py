#!/usr/bin/env python3
"""Smoke check for the commercial sprint workbook import execution record."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
JSON_PATH = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.local.json"
MD_PATH = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.md"
CSV_PATH = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.csv"
BOUNDARY_PATH = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied_boundary_audit.md"
IMPORTED_WORKBOOK = SPRINT_DIR / "commercial_sprint_human_input_workbook.imported_from_quick_fill.local.csv"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    for path in [JSON_PATH, MD_PATH, CSV_PATH, BOUNDARY_PATH, IMPORTED_WORKBOOK, TOP_DOC, GATE]:
        if not path.is_file():
            fail(f"missing {path}")

    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_workbook_import_execution_applied_v0_1": True,
        "execution_type": "human_authorized_local_workbook_import",
        "execution_scope": "quick_fill_to_local_workbook_csv_only",
        "status": "workbook_import_applied_pending_template_transfer_request",
        "human_execution_authorized": True,
        "human_execution_request_recorded": True,
        "workbook_import_authorized": True,
        "workbook_import_performed": True,
        "workbook_written": True,
        "workbook_row_count": 65,
        "imported_value_row_count": 64,
        "pending_value_row_count": 1,
        "ready_for_template_transfer_request": True,
        "template_transfer_authorized": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "validators_run_on_real_input": False,
        "ready_for_validator_execution": False,
        "validator_execution_authorized": False,
        "evidence_collection_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_workbook_import": 0,
        "real_evidence_created": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "payment_collected": False,
        "revenue_validated": False,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")
    rows = payload.get("rows", [])
    if len(rows) != 65:
        fail("payload rows must contain 65 workbook rows")
    if sum(1 for row in rows if row.get("imported_from_quick_fill")) != 64:
        fail("exactly 64 rows must be imported from quick fill")

    with IMPORTED_WORKBOOK.open("r", encoding="utf-8", newline="") as handle:
        workbook_rows = list(csv.DictReader(handle))
    if len(workbook_rows) != 65:
        fail("imported workbook must contain 65 rows")
    if sum(1 for row in workbook_rows if row.get("human_value_placeholder", "").strip()) != 64:
        fail("imported workbook must contain 64 human values")

    required_tokens = [
        "workbook_import_performed: true",
        "workbook_written: true",
        "template_transfer_authorized: false",
        "values_transferred: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "blockers_closed_by_workbook_import: 0",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "private_core_exposed: false",
    ]
    for path in [MD_PATH, BOUNDARY_PATH, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED_SMOKE: PASS "
        "imported_value_row_count=64 template_transfer_authorized=false production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
