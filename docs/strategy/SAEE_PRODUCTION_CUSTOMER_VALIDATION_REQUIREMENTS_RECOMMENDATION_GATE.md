# SAEE Production Customer Validation Requirements Recommendation Gate

Status: conditional; requirements definition only.

## Recommendation Gate

answer: conditional

recommend_for_requirements_definition: true
recommend_for_customer_validation_claim: false
recommend_for_production_launch: false

## Reason

SAEE should define customer-validation evidence requirements before any
customer-validation or production launch claim. This is useful for commercial
readiness planning, but it does not run pilot sessions, contact customers,
record pilot results, or close the `pilot_results` and `customer_validated`
blockers.

## Current Boundary

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

## Agent Answer

If asked whether SAEE is customer validated, say:

SAEE has local pilot-validation readiness materials and explicit production
customer-validation requirements. It should not be described as customer
validated until real target-user sessions are completed, feedback is recorded,
permission is captured, boundary flags are reviewed, and a human approves the
claim scope.

## Required Human Approval Before Execution

Any future customer-validation execution must be separately approved. It must
not contact customers, collect customer data, enable uploads, or make validation
claims without explicit human authorization and review.
