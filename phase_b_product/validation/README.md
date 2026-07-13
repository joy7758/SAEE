# SAEE Product Validation Layer

Status: first-user test planning only, not customer validation and not product
launch.

## Purpose

This folder defines how to test whether SAEE's interactive MVP decision output
is commercially useful.

The validation target is:

```text
Goal = Validate decision usefulness of SAEE output
```

This is a value-loop validation layer. It does not add product features, change
the SAEE decision engine, or enable user uploads.

## Files

- `SAEE_FIRST_USER_TEST_PLAN.md`: target users, session script, metrics, and execution protocol.
- `FIRST_USER_FEEDBACK_FORM.md`: questions for demo participants.
- `FIRST_USER_SUCCESS_CRITERIA.md`: go / hold / pivot thresholds.
- `PILOT_RESULT_TEMPLATE.json`: machine-readable template for future human-approved pilot evidence.
- `LOCAL_MVP_TRYOUT_GUIDE_V0_1.md`: shortest safe local tryout path and evidence handoff.
- `local_mvp_tryout_status.json`: machine-readable local tryout boundary status.

## Boundary

```yaml
first_user_test_plan_created: true
pilot_result_template_available: true
pilot_sessions_completed: 0
pilot_results_recorded: false
customer_permission_recorded: false
customer_validated: false
customer_contacted: false
product_launched: false
production_deployed: false
public_sdk_release: false
user_upload_enabled: false
customer_data_processing_ready: false
api_contract_modified: false
api_schema_modified: false
landing_page_modified: false
decision_engine_modified: false
private_core_exported: false
implementation_disclosed: false
local_mvp_tryout_guide_available: true
blockers_closed_by_tryout_guide: 0
```
