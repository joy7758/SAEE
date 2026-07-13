# SAEE Capability Registry Migration Notes v0.1

## Purpose

These notes preserve the difference between current local capability contracts and the historical public discovery snapshot. They propose a future migration without rewriting historical records or claiming that migration has occurred.

```text
historical_records_rewritten=false
public_metadata_migrated=false
known_public_surface_gap_count=3
```

## Drift Register

| ID | Detected drift | Current state | Proposed resolution | Status |
|---|---|---|---|---|
| `REGISTRY-MIGRATION-001` | Public capability manifest does not reference the Phase 4.1 Tool request/output schemas | Public surface remains static and does not expose a callable Tool | In a separately approved public metadata release, add non-executable schema links and keep `public_tool_available=false` until a separate service gate | `OPEN_DOCUMENTED` |
| `REGISTRY-MIGRATION-002` | Public manifest lists `observation_references` as required; local Tool treats them as optional inert provenance | Registry card follows the implemented local contract: required evidence/claim/profile, optional observation references | Version the public input contract and migrate the field to optional without altering the v0.1 historical snapshot | `OPEN_DOCUMENTED` |
| `REGISTRY-MIGRATION-003` | Public limitations page states that the entry uses IP/HTTP without TLS | Live canonical entry was inspected over HTTPS, while the checked-in historical limitations text remains stale | Correct the statement in a future public metadata release and retain the old release as historical evidence | `OPEN_DOCUMENTED` |

## Current Canonical Interpretation

- Local Tool contract truth: `agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json`.
- Local output truth: `agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json`.
- Public historical snapshot: `public-release/saee-agent-discovery-v0.1/`.
- Registry migration status: documentation only; no public deployment performed.

The registry card exposes local file-backed contract references for agent reasoning. It does not claim that these references are already published at `redcrag.cn` or callable by external agents.

## Migration Gate

Before any public migration:

1. create a versioned public metadata change plan;
2. verify URL and schema stability;
3. preserve historical snapshot hashes;
4. rerun discovery and boundary tests;
5. obtain explicit deployment approval;
6. keep registry, Tool, adoption and production status separate.
