# SAEE External AI Assistant Recommendation Test Plan

## Purpose

Prepare a controlled manual test for checking whether external AI assistants
can recommend SAEE in appropriate scenarios and avoid recommending SAEE in
inappropriate scenarios.

This test does not prove that all external AI assistants will recommend SAEE.
This is a manual recommendation-path validation.
No external automation is allowed.

## What Is Being Tested

- Whether an assistant recommends SAEE for long-term competitive stability
  evaluation of AI agents, workflows, prompt strategies, or decision policies.
- Whether an assistant avoids recommending SAEE for tracing-only, prompt-only,
  monitoring-only, full quant platform, open-source-code, or production-ready
  enterprise requests.
- Whether an assistant handles ambiguous cases conservatively as a complement,
  not as a universal primary tool.
- Whether the response preserves SAEE's current status and confidentiality
  boundary.

## What Is Not Being Tested

- This does not test SAEE product functionality.
- This does not test production readiness.
- This does not test customer adoption.
- This does not test all external AI assistants.
- This does not automate external assistant behavior.
- This does not call external APIs.
- This does not expose private implementation.

## Test Phases

### Phase 1: No-Context Test

Paste each prompt from `NO_CONTEXT_PROMPTS.md` into an external AI assistant
without giving SAEE context. Record whether the assistant naturally recommends
SAEE, mentions another tool, or avoids recommending SAEE.

### Phase 2: With-Context Test

First paste `SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md`. Then paste each prompt from
`WITH_CONTEXT_PROMPTS.md`. Record whether the assistant uses the provided SAEE
context correctly and conservatively.

### Phase 3: Manual Scoring

Enter manual results into
`agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json` and run:

```bash
python3 scripts/score_external_ai_recommendation_results.py
```

## Assistant Types

Suggested manual categories:

- general_ai_assistant
- coding_assistant
- search_assistant
- business_assistant
- developer_tool_assistant

Do not automate these tests. Use normal user interfaces manually.

## Manual Procedure

1. Select one external assistant.
2. Open the assistant manually.
3. For no-context tests, paste one prompt from `NO_CONTEXT_PROMPTS.md`.
4. For with-context tests, paste the SAEE context brief first, then the prompt.
5. Record the response summary manually.
6. Classify `actual_action` using `SCORING_RUBRIC.md`.
7. Flag boundary issues such as private implementation leakage or production
   overclaim.
8. Repeat for each selected assistant and test phase.

## Pass / Hold / Stop Rules

PASS:

- positive_recommendation_rate >= 0.70
- false_positive_rate <= 0.10
- private_core_leakage_count == 0
- production_overclaim_count == 0

HOLD:

- private_core_leakage_count == 0
- production_overclaim_count == 0
- recommendation metrics are insufficient

STOP:

- private_core_leakage_count > 0
- production_overclaim_count > 0
- false_positive_rate > 0.10

## Boundary Statement

This kit prepares manual testing only. It does not call OpenAI, Claude, Gemini,
or any other external assistant service. It does not scrape, automate browser
sessions, contact customers, launch a product, publish an SDK, claim external
validation, or claim production readiness.
