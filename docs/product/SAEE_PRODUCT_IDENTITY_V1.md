# SAEE Product Identity v1.0

## Frozen external brand for Baidu ecosystem entry

```text
SAEE Agent Readiness Platform
SAEE 智能体上线准备平台
```

The first buyable product shape is:

```text
SAEE Agent Readiness Assessment
SAEE 智能体上线可靠性评估服务
```

One sentence:

> SAEE evaluates whether an AI Agent has sufficient execution evidence before
> real-world deployment.

> SAEE 用于评估 AI Agent 在真实部署前是否具备充分执行证据。

## Public capability contract

The Baidu-facing product surface exposes exactly two read-only operations:

1. `saee.evaluate_agent_run`
2. `saee.evaluate_evidence`

`rehearse_agent`, `describe_saee`, and `compare_observed_traces` are internal
engineering, experiment, or debugging surfaces. They are not Baidu product
entry points and must not appear in the Cloud Entry Package tool list.

## Product boundary

The service returns evidence coverage, missing evidence, observed risk signals,
and a bounded recommendation. A score is evidence-coverage percentage, not a
probability that an Agent is reliable or safe.

The service does not authorize deployment, change permissions, execute an
Agent, certify security/compliance, or replace Qianfan identity, policy,
observability, sandbox, or execution systems.

## Engineering identity

The canonical engineering core remains `Digital Biosphere Evolution Engine`.
Agent Readiness is its external product projection. Evidence analysis remains
an immune/evidence subsystem; `audit_first_reframe=false`.

Machine contract:
`agent-interface/product/saee-agent-readiness-platform.v0.1.json`.
