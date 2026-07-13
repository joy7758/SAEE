#!/usr/bin/env python3
"""Smoke check for controlled quick-fill workbook importer."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER_RECOMMENDATION_GATE.md"
)
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER_SMOKE: "
        f"FAIL: {message}"
    )


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_default() -> dict:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py",
        ],
        cwd=ROOT,
        check=True,
    )
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))


def assert_default_payload(payload: dict) -> None:
    expected = {
        "commercial_sprint_human_input_quick_fill_workbook_importer_v0_1": True,
        "importer_type": "controlled_quick_fill_to_workbook_importer",
        "importer_scope": "quick_fill_to_workbook_only_no_template_transfer_no_evidence",
        "status": "ready_for_apply_pending_explicit_human_command",
        "execution_mode": "dry_run_no_write",
        "quick_fill_row_count": 64,
        "workbook_row_count": 65,
        "import_candidate_row_count": 64,
        "resolved_import_mapping_row_count": 64,
        "unresolved_import_mapping_row_count": 0,
        "all_import_mappings_resolved": True,
        "value_present_row_count": 64,
        "missing_value_row_count": 0,
        "import_ready_row_count": 64,
        "apply_requested": False,
        "human_import_confirmation_provided": False,
        "apply_preconditions_met": False,
        "apply_performed": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "ready_for_workbook_import": True,
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
        "blockers_closed_by_importer": 0,
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
        fail("default importer boundary violations must remain empty")
    rows = payload.get("import_rows", [])
    if len(rows) != 64:
        fail("default importer must contain 64 import rows")
    if any(row.get("human_value_present") is not True for row in rows):
        fail("default importer must see all 64 human-confirmed values")
    if any(row.get("import_ready") is not True for row in rows):
        fail("default importer must mark all 64 rows import-ready")
    if any(row.get("value_imported_to_workbook") for row in rows):
        fail("default importer must not mark workbook import")


def assert_docs() -> None:
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_workbook_importer_v0_1: true",
        "status: ready_for_apply_pending_explicit_human_command",
        "execution_mode: dry_run_no_write",
        "importer_scope: quick_fill_to_workbook_only_no_template_transfer_no_evidence",
        "quick_fill_row_count: 64",
        "workbook_row_count: 65",
        "import_candidate_row_count: 64",
        "resolved_import_mapping_row_count: 64",
        "unresolved_import_mapping_row_count: 0",
        "value_present_row_count: 64",
        "missing_value_row_count: 0",
        "import_ready_row_count: 64",
        "apply_requested: false",
        "human_import_confirmation_provided: false",
        "apply_performed: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "ready_for_workbook_import: true",
        "ready_for_template_transfer: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_importer: 0",
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
        "answer: conditional",
        "recommend_for_import_readiness_check: true",
        "recommend_for_human_approved_workbook_import: true",
        "recommend_for_unapproved_import: false",
        "recommend_for_value_inference: false",
        "recommend_for_value_suggestion: false",
        "recommend_for_template_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in gate:
            fail(f"gate missing token {token}")
    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 64:
        fail("importer CSV must contain 64 rows")


def assert_apply_fixture() -> None:
    with tempfile.TemporaryDirectory() as temp:
        tempdir = Path(temp)
        tmp_quick = tempdir / "quick_fill.csv"
        tmp_workbook = tempdir / "workbook.csv"
        tmp_output = tempdir / "workbook.imported.csv"
        shutil.copy2(WORKBOOK_CSV, tmp_workbook)
        quick_fields, quick_rows = load_csv(QUICK_FILL_CSV)
        for row in quick_rows:
            row["human_value_to_enter"] = f"human-approved-value-{row['quick_fill_row_id']}"
            row["target_workbook_csv"] = str(tmp_workbook.resolve())
        write_csv(tmp_quick, quick_fields, quick_rows)
        subprocess.run(
            [
                sys.executable,
                "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py",
                "--quick-fill-csv",
                str(tmp_quick),
                "--workbook-csv",
                str(tmp_workbook),
                "--output-workbook-csv",
                str(tmp_output),
                "--apply",
                "--confirm-human-approved-import",
            ],
            cwd=ROOT,
            check=True,
        )
        if not tmp_output.exists():
            fail("apply fixture must write output workbook")
        _, out_rows = load_csv(tmp_output)
        imported_values = [row["human_value_placeholder"] for row in out_rows if row["workbook_row_id"] != "WB-016"]
        if len(imported_values) != 64:
            fail("apply fixture output must retain 64 imported target rows")
        if any(not value.startswith("human-approved-value-QF-") for value in imported_values):
            fail("apply fixture must import human-approved quick-fill values")
        apply_payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if apply_payload.get("apply_performed") is not True:
            fail("apply fixture payload must record apply_performed true")
        if apply_payload.get("workbook_written") is not True:
            fail("apply fixture payload must record workbook_written true")
    # Leave repository artifacts in default dry-run state.
    payload = run_default()
    assert_default_payload(payload)


def main() -> int:
    payload = run_default()
    assert_default_payload(payload)
    assert_docs()
    assert_apply_fixture()

    runner = (
        ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER_SMOKE: PASS "
        f"status={payload['status']} "
        f"execution_mode={payload['execution_mode']} "
        f"import_ready_row_count={payload['import_ready_row_count']} "
        f"apply_performed={str(payload['apply_performed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
