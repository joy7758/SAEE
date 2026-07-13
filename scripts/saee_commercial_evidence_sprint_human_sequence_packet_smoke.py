#!/usr/bin/env python3
"""Smoke check for the commercial evidence sprint human sequence packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_commercial_evidence_sprint_human_sequence_packet.py"
OUTPUT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "human_sequence_packet.local.json"
)
OUTPUT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "human_sequence_packet.md"
)
OUTPUT_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "human_sequence_packet.csv"
)
BOUNDARY_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "human_sequence_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET_RECOMMENDATION_GATE.md"
)
FIRST_OWNER = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_action_packet.local.json"
)
OWNER_BOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "owner_assignment_readiness_board.local.json"
)
APPROVAL_BOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "evidence_request_approval_readiness_board.local.json"
)
CLOSURE_BOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/"
    "closure_readiness_board.local.json"
)

PASS_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET_SMOKE: PASS"
FAIL_PREFIX = "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def run_packet(*args: str) -> dict[str, object]:
    subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, check=True, text=True)
    output_path = OUTPUT_JSON
    if "--output-json" in args:
        output_path = Path(args[args.index("--output-json") + 1])
    return json.loads(output_path.read_text(encoding="utf-8"))


def check_false_boundaries(payload: dict[str, object]) -> None:
    for key in [
        "owner_assigned_by_codex",
        "owner_contacted_by_codex",
        "request_approved_by_codex",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "ready_for_validator_import",
        "ready_for_separate_evidence_collection_request",
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "vendor_contacted",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "customer_data_collected",
        "customer_data_processed",
        "payment_collected",
        "revenue_validated",
    ]:
        require(payload.get(key) is False, f"{key} must remain false")
    require(payload.get("blockers_closed_by_packet") == 0, "packet closes no blockers")


def write_json(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    payload = run_packet()
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, BOUNDARY_AUDIT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    expected = {
        "commercial_evidence_sprint_human_sequence_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_sprint_human_sequence_packet",
        "packet_version": "v0.1",
        "status": "hold_first_owner_input_required",
        "packet_scope": "local_human_only_commercial_evidence_sprint_sequence",
        "first_blocker_id": "support_contact",
        "current_step_id": "SEQ-001",
        "current_step_entrypoint": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.md",
        "current_step_command_template_available": True,
        "sequence_step_count": 7,
        "owner_import_ready_count": 0,
        "approval_import_ready_count": 0,
        "closure_candidate_count": 0,
        "human_review_required": True,
        "separate_owner_input_required": True,
        "separate_validator_required": True,
        "separate_approval_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_final_closure_approval_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"default {key} must be {value}")
    check_false_boundaries(payload)
    steps = payload.get("sequence_steps", [])
    require(isinstance(steps, list) and len(steps) == 7, "sequence must have 7 steps")
    current = [step for step in steps if step.get("current_step") is True]
    require(len(current) == 1 and current[0]["step_id"] == "SEQ-001", "default current step")
    require(
        current[0].get("entrypoint")
        == "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.md",
        "SEQ-001 must point to first owner input request packet",
    )
    require(all(step.get("automated_by_codex") is False for step in steps), "no automated steps")
    command = payload.get("current_step_command_template")
    require(isinstance(command, str), "current_step_command_template must be a string")
    for token in [
        "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py",
        "--single-blocker-id support_contact",
        "--assigned-human-owner",
        "--owner-contact-reference",
        "--target-review-date",
        "--owner-acknowledged-scope true",
        "--human-approval-reference",
        "owner_assignment_input.human_filled.local.json",
    ]:
        require(token in command, "current step command template missing " + token)

    with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 7, "CSV must contain 7 sequence rows")
    require(rows[0].get("step_id") == "SEQ-001", "CSV first step mismatch")
    require(rows[0].get("current_step") == "true", "CSV current step mismatch")
    require(
        rows[0].get("entrypoint")
        == "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.md",
        "CSV SEQ-001 entrypoint mismatch",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        owner_ready = json.loads(OWNER_BOARD.read_text(encoding="utf-8"))
        owner_ready["status"] = "ready_for_validator_import"
        owner_ready["import_ready_assignment_count"] = 1
        owner_ready_path = write_json(tmp / "owner_ready.json", owner_ready)
        owner_payload = run_packet(
            "--owner-readiness-board",
            str(owner_ready_path),
            "--output-json",
            str(tmp / "owner_seq.json"),
            "--output-md",
            str(tmp / "owner_seq.md"),
            "--output-csv",
            str(tmp / "owner_seq.csv"),
            "--boundary-audit",
            str(tmp / "owner_boundary.md"),
            "--top-doc",
            str(tmp / "owner_top.md"),
            "--gate",
            str(tmp / "owner_gate.md"),
        )
        require(owner_payload["status"] == "hold_owner_validator_required", "owner-ready status")
        require(owner_payload["current_step_id"] == "SEQ-002", "owner-ready current step")
        check_false_boundaries(owner_payload)

        approval_ready = json.loads(APPROVAL_BOARD.read_text(encoding="utf-8"))
        approval_ready["status"] = "ready_for_validator_import"
        approval_ready["import_ready_request_count"] = 1
        approval_ready_path = write_json(tmp / "approval_ready.json", approval_ready)
        approval_payload = run_packet(
            "--approval-readiness-board",
            str(approval_ready_path),
            "--output-json",
            str(tmp / "approval_seq.json"),
            "--output-md",
            str(tmp / "approval_seq.md"),
            "--output-csv",
            str(tmp / "approval_seq.csv"),
            "--boundary-audit",
            str(tmp / "approval_boundary.md"),
            "--top-doc",
            str(tmp / "approval_top.md"),
            "--gate",
            str(tmp / "approval_gate.md"),
        )
        require(
            approval_payload["status"] == "hold_approval_validator_required",
            "approval-ready status",
        )
        require(approval_payload["current_step_id"] == "SEQ-004", "approval-ready current step")
        check_false_boundaries(approval_payload)

        unsafe_first = json.loads(FIRST_OWNER.read_text(encoding="utf-8"))
        unsafe_first["production_ready"] = True
        unsafe_first_path = write_json(tmp / "unsafe_first.json", unsafe_first)
        unsafe_payload = run_packet(
            "--first-owner-packet",
            str(unsafe_first_path),
            "--output-json",
            str(tmp / "unsafe_seq.json"),
            "--output-md",
            str(tmp / "unsafe_seq.md"),
            "--output-csv",
            str(tmp / "unsafe_seq.csv"),
            "--boundary-audit",
            str(tmp / "unsafe_boundary.md"),
            "--top-doc",
            str(tmp / "unsafe_top.md"),
            "--gate",
            str(tmp / "unsafe_gate.md"),
        )
        require(
            unsafe_payload["status"] == "stop_boundary_violation",
            "unsafe fixture must stop",
        )
        require(unsafe_payload["current_step_id"] == "SEQ-000", "unsafe current step")
        require(unsafe_payload["boundary_violation_count"] >= 1, "unsafe violation count")

    # Restore default repo outputs after temp fixtures.
    payload = run_packet()

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, BOUNDARY_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "commercial_evidence_sprint_human_sequence_packet_v0_1: true",
        "status: hold_first_owner_input_required",
        "packet_scope: local_human_only_commercial_evidence_sprint_sequence",
        "first_blocker_id: support_contact",
        "current_step_id: SEQ-001",
        "current_step_entrypoint: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.md",
        "current_step_command_template_available: true",
        "sequence_step_count: 7",
        "ready_for_validator_import: false",
        "ready_for_separate_evidence_collection_request: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "owner_contacted_by_codex: false",
        "request_approved_by_codex: false",
        "blockers_closed_by_packet: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_sequence_control: true",
        "recommend_for_owner_assignment: false",
        "recommend_for_request_approval: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py",
        "--single-blocker-id support_contact",
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
        "request_approved_by_codex: true",
        '"request_approved_by_codex": true',
        "recommend_for_owner_assignment: true",
        "recommend_for_request_approval: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    print(
        PASS_PREFIX
        + " status=hold_first_owner_input_required current_step_id=SEQ-001 "
        + "blockers_closed_by_packet=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
