#!/usr/bin/env python3
"""Smoke check for commercial sprint quick-fill owner packets."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "quick_fill_owner_packets"
)
OUT_JSON = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.local.json"
OUT_MD = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.md"
OUT_CSV = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.csv"
OUT_BOUNDARY = (
    PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_RECOMMENDATION_GATE.md"
)
COMPLETED_STATUS = "completed_owner_lane_packets_pending_workbook_import_approval_review"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_SMOKE: "
        f"FAIL: {message}"
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    subprocess.run(
        [
            sys.executable,
            "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_human_input_quick_fill_owner_packets_v0_1": True,
        "packet_type": "blocker_specific_human_quick_fill_owner_packets",
        "packet_scope": "manual_owner_review_packets_only_no_import",
        "status": COMPLETED_STATUS,
        "quick_fill_row_count": 64,
        "owner_packet_count": 5,
        "owner_review_lane_count": 5,
        "blocker_count": 5,
        "blank_human_value_row_count": 0,
        "nonblank_human_value_row_count": 64,
        "suggested_values_count": 0,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_human_quick_fill": False,
        "ready_for_workbook_import_approval_review": True,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "human_value_prefilled_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_owner_packets": 0,
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

    packets = payload.get("owner_packets", [])
    if len(packets) != 5:
        fail("owner_packets must contain 5 packets")
    expected_counts = {
        "formal_security_review": 12,
        "pricing_page": 14,
        "production_monitoring": 10,
        "production_restore_policy": 13,
        "support_contact": 15,
    }
    if payload.get("owner_packet_rows_by_blocker") != expected_counts:
        fail("owner packet blocker counts changed")

    index_rows = read_csv(OUT_CSV)
    if len(index_rows) != 5:
        fail("owner packet index CSV must contain 5 rows")

    total_rows = 0
    for packet in packets:
        packet_path = ROOT / packet["owner_packet_csv"]
        if not packet_path.exists():
            fail(f"missing owner packet CSV {packet_path}")
        rows = read_csv(packet_path)
        total_rows += len(rows)
        if len(rows) != packet["packet_row_count"]:
            fail(f"{packet_path} row count does not match payload")
        if sum(1 for row in rows if row.get("human_value_to_enter")) != len(rows):
            fail(f"{packet_path} must contain human-confirmed values")
        for flag in [
            "codex_filled_value",
            "workbook_import_performed",
            "validators_run_on_real_input",
            "evidence_collection_authorized",
            "execution_authorized",
        ]:
            if any(row.get(flag) not in {"False", "false", False} for row in rows):
                fail(f"{packet_path} {flag} must remain false")
    if total_rows != 64:
        fail("owner packet CSV rows must total 64")

    required_tokens = [
        "commercial_sprint_human_input_quick_fill_owner_packets_v0_1: true",
        f"status: {COMPLETED_STATUS}",
        "packet_scope: manual_owner_review_packets_only_no_import",
        "quick_fill_row_count: 64",
        "owner_packet_count: 5",
        "owner_review_lane_count: 5",
        "blocker_count: 5",
        "blank_human_value_row_count: 0",
        "nonblank_human_value_row_count: 64",
        "ready_for_workbook_import_approval_review: true",
        "suggested_values_count: 0",
        "human_value_prefilled_by_codex: false",
        "quick_fill_values_entered_by_codex: false",
        "human_input_filled_by_codex: false",
        "workbook_import_authorized: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "validators_run_on_real_input: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_owner_packets: 0",
        "boundary_violation_count: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")

    gate = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: recommend",
        "recommend_for_owner_lane_handoff: true",
        "recommend_for_human_quick_fill_entry_support: true",
        "recommend_for_human_fill_coordination: true",
        "recommend_for_value_generation: false",
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
        ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets.py"
    ).read_text(encoding="utf-8")
    for token in ["requests.", "urllib.", "httpx.", "webbrowser"]:
        if token in runner:
            fail(f"runner suggests external access: {token}")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_SMOKE: PASS "
        f"status={payload['status']} "
        f"owner_packet_count={payload['owner_packet_count']} "
        f"quick_fill_row_count={payload['quick_fill_row_count']} "
        f"blank_human_value_row_count={payload['blank_human_value_row_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
