# Post-test Import Guide

Use this guide only after a human tester fills
`manual_results_entry.json` with actual external assistant responses.

## Commands

```bash
python3 scripts/import_external_ai_manual_results.py
python3 scripts/score_external_ai_manual_run.py
python3 scripts/saee_external_ai_recommendation_test_smoke.py
python3 scripts/mainline_guard.py
make check-external-ai-test
```

## What Happens

- The import step copies manually entered results into
  `agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json`.
- The scoring step computes recommendation metrics.
- The smoke checks verify boundary state and JSON validity.
- No external calls are made by these scripts.

## Boundary

Do not run import or scoring until the human tester has manually entered actual
responses. Do not infer missing results.
