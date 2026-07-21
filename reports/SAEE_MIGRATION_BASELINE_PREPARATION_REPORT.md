# SAEE Migration Baseline Preparation Report

```text
report_id=SAEE_MIGRATION_BASELINE_PREPARATION_REPORT
phase=Phase_0.5.6G-2
mode=BASELINE_PREPARATION_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
decision_truth_alignment=COMPLETE
g1_effective=false
```

本报告分析未来 Authority Migration 的可信起点，并设计 clean isolated worktree、immutable
input manifest、rollback references 和 baseline validation gate。它不创建 worktree、branch、
manifest 或 commit，不修改任何现有 dirty evidence，也不执行 migration 或 authority switch。

## 1. Executive Decision

No existing commit currently satisfies the migration baseline requirements. The repository's
committed candidates all predate the complete v1.1 authority family and Phase 0.5.6G-1 Decision
Truth Alignment surfaces. Therefore a baseline must not be forced from current history.

```text
BASELINE_PREPARATION_STATUS=COMPLETE
MIGRATION_BASELINE_COMMIT=UNRESOLVED
BASELINE_GATE=BLOCKED_PENDING_FUTURE_CLEAN_CLOSURE_COMMIT
CURRENT_WORKTREE_MODIFIED=false
WORKTREE_CREATED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
```

`CURRENT_WORKTREE_MODIFIED=false` means no pre-existing path, index entry or dirty evidence was
changed by this phase. The only new path permitted by this preparation is this report.

## 2. Baseline Source Analysis

### 2.1 Eligibility criteria

An eligible `MIGRATION_BASELINE_COMMIT` must be one immutable commit whose tree contains, at minimum:

1. a complete and internally consistent v1.1 historical/active authority family;
2. the accepted Phase 0.5.6G-1 Project Memory state and V2 namespace validator/tests;
3. the controlled SAEE / Agent Evidence integration mainline without staged-truth promotion;
4. canonical capability, product and MCP truth-source references with recorded digests;
5. approved preflight/migration preparation evidence required by G1;
6. no unrelated marketplace, runtime, adapter, formatting or other-task changes;
7. validators that pass without modifying a clean worktree.

It must also have a human-approved source lineage, exact path allowlist, assigned owner, independent
validation receipt and rollback reference.

### 2.2 Candidate commit matrix

| Candidate | Role/lineage | Clean committed tree | Required v1.1 family | G-1 Project Memory/validator/report | Decision |
|---|---|---:|---:|---:|---|
| `f6ac41f4b068377e7778e8c3d83b99bd8382debc` | current branch HEAD; Phase 0 governance/dogfooding lineage | yes | missing document, contract and schema from tree | missing | `SOURCE_ANCHOR_ONLY` |
| `e12f62a2cd8aa39f70c2ec48f3ffa1b8ba7c3b81` | earlier Codex identity alignment | yes | incomplete/missing from tree | missing | `TOO_OLD` |
| `d0b3dd796aff58557d0f45e4abcf170c4a7eda51` | clean idempotency-fix branch based on `00d8d0467` | yes | missing | missing | `PATCH_SOURCE_CANDIDATE_ONLY` |
| `18942ce16071390969e0814dc1f2fe0a0efed06d` | clean governance/idempotency integration commit | yes | missing | missing | `DIVERGENT_PATCH_SOURCE_ONLY` |
| `00d8d0467761fe044355aeb678f3cd12efc6c7cf` | current `main`; older marketplace-era lineage | yes | missing | missing | `TOO_OLD` |

Tree inspection confirmed that all five candidates contain `capability-package/manifest.json`, but
none contains these required current paths:

```text
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
agent-interface/governance/saee-development-constitution.v1.1.json
schemas/saee-development-constitution.schema.v1.1.json
governance/project-memory/v2-transition-decisions.md
scripts/saee_project_memory_check.py
reports/SAEE_DECISION_TRUTH_ALIGNMENT_EXECUTION_REPORT.md
```

`git log --all -- <required paths>` and `git ls-files` also show no committed history for the G-1
Project Memory/validator/report surfaces. Thus neither current HEAD nor another branch can be named
as the migration baseline.

### 2.3 Branch and worktree findings

