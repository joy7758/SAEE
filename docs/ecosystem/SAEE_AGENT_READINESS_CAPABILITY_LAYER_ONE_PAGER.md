# SAEE: Agent Readiness Capability Layer

> SAEE evaluates whether an autonomous agent has sufficient execution evidence
> before real-world actions.

## The missing layer

Agent platforms can plan, write code, call tools, and prepare consequential
actions. Task completion alone does not show that rollback, permission, test,
or approval evidence exists. SAEE supplies that missing pre-action context.

```text
Qoder / Qianfan / Claude Code / LangChain / CrewAI
  -> SAEE Agent Readiness Capability
  -> evaluate declared trace and evidence coverage
  -> CONTINUE / HUMAN_REVIEW_REQUIRED / REPLAN / STOP context
  -> independently authorized real-world decision
```

## Stable surface

- `saee.evaluate_agent_run`: evaluate one declared Agent run.
- `saee.evaluate_evidence`: evaluate one declared evidence bundle.
- Protocol projections: MCP stdio and an HTTP contract.
- Score meaning: required-evidence coverage, not reliability probability.

## Why an Agent would choose it

Use SAEE before a high-impact or external action when the workflow needs an
explicit missing-evidence list. Do not use it as a runtime blocker, permission
engine, certification service, legal conclusion, or deployment authority.

## Current evidence and limits

Local MCP discovery and invocation pass for exactly two tools. A Qoder-format
project configuration and coding-release demo pass a platform-compatible local
JSON-RPC test. Qianfan bounded synthetic provider receipts pass. No Qoder
process, official Qoder Plugin, official cloud integration, customer validation,
marketplace listing, or production deployment is established.
