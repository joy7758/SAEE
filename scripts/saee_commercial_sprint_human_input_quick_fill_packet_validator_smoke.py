#!/usr/bin/env python3
"""Smoke check for commercial sprint quick-fill packet completion validator."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_all_confirmed_values_source_apply.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py"],
        cwd=ROOT,
        check=True,
    )

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_quick_fill_packet_validator_v0_1": True,
        "validator_type": "local_quick_fill_completion_validator",
        "validator_scope": "quick_fill_human_value_completion_only_no_import_no_transfer",
        "status": "ready_for_workbook_import_pending_human_approval",
        "quick_fill_row_count": 64,
        "required_quick_fill_row_count": 64,
        "completed_quick_fill_row_count": 64,
        "missing_quick_fill_row_count": 0,
        "quick_fill_complete": True,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_workbook_import": True,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "quick_fill_values_entered_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_quick_fill_validator": 0,
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
    if payload.get("duplicate_quick_fill_row_ids") != []:
        fail("duplicate_quick_fill_row_ids must remain empty")
    rows = payload.get("validation_rows", [])
    if len(rows) != 64:
        fail("validation_rows must contain 64 rows")
    if any(row.get("human_value_present") is not True for row in rows):
        fail("validation rows must show all human-confirmed values")
    if any(row.get("row_complete") is not True for row in rows):
        fail("validation rows must be complete after human confirmation")
    if any(row.get("status") != "complete_pending_human_approved_workbook_import" for row in rows):
        fail("all validation rows should be complete pending human-approved workbook import")
    if any(row.get("value_imported_to_workbook") is not False for row in rows):
        fail("validation rows must not import values")
    if any(row.get("value_transferred") is not False for row in rows):
        fail("validation rows must not transfer values")
    if any(row.get("template_written") is not False for row in rows):
        fail("validation rows must not write templates")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("validation CSV must contain 64 rows")
    if any(row.get("row_complete") != "True" for row in csv_rows):
        fail("validation CSV rows must be complete")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_packet_validator_v0_1: true",
        "status: ready_for_workbook_import_pending_human_approval",
        "validator_scope: quick_fill_human_value_completion_only_no_import_no_transfer",
        "quick_fill_row_count: 64",
        "required_quick_fill_row_count: 64",
        "completed_quick_fill_row_count: 64",
        "missing_quick_fill_row_count: 0",
        "quick_fill_complete: true",
        "ready_for_workbook_import: true",
        "quick_fill_values_entered_by_codex: false",
        "quick_fill_imported_to_workbook: false",
        "human_input_filled_by_codex: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_quick_fill_validator: 0",
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
        "recommend_for_completion_validation: true",
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
        ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR_SMOKE: PASS "
        f"status={payload['status']} "
        f"completed_quick_fill_row_count={payload['completed_quick_fill_row_count']} "
        f"missing_quick_fill_row_count={payload['missing_quick_fill_row_count']} "
        f"ready_for_workbook_import={str(payload['ready_for_workbook_import']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
