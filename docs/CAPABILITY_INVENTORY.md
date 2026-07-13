# SAEE Canonical Capability Inventory and Routing v1

## Authority

The sole machine-readable authority for current integrable capability facts is:

`capability-package/manifest.json#canonical_inventory`

This document, `agent-index.json`, public discovery metadata and MCP routing
descriptions are projections. They must pass
`python3 scripts/saee_canonical_capability_inventory_smoke.py`; they are not
independent truth sources.

Development recommendations are intentionally separate. Historical
`recommended_next_pr` fields in `agent-index.json` are deprecated compatibility
metadata. Strategy belongs in assessment or roadmap documents.

## Current Capability Facts

| Capability ID | Implementation | Lifecycle | Canonical local entry |
|---|---|---|---|
| `saee.evaluate_agent_run` | `implemented` | `active` | MCP tool through `scripts/saee_agent_readiness_mcp_stdio.py` |
| `saee.evaluate_evidence` | `implemented` | `active` | MCP tool through `scripts/saee_agent_readiness_mcp_stdio.py` |
| `saee.rehearse_agent` | `design_only` | `experimental` | None; internal contract-only exposure is not a public implementation |
| `saee.otel_style_candidate_mapping` | `implemented` | `experimental` | `saee-agent evaluate-trace-candidate` |
| `saee.general_trace_normalization` | `partial` | `experimental` | bounded `saee-agent evaluate-traces` input only |
| `saee.otel_sdk_or_otlp_ingestion` | `missing` | `experimental` | None |
| `saee.trusted_trace_to_evidence_conversion` | `missing` | `experimental` | None |
| `saee.external_identity_binding` | `missing` | `experimental` | None |
| `saee.delegation_binding` | `missing` | `experimental` | None |

The canonical JSON records contain implementation paths, executable entries,
test evidence, documentation, aliases, claims, non-claims and lifecycle data.
An `implemented` label is rejected when implementation, entry point or test
evidence is absent.

## Canonical MCP Entry

New local external-Agent integrations should use the project configuration:

```text
.mcp.json
  -> python3 scripts/saee_agent_readiness_mcp_stdio.py
  -> saee.evaluate_agent_run
  -> saee.evaluate_evidence
```

This is the canonical local public-contract entry. It is not a deployed public
MCP endpoint and does not establish external interoperability, customer
validation or production readiness.

## MCP Surface Classification

| Surface | Tools | Classification | Relationship and migration |
|---|---|---|---|
| `scripts/saee_agent_readiness_mcp_stdio.py` | `saee.evaluate_agent_run`, `saee.evaluate_evidence` | `canonical_public` | Default platform-neutral local entry for new integrations |
| `scripts/saee_qianfan_readiness_mcp_stdio.py` | same two namespaced tools | `compatibility` | Qianfan wrapper sharing the same adapter; platform-neutral callers migrate to the canonical entry |
| `scripts/saee_capability_mcp_stdio.py` | `evaluate_agent_run`, `evaluate_evidence`, `rehearse_agent` | `internal` | Capability Package adapter; external callers use the namespaced canonical entry |
| `scripts/saee_mcp_stdio.py` | `describe_saee`, `compare_observed_traces` | `internal` | Legacy observed-trace/descriptor surface; no truthful one-to-one public replacement is claimed |

No surface is physically deleted or marked retired in v1. Real usage evidence
is unavailable, so every `usage_evidence` field is `UNKNOWN`. Removal requires
caller identification, verified replacement coverage and a separate review.

## OpenTelemetry Boundary

Current `synthetic_opentelemetry_style` support does not equal real OTLP
ingestion, OpenTelemetry Collector compatibility, telemetry authenticity or
end-to-end identity and delegation binding.

The implemented mapper accepts one closed synthetic, allowlisted event shape,
extracts non-authoritative candidate fields and routes them to local Evidence
Adequacy evaluation. It does not import the OpenTelemetry SDK, receive OTLP,
normalize a full span graph, authenticate telemetry or make a trace become
evidence.

## Claims

- Two bounded readiness operations are locally executable through the canonical
  platform-neutral MCP stdio wrapper.
- Closed evidence and synthetic candidate inputs can be evaluated
  deterministically against repository-controlled contracts.
- Capability and MCP routes are machine-resolvable without fuzzy matching or a
  language model.

## Non-Claims

- No public MCP endpoint or public API is deployed.
- No third-party MCP interoperability, customer adoption or production
  readiness is established.
- No result authorizes deployment, permission expansion or external action.
- No trace authenticity, signed delegation, remote attestation, OTLP ingestion
  or Collector compatibility exists.

## Deterministic Agent Commands

```bash
python3 scripts/saee_agent_cli.py capability-list
python3 scripts/saee_agent_cli.py capability-show saee.evaluate_evidence
python3 scripts/saee_agent_cli.py capability-show synthetic_opentelemetry_style
python3 scripts/saee_agent_cli.py capability-resolve saee.evaluate_agent_run --interface mcp
python3 scripts/saee_agent_cli.py capability-validate
```

Unknown capabilities fail explicitly. Exact aliases resolve to a canonical
`capability_id`; no fuzzy matching is used. Multiple canonical entries for one
capability and interface type fail validation.

## Compatibility And Deprecation

`deprecated` does not mean immediate removal. A deprecated capability or
interface must carry a reason, replacement, migration guidance, removal
criteria and usage evidence. Compatibility wrappers can remain active while
their role is explicit. v1 classifies existing MCP surfaces without deleting
them because real caller data is `UNKNOWN`.
