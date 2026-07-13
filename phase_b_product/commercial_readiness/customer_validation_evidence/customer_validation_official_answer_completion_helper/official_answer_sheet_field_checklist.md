# Official Customer Validation Answer Sheet Field Checklist

Use this checklist only after a real external customer or target-user session.
Codex must not invent or prefill customer answers.

- Target answer sheet: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md`
- Source template: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.template.md`
- Staged draft available: `false`

## Session and customer fields

- [ ] `Use `key`
- [ ] `session_id`
- [ ] `session_date`
- [ ] `human_reviewer_name`
- [ ] `participant_role`
- [ ] `team_type`
- [ ] `current_evaluation_method`
- [ ] `candidate_count`
- [ ] `understanding_score`
- [ ] `trust_score`
- [ ] `decision_influence_score`
- [ ] `repeat_usage_intent_score`
- [ ] `time_to_value_minutes`
- [ ] `willing_to_test_own_candidates`
- [ ] `top_objection`
- [ ] `evidence_missing`
- [ ] `notes`
- [ ] `human_source_context`
- [ ] `human_entry_confirmed`

## Boundary confirmations

- [ ] `no_secrets_collected`
- [ ] `no_production_data_collected`
- [ ] `no_customer_data_uploaded`
- [ ] `no_private_core_disclosed`
- [ ] `no_production_ready_claim_made`

## Evidence review confirmations

- [ ] `at_least_one_human_approved_pilot_session_completed`
- [ ] `boundary_flags_reviewed`
- [ ] `claim_scope_approved`
- [ ] `customer_problem_fit_reviewed`
- [ ] `customer_role_and_segment_recorded`
- [ ] `customer_validation_record_approved_by_human`
- [ ] `decision_usefulness_observed`
- [ ] `deployment_decision_value_observed`
- [ ] `failure_summary_usefulness_observed`
- [ ] `feedback_form_completed`
- [ ] `go_hold_pivot_decision_recorded`
- [ ] `negative_feedback_recorded`
- [ ] `no_customer_secrets_collected`
- [ ] `no_customer_upload_required`
- [ ] `no_private_core_disclosed`
- [ ] `no_production_ready_claim_added`
- [ ] `no_public_launch_claim_added`
- [ ] `pain_point_fit_observed`
- [ ] `permission_to_use_feedback_recorded`
- [ ] `pilot_result_reviewed_by_human`
- [ ] `pilot_result_template_completed`
- [ ] `real_customer_or_target_user_feedback_recorded`
- [ ] `recommendation_output_understood`
- [ ] `reviewer_approved_validation_claim`
- [ ] `success_criteria_applied`

## Required Next Command After Human Completion

```bash
python3 scripts/saee_customer_validation_answer_intake_helper.py --apply
python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply
python3 scripts/mainline_guard.py
make check
```
