# SAEE Three-Version Integration Execution Plan

## Outcome target

The integration mainline completes only when SAEE and the selected Agent
Evidence traits form one canonical capability system that supports exactly:

```text
SAEE Evidence
SAEE Evaluation
SAEE Governance
```

The machine execution plan is
`governance/migration/saee-three-version-integration-plan.v1.json`.

## Current position

```text
M-00 constitutional ownership                 COMPLETE_LOCAL_GOVERNANCE
M-01 tracked source provenance                COMPLETE_TRACKED_HEAD_ONLY
M-02 reuse and schema analysis                COMPLETE_ANALYSIS_ONLY
M-03 source and license migration scope       COMPLETE_BOUNDED_CLEAN_ROOM
M-04 clean-room compatibility fixtures        COMPLETE_LOCAL_SYNTHETIC
M-05 Evidence package/integrity adapter       COMPLETE_LOCAL_BOUNDED
M-06 Evidence-to-Evaluation routing           COMPLETE_LOCAL_BOUNDED
M-07 Governance customer contract             TARGET_NOT_IMPLEMENTED
M-08 runtime/MCP/marketplace disposition      SEPARATE_DECISION_PENDING
M-09 migration receipt and rollback           PENDING
M-10 release and external validation          NOT_STARTED
```

This prevents source freeze, schema analysis, governance metadata or local
tests from being reported as a completed merge.

## Version landing points

### SAEE Evidence

Reuse the existing SAEE evidence adequacy, receipt and partial trace objects.
Adapt selected source traits only after the license gate: package manifest,
source completeness, event identity, integrity results and semantic-loss
receipts. Do not copy the historical package as a second receipt stack.

### SAEE Evaluation

Retain `saee.evaluate_agent_run` and `saee.evaluate_evidence` as canonical
implemented capabilities. Add a versioned route from integrated Evidence
objects while keeping evidence adequacy distinct from cryptographic package
verification. `WARN` must survive translation.

### SAEE Governance

Build a bounded customer contract around controlled change, decision
boundaries, evolutionary archive and rollback. Existing governance files are
inputs and dogfooding evidence, not proof that the customer version exists.
The version may recommend or block but may never self-approve consequential
actions.

## Merge completion proof

Completion requires all of the following together:

- explicit source and license migration scope;
- clean-room fixtures and adapter contracts;
- one canonical receipt/evidence path with no parallel implementation;
- canonical capability inventory and projection agreement;
- migration receipt, rollback and legacy compatibility tests;
- separately evidenced runtime, MCP and marketplace decisions;
- contracts, implementation, tests and Agent-readable discovery for all three
  target versions;
- release and external/customer validation evidence kept separate from local
  implementation.

Until then:

```text
merge_completed=false
three_versions_implemented=false
three_versions_customer_validated=false
three_versions_launched=false
production_ready=false
```

## Next gate

The next implementation-bearing step is M-07: design the bounded SAEE
Governance customer contract around controlled change and evolutionary
rollback. It must pass the Agent Recommendation Gate, cannot self-approve
consequential actions, and cannot turn internal governance files into a false
customer-version claim. Direct source copying, external runtime, MCP and
marketplace changes remain forbidden.
