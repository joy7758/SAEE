#!/usr/bin/env python3
"""Generate the SAEE invoice process human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not create or send invoices, configure payment providers, contact
customers, collect payment, validate revenue, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PACKET_JSON = OUTPUT_DIR / "invoice_process_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "invoice_process_review_packet.md"

REQUIRED_INVOICE_PROCESS_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "invoice_owner_named": False,
    "invoice_workflow_approved": False,
    "contract_handoff_defined": False,
    "invoice_numbering_policy_approved": False,
    "payment_reconciliation_tested": False,
    "billing_support_handoff_defined": False,
    "bookkeeping_review_completed": False,
    "invoice_dispute_process_approved": False,
    "legal_review_completed": False,
    "tax_review_completed": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "invoice_process_ready": False,
    "invoice_created": False,
    "invoice_sent_to_customer": False,
    "invoice_template_published": False,
    "enterprise_contract_signed": False,
    "payment_provider_selected": False,
    "payment_provider_configured": False,
    "checkout_enabled": False,
    "payment_link_created": False,
    "customer_payment_collected": False,
    "paid_pilot_completed": False,
    "revenue_validated": False,
    "tax_collection_started": False,
    "refund_policy_published": False,
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
        "invoice_owner_requires_separate_approval": True,
        "invoice_workflow_requires_separate_approval": True,
        "contract_handoff_requires_separate_approval": True,
        "payment_reconciliation_requires_separate_approval": True,
        "bookkeeping_review_required_before_invoice_use": True,
        "legal_and_tax_review_required_before_customer_invoice": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_invoice_process_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_invoice_process_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "invoice_process_human_review_packet_only",
        "blocker_target": "invoice_process",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "invoice_process_approval_status": "not_approved",
        "required_invoice_process_sections": REQUIRED_INVOICE_PROCESS_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "invoice_process_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human commercial, legal, tax, accounting, and support owners must "
            "review invoice ownership, workflow, contract handoff, reconciliation, "
            "bookkeeping, dispute handling, and tenant invoice boundaries before "
            "the invoice_process blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_invoice_process_sections"]
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
    return f"""# SAEE Invoice Process Review Packet v0.1

Status: draft ready for human review; invoice process not approved.

This packet converts the `invoice_process` commercial blocker into a concrete
human review surface. It does not create invoice templates, create or send
invoices, sign contracts, configure payment providers, collect payment,
validate revenue, contact customers, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
invoice_process_approval_status: {packet['invoice_process_approval_status']}
ready_for_human_review: true
invoice_process_evidence_complete: false
production_billing_revenue_ready: false
```

## Required Invoice Process Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Commercial owner
- Legal owner
- Tax / accounting owner
- Billing support owner
- Tenant / privacy boundary owner

## Non-Approval Statement

This packet is not an invoice workflow, not a contract handoff, not an
accounting approval, not customer billing evidence, and not production billing
evidence by itself. The `invoice_process` blocker remains open until invoice
ownership, workflow, reconciliation, bookkeeping, dispute handling, tax/legal
handoff, and tenant invoice boundaries are approved and backed by
human-provided evidence.
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
        "SAEE_INVOICE_PROCESS_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "invoice_process_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
