#!/usr/bin/env python3
"""Generate the SAEE tenant billing isolation human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not approve tenant billing isolation, test cross-tenant billing access,
configure payment provider tenant mapping, collect payment, validate revenue,
or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
PACKET_JSON = OUTPUT_DIR / "tenant_billing_isolation_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "tenant_billing_isolation_review_packet.md"

REQUIRED_TENANT_BILLING_ISOLATION_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "tenant_billing_account_model_approved": False,
    "tenant_invoice_partitioning_approved": False,
    "tenant_payment_event_partitioning_approved": False,
    "cross_tenant_billing_access_tests_passed": False,
    "billing_audit_metadata_policy_approved": False,
    "tenant_billing_export_policy_approved": False,
    "tenant_billing_retention_policy_approved": False,
    "tenant_invoice_numbering_approved": False,
    "tenant_refund_partitioning_approved": False,
    "payment_provider_tenant_mapping_approved": False,
    "tenant_privacy_security_review_completed": False,
    "legal_review_completed": False,
    "accounting_review_completed": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "tenant_billing_isolated": False,
    "tenant_billing_isolation_enabled": False,
    "tenant_billing_isolation_evidence_complete": False,
    "tenant_billing_account_model_available": False,
    "tenant_invoice_partitioning_tested": False,
    "tenant_payment_event_partitioning_tested": False,
    "cross_tenant_billing_access_tests_passed": False,
    "billing_audit_metadata_policy_available": False,
    "tenant_billing_export_policy_available": False,
    "tenant_billing_retention_policy_available": False,
    "tenant_invoice_numbering_available": False,
    "tenant_refund_partitioning_available": False,
    "payment_provider_tenant_mapping_configured": False,
    "payment_provider_configured": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "paid_pilot_completed": False,
    "revenue_validated": False,
    "invoice_sent_to_customer": False,
    "refund_policy_published": False,
    "tax_review_completed": False,
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
        "tenant_billing_account_model_requires_approval": True,
        "invoice_partitioning_requires_accounting_review": True,
        "payment_event_partitioning_requires_security_review": True,
        "cross_tenant_access_tests_require_execution_approval": True,
        "billing_audit_metadata_requires_privacy_review": True,
        "export_policy_requires_legal_review": True,
        "retention_policy_requires_privacy_and_accounting_review": True,
        "payment_provider_mapping_requires_separate_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_tenant_billing_isolation_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_tenant_billing_isolation_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "tenant_billing_isolation_human_review_packet_only",
        "blocker_target": "tenant_billing_isolation",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "tenant_billing_isolation_approval_status": "not_approved",
        "required_tenant_billing_isolation_sections": (
            REQUIRED_TENANT_BILLING_ISOLATION_SECTIONS
        ),
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "tenant_billing_isolation_evidence_complete": False,
        "production_billing_revenue_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human commercial, accounting, security, privacy, legal, and "
            "payment-provider owners must review tenant billing account model, "
            "invoice partitioning, payment-event partitioning, cross-tenant "
            "billing access tests, billing audit metadata, export policy, "
            "retention policy, invoice numbering, refund partitioning, and "
            "provider tenant mapping before the tenant_billing_isolation "
            "blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_tenant_billing_isolation_sections"]
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
    return f"""# SAEE Tenant Billing Isolation Review Packet v0.1

Status: draft ready for human review; tenant billing isolation not approved.

This packet converts the `tenant_billing_isolation` commercial blocker into a
concrete human review surface. It does not approve a tenant billing account
model, test cross-tenant billing access, configure payment provider tenant
mapping, collect payment, validate revenue, contact customers, or make SAEE
production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
tenant_billing_isolation_approval_status: {packet['tenant_billing_isolation_approval_status']}
ready_for_human_review: true
tenant_billing_isolation_evidence_complete: false
production_billing_revenue_ready: false
```

## Required Tenant Billing Isolation Sections

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
- Accounting / billing owner
- Security owner
- Privacy owner
- Legal owner
- Payment provider owner
- Tenant boundary owner

## Non-Approval Statement

This packet is not an approved tenant billing account model, not an invoice
partitioning test, not a payment-event partitioning test, not a cross-tenant
billing access test result, not a payment-provider tenant mapping, not customer
billing evidence, and not production billing evidence by itself. The
`tenant_billing_isolation` blocker remains open until the account model,
invoice partitioning, payment-event partitioning, cross-tenant tests, audit
metadata, export policy, retention policy, invoice numbering, refund
partitioning, provider tenant mapping, and privacy/security/legal handoffs are
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
        "SAEE_TENANT_BILLING_ISOLATION_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "tenant_billing_isolation_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
