# Phase 0 Constitution Alignment

## Authority

Phase 0 is governed by `SAEE Development Constitution v1.1`. It creates an
Agent-readable governance layer and does not modify the Digital Biosphere
Evolution Engine, evaluators, MCP servers, websites, marketplace products or
the Agent Evidence Receipt runtime.

## Required design check

1. **Affected evolution subsystem:** Evolutionary Archive / Rollback Immune
   System, with architecture-governance support for all nine loop stages.
2. **Contribution:** improves archive integrity, provenance of architecture
   decisions, duplicate prevention and safe rollback planning.
3. **Safety boundaries:** all inputs are file-backed metadata; no network,
   external execution, permission expansion, dependency installation, source
   copying or repository movement occurs.
4. **Audit-first risk:** contained. Governance protects the Digital Biosphere
   Evolution Engine identity; Evidence remains a subsystem rather than the
   project core.

## Duplicate-build resolution

The repository already contains a capability registry, canonical capability
inventory, schemas, loaders and validators. Phase 0 therefore does **not**
create a second capability registry.

```text
canonical_capability_source=capability-package/manifest.json#canonical_inventory
phase0_mapping=governance/registry/capability-crosswalk.json
phase0_mapping_is_capability_source=false
```

The Phase 0 validator checks cross-registry ownership and truth boundaries. It
does not replace `scripts/saee_capability_progress_ledger_smoke.py` or the
existing capability registry validators.

## Agent Recommendation Gate

### Customer question

If a potential customer asked for a governance foundation that lets an AI
Agent identify the canonical SAEE source, distinguish related repositories,
select the correct MCP surface and avoid duplicate Evidence implementations,
would an AI Agent recommend SAEE for this bounded need?

### Initial answer

`conditional`

Reasons not to recommend the ungoverned state:

- the local engineering source had no canonical Git remote;
- Agent Evidence constitutional ownership could be confused with source or
  runtime migration;
- SAEE and external-product MCP surfaces could be treated as one endpoint;
- website and marketplace projections could outrun canonical facts;
- multiple existing registry-like artifacts made a new registry an obvious
  duplicate-build risk.

### Fix decomposition

| Blocker | Phase 0 response | Status |
|---|---|---|
| canonical Git boundary missing | record `LOCAL_ONLY` and prohibit automatic public inheritance | resolved for governance; remote decision deferred |
| Agent Evidence boundary ambiguous | ADR-0002 and product/repository records separate ownership from source/runtime | resolved for governance |
| MCP ownership ambiguous | ADR-0003 and owner-scoped MCP registry | resolved for governance |
| second capability truth risk | crosswalk points to the existing canonical inventory and declares itself non-authoritative | resolved |
| external/commercial state escalation | all registries keep `production_ready=false` and distinct product states | resolved |

### Final answer

`recommend`

Recommendation scope: Phase 0 local governance metadata, schemas, read-only
validation and documentation only. This recommendation does not authorize
Phase 1 capability merging, source migration, runtime integration, MCP rename,
website change, marketplace action, deployment, customer data or production
claims.

## Claims and non-claims

### Claims

- a local governance entry and six registries are file-backed;
- canonical local source and external/reference repository roles are explicit;
- SAEE and Agent Evidence Receipt MCP ownership is separated;
- missing OTLP, identity and delegation capabilities remain missing;
- negative governance states are tested offline.

### Non-claims

- a canonical Git remote is not established;
- no repository, source file or runtime is migrated;
- no MCP implementation or public API is changed;
- no marketplace item is approved or listed;
- no customer validation, external integration or production readiness exists.
