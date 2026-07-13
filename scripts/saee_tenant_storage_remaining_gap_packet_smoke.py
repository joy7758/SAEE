#!/usr/bin/env python3
"""Smoke test for tenant_storage_isolation remaining-gap packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_tenant_storage_remaining_gap_packet.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence"
OUT_JSON = OUTPUT_DIR / "tenant_storage_remaining_gap_packet.local.json"
OUT_MD = OUTPUT_DIR / "tenant_storage_remaining_gap_packet.md"
OUT_CSV = OUTPUT_DIR / "tenant_storage_remaining_gap_packet.csv"
OUT_TEMPLATE = OUTPUT_DIR / "tenant_storage_remaining_gap_decision_template.json"
OUT_AUDIT = OUTPUT_DIR / "tenant_storage_remaining_gap_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/TENANT_STORAGE_REMAINING_GAP_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_TENANT_STORAGE_REMAINING_GAP_PACKET_GATE.md"

EXPECTED_MISSING = [
    "privacy_legal_review_completed",
]


def fail(message: str) -> None:
    raise SystemExit("SAEE_TENANT_STORAGE_REMAINING_GAP_PACKET_SMOKE: FAIL: " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_TEMPLATE, OUT_AUDIT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "tenant_storage_remaining_gap_packet_v0_1": True,
        "packet_type": "tenant_storage_remaining_gap_agent_review_packet",
        "packet_scope": "remaining_one_agent_review_only_no_execution_no_closure",
        "status": "hold_remaining_one_agent_review_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "tenant_storage_isolation",
        "required_evidence_item_count": 18,
        "local_public_shell_present_count": 17,
        "remaining_missing_evidence_count": 1,
        "tenant_security_privacy_packet_status": "draft_ready_for_human_review",
        "tenant_storage_approval_input_validation_status": "hold",
        "tenant_storage_approval_input_complete": False,
        "tenant_storage_builder_ready": False,
        "human_review_required": False,
        "human_validation_used": False,
        "agent_review_required": True,
        "agent_validation_primary": True,
        "recommended_default_decision": "hold",
        "ready_for_closure": False,
        "ready_for_matrix_update": False,
        "ready_for_evidence_builder": False,
        "blockers_closed_by_packet": 0,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(
        payload.get("remaining_missing_evidence_keys") == EXPECTED_MISSING,
        "remaining missing keys changed",
    )
    rows = payload.get("packet_rows", [])
    require(isinstance(rows, list) and len(rows) == 1, "packet must contain one row")
    require(
        [row.get("evidence_key") for row in rows] == EXPECTED_MISSING,
        "packet row evidence keys changed",
    )
    require(
        all(row.get("closure_allowed_by_packet") is False for row in rows),
        "packet rows must not allow closure",
    )
    require(all(row.get("human_review_required") is False for row in rows), "no human review")
    require(all(row.get("agent_review_required") is True for row in rows), "agent review required")

    false_flags = [
        "human_decision_recorded",
        "remaining_gap_approval_recorded",
        "evidence_collection_authorized",
        "execution_authorized",
        "development_permission_granted",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "blockers_closed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "production_database_modified",
        "storage_behavior_modified",
        "migration_executed",
        "live_customer_data_migrated",
        "customer_data_processed",
        "customer_data_processing_started",
        "production_tenant_storage_enabled",
        "production_tenant_storage_isolated",
        "tenant_storage_isolated",
        "tenant_authorization_enabled",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")

    template = json.loads(OUT_TEMPLATE.read_text(encoding="utf-8"))
    require(template.get("review_actor_type") == "independent_agent", "template actor")
    require(template.get("agent_reviewer_id") == "", "template reviewer must be blank")
    require(template.get("human_validation_used") is False, "template human boundary")
    require(template.get("review_date") == "", "template review_date must be blank")
    decisions = template.get("remaining_gap_decisions", [])
    require(len(decisions) == 1, "template must contain one decision")
    require(
        [row.get("evidence_key") for row in decisions] == EXPECTED_MISSING,
        "template decision keys changed",
    )
    require(all(row.get("decision") == "hold" for row in decisions), "template defaults must hold")
    require(all(row.get("approved") is False for row in decisions), "template approvals must be false")
    for flag in [
        "authorize_evidence_builder",
        "authorize_matrix_update",
        "authorize_blocker_closure",
        "authorize_product_launch",
    ]:
        require(template.get(flag) is False, f"template {flag} must be false")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 1, "CSV must contain one row")
    require([row["evidence_key"] for row in csv_rows] == EXPECTED_MISSING, "CSV keys changed")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "tenant_storage_remaining_gap_packet_v0_1: true",
        "status: hold_remaining_one_agent_review_required",
        "required_evidence_item_count: 18",
        "local_public_shell_present_count: 17",
        "remaining_missing_evidence_count: 1",
        "human_validation_used: false",
        "agent_validation_primary: true",
        "ready_for_evidence_builder: false",
        "ready_for_matrix_update: false",
        "ready_for_closure: false",
        "blockers_closed_by_packet: 0",
        "production_tenant_storage_isolated: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "recommend_for_evidence_builder: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
    ]:
        require(token in combined, f"missing token {token}")
    for key in EXPECTED_MISSING:
        require(key in combined, f"missing evidence key {key}")
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "production_tenant_storage_isolated: true",
        "ready_for_closure: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "blockers_closed_by_packet: 1",
    ]:
        require(token not in combined, f"forbidden token {token}")

    print(
        "SAEE_TENANT_STORAGE_REMAINING_GAP_PACKET_SMOKE: PASS "
        f"status={payload['status']} present=17 missing=1 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
