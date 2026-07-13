#!/usr/bin/env python3
"""Smoke check for quick-fill to workbook import dry run."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.local.json"
)
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.csv"
OUT_BOUNDARY = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_all_confirmed_values_source_apply.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py",
        ],
        cwd=ROOT,
        check=True,
    )

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_v0_1": True,
        "dry_run_type": "quick_fill_to_workbook_import_mapping_only",
        "dry_run_scope": "resolve_quick_fill_to_workbook_without_import",
        "status": "ready_for_workbook_import_pending_human_approval",
        "quick_fill_row_count": 64,
        "workbook_row_count": 65,
        "import_mapping_row_count": 64,
        "resolved_import_mapping_row_count": 64,
        "unresolved_import_mapping_row_count": 0,
        "all_import_mappings_resolved": True,
        "value_present_row_count": 64,
        "missing_value_row_count": 0,
        "would_import_row_count": 64,
        "ready_for_workbook_import": True,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_import_dry_run": 0,
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
    if payload.get("unresolved_import_mappings") != []:
        fail("unresolved_import_mappings must remain empty")
    rows = payload.get("dry_run_rows", [])
    if len(rows) != 64:
        fail("dry_run_rows must contain 64 rows")
    if any(row.get("mapping_resolved") is not True for row in rows):
        fail("all dry-run mappings must resolve")
    if any(row.get("human_value_present") is not True for row in rows):
        fail("all dry-run rows should see human-confirmed values")
    if any(row.get("would_import") is not True for row in rows):
        fail("all dry-run rows should be ready to import")
    if any(row.get("workbook_import_performed") is not False for row in rows):
        fail("dry run must not perform workbook import")
    if any(row.get("value_imported_to_workbook") is not False for row in rows):
        fail("dry run must not mark values imported")
    if any(row.get("value_transferred") is not False for row in rows):
        fail("dry run must not transfer values")
    if any(row.get("template_written") is not False for row in rows):
        fail("dry run must not write templates")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("dry-run CSV must contain 64 rows")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_v0_1: true",
        "status: ready_for_workbook_import_pending_human_approval",
        "dry_run_scope: resolve_quick_fill_to_workbook_without_import",
        "quick_fill_row_count: 64",
        "workbook_row_count: 65",
        "import_mapping_row_count: 64",
        "resolved_import_mapping_row_count: 64",
        "unresolved_import_mapping_row_count: 0",
        "all_import_mappings_resolved: true",
        "value_present_row_count: 64",
        "missing_value_row_count: 0",
        "would_import_row_count: 64",
        "ready_for_workbook_import: true",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_import_dry_run: 0",
        "boundary_violation_count: 0",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")

    gate = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: recommend",
        "recommend_for_import_readiness_check: true",
        "recommend_for_human_fill_coordination: true",
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
        ROOT
        / "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN_SMOKE: PASS "
        f"status={payload['status']} "
        f"resolved_import_mapping_row_count={payload['resolved_import_mapping_row_count']} "
        f"value_present_row_count={payload['value_present_row_count']} "
        f"would_import_row_count={payload['would_import_row_count']} "
        f"workbook_import_performed={str(payload['workbook_import_performed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
