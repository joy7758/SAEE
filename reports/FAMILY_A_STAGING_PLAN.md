# Family A Staging Plan

Date: 2026-07-14
Phase: `0.5.2B Family A Constitution Governance Split Dry Run`
Current HEAD: `f6ac41f4b068377e7778e8c3d83b99bd8382debc`
Proposed future commit message: `chore: finalize SAEE constitution governance baseline`

## Scope Decision

```text
AFFECTED_LAYER=Governance
AFFECTED_OBJECT=SAEE Development Constitution v1.1 repository authority
CAPABILITY_FACT_CHANGE=false
DUPLICATE_CAPABILITY_CREATED=false
ALIBABA_CHANGE=false
AGENT_EVIDENCE_SOURCE_MIGRATED=false
PRODUCTION_READY=false
```

Family A strengthens the Evolutionary Archive / Rollback Immune System by
creating an auditable Constitution authority boundary. It does not add runtime
behavior or move the project into audit-first framing.

## Exact File Actions

| File | Action | Reason |
|---|---|---|
| `.codex/current_state.md` | `STAGE_FULL` | Constitution authority, Evidence/Immune ownership and explicit non-migration truth. |
| `.codex/rules.md` | `STAGE_FULL` | Constitution-first startup, duplicate-build and validator rules. |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | `STAGE_FULL` | Machine-readable Constitution contract. |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | `STAGE_FULL` | Evidence and Immune constitutional ownership and migration gates. |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | `STAGE_FULL` | Canonical Constitution v1.1 document. |
| `docs/product/SAEE_MODULE_REGISTRY.md` | `STAGE_FULL` | Module ownership alignment without source/runtime migration claim. |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | `STAGE_FULL` | Product architecture ownership and no-parallel-stack boundary. |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | `STAGE_FULL` | Agent Recommendation Gate and deferred blockers. |
| `schemas/saee-development-constitution.schema.v1.1.json` | `STAGE_FULL` | Closed schema for the machine contract. |
| `scripts/mainline_guard.py` | `STAGE_FULL` | Adds the Constitution package and smoke to the guard. |
| `scripts/saee_development_constitution_smoke.py` | `STAGE_FULL` | Deterministic, negative and staged-truth validation. |
| `agent-index.json#development_constitution_v1_1` | `STAGE_HUNK` | The only Family A semantic hunk in the mixed file. |
| `agent-index.json#commercial_trial_operator_status_v0_1.generated_at` | `DO_NOT_STAGE` | Unrelated generated timestamp residual. |
| `agent-index.json#alibaba_marketplace_assessment_delivery_bridge_v0_1` | `DO_NOT_STAGE` | Semantically neutral serialization/key-order noise. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json` | `DO_NOT_STAGE` | Family B commercial repair and lifecycle truth. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md` | `DO_NOT_STAGE` | Family B provider-neutral marketplace copy repair. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json` | `DO_NOT_STAGE` | Family B marketplace copy and review-state record. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md` | `DO_NOT_STAGE` | Family B user-guide repair. |
| `scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py` | `DO_NOT_STAGE` | Family B validator. |
| `reports/CONSTITUTION_VS_ALIBABA_FILE_MAP.md` | `DO_NOT_STAGE` | Phase 0.5.2 audit output, not Constitution implementation history. |
| `reports/FORMAL_HISTORY_DIRTY_INVENTORY.md` | `DO_NOT_STAGE` | Phase 0.5.2 audit output. |
| `reports/FORMAL_HISTORY_SPLIT_PLAN.md` | `DO_NOT_STAGE` | Phase 0.5.2 audit output. |
| `reports/PHASE0_5_2_BASELINE.md` | `DO_NOT_STAGE` | Phase 0.5.2 audit output. |
| `reports/PHASE0_5_2_CHANGE_READINESS_DESIGN.md` | `DO_NOT_STAGE` | Phase 0.5.2 audit output. |
| `reports/PHASE0_5_2_SPLIT_GATE.md` | `DO_NOT_STAGE` | Phase 0.5.2 audit output. |
| `reports/FAMILY_A_AGENT_INDEX_HUNK_PLAN.md` | `DO_NOT_STAGE` | Dry-run planning output, not Commit A content. |
| `reports/FAMILY_A_STAGING_PLAN.md` | `DO_NOT_STAGE` | Dry-run planning output, not Commit A content. |
| `reports/FAMILY_A_SPLIT_GATE.md` | `DO_NOT_STAGE` | Dry-run gate output, not Commit A content. |

## Future Staging Sequence

The following sequence is a design for a later authorized execution. It was
not run by this dry run.

1. Reconfirm HEAD and the protected 17-path fingerprints.
2. Stage the 11 `STAGE_FULL` paths by exact path; never use `git add .`.
3. Inspectively hunk-stage `agent-index.json` according to
   `reports/FAMILY_A_AGENT_INDEX_HUNK_PLAN.md`.
4. Inspect `git diff --cached --name-only` and the complete cached diff.
5. Parse the staged `agent-index.json` and verify the Constitution object hash.
6. Confirm all `DO_NOT_STAGE` paths and residual hunks remain unstaged.
7. Run the staged-snapshot validations below.
8. Do not commit until the staged gate is separately reviewed.

## Future Staged-Snapshot Validation

Required before Commit A:

1. Constitution smoke: PASS.
2. Codex context check: PASS.
3. Governance registry check: PASS.
4. Capability progress ledger smoke: PASS.
5. Staged `agent-index.json`: valid JSON and exact Constitution-only delta.
6. `capability-package/manifest.json`: absent from staged diff.
7. Alibaba, MCP, Agent Evidence source/runtime, website and product files:
   absent from staged diff.
8. Phase 0 commit `307cebd6c…`, Phase 0.5.1 commit `e12f62a2…` and Dogfooding
   commit `f6ac41f4…`: ancestry intact.
9. Mainline guard: PASS in an isolated disposable worktree or equivalent
   isolated staged snapshot, because the current guard can invoke
   reconciliation smokes that rewrite local status snapshots even on PASS.

## Rollback Boundary

Before a commit exists, rollback means clearing only the future index entries
through a separately authorized non-destructive index operation. This dry run
does not prescribe or execute `reset`, `restore`, `stash` or worktree cleanup.
