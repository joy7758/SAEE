# Canonical Capability Routing Postflight

Date: 2026-07-13

Scope: repository-local capability discovery, deterministic routing and
compatibility truth. This assessment does not claim a deployed public service,
external interoperability, customer validation or production readiness.

## Customer Need

> We plan to integrate SAEE and need an unambiguous statement of formal
> capabilities, canonical and compatibility entry points, deprecation
> relationships and current implementation status.

## 1. Recommendation After This Change

`recommend` for bounded local, repository-controlled readiness evaluation.

`conditional` for third-party or enterprise integration because no deployed
public endpoint, external MCP interoperability evidence, customer validation or
production evidence exists.

The recommendation is limited to the capability and routing contract validated
by `python3 scripts/saee_canonical_capability_inventory_smoke.py`.

## 2. Recommended Entry

Use the platform-neutral project configuration `.mcp.json`, which starts:

```text
python3 scripts/saee_agent_readiness_mcp_stdio.py
```

The canonical local public-contract tools are:

- `saee.evaluate_agent_run`
- `saee.evaluate_evidence`

This is a local stdio contract, not a deployed public MCP endpoint.

## 3. Limited Claims Supported

- SAEE has one machine-readable capability authority:
  `capability-package/manifest.json#canonical_inventory`.
- The two readiness operations above are implemented, locally executable and
  covered by repository tests.
- Four executable MCP stdio surfaces are classified and machine-routable.
- Exact capability IDs and aliases resolve deterministically; unknown IDs and
  multiple canonical entries fail closed.
- The existing synthetic OpenTelemetry-style candidate mapper is implemented
  for a bounded offline input shape and is not rebuilt by this change.

## 4. Remaining Reasons For Caution

- `public_mcp_endpoint_available=false`.
- `external_mcp_interoperability_validated=false`.
- `customer_validated=false`.
- `production_ready=false`.
- Real caller usage for compatibility and internal surfaces is `UNKNOWN`.
- Real OTLP ingestion, Collector compatibility, trace authenticity, external
  identity binding and delegation binding remain missing.

## 5. Blockers Removed Since Preflight

- Capability facts now have one runtime-consumed canonical source.
- `agent-index.json`, public operations, well-known discovery and critical
  Agent-readable documents are strict projections validated against it.
- All four executable MCP stdio surfaces have a role, audience, test evidence,
  compatibility guidance and truthful `usage_evidence`.
- The platform-neutral two-tool wrapper is the sole canonical public contract.
- Historical `recommended_next_pr` fields are globally deprecated as
  compatibility metadata; completed OTEL work cannot remain an active
  recommendation without failing validation.
- Sixteen adversarial mutations prove the guard fails on projection drift,
  duplicate IDs, routing conflicts, deprecation cycles and missing paths.

## 6. Should Read-Only OTLP Ingestion Be Next?

Not automatically. It is a reasonable next capability candidate only after a
fresh recommendation gate confirms a concrete consumer need and avoids
rebuilding the existing synthetic mapper. Governance completion alone is not
evidence of adoption demand.

## 7. Conditions Before Starting OTLP Ingestion

Do not start until all of the following are recorded:

1. this canonical inventory change is accepted on the repository mainline;
2. a named read-only consumer and bounded input contract are documented;
3. OTLP transport scope is chosen explicitly (`OTLP/HTTP`, `OTLP/gRPC`, or an
   offline export), including Collector and semantic-convention non-claims;
4. trust boundaries distinguish received telemetry, normalized observations,
   candidate evidence and verified evidence;
5. identity, delegation and authenticity remain explicit missing capabilities
   unless independently implemented and tested;
6. the feature passes the required Agent Recommendation Gate and identifies
   which evolution subsystem it strengthens;
7. the canonical inventory, schemas, CLI/tool surface, negative tests,
   `agent-index.json`, `AGENTS.md` and `llms.txt` have a same-change sync plan.

## Final Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: canonical capability inventory routing and deprecation map v1
  target_customer_need: identify real SAEE capabilities and the correct local MCP entry without ambiguity
  answer: recommend
  recommendation_scope: bounded local repository-controlled readiness evaluation only
  canonical_source: capability-package/manifest.json#canonical_inventory
  canonical_entry: python3 scripts/saee_agent_readiness_mcp_stdio.py
  remaining_conditions:
    - no deployed public MCP endpoint
    - external interoperability not validated
    - customer validation absent
    - production readiness absent
  otlp_next_step: conditional_candidate_not_authorized
  production_ready: false
  customer_validated: false
```
