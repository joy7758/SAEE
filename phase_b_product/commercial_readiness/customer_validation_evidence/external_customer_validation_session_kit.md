# SAEE External Customer Validation Session Kit v0.1

Status: ready_for_human_external_customer_validation_session.

This kit helps a human run one external customer or target-user validation
session for SAEE. It is not a validation result. It does not contact anyone,
execute a pilot, collect customer data through Codex, close blockers, launch
product, or claim production readiness.

## What To Use

- Interview script: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_interview_script.md`
- Feedback form: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_feedback_form.template.md`
- Field map: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_field_mapping.csv`
- Existing evidence template: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json`

## Current State

```yaml
external_customer_validation_session_kit_v0_1: true
status: ready_for_human_external_customer_validation_session
current_goal_blocker: customer_validated
remaining_blocker_count: 1
required_real_external_sessions_min: 1
session_kit_ready: true
customer_validated: false
production_ready: false
product_launched: false
customer_contacted_by_codex: false
private_core_exposed: false
blockers_closed_by_session_kit: 0
```

## Human Procedure

1. Human selects one real external customer or target user.
2. Human opens the SAEE demo or screenshots locally.
3. Human uses the interview script and feedback form.
4. Human records only summary feedback and scores. Do not collect secrets,
   source code, credentials, production data, or private workflow internals.
5. Human transfers the result into the existing customer-validation evidence
   JSON template.
6. Only after that, run the existing validator.

## Stop Rules

- Stop if the participant wants to upload production or secret data.
- Stop if private core details would need to be disclosed.
- Stop if anyone asks to claim SAEE is production-ready.
- Stop before publishing testimonials, case studies, or customer-validation
  claims.
