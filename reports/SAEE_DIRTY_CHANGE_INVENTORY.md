# SAEE Dirty Change Inventory

## Classification rule

- `A_FORMAL_HISTORY`: required constitutional, governance, validation or
  verified marketplace-history change that should enter reviewed Git history.
- `B_EXPERIMENTAL`: bounded exploration that should remain separate from the
  formal mainline.
- `C_GENERATED`: reproducible generated output that may become a future delete
  candidate after source and retention checks.
- `D_UNKNOWN`: ownership or purpose cannot yet be established.

No file was modified, deleted, reset, restored or cleaned to produce this
inventory.

## Inventory

| File | Change type | Category | Commit family | Disposition |
|---|---|---|---|---|
| `.codex/context.md` | modified | `A_FORMAL_HISTORY` | Codex identity alignment | Preserve; commit only after validator contract is aligned |
| `.codex/current_state.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; formal state-boundary update |
| `.codex/rules.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; formal Codex governance update |
| `AGENTS.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; constitutional authority pointer |
| `README.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; product/core relationship update |
| `agent-index.json` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; machine projection with staged truth |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json` | modified | `A_FORMAL_HISTORY` | Alibaba 68657 repair | Preserve separately; records rejected/repair/not-listed state |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md` | modified | `A_FORMAL_HISTORY` | Alibaba 68657 repair | Preserve separately; removes unsupported platform association |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json` | modified | `A_FORMAL_HISTORY` | Alibaba 68657 repair | Preserve separately; review-state and non-claim repair |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md` | modified | `A_FORMAL_HISTORY` | Alibaba 68657 repair | Preserve separately; provider-neutral non-claim |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; Agent Evidence subsystem boundary |
| `docs/product/SAEE_MODULE_REGISTRY.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; module ownership without source migration claim |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; Evidence/Immune product-architecture boundary |
| `llms.txt` | modified | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; authority pointers, not live-state copy |
| `scripts/mainline_guard.py` | modified | `A_FORMAL_HISTORY` | Constitution validation | Preserve; commit only after full mainline passes |
| `scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py` | modified | `A_FORMAL_HISTORY` | Alibaba 68657 repair | Preserve separately; validates provider-neutral repair state |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | untracked | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; machine contract |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | untracked | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; constitutional authority document |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | untracked | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; Agent Recommendation Gate |
| `schemas/saee-development-constitution.schema.v1.1.json` | untracked | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; strict machine schema |
| `scripts/saee_development_constitution_smoke.py` | untracked | `A_FORMAL_HISTORY` | Constitution v1.1 | Preserve; deterministic validator |

## Formal commit boundaries

### Commit family 1 — Constitution v1.1 authority package

Include the constitution document, machine contract, schema, recommendation
gate, smoke, module/product/immune alignment, `AGENTS.md`, `README.md`,
`agent-index.json`, `llms.txt` and bounded Codex authority surfaces.

This family is **not ready to commit as-is** because the changed
`.codex/context.md` no longer satisfies the unchanged
`scripts/codex_context_check.py`. The identity validator must be aligned in the
same stabilization PR, then `make check` must pass.

### Commit family 2 — Alibaba product 68657 repair

Keep the five marketplace repair files in an independent commit/PR. They
record a platform-derived rejection/repair state and remove unsupported
platform-association claims. They must not be bundled with constitutional or
Codex identity changes.

## What should remain independent?

- Alibaba 68657 repair remains independent from Constitution v1.1.
- Agent Evidence Layer remains an external repository/runtime baseline; no
  source from it belongs in either SAEE commit family.
- Phase 0.5 reports and stabilization registry form their own governance-only
  commit.

## Future deletion candidates

None are confirmed.

There are no `C_GENERATED` or `D_UNKNOWN` entries in the current 21-file SAEE
snapshot. Any future deletion requires reference, provenance, restore and
retention evidence; filename age or duplication appearance is insufficient.

## Decision

```text
dirty_entries=21
formal_history=21
experimental=0
generated=0
unknown=0
safe_to_delete_now=0
worktree_classified=true
worktree_clean=false
```
