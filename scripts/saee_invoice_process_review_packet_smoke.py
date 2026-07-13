#!/usr/bin/env python3
"""Smoke check for the SAEE invoice process review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "invoice_process_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "invoice_process_review_packet.md"
)
GATE_PATH = ROOT / "docs/strategy/SAEE_INVOICE_PROCESS_REVIEW_PACKET_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_INVOICE_PROCESS_REVIEW_PACKET_SMOKE: FAIL: " + message)


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_invoice_process_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "invoice_process_human_review_packet_only",
        "blocker_target": "invoice_process",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "invoice_process_approval_status": "not_approved",
        "ready_for_human_review": True,
        "invoice_process_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "invoice_owner_boundary",
        "invoice_workflow_boundary",
        "contract_handoff_boundary",
        "invoice_numbering_policy",
        "payment_reconciliation_plan",
        "billing_support_handoff",
        "bookkeeping_review_boundary",
        "invoice_dispute_process",
        "tax_and_refund_handoff",
        "tenant_invoice_boundary",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections <= set(packet.get("required_invoice_process_sections", [])),
        "missing required invoice process sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_invoice_process_review_packet",
        "packet_status: draft_ready_for_human_review",
        "invoice_process_approval_status: not_approved",
        "invoice_process_evidence_complete: false",
        "production_billing_revenue_ready: false",
        "invoice_process_ready: false",
        "invoice_created: false",
        "invoice_sent_to_customer: false",
        "invoice_template_published: false",
        "enterprise_contract_signed: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "tenant_billing_isolated: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_invoice_process_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_review_packet.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_review_packet.local.json",
        "/docs/strategy/SAEE_INVOICE_PROCESS_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_invoice_process_review_packet.py",
        "/scripts/saee_invoice_process_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("invoice_process_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_invoice_process_review_packet",
        "blocker_target": "invoice_process",
        "human_review_required": True,
        "ready_for_human_review": True,
        "invoice_process_approval_status": "not_approved",
        "invoice_process_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "invoice_process_ready": False,
        "invoice_created": False,
        "invoice_sent_to_customer": False,
        "invoice_template_published": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "tenant_billing_isolated": False,
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
        "SAEE_INVOICE_PROCESS_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true invoice_process_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
