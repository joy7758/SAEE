# SAEE Agent Evidence Clean-Room Compatibility Adapter v0.1

## Purpose

This directory is the Agent-readable entry for migration slices M-04 through
M-06. It defines new SAEE-owned contracts for adapting selected traits from the
frozen Agent Evidence source and routing a separately supplied adequacy package
into the existing SAEE evaluator without copying or executing that repository.

```text
source_commit=e5f3ab67dfc3f0d86c1d83c2fee8d3014a5c6219
authorization=APPROVE_CLEAN_ROOM_TRAIT_MIGRATION
input_schema=../../schemas/saee-agent-evidence-trait-adapter-input.v0.1.json
result_schema=../../schemas/saee-agent-evidence-trait-adapter-result.v0.1.json
implementation=../../../saee_backend/services/agent_evidence_trait_adapter.py
smoke=../../../scripts/saee_agent_evidence_trait_adapter_smoke.py
evaluation_bridge_input=../../schemas/saee-agent-evidence-evaluation-bridge-input.v0.1.json
evaluation_bridge_result=../../schemas/saee-agent-evidence-evaluation-bridge-result.v0.1.json
evaluation_bridge=../../../saee_backend/services/agent_evidence_evaluation_bridge.py
evaluation_bridge_smoke=../../../scripts/saee_agent_evidence_evaluation_bridge_smoke.py
capability_status=NOT_A_CAPABILITY_INTERNAL_MIGRATION_ADAPTER
```

## Contract behavior

The adapter:

- accepts a closed, bounded synthetic event and source-completeness envelope;
- preserves event identity, ordering, timestamps, actor references, action
  labels, source references, upstream checks and `PASS/WARN/FAIL`;
- replaces payload content with a deterministic SHA-256 digest;
- rejects count mismatch, non-contiguous events, duplicate event IDs, open
  input objects and oversized payloads;
- records semantic loss explicitly;
- does not map events into quality, survival or risk scores;
- never treats adapted candidates themselves as adequate evidence.

The M-06 bridge:

- verifies the adapter receipt digest and declared event-ID subset before
  calling the existing SAEE evidence-adequacy evaluator;
- keeps package integrity and evidence adequacy in separate result contexts;
- preserves upstream `WARN` and any missing local integrity check as `REPLAN`;
- allows at most `HUMAN_REVIEW` when integrity and adequacy both pass because
  the Evidence-to-Evaluation binding is declared-only;
- never establishes authenticity, identity, authorization or permission to act.

## Fixtures

- `fixtures/valid-pass.v0.1.json`: upstream `PASS` remains integrity context.
- `fixtures/valid-signed.v0.1.json`: a synthetic Ed25519 signature over the
  adapter Merkle-root message is verified with an existing OpenSSL 3 binary.
- `fixtures/valid-warn.v0.1.json`: upstream `WARN` and one dropped event remain
  visible.
- `fixtures/invalid-counts.v0.1.json`: inconsistent source completeness is
  rejected.

All fixtures are synthetic and repository-controlled. They contain no customer
or external runtime data.

## Claims

- M-04 has a local clean-room compatibility fixture contract.
- A bounded SAEE-owned trait adapter is locally implemented and deterministic.
- Payload bytes are not retained in the adapted candidates.
- The local ASCII/integer JCS-safe subset, event chain, Merkle root and bounded
  Ed25519 verification are implemented with tamper-negative tests.
- A strict local Evidence-to-Evaluation bridge reuses the existing SAEE
  adequacy evaluator and preserves a `HUMAN_REVIEW` ceiling.

## Non-claims

- No historical source implementation text or Git history is copied.
- Full RFC 8785 JCS is not claimed; only the declared ASCII/integer safe subset
  is canonicalized locally.
- The synthetic Ed25519 check starts a disclosed local OpenSSL subprocess; no
  shell, network, installation or private key is used.
- Candidate output is not trusted evidence. M-06 evaluates a separate closed
  adequacy package bound by declared receipt/event references; it does not
  reinterpret candidate payload digests as evidence fields.
- The bridge binding and source-event authenticity are not independently
  verified, even when local integrity and adequacy both pass.
- No Agent Evidence API, MCP, worker, storage, auth, metering, marketplace or
  deployed runtime is integrated.
- These internal migration components are not canonical capabilities or
  completed SAEE Evidence / Evaluation customer versions.
