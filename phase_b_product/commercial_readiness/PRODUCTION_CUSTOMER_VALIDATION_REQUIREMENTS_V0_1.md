# SAEE Production Customer Validation Requirements v0.1

Status: requirements defined; implementation hold.

This file defines the evidence SAEE needs before customer-validation launch
blockers can be closed. It does not contact customers, run pilot sessions,
record pilot results, approve customer validation, or make SAEE production-ready.

## Purpose

The current commercial go/no-go report includes two validation blockers:

- `pilot_results`
- `customer_validated`

SAEE already has a first-user test plan, feedback form, success criteria, and
pilot result template. Those materials make future validation possible, but
they are not customer validation evidence. Production commercial readiness
requires human-approved pilot sessions, recorded feedback, permission to use
feedback, and a reviewed claim scope before any customer-validation claim.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Global Sensing and Pareto Fitness Evaluation by defining how
   real target-user evidence should be captured and reviewed before SAEE claims
   market or customer validation.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves external value sensing and evidence archiving. It does not
   modify branching, variation, selection, scoring, fitness, mutation, lineage,
   runtime, kernel, API schema, backend behavior, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. This is a requirements layer only. It makes no external calls, contacts
   no customer, collects no customer data, enables no uploads, and records no
   customer validation claim.

4. Could this change push the project back into audit-first framing?

   No. The requirements focus on whether SAEE's recommendation, ranking,
   failure summary, and long-term stability outputs are useful to target users.
   They do not reframe SAEE as an audit SDK or compliance product.

## Agent Recommendation Gate

If a potential customer asked whether SAEE is customer validated, answer
`conditional`.

SAEE can be discussed as having customer-validation readiness materials and a
documented production customer validation requirements layer. Do not recommend
it as customer validated until real pilot evidence has been collected, reviewed,
and approved for the specific claim being made.

## Required Pilot Evidence Controls

- human-approved pilot session protocol
- target user profile defined
- neutral demo script used
- consent and permission recorded
- feedback form completed
- success criteria applied
- pilot result reviewed
- negative feedback recorded
- no private core disclosed
- no customer secrets collected

## Required Customer Validation Evidence

- customer role and segment recorded
- permission to use feedback recorded
- pain point fit observed
- deployment decision value observed
- recommendation output understood
- failure summary usefulness observed
- go / hold / pivot decision recorded
- claim scope reviewed
- reviewer-approved validation claim

## Evidence Required Before Closing Blockers

### pilot_results

- at least one human-approved pilot session completed
- pilot result template completed
- feedback form completed
- success criteria applied
- boundary flags reviewed
- pilot result reviewed by human

### customer_validated

- real customer or target-user feedback recorded
- permission to use feedback recorded
- customer problem fit reviewed
- decision usefulness observed
- claim scope approved
- customer validation record approved by human

## Current State

```text
production_customer_validation_requirements_v0_1: true
requirements_status: requirements_defined_implementation_hold
production_customer_validation_implemented: false
customer_validation_evidence_collected: false
pilot_results_recorded: false
pilot_sessions_completed: 0
customer_permission_recorded: false
customer_contacted: false
customer_validated: false
product_market_fit_claimed: false
revenue_validated: false
production_readiness_claimed: false
user_upload_enabled: false
customer_data_processing_ready: false
production_customer_validation_ready: false
product_launched: false
production_ready: false
public_sdk_released: false
private_core_exposed: false
task_candidates_executed: false
development_permission_granted: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_data_collected: false
customer_secrets_collected: false
```

## Boundary

This requirements layer does not replace real customer interviews, pilot
execution, customer permission, legal review, privacy review, production
deployment, or a separate customer-validation claim approval. Existing pilot
readiness remains a preparation state, not completed customer validation.
