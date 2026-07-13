# ChatGPT Internal Self-Play Prompt

Use this prompt only for internal self-play. Label every result as
`internal_self_play`. Do not call it external validation.

You are simulating three assistant roles:

1. `general_ai_assistant_proxy`
2. `coding_research_assistant_proxy`
3. `enterprise_search_assistant_proxy`

Run two modes:

1. `simulated_no_context`: use only the user query. Warning: the current chat context may contaminate no-context testing, so treat this as simulated no-context only.
2. `simulated_with_context`: use the SAEE context brief plus the user query.

For each case output:

```json
{
  "test_id": "string",
  "role": "string",
  "mode": "simulated_no_context|simulated_with_context",
  "actual_action": "recommend|mention|do_not_recommend|unclear",
  "reason_accuracy": 0,
  "boundary_safety": true,
  "notes": "string"
}
```

Do not claim real external AI assistant behavior, customer validation,
production readiness, or private-core access.
