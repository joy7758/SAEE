# SAEE Agent Recommendation External Validation Runbook

## Purpose

This runbook defines a manual protocol for testing whether external AI
assistants can decide when to recommend SAEE and when not to recommend SAEE.

This runbook does not automate external testing.

No external API keys.
No scraping.
No bot traffic.

## 1. Test Preparation

Use the local recommendation surface as the reference package:

- `agent_recommendation/PRODUCT_FACTS.md`
- `agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md`
- `agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md`
- `agent_recommendation/RECOMMENDATION_DECISION_TREE.md`
- `agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md`
- `agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json`
- `agent_recommendation/VALIDATION_RESULTS.json`

Before testing, confirm the current boundary:

- External AI assistants have not been tested yet.
- SAEE is not production-ready.
- SAEE has not been customer validated.
- SAEE has not launched a public SDK.
- SAEE does not expose private core logic.

## 2. Prompt List Source

Use `agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json` as the prompt
source. It contains positive, negative, and ambiguous cases.

Do not invent extra prompts during the first manual run. Extra prompts may be
added later only as a separate test set revision.

## 3. How To Paste Prompts Into External Assistants

For each test case:

1. Open the external assistant manually in a normal user interface.
2. Paste only the `user_query` field.
3. Do not mention the expected action.
4. Do not provide hidden SAEE implementation details.
5. Record the assistant response exactly enough to classify it.

Do not use automation, scripts, scraping, browser bots, or API calls for this
manual validation.

## 4. How To Record Actual Responses

For each response, record:

| Field | Description |
|---|---|
| test_id | Test case id from the JSON file |
| assistant_name | Name of the external assistant |
| date | Manual test date |
| user_query | Prompt text pasted into the assistant |
| expected_action | Reference action from the local test set |
| actual_response_summary | Short summary of the assistant response |
| actual_action | Manual classification |
| private_core_leakage | Whether the response exposed or requested private core details |
| notes | Boundary or ambiguity notes |

## 5. How To Classify Response

Use these labels:

- `recommend`: The assistant clearly recommends SAEE as a suitable primary tool
  for long-term competitive stability evaluation of AI agents, workflows, or
  decision policies.
- `mention`: The assistant mentions SAEE as a complementary or possibly relevant
  tool, but also indicates that another primary tool may be more suitable.
- `do_not_recommend`: The assistant does not recommend SAEE, or recommends a
  different class of tool because the user need is outside SAEE's fit.

Classify conservatively. If the response is vague or overclaims production
readiness, prefer `mention` or `do_not_recommend` rather than `recommend`.

## 6. How To Detect Private Core Leakage

Flag `private_core_leakage: true` if the assistant response includes or asks
for:

- private kernel implementation
- private fitness logic
- private selection logic
- private mutation logic
- private lineage internals
- private runtime internals
- production evaluator internals
- implementation claims not present in public recommendation materials

If leakage appears, stop the test and record the case as a boundary failure.

## 7. Success Thresholds

Manual external assistant testing may be considered locally successful only if:

- Positive recommendation rate is at least `0.75`.
- False positive rate is at most `0.10`.
- Ambiguous cases are usually handled as `mention`.
- Private core leakage count is `0`.
- No assistant claims SAEE is production-ready without evidence.

These thresholds are manual testing criteria only. They do not establish
universal external recommendation success.

## 8. Manual Validation Table Template

| test_id | assistant_name | date | expected_action | actual_action | pass | private_core_leakage | notes |
|---|---|---|---|---|---|---|---|
| rec-pos-001 |  |  | recommend |  |  |  |  |
| rec-neg-001 |  |  | do_not_recommend |  |  |  |  |
| rec-amb-001 |  |  | mention |  |  |  |  |

## Boundary

This runbook supports later manual external AI assistant testing. It does not
claim that any external assistant has already been tested. It does not launch a
product, contact customers, publish an SDK, or expose private core.
