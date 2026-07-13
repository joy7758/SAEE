#!/usr/bin/env python3
"""Smoke check for the SAEE production restore policy review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_restore_policy_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_restore_policy_review_packet.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_REVIEW_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_RESTORE_POLICY_REVIEW_PACKET_SMOKE: FAIL: {message}")


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_production_restore_policy_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "production_restore_policy_human_review_packet_only",
        "blocker_target": "production_restore_policy",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "policy_approval_status": "not_approved",
        "ready_for_human_review": True,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "restore_authority_and_approval",
        "backup_retention_and_encryption",
        "tenant_data_scope_and_isolation",
        "customer_data_handling_boundary",
        "credential_and_secret_exclusion",
        "private_core_exclusion",
        "incident_response_handoff",
        "customer_notification_boundary",
        "restore_evidence_retention",
        "post_restore_review",
    }
    require(required_sections <= set(packet.get("required_policy_sections", [])), "missing policy sections")

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(encoding="utf-8")
    for token in [
        "packet_type: saee_production_restore_policy_review_packet",
        "packet_status: draft_ready_for_human_review",
        "policy_approval_status: not_approved",
        "production_restore_policy_available: false",
        "production_data_operations_ready: false",
        "restore_to_live_path_enabled: false",
        "live_restore_performed: false",
        "production_data_path_modified: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_production_readiness_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_review_packet.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_review_packet.local.json",
        "/docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_restore_policy_review_packet.py",
        "/scripts/saee_production_restore_policy_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_restore_policy_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_production_restore_policy_review_packet",
        "blocker_target": "production_restore_policy",
        "human_review_required": True,
        "production_restore_policy_available": False,
        "production_restore_policy_approved": False,
        "production_data_operations_ready": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "production_data_path_modified": False,
        "private_core_exposed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
    }
    for key, expected_value in expected_entry.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true production_restore_policy_available=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
