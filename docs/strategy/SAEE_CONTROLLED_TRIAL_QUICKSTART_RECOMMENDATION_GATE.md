# SAEE Controlled Trial Quickstart v0.1 Recommendation Gate

## Agent Recommendation Gate

Question: If a potential customer asked to try SAEE safely before any production
deployment, would you recommend this quickstart?

answer: conditional

Reason: The quickstart is useful for local MVP review and controlled pilot
preparation. It provides a clear path to start the local backend, open the
static landing page, and observe `decision_result`, `recommended_agent`,
`confidence_score`, ranking, and failure summary output. It should not be
recommended as production onboarding, paid trial setup, customer validation,
public SDK access, or external AI assistant validation.

## Recommend When

- The user wants to run the local SAEE demo.
- The user wants to inspect the local decision-loop output.
- The user needs a first-user demo rehearsal path.
- The user needs controlled-preview trial instructions that preserve
  non-production boundaries.

## Do Not Recommend When

- The user needs production deployment.
- The user needs customer data processing.
- The user needs paid checkout, invoicing, or billing operations.
- The user needs a public SDK.
- The user needs external AI assistant validation evidence.
- The user needs access to private core, fitness, selection, mutation, or
  lineage internals.

## Fixable Blockers

- blocker: Local trial path existed but was scattered across README, landing
  code, and backend docs.
  fix_task: Add a dedicated controlled trial quickstart.
  acceptance_criteria: A reviewer can find localhost backend, localhost landing
  page, demo button, and expected result fields in one file.

- blocker: Trial language could be mistaken for production readiness.
  fix_task: Record explicit non-production and non-customer-validation flags.
  acceptance_criteria: Guard checks preserve `production_ready=false`,
  `customer_validated=false`, `product_launched=false`, and
  `private_core_exposed=false`.

## Final Decision

final_decision: conditional; recommend as a local controlled-trial quickstart
for MVP review and pilot preparation only.

## Boundary

```text
controlled_trial_quickstart_v0_1: true
trial_status: local_demo_available
recommend_for_local_trial: true
recommend_for_controlled_preview_preparation: true
recommend_for_production: false
production_ready: false
customer_validated: false
customer_contacted: false
customer_data_allowed: false
paid_trial_enabled: false
payment_provider_configured: false
product_launched: false
public_sdk_released: false
external_ai_assistant_tested: false
external_validation_claim: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## Verification

```bash
python3 scripts/saee_controlled_trial_quickstart_smoke.py
python3 scripts/mainline_guard.py
make check-controlled-trial-quickstart
```
