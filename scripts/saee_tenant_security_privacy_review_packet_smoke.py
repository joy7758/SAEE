#!/usr/bin/env python3
"""Smoke check for the SAEE tenant security/privacy review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/"
    "tenant_security_privacy_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/"
    "tenant_security_privacy_review_packet.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_TENANT_SECURITY_PRIVACY_REVIEW_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_TENANT_SECURITY_PRIVACY_REVIEW_PACKET_SMOKE: FAIL: " + message
        )


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_tenant_security_privacy_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "tenant_security_privacy_human_review_packet_only",
        "blocker_target": "tenant_storage_isolation",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "policy_approval_status": "not_approved",
        "ready_for_human_review": True,
        "tenant_security_privacy_evidence_complete": False,
        "production_tenant_storage_evidence_complete": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "tenant_authorization_policy",
        "tenant_role_and_operator_access_boundary",
        "tenant_secret_boundary",
        "customer_data_processing_non_claim",
        "cross_tenant_access_review",
        "security_review_handoff",
        "privacy_legal_review_handoff",
        "private_core_exclusion",
        "production_enablement_exclusion",
        "separate_execution_approval",
    }
    require(
        required_sections <= set(packet.get("required_review_sections", [])),
        "missing required review sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_tenant_security_privacy_review_packet",
        "packet_status: draft_ready_for_human_review",
        "policy_approval_status: not_approved",
        "tenant_security_privacy_evidence_complete: false",
        "production_tenant_storage_evidence_complete: false",
        "tenant_authorization_enabled: false",
        "customer_data_processed: false",
        "tenant_storage_isolated: false",
        "production_tenant_storage_isolated: false",
        "multi_tenant_production_ready: false",
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
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_security_privacy_review_packet.md",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_security_privacy_review_packet.local.json",
        "/docs/strategy/SAEE_TENANT_SECURITY_PRIVACY_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_tenant_security_privacy_review_packet.py",
        "/scripts/saee_tenant_security_privacy_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("tenant_security_privacy_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_tenant_security_privacy_review_packet",
        "blocker_target": "tenant_storage_isolation",
        "human_review_required": True,
        "ready_for_human_review": True,
        "policy_approval_status": "not_approved",
        "tenant_security_privacy_evidence_complete": False,
        "production_tenant_storage_evidence_complete": False,
        "tenant_authorization_enabled": False,
        "customer_data_processed": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
        "private_core_exposed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected_entry.items():
        require(
            entry.get(key) == expected_value,
            f"agent-index {key} must be {expected_value}",
        )

    print(
        "SAEE_TENANT_SECURITY_PRIVACY_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true tenant_security_privacy_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
