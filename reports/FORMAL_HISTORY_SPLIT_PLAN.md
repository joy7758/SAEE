# Formal History Split Plan

## Decision Summary

The change families are distinguishable, but the split is not safe to execute
yet. Family A is structurally ready with one hunk-isolation requirement. Family
B is blocked by conflicting current Alibaba review status across Agent-readable
truth surfaces.

## Commit Family A — SAEE Constitution Governance Baseline

Proposed message:

```text
chore: establish SAEE development constitution v1.1 baseline
```

### Whole-file members

1. `.codex/current_state.md`
2. `.codex/rules.md`
3. `agent-interface/governance/saee-development-constitution.v1.1.json`
4. `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md`
5. `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
6. `docs/product/SAEE_MODULE_REGISTRY.md`
7. `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md`
8. `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md`
9. `schemas/saee-development-constitution.schema.v1.1.json`
10. `scripts/mainline_guard.py`
11. `scripts/saee_development_constitution_smoke.py`

### Partial member

- `agent-index.json`: only add the `development_constitution_v1_1` top-level
  object. Reject the `generated_at` and Alibaba key-order hunks.

### Required validation before a future commit

- inspect `git diff --cached --name-only` and `git diff --cached`;
- parse the staged `agent-index.json` from the index;
- run `python3 scripts/saee_development_constitution_smoke.py`;
- run `python3 scripts/codex_context_check.py`;
- run `python3 scripts/saee_governance_registry_check.py`;
- run `python3 scripts/saee_capability_progress_ledger_smoke.py`;
- confirm `capability-package/manifest.json` is absent from the staged diff.

## Commit Family B — SAEE Alibaba Marketplace Repair

Proposed message after unblocking:

```text
fix: record Alibaba Marketplace product 68657 rejection repair
```

### Current candidate members

1. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json`
2. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md`
3. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json`
4. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md`
5. `scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py`

### Blocking prerequisite

Confirm the latest authoritative platform state for product `68657` /
`cmfw00074657`. Then classify each `审核中` surface as either current truth or a
time-bounded historical snapshot. Current truth surfaces must agree with the
chosen state in the same commercial-history change; historical observations
must remain explicitly historical.

Potential surfaces requiring that classification include `agent-index.json`,
the top `llms.txt` truth block, marketplace README/readiness contracts,
multi-cloud projections and validators. This plan does not authorize editing
them.

### Required validation after status reconciliation

- run `python3 scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py`;
- run the broader Alibaba entry-readiness smoke only after its current-vs-
  historical expectations are reviewed;
- confirm product remains `not listed`, `customer_validated=false` and
  `production_ready=false`;
- confirm no Constitution, capability, MCP, Agent Evidence or website file is
  staged.

## Recommended Git Method After Unblocking

Prefer exact-path staging plus `git add -p` for the one mixed file. Do not use a
new branch replay or temporary whole-repository patch: the current ancestry is
already correct, and replay would add unnecessary history risk.

Future sequence, not executed by this audit:

1. Recompute the 17-path status and content fingerprints.
2. Resolve the two human decisions in the Gate report.
3. Stage Family A whole-file members by exact path.
4. Run `git add -p agent-index.json`; accept only the Constitution object hunk.
5. Inspect and validate the staged snapshot before creating Family A.
6. Confirm Phase 0, Phase 0.5.1 and Dogfooding commits remain ancestors.
7. Stage the approved Family B paths only after Alibaba status reconciliation.
8. Inspect and validate the staged snapshot before creating Family B.
9. Verify remaining dirty entries; do not hide residual `agent-index.json` hunks.
10. Run full mainline validation in an isolated disposable worktree because the
    current mainline guard invokes reconciliation smokes that can rewrite local
    status snapshots even on PASS.

No `reset`, `restore`, `stash`, history rewrite, remote or push is required for
the designed split.

## History Integrity Effects

| Surface | Expected effect if plan is followed |
|---|---|
| Constitution continuity | Preserved: Phase 0 -> identity alignment -> Dogfooding -> Constitution baseline. |
| Alibaba audit chain | Preserved only after current-vs-historical status reconciliation. |
| Dogfooding evidence chain | Preserved; `f6ac41f4…` remains unchanged and continues to reference `e12f62a2…`. |
| Capability ledger | Unchanged; no canonical inventory fact is part of either family. |
| Mainline guard | Family A adds the Constitution smoke; final full run should use isolation to contain generated outputs. |
| Governance registry | Structure remains unchanged; existing registry already records rejected/repair/not-listed state. |
| Future remote migration | Improved by atomic history, but remote readiness remains separately blocked. |

## Safety Decision

```text
FAMILY_A=READY_AFTER_AGENT_INDEX_HUNK_ISOLATION
FAMILY_B=BLOCKED_BY_ALIBABA_STATUS_TRUTH_DRIFT
WHOLE_SPLIT=BLOCKED
```
