# SAEE Billing / Pricing Readiness v0.1

Status: controlled-preview billing and pricing readiness, not published pricing
and not revenue validation.

## Purpose

SAEE Billing / Pricing Readiness v0.1 makes the commercial pricing and billing
boundary machine-readable. It records that an internal MVP pricing and packaging
plan exists, while keeping all customer-facing payment, invoice, tax, contract,
and revenue claims false.

This layer is useful before controlled preview because pricing language can
create product-launch or revenue claims if it is not explicitly bounded.

## Current Source Material

- `phase_b_product/mvp/MVP_PRICING_AND_PACKAGING.md`

That file is an internal packaging plan. It is not a public pricing page, not a
sales offer, not a payment flow, and not a signed customer agreement.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and Rollback Immune System readiness by
   keeping monetization assumptions separate from runtime behavior.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves commercial-boundary sensing and evidence archiving. It does not
   modify scoring, fitness, selection, mutation, lineage, runtime, kernel, API
   schema, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It is documentation and deterministic local reporting only. It makes no
   external calls, configures no payment provider, collects no payment, and
   contacts no customer.

4. Could this change push the project back into audit-first framing?

   No. Billing readiness supports controlled commercialization of SAEE's agent
   stability evaluation surface. It does not reframe SAEE as an audit SDK.

## Current State

```text
billing_pricing_readiness_v0_1: true
billing_pricing_status: hold
pricing_packaging_plan_available: true
internal_price_bands_available: true
billing_policy_draft_available: true
pricing_page_published: false
sales_offer_sent: false
paid_product_launched: false
enterprise_contract_signed: false
payment_provider_configured: false
checkout_enabled: false
invoice_process_ready: false
tax_review_completed: false
refund_policy_available: false
billing_operations_ready: false
tenant_billing_isolated: false
customer_payment_collected: false
paid_pilot_completed: false
revenue_validated: false
product_market_fit_claimed: false
production_readiness_claimed: false
customer_contacted: false
customer_validated: false
product_launched: false
production_ready: false
public_sdk_released: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## Hold Reasons

- No public pricing page has been approved.
- No sales offer has been sent.
- No payment provider, checkout flow, invoice process, tax review, or refund
  policy is configured.
- No paid pilot, payment, invoice, or revenue validation has been recorded.
- Tenant billing isolation is not available.

## Allowed Next Actions

- Review the internal price bands against pilot feedback.
- Draft a billing policy for human/legal review.
- Draft refund, invoice, tax, and procurement notes for later review.
- Keep all pricing and payment claims out of public launch materials until
  separately approved.

## Forbidden Claims

- Do not claim SAEE has published pricing.
- Do not claim SAEE has collected payment or validated revenue.
- Do not claim SAEE has a payment provider, checkout flow, or invoice process.
- Do not claim SAEE has enterprise contracts or signed customers.
- Do not claim SAEE is production-ready or commercially launched.