| Existing worktree | HEAD | Status entries | Baseline use |
|---|---|---:|---|
| `/Users/zhangbin/Documents/SAEE` | `f6ac41f4b...` | 88 dirty entries | prohibited; current evidence worktree |
| `/private/tmp/saee-check-idempotency` | `d0b3dd796...` | 0 | prohibited; other-task worktree and incomplete lineage |
| `/private/tmp/saee-family-a-staged-review` | `f6ac41f4b...` | 56 | prohibited; dirty review worktree |
| `/private/tmp/saee-governance-idempotency-integration` | `18942ce16...` | 0 | prohibited; other-task divergent worktree |

The clean status of another worktree does not transfer ownership or baseline eligibility. Neither
`f6ac41f4b...` nor `18942ce16...` is an ancestor of the other; their merge base is
`85677aaadfaee3a7d7bc4197da21e1c9328c70d7`. Wholesale reuse would silently choose a lineage and
scope not approved for migration.

### 2.4 Future source strategy

The future Human Authority Owner must choose an exact composition, not an existing worktree:

1. nominate a committed lineage anchor, with `f6ac41f4b...` as the strongest current semantic/
   governance candidate but not yet a baseline;
2. review idempotency changes from `d0b3dd796...` / `18942ce16...` as content-addressed patch sources,
   not wholesale branch merges;
3. reconstruct only the approved v1.1 family, G-1 truth alignment and required preflight evidence in
   a new isolated worktree;
4. validate the reconstructed tree before requesting authorization to create a closure commit;
5. designate that new closure commit as `MIGRATION_BASELINE_COMMIT` only after independent PASS.

Until the source anchor, exact replay set and owner are approved, source selection remains unresolved.

```text
BASELINE_SOURCE_ANALYSIS=COMPLETE_NO_ELIGIBLE_EXISTING_COMMIT
CURRENT_HEAD_IS_BASELINE=false
OTHER_BRANCH_COMMIT_IS_BASELINE=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
```

## 3. Dirty Worktree Boundary

### 3.1 Current immutable observation

