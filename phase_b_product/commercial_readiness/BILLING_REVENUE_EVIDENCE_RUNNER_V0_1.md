# SAEE Billing / Revenue Evidence Runner v0.1

Status: local public-shell billing/revenue evidence generated for human
review, not production billing readiness.

## Purpose

This runner converts the controlled-preview billing/pricing readiness surface
into a local evidence JSON file. It helps commercial review see which
billing/revenue materials are already demonstrated and which production
billing blockers remain open.

It strengthens the commercial evidence surface. It does not modify runtime
behavior, backend route behavior, API schema, kernel, private core, pricing
publication, payment providers, checkout, invoices, tax collection, refund
policy publication, customer contact, payment collection, revenue validation,
or production launch behavior.

## Entrypoints

```text
scripts/saee_billing_revenue_evidence_runner.py
scripts/saee_billing_revenue_evidence_runner_smoke.py
phase_b_product/commercial_readiness/billing_revenue_evidence/
```

Generated evidence file:

```text
phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json
```

## What The Runner Verifies

- Internal pricing/packaging plan material is available for review.
- Internal price bands are available for review.
- Billing policy draft material is available for review.
- Production-readiness non-claim review can be recorded.
- Checkout enablement remains approval-gated.
- The runner does not publish pricing.
- The runner does not configure a payment provider.
- The runner does not enable checkout or create payment links.
- The runner does not create invoices, collect tax, collect payment, or validate revenue.
- The runner does not contact customers, payment providers, tax advisors, or legal counsel.

## What Remains Unproven

- Human-approved customer-facing pricing page copy.
- Approved plan and usage terms.
- Legal review and pricing-page publication approval.
- Payment provider selection and test-mode review.
- Webhook signature validation, payment-event redaction review, and security review.
- Invoice owner, invoice workflow, payment reconciliation, and bookkeeping review.
- Tax jurisdiction, tax obligation, invoice wording, currency, and tax collection approval.
- Refund, cancellation, trial conversion, service-failure remedy, and support escalation policy approval.
- Tenant billing account model, invoice partitioning, payment-event partitioning, cross-tenant tests, audit metadata, and retention policy approval.

## Boundary Contract

```yaml
billing_revenue_evidence_runner_v0_1: true
evidence_scope: local_public_shell_billing_revenue_review_packet
evidence_file: phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json
default_status_after_evidence_generation: hold
pricing_packaging_plan_available: true
internal_price_bands_available: true
billing_policy_draft_available: true
production_readiness_non_claim_reviewed: true
checkout_enablement_approval_required: true
pricing_page_evidence_complete: false
payment_provider_evidence_complete: false
invoice_process_evidence_complete: false
tax_review_evidence_complete: false
refund_policy_evidence_complete: false
tenant_billing_isolation_evidence_complete: false
production_billing_revenue_ready: false
pricing_page_published: false
sales_offer_sent: false
paid_product_launched: false
enterprise_contract_signed: false
payment_provider_configured: false
checkout_enabled: false
invoice_process_ready: false
tax_review_completed: false
refund_policy_available: false
tenant_billing_isolated: false
customer_payment_collected: false
paid_pilot_completed: false
revenue_validated: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
payment_provider_contacted: false
tax_advisor_contacted: false
legal_counsel_contacted: false
```

## How To Run

```bash
python3 scripts/saee_billing_revenue_evidence_runner.py
python3 scripts/saee_billing_revenue_evidence_runner_smoke.py
```

The runner writes local evidence only. It does not configure
`SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH` by default and does not close
the production launch gate by itself.

## Recommendation Gate Result

Use this runner for local evidence generation and human commercial review. Do
not recommend it as pricing publication, payment integration, checkout
readiness, invoice readiness, tax approval, refund-policy readiness, tenant
billing isolation, customer payment collection, revenue validation, customer
validation, production billing readiness, or launch approval.
