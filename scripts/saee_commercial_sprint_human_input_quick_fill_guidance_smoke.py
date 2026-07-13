#!/usr/bin/env python3
"""Smoke check for commercial sprint quick-fill guidance."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_human_input_quick_fill_guidance.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_quick_fill_guidance_v0_1": True,
        "guidance_type": "row_level_human_quick_fill_guidance",
        "guidance_scope": "human_fill_guidance_only_no_values_no_import",
        "status": "ready_for_human_quick_fill",
        "guidance_row_count": 64,
        "quick_fill_row_count": 64,
        "unique_blocker_count": 5,
        "unique_input_group_count": 9,
        "unique_input_kind_count": 3,
        "suggested_values_count": 0,
        "actual_values_provided_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "ready_for_human_fill": True,
        "ready_for_workbook_import": False,
        "quick_fill_values_entered_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_guidance": 0,
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
    rows = payload.get("guidance_rows", [])
    if len(rows) != 64:
        fail("guidance_rows must contain 64 rows")
    if any(row.get("suggested_value") for row in rows):
        fail("guidance must not include actual suggested values")
    if any(row.get("actual_value_provided") for row in rows):
        fail("guidance must not mark actual values provided")
    if any(row.get("codex_filled_value") for row in rows):
        fail("guidance must not fill values by Codex")
    if any(row.get("workbook_import_performed") for row in rows):
        fail("guidance must not import workbook")
    if any(row.get("value_transferred") for row in rows):
        fail("guidance must not transfer values")
    if any(row.get("template_written") for row in rows):
        fail("guidance must not write templates")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("guidance CSV must contain 64 rows")
    if any(row.get("suggested_value") for row in csv_rows):
        fail("guidance CSV suggested_value cells must be blank")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_guidance_v0_1: true",
        "status: ready_for_human_quick_fill",
        "guidance_scope: human_fill_guidance_only_no_values_no_import",
        "guidance_row_count: 64",
        "quick_fill_row_count: 64",
        "unique_blocker_count: 5",
        "unique_input_group_count: 9",
        "unique_input_kind_count: 3",
        "suggested_values_count: 0",
        "actual_values_provided_count: 0",
        "ready_for_human_fill: true",
        "ready_for_workbook_import: false",
        "quick_fill_values_entered_by_codex: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_guidance: 0",
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
        "recommend_for_human_fill_guidance: true",
        "recommend_for_human_fill_coordination: true",
        "recommend_for_value_suggestion: false",
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
        ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_guidance.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE_SMOKE: PASS "
        f"status={payload['status']} "
        f"guidance_row_count={payload['guidance_row_count']} "
        f"suggested_values_count={payload['suggested_values_count']} "
        f"ready_for_human_fill={str(payload['ready_for_human_fill']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
