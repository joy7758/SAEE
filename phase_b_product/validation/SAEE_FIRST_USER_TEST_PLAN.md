# SAEE First User Test Plan

## Objective

Validate whether SAEE's output is decision-useful for teams deciding which AI
agent, workflow, or policy should be deployed.

This test does not validate production readiness. It validates value.

```text
Goal = Validate decision usefulness of SAEE output
```

## Product State Under Test

```text
SAEE = Interactive AI Decision System
Stage = Local MVP Complete
Commercial State = First Demo Ready
Production State = Not production-ready yet
```

## Core Hypothesis

```text
Teams shipping AI agents will find long-horizon stability, ranking, and failure
summary more useful than single-run success metrics when choosing what to
deploy.
```

## Target Users

Primary targets:

- AI agent framework teams.
- LLM application teams.
- Workflow automation teams.
- Enterprise AI platform / LLMOps teams.

Screening criteria:

- The team has at least two candidate agents, workflows, prompts, or policies.
- They currently compare candidates using single-run tests, manual review, or
  prompt-eval style metrics.
- They make deployment, rollback, or promotion decisions.

## Session Format

Recommended session length:

```text
30 minutes
```

Session flow:

1. Ask how the team currently decides which agent/workflow goes live.
2. Show the problem statement: "single-run performance does not prove
   long-term stability."
3. Open the local landing page.
4. Click `Run Demo Battle`.
5. Walk through recommendation, confidence, ranking, and failure summary.
6. Ask the user to map their real candidate systems to Agent A/B/C.
7. Ask whether this output would change a deployment decision.
8. Collect feedback through `FIRST_USER_FEEDBACK_FORM.md`.

## Demo Script

Opening:

```text
SAEE tests which AI agent survives long-term competition before you deploy it.
```

User problem prompt:

```text
When you have several agent versions or workflow strategies, how do you decide
which one should be deployed?
```

Demo action:

```text
Click Run Demo Battle.
```

Result narration:

```text
SAEE returns a recommended agent, confidence score, ranking, and failure-mode
summary. The goal is not to debug one trace; the goal is to decide which system
is safer to deploy after repeated competitive stress.
```

Decision question:

```text
If these were your agents, would this recommendation influence which one you
deploy, hold, or retest?
```

## Metrics

Primary metrics:

```text
understanding_rate
trust_rate
decision_influence_rate
repeat_usage_intent
```

Definitions:

```text
understanding_rate =
  users who can restate SAEE's value in their own words / total users

trust_rate =
  users rating the output as credible enough to discuss internally / total users

decision_influence_rate =
  users saying the output could affect deploy / hold / retest decisions / total users

repeat_usage_intent =
  users willing to test their own agent/workflow candidates / total users
```

Secondary metrics:

```text
time_to_value_minutes
most_confusing_output
minimum_required_input
willingness_to_pay_signal
```

## Data To Record

For each session, record:

- user role;
- team type;
- current evaluation method;
- number of candidate agents/workflows;
- whether the value was understood;
- whether the recommendation was trusted;
- whether it could affect a deployment decision;
- what evidence was missing;
- whether the user would run this with real candidates.

Do not record secrets, production credentials, source code, model keys, private
customer data, or proprietary workflow internals.

## Valid Test Inputs

Allowed:

- user descriptions of candidate agents;
- high-level workflow diagrams;
- anonymized prompt/policy summaries;
- synthetic or sanitized examples;
- local demo request already present in `phase_b_product/landing/app.js`.

Forbidden:

- production API keys;
- private model credentials;
- private repositories;
- customer data uploads;
- external code execution;
- untrusted install scripts;
- private SAEE core disclosure.

## Output

After 5 to 10 sessions, produce:

```text
understanding_rate
trust_rate
decision_influence_rate
repeat_usage_intent
top objections
minimum viable next change
go / hold / pivot recommendation
```

## Boundary

```yaml
first_user_test_plan_created: true
customer_validated: false
customer_contacted: false
production_deployed: false
product_launched: false
public_sdk_release: false
user_upload_enabled: false
new_runtime_behavior_added: false
api_contract_modified: false
landing_page_modified: false
decision_engine_modified: false
private_core_exported: false
implementation_disclosed: false
```
