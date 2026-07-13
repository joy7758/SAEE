#!/usr/bin/env python3
"""Smoke check for the commercial sprint human input workbook validator."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR_SMOKE: FAIL: {message}"
    )


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_human_input_workbook.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_human_input_workbook_validator.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_workbook_validator_v0_1": True,
        "validator_type": "local_human_input_workbook_completion_validator",
        "validator_scope": "commercial_sprint_human_input_workbook_completion_only",
        "status": "hold_human_input_required",
        "selected_blocker_count": 5,
        "workbook_row_count": 65,
        "expected_workbook_row_count": 65,
        "required_row_count": 64,
        "completed_required_row_count": 0,
        "missing_required_row_count": 64,
        "workbook_complete": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "human_input_required": True,
        "human_review_required": True,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_validator": 0,
        "boundary_violation_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "customer_contacted": False,
        "vendor_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}, got {payload.get(key)!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")
    if len(payload.get("rows", [])) != 65:
        fail("rows must contain 65 validation rows")
    if any(row.get("human_value_present") is not False for row in payload["rows"] if row.get("minimum_required")):
        fail("default required rows must not have human values")
    if any(row.get("row_complete") is True for row in payload["rows"] if row.get("minimum_required")):
        fail("default required rows must not be complete")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 65:
        fail("validation CSV must contain 65 rows")
    for path in [OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        if not path.exists():
            fail(f"missing artifact: {path}")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_sprint_human_input_workbook_validator_v0_1: true",
        "status: hold_human_input_required",
        "workbook_row_count: 65",
        "missing_required_row_count: 64",
        "ready_for_existing_local_validators: false",
        "human_input_filled_by_codex: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_input_completion_check: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
    ]
    for token in required_tokens:
        if token not in combined:
            fail(f"missing token: {token}")
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_VALIDATOR_SMOKE: PASS "
        f"status={payload['status']} "
        f"workbook_row_count={payload['workbook_row_count']} "
        f"missing_required_row_count={payload['missing_required_row_count']} "
        f"blockers_closed_by_validator={payload['blockers_closed_by_validator']} "
        "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
