#!/usr/bin/env python3
"""Smoke test for the local human-confirmed recommended values ledger."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
JSON_PATH = BASE / "commercial_sprint_human_confirmed_recommended_values.local.json"
MD_PATH = BASE / "commercial_sprint_human_confirmed_recommended_values.md"
CSV_PATH = BASE / "commercial_sprint_human_confirmed_recommended_values.csv"
BOUNDARY_PATH = BASE / "commercial_sprint_human_confirmed_recommended_values_boundary_audit.md"
SOURCE_QUICK_FILL = BASE / "commercial_sprint_human_input_quick_fill_packet.csv"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HUMAN_CONFIRMED_RECOMMENDED_VALUES_SMOKE: FAIL {message}")


def require_false(payload: dict, key: str) -> None:
    if payload.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [JSON_PATH, MD_PATH, CSV_PATH, BOUNDARY_PATH, SOURCE_QUICK_FILL]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if payload.get("commercial_sprint_human_confirmed_recommended_values_v0_1") is not True:
        fail("ledger version flag missing")
    if payload.get("status") != "hold_confirmed_values_recorded_no_import":
        fail("ledger status changed")
    if payload.get("record_type") != "local_human_confirmed_recommended_values_ledger":
        fail("ledger record type changed")
    if payload.get("confirmed_value_row_count") != 28:
        fail("confirmed value row count must be 28")
    if payload.get("support_contact_confirmed_rows") != 15:
        fail("support contact confirmed row count must be 15")
    if payload.get("pricing_page_confirmed_rows") != 13:
        fail("pricing page confirmed row count must be 13")

    false_flags = [
        "source_quick_fill_packet_modified",
        "quick_fill_imported_to_workbook",
        "workbook_import_performed",
        "workbook_written",
        "values_transferred",
        "human_filled_templates_written",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
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
    ]
    for flag in false_flags:
        require_false(payload, flag)
    if payload.get("blockers_closed_by_confirmed_values") != 0:
        fail("confirmed values must not close blockers")

    values = payload.get("confirmed_values", [])
    if len(values) != 28:
        fail("confirmed_values must contain 28 records")
    row_ids = [row.get("quick_fill_row_id") for row in values]
    expected_ids = [f"QF-{i:03d}" for i in range(1, 29)]
    if row_ids != expected_ids:
        fail("confirmed row IDs must be QF-001 through QF-028 only")
    if "QF-029" in row_ids:
        fail("QF-029 must not be recorded as confirmed")
    holds = [row for row in values if row.get("closure_effect") == "keeps_blocker_open"]
    if len(holds) < 8:
        fail("ledger must preserve hold rows instead of closing blockers")

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    if len(csv_rows) != 28:
        fail("CSV must contain 28 data rows")

    with SOURCE_QUICK_FILL.open(newline="", encoding="utf-8") as f:
        source_rows = list(csv.DictReader(f))
    if len(source_rows) != 64:
        fail("source quick-fill packet must still contain 64 rows")
    source_value_count = sum(
        1 for row in source_rows if row.get("human_value_to_enter", "").strip()
    )
    if source_value_count not in {0, 64}:
        fail("source quick-fill packet must be blank or fully confirmed")
    if any(row.get("value_imported_to_workbook") != "False" for row in source_rows):
        fail("source quick-fill packet import flags must remain false")
    if any(row.get("value_transferred") != "False" for row in source_rows):
        fail("source quick-fill packet transfer flags must remain false")
    if any(row.get("template_written") != "False" for row in source_rows):
        fail("source quick-fill packet template flags must remain false")

    combined = "\n".join(
        [
            JSON_PATH.read_text(encoding="utf-8"),
            MD_PATH.read_text(encoding="utf-8"),
            CSV_PATH.read_text(encoding="utf-8"),
            BOUNDARY_PATH.read_text(encoding="utf-8"),
        ]
    )
    forbidden_tokens = [
        '"production_ready": true',
        "production_ready: true",
        '"product_launched": true',
        "product_launched: true",
        '"customer_validated": true',
        "customer_validated: true",
        '"customer_contacted": true',
        "customer_contacted: true",
        '"private_core_exposed": true',
        "private_core_exposed: true",
        '"quick_fill_imported_to_workbook": true',
        '"workbook_written": true',
        '"values_transferred": true',
        '"validators_run_on_real_input": true',
        '"execution_authorized": true',
        '"blocker_closure_authorized": true',
    ]
    found = [token for token in forbidden_tokens if token in combined]
    if found:
        fail("forbidden claim found: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_CONFIRMED_RECOMMENDED_VALUES_SMOKE: PASS "
        "status=hold_confirmed_values_recorded_no_import confirmed_value_row_count=28 "
        "blockers_closed_by_confirmed_values=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
