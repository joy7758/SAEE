#!/usr/bin/env python3
"""Smoke test for applying all confirmed values to the quick-fill source."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_all_confirmed_values_source_apply.py"
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
SOURCE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply_boundary_audit.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY_V0_1.md"
)
GATE = (
    ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY_SMOKE: FAIL "
        + message
    )


def read_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)

    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE, SOURCE_JSON]:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    payload = read_json(OUT_JSON)
    source_payload = read_json(SOURCE_JSON)
    expected = {
        "commercial_sprint_all_confirmed_values_source_apply_v0_1": True,
        "status": "source_values_applied_pending_safety_preflight",
        "apply_scope": "copy_human_confirmed_preview_values_to_official_quick_fill_source_only",
        "source_quick_fill_row_count": 64,
        "preview_value_row_count": 64,
        "applied_value_row_count": 64,
        "missing_preview_value_row_count": 0,
        "source_quick_fill_packet_modified": True,
        "ready_for_safety_preflight": True,
        "ready_for_workbook_import": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_source_apply": 0,
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
        "payment_collected": False,
        "revenue_validated": False,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"{key} must be {expected_value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")
    source_expected = {
        "status": "human_confirmed_values_present_pending_safety_preflight",
        "packet_scope": "human_confirmed_quick_fill_source_only_no_import_no_transfer",
        "quick_fill_row_count": 64,
        "blank_value_row_count": 0,
        "confirmed_value_row_count": 64,
        "quick_fill_values_entered_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "ready_for_safety_preflight": True,
        "ready_for_workbook_import": False,
        "blockers_closed_by_quick_fill_packet": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }
    for key, expected_value in source_expected.items():
        if source_payload.get(key) != expected_value:
            fail(f"source payload {key} must be {expected_value!r}")

    source_rows = read_csv(SOURCE_CSV)
    if len(source_rows) != 64:
        fail("source CSV must contain 64 rows")
    if sum(bool(row.get("human_value_to_enter", "").strip()) for row in source_rows) != 64:
        fail("source CSV must contain 64 human-confirmed values")
    for flag in ["value_imported_to_workbook", "value_transferred", "template_written"]:
        if any(row.get(flag) != "False" for row in source_rows):
            fail(f"source CSV {flag} must remain False")
    if any(
        row.get("quick_fill_status") != "human_confirmed_value_present_pending_safety_preflight"
        for row in source_rows
    ):
        fail("source CSV quick_fill_status must reflect pending safety preflight")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_JSON, OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_sprint_all_confirmed_values_source_apply_v0_1: true",
        "status: source_values_applied_pending_safety_preflight",
        "source_quick_fill_packet_modified: true",
        "applied_value_row_count: 64",
        "ready_for_safety_preflight: true",
        "ready_for_workbook_import: false",
        "workbook_import_performed: false",
        "validators_run_on_real_input: false",
        "blockers_closed_by_source_apply: 0",
        "production_ready: false",
    ]
    for token in required_tokens:
        if token not in combined:
            fail(f"missing doc token {token}")
    forbidden_tokens = [
        "workbook_import_performed: true",
        "workbook_written: true",
        "values_transferred: true",
        "validators_run_on_real_input: true",
        "evidence_collection_authorized: true",
        "execution_authorized: true",
        "blocker_closure_authorized: true",
        "production_ready: true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    if found:
        fail("forbidden true claim found: " + ", ".join(found))

    runner_text = RUNNER.read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner_text:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY_SMOKE: PASS "
        "status=source_values_applied_pending_safety_preflight "
        "applied_value_row_count=64 workbook_import_performed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