At task start:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
HEAD_TREE=def1f5fb06b8087a5c0fabd929be253f25faed67
BRANCH=feat/canonical-capability-inventory-routing-v1
STATUS_ENTRIES=88
INDEX_CHANGE_ENTRIES=12
WORKTREE_CHANGE_ENTRIES=20
UNTRACKED_ENTRIES=63
STATUS_SHA256=8310e4745f7d06b6a2af731abaa1ae6934f457f9922fa04c9ea719267bd1a181
STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
UNTRACKED_CONTENT_AGGREGATE_SHA256=25f7a452cb41165ca97677ce33ab77b3ae3a4e0b2f9e024cb2830cc4ef44dd31
```

Index/worktree/untracked counts are overlapping status dimensions and therefore do not sum to the
88 path entries.

### 3.2 Evidence classification

All current dirty content is `EXISTING_EVIDENCE`, not an approved migration input set.

| Category | Examples | Migration treatment |
|---|---|---|
| staged Family A candidate | v1.1 document/contract/schema/gate/smoke and authority-related files | preserve current index; do not commit/import wholesale; reconcile against latest approved content in a new worktree |
| G-1 decision truth | four Project Memory files, validator/test and execution report | required future baseline candidate inputs, but currently uncommitted; replay only by exact hashes |
| v2/preflight preparation | constitution-migration package and Phase 0.5 reports | candidate evidence inputs; each path requires explicit allowlist approval |
| Agent Evidence integration work | adapters, fixtures, schemas, services and tests | mainline evidence but not automatically part of an authority-only baseline; separate source/owner decision required |
| Alibaba/product work | marketplace drafts, product registry/schema and smoke | excluded by default; separate Family B truth surface |
| unrelated reports/scripts/tests | remaining dirty/untracked paths | excluded unless individually justified and approved |

No current dirty path may enter the future baseline merely because it is staged, important, recent or
present in a report. `approved_paths` and `excluded_paths` must enumerate exact paths; globs and
directory-level authorization are invalid.

### 3.3 Prohibited handling

```text
GIT_CLEAN_ALLOWED=false
GIT_RESET_ALLOWED=false
GIT_RESTORE_ALLOWED=false
GIT_STASH_ALLOWED=false
GIT_REBASE_ALLOWED=false
CURRENT_INDEX_REWRITTEN=false
CURRENT_DIRTY_FILES_DELETED=false
CURRENT_DIRTY_CONTENT_USED_WHOLESALE=false
```

The main worktree stays as historical evidence. Content needed in the future baseline is copied only
through a separately approved content-addressed patch/commit process in a new worktree; the source
worktree itself is never normalized into the baseline.

```text
DIRTY_WORKTREE_BOUNDARY=FROZEN_EXISTING_EVIDENCE
CURRENT_WORKTREE_MODIFIED=false
```

## 4. Migration Worktree Design

### 4.1 Candidate identity

```text
future_branch=codex/saee-v2-authority-migration-v2-0
future_worktree=<new_nonexistent_human_approved_path>
base_source_commit=<full_40_character_human_approved_hash>
creation_authorized=false
```

The future path must not be the current repository, any `/private/tmp/saee-*` worktree listed above,
or any pre-existing directory. Branch and worktree creation require a new explicit Git authorization.

### 4.2 Future construction sequence

1. Human Authority Owner approves the source anchor, exact content-addressed replay list, excluded
   list, executor, validator and worktree path.
2. Executor proves the path and branch do not exist, then creates the new worktree from the full
   approved source hash.
3. Evidence Recorder captures Git version, command, timestamp, source commit/tree and clean status.
4. Executor applies only approved commits/patches in the declared order; no merge of another
   worktree and no copy of the current directory.
5. Each applied input is checked against its approved SHA-256 and owner/source record.
6. Reconstruct the complete v1.1 family and G-1 truth state without creating any v2 authority-family
   file or pointer change.
7. Run validation on the uncommitted candidate and prove no validator changes status.
8. Human separately authorizes one closure commit after reviewing the exact diff.
9. Independent Validator resolves the new full commit from scratch, checks its tree and reruns the
   baseline gate.
10. Only then record the commit as `MIGRATION_BASELINE_COMMIT`.

### 4.3 Required worktree invariants

```text
SEPARATE_PATH=true
APPROVED_SOURCE_COMMIT=true
UNRELATED_CHANGE_COUNT=0
WORKTREE_CLEAN_BEFORE=true
WORKTREE_CLEAN_AFTER=true
ACTIVE_POINTER_CHANGE=false
V2_AUTHORITY_FAMILY_CREATED=false
CURRENT_WORKTREE_IMPACT=NONE
ROLLBACK_REFERENCE=MIGRATION_BASELINE_COMMIT
```

These are future acceptance values, not current facts.

```text
WORKTREE_DESIGN=COMPLETE_NOT_CREATED
WORKTREE_CREATED=false
```

## 5. Immutable Input Manifest Design

### 5.1 Manifest role and timing

The manifest is generated after a future clean closure commit is independently validated and before
G1 human reconfirmation or Commit A. It is a detached content-addressed evidence artifact outside the
migration worktree to avoid a commit self-reference and an untracked sidecar.

It references canonical sources and does not become a second capability/product/MCP truth source.

### 5.2 Required fields

| Field | Required content |
|---|---|
| `manifest_version` | closed format version |
| `authorization_id` | future one-use G1 authorization ID |
| `baseline_commit` | full `MIGRATION_BASELINE_COMMIT` |
| `baseline_tree` | Git tree hash of baseline commit |
| `parent_commit` | direct parent of baseline commit |
| `source_lineage` | anchor, replayed commits/patch IDs, order and owners |
| `approved_paths` | exact sorted path allowlist; no globs |
| `excluded_paths` | exact dirty/other-task paths excluded from baseline |
| `sha256` | per-file raw SHA-256 and aggregate approved-path digest |
| `capability_digest` | raw source hash plus canonical JSON digest of canonical inventory |
| `product_digest` | raw/canonical digest of authoritative product registry |
| `mcp_digest` | raw/canonical digest of authoritative MCP registry/projection |
| `authority_family_digest` | v1.1 document/contract/schema/gate/validator hashes |
| `project_memory_digest` | G-1 accepted Project Memory aggregate digest |
| `validator_results` | command, executable hash/version, exit code and output hash |
| `rollback_reference` | baseline commit/tree and acceptance rule |
| `owner` | baseline owner, generator, retention owner and approver IDs |
| `roles` | executor, independent validator, rollback owner and evidence recorder IDs |
| `timestamp` | timezone-qualified generation timestamp |
| `non_claims` | no activation, capability/product/MCP/ecosystem/production effect |

### 5.3 Planning-only digest observations

These current-worktree values are observations for later comparison, not baseline digests:

```text
capability_manifest_raw_sha256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
canonical_inventory_canonical_json_sha256=33085f918206142edead466f086cad0d4f99b13cf9ac73f2750c31f452a6ad46
product_registry_raw_sha256=62c9ee638a4e763e60d2290cdf6fa2bbeabf93373ced8fa4af084203146a316d
product_registry_canonical_json_sha256=aed85e2c765aaf14211c0b4adebe80d81014e0689a075bfd4116374124eb5308
mcp_registry_raw_sha256=fdeda93c44104c61efcdcea2ea2703a919630a68b2af96b12438d45834258a76
mcp_registry_canonical_json_sha256=52fde49b1da494ec670e649c4e7b6c707d4ac250403de8271bb5a065172ea635
```

Future baseline digests must be recomputed from the clean closure commit. Current dirty values cannot
be copied into the manifest as if they were validated baseline facts.

### 5.4 Generation and verification roles

```text
manifest_generator=UNASSIGNED_MIGRATION_EXECUTOR
manifest_verifier=UNASSIGNED_INDEPENDENT_VALIDATOR
manifest_owner=UNASSIGNED_HUMAN_AUTHORITY_OWNER
manifest_retention=UNASSIGNED_EVIDENCE_RECORDER
```

Phase 0.5.6G-3 must assign stable role identifiers before generation. Independent Validator must
reconstruct all hashes from the baseline commit and reject stale, ambiguous, globbed, duplicate or
self-referential inputs.

```text
MANIFEST_DESIGN=COMPLETE_NOT_CREATED
IMMUTABLE_MANIFEST_CREATED=false
IMMUTABLE_MANIFEST_VERIFIED=false
```

## 6. Rollback Reference Design

Three references have distinct lifecycles:

| Reference | Definition time | Purpose | Current state |
|---|---|---|---|
| baseline rollback reference | after clean closure commit PASS | restore result tree after failed Commit A/B | `UNRESOLVED` |
| pre-switch reference | after Commit B PASS and before G2/Commit C | restore all active pointers to v1.1 | `NOT_APPLICABLE_YET` |
| correction commit reference | after an authorized rollback is actually created | record non-destructive recovery commit and result tree | `NOT_CREATED` |

Future required fields:

```text
BASELINE_ROLLBACK_COMMIT=MIGRATION_BASELINE_COMMIT
BASELINE_ROLLBACK_TREE=<baseline_tree>
PRE_SWITCH_COMMIT=<defined_only_after_commit_b>
CORRECTION_COMMIT=<defined_only_if_rollback_executes>
ROLLBACK_METHOD=AUTHORIZED_CORRECTION_OR_REVERT_COMMIT
DESTRUCTIVE_RESET_ALLOWED=false
HISTORY_REWRITE_ALLOWED=false
FORCE_PUSH_ALLOWED=false
V2_EVIDENCE_DELETION_ALLOWED=false
```

The correction/revert result must equal the approved target tree and rerun all required validators.
References are full hashes, not mutable branch names.

```text
ROLLBACK_REFERENCE_DESIGN=COMPLETE
BASELINE_ROLLBACK_REFERENCE=UNRESOLVED
PRE_SWITCH_REFERENCE=NOT_APPLICABLE_YET
CORRECTION_COMMIT_REFERENCE=NOT_CREATED
```

## 7. Baseline Validation Gate

### 7.1 Future required checks

```text
WORKTREE_CLEAN=true
BASELINE_COMMIT_DEFINED=true
BASELINE_TREE_DEFINED=true
SOURCE_LINEAGE_HUMAN_APPROVED=true
APPROVED_PATHS_HASH_VERIFIED=true
EXCLUDED_PATHS_HASH_VERIFIED=true
MANIFEST_VERIFIED=true
CAPABILITY_DIGEST_RECORDED=true
PRODUCT_DIGEST_RECORDED=true
MCP_DIGEST_RECORDED=true
ROLLBACK_REFERENCE_READY=true
ROLES_ASSIGNED=true
VALIDATORS_PASS=true
VALIDATORS_NO_MUTATION=true
UNRELATED_CHANGE_COUNT=0
```

Validator set:

```text
python3 scripts/saee_project_memory_check.py
python3 -m unittest tests/test_project_memory.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
git diff --check
```

`scripts/mainline_guard.py` is added only after its dependencies and no-mutation behavior are proven
on the selected lineage. Any missing assertion, mutation, stale hash or non-reproducible PASS blocks
the baseline.

### 7.2 Current gate result

```text
WORKTREE_CLEAN=false
BASELINE_COMMIT_DEFINED=false
MANIFEST_VERIFIED=false
CAPABILITY_DIGEST_RECORDED=false
PRODUCT_DIGEST_RECORDED=false
MCP_DIGEST_RECORDED=false
ROLLBACK_REFERENCE_READY=false
ROLES_ASSIGNED=false
VALIDATORS_PASS=NOT_RUN_ON_FUTURE_BASELINE
BASELINE_GATE=BLOCKED
```

Current validators may pass on the dirty evidence worktree, but that does not validate a nonexistent
baseline commit.

```text
BASELINE_GATE=DESIGNED_CURRENTLY_BLOCKED
```

## 8. Complexity Encapsulation Check

Baseline governance remains an internal safety mechanism. A future reviewer-facing envelope may
expose only:

```text
baseline.commit
baseline.tree
baseline.clean
source_lineage.status
manifest.sha256
digests.capability_product_mcp
rollback.reference
validation.status
reason_codes[]
evidence_refs[]
```

The simple envelope must link to complete evidence and cannot hide excluded paths, source lineage,
validator failures or staged truth. This phase does not change any user, developer, Agent, API, MCP
or product interface.

```text
INTERNAL_BASELINE_COMPLEXITY=ENCAPSULATED_NOT_HIDDEN
EXTERNAL_INTERFACE_CHANGED=false
AUTHORITY_CHANGED=false
CAPABILITY_CHANGED=false
PRODUCT_CHANGED=false
MCP_CHANGED=false
```

## 9. Risks and Human Review Questions

| Risk | Current control | Human decision still required |
|---|---|---|
| selecting a convenient but incomplete commit | candidate matrix and required-path tree inspection | approve source anchor/composition |
| stealing another task's clean worktree | explicit ownership/path prohibition | approve a new unique worktree path |
| importing the current dirty tree wholesale | dirty snapshot/digests and default exclusion | approve exact replay paths and hashes |
| losing idempotency fixes | treat `d0b3dd796...` / `18942ce16...` as patch sources only | approve exact patch subset/order |
| manifest becoming a second truth source | reference-only digest design | approve schema/retention boundary |
| self approval | roles remain unassigned | assign separate owner/executor/validator/rollback/recorder roles in G-3 |
| false PASS on dirty state | future clean/no-mutation gate | approve independent validation environment |

Human review must decide whether `f6ac41f4b...` is the source anchor and which exact idempotency and
current approved artifacts are replayed. It must not approve `MIGRATION_BASELINE_COMMIT` until the
future closure commit exists and passes the gate.

## 10. Final Status

```text
BASELINE_PREPARATION_STATUS=COMPLETE
BASELINE_SOURCE_ANALYSIS=COMPLETE_NO_ELIGIBLE_EXISTING_COMMIT
DIRTY_WORKTREE_BOUNDARY=FROZEN_EXISTING_EVIDENCE
WORKTREE_DESIGN=COMPLETE_NOT_CREATED
MANIFEST_DESIGN=COMPLETE_NOT_CREATED
ROLLBACK_REFERENCE_DESIGN=COMPLETE
BASELINE_GATE=DESIGNED_CURRENTLY_BLOCKED
MIGRATION_BASELINE_COMMIT=UNRESOLVED
CURRENT_WORKTREE_MODIFIED=false
WORKTREE_CREATED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
NEXT_ACTION=HUMAN_REVIEW_OF_BASELINE_PREPARATION
```

## 11. Validation and Scope Boundary

Task baseline before report creation:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=88
BASELINE_STATUS_SHA256=8310e4745f7d06b6a2af731abaa1ae6934f457f9922fa04c9ea719267bd1a181
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

Required validation commands:

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
git diff --check
```

Only this preparation report may be added. No pre-existing path may change.

Final validation and scope result:

```text
SAEE_PROJECT_MEMORY_CHECK=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
GIT_DIFF_CHECK=PASS
FINAL_STATUS_ENTRIES=89
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=88
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=8310e4745f7d06b6a2af731abaa1ae6934f457f9922fa04c9ea719267bd1a181
AUDIT_INPUT_HASHES_UNCHANGED=6/6_GROUPS
ONLY_NEW_STATUS_ENTRY=reports/SAEE_MIGRATION_BASELINE_PREPARATION_REPORT.md
PRE_EXISTING_PATHS_MODIFIED=0
STAGED_TASK_FILES=0
WORKTREE_COUNT_BEFORE=4
WORKTREE_COUNT_AFTER=4
BRANCH_COUNT_BEFORE=4
BRANCH_COUNT_AFTER=4
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
PR_CREATED=false
```
