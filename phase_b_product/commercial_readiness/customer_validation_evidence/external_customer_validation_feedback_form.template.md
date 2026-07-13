# SAEE External Customer Validation Feedback Form Template

Do not record secrets, source code, credentials, production data, customer data,
or private workflow internals.

```text
session_id:
session_date:
participant_role:
team_type:
current_evaluation_method:
candidate_count:
saee_demo_surface_used:

understanding_score: 1-5
trust_score: 1-5
decision_influence_score: 1-5
repeat_usage_intent_score: 1-5
time_to_value_minutes:

top_objection:
evidence_missing:
willing_to_test_own_candidates: true/false
notes:
```

Boundary flags must remain false:

```yaml
secrets_collected: false
production_data_collected: false
customer_data_uploaded: false
private_core_disclosed: false
production_ready_claim_made: false
```

After human review, transfer the answers into:

`phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json`
