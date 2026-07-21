# SAEE Mainline Guardian

This is a short-term routing reminder. It does not amend the Constitution,
capability inventory, Project Memory, or product status.

## Authority Boundary

The constitutional program mainline remains the controlled integration of SAEE
and the Agent Evidence Project, followed by the target customer-version family:
`SAEE Evidence / SAEE Evaluation / SAEE Governance`.

This rule cannot replace that authority. In this file, "current mainline" means
the current business-validation execution priority only.

## Current Business Objective

The first business objective is to validate whether a real Agent discovers,
understands, and invokes SAEE, and whether that use produces observable user
value.

```text
CURRENT_BUSINESS_OBJECTIVE=FIRST_REAL_AGENT_USES_SAEE
```

## Current Mainline

Current business-validation execution priority:

```text
REQUESTED_PHASE_LABEL=Phase 7.0
CURRENT_BUSINESS_VALIDATION_MAINLINE=SAEE Agent Review Skill MVP
PHASE_LABEL_CANONICAL=false
PHASE_LABEL_NOTE=Phase 7.0 already exists historically for an internal reliability benchmark
```

The phase label is therefore a human routing label, not a new canonical phase,
capability, product, implementation, launch, or customer-validation claim.

## Governance Track

`H0-R / Baseline Reconstruction / Immutable Evidence / Preimage P / Enterprise
Governance` belongs to long-term infrastructure validation.

```text
GOVERNANCE_TRACK_STATUS=VALIDATED_PROTOTYPE_PAUSED
GOVERNANCE_TRACK_IS_CURRENT_BUSINESS_MAINLINE=false
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

Governance evidence may support the constitutional mainline, but it must not
displace business validation or authorize its own continuation.

## Drift Detection Rules

Before every SAEE task, evaluate its direct effect. If it mainly adds a
governance, authorization, protocol, or documentation layer without increasing
Agent adoption, Agent invocation, or user value, output:

```text
MAINLINE_DRIFT_RISK=true
```

If a task elevates a commercial, Demo, governance, testing, or audit lane above
the constitutional integration mainline, output `MAINLINE_DRIFT_DETECTED` and
recommend correction.

If a task creates a new Capability, Protocol, governance layer, or authorization
flow, require explicit human confirmation of commercial necessity before
development. Validation, recommendation, or evidence does not grant execution
authority.

## Decision Questions

Answer before execution:

1. Does this help the first real Agent use SAEE?
2. Does it produce observable user value?
3. Can a smaller experiment validate the same assumption?

If Questions 1 or 2 are not clearly `yes`, lower the task's default priority.
If Question 3 is `yes`, prefer the smaller experiment.

## Priority

```text
Agent Usage
>
User Feedback
>
Demo
>
Commercial Validation
>
Governance Expansion
```

## Staged Truth

Agent discovery, local invocation, Demo pass, user feedback, commercial
validation, customer validation, and production readiness are separate states.
Never promote one state into another without current authoritative evidence.

## Rule Status

```text
MAINLINE_GUARD_CREATED=true
MAINLINE_DRIFT_PREVENTION_RULE=true
AUTO_ENFORCEMENT=false
CODE_CHANGED=false
CAPABILITY_CHANGED=false
MCP_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_MAINLINE_GUARD
```
