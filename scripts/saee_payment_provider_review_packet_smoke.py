#!/usr/bin/env python3
"""Smoke check for the SAEE payment provider review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "payment_provider_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "payment_provider_review_packet.md"
)
GATE_PATH = ROOT / "docs/strategy/SAEE_PAYMENT_PROVIDER_REVIEW_PACKET_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PAYMENT_PROVIDER_REVIEW_PACKET_SMOKE: FAIL: " + message)


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_payment_provider_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "payment_provider_human_review_packet_only",
        "blocker_target": "payment_provider",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "provider_selection_status": "not_selected",
        "ready_for_human_review": True,
        "payment_provider_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "provider_selection_boundary",
        "test_mode_configuration_boundary",
        "live_mode_enablement_boundary",
        "checkout_enablement_boundary",
        "webhook_signature_validation_plan",
        "payment_event_redaction_boundary",
        "failed_payment_and_dispute_handling",
        "refund_tax_and_invoice_handoff",
        "tenant_billing_boundary",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections <= set(packet.get("required_payment_provider_sections", [])),
        "missing required payment provider sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_payment_provider_review_packet",
        "packet_status: draft_ready_for_human_review",
        "provider_selection_status: not_selected",
        "payment_provider_evidence_complete: false",
        "production_billing_revenue_ready: false",
        "payment_provider_selected: false",
        "payment_provider_contacted: false",
        "payment_provider_configured: false",
        "payment_provider_live_mode_enabled: false",
        "checkout_enabled: false",
        "payment_link_created: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_payment_provider_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_review_packet.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_review_packet.local.json",
        "/docs/strategy/SAEE_PAYMENT_PROVIDER_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_payment_provider_review_packet.py",
        "/scripts/saee_payment_provider_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("payment_provider_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_payment_provider_review_packet",
        "blocker_target": "payment_provider",
        "human_review_required": True,
        "ready_for_human_review": True,
        "provider_selection_status": "not_selected",
        "payment_provider_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "payment_provider_selected": False,
        "payment_provider_contacted": False,
        "payment_provider_configured": False,
        "payment_provider_live_mode_enabled": False,
        "checkout_enabled": False,
        "payment_link_created": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
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
        "SAEE_PAYMENT_PROVIDER_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true payment_provider_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
