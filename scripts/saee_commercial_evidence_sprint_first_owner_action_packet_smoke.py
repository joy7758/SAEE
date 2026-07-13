#!/usr/bin/env python3
"""Smoke check for the commercial evidence sprint first-owner action packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/saee_commercial_evidence_sprint_first_owner_action_packet.py"
)
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_action_packet.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_action_packet.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_action_packet.csv"
)
BOUNDARY_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_action_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET_RECOMMENDATION_GATE.md"
)
OWNER_PACKET = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "owner_assignment_packet.local.json"
)
READINESS_BOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "owner_assignment_readiness_board.local.json"
)

PASS_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def run_packet(*args: str) -> dict[str, object]:
    subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, check=True, text=True)
    output_path = OUTPUT_JSON
    if "--output-json" in args:
        output_path = Path(args[args.index("--output-json") + 1])
    return json.loads(output_path.read_text(encoding="utf-8"))


def check_boundary(payload: dict[str, object]) -> None:
    for key in [
        "owner_assignment_complete",
        "ready_for_validator_import",
        "ready_for_separate_evidence_collection_request",
        "evidence_collection_authorized",
        "execution_authorized",
        "owner_contacted_by_codex",
        "customer_contacted",
        "vendor_contacted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "task_candidates_executed",
        "development_permission_granted",
        "customer_data_collected",
        "customer_data_processed",
        "payment_collected",
        "revenue_validated",
    ]:
        require(payload.get(key) is False, f"{key} must remain false")
    require(payload.get("blockers_closed_by_packet") == 0, "packet closes no blockers")


def main() -> int:
    payload = run_packet()
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, BOUNDARY_AUDIT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    expected = {
        "commercial_evidence_sprint_first_owner_action_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_sprint_first_owner_action_packet",
        "packet_version": "v0.1",
        "status": "hold_human_owner_input_required",
        "packet_scope": "local_first_owner_assignment_action_packet",
        "selected_blocker_count": 5,
        "first_blocker_id": "support_contact",
        "human_review_required": True,
        "human_owner_input_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"default {key} must be {value}")
    check_boundary(payload)
    first = payload.get("first_blocker", {})
    require(isinstance(first, dict), "first_blocker must be an object")
    require(first.get("blocker_id") == "support_contact", "default first blocker mismatch")
    require(
        first.get("owner_review_lane") == "support_operations",
        "default owner lane mismatch",
    )
    command = payload.get("human_fill_shell_command", "")
    require(isinstance(command, str), "human_fill_shell_command must be a string")
    for token in [
        "--single-blocker-id support_contact",
        '"<human owner>"',
        '"<internal owner reference>"',
        '"YYYY-MM-DD"',
        "--owner-acknowledged-scope true",
        '"<human approval record>"',
    ]:
        require(token in command, "command template missing " + token)
    forbidden_command_values = ["Fixture Owner", "zhangbin", "customer@", "vendor@"]
    found_command = [token for token in forbidden_command_values if token in command]
    require(not found_command, "command template contains non-placeholder values")

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 1, "CSV must contain exactly one first action row")
    require(rows[0].get("first_blocker_id") == "support_contact", "CSV first blocker mismatch")
    require(rows[0].get("blockers_closed_by_packet") == "0", "CSV must close zero blockers")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        pricing = run_packet(
            "--blocker-id",
            "pricing_page",
            "--output-json",
            str(tmp / "pricing.json"),
            "--output-md",
            str(tmp / "pricing.md"),
            "--output-csv",
            str(tmp / "pricing.csv"),
            "--boundary-audit",
            str(tmp / "pricing_boundary.md"),
            "--top-doc",
            str(tmp / "pricing_top.md"),
            "--gate",
            str(tmp / "pricing_gate.md"),
        )
        require(pricing["first_blocker_id"] == "pricing_page", "pricing fixture mismatch")
        require(pricing["status"] == "hold_human_owner_input_required", "pricing fixture status")
        check_boundary(pricing)

        unsafe_owner = tmp / "unsafe_owner_assignment_packet.json"
        unsafe_data = json.loads(OWNER_PACKET.read_text(encoding="utf-8"))
        unsafe_data["production_ready"] = True
        unsafe_owner.write_text(json.dumps(unsafe_data, indent=2) + "\n", encoding="utf-8")
        unsafe = run_packet(
            "--source-owner-assignment-packet",
            str(unsafe_owner),
            "--source-readiness-board",
            str(READINESS_BOARD),
            "--output-json",
            str(tmp / "unsafe.json"),
            "--output-md",
            str(tmp / "unsafe.md"),
            "--output-csv",
            str(tmp / "unsafe.csv"),
            "--boundary-audit",
            str(tmp / "unsafe_boundary.md"),
            "--top-doc",
            str(tmp / "unsafe_top.md"),
            "--gate",
            str(tmp / "unsafe_gate.md"),
        )
        require(
            unsafe["status"] == "stop_boundary_violation",
            "unsafe fixture must stop on boundary violation",
        )
        require(
            unsafe["boundary_violation_count"] >= 1,
            "unsafe fixture must report boundary violation",
        )

    # Restore default repo outputs after temp fixtures.
    payload = run_packet()

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, BOUNDARY_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "commercial_evidence_sprint_first_owner_action_packet_v0_1: true",
        "status: hold_human_owner_input_required",
        "packet_scope: local_first_owner_assignment_action_packet",
        "first_blocker_id: support_contact",
        "owner_assignment_complete: false",
        "ready_for_validator_import: false",
        "ready_for_separate_evidence_collection_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "owner_contacted_by_codex: false",
        "blockers_closed_by_packet: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_first_human_owner_action: true",
        "recommend_for_owner_assignment_completion: false",
        "recommend_for_validator_import: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
    ]:
        require(token in combined, "missing doc/gate token " + token)

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "owner_contacted_by_codex: true",
        '"owner_contacted_by_codex": true',
        "recommend_for_owner_assignment_completion: true",
        "recommend_for_validator_import: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print(
        PASS_PREFIX
        + " status=hold_human_owner_input_required first_blocker_id=support_contact "
        + "blockers_closed_by_packet=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
