# SAEE External AI Assistant Recommendation Test Kit

This folder is for manual external AI assistant recommendation testing.

It is not automated.
It does not call external APIs.
It does not contact customers.
It does not launch a product.
It does not claim production readiness.
It does not expose private core.

## Files

- `EXTERNAL_AI_TEST_PLAN.md`: manual test plan.
- `NO_CONTEXT_PROMPTS.md`: prompts to paste without SAEE context.
- `WITH_CONTEXT_PROMPTS.md`: prompts to paste after the context brief.
- `SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md`: short context brief for assistants.
- `MANUAL_RESULT_TEMPLATE.json`: JSON template for manual result entry.
- `MANUAL_RESULT_TEMPLATE.csv`: CSV template for manual result entry.
- `SCORING_RUBRIC.md`: manual scoring rubric.
- `EXTERNAL_VALIDATION_RESULTS.json`: pending machine-readable result file.
- `EXTERNAL_VALIDATION_RESULTS.md`: pending human-readable result file.

## Current State

```text
external_ai_tested: false
manual_test_prepared: true
product_launched: false
customer_contacted: false
private_core_exposed: false
production_ready_claim: false
```

## Next Step

Manually run no-context and with-context tests against external AI assistants.
Record results manually. Do not automate the test.
