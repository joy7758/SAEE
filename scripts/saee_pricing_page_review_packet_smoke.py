#!/usr/bin/env python3
"""Smoke check for the SAEE pricing page review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "pricing_page_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "pricing_page_review_packet.md"
)
GATE_PATH = ROOT / "docs/strategy/SAEE_PRICING_PAGE_REVIEW_PACKET_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRICING_PAGE_REVIEW_PACKET_SMOKE: FAIL: " + message)


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_pricing_page_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "pricing_page_human_review_packet_only",
        "blocker_target": "pricing_page",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "publication_approval_status": "not_approved",
        "ready_for_human_review": True,
        "pricing_page_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "target_buyer_and_use_case_boundary",
        "plan_names_and_package_scope",
        "price_points_or_contact_sales_boundary",
        "usage_limits_and_overage_policy",
        "trial_or_controlled_preview_terms",
        "non_production_ready_disclaimer",
        "refund_and_cancellation_pointer",
        "customer_data_processing_boundary",
        "private_core_exclusion",
        "legal_and_tax_review_handoff",
        "publication_approval_record",
    }
    require(
        required_sections <= set(packet.get("required_pricing_page_sections", [])),
        "missing required pricing page sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_pricing_page_review_packet",
        "packet_status: draft_ready_for_human_review",
        "publication_approval_status: not_approved",
        "pricing_page_evidence_complete: false",
        "production_billing_revenue_ready: false",
        "pricing_page_published: false",
        "sales_offer_sent: false",
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
        "recommend_for_public_pricing_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.local.json",
        "/docs/strategy/SAEE_PRICING_PAGE_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_pricing_page_review_packet.py",
        "/scripts/saee_pricing_page_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("pricing_page_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_pricing_page_review_packet",
        "blocker_target": "pricing_page",
        "human_review_required": True,
        "ready_for_human_review": True,
        "publication_approval_status": "not_approved",
        "pricing_page_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
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
        "SAEE_PRICING_PAGE_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true pricing_page_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
