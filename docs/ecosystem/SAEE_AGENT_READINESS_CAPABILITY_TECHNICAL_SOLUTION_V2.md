# SAEE Agent Readiness Capability - Technical Solution v2.0

## Page 1 - Agent risk problem

Agent platforms can complete code or business tasks, but completion does not
prove that the evidence required for a consequential action exists. Missing
rollback, permission, testing, or approval evidence creates an execution gap.

## Page 2 - Current solution gap

Observability explains what happened. Policy and authorization determine what
is permitted. Sandboxes constrain execution. SAEE fills a separate gap: before
an independently authorized decision, it evaluates whether the declared trace
and evidence cover a bounded readiness profile.

## Page 3 - SAEE position

Frozen name: `SAEE Agent Readiness Capability / SAEE 智能体就绪评估能力`.
SAEE is not an Agent platform, audit SDK, governance tool, or external-world
executor. It is a callable capability projection from the Digital Biosphere
Evolution Engine.

## Page 4 - Architecture

```text
Agent Platform -> MCP/HTTP Adapter -> Two-tool SAEE Runtime
  -> Evidence Coverage Evaluation -> Bounded Readiness Receipt
  -> Independently Authorized Decision
```

The adapter never expands permissions, executes supplied code, installs
dependencies, contacts external services, or treats evidence references as
authenticated facts.

## Page 5 - Stable operations

`saee.evaluate_agent_run` accepts one declared Agent trace plus an evidence
list. `saee.evaluate_evidence` accepts one evidence bundle plus required types.
Both return missing evidence, bounded reason/risk fields, explicit score
semantics, and non-authorization truth boundaries.

## Page 6 - Qoder coding-release demo

A coding Agent changes a synthetic fixture and runs tests. Before deployment it
calls SAEE. Tests and permission boundary are present; rollback plan and human
approval are missing. SAEE returns `readiness=replan`, `score=50`, and
`recommendation=REPLAN`. No deployment occurs.

## Page 7 - Integration branches

Qoder and Claude Code use project-scoped `.mcp.json`. LangChain uses
`MultiServerMCPClient`. CrewAI uses MCP server parameters. Qianfan uses the
existing bounded adapter and provider receipts. Every branch points to the same
two-tool runtime; templates do not establish official interoperability.

## Page 8 - Safety and truth boundaries

SAEE accepts no customer data in this Alpha, performs no external-world action,
does not verify trace authenticity, and cannot authorize deployment. Platform
compatibility is reported separately from a platform process test, official
integration, marketplace listing, adoption, customer validation, and production
readiness.

## Page 9 - 180-day route

Days 0-30 freeze identity, contracts, card, repository discovery, and tests.
Days 30-90 validate Qoder first, retain Qianfan, and prepare framework branches.
Days 90-150 collect consented technical conversations, ecosystem presentation,
and external developer tests. Days 150-180 pursue an approved plugin or
marketplace route only after support and authorization gates pass.

## Page 10 - KPI and next decisions

Technical target: MCP, Qoder adapter, Qianfan adapter, stable OpenAPI.
Ecosystem target: two technical conversations, one ecosystem presentation,
three consented external developer tests. Commercial target: one Design Partner
and one joint-solution draft. Local preparation is not external KPI completion.
