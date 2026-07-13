# SAEE Minimum Session Filling Guide

Use `minimum_session_form.html` to generate JSON locally, or fill
`minimum_session_human_filled_template.local.json` from the 12-question session.

## Field Mapping

- Q1 -> `session.participant_role`
- Q2 -> `session.team_type`
- Q3 -> `session.current_evaluation_method`
- Q4 -> `session.candidate_count`
- Q5 -> `session.understanding_score`
- Q6 -> `session.trust_score`
- Q7 -> `session.decision_influence_score`
- Q8 -> `session.repeat_usage_intent_score`
- Q9 -> `session.time_to_value_minutes`
- Q10, Q11, Q12 -> `session.notes`, `session.top_objection`, and
  `session.evidence_missing`

Set `human_entry_confirmed=true` only after the answers come from a real
external customer or target user. Set all `boundary_confirmation` values to
true only if the boundary was actually followed.

Copy the filled JSON to:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

Do not change `customer_validated`, `production_ready`, `product_launched`,
`private_core_exposed`, `public_validation_claim_published`, `testimonial_published`,
or `case_study_published`; they must remain false in this entry.
