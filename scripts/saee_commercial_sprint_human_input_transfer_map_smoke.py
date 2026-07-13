#!/usr/bin/env python3
"""Smoke check for the commercial sprint human input transfer map."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_transfer_map_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP_SMOKE: FAIL: {message}"
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
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_human_input_transfer_map.py"],
        cwd=ROOT,
        check=True,
    )

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_transfer_map_v0_1": True,
        "map_type": "local_workbook_to_human_filled_template_mapping",
        "map_scope": "mapping_only_no_value_transfer",
        "status": "hold_human_input_required",
        "selected_blocker_count": 5,
        "workbook_row_count": 65,
        "required_row_count": 64,
        "completed_required_row_count": 0,
        "missing_required_row_count": 64,
        "target_template_count": 5,
        "source_template_count": 6,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "values_transferred": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_transfer_map": 0,
        "boundary_violation_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
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
    rows = payload.get("mapping_rows", [])
    if len(rows) != 65:
        fail("mapping_rows must contain 65 rows")
    if any(row.get("value_transferred") is not False for row in rows):
        fail("no row may transfer a value")
    if any(row.get("transfer_ready") is not False for row in rows):
        fail("no row may be transfer-ready before human input")
    if len(payload.get("target_summaries", [])) != 5:
        fail("target_summaries must contain 5 targets")
    if any(target.get("values_transferred") is not False for target in payload["target_summaries"]):
        fail("target summaries must not mark transferred values")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 65:
        fail("CSV must contain 65 mapping rows")
    required_tokens = [
        "commercial_sprint_human_input_transfer_map_v0_1: true",
        "status: hold_human_input_required",
        "map_scope: mapping_only_no_value_transfer",
        "workbook_row_count: 65",
        "missing_required_row_count: 64",
        "ready_for_template_transfer: false",
        "values_transferred: false",
        "human_input_filled_by_codex: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_transfer_map: 0",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")
    runner = (ROOT / "scripts/saee_commercial_sprint_human_input_transfer_map.py").read_text(
        encoding="utf-8"
    )
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP_SMOKE: PASS "
        f"status={payload['status']} "
        f"workbook_row_count={payload['workbook_row_count']} "
        f"target_template_count={payload['target_template_count']} "
        f"values_transferred={str(payload['values_transferred']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
