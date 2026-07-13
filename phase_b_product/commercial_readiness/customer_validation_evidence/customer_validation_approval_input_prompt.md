# SAEE Customer Validation Approval Input Prompt v0.1

customer_validation_approval_input_prompt_v0_1: true
status: hold_human_customer_validation_input_required
target_blocker_ids: pilot_results,customer_validated
source_customer_validation_approval_input_prompt_html: phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html
local_static_customer_validation_approval_input_prompt_html: true
browser_readable_customer_validation_approval_input_prompt: true
plain_language_customer_validation_approval_input_prompt_v0_2: true
customer_validation_human_review_step_count: 5
plain_language_status_label: 客户验证还没有完成，也不能对外声称已验证。
required_review_key_count: 25
completed_review_key_count: 0
required_session_text_field_count: 5
required_session_score_field_count: 4
required_session_boundary_false_key_count: 5
completed_session_count: 0
builder_ready: false
pilot_results_recorded: false
customer_validation_approved: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives human reviewers the shortest safe path for filling the local
customer-validation input before any separate validator run or evidence-builder
request.

It is a prompt only. It does not contact customers, run pilot sessions, infer
missing results, collect customer data, publish validation claims, create
testimonials or case studies, close blockers, or claim production readiness.

## Human Procedure

1. Copy the template:

```bash
cp phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json
```

2. Fill at least one real human-approved pilot session in
   `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json`.
3. Set `evidence_review` keys to `true` only when backed by real human-reviewed
   pilot/customer evidence.
4. Keep every boundary flag false unless the review must stop.
5. Run the validator:

```bash
python3 scripts/saee_customer_validation_approval_input_validator.py --input phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json
```

6. Run the evidence builder only after a separate explicit execution request:

```bash
python3 scripts/saee_customer_validation_evidence_builder.py --input phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json
```

## Evidence Review Keys

| evidence_key | set_evidence_review_to_true_only_after_human_approval | human_must_provide_source_context | codex_may_fill |
| --- | --- | --- | --- |
| at_least_one_human_approved_pilot_session_completed | True | True | False |
| boundary_flags_reviewed | True | True | False |
| claim_scope_approved | True | True | False |
| customer_problem_fit_reviewed | True | True | False |
| customer_role_and_segment_recorded | True | True | False |
| customer_validation_record_approved_by_human | True | True | False |
| decision_usefulness_observed | True | True | False |
| deployment_decision_value_observed | True | True | False |
| failure_summary_usefulness_observed | True | True | False |
| feedback_form_completed | True | True | False |
| go_hold_pivot_decision_recorded | True | True | False |
| negative_feedback_recorded | True | True | False |
| no_customer_secrets_collected | True | True | False |
| no_customer_upload_required | True | True | False |
| no_private_core_disclosed | True | True | False |
| no_production_ready_claim_added | True | True | False |
| no_public_launch_claim_added | True | True | False |
| pain_point_fit_observed | True | True | False |
| permission_to_use_feedback_recorded | True | True | False |
| pilot_result_reviewed_by_human | True | True | False |
| pilot_result_template_completed | True | True | False |
| real_customer_or_target_user_feedback_recorded | True | True | False |
| recommendation_output_understood | True | True | False |
| reviewer_approved_validation_claim | True | True | False |
| success_criteria_applied | True | True | False |

## Session Text Fields

| field_name | human_must_provide | codex_may_fill |
| --- | --- | --- |
| session_id | True | False |
| session_date | True | False |
| participant_role | True | False |
| team_type | True | False |
| current_evaluation_method | True | False |

## Session Score Fields

| field_name | required_range | human_must_provide | codex_may_fill |
| --- | --- | --- | --- |
| understanding_score | 1-5 | True | False |
| trust_score | 1-5 | True | False |
| decision_influence_score | 1-5 | True | False |
| repeat_usage_intent_score | 1-5 | True | False |

## Boundary Flags

- `secrets_collected` must remain `false`
- `production_data_collected` must remain `false`
- `customer_data_uploaded` must remain `false`
- `private_core_disclosed` must remain `false`
- `production_ready_claim_made` must remain `false`

## Boundary

- builder_ready: false
- pilot_results_recorded: false
- customer_validation_approved: false
- customer_validation_claim_published: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- customer_contacted: false
- automated_customer_contact: false
- customer_data_collected: false
- customer_secrets_collected: false
- public_validation_claim_published: false
- testimonial_published: false
- case_study_published: false
