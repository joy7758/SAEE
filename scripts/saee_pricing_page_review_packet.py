#!/usr/bin/env python3
"""Generate the SAEE pricing page human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not publish pricing, create a sales offer, configure payments, enable
checkout, contact customers, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PACKET_JSON = OUTPUT_DIR / "pricing_page_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "pricing_page_review_packet.md"

REQUIRED_PRICING_PAGE_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "human_approved_pricing_page_copy": False,
    "approved_plan_and_usage_terms": False,
    "legal_review_completed": False,
    "tax_review_completed": False,
    "pricing_page_publication_approval_recorded": False,
    "production_readiness_non_claim_reviewed": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "pricing_page_published": False,
    "sales_offer_sent": False,
    "paid_product_launched": False,
    "enterprise_contract_signed": False,
    "payment_provider_configured": False,
    "checkout_enabled": False,
    "payment_link_created": False,
    "invoice_sent_to_customer": False,
    "tax_collection_started": False,
    "customer_payment_collected": False,
    "paid_pilot_completed": False,
    "revenue_validated": False,
    "production_billing_enabled": False,
    "production_billing_revenue_ready": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "external_calls_made": False,
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "production_ready": False,
}


def build_packet() -> dict[str, Any]:
    review_checklist = {
        "required_sections_present": True,
        "human_review_required": True,
        "pricing_publication_requires_separate_approval": True,
        "payment_enablement_requires_separate_approval": True,
        "legal_review_required_before_publication": True,
        "tax_review_required_before_payment_collection": True,
        "production_readiness_claim_forbidden": True,
        "customer_data_processing_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_pricing_page_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_pricing_page_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "pricing_page_human_review_packet_only",
        "blocker_target": "pricing_page",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "publication_approval_status": "not_approved",
        "required_pricing_page_sections": REQUIRED_PRICING_PAGE_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "pricing_page_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human product, legal, tax, and commercial owners must review "
            "and approve pricing page copy before the pricing_page blocker "
            "can close or any customer-facing pricing page is published."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_pricing_page_sections"]
    )
    checklist_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["review_checklist"].items()
    )
    approval_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["approval_flags"].items()
    )
    boundary_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["boundary_flags"].items()
    )
    return f"""# SAEE Pricing Page Review Packet v0.1

Status: draft ready for human review; not approved.

This packet converts the `pricing_page` commercial blocker into a concrete
human review surface. It does not publish pricing, create a sales offer,
configure payment providers, enable checkout, contact customers, collect
payment, validate revenue, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
publication_approval_status: {packet['publication_approval_status']}
ready_for_human_review: true
pricing_page_evidence_complete: false
production_billing_revenue_ready: false
```

## Required Pricing Page Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Product / packaging owner
- Commercial owner
- Legal owner
- Tax / accounting owner

## Non-Approval Statement

This packet is not a public pricing page, not a sales offer, and not production
billing evidence by itself. The `pricing_page` blocker remains open until the
approval flags are backed by human-approved commercial, legal, and tax review.
"""


def write_outputs(packet: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKET_JSON.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    PACKET_MD.write_text(render_markdown(packet), encoding="utf-8")


def main() -> None:
    packet = build_packet()
    write_outputs(packet)
    print(
        "SAEE_PRICING_PAGE_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "pricing_page_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
