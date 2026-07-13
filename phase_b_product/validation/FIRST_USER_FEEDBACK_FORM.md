# SAEE First User Feedback Form

## Participant Context

```text
role:
team_type:
current_agent_or_workflow_count:
current_evaluation_method:
deployment_decision_owner: yes/no
```

## Understanding

1. In your own words, what does SAEE help you decide?
2. Is the difference between single-run performance and long-horizon stability
   clear?
3. Which output is easiest to understand?
   - recommended agent
   - confidence score
   - ranking
   - failure summary
   - stability language

Score:

```text
understanding_score: 1-5
```

## Trust

1. Would you trust this output enough to discuss it in a deployment review?
2. What extra evidence would you need before acting on the recommendation?
3. Which part feels least credible?

Score:

```text
trust_score: 1-5
```

## Decision Influence

1. If these were your agents, would SAEE affect deploy / hold / retest
   decisions?
2. Would you compare multiple real agent/workflow versions this way before
   launch?
3. What decision would you want SAEE to help with first?

Score:

```text
decision_influence_score: 1-5
```

## Data Willingness

1. Would you provide sanitized agent/workflow descriptions for a test?
2. What inputs can you share safely?
   - agent config summary
   - prompt summary
   - workflow diagram
   - policy file
   - synthetic trace
   - none
3. What would block you from using this on real candidates?

Score:

```text
repeat_usage_intent_score: 1-5
```

## Commercial Signal

1. Who would own this tool internally?
2. What budget category would it fit?
   - LLMOps
   - QA / evaluation
   - AI platform
   - risk / governance
   - engineering productivity
3. Would this be more useful as:
   - local tool
   - hosted dashboard
   - API
   - private deployment

## Final Call

```text
would_use_again: yes/no/maybe
would_pay: yes/no/maybe
most_valuable_output:
biggest_missing_piece:
verbatim_quote:
```

## Boundary

Do not collect secrets, source code, credentials, production data, customer data,
or private workflow internals during first-user testing.

```yaml
customer_validated: false
product_launched: false
production_deployed: false
public_sdk_release: false
user_upload_enabled: false
private_core_exported: false
implementation_disclosed: false
```
