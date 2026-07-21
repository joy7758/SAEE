# Constitution vs Alibaba File Responsibility Map

## File Map

| File | Ownership | Evidence | Split recommendation |
|---|---|---|---|
| `.codex/current_state.md` | `A_CONSTITUTION` | Constitution authority, Evidence/Immune ownership, `source_code_migrated=false`, `runtime_integrated=false`. | Entire file diff belongs in Family A. |
| `.codex/rules.md` | `A_CONSTITUTION` | Constitution-first read order, duplicate-build gate and Constitution smoke requirement. | Entire file diff belongs in Family A. |
| `agent-index.json` | `C_SHARED` | Semantic JSON comparison finds `development_constitution_v1_1` added and `commercial_trial_operator_status_v0_1.generated_at` changed. A separate early hunk only reorders equal Alibaba values; the actual review value remains `审核中`. | Use hunk-level staging. Put only `development_constitution_v1_1` in A. Do not put the timestamp/order hunks in A or B. Alibaba truth alignment requires a separate decision before B. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json` | `B_ALIBABA` | Product `68657`, code `cmfw00074657`, rejected/repair/not-listed state and provider-neutral anchor. | Family B, but only after current-status truth drift is resolved. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md` | `B_ALIBABA` | Removes unsupported Bailian-specific association and platform endorsement implication. | Entire file diff belongs in Family B. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json` | `B_ALIBABA` | Rejected/repair state, provider-neutral SEO copy and no official platform integration. | Family B, subject to status-source reconciliation. |
| `cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md` | `B_ALIBABA` | Provider-neutral no-integration/non-endorsement statement. | Entire file diff belongs in Family B. |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | `A_CONSTITUTION` | Constitutional Agent Evidence ownership and staged-truth migration gates. | Entire file diff belongs in Family A. |
| `docs/product/SAEE_MODULE_REGISTRY.md` | `A_CONSTITUTION` | Evidence and Immune module ownership; explicit source-history preservation. | Family A despite its `docs/product` location; semantics are architectural governance. |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | `A_CONSTITUTION` | Agent Evidence subsystem role and no-parallel-stack boundary. | Entire file diff belongs in Family A. |
| `scripts/mainline_guard.py` | `A_CONSTITUTION` | Requires all five Constitution package files and invokes their smoke. | Entire file diff belongs in Family A. |
| `scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py` | `B_ALIBABA` | Validates product copy, provider-neutral terms and marketplace review boundary. | Family B after truth-source reconciliation. |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | `A_CONSTITUTION` | Machine contract declares development authority and staged truth. | Entire new file belongs in Family A. |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | `A_CONSTITUTION` | Canonical Constitution v1.1. | Entire new file belongs in Family A. |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | `A_CONSTITUTION` | Governance recommendation and deferred migration blockers. | Entire new file belongs in Family A. |
| `schemas/saee-development-constitution.schema.v1.1.json` | `A_CONSTITUTION` | Closed schema for the machine authority contract. | Entire new file belongs in Family A. |
| `scripts/saee_development_constitution_smoke.py` | `A_CONSTITUTION` | Deterministic, negative and staged-truth validation. | Entire new file belongs in Family A. |

## Cross-File Analysis

### Is any file both Constitution and Alibaba repair?

No file contains both a real Constitution change and a real Alibaba repair
change. `agent-index.json` is still `C_SHARED` because it combines the Family A
machine entry with non-A residuals. Its Alibaba hunk is textual key-order noise,
not a repair-state update.

### Entry files already in history

`AGENTS.md`, `README.md`, `llms.txt`, `.codex/context.md` and
`scripts/codex_context_check.py` were committed by Phase 0.5.1. They must not be
restaged into Family A. Their history is an existing dependency of Family A.

### Alibaba current-truth drift

The following facts conflict:

- `governance/registry/asset-registry.json` and the five repair files say product
  68657 was rejected, repair is in progress and it is not listed.
- `agent-index.json`, the top `llms.txt` truth block, marketplace readiness
  contracts and several validators still say `审核中` / review in progress.
- `submission-observation.v0.1.json` can remain a historical observation only if
  it is explicitly treated as time-bounded evidence rather than current truth.

Because the latest external platform state was not independently re-read in
this audit, it is unsafe to choose one value by inference. Family B is not ready
until an owner confirms the authoritative latest state and current-vs-historical
surfaces are classified.

## Shared-File Decision

For `agent-index.json`, select **Option C: hunk-level split**, with an additional
defer decision:

1. stage only the `development_constitution_v1_1` top-level object in Family A;
2. leave `commercial_trial_operator_status_v0_1.generated_at` unstaged;
3. leave the semantically neutral Alibaba key-order hunk unstaged;
4. do not place either residual hunk in Family B;
5. obtain explicit owner disposition for the residuals and Alibaba status sync.

Staging the whole file into A or B would falsify responsibility boundaries.
