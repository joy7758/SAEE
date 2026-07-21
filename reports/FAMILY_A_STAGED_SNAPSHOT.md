# Family A Staged Snapshot Evidence

Date: 2026-07-14
Phase: `0.5.2B-1 Family A Precise Staging`
Current HEAD: `f6ac41f4b068377e7778e8c3d83b99bd8382debc`

## Result

```text
FAMILY_A_STAGED=YES
STAGED_PATH_COUNT=12
STAGED_FULL_FILE_COUNT=11
STAGED_AGENT_INDEX_HUNK_COUNT=1
FAMILY_B_STAGED=false
REPORTS_STAGED=false
COMMIT_CREATED=false
```

## Hash Evidence

The requested hashes cover tracked Git diffs. Untracked reports are listed
separately and are not represented by `git diff --binary`.

```text
BEFORE_STAGING_HASH=dd5af9118723433bd48a082656be6a2f6558f026d00d56bd72fbb4782067104b
AFTER_STAGED_HASH=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
REMAINING_UNSTAGED_HASH=26793e678e976e4e6e7c63744f0cfd174ba4030fd580383f799642cfa8472cde
```

Commands represented:

```text
BEFORE_STAGING_HASH: git diff --binary | shasum -a 256
AFTER_STAGED_HASH: git diff --cached --binary | shasum -a 256
REMAINING_UNSTAGED_HASH: git diff --binary | shasum -a 256
```

## Staged Files

| File | Staging mode | Boundary |
|---|---|---|
| `.codex/current_state.md` | full file | Constitution governance |
| `.codex/rules.md` | full file | Constitution governance |
| `agent-index.json` | one hunk | `development_constitution_v1_1` only |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | full file | machine contract |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | full file | architecture governance |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | full file | canonical Constitution |
| `docs/product/SAEE_MODULE_REGISTRY.md` | full file | module ownership |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | full file | product architecture boundary |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | full file | recommendation gate |
| `schemas/saee-development-constitution.schema.v1.1.json` | full file | closed schema |
| `scripts/mainline_guard.py` | full file | mainline Constitution guard |
| `scripts/saee_development_constitution_smoke.py` | full file | deterministic validator |

Staged diff summary:

```text
12 files changed, 841 insertions(+), 5 deletions(-)
```

## Agent Index Hunk State

The cached diff for `agent-index.json` adds exactly one top-level object:

```text
INCLUDED=development_constitution_v1_1
EXCLUDED=alibaba_marketplace_assessment_delivery_bridge_v0_1 serialization hunk
EXCLUDED=commercial_trial_operator_status_v0_1.generated_at hunk
```

The staged `agent-index.json` parses successfully. Its canonical Constitution
object fingerprint is:

```text
development_constitution_v1_1_sha256=04ef9a338b161f3b7297b4d2cc07909546704af57a8fb445ddc2b2d81853ebff
```

The unstaged diff for `agent-index.json` still contains exactly the Alibaba
serialization hunk and the unrelated `generated_at` hunk. This proves those
residuals did not enter Family A.

## Excluded And Remaining Changes

The following Family B paths remain unstaged:

1. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json`
2. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md`
3. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json`
4. `cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md`
5. `scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py`

All Phase 0.5.2 audit, dry-run and staging-evidence reports remain untracked
and unstaged. No Alibaba, capability inventory, MCP, Agent Evidence source or
runtime, website, remote or Phase 1 path is staged.

## Validation Evidence

```text
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE=PASS
SAEE_CODEX_CONTEXT_CHECK=PASS
STAGED_AGENT_INDEX_JSON_PARSE=PASS
STAGED_PATH_SET_MATCH=PASS
HISTORY_ANCESTRY=PASS
```

The validators read the current working tree. Every Family A file they govern
is identical to its staged version, while the cached-path and hunk checks
separately prove the index boundary.

`git diff --cached --check` reports the two-space Markdown hard-line-break
syntax on lines 16-18 of the Constitution document as trailing whitespace.
Those spaces are intentional Markdown formatting already present in the
authorized file content. The staging task prohibited content edits, so no
rewrite was performed; the condition is recorded for commit review.

`scripts/mainline_guard.py` was not run. The approved plan requires it to run
against an isolated staged snapshot because reconciliation smokes may rewrite
local status artifacts even on PASS. No repair or workaround was attempted.
