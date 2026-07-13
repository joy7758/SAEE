#!/usr/bin/env python3
"""Smoke check for the commercial sprint validator approval request packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_validator_approval_request_packet.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_validator_approval_request_packet_v0_1": True,
        "packet_type": "controlled_validator_execution_approval_request_packet",
        "packet_scope": "post_transfer_validator_approval_request_only_no_validator_execution_no_evidence",
        "status": "hold_validator_approval_required",
        "planned_validator_count": 5,
        "approval_request_count": 5,
        "ready_validator_count": 5,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "validators_run_count": 0,
        "builder_ready_count": 0,
        "blockers_closed_by_packet": 0,
        "template_transfer_complete": True,
        "ready_for_validator_approval": True,
        "ready_for_validator_execution": False,
        "human_validator_approval_required": True,
        "separate_validator_execution_request_required": True,
        "separate_evidence_builder_request_required": True,
        "validator_execution_authorized": False,
        "validators_run": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
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
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "payment_collected": False,
        "revenue_validated": False,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            fail(f"{key} must be {value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary violations must remain empty")
    requests = payload.get("approval_requests", [])
    if len(requests) != 5:
        fail("approval_requests must contain five validator approval rows")
    if any(row.get("human_validator_approval_recorded") for row in requests):
        fail("approval request packet must not record human approvals")
    if any(row.get("validator_execution_authorized") for row in requests):
        fail("approval request packet must not authorize validator execution")
    if any(row.get("validator_run") for row in requests):
        fail("approval request packet must not run validators")
    if any(row.get("builder_ready") for row in requests):
        fail("approval request packet must not mark builders ready")
    expected_runners = {
        "scripts/saee_support_contact_approval_input_validator.py",
        "scripts/saee_pricing_page_approval_input_validator.py",
        "scripts/saee_formal_security_review_approval_input_validator.py",
        "scripts/saee_production_restore_policy_approval_input_validator.py",
        "scripts/saee_production_monitoring_approval_input_validator.py",
    }
    if {row.get("runner") for row in requests} != expected_runners:
        fail("approval requests must reference the five expected validators")
    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 5:
        fail("CSV must contain five approval request rows")
    required_tokens = [
        "commercial_sprint_validator_approval_request_packet_v0_1: true",
        "status: hold_validator_approval_required",
        "packet_scope: post_transfer_validator_approval_request_only_no_validator_execution_no_evidence",
        "planned_validator_count: 5",
        "approval_request_count: 5",
        "ready_validator_count: 5",
        "approved_validator_count: 0",
        "validator_execution_authorized_count: 0",
        "validators_run_count: 0",
        "builder_ready_count: 0",
        "blockers_closed_by_packet: 0",
        "template_transfer_complete: true",
        "ready_for_validator_approval: true",
        "ready_for_validator_execution: false",
        "human_validator_approval_required: true",
        "separate_validator_execution_request_required: true",
        "separate_evidence_builder_request_required: true",
        "validator_execution_authorized: false",
        "validators_run: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")
    gate_text = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: conditional",
        "recommend_for_validator_approval_request_packet: true",
        "recommend_for_human_validator_approval_collection: true",
        "recommend_for_validator_execution: false",
        "recommend_for_auto_approval: false",
        "recommend_for_real_input_validation_without_human_approval: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
    ]:
        if token not in gate_text:
            fail(f"recommendation gate missing token {token}")
    runner = (
        ROOT / "scripts/saee_commercial_sprint_validator_approval_request_packet.py"
    ).read_text(encoding="utf-8")
    for forbidden in ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]:
        if forbidden in runner:
            fail(f"runner must not suggest external calls or execution: {forbidden}")
    print(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET_SMOKE: PASS "
        f"status={payload['status']} "
        f"approval_request_count={payload['approval_request_count']} "
        "validator_execution_authorized_count=0 validators_run=false production_ready=false"
    )


if __name__ == "__main__":
    main()
