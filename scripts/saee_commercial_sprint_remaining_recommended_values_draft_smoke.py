#!/usr/bin/env python3
"""Smoke test for remaining quick-fill recommended values draft."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
JSON_PATH = BASE / "commercial_sprint_remaining_recommended_values_draft.local.json"
MD_PATH = BASE / "commercial_sprint_remaining_recommended_values_draft.md"
CSV_PATH = BASE / "commercial_sprint_remaining_recommended_values_draft.csv"
BOUNDARY_PATH = BASE / "commercial_sprint_remaining_recommended_values_draft_boundary_audit.md"
SOURCE_QUICK_FILL = BASE / "commercial_sprint_human_input_quick_fill_packet.csv"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_REMAINING_RECOMMENDED_VALUES_DRAFT_SMOKE: FAIL {message}")


def main() -> None:
    for path in [JSON_PATH, MD_PATH, CSV_PATH, BOUNDARY_PATH, SOURCE_QUICK_FILL]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if payload.get("commercial_sprint_remaining_recommended_values_draft_v0_1") is not True:
        fail("version flag missing")
    if payload.get("status") != "pending_human_confirmation_no_import":
        fail("status must remain pending_human_confirmation_no_import")
    if payload.get("draft_row_range") != "QF-029..QF-064":
        fail("draft row range changed")
    if payload.get("draft_row_count") != 36:
        fail("draft row count must be 36")
    if payload.get("human_confirmed") is not False:
        fail("draft must not be marked human confirmed")
    if payload.get("blockers_closed_by_draft") != 0:
        fail("draft must not close blockers")

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
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")

    rows = payload.get("recommended_values", [])
    if len(rows) != 36:
        fail("recommended_values must contain 36 rows")
    expected_ids = [f"QF-{index:03d}" for index in range(29, 65)]
    if [row.get("quick_fill_row_id") for row in rows] != expected_ids:
        fail("recommended row IDs must be QF-029 through QF-064")
    if sum(row.get("closure_effect") == "keeps_blocker_open" for row in rows) < 20:
        fail("draft must keep most remaining production rows on hold")
    if any(row.get("draft_status") == "confirmed" for row in rows):
        fail("draft rows must not be marked confirmed")

    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 36:
        fail("CSV must contain 36 draft rows")

    with SOURCE_QUICK_FILL.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    if len(source_rows) != 64:
        fail("source quick-fill packet must still contain 64 rows")
    source_value_count = sum(
        1 for row in source_rows if row.get("human_value_to_enter", "").strip()
    )
    if source_value_count not in {0, 64}:
        fail("source quick-fill packet must be blank or fully confirmed")
    if any(row.get("value_imported_to_workbook") != "False" for row in source_rows):
        fail("source quick-fill import flags must remain false")
    if any(row.get("value_transferred") != "False" for row in source_rows):
        fail("source quick-fill transfer flags must remain false")
    if any(row.get("template_written") != "False" for row in source_rows):
        fail("source quick-fill template flags must remain false")

    combined = "\n".join(
        [
            JSON_PATH.read_text(encoding="utf-8"),
            MD_PATH.read_text(encoding="utf-8"),
            CSV_PATH.read_text(encoding="utf-8"),
            BOUNDARY_PATH.read_text(encoding="utf-8"),
        ]
    )
    forbidden_tokens = [
        '"human_confirmed": true',
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
        "SAEE_COMMERCIAL_SPRINT_REMAINING_RECOMMENDED_VALUES_DRAFT_SMOKE: PASS "
        "status=pending_human_confirmation_no_import draft_row_count=36 "
        "human_confirmed=false blockers_closed_by_draft=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
