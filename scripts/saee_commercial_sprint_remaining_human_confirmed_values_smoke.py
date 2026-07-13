#!/usr/bin/env python3
"""Smoke test for remaining confirmed values and complete quick-fill preview."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_remaining_human_confirmed_values.py"
SOURCE_QUICK_FILL = BASE / "commercial_sprint_human_input_quick_fill_packet.csv"

REMAINING_JSON = BASE / "commercial_sprint_remaining_human_confirmed_recommended_values.local.json"
REMAINING_MD = BASE / "commercial_sprint_remaining_human_confirmed_recommended_values.md"
REMAINING_CSV = BASE / "commercial_sprint_remaining_human_confirmed_recommended_values.csv"
REMAINING_BOUNDARY = BASE / "commercial_sprint_remaining_human_confirmed_recommended_values_boundary_audit.md"

FULL_PREVIEW_JSON = BASE / "commercial_sprint_all_confirmed_values_import_preview.local.json"
FULL_PREVIEW_MD = BASE / "commercial_sprint_all_confirmed_values_import_preview.md"
FULL_PREVIEW_CSV = BASE / "commercial_sprint_all_confirmed_values_import_preview.csv"
FULL_PREVIEW_QUICK_FILL = BASE / "commercial_sprint_all_confirmed_values_quick_fill_preview.local.csv"
FULL_PREVIEW_BOUNDARY = BASE / "commercial_sprint_all_confirmed_values_import_preview_boundary_audit.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_REMAINING_HUMAN_CONFIRMED_VALUES_SMOKE: FAIL {message}")


def require_false(payload: dict, key: str) -> None:
    if payload.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)

    required_files = [
        RUNNER,
        SOURCE_QUICK_FILL,
        REMAINING_JSON,
        REMAINING_MD,
        REMAINING_CSV,
        REMAINING_BOUNDARY,
        FULL_PREVIEW_JSON,
        FULL_PREVIEW_MD,
        FULL_PREVIEW_CSV,
        FULL_PREVIEW_QUICK_FILL,
        FULL_PREVIEW_BOUNDARY,
    ]
    for path in required_files:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    remaining = json.loads(REMAINING_JSON.read_text(encoding="utf-8"))
    full_preview = json.loads(FULL_PREVIEW_JSON.read_text(encoding="utf-8"))

    if remaining.get("commercial_sprint_remaining_human_confirmed_recommended_values_v0_1") is not True:
        fail("remaining confirmed version flag missing")
    if remaining.get("status") != "hold_remaining_confirmed_values_recorded_no_import":
        fail("remaining confirmed status changed")
    if remaining.get("confirmed_row_range") != "QF-029..QF-064":
        fail("remaining confirmed row range changed")
    if remaining.get("confirmed_value_row_count") != 36:
        fail("remaining confirmed value row count must be 36")
    if remaining.get("human_confirmation_source") != "user_reply_all_recommended_confirmed":
        fail("remaining confirmation source changed")
    if remaining.get("keeps_blocker_open_row_count", 0) < 20:
        fail("remaining confirmed values must keep blocker holds visible")
    if remaining.get("boundary_violation_count") != 0:
        fail("remaining confirmed values must have zero boundary violations")
    if remaining.get("unsafe_pattern_hit_count") != 0:
        fail("remaining confirmed values must have zero unsafe pattern hits")

    remaining_values = remaining.get("confirmed_values", [])
    if len(remaining_values) != 36:
        fail("remaining confirmed values must contain 36 rows")
    if [row.get("quick_fill_row_id") for row in remaining_values] != [
        f"QF-{index:03d}" for index in range(29, 65)
    ]:
        fail("remaining confirmed IDs must be QF-029 through QF-064")

    expected_remaining_counts = {
        "formal_security_review_confirmed_rows": 12,
        "pricing_page_confirmed_rows": 1,
        "production_monitoring_confirmed_rows": 10,
        "production_restore_policy_confirmed_rows": 13,
    }
    for key, expected in expected_remaining_counts.items():
        if remaining.get(key) != expected:
            fail(f"{key} must be {expected}")

    if full_preview.get("commercial_sprint_all_confirmed_values_import_preview_v0_1") is not True:
        fail("full preview version flag missing")
    if (
        full_preview.get("status")
        != "stop_boundary_or_safety_issue"
    ):
        fail("full preview status changed")
    expected_full_counts = {
        "source_quick_fill_row_count": 64,
        "initial_confirmed_value_row_count": 28,
        "remaining_confirmed_value_row_count": 36,
        "confirmed_value_row_count": 64,
        "preview_value_row_count": 64,
        "preview_missing_value_row_count": 0,
        "remaining_missing_value_row_count": 0,
        "unsafe_pattern_hit_count": 0,
        "boundary_violation_count": 1,
    }
    for key, expected in expected_full_counts.items():
        if full_preview.get(key) != expected:
            fail(f"{key} must be {expected}")
    if full_preview.get("remaining_missing_by_blocker") != {}:
        fail("full preview must have no remaining missing blockers")
    if full_preview.get("value_counts_by_blocker") != {
        "formal_security_review": 12,
        "pricing_page": 14,
        "production_monitoring": 10,
        "production_restore_policy": 13,
        "support_contact": 15,
    }:
        fail("full preview blocker counts changed")
    if full_preview.get("boundary_violations") != [
        "source_quick_fill_packet_already_contains_values"
    ]:
        fail("full preview must stop because source quick-fill already contains values")
    if full_preview.get("ready_for_safety_preflight_review") is not False:
        fail("full preview safety preflight must stop until source-state conflict is resolved")
    if full_preview.get("ready_for_workbook_import_approval_request") is not False:
        fail("full preview must not request workbook import approval after boundary stop")

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
    for payload in [remaining, full_preview]:
        for flag in false_flags:
            require_false(payload, flag)
        if payload.get("blockers_closed_by_confirmed_values") not in (None, 0):
            fail("confirmed values must not close blockers")
        if payload.get("blockers_closed_by_preview") not in (None, 0):
            fail("preview must not close blockers")

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

    with FULL_PREVIEW_QUICK_FILL.open(newline="", encoding="utf-8") as handle:
        preview_rows = list(csv.DictReader(handle))
    if len(preview_rows) != 64:
        fail("full preview quick-fill CSV must contain 64 rows")
    if sum(bool(row.get("human_value_to_enter")) for row in preview_rows) != 64:
        fail("full preview quick-fill CSV must contain 64 values")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            REMAINING_JSON,
            REMAINING_MD,
            REMAINING_CSV,
            REMAINING_BOUNDARY,
            FULL_PREVIEW_JSON,
            FULL_PREVIEW_MD,
            FULL_PREVIEW_CSV,
            FULL_PREVIEW_BOUNDARY,
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
        "SAEE_COMMERCIAL_SPRINT_REMAINING_HUMAN_CONFIRMED_VALUES_SMOKE: PASS "
        "remaining_confirmed_value_row_count=36 full_preview_value_row_count=64 "
        "preview_missing_value_row_count=0 source_quick_fill_packet_modified=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
