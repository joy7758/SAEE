#!/usr/bin/env python3
"""Smoke test for the support-contact first-priority packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "support_contact_first_priority_packet"
)
OUT_JSON = OUT_DIR / "support_contact_first_priority_packet.local.json"
OUT_MD = OUT_DIR / "support_contact_first_priority_packet.md"
OUT_CSV = OUT_DIR / "support_contact_first_priority_packet.csv"
OUT_HTML = OUT_DIR / "support_contact_first_priority_packet.html"
OUT_AUDIT = OUT_DIR / "support_contact_first_priority_packet_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_support_contact_first_priority_packet.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "support_contact_first_priority_packet_v0_1": True,
        "packet_type": "support_contact_first_priority_human_packet",
        "packet_scope": "first_priority_human_navigation_only_no_values_no_export_no_execution",
        "status": "hold_human_support_contact_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "support_contact",
        "first_priority_rank": 1,
        "first_priority_tier": "validators_passed_pending_evidence_builder_request",
        "review_batch_fill_card_row_count": 10,
        "review_batch_blank_value_row_count": 10,
        "combined_bridge_input_row_count": 16,
        "missing_first_owner_field_count": 5,
        "missing_support_decision_field_count": 15,
        "candidate_contact_slot_count": 2,
        "minimum_completed_contact_slot_count": 1,
        "readiness_completed_step_count": 0,
        "readiness_incomplete_step_count": 5,
        "human_review_required": True,
        "human_input_required": True,
        "boundary_violation_count": 0,
    }
    for key, value in expected_values.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    false_flags = [
        "production_ready",
        "product_launched",
        "customer_validated",
        "customer_contacted",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "workbook_import_authorized",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "development_permission_granted",
        "production_ready_claim",
        "customer_validation_claim",
        "raw_values_recorded",
        "human_values_generated_by_codex",
        "quick_fill_values_entered_by_codex",
        "human_input_filled_by_codex",
        "validator_inputs_exported",
        "validators_run",
        "support_contact_configured",
        "support_contact_published",
        "support_contact_test_performed",
        "support_contact_claim_published",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")

    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    steps = payload.get("human_steps", [])
    require(len(steps) == 6, "human step count")
    require(all(step["codex_execution_allowed"] is False for step in steps), "codex execution")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 6, "CSV must include 6 rows")
    require(rows[0]["step_id"] == "SCFP-001", "first CSV step")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_HTML, OUT_AUDIT, OUT_README, TOP_DOC, GATE]
    )
    required_tokens = [
        "support_contact_first_priority_packet_v0_1",
        "status: hold_human_support_contact_input_required",
        "target_blocker_id: support_contact",
        "review_batch_fill_card_row_count: 10",
        "review_batch_blank_value_row_count: 10",
        "combined_bridge_input_row_count: 16",
        "support_contact_published: false",
        "support_contact_configured: false",
        "workbook_import_authorized: false",
        "evidence_collection_authorized: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "recommend_for_product_launch: false",
        "recommend_for_support_contact_publication: false",
    ]
    for token in required_tokens:
        require(token in combined, "missing token " + token)

    forbidden_tokens = [
        "support_contact_published: true",
        '"support_contact_published": true',
        "support_contact_configured: true",
        '"support_contact_configured": true',
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
        "recommend_for_product_launch: true",
        "recommend_for_support_contact_publication: true",
        "<script",
        "fetch(",
        "XMLHttpRequest",
    ]
    for token in forbidden_tokens:
        require(token not in combined, "forbidden token " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/README.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.html",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_GATE.md",
        "/scripts/saee_support_contact_first_priority_packet.py",
        "/scripts/saee_support_contact_first_priority_packet_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    status_surfaces = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Support Contact First Priority Packet v0.1",
        "support_contact_first_priority_packet_v0_1",
        "hold_human_support_contact_input_required",
        "target_blocker_id=support_contact",
        "review_batch_blank_value_row_count=10",
        "support_contact_published=false",
        "production_ready=false",
    ]:
        require(token in status_surfaces, "status surfaces missing " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "check-support-contact-first-priority-packet:",
        "support-contact-first-priority-packet-smoke:",
        "scripts/saee_support_contact_first_priority_packet_smoke.py",
    ]:
        require(token in makefile, "Makefile missing " + token)

    agent_index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = agent_index.get("support_contact_first_priority_packet_v0_1", {})
    require(entry, "agent-index missing support_contact_first_priority_packet_v0_1")
    for key, value in expected_values.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")
    for flag in false_flags:
        require(entry.get(flag) is False, f"agent-index {flag} must be false")
    require(
        entry.get("make_target") == "make check-support-contact-first-priority-packet",
        "agent-index make target",
    )

    print(
        "SAEE_SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_SMOKE: PASS "
        f"status={payload['status']} "
        f"target={payload['target_blocker_id']} "
        f"blank_rows={payload['review_batch_blank_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
