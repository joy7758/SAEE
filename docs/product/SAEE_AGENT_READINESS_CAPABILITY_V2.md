# SAEE Agent Readiness Capability

中文冻结名：`SAEE 智能体就绪评估能力`。

SAEE is an Agent Readiness Infrastructure that evaluates whether AI agents
have sufficient execution evidence before real-world deployment.

The external capability surface has exactly two read-only operations:

1. `saee.evaluate_agent_run` evaluates one declared Agent run and its required
   execution-evidence coverage.
2. `saee.evaluate_evidence` evaluates whether a declared evidence bundle
   covers an explicit readiness evidence set.

`rehearse_agent`, `describe_saee`, and `compare_observed_traces` remain internal
engineering surfaces. They are not public capability operations.

## Agent-native decision

Use this capability when an Agent is preparing a consequential action and the
workflow needs missing-evidence context before a separately authorized
decision. Do not use it for simple lookup or rewriting, runtime permission
enforcement, security/compliance certification, or deployment approval.

## Composition flow

```text
Agent Platform
  -> SAEE Agent Readiness Capability
  -> Evidence Evaluation
  -> Readiness Decision
  -> Continue / Review / Replan context
  -> independently authorized Allow / Review / Block decision
```

SAEE does not execute the external world. A readiness result is not an
authorization decision, a reliability probability, a certification, or proof
that the supplied trace is authentic.

## Project identity boundary

The engineering core remains the Digital Biosphere Evolution Engine. This
document is an external capability projection that strengthens Trait
Extraction and Pareto Fitness Evaluation; it does not reframe SAEE as an audit
SDK or generic multi-agent framework.
