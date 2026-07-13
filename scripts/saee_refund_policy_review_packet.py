#!/usr/bin/env python3
"""Generate the SAEE refund policy human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not publish a refund policy, process refunds, configure payment providers,
collect payment, validate revenue, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PACKET_JSON = OUTPUT_DIR / "refund_policy_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "refund_policy_review_packet.md"

REQUIRED_REFUND_POLICY_SECTIONS = [
    "refund_policy_owner_boundary",
    "refund_eligibility_boundary",
    "cancellation_process_boundary",
    "trial_conversion_policy",
    "service_failure_remedy_boundary",
    "refund_request_workflow",
    "refund_approval_record",
    "refund_tax_and_invoice_handoff",
    "payment_provider_refund_handoff",
    "support_escalation_route",
    "tenant_refund_boundary",
    "private_core_exclusion",
    "approval_record",
]

APPROVAL_FLAGS: dict[str, bool] = {
    "refund_policy_owner_named": False,
    "refund_window_approved": False,
    "eligibility_rules_approved": False,
    "cancellation_process_approved": False,
    "trial_conversion_policy_approved": False,
    "service_failure_remedy_boundary_approved": False,
    "refund_request_workflow_approved": False,
    "refund_tax_handoff_approved": False,
    "payment_provider_refund_handoff_approved": False,
    "support_escalation_route_defined": False,
    "tenant_refund_boundary_reviewed": False,
    "legal_review_completed": False,
    "accounting_review_completed": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "refund_policy_available": False,
    "refund_policy_published": False,
    "refund_policy_approved": False,
    "cancellation_process_available": False,
    "trial_conversion_policy_available": False,
    "service_failure_remedy_available": False,
    "refund_request_workflow_available": False,
    "refund_processed": False,
    "refund_issued_to_customer": False,
    "payment_provider_selected": False,
    "payment_provider_configured": False,
    "checkout_enabled": False,
    "payment_link_created": False,
    "customer_payment_collected": False,
    "paid_pilot_completed": False,
    "revenue_validated": False,
    "invoice_sent_to_customer": False,
    "tax_review_completed": False,
    "tax_collection_started": False,
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
        "refund_policy_owner_requires_separate_approval": True,
        "refund_eligibility_requires_legal_review": True,
        "cancellation_process_requires_support_review": True,
        "trial_conversion_requires_commercial_review": True,
        "service_failure_remedy_requires_legal_review": True,
        "tax_and_invoice_handoff_requires_accounting_review": True,
        "payment_provider_refund_handoff_requires_separate_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_refund_policy_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_refund_policy_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "refund_policy_human_review_packet_only",
        "blocker_target": "refund_policy",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "refund_policy_approval_status": "not_approved",
        "required_refund_policy_sections": REQUIRED_REFUND_POLICY_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "refund_policy_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human legal, accounting, commercial, support, payment, and tenant "
            "boundary owners must review refund eligibility, cancellation, "
            "trial conversion, service-failure remedies, refund workflow, tax "
            "and invoice handoff, provider handoff, and tenant refund boundaries "
            "before the refund_policy blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_refund_policy_sections"]
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
    return f"""# SAEE Refund Policy Review Packet v0.1

Status: draft ready for human review; refund policy not approved.

This packet converts the `refund_policy` commercial blocker into a concrete
human review surface. It does not publish a refund policy, approve
cancellations, process refunds, configure payment providers, collect payment,
validate revenue, contact customers, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
refund_policy_approval_status: {packet['refund_policy_approval_status']}
ready_for_human_review: true
refund_policy_evidence_complete: false
production_billing_revenue_ready: false
```

## Required Refund Policy Sections

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
- Accounting / tax owner
- Commercial owner
- Billing support owner
- Payment provider owner
- Tenant / privacy boundary owner

## Non-Approval Statement

This packet is not an approved refund policy, not a cancellation workflow, not
a payment-provider refund configuration, not customer billing evidence, and not
production billing evidence by itself. The `refund_policy` blocker remains open
until refund eligibility, cancellation, trial conversion, service-failure
remedies, tax and invoice handoff, provider handoff, support escalation, and
tenant refund boundaries are approved and backed by human-provided evidence.
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
        "SAEE_REFUND_POLICY_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "refund_policy_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
