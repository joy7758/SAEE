# SAEE Minimum Session Answer Converter v0.1

Status: `hold_minimum_session_answers_missing`.

This local converter lets a human reviewer record the 12 minimum external
customer-validation questions in a simple text sheet and convert them into the
existing session-entry JSON shape.

It does not contact customers, infer missing feedback, close blockers, launch
SAEE, claim customer validation, or claim production readiness.

## Files

- Source questions: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md`
- Answer template: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.template.md`
- Human answer input: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.human_filled.md`
- Target session entry: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

## Current State

```yaml
external_customer_validation_minimum_session_answer_converter_v0_1: true
status: hold_minimum_session_answers_missing
human_answer_input_exists: false
session_entry_written: false
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_converter: 0
```

## Missing Fields

- `candidate_count`
- `decision_influence_score`
- `human_entry_confirmed`
- `human_reviewer_name`
- `human_source_context`
- `no_customer_data_uploaded`
- `no_private_core_disclosed`
- `no_production_data_collected`
- `no_production_ready_claim_made`
- `no_secrets_collected`
- `q01`
- `q02`
- `q03`
- `q04`
- `q05`
- `q06`
- `q07`
- `q08`
- `q09`
- `q10`
- `q11`
- `q12`
- `repeat_usage_intent_score`
- `session_date`
- `session_id`
- `time_to_value_minutes`
- `trust_score`
- `understanding_score`
- `willing_to_test_own_candidates`

## Invalid Fields

- None

## Human Use

After a real external customer or target-user session, fill:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answers.human_filled.md`

Then run:

```bash
python3 scripts/saee_external_customer_validation_minimum_session_answer_converter.py --apply
python3 scripts/saee_external_customer_validation_post_session_processor.py
```
