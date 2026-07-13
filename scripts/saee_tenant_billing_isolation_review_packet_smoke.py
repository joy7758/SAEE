#!/usr/bin/env python3
"""Smoke check for the SAEE tenant billing isolation review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "tenant_billing_isolation_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "tenant_billing_isolation_review_packet.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_TENANT_BILLING_ISOLATION_REVIEW_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_REVIEW_PACKET_SMOKE: FAIL: "
            + message
        )


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_tenant_billing_isolation_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "tenant_billing_isolation_human_review_packet_only",
        "blocker_target": "tenant_billing_isolation",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "tenant_billing_isolation_approval_status": "not_approved",
        "ready_for_human_review": True,
        "tenant_billing_isolation_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "tenant_billing_account_model_boundary",
        "tenant_invoice_partitioning_boundary",
        "tenant_payment_event_partitioning_boundary",
        "cross_tenant_billing_access_test_plan",
        "billing_audit_metadata_policy",
        "tenant_billing_export_policy",
        "tenant_billing_deletion_or_retention_policy",
        "tenant_invoice_numbering_boundary",
        "tenant_refund_partitioning_boundary",
        "payment_provider_tenant_mapping_boundary",
        "tenant_privacy_security_handoff",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections
        <= set(packet.get("required_tenant_billing_isolation_sections", [])),
        "missing required tenant billing isolation sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_tenant_billing_isolation_review_packet",
        "packet_status: draft_ready_for_human_review",
        "tenant_billing_isolation_approval_status: not_approved",
        "tenant_billing_isolation_evidence_complete: false",
        "production_billing_revenue_ready: false",
        "tenant_billing_isolated: false",
        "tenant_billing_isolation_enabled: false",
        "tenant_billing_account_model_available: false",
        "tenant_invoice_partitioning_tested: false",
        "tenant_payment_event_partitioning_tested: false",
        "cross_tenant_billing_access_tests_passed: false",
        "billing_audit_metadata_policy_available: false",
        "tenant_billing_export_policy_available: false",
        "tenant_billing_retention_policy_available: false",
        "payment_provider_tenant_mapping_configured: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_tenant_billing_isolation_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_review_packet.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_review_packet.local.json",
        "/docs/strategy/SAEE_TENANT_BILLING_ISOLATION_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_tenant_billing_isolation_review_packet.py",
        "/scripts/saee_tenant_billing_isolation_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("tenant_billing_isolation_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_tenant_billing_isolation_review_packet",
        "blocker_target": "tenant_billing_isolation",
        "human_review_required": True,
        "ready_for_human_review": True,
        "tenant_billing_isolation_approval_status": "not_approved",
        "tenant_billing_isolation_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "tenant_billing_isolated": False,
        "tenant_billing_isolation_enabled": False,
        "tenant_billing_account_model_available": False,
        "tenant_invoice_partitioning_tested": False,
        "tenant_payment_event_partitioning_tested": False,
        "cross_tenant_billing_access_tests_passed": False,
        "billing_audit_metadata_policy_available": False,
        "tenant_billing_export_policy_available": False,
        "tenant_billing_retention_policy_available": False,
        "payment_provider_tenant_mapping_configured": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "private_core_exposed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected_entry.items():
        require(
            entry.get(key) == expected_value,
            f"agent-index {key} must be {expected_value}",
        )

    print(
        "SAEE_TENANT_BILLING_ISOLATION_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true "
        "tenant_billing_isolation_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
