# Example: Coding Change Review

This synthetic example shows when an Agent should consider SAEE Agent Review.
It does not authorize an actual merge, release, deployment, or external action.

## Scenario

A Coding Agent has completed a declared local change to a payment module. The
declared test step passed, the permission boundary is known, and a human approval
context is present. The Agent is now preparing for a merge-like consequential
step, but no rollback plan has been declared.

```text
workflow_point=POST_RUN_PRE_CONSEQUENTIAL_ACTION
high_impact=true
external_effect=false
declared_run_exists=true
declared_trace_exists=true
```

Declared evidence:

```text
TEST_RESULT=present
ROLLBACK_PLAN=missing
PERMISSION_BOUNDARY=present
HUMAN_APPROVAL=present
```

## Trigger and eligibility check

The Agent checks, in order:

1. Is there a completed, declared coding run? `yes`
2. Is the next step consequential? `yes`
3. Is high impact or external effect declared? `yes`
4. Can a request be formed from the declared trace and evidence without adding
   facts? `yes`

The Skill is eligible for consideration. Eligibility does not force an
invocation and does not authorize the next step.

## Bounded workflow

1. Preserve the declared input facts.
2. Validate the request against the existing request schema.
3. Invoke the existing `saee.evaluate_agent_run` operation once if it is
   available through the already configured SAEE MCP surface.
4. Interpret only the existing response fields and recommendation vocabulary.
5. If the result identifies `ROLLBACK_PLAN` as missing and returns
   `HUMAN_REVIEW_REQUIRED`, pause the consequential step and request a concrete
   rollback plan from the responsible human or workflow owner.
6. Do not treat the recommendation as approval or as proof that the other
   evidence is authentic.

The schema-valid request and faithful local Alpha response are shown in
[`missing-evidence-example.md`](missing-evidence-example.md).

## What this adds

Without the checkpoint, an Agent may say only “human confirmation is needed.”
The existing evaluator can make the declared gap actionable by identifying the
missing evidence type and associated risk. It still leaves the consequential
decision with the responsible Agent policy and human authority owner.

## Low-impact negative control

For a routine documentation correction with no consequential next step:

```text
high_impact=false
external_effect=false
POST_RUN_PRE_CONSEQUENTIAL_ACTION=false
```

Do not call SAEE merely because the Skill exists. Continue the ordinary
low-impact workflow, subject to the Agent's normal instructions.
