#!/usr/bin/env python3
"""Smoke test for confirmed-values quick-fill import preview."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_human_confirmed_values_import_preview.py"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview_boundary_audit.md"
PREVIEW_CSV = SPRINT_DIR / "commercial_sprint_human_confirmed_values_quick_fill_preview.local.csv"
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_CONFIRMED_VALUES_IMPORT_PREVIEW_SMOKE: FAIL "
        + message
    )


def require_false(payload: dict, key: str) -> None:
    if payload.get(key) is not False:
        fail(f"{key} must be false")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, PREVIEW_CSV, SOURCE_CSV]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_confirmed_values_import_preview_v0_1": True,
        "status": "superseded_by_all_confirmed_values_pending_workbook_import_approval",
        "preview_type": "local_confirmed_values_to_quick_fill_preview",
        "preview_scope": "local_preview_only_no_source_overwrite_no_workbook_import",
        "source_quick_fill_row_count": 64,
        "source_quick_fill_value_row_count": 64,
        "confirmed_value_row_count": 28,
        "preview_value_row_count": 64,
        "preview_missing_value_row_count": 0,
        "support_contact_preview_value_row_count": 15,
        "pricing_page_preview_value_row_count": 14,
        "remaining_missing_value_row_count": 0,
        "global_remaining_missing_value_row_count": 0,
        "unsafe_pattern_hit_count": 0,
        "boundary_violation_count": 0,
        "local_quick_fill_preview_written": True,
        "ready_for_safety_preflight_review": True,
        "ready_for_workbook_import_approval_review": True,
        "ready_for_full_workbook_import": False,
        "ready_for_template_transfer": False,
        "values_inferred_by_codex": False,
        "human_confirmed_recommended_values_used": True,
        "superseded_by_all_confirmed_values_preview": True,
        "blockers_closed_by_preview": 0,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value}")
    if payload.get("boundary_violations") != []:
        fail("boundary violations must remain empty")
    if payload.get("remaining_missing_by_blocker") != {}:
        fail("remaining missing distribution must be empty after full confirmed source")

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

    preview_rows = read_csv(PREVIEW_CSV)
    source_rows = read_csv(SOURCE_CSV)
    summary_rows = read_csv(OUT_CSV)
    if len(preview_rows) != 64 or len(source_rows) != 64 or len(summary_rows) != 64:
        fail("source, preview, and summary CSVs must contain 64 rows")
    if sum(1 for row in preview_rows if row.get("human_value_to_enter", "").strip()) != 64:
        fail("preview CSV must preserve 64 existing source quick-fill values")
    source_value_count = sum(
        1 for row in source_rows if row.get("human_value_to_enter", "").strip()
    )
    if source_value_count not in {0, 64}:
        fail("official source quick-fill CSV must be blank or fully confirmed")
    if any(row.get("value_imported_to_workbook") != "False" for row in source_rows):
        fail("official source quick-fill import flags must remain false")
    if any(row.get("value_transferred") != "False" for row in source_rows):
        fail("official source quick-fill transfer flags must remain false")
    if any(row.get("template_written") != "False" for row in source_rows):
        fail("official source quick-fill template flags must remain false")

    combined = "\n".join(
        [
            OUT_JSON.read_text(encoding="utf-8"),
            OUT_MD.read_text(encoding="utf-8"),
            OUT_BOUNDARY.read_text(encoding="utf-8"),
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_CONFIRMED_VALUES_IMPORT_PREVIEW_SMOKE: PASS "
        "status=superseded_by_all_confirmed_values_pending_workbook_import_approval "
        "preview_value_row_count=64 preview_missing_value_row_count=0 "
        "source_quick_fill_packet_modified=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
