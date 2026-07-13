#!/usr/bin/env python3
"""Smoke check for the commercial sprint human input workbook."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_workbook.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_workbook_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_SMOKE: FAIL: {message}")


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_human_input_workbook.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_workbook_v0_1": True,
        "workbook_type": "local_human_input_workbook_for_current_commercial_sprint",
        "workbook_scope": "selected_blocker_human_input_fields_only",
        "status": "hold_human_input_required",
        "selected_blocker_count": 5,
        "workbook_row_count": 65,
        "human_input_required": True,
        "human_review_required": True,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_workbook": 0,
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

    expected_counts = {
        "support_contact": 16,
        "pricing_page": 14,
        "formal_security_review": 12,
        "production_restore_policy": 13,
        "production_monitoring": 10,
    }
    if payload.get("row_counts_by_blocker") != expected_counts:
        fail("unexpected row_counts_by_blocker")
    rows = payload.get("rows", [])
    if len(rows) != 65:
        fail("rows must contain 65 workbook rows")
    if any(row.get("status") != "pending_human_input" for row in rows):
        fail("all workbook rows must remain pending human input")
    if any(row.get("human_value_placeholder") for row in rows):
        fail("workbook rows must not be pre-filled")
    if any(row.get("codex_may_fill") is not False for row in rows):
        fail("Codex must not be allowed to fill workbook rows")
    if any(row.get("human_must_fill") is not True for row in rows):
        fail("all workbook rows must require human input")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 65:
        fail("CSV must contain 65 rows")

    for path in [OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        if not path.exists():
            fail(f"missing artifact: {path}")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_sprint_human_input_workbook_v0_1: true",
        "status: hold_human_input_required",
        "workbook_row_count: 65",
        "human_input_filled_by_codex: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_workbook: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_input_preparation: true",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
    ]
    for token in required_tokens:
        if token not in combined:
            fail(f"missing token: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_SMOKE: PASS "
        f"status={payload['status']} "
        f"workbook_row_count={payload['workbook_row_count']} "
        "human_input_filled_by_codex=false "
        f"blockers_closed_by_workbook={payload['blockers_closed_by_workbook']} "
        "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
