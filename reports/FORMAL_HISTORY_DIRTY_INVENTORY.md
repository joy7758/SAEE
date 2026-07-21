# Formal History Dirty Inventory

Baseline HEAD: `f6ac41f4b068377e7778e8c3d83b99bd8382debc`

| File | Status | Size (bytes) | Category | Reason |
|---|---:|---:|---|---|
| `.codex/current_state.md` | `M` | 1,696 | `CONSTITUTION_GOVERNANCE` | Adds Constitution authority, Agent Evidence ownership and explicit non-migration truth. |
| `.codex/rules.md` | `M` | 1,873 | `CONSTITUTION_GOVERNANCE` | Adds constitution-first, duplicate-build, recommendation-gate and validator rules. |
| `agent-index.json` | `M` | 2,097,009 | `MIXED_SCOPE` | Adds the Constitution machine entry, changes an unrelated generated timestamp and contains textual key-order noise; its Alibaba current status remains `审核中`. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json` | `M` | 5,675 | `ALIBABA_COMMERCIAL_REPAIR` | Changes product 68657 from review-in-progress to rejected/repair-in-progress and removes unsupported cloud-platform association. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md` | `M` | 2,563 | `ALIBABA_COMMERCIAL_REPAIR` | Makes customer/platform wording provider-neutral and strengthens the no-official-integration claim. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json` | `M` | 6,613 | `ALIBABA_COMMERCIAL_REPAIR` | Records rejected/repair/not-listed state and removes unsupported Bailian positioning. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md` | `M` | 3,224 | `ALIBABA_COMMERCIAL_REPAIR` | Replaces a Bailian-specific non-claim with a provider-neutral platform non-claim. |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | `M` | 1,761 | `CONSTITUTION_GOVERNANCE` | Places Agent Evidence in the Evidence and Immune Subsystem with staged-truth boundaries. |
| `docs/product/SAEE_MODULE_REGISTRY.md` | `M` | 2,196 | `CONSTITUTION_GOVERNANCE` | Aligns module ownership without claiming source or runtime migration. |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | `M` | 2,301 | `CONSTITUTION_GOVERNANCE` | Adds the constitutional Agent Evidence relationship and prevents a parallel evidence stack. |
| `scripts/mainline_guard.py` | `M` | 4,029,698 | `CONSTITUTION_GOVERNANCE` | Adds Constitution package files and the Constitution smoke to mainline validation. |
| `scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py` | `M` | 5,766 | `ALIBABA_COMMERCIAL_REPAIR` | Validates provider-neutral copy and accepts the repair-state review value. |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | `??` | 3,541 | `CONSTITUTION_GOVERNANCE` | New closed machine contract for Constitution v1.1. |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | `??` | 11,284 | `CONSTITUTION_GOVERNANCE` | New canonical development authority document. |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | `??` | 4,257 | `CONSTITUTION_GOVERNANCE` | Records the conditional-to-recommend governance decision and deferred migration blockers. |
| `schemas/saee-development-constitution.schema.v1.1.json` | `??` | 5,219 | `CONSTITUTION_GOVERNANCE` | New strict JSON Schema for the machine contract. |
| `scripts/saee_development_constitution_smoke.py` | `??` | 9,698 | `CONSTITUTION_GOVERNANCE` | New deterministic and negative-case Constitution validator. |

## Count

```text
CONSTITUTION_GOVERNANCE=11 pure files
ALIBABA_COMMERCIAL_REPAIR=5 pure files
MIXED_SCOPE=1 file
UNKNOWN=0 whole files
TOTAL=17
```

The `MIXED_SCOPE` file contains one attributable Constitution entry and
unrelated residual hunks. It must not be staged as a whole.
