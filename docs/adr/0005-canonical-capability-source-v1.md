# ADR-0005: Canonical Capability Source v1
# ADR-0005：规范能力真源第一版

## Status

Accepted（已接受）

## Context

SAEE has several valid but overlapping capability projections: the Capability
Service Package, registry objects, public discovery metadata,
`agent-index.json`, MCP descriptors and release material. They were created for
different phases and audiences. Without an explicit authority and validation
direction, an Agent can select an obsolete entry or recommend already completed
work.

The repository also contains four executable MCP stdio surfaces. They are not
four equivalent public services: two share one readiness implementation, one is
an internal Capability Runtime adapter and one is a legacy observed-trace
surface. Deleting them without usage evidence would be unsafe.

## Decision

`capability-package/manifest.json` is the sole canonical source for current
integrable capability facts, canonical local entry points, interface roles,
claims, non-claims and compatibility/deprecation relationships.

This existing source is selected because:

- `saee_backend/services/capability_runtime/capability_registry_loader.py`
  already consumes it before routing local Capability Runtime requests;
- it already owns package identity, operations, contracts, runtime references,
  boundaries and validation commands;
- it is repository-relative, deterministic and dependency-free JSON;
- extending it avoids creating a fifth independent inventory.

The manifest's `canonical_inventory` object is authoritative. Existing
top-level `operations` remain for one compatibility cycle and are strictly
validated against canonical records. They are not a second authority.

Development recommendations are not capability facts. They remain in
assessment or roadmap documents. `recommended_next_pr` in `agent-index.json`
is a deprecated compatibility field and cannot override the manifest.

## Existing Sources Accepted Or Rejected

| Source | Decision | Reason |
|---|---|---|
| `capability-package/manifest.json` | Accepted and extended | Runtime-consumed, bounded package authority, already validated |
| `agent-interface/registry/saee-capability-card.v0.1.json` | Validated projection | Detailed evidence-adequacy registry entry, but not a complete routing inventory |
| `agent-interface/capabilities/saee-capability-manifest.v0.1.json` | Historical capability description | Large research narrative and phase history; not runtime routing authority |
| `agent-interface/public/saee-public-capability-surface.v0.1.json` | Validated public projection | Public discovery view, not implementation authority |
| `agent-index.json` | Validated retrieval projection | Very broad historical index mixing facts and roadmap fields |
| New `capability-inventory.yaml` | Rejected | Would create another manually synchronized truth source |

## Generated And Validated Views

The v1 implementation uses validation mode rather than rewriting large legacy
files:

```text
capability-package/manifest.json#canonical_inventory
    -> validates capability-package projections
    -> validates agent-index.json capability progress projection
    -> validates public capability metadata and well-known discovery
    -> validates MCP surface classification and executable paths
    -> validates Agent-readable documentation routes
```

The validator must inspect implementation, executable entry point, tests and
documentation for every `implemented` record. It must reject conflicting IDs,
aliases, canonical interfaces, missing paths, deprecation cycles and public
surface drift.

## Compatibility Impact

- No MCP executable is deleted.
- The platform-neutral `scripts/saee_agent_readiness_mcp_stdio.py` becomes the
  canonical local public-contract entry.
- `scripts/saee_qianfan_readiness_mcp_stdio.py` remains a Qianfan compatibility
  wrapper over the same implementation.
- `scripts/saee_capability_mcp_stdio.py` remains an internal package adapter.
- `scripts/saee_mcp_stdio.py` remains an internal legacy observed-trace surface.
- Existing `operations` and `recommended_next_pr` fields remain readable for a
  compatibility cycle but are explicitly non-authoritative.

## Migration Path

1. Inventory and classify every current MCP stdio executable.
2. Route new local integrations through `.mcp.json` and the platform-neutral
   readiness entry.
3. Keep compatibility commands operational while documentation migrates.
4. Collect real usage evidence; until then `usage_evidence=UNKNOWN`.
5. Deprecate or retire a surface only after callers are known, replacement
   coverage is verified and a separately reviewed removal decision exists.

## Non-Goals

- OTLP, OTLP/gRPC, OTLP/HTTP or Collector ingestion;
- OpenTelemetry semantic-convention compliance;
- trace authenticity, signing or remote attestation;
- identity or delegation binding;
- a new MCP server or runtime control plane;
- physical deletion of compatibility surfaces;
- production, customer, certification or public-deployment claims;
- a new long-term product roadmap.

## Consequences

The manifest becomes more structured and its validation becomes stricter. A
capability fact change is incomplete until implementation/contracts, tests,
public projections, Agent-readable documentation and the canonical inventory
agree. Audit remains an immune/evidence subsystem; this ADR governs archive and
reuse integrity rather than reframing SAEE as an audit product.
