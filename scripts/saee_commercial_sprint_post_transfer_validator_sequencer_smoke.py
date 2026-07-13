#!/usr/bin/env python3
"""Smoke check for the commercial sprint post-transfer validator sequencer."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER_SMOKE: "
        f"FAIL: {message}"
    )


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_sprint_post_transfer_validator_sequencer_v0_1": True,
        "sequencer_type": "controlled_post_transfer_validator_sequence",
        "sequencer_scope": "post_transfer_validator_sequence_only_no_validator_execution_no_evidence",
        "status": "ready_for_separate_validator_approval",
        "planned_validator_count": 5,
        "ready_validator_count": 5,
        "validators_run_count": 0,
        "builder_ready_count": 0,
        "blockers_closed_by_sequencer": 0,
        "template_transfer_complete": True,
        "ready_for_validator_execution": False,
        "ready_for_evidence_builder_execution": False,
        "separate_validator_approval_required": True,
        "separate_evidence_builder_request_required": True,
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
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"{key} must be {expected_value!r}")
    if payload.get("boundary_violations") != []:
        fail("boundary violations must remain empty")
    steps = payload.get("validator_steps", [])
    if len(steps) != 5:
        fail("validator_steps must contain five existing validators")
    if any(step.get("validator_run") for step in steps):
        fail("sequencer must not run validators")
    if any(step.get("builder_ready") for step in steps):
        fail("sequencer must not mark builders ready")
    if not all(step.get("ready_for_validator") for step in steps):
        fail("post-transfer state must mark all validators ready for approval")
    expected_runners = {
        "scripts/saee_support_contact_approval_input_validator.py",
        "scripts/saee_pricing_page_approval_input_validator.py",
        "scripts/saee_formal_security_review_approval_input_validator.py",
        "scripts/saee_production_restore_policy_approval_input_validator.py",
        "scripts/saee_production_monitoring_approval_input_validator.py",
    }
    if {step.get("runner") for step in steps} != expected_runners:
        fail("validator sequence must reference the five expected validators")
    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 5:
        fail("CSV must contain five validator sequence rows")
    required_tokens = [
        "commercial_sprint_post_transfer_validator_sequencer_v0_1: true",
        "status: ready_for_separate_validator_approval",
        "sequencer_scope: post_transfer_validator_sequence_only_no_validator_execution_no_evidence",
        "planned_validator_count: 5",
        "ready_validator_count: 5",
        "validators_run_count: 0",
        "builder_ready_count: 0",
        "blockers_closed_by_sequencer: 0",
        "template_transfer_complete: true",
        "ready_for_validator_execution: false",
        "ready_for_evidence_builder_execution: false",
        "validators_run: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
    ]
    for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                fail(f"{path} missing token {token}")
    gate_text = GATE.read_text(encoding="utf-8")
    for token in [
        "answer: conditional",
        "recommend_for_post_transfer_validator_sequence: true",
        "recommend_for_validator_ordering: true",
        "recommend_for_validator_execution: false",
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
        ROOT / "scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py"
    ).read_text(encoding="utf-8")
    for forbidden in ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]:
        if forbidden in runner:
            fail(f"runner must not suggest external calls or validator execution: {forbidden}")
    print(
        "SAEE_COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER_SMOKE: PASS "
        f"status={payload['status']} "
        f"planned_validator_count={payload['planned_validator_count']} "
        f"ready_validator_count={payload['ready_validator_count']} "
        "validators_run=false production_ready=false"
    )


if __name__ == "__main__":
    main()
