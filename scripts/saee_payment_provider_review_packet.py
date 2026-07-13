#!/usr/bin/env python3
"""Generate the SAEE payment provider human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not select or contact a payment provider, configure test or live mode,
enable checkout, create payment links, collect payment, or mark SAEE
production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PACKET_JSON = OUTPUT_DIR / "payment_provider_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "payment_provider_review_packet.md"

REQUIRED_PAYMENT_PROVIDER_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "human_approved_payment_provider_selection": False,
    "test_mode_configuration_reviewed": False,
    "checkout_enablement_approval_recorded": False,
    "webhook_signature_validation_tested": False,
    "payment_event_redaction_reviewed": False,
    "security_review_completed": False,
    "legal_review_completed": False,
    "tax_review_completed": False,
    "live_mode_approval_recorded": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "payment_provider_selected": False,
    "payment_provider_contacted": False,
    "payment_provider_configured": False,
    "payment_provider_live_mode_enabled": False,
    "checkout_enabled": False,
    "payment_link_created": False,
    "webhook_endpoint_created": False,
    "webhook_secret_configured": False,
    "invoice_sent_to_customer": False,
    "tax_collection_started": False,
    "refund_policy_published": False,
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
        "provider_selection_requires_separate_approval": True,
        "test_mode_configuration_requires_separate_approval": True,
        "live_mode_requires_separate_approval": True,
        "checkout_enablement_requires_separate_approval": True,
        "security_review_required_before_webhooks": True,
        "legal_and_tax_review_required_before_payment_collection": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_payment_provider_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_payment_provider_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "payment_provider_human_review_packet_only",
        "blocker_target": "payment_provider",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "provider_selection_status": "not_selected",
        "required_payment_provider_sections": REQUIRED_PAYMENT_PROVIDER_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "payment_provider_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human product, security, legal, tax, and commercial owners must "
            "review provider selection, test-mode boundaries, webhook security, "
            "and checkout enablement before the payment_provider blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_payment_provider_sections"]
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
    return f"""# SAEE Payment Provider Review Packet v0.1

Status: draft ready for human review; provider not selected or configured.

This packet converts the `payment_provider` commercial blocker into a concrete
human review surface. It does not select or contact a payment provider,
configure test mode, enable live mode, enable checkout, create payment links,
collect payment, validate revenue, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
provider_selection_status: {packet['provider_selection_status']}
ready_for_human_review: true
payment_provider_evidence_complete: false
production_billing_revenue_ready: false
```

## Required Payment Provider Sections

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
- Security owner
- Legal owner
- Tax / accounting owner

## Non-Approval Statement

This packet is not a payment-provider integration, not a checkout path, not a
payment collection approval, and not production billing evidence by itself. The
`payment_provider` blocker remains open until provider selection, test mode,
webhook security, event redaction, checkout enablement, and security review are
approved and backed by human-provided evidence.
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
        "SAEE_PAYMENT_PROVIDER_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "payment_provider_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
