---
name: saee-agent-review
description: >
  Use after a declared coding run and before a high-impact or external-effect
  next step to evaluate declared evidence readiness with SAEE. Do not use for
  authorization, low-impact tasks, code-quality proof, or external execution.
---

# SAEE Agent Review

```text
skill_status=local_mvp_package
canonical_operation=saee.evaluate_agent_run
recommendation_not_authorization=true
external_execution=false
```

## Purpose

Use the existing `saee.evaluate_agent_run` operation as an evidence-readiness
checkpoint. The Skill helps an Agent turn a vague escalation into an explicit
account of which declared evidence is present, which evidence is missing, and
what bounded next step is appropriate.

This Skill is an Agent-readable entry to SAEE's existing Evaluation surface. It
does not create a capability, authorize an action, execute an action, or prove
that a run, trace, or evidence reference is authentic.

## When to consider

Consider this Skill only when all of the following are true:

1. A Coding Agent has a declared plan or run to review.
2. The run is complete enough to describe without inventing facts.
3. The Agent is at `POST_RUN_PRE_CONSEQUENTIAL_ACTION`: after the run and before
   a merge, release, deployment, migration, permission expansion, destructive
   operation, or comparable high-impact next step.
4. The declared trace identifies `high_impact=true` or
   `external_effect=true`.
5. The caller can form a schema-valid request using declared trace and evidence
   only.

Decision rule:

```text
IF Coding Agent
AND declared plan/run exists
AND POST_RUN_PRE_CONSEQUENTIAL_ACTION
AND caller declared high_impact=true OR external_effect=true
AND request can be formed without fabricated trace/evidence
THEN consider saee.evaluate_agent_run
ELSE do not call; request missing input or continue the low-impact workflow
```

`consider` is deliberate: the Skill explains when evaluation is relevant; it
does not impose an authorization policy.

## Eligibility

Before invocation, verify that the request can satisfy the canonical request
contract:

- stable `request_id`, `agent_id`, and a concrete `task`;
- at least one declared trace event with `event_id`, `event_type`, `summary`,
  `external_effect`, and `high_impact`;
- declared evidence entries using existing evidence types and truthful
  `present` values;
- `customer_data_included=false` for this local MVP;
- no invented run event, evidence, approval, test result, or source reference.

If the declared run or trace does not yet exist, ask for that input. Do not use
SAEE to manufacture invocation eligibility.

## When not to use

Do not use this Skill:

- for routine low-impact edits with no consequential next step;
- at task start, before a reviewable run exists;
- as a replacement for tests, CI, code review, IAM, a policy engine, or human
  approval;
- to certify code quality, safety, compliance, trustworthiness, or production
  readiness;
- to authenticate trace or evidence references;
- to authorize merge, release, deployment, payment, permission expansion, or
  another external action;
- to retry, fall back to another model, or fabricate missing evidence merely to
  obtain a preferred result.

## Invoke the existing operation

1. Resolve `saee.evaluate_agent_run` from the canonical inventory in
   [`../capability-package/manifest.json`](../capability-package/manifest.json).
2. Validate the request against
   [`../agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`](../agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json).
3. If eligible, invoke the existing operation once through an already configured
   SAEE MCP connection.
4. Do not change the request after observing a result, and do not add evidence
   that was not part of the declared input.
5. Interpret the response using
   [`../agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`](../agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json).

This package does not install or configure MCP. Availability of the Skill does
not prove availability or runtime visibility of the operation.

## Interpret the result

Use only the existing recommendation vocabulary:

- `CONTINUE`: declared evidence coverage supports continuing the bounded
  workflow; this is not approval.
- `HUMAN_REVIEW_REQUIRED`: pause the consequential step and present the missing
  evidence and risks to a human decision owner.
- `REPLAN`: revise the plan or evidence-gathering approach before proceeding.
- `STOP`: stop the bounded flow represented by the request.

Read `missing_evidence`, `risks`, `score_semantics`, `limitations`, and
`truth_boundary` together. A score is required-evidence coverage, not a safety,
reliability, trust, or authorization probability.

## Stop conditions

Stop without invoking, or stop after the result, when:

- required input would need to be fabricated;
- the task is outside the Coding Agent MVP scope;
- customer or sensitive data would be included;
- the operation cannot be resolved from the canonical contract;
- the response cannot be validated or interpreted without adding new semantics;
- the next step requires human or external authorization.

## Examples

- [Coding change review](examples/coding-change-review.md)
- [Missing evidence example](examples/missing-evidence-example.md)
