#!/usr/bin/env python3
"""Smoke test for the all-confirmed quick-fill preview safety preflight."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_all_confirmed_values_safety_preflight.py"
SOURCE_PREVIEW_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_quick_fill_preview.local.csv"
SOURCE_OFFICIAL_QUICK_FILL = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight_boundary_audit.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SAFETY_PREFLIGHT_SMOKE: "
        f"FAIL {message}"
    )


def require_false(payload: dict, key: str) -> None:
    if payload.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)
    for path in [RUNNER, SOURCE_PREVIEW_CSV, SOURCE_OFFICIAL_QUICK_FILL, OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_all_confirmed_values_safety_preflight_v0_1": True,
        "preflight_type": "local_all_confirmed_values_preview_safety_preflight",
        "preflight_scope": "all_confirmed_preview_values_only_no_source_overwrite_no_workbook_import",
        "status": "pass_no_sensitive_values_found_pending_import_approval",
        "source_preview_confirmed_value_row_count": 64,
        "source_preview_missing_value_row_count": 0,
        "rows_scanned_count": 64,
        "filled_value_row_count": 64,
        "blank_value_row_count": 0,
        "secret_pattern_hit_count": 0,
        "private_core_reference_count": 0,
        "production_overclaim_count": 0,
        "customer_validation_claim_count": 0,
        "product_launch_claim_count": 0,
        "external_validation_claim_count": 0,
        "unsafe_row_count": 0,
        "base_warning_row_count": 0,
        "benign_date_warning_count": 0,
        "unresolved_warning_count": 0,
        "boundary_violation_count": 0,
        "safe_to_import_after_human_approval": True,
        "ready_for_workbook_import_approval_request": True,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}, got {payload.get(key)!r}")

    false_flags = [
        "source_quick_fill_packet_modified",
        "quick_fill_imported_to_workbook",
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
        "development_permission_granted",
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
        "payment_collected",
        "revenue_validated",
        "raw_values_recorded",
        "ready_for_workbook_import_execution",
        "ready_for_full_workbook_import",
    ]
    for flag in false_flags:
        require_false(payload, flag)

    rows = payload.get("row_summaries", [])
    if len(rows) != 64:
        fail("row_summaries must contain 64 rows")
    if any(row.get("unresolved_warning_patterns") for row in rows):
        fail("row_summaries must not contain unresolved warnings")
    if sum(bool(row.get("benign_warning_patterns")) for row in rows) != payload["benign_date_warning_count"]:
        fail("benign warning row count must match payload")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("preflight CSV must contain 64 rows")
    raw_columns = {"human_value_to_enter", "notes_for_human"}
    if raw_columns.intersection(csv_rows[0].keys()):
        fail("preflight CSV must not expose raw human value columns")

    with SOURCE_OFFICIAL_QUICK_FILL.open("r", encoding="utf-8", newline="") as handle:
        official_rows = list(csv.DictReader(handle))
    if len(official_rows) != 64:
        fail("official quick-fill packet must still contain 64 rows")
    if sum(bool((row.get("human_value_to_enter") or "").strip()) for row in official_rows) != 64:
        fail("official quick-fill packet must contain 64 confirmed values")
    if any(row.get("value_imported_to_workbook") != "False" for row in official_rows):
        fail("official import flags must remain false")
    if any(row.get("value_transferred") != "False" for row in official_rows):
        fail("official transfer flags must remain false")
    if any(row.get("template_written") != "False" for row in official_rows):
        fail("official template flags must remain false")

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY])
    required_tokens = [
        "commercial_sprint_all_confirmed_values_safety_preflight_v0_1: true",
        "status: pass_no_sensitive_values_found_pending_import_approval",
        "rows_scanned_count: 64",
        "filled_value_row_count: 64",
        "secret_pattern_hit_count: 0",
        "benign_date_warning_count: 0",
        "unresolved_warning_count: 0",
        "safe_to_import_after_human_approval: true",
        "ready_for_workbook_import_execution: false",
        "source_quick_fill_packet_modified: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "validators_run_on_real_input: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "does not modify the official quick-fill packet",
    ]
    missing = [token for token in required_tokens if token not in docs]
    if missing:
        fail("docs missing tokens: " + ", ".join(missing))
    forbidden = [
        "ready_for_workbook_import_execution: true",
        "quick_fill_imported_to_workbook: true",
        "workbook_import_performed: true",
        "validators_run_on_real_input: true",
        "blocker_closure_authorized: true",
        "production_ready: true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
    ]
    found = [token for token in forbidden if token in docs]
    if found:
        fail("docs contain forbidden tokens: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SAFETY_PREFLIGHT_SMOKE: PASS "
        f"rows_scanned_count={payload['rows_scanned_count']} "
        f"secret_pattern_hit_count={payload['secret_pattern_hit_count']} "
        f"benign_date_warning_count={payload['benign_date_warning_count']} "
        f"unresolved_warning_count={payload['unresolved_warning_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
