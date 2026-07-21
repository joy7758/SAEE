# SAEE Agent Evidence Schema Compatibility Gate

## Decision

```text
SCHEMA_INVENTORY_FROZEN=true
DIRECT_SCHEMA_COMPATIBILITY=false
ADAPTER_REQUIRED=true
ADAPTER_IMPLEMENTED=true
ADAPTER_IMPLEMENTATION_STATUS=COMPLETED_BOUNDED_LOCAL_INTEGRITY_AND_EVALUATION_BRIDGE
LICENSE_GATE=PASS_BOUNDED_CLEAN_ROOM_SCOPE
MIGRATION_EXECUTION=AUTHORIZED_FIXTURES_AND_ADAPTERS_ONLY
DECISION=PASS_BOUNDED_ADAPTER_AND_EVALUATION_BRIDGE_LOCAL
```

This is a read-only field and trait comparison against the tracked source at
`e5f3ab67dfc3f0d86c1d83c2fee8d3014a5c6219`. It does not copy source schemas
or implementation into an SAEE runtime path.

## Compatibility findings

| Source contract | SAEE destination | Result | Required route |
|---|---|---|---|
| Normalized Event `0.2.0` | `ObservedTraceBundle` | lossy, not directly compatible | allowlisted adapter with semantic-loss receipt |
| Receipt Manifest `0.2.0` | invocation/resource receipts `0.1` | distinct lifecycle and integrity scopes | preserve versioned contracts; adapt only after gate |
| Verification Receipt `0.2.0` | evidence adequacy result | different result and check taxonomies | separate integrity and adequacy claims |

The machine-readable field map is
`governance/migration/agent-evidence-schema-compatibility.v1.json`.

## Critical semantic gaps

- Agent Evidence event IDs, timestamps, actions and per-event source refs do
  not have lossless destinations in the current SAEE observed-trace model.
- Agent Evidence payloads cannot be treated as SAEE quality, survival or risk
  metrics without an explicit, allowlisted extractor.
- Agent Evidence JCS is not proven equivalent to `saee-canonical-json-v0.1`.
- Merkle root, source-completeness digest and signer fields have no equivalent
  in the current SAEE invocation receipt.
- Agent Evidence `WARN` has no direct SAEE evidence-adequacy result value and
  must never be silently promoted to `PASS`.
- Cryptographic package verification and evidence adequacy answer different
  questions and must remain separately visible.

## Mainline correction

The merge route is therefore adapter-first, not repository-copy-first:

```text
Agent Evidence tracked contract
  -> versioned compatibility adapter
  -> SAEE Evidence package/integrity surface
  -> SAEE Evaluation adequacy surface
  -> SAEE Governance policy and non-claim surface
```

This advances the three-version target without pretending that those versions
already exist.

## Current implementation boundary

The authorized rightsholder approved the bounded clean-room scope. Four local
synthetic fixtures, a strict SAEE-owned trait adapter and a local
Evidence-to-Evaluation bridge are implemented. The adapter preserves event
identity, completeness and upstream result status while replacing payload
content with a digest. The bounded ASCII/integer canonicalization subset,
event-chain, Merkle-root and optional Ed25519 checks are performed locally; full
RFC 8785 and historical-bundle conformance are not claimed. The bridge reuses
the existing adequacy evaluator and can reach `HUMAN_REVIEW` at most. Runtime,
MCP and marketplace changes remain outside this gate.
