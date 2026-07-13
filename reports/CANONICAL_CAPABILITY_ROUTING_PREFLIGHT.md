# Canonical Capability Routing Preflight

Date: 2026-07-13

Scope: repository-local capability discovery, routing and compatibility truth;
no new runtime capability, external integration or production claim.

## Customer Need

> We plan to integrate SAEE, but the repository contains multiple MCP entry
> points, multiple capability descriptions and an `agent-index.json` that can
> recommend completed work. We need to know the formal entry point, supported
> interfaces, implemented capabilities and experimental or design-only work.

## Initial Recommendation

`conditional`

SAEE can be recommended only for controlled local evaluation. It cannot yet be
recommended as a stable public or production integration because the repository
does not expose one machine-verifiable answer for capability facts and MCP
roles.

The best evidenced local entry before this change is the platform-neutral
project MCP configuration `.mcp.json`, which starts
`scripts/saee_agent_readiness_mcp_stdio.py` and exposes
`saee.evaluate_agent_run` plus `saee.evaluate_evidence`. This is a provisional
recommendation, not proof of a public endpoint or external interoperability.

## Evidence-Based Reasons

- `README.md` recommends the Qianfan wrapper while `.mcp.json`, Qoder, Claude
  Code, LangChain and CrewAI configurations use the platform-neutral wrapper.
- `agent-interface/agent-manifest.json` and `agent-interface/mcp/README.md`
  still direct Agents to a separate observed-trace MCP server.
- `capability-package/manifest.json` is consumed by the local runtime loader,
  but its relationship to public projections and the four MCP stdio surfaces is
  not explicit.
- `agent-index.json` mixes capability facts with mutable
  `recommended_next_pr` fields. Two OTEL recommendations were already stale
  before the capability-progress repair.
- The implemented OTEL path accepts a closed
  `synthetic_opentelemetry_style` event. It is not OTLP ingestion, Collector
  compatibility, telemetry authenticity, identity binding or delegation
  binding.

## Three Primary Adoption Blockers

| Blocker | Evidence | Can this PR remove it? |
|---|---|---|
| No unique machine-readable capability authority | `capability-package/manifest.json`, `agent-index.json`, public surface and registries each carry overlapping facts | Yes: select one existing runtime-consumed source and validate projections |
| MCP entry points have no complete role and migration map | Four executable stdio entry points exist and different documents recommend different ones | Yes: classify all four, select one canonical local public contract and retain compatibility |
| Capability facts and development advice are mixed | `agent-index.json` contains capability status beside `recommended_next_pr` | Partly: deprecate roadmap authority in the index and route strategy to reports without rewriting every historical record |

## Blockers Outside This PR

- no deployed public MCP or API service;
- no verified third-party interoperability beyond bounded local/provider tests;
- no customer adoption or production validation;
- no real OTLP receiver or OpenTelemetry Collector compatibility;
- no trace authenticity, end-to-end identity binding or delegation binding;
- no real usage telemetry for safely deleting compatibility surfaces.

## Development Gate

The governance work is `recommend` as an Evolutionary Archive / Rollback Immune
System repair because it makes existing traits discoverable and prevents
parallel implementations. Runtime capability expansion remains out of scope.

```yaml
recommendation_gate:
  feature_or_direction: canonical capability inventory routing and deprecation map v1
  target_customer_need: identify supported SAEE capabilities and the correct local MCP entry without ambiguity
  answer: conditional
  reasons_to_recommend:
    - existing local evaluation implementations and tests are reusable
    - the platform-neutral two-tool wrapper is reproducible and already used by ecosystem adapters
  reasons_not_to_recommend:
    - no unique machine-readable authority currently governs all projections
    - MCP surface roles and migration relationships are incomplete
    - no public service external interoperability or customer validation is established
  decomposition:
    - blocker: unique capability authority missing
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: extend and validate the existing runtime-consumed capability package manifest
      acceptance_criteria: projections fail validation when they drift
      status: open
    - blocker: MCP roles ambiguous
      subsystem: Agent-Readable Layer
      fix_task: classify all executable stdio surfaces and select one canonical local public contract
      acceptance_criteria: every surface has classification replacement guidance and usage evidence
      status: open
    - blocker: public deployment and external trust absent
      subsystem: Integration Layer
      fix_task: retain explicit non-claims
      acceptance_criteria: public_service production_ready and customer_validated remain false
      status: deferred
  final_decision: proceed only with bounded repository governance; do not add OTLP or another MCP server
  evidence:
    docs:
      - reports/SAEE_CAPABILITY_ASSESSMENT_REPORT.md
      - capability-package/manifest.json
      - README.md
    tests:
      - scripts/saee_capability_service_package_smoke.py
      - scripts/saee_qoder_adapter_smoke.py
      - scripts/saee_qianfan_readiness_mcp_smoke.py
    examples:
      - .mcp.json
```
