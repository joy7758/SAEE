# ADR-0002: Agent Evidence Boundary

## Status

Accepted for Phase 0.

## Context

`Agent Evidence Project` is the constitutional name for the evidence project
whose historical product name is `Agent Evidence Receipt` and whose historical
source repository is `agent-evidence-layer`. Its Receipt contracts, integrity,
provenance and source-completeness work strengthen the SAEE Evidence and Immune
Subsystem. It also has independent source, runtime and marketplace state.

## Decision

Agent Evidence Receipt is:

- an SAEE subproject at the constitutional architecture level;
- part of the SAEE Evidence and Immune Subsystem;
- a source of shared, versioned contract infrastructure when reuse gates pass.

It remains independent at Phase 0 for:

- source repository and Git history;
- runtime deployment and operations;
- public three-tool MCP contract;
- signing, tenant, token and metering operations;
- Aliyun product `68658` and its review state.

```text
constitutional_ownership=SAEE_EVIDENCE_AND_IMMUNE_SUBSYSTEM
source_code_migrated=false
runtime_integrated=false
marketplace_transferred=false
production_ready=false
```

## Shared infrastructure boundary

Schema crosswalks, canonicalization semantics, digest fields, validation result
envelopes, reason codes and negative fixtures may be proposed for reuse only
after source provenance, license, version and compatibility checks. Phase 0
does not copy any implementation.

## Rejected alternatives

- **Fully independent:** rejected because it conflicts with constitutional
  ownership.
- **Immediate repository merge:** rejected because source provenance, dirty
  worktree, runtime ownership and marketplace dependencies are not frozen.
- **Treat as SAEE runtime:** rejected because no runtime integration evidence
  exists.
