#!/usr/bin/env python3
"""Generate the SAEE tax review human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not contact tax advisors, complete tax review, start tax collection,
collect payment, validate revenue, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PACKET_JSON = OUTPUT_DIR / "tax_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "tax_review_packet.md"

REQUIRED_TAX_REVIEW_SECTIONS = [
    "target_jurisdictions_boundary",
    "tax_obligations_boundary",
    "invoice_wording_review_boundary",
    "currency_policy_boundary",
    "sales_tax_or_vat_handling",
    "accounting_review_record",
    "payment_collection_approval_boundary",
    "refund_tax_handoff",
    "payment_provider_tax_handoff",
    "tenant_tax_boundary",
    "private_core_exclusion",
    "approval_record",
]

APPROVAL_FLAGS: dict[str, bool] = {
    "target_jurisdictions_reviewed": False,
    "tax_obligations_reviewed": False,
    "invoice_wording_approved": False,
    "currency_policy_approved": False,
    "tax_collection_approval_recorded": False,
    "accounting_review_completed": False,
    "legal_review_completed": False,
    "refund_tax_handoff_approved": False,
    "payment_provider_tax_handoff_approved": False,
    "tenant_tax_boundary_reviewed": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "tax_review_completed": False,
    "tax_advisor_contacted": False,
    "legal_counsel_contacted": False,
    "target_jurisdictions_reviewed": False,
    "tax_collection_started": False,
    "tax_rate_configured": False,
    "tax_exemption_process_available": False,
    "invoice_wording_published": False,
    "currency_policy_published": False,
    "payment_provider_configured": False,
    "checkout_enabled": False,
    "invoice_sent_to_customer": False,
    "refund_policy_published": False,
    "customer_payment_collected": False,
    "paid_pilot_completed": False,
    "revenue_validated": False,
    "tenant_billing_isolated": False,
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
        "jurisdiction_review_requires_separate_approval": True,
        "tax_obligation_review_requires_separate_approval": True,
        "invoice_wording_requires_legal_tax_approval": True,
        "currency_policy_requires_accounting_approval": True,
        "payment_collection_requires_separate_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_tax_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_tax_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "tax_review_human_review_packet_only",
        "blocker_target": "tax_review",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "tax_review_approval_status": "not_approved",
        "required_tax_review_sections": REQUIRED_TAX_REVIEW_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "tax_review_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human legal, tax, accounting, commercial, and billing owners must "
            "review jurisdictions, tax obligations, invoice wording, currency "
            "policy, tax collection approval, refund handoff, and tenant tax "
            "boundaries before the tax_review blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_tax_review_sections"]
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
    return f"""# SAEE Tax Review Packet v0.1

Status: draft ready for human review; tax review not approved.

This packet converts the `tax_review` commercial blocker into a concrete human
review surface. It does not contact tax advisors, complete tax review, publish
tax wording, configure tax rates, start tax collection, collect payment,
validate revenue, contact customers, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
tax_review_approval_status: {packet['tax_review_approval_status']}
ready_for_human_review: true
tax_review_evidence_complete: false
production_billing_revenue_ready: false
```

## Required Tax Review Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Legal owner
- Tax / accounting owner
- Commercial owner
- Billing support owner
- Tenant / privacy boundary owner

## Non-Approval Statement

This packet is not tax approval, not accounting approval, not payment
collection approval, not customer billing evidence, and not production billing
evidence by itself. The `tax_review` blocker remains open until jurisdiction,
obligation, invoice wording, currency, collection, refund, provider handoff,
and tenant tax boundaries are approved and backed by human-provided evidence.
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
        "SAEE_TAX_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "tax_review_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
