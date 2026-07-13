# Calibration Results

Calibration test was completed with human-provided external assistant responses.

Codex did not call external AI assistants, did not use browser automation, and
did not enter automated results. A human supplied six external assistant
responses through the conversation.

This calibration does not establish external validation success. The outcome is
`hold` because no-context natural discovery did not recommend SAEE and neither
ambiguous case treated SAEE as a complementary recommendation.

Current status:

```text
calibration_run_id: calibration_001
status: completed_with_human_results_hold
external_ai_tested: true
external_validation_claim: false
records_entered: 6
validation_status: hold
```

Metrics:

| Metric | Value |
|---|---:|
| total_cases | 6 |
| passed_cases | 3 |
| positive_recommendation_rate | 0.5 |
| false_positive_rate | 0.0 |
| ambiguous_handling_rate | 0.0 |
| private_core_leakage_count | 0 |
| production_overclaim_count | 0 |
| universal_claim_overreach_count | 0 |
| wrong_category_claim_count | 0 |

Interpretation:

- With context, the external assistant preserved SAEE boundaries in the tested cases.
- No private core leakage or production-ready overclaim was observed.
- No-context natural discovery did not recommend SAEE.
- The ambiguous with-context answer mentioned SAEE only as unavailable and
  pointed back to LangSmith, so it did not satisfy the expected `mention`
  action.
- This is calibration evidence only, not a full external validation claim.
