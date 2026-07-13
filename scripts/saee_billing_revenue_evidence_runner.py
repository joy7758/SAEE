#!/usr/bin/env python3
"""Generate local public-shell billing/revenue evidence.

This runner converts existing billing/pricing readiness checks into a partial
production billing/revenue evidence JSON file for human review. It does not
publish pricing, configure payment providers, enable checkout, create invoices,
contact tax/legal/payment vendors, collect payment, validate revenue, modify
backend behavior, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.billing_pricing_readiness import (
    evaluate_billing_pricing_readiness,
)
from saee_backend.services.production_billing_revenue_evidence import (
    FORBIDDEN_TRUE_KEYS,
    INVOICE_PROCESS_KEYS,
    PAYMENT_PROVIDER_KEYS,
    PRICING_PAGE_KEYS,
    REFUND_POLICY_KEYS,
    TAX_REVIEW_KEYS,
    TENANT_BILLING_ISOLATION_KEYS,
    evaluate_production_billing_revenue_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
OUTPUT_PATH = OUTPUT_DIR / "billing_revenue_evidence.local.json"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_local_billing_revenue_evidence() -> dict[str, Any]:
    readiness = evaluate_billing_pricing_readiness(load_settings({}))

    require(
        readiness["billing_pricing_readiness_type"]
        == "controlled_preview_billing_pricing_readiness",
        "wrong billing/pricing readiness type",
    )
    require(
        readiness["pricing_packaging_plan_available"] is True,
        "pricing/packaging plan must be available",
    )
    require(
        readiness["internal_price_bands_available"] is True,
        "internal price bands must be available",
    )
    require(
        readiness["billing_policy_draft_available"] is True,
        "billing policy draft must be available",
    )
    require(
        readiness["pricing_page_published"] is False,
        "runner must not publish pricing page",
    )
    require(
        readiness["payment_provider_configured"] is False,
        "runner must not configure payment provider",
    )
    require(readiness["checkout_enabled"] is False, "runner must not enable checkout")
    require(
        readiness["invoice_process_ready"] is False,
        "runner must not claim invoice process readiness",
    )
    require(
        readiness["tax_review_completed"] is False,
        "runner must not claim tax review",
    )
    require(
        readiness["refund_policy_available"] is False,
        "runner must not claim refund policy availability",
    )
    require(
        readiness["tenant_billing_isolated"] is False,
        "runner must not claim tenant billing isolation",
    )
    require(readiness["revenue_validated"] is False, "runner must not validate revenue")
    require(readiness["external_calls_made"] is False, "runner must not call external services")
    require(readiness["customer_contacted"] is False, "runner must not contact customers")
    return readiness


def build_evidence() -> dict[str, Any]:
    readiness = run_local_billing_revenue_evidence()

    evidence: dict[str, Any] = {
        "billing_revenue_evidence_type": "production_billing_revenue_evidence",
        "evidence_scope": "local_public_shell_billing_revenue_review_packet",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_billing_revenue_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_billing_pricing_helper": "saee_backend/services/billing_pricing_readiness.py",
        "human_approved_pricing_page_copy": False,
        "approved_plan_and_usage_terms": False,
        "legal_review_completed": False,
        "production_readiness_non_claim_reviewed": True,
        "pricing_page_publication_approval_recorded": False,
        "payment_provider_selected": False,
        "test_mode_configuration_reviewed": False,
        "checkout_enablement_approval_required": True,
        "webhook_signature_validation_tested": False,
        "payment_event_redaction_reviewed": False,
        "security_review_completed": False,
        "invoice_owner_named": False,
        "invoice_workflow_approved": False,
        "contract_handoff_defined": False,
        "payment_reconciliation_tested": False,
        "billing_support_handoff_defined": False,
        "bookkeeping_review_completed": False,
        "target_jurisdictions_reviewed": False,
        "tax_obligations_reviewed": False,
        "invoice_wording_approved": False,
        "currency_policy_approved": False,
        "tax_collection_approval_recorded": False,
        "refund_policy_approved": False,
        "cancellation_process_approved": False,
        "trial_conversion_policy_approved": False,
        "service_failure_remedy_boundary_approved": False,
        "support_escalation_route_defined": False,
        "tenant_billing_isolation_review_packet_ready": True,
        "tenant_billing_isolation_approval_status": "not_approved",
        "tenant_billing_isolation_evidence_complete": False,
        "tenant_billing_account_model_approved": False,
        "tenant_invoice_partitioning_tested": False,
        "tenant_payment_event_partitioning_tested": False,
        "cross_tenant_billing_access_tests_passed": False,
        "billing_audit_metadata_policy_approved": False,
        "tenant_billing_retention_policy_approved": False,
        "local_public_shell_results": {
            "billing_pricing_readiness_type": readiness[
                "billing_pricing_readiness_type"
            ],
            "billing_pricing_status": readiness["billing_pricing_status"],
            "pricing_packaging_plan_available": True,
            "internal_price_bands_available": True,
            "billing_policy_draft_available": True,
            "pricing_page_published": False,
            "sales_offer_sent": False,
            "paid_product_launched": False,
            "enterprise_contract_signed": False,
            "payment_provider_configured": False,
            "checkout_enabled": False,
            "invoice_process_ready": False,
            "tax_review_completed": False,
            "refund_policy_available": False,
            "billing_operations_ready": False,
            "tenant_billing_isolated": False,
            "customer_payment_collected": False,
            "paid_pilot_completed": False,
            "revenue_validated": False,
            "external_calls_made": False,
            "customer_contacted": False,
        },
        "limitations": [
            "No human-approved customer-facing pricing page exists.",
            "No approved public plan terms, usage terms, or publication approval exists.",
            "No payment provider has been selected or configured.",
            "No checkout flow, payment link, or live-mode payment path is enabled.",
            "No webhook signature validation, payment-event redaction review, or security review is complete.",
            "No invoice workflow, payment reconciliation, bookkeeping review, or billing support handoff is approved.",
            "No tax jurisdiction, obligation, currency, wording, or tax collection approval is complete.",
            "No refund, cancellation, trial conversion, or service-failure remedy policy is approved.",
            "No tenant billing account model, invoice partitioning, payment-event partitioning, or cross-tenant billing test is complete.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in PRICING_PAGE_KEYS
        + PAYMENT_PROVIDER_KEYS
        + INVOICE_PROCESS_KEYS
        + TAX_REVIEW_KEYS
        + REFUND_POLICY_KEYS
        + TENANT_BILLING_ISOLATION_KEYS
        + FORBIDDEN_TRUE_KEYS
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Billing / Revenue Evidence

Status: local public-shell billing/revenue review evidence, not production
billing readiness.

This directory contains generated local evidence files for controlled preview
billing and revenue materials. It records only what the local runner and
human-review packet can prove.

It does not publish pricing, send sales offers, configure payment providers,
enable checkout, create payment links, create or send invoices, contact
customers, contact payment/tax/legal vendors, collect payment, validate
revenue, modify runtime behavior, modify backend behavior, modify API schema,
or expose private core.

Primary files:

```text
billing_revenue_evidence.local.json
pricing_page_review_packet.local.json
pricing_page_review_packet.md
pricing_page_copy_draft.local.json
pricing_page_copy_draft.md
pricing_page_copy_draft_boundary_audit.md
pricing_page_evidence_input.template.json
pricing_page_evidence_builder_output.local.json
production_billing_revenue_evidence.from_pricing_page.local.json
pricing_page_evidence_builder_report.md
pricing_page_approval_input_prompt.local.json
pricing_page_approval_input_prompt.md
pricing_page_approval_input_prompt.html
payment_provider_review_packet.local.json
payment_provider_review_packet.md
payment_provider_evidence_input.template.json
payment_provider_evidence_builder_output.local.json
production_billing_revenue_evidence.from_payment_provider.local.json
payment_provider_evidence_builder_report.md
payment_provider_approval_input_prompt.local.json
payment_provider_approval_input_prompt.md
payment_provider_approval_input_prompt.html
payment_provider_approval_input_validation.local.json
payment_provider_approval_input_validation.md
invoice_process_review_packet.local.json
invoice_process_review_packet.md
invoice_process_evidence_input.template.json
invoice_process_evidence_builder_output.local.json
production_billing_revenue_evidence.from_invoice_process.local.json
invoice_process_evidence_builder_report.md
invoice_process_approval_input_prompt.local.json
invoice_process_approval_input_prompt.md
invoice_process_approval_input_prompt.html
invoice_process_approval_input_validation.local.json
invoice_process_approval_input_validation.md
tax_review_packet.local.json
tax_review_packet.md
tax_review_evidence_input.template.json
tax_review_evidence_builder_output.local.json
production_billing_revenue_evidence.from_tax_review.local.json
tax_review_evidence_builder_report.md
tax_review_approval_input_prompt.local.json
tax_review_approval_input_prompt.md
tax_review_approval_input_prompt.html
tax_review_approval_input_validation.local.json
tax_review_approval_input_validation.md
refund_policy_review_packet.local.json
refund_policy_review_packet.md
refund_policy_evidence_input.template.json
refund_policy_evidence_builder_output.local.json
production_billing_revenue_evidence.from_refund_policy.local.json
refund_policy_evidence_builder_report.md
refund_policy_approval_input_prompt.local.json
refund_policy_approval_input_prompt.md
refund_policy_approval_input_prompt.html
refund_policy_approval_input_validation.local.json
refund_policy_approval_input_validation.md
tenant_billing_isolation_review_packet.local.json
tenant_billing_isolation_review_packet.md
tenant_billing_isolation_evidence_input.template.json
tenant_billing_isolation_evidence_builder_output.local.json
production_billing_revenue_evidence.from_tenant_billing_isolation.local.json
tenant_billing_isolation_evidence_builder_report.md
tenant_billing_isolation_approval_input_prompt.local.json
tenant_billing_isolation_approval_input_prompt.md
tenant_billing_isolation_approval_input_prompt.html
tenant_billing_isolation_approval_input_validation.local.json
tenant_billing_isolation_approval_input_validation.md
billing_revenue_evidence_profile.local.json
production_billing_revenue_evidence.combined_profile.local.json
billing_revenue_evidence_profile_report.md
```

Generate it with:

```bash
python3 scripts/saee_billing_revenue_evidence_runner.py
python3 scripts/saee_pricing_page_review_packet.py
python3 scripts/saee_pricing_page_copy_draft.py
python3 scripts/saee_pricing_page_evidence_builder.py
python3 scripts/saee_pricing_page_approval_input_prompt.py
python3 scripts/saee_payment_provider_review_packet.py
python3 scripts/saee_payment_provider_evidence_builder.py
python3 scripts/saee_payment_provider_approval_input_prompt.py
python3 scripts/saee_payment_provider_approval_input_validator.py
python3 scripts/saee_invoice_process_review_packet.py
python3 scripts/saee_invoice_process_evidence_builder.py
python3 scripts/saee_invoice_process_approval_input_prompt.py
python3 scripts/saee_invoice_process_approval_input_validator.py
python3 scripts/saee_tax_review_packet.py
python3 scripts/saee_tax_review_evidence_builder.py
python3 scripts/saee_tax_review_approval_input_prompt.py
python3 scripts/saee_tax_review_approval_input_validator.py
python3 scripts/saee_refund_policy_review_packet.py
python3 scripts/saee_refund_policy_evidence_builder.py
python3 scripts/saee_refund_policy_approval_input_prompt.py
python3 scripts/saee_refund_policy_approval_input_validator.py
python3 scripts/saee_tenant_billing_isolation_review_packet.py
python3 scripts/saee_tenant_billing_isolation_evidence_builder.py
python3 scripts/saee_tenant_billing_isolation_approval_input_prompt.py
python3 scripts/saee_tenant_billing_isolation_approval_input_validator.py
python3 scripts/saee_billing_revenue_evidence_profile.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_billing_revenue_review_packet
pricing_packaging_plan_available: true
internal_price_bands_available: true
billing_policy_draft_available: true
pricing_page_review_packet_ready: true
pricing_page_copy_draft_available: true
pricing_page_copy_draft_status: draft_not_approved
pricing_page_evidence_builder_available: true
pricing_page_evidence_builder_status: local_builder_available_default_hold
pricing_page_evidence_complete_for_review: false
pricing_page_evidence_complete: false
pricing_page_publication_approval_status: not_approved
pricing_page_approval_input_prompt_available: true
pricing_page_approval_input_prompt_status: hold_human_pricing_page_input_required
pricing_page_approval_input_prompt_plain_language_entry: true
plain_language_pricing_page_review_entry_v0_2: true
pricing_page_approval_input_prompt_required_metadata_fields: 9
pricing_page_approval_input_prompt_required_pricing_page_evidence_items: 5
pricing_page_approval_input_prompt_ready_for_validator: false
pricing_page_approval_input_prompt_builder_ready: false
pricing_page_approval_input_prompt_closes_blockers: false
payment_provider_review_packet_ready: true
payment_provider_evidence_complete: false
provider_selection_status: not_selected
payment_provider_evidence_builder_available: true
payment_provider_evidence_builder_status: local_builder_available_default_hold
payment_provider_evidence_complete_for_review: false
payment_provider_approval_input_prompt_available: true
payment_provider_approval_input_prompt_status: hold_human_payment_provider_input_required
payment_provider_approval_input_prompt_plain_language_entry: true
plain_language_payment_provider_review_entry_v0_2: true
payment_provider_approval_input_prompt_required_metadata_fields: 7
payment_provider_approval_input_prompt_required_payment_provider_evidence_items: 6
payment_provider_approval_input_prompt_ready_for_evidence_builder: false
payment_provider_approval_input_prompt_builder_ready: false
payment_provider_approval_input_prompt_closes_blockers: false
payment_provider_approval_input_validator_available: true
payment_provider_approval_input_validator_status: hold
payment_provider_approval_input_validator_builder_ready: false
payment_provider_approval_input_validator_closes_blockers: 0
invoice_process_review_packet_ready: true
invoice_process_evidence_complete: false
invoice_process_approval_status: not_approved
invoice_process_evidence_builder_available: true
invoice_process_evidence_builder_status: local_builder_available_default_hold
invoice_process_evidence_complete_for_review: false
invoice_process_approval_input_prompt_available: true
invoice_process_approval_input_prompt_status: hold_human_invoice_process_input_required
invoice_process_approval_input_prompt_plain_language_entry: true
plain_language_invoice_process_review_entry_v0_2: true
invoice_process_approval_input_prompt_required_metadata_fields: 8
invoice_process_approval_input_prompt_required_invoice_process_evidence_items: 6
invoice_process_approval_input_prompt_ready_for_evidence_builder: false
invoice_process_approval_input_prompt_builder_ready: false
invoice_process_approval_input_prompt_closes_blockers: false
invoice_process_approval_input_validator_available: true
invoice_process_approval_input_validator_status: hold
invoice_process_approval_input_validator_builder_ready: false
invoice_process_approval_input_validator_closes_blockers: 0
tax_review_packet_ready: true
tax_review_evidence_complete: false
tax_review_approval_status: not_approved
tax_review_evidence_builder_available: true
tax_review_evidence_builder_status: local_builder_available_default_hold
tax_review_evidence_complete_for_review: false
tax_review_approval_input_prompt_available: true
tax_review_approval_input_prompt_status: hold_human_tax_review_input_required
tax_review_approval_input_prompt_plain_language_entry: true
plain_language_tax_review_entry_v0_2: true
tax_review_approval_input_prompt_required_metadata_fields: 9
tax_review_approval_input_prompt_required_tax_review_evidence_items: 5
tax_review_approval_input_prompt_ready_for_evidence_builder: false
tax_review_approval_input_prompt_builder_ready: false
tax_review_approval_input_prompt_closes_blockers: false
tax_review_approval_input_validator_available: true
tax_review_approval_input_validator_status: hold
tax_review_approval_input_validator_builder_ready: false
tax_review_approval_input_validator_closes_blockers: 0
refund_policy_review_packet_ready: true
refund_policy_evidence_complete: false
refund_policy_approval_status: not_approved
refund_policy_evidence_builder_available: true
refund_policy_evidence_builder_status: local_builder_available_default_hold
refund_policy_evidence_complete_for_review: false
refund_policy_approval_input_prompt_available: true
refund_policy_approval_input_prompt_status: hold_human_refund_policy_input_required
refund_policy_approval_input_prompt_plain_language_entry: true
plain_language_refund_policy_entry_v0_2: true
refund_policy_approval_input_prompt_required_metadata_fields: 11
refund_policy_approval_input_prompt_required_refund_policy_evidence_items: 5
refund_policy_approval_input_prompt_ready_for_evidence_builder: false
refund_policy_approval_input_prompt_builder_ready: false
refund_policy_approval_input_prompt_closes_blockers: false
refund_policy_approval_input_validator_available: true
refund_policy_approval_input_validator_status: hold
refund_policy_approval_input_validator_builder_ready: false
refund_policy_approval_input_validator_closes_blockers: 0
tenant_billing_isolation_review_packet_ready: true
tenant_billing_isolation_evidence_complete: false
tenant_billing_isolation_approval_status: not_approved
tenant_billing_isolation_evidence_builder_available: true
tenant_billing_isolation_evidence_builder_status: local_builder_available_default_hold
tenant_billing_isolation_evidence_complete_for_review: false
tenant_billing_isolation_approval_input_prompt_available: true
tenant_billing_isolation_approval_input_prompt_status: hold_human_tenant_billing_isolation_input_required
tenant_billing_isolation_approval_input_prompt_required_metadata_fields: 11
tenant_billing_isolation_approval_input_prompt_required_tenant_billing_isolation_evidence_items: 6
tenant_billing_isolation_approval_input_prompt_browser_readable_html: true
plain_language_tenant_billing_isolation_entry_v0_2: true
tenant_billing_isolation_approval_input_prompt_ready_for_evidence_builder: false
tenant_billing_isolation_approval_input_prompt_builder_ready: false
tenant_billing_isolation_approval_input_prompt_closes_blockers: false
tenant_billing_isolation_approval_input_validator_available: true
tenant_billing_isolation_approval_input_validator_status: hold
tenant_billing_isolation_approval_input_validator_builder_ready: false
tenant_billing_isolation_approval_input_validator_closes_blockers: 0
billing_revenue_evidence_profile_available: true
billing_revenue_evidence_profile_status: local_combined_billing_revenue_profile_hold
billing_revenue_evidence_profile_scope: combined_billing_revenue_evidence_profile_to_go_no_go
billing_revenue_evidence_profile_target_blockers_satisfied: 0
billing_revenue_evidence_profile_production_blocker_count: 24
billing_revenue_evidence_profile_closes_blockers: false
pricing_page_published: false
payment_provider_configured: false
checkout_enabled: false
invoice_process_ready: false
tax_review_completed: false
refund_policy_available: false
tenant_billing_isolated: false
production_billing_revenue_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
customer_contacted: false
```

The pricing page review packet is a draft for human review only. It does not
publish pricing, create a sales offer, configure payment providers, enable
checkout, collect payment, validate revenue, contact customers, or make SAEE
production-ready.

The pricing page copy draft is a documentation-only human-review surface. It
does not publish pricing, create customer-facing offers, approve plan names,
configure payment, collect payment, validate revenue, contact customers, or
make SAEE production-ready.

The payment provider review packet is a draft for human review only. It does
not select or contact a payment provider, configure test or live mode, enable
checkout, create payment links, collect payment, validate revenue, contact
customers, or make SAEE production-ready.

The payment provider evidence builder is a local human-input converter. It
does not select or contact a payment provider, configure test or live mode,
enable checkout, create payment links, process webhooks, collect payment,
validate revenue, close blockers, or make SAEE production-ready.

The invoice process review packet is a draft for human review only. It does
not create invoice templates, create or send invoices, sign contracts, perform
reconciliation, collect payment, validate revenue, contact customers, or make
SAEE production-ready.

The invoice process evidence builder is a local human-input converter. It does
not create invoice templates, create or send invoices, sign contracts, perform
reconciliation, collect payment, validate revenue, close blockers, or make
SAEE production-ready.

The tax review packet is a draft for human review only. It does not contact
tax advisors or legal counsel, complete tax review, configure tax collection,
collect payment, validate revenue, contact customers, or make SAEE
production-ready.

The tax review evidence builder is a local human-input converter. It does not
contact tax advisors or legal counsel, complete tax review, configure tax
rates, start tax collection, collect payment, validate revenue, close blockers,
or make SAEE production-ready.

The refund policy review packet is a draft for human review only. It does not
publish a refund policy, approve cancellation handling, process refunds,
configure payment-provider refund handling, collect payment, validate revenue,
contact customers, or make SAEE production-ready.

The refund policy evidence builder is a local human-input converter. It does
not publish a refund policy, approve cancellation handling, process refunds,
configure payment-provider refund handling, collect payment, validate revenue,
close blockers, or make SAEE production-ready.

The tenant billing isolation review packet is a draft for human review only.
It does not approve a tenant billing account model, test cross-tenant billing
access, configure payment-provider tenant mapping, collect payment, validate
revenue, contact customers, or make SAEE production-ready.

The tenant billing isolation evidence builder is a local human-input converter.
It does not approve a tenant billing account model, test cross-tenant billing
access, configure payment-provider tenant mapping, collect payment, validate
revenue, close blockers, or make SAEE production-ready.

The billing / revenue evidence profile is a local go/no-go input combiner. It
does not create any evidence source, publish pricing, select payment providers,
enable checkout, issue invoices, collect payment, validate revenue, contact
customers, close blockers by itself, or make SAEE production-ready.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme()
    readiness = evaluate_production_billing_revenue_evidence(
        load_settings(
            {"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(OUTPUT_PATH)}
        )
    )
    print(
        "SAEE_BILLING_REVENUE_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_billing_revenue_ready=false"
    )


if __name__ == "__main__":
    main()
