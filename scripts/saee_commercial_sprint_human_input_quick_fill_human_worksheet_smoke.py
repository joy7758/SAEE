#!/usr/bin/env python3
"""Smoke check for the commercial sprint human quick-fill worksheet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET_RECOMMENDATION_GATE.md"
)
COMPLETED_STATUS = "completed_human_quick_fill_pending_workbook_import_approval"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_quick_fill_human_worksheet_v0_1": True,
        "worksheet_type": "human_quick_fill_entry_worksheet",
        "worksheet_scope": "manual_human_entry_review_only_no_import",
        "status": COMPLETED_STATUS,
        "quick_fill_row_count": 64,
        "worksheet_row_count": 64,
        "blocker_count": 5,
        "input_group_count": 9,
        "input_kind_count": 3,
        "blank_human_value_row_count": 0,
        "nonblank_human_value_row_count": 64,
        "suggested_values_count": 0,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_human_quick_fill": False,
        "ready_for_workbook_import_approval_review": True,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "human_value_prefilled_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_worksheet": 0,
        "boundary_violation_count": 0,
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
        "task_candidates_executed": False,
        "payment_collected": False,
        "revenue_validated": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must remain empty")
    rows = payload.get("worksheet_rows", [])
    if len(rows) != 64:
        fail("worksheet_rows must contain 64 rows")
    if sum(1 for row in rows if row.get("human_value_to_enter")) != 64:
        fail("worksheet rows must contain 64 human-confirmed values")
    if sum(1 for row in rows if row.get("notes_for_human")) != 64:
        fail("worksheet rows must contain 64 human-confirmed notes")
    if any(row.get("codex_filled_value") for row in rows):
        fail("Codex must not fill values")
    if any(row.get("workbook_import_performed") for row in rows):
        fail("worksheet must not import workbook")
    if any(row.get("validators_run_on_real_input") for row in rows):
        fail("worksheet must not run validators on real input")
    if any(row.get("evidence_collection_authorized") for row in rows):
        fail("worksheet must not authorize evidence collection")
    if any(row.get("execution_authorized") for row in rows):
        fail("worksheet must not authorize execution")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("worksheet CSV must contain 64 rows")
    if sum(1 for row in csv_rows if row.get("human_value_to_enter")) != 64:
        fail("worksheet CSV human value cells must contain 64 human-confirmed values")
    if sum(1 for row in csv_rows if row.get("notes_for_human")) != 64:
        fail("worksheet CSV note cells must contain 64 human-confirmed notes")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_human_worksheet_v0_1: true",
        f"status: {COMPLETED_STATUS}",
        "worksheet_scope: manual_human_entry_review_only_no_import",
        "quick_fill_row_count: 64",
        "worksheet_row_count: 64",
        "blocker_count: 5",
        "input_group_count: 9",
        "input_kind_count: 3",
        "blank_human_value_row_count: 0",
        "nonblank_human_value_row_count: 64",
        "ready_for_workbook_import_approval_review: true",
        "suggested_values_count: 0",
        "human_value_prefilled_by_codex: false",
        "quick_fill_values_entered_by_codex: false",
        "human_input_filled_by_codex: false",
        "workbook_import_authorized: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "validators_run_on_real_input: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_worksheet: 0",
        "boundary_violation_count: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")

    gate = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: recommend",
        "recommend_for_human_quick_fill_entry_support: true",
        "recommend_for_human_fill_coordination: true",
        "recommend_for_value_generation: false",
        "recommend_for_value_suggestion: false",
        "recommend_for_value_import: false",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in gate:
            fail(f"gate missing token {token}")

    runner = (
        ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET_SMOKE: PASS "
        f"status={payload['status']} "
        f"worksheet_row_count={payload['worksheet_row_count']} "
        f"blank_human_value_row_count={payload['blank_human_value_row_count']} "
        f"suggested_values_count={payload['suggested_values_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
