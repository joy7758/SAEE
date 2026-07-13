#!/usr/bin/env python3
"""Smoke check for commercial sprint human input quick-fill packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> int:
    for script in [
        "scripts/saee_commercial_sprint_human_input_workbook.py",
        "scripts/saee_commercial_sprint_human_input_workbook_validator.py",
        "scripts/saee_commercial_sprint_human_input_transfer_map.py",
        "scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py",
        "scripts/saee_commercial_sprint_human_input_completion_queue.py",
        "scripts/saee_commercial_sprint_human_input_quick_fill_packet.py",
    ]:
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_quick_fill_packet_v0_1": True,
        "packet_type": "local_human_quick_fill_packet",
        "packet_scope": "human_confirmed_quick_fill_source_only_no_import_no_transfer",
        "status": "human_confirmed_values_present_pending_safety_preflight",
        "source_queue_item_count": 64,
        "quick_fill_row_count": 64,
        "blank_value_row_count": 0,
        "confirmed_value_row_count": 64,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_safety_preflight": True,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_quick_fill_packet": 0,
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
    rows = payload.get("quick_fill_rows", [])
    if len(rows) != 64:
        fail("quick_fill_rows must contain 64 confirmed rows")
    if any(not str(row.get("human_value_to_enter", "")).strip() for row in rows):
        fail("quick-fill rows must contain human-confirmed values")
    if any(row.get("value_imported_to_workbook") is not False for row in rows):
        fail("quick-fill rows must not be imported into workbook")
    if any(row.get("value_transferred") is not False for row in rows):
        fail("quick-fill rows must not transfer values")
    if any(row.get("template_written") is not False for row in rows):
        fail("quick-fill rows must not write templates")
    if payload.get("blocker_fill_counts") != {
        "formal_security_review": 12,
        "pricing_page": 14,
        "production_monitoring": 10,
        "production_restore_policy": 13,
        "support_contact": 15,
    }:
        fail("unexpected blocker_fill_counts")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != 64:
        fail("CSV must contain 64 quick-fill rows")
    if any(not row.get("human_value_to_enter", "").strip() for row in csv_rows):
        fail("CSV human_value_to_enter cells must be filled")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_packet_v0_1: true",
        "status: human_confirmed_values_present_pending_safety_preflight",
        "packet_scope: human_confirmed_quick_fill_source_only_no_import_no_transfer",
        "source_queue_item_count: 64",
        "quick_fill_row_count: 64",
        "blank_value_row_count: 0",
        "confirmed_value_row_count: 64",
        "quick_fill_values_entered_by_codex: false",
        "quick_fill_imported_to_workbook: false",
        "human_input_filled_by_codex: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "ready_for_workbook_import: false",
        "ready_for_template_transfer: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_quick_fill_packet: 0",
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
        ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_packet.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_SMOKE: PASS "
        f"status={payload['status']} "
        f"quick_fill_row_count={payload['quick_fill_row_count']} "
        f"quick_fill_imported_to_workbook={str(payload['quick_fill_imported_to_workbook']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
