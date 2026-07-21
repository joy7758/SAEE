# SAEE Baseline Reconstruction Preparation

```text
report_id=SAEE_BASELINE_RECONSTRUCTION_PREPARATION
phase=Phase_0.5.6G-4
mode=RECONSTRUCTION_DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
decision_truth_alignment=PASS
migration_baseline_commit=UNRESOLVED
g1_effective=false
phase_0_5_7a_authorized=false
```

本报告设计如何从当前复杂历史中重建一个 clean、可复核、可回滚的 Migration
Baseline。它不选择或创建 baseline commit，不创建 branch/worktree，不执行 replay、merge、
cherry-pick、stage、commit、migration 或 authority switch，也不改变现有 dirty worktree。

## 1. Executive Boundary

当前不存在可以直接指定为 `MIGRATION_BASELINE_COMMIT` 的 commit。原因不是 Git 对象不
干净，而是任何现有 commit 都没有同时包含：

1. 完整且一致的 v1.1.1 active/historical authority family；
2. 已执行的 Phase 0.5.6G-1 Decision Truth Alignment；
3. 可重复、只读的 idempotent mainline validation；
4. 经批准的精确 scope、role binding、rollback reference 与 immutable manifest。

当前 HEAD 是可追溯的治理 lineage anchor，但不是 baseline。现有 idempotency branches
提供了可验证的 patch provenance，但它们不是可整支采用的迁移主线。当前 dirty tree 是
历史证据，不是重建输入集合。

```text
BASELINE_RECONSTRUCTION_PREPARATION_STATUS=COMPLETE
SOURCE_LINEAGE_ANALYSIS=COMPLETE_RECONSTRUCTION_REQUIRED
BASELINE_SCOPE=DESIGNED_FAIL_CLOSED
EXCLUSION_RULES=DESIGNED_FAIL_CLOSED
WORKTREE_RECONSTRUCTION_DESIGN=COMPLETE_NOT_EXECUTED
BASELINE_VALIDATION_GATE=DESIGNED_NOT_RUN
MIGRATION_BASELINE_COMMIT=UNRESOLVED
WORKTREE_CREATED=false
BASELINE_CREATED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
```

## 2. Source Lineage Analysis

### 2.1 Immutable Git observations

```text
current_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
current_head_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
current_branch=feat/canonical-capability-inventory-routing-v1
local_branch_count=4
registered_worktree_count=4
configured_remote_count=0
tag_count=0
```

Relevant topology:

```text
00d8d0467761  Record Alibaba Marketplace submission review state
├── d0b3dd796aff  idempotency repair
│    └── 18942ce16071  merge with capability governance at 85677aaa
└── ... capability governance ... 85677aaadfae
     └── 307cebd6c1a6  Phase 0 governance
          └── be7b87ff2a7a  governance stabilization
               └── e12f62a2cd8a  Codex/v1.1 identity alignment
                    └── f6ac41f4b068  dogfooding/current HEAD
```

`f6ac41f4...` and `18942ce1...` are divergent descendants of
`85677aaadfaee3a7d7bc4197da21e1c9328c70d7`; neither is the ancestor of the
other. `d0b3dd79...` and current HEAD share `00d8d046...` as merge base.

### 2.2 Candidate classification

| Candidate | Evidence role | Classification | Baseline decision |
|-|-|-|-|
| `f6ac41f4b068377e7778e8c3d83b99bd8382debc` | current Phase 0 governance/Codex/dogfooding lineage tip | `ACCEPTABLE_SOURCE` | recommended lineage anchor only; incomplete, not baseline |
| `307cebd6c1a6072958264b35eb2c38edd7195eb2` → `f6ac41f4...` | four approved governance commits after `85677aaa...` | `ACCEPTABLE_SOURCE` | preserve as existing ancestry through current HEAD; do not squash or rewrite |
| `d0b3dd796aff58557d0f45e4abcf170c4a7eda51` | verified clean/idempotent validation repair | `ACCEPTABLE_SOURCE` | exact patch provenance only; wholesale branch adoption prohibited |
| `18942ce16071390969e0814dc1f2fe0a0efed06d` | verified integration of idempotency repair with capability governance at `85677aaa...` | `ACCEPTABLE_SOURCE` | semantic oracle and patch verification source only; not migration baseline |
| `e12f62a2cd8aa39f70c2ec48f3ffa1b8ba7c3b81` | committed v1.1 identity routing | `ACCEPTABLE_SOURCE` | valid historical ancestor, but not complete v1.1 family |
| working-tree v1.1.1 authority family | current active authority content, not committed; staged snapshot is older 1.1.0 | `UNKNOWN_SOURCE` | exact working bytes/hunks require human approval and independent reconciliation |
| Phase 0.5.6G-1 Project Memory/validator/report bytes | executed and locally validated, but uncommitted | `UNKNOWN_SOURCE` | candidate baseline inputs only after exact-hash approval |
| `00d8d0467761fe044355aeb678f3cd12efc6c7cf` / `main` | marketplace-era commit and current main pointer | `EXCLUDED_SOURCE` | too old and wrong semantic source for reconstruction |
| `/private/tmp/saee-check-idempotency` | other-task worktree at `d0b3dd79...` | `EXCLUDED_SOURCE` | never reuse the worktree; commit bytes remain separately addressable |
| `/private/tmp/saee-governance-idempotency-integration` | other-task worktree at `18942ce1...` | `EXCLUDED_SOURCE` | never reuse the worktree; use commit/tree evidence only |
| `/private/tmp/saee-family-a-staged-review` | dirty forensic worktree | `EXCLUDED_SOURCE` | retained evidence; known mainline mutation; never normalize into baseline |
| current `/Users/zhangbin/Documents/SAEE` dirty tree/index | 90 status entries across multiple programs | `EXCLUDED_SOURCE` | never copy, stash, clean, reset or import wholesale |
| any unlisted/experimental/future ref | ownership and validation unknown | `UNKNOWN_SOURCE` | fail closed until full hash, owner, scope and validation are established |

`ACCEPTABLE_SOURCE` means acceptable for the bounded role shown in the table. It does not mean the
commit is a baseline, grants G1, or permits branch/worktree creation.

### 2.3 Required-path completeness

Current HEAD and every other existing branch tip lack the complete committed Pre-G1 input set. At
current HEAD these required paths are absent from the commit tree and have no committed path history:

```text
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
agent-interface/governance/saee-development-constitution.v1.1.json
schemas/saee-development-constitution.schema.v1.1.json
governance/project-memory/v2-transition-decisions.md
scripts/saee_project_memory_check.py
reports/SAEE_DECISION_TRUTH_ALIGNMENT_EXECUTION_REPORT.md
```

Therefore clean Git status on an existing branch is insufficient. `MIGRATION_BASELINE_COMMIT` must
be a future, independently validated closure commit.

### 2.4 Recommended reconstruction source model

The recommended design preserves the current approved governance ancestry:

```text
lineage_anchor=f6ac41f4b068377e7778e8c3d83b99bd8382debc
idempotency_patch_provenance=d0b3dd796aff58557d0f45e4abcf170c4a7eda51
idempotency_integration_oracle=18942ce16071390969e0814dc1f2fe0a0efed06d
closure_input=v1.1.1_family_plus_decision_truth_plus_approved_preflight_evidence
future_result=<one_human_authorized_closure_commit>
```

The future executor must reconstruct the idempotency semantics on top of `f6ac41f4...` by exact,
content-addressed path/hunk composition. It must not merge or cherry-pick either other-task branch
wholesale. `README.md`, `llms.txt`, `agent-index.json` and `scripts/mainline_guard.py` are semantic
collision points; taking one side wholesale would either lose current governance/mainline rules or
regress caller-worktree isolation.

An alternative starting at `18942ce1...` and replaying `307cebd6...` through `f6ac41f4...` remains
`UNKNOWN_SOURCE` until a separate read-only conflict simulation and human comparison show it is
strictly safer. This report does not select that alternative.

### 2.5 Ancestry preservation versus migration scope

`00d8d046...` and earlier commercial commits remain ancestors of both candidate histories. Historical
safety prohibits deleting or rewriting them. Excluding Alibaba therefore means:

- no Alibaba path or semantic change enters the reconstruction delta;
- inherited Alibaba tree objects remain byte-identical to the selected anchor;
- they are not cited as authority-migration input or current external truth;
- their external status remains separately governed and may remain `UNKNOWN`/historical;
- the manifest records their unchanged inherited-tree digest where needed to prove non-interference.

It does not mean manufacturing an orphan history or deleting old commits.

```text
SOURCE_LINEAGE_ANALYSIS=COMPLETE_RECONSTRUCTION_REQUIRED
RECOMMENDED_LINEAGE_ANCHOR=f6ac41f4b068377e7778e8c3d83b99bd8382debc
RECOMMENDED_LINEAGE_ANCHOR_APPROVED=false
EXISTING_COMMIT_ELIGIBLE_AS_BASELINE=false
CURRENT_HEAD_IS_BASELINE=false
OTHER_BRANCH_IS_BASELINE=false
```

## 3. Baseline Scope

### 3.1 Scope layers

The future closure must use an exact path/hunk allowlist. Directory globs and “related files” are
invalid. Candidate layers are:

#### Layer L0 — Inherited committed anchor

All paths inherited from `f6ac41f4...` are immutable background. Only paths explicitly listed in
L1-L5 may differ from that anchor. Every other path must have the same Git object OID as the anchor.

#### Layer L1 — Idempotency stabilization

Candidate source is the exact repair semantics from `d0b3dd79...`, checked against the verified
integration at `18942ce1...`. The future allowlist must enumerate only the files and hunks required
to make validation read-only, isolated and repeatable. It must preserve:

```text
normal_check_external_provider_evidence=NOT_REQUIRED
strict_provider_evidence_missing=NOT_AVAILABLE
caller_worktree_mutation=false
generated_artifact_validation=ISOLATED
```

Unrelated documentation, commercial state, capability facts or integration-branch reports do not
enter merely because they exist in those commits.

#### Layer L2 — Complete active v1.1.1 authority family

The future candidate may include the already approved v1.1.1/mainline correction, reconciled from
the working tree rather than the superseded 1.1.0 staged bytes:

```text
.codex/current_state.md
.codex/rules.md
AGENTS.md                          # exact v1.1/mainline hunk only
agent-index.json                   # exact development_constitution_v1_1 hunk only
agent-interface/governance/saee-development-constitution.v1.1.json
docs/architecture/IMMUNE_GOVERNANCE_PLANE.md
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
docs/product/SAEE_MODULE_REGISTRY.md
docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md
docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md
llms.txt                           # exact v1.1/mainline discovery hunk only
schemas/saee-development-constitution.schema.v1.1.json
scripts/mainline_guard.py          # semantic merge with L1; never whole-side overwrite
scripts/saee_development_constitution_smoke.py
```

The Family A index digest `31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f`
is historical evidence only. It contains v1.1.0 and is superseded by the unstaged v1.1.1 correction.
No future replay may silently use the index blob for a path whose working-tree content differs.

#### Layer L3 — Decision Truth Alignment and Project Memory

The baseline must contain the complete accepted Project Memory family, not only the four files
changed by G-1, because its validator resolves the family as one closed decision surface:

```text
governance/project-memory/README.md
governance/project-memory/active-questions.md
governance/project-memory/current-state.md
governance/project-memory/decision-change-proposals/DCP-001-mainline-and-three-customer-versions.md
governance/project-memory/decision-log.md
governance/project-memory/frozen-decisions.md
governance/project-memory/memory-policy.md
governance/project-memory/rejected-options.md
governance/project-memory/v2-transition-decisions.md
scripts/saee_project_memory_check.py
tests/test_project_memory.py
reports/SAEE_DECISION_TRUTH_ALIGNMENT_EXECUTION_REPORT.md
```

Required state remains:

```text
V2_F_001_THROUGH_V2_F_005=APPROVED_DESIGN_DIRECTION
V2_P_001_THROUGH_V2_P_003=APPROVED_DESIGN_DIRECTION
V2_AUTHORITY_STATUS=INACTIVE
FROZEN_DECISION_CREATED=false
ACTIVE_AUTHORITY_CREATED=false
```

#### Layer L4 — Approved governance truth correction

The current v1.1.1 mainline correction requires the already reviewed target-version registry
alignment so governance validation does not preserve a contradiction. It may enter only as a
separately approved pre-baseline stabilization input with exact hashes and the established
`target_not_implemented`/non-production boundaries. It is not a new migration product change.

Candidate paths:

```text
governance/registry/product-registry.json
governance/schemas/product.schema.json
scripts/saee_governance_registry_check.py
tests/test_governance_registry.py
reports/SAEE_PRODUCT_REGISTRY_MAINLINE_CORRECTION.md
```

If the Human Authority Owner does not accept this prior correction as a baseline input, the baseline
must remain blocked; the executor may not invent a different product disposition.

#### Layer L5 — Preparation evidence

The following reports are candidate historical evidence inputs, not normative authority or a second
truth source:

```text
reports/SAEE_AUTHORITY_MIGRATION_EXECUTION_AUTHORIZATION_PACKAGE.md
reports/SAEE_PRE_G1_CLOSURE_EXECUTION_PREPARATION.md
reports/SAEE_DECISION_TRUTH_ALIGNMENT_EXECUTION_REPORT.md
reports/SAEE_MIGRATION_BASELINE_PREPARATION_REPORT.md
reports/SAEE_ROLE_ASSIGNMENT_AND_IMMUTABLE_MANIFEST_PREPARATION.md
reports/SAEE_BASELINE_RECONSTRUCTION_PREPARATION.md
```

Human review may choose to keep some or all as detached content-addressed evidence rather than
baseline-tree files. Their location does not change their non-authoritative status.

### 3.2 Explicitly forbidden baseline effects

```text
V2_AUTHORITY_FAMILY_CREATED=false
V2_SUCCESSOR_ACTIVATED=false
ACTIVE_POINTER_SWITCH=false
CAPABILITY_FACT_CHANGE=false
PRODUCT_IMPLEMENTATION_OR_LAUNCH_CHANGE=false
MCP_CHANGE=false
APPLICATION_RUNTIME_CHANGE=false
ECOSYSTEM_STATUS_CHANGE=false
EXTERNAL_CLAIM_CHANGE=false
```

The exact Commit A family paths from the authorization package must be absent from the baseline.
The existing `governance/constitution-migration/v2-authority-successor-draft.md` is preparation
evidence and must not be promoted into the baseline as a v2 authority-family member. It may be
retained outside the migration tree with a recorded hash.

`capability-package/manifest.json` remains the sole capability fact source. Its expected raw
SHA-256 at the observed planning state is:

```text
fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
```

The future baseline digest must be recomputed from the committed baseline tree; this planning hash
cannot be copied forward as a validated baseline fact.

### 3.3 Mainline preservation boundary

The controlled SAEE / Agent Evidence integration remains the program mainline. The authority
reconstruction lane supports it and may not replace it. Current uncommitted adapter/runtime/schema
work is not imported into this authority-only closure because application/runtime changes are
forbidden here. It must remain preserved in the existing evidence worktree and receive its own
authorized history closure.

The future migration branch cannot be declared canonical product mainline merely because its
authority baseline passes. Any change in the integration mainline after the baseline hash is bound
invalidates G1 and requires rebase/reconstruction review plus a new manifest.

```text
PROGRAM_MAINLINE_PRESERVED=true
AUTHORITY_GOVERNANCE_DISPLACES_MAINLINE=false
CURRENT_AGENT_EVIDENCE_RUNTIME_INPUT_INCLUDED=false
```

## 4. Exclusion Rules

### 4.1 Mandatory exclusion inventory

| Excluded source/change | Reason | Required proof |
|-|-|-|
| current dirty worktree/index wholesale | 12 staged, 20 unstaged tracked and 82 untracked dimensions span unrelated programs | status, index patch and dirty-content digests unchanged |
| superseded Family A 1.1.0 index bytes | no longer the complete active v1.1.1 candidate | compare index blob and approved working hash per path |
| Alibaba repair paths and SEO smoke | unresolved external/current-vs-historical truth and Family B ownership | zero Alibaba paths in reconstruction diff; inherited OIDs unchanged |
| `agent-index.json` commercial timestamp/key-order hunks | mixed responsibility and generated noise | hunk-level after-hash; capability ledger and Alibaba objects unchanged |
| `fix/check-idempotency-v1` worktree/branch wholesale | other-task ownership and older base | use only exact approved patch semantics |
| `integration/governance-on-idempotent-checks-v1` worktree/branch wholesale | divergent from Phase 0 governance after `85677aaa...` | use as validation oracle only |
| detached Family A forensic worktree | known 45-path mutation and dirty evidence | no path copied from worktree location |
| current Agent Evidence adapters/services/tests | mainline work but application/runtime scope outside this baseline | preserve separately; zero runtime paths in reconstruction diff |
| v2 successor draft/Commit A family | would pre-create the authority family before G1 | absence check against exact Commit A path set |
| v2 pointer changes/Commit C hunks | activation not authorized | every active pointer resolves to v1.1 |
| capability, MCP, marketplace, website or external state | separate truth/authorization domains | authoritative digests unchanged |
| generated, cache, ignored output, credentials or local Provider evidence | non-portable, non-source, potentially sensitive | clean checkout and ignored/untracked count zero |
| any unknown branch/ref/path | no approved owner, provenance or scope | default `UNKNOWN_SOURCE` and stop |

Exact observed Alibaba paths excluded from the reconstruction delta:

```text
cloud-entry-package/alibaba-cloud-marketplace-v0.1/listing-draft.json
cloud-entry-package/alibaba-cloud-marketplace-v0.1/product-detail-draft.md
cloud-entry-package/alibaba-cloud-marketplace-v0.1/seo-listing-copy.v0.1.json
cloud-entry-package/alibaba-cloud-marketplace-v0.1/service-user-guide.md
scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py
```

### 4.2 Exclusion semantics

The future manifest must expand every category into exact sorted paths and expected anchor object
OIDs. Globs are useful only in this design narrative; they are invalid in execution authorization.

```text
GIT_RESET_ALLOWED=false
GIT_CLEAN_ALLOWED=false
GIT_STASH_ALLOWED=false
GIT_RESTORE_ALLOWED=false
HISTORY_REWRITE_ALLOWED=false
FORCE_PUSH_ALLOWED=false
CURRENT_DIRTY_CONTENT_DELETED=false
OTHER_TASK_WORKTREE_REUSED=false
```

## 5. Worktree Reconstruction Design

### 5.1 Future identity

```text
future_branch=codex/saee-v2-authority-migration-v2-0
future_worktree=<new_nonexistent_human_approved_path>
source_commit=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
creation_authorized=false
```

The path must not be the current repository, any registered `/private/tmp/saee-*` worktree, an
existing directory or a location owned by another task. Branch and worktree creation require new
explicit authorization after human review of this design.

### 5.2 Future fail-closed sequence

1. Human Authority Owner approves the exact lineage anchor, path/hunk allowlist, excluded-object
   inventory, role records, worktree path and closure-commit rule.
2. Evidence Recorder freezes full hashes for the anchor, `d0b3dd79...`, `18942ce1...`, every
   uncommitted approved input and every detached preparation artifact.
3. Executor proves the future branch/path do not exist, then creates the isolated worktree only
   under a separate Git authorization.
4. Prove the new worktree begins clean at the exact anchor commit/tree.
5. Apply only the approved idempotency semantics. Do not merge/cherry-pick an entire other-task
   branch. Resolve collision paths by the expected semantic assertions and exact after hashes.
6. Apply the reconciled v1.1.1 authority family, approved registry correction and G-1 Project
   Memory inputs. No current-directory copy, directory glob or index reuse is permitted.
7. Add only the human-approved preparation evidence disposition. Keep v2 successor/family and
   pointer artifacts outside the baseline.
8. Compare the candidate diff to the exact allowlist and anchor object inventory. Any extra path,
   mode change, generated timestamp or missing expected hash stops reconstruction.
9. Run the complete validation gate on the uncommitted candidate and prove no mutation.
10. Human reviews the exact final tree/diff and separately authorizes one baseline closure commit.
11. Independent Validator resolves the new commit from its full hash in a fresh clean location,
    recomputes every digest and reruns the gate.
12. Only an independent PASS plus explicit human designation may set the full hash as
    `MIGRATION_BASELINE_COMMIT`.

No step above is executed by this report.

### 5.3 Collision controls

| Collision surface | Risk | Required future resolution |
|-|-|-|
| `scripts/mainline_guard.py` | current v1.1 smoke addition can overwrite idempotency isolation | semantic composition; require both v1.1 checks and caller-isolation contract |
| `README.md` / `llms.txt` | idempotency routing and governance/mainline discovery can displace each other | explicit token set plus exact after-hash |
| `agent-index.json` | Constitution hunk, Alibaba formatting/timestamp and capability projection coexist | structured/hunk-level composition; canonical capability ledger unchanged |
| `.codex/*` / `AGENTS.md` | active v1.1 rules can be confused with later v2 switch | v1.1-only pointer assertion; no v2 selector |
| product registry family | approved target correction can be mistaken for product launch | retain `target_not_implemented`, false launch/customer/production claims |
| Project Memory | design approval can be mistaken for authority activation | validator rejects `FROZEN`/`ACTIVE_AUTHORITY` and keeps G1 false |

### 5.4 Clean-state definition

`clean` means more than empty `git status`:

```text
HEAD_EQUALS_APPROVED_FULL_HASH=true
HEAD_TREE_EQUALS_APPROVED_TREE=true
INDEX_EQUALS_HEAD=true
TRACKED_WORKTREE_EQUALS_INDEX=true
UNTRACKED_PATH_COUNT=0
IGNORED_GENERATED_INPUT_COUNT=0
SUBMODULE_OR_GITLINK_STATE=DECLARED
VALIDATORS_NO_MUTATION=true
UNRELATED_DIFF_PATH_COUNT=0
```

A disposable clone that omits required untracked input is not a valid proof that uncommitted
Project Memory or authority files exist. Conversely, a dirty worktree whose validators pass is not
a valid baseline.

```text
WORKTREE_RECONSTRUCTION_DESIGN=COMPLETE_NOT_EXECUTED
WORKTREE_CREATED=false
BRANCH_CREATED=false
BASELINE_CREATED=false
```

## 6. Baseline Validation Gate

### 6.1 Required future commands

At minimum:

```text
python3 scripts/saee_project_memory_check.py
python3 -m unittest tests/test_project_memory.py
python3 scripts/saee_governance_registry_check.py
python3 -m unittest tests/test_governance_registry.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
git diff --check
```

After idempotency integration is present and hash-verified:

```text
make check
python3 scripts/mainline_guard.py
```

Both must run twice with the same exit status and deterministic output hash where the contract
requires determinism. Repository status and full-tree content snapshots must be identical before
and after every run.

### 6.2 Authority consistency pre-check

The formal `scripts/saee_authority_consistency_check.py` belongs to future Commit A and therefore
must not be fabricated in the baseline. Before Commit A, an independently retained, hash-pinned
read-only pre-check must assert directly over the baseline tree:

```text
ALL_ACTIVE_AUTHORITY_POINTERS=v1.1
V1_1_DOCUMENT_CONTRACT_SCHEMA_GATE_VALIDATOR=COMPLETE_AND_MATCHING
V2_ACTIVE_POINTER_COUNT=0
COMMIT_A_AUTHORITY_FAMILY_PATH_COUNT=0
PROJECT_MEMORY_ACTIVE_AUTHORITY=false
G1_EFFECTIVE=false
CAPABILITY_SOURCE_COUNT=1
CAPABILITY_SOURCE=capability-package/manifest.json#canonical_inventory
```

The pre-check recipe, interpreter/tool version, input tree and output hash become detached evidence.
It cannot grant authority or become a second authority source. Commit A later replaces this limited
pre-check with the repository-owned cross-surface validator defined by the authorization package.

### 6.3 Reproducibility protocol

Independent validation must resolve only the full closure commit, not a branch name or current
directory. It must record:

- commit, parent and Git tree OIDs;
- canonical tree-inventory SHA-256;
- approved/excluded path digests;
- v1.1 authority-family and Project Memory digests;
- capability, product and MCP raw/canonical digests;
- validator/script/interpreter/Git versions and output hashes;
- clean status/full-content snapshot before and after every command;
- source location identity and actor/session identity;
- all limitations and skipped checks.

Two independent resolutions of the same full commit must produce the same tree/digests and
equivalent deterministic results. A missing validator, skipped mainline check, mutation, extra path,
stale hash or environment-dependent result blocks the baseline.

### 6.4 Acceptance gate

```text
SOURCE_LINEAGE_HUMAN_APPROVED=true
RECONSTRUCTION_ALLOWLIST_HASH_VERIFIED=true
EXCLUSION_OBJECT_HASHES_VERIFIED=true
V1_1_AUTHORITY_FAMILY=PASS
DECISION_TRUTH_ALIGNMENT=PASS
PROJECT_MEMORY_VALIDATION=PASS
GOVERNANCE_REGISTRY_VALIDATION=PASS
CAPABILITY_LEDGER_VALIDATION=PASS
MAINLINE_IDEMPOTENCY=PASS_NO_MUTATION
AUTHORITY_CONSISTENCY_PRECHECK=PASS_V1_1_ONLY
WORKTREE_CLEAN_BEFORE=true
WORKTREE_CLEAN_AFTER=true
ROLLBACK_REFERENCE=MIGRATION_BASELINE_COMMIT
INDEPENDENT_VALIDATION=PASS
HUMAN_BASELINE_DESIGNATION=true
```

These are future acceptance requirements, not current values. Current gate:

```text
SOURCE_LINEAGE_HUMAN_APPROVED=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
ROLLBACK_REFERENCE=UNRESOLVED
ROLES_ASSIGNED=false
IMMUTABLE_MANIFEST_CREATED=false
BASELINE_VALIDATION_GATE=DESIGNED_NOT_RUN
```

## 7. Complexity Encapsulation Check

Reconstruction archaeology remains internal governance complexity. It does not add a user, Agent,
API, MCP, product or ecosystem interface. A future Agent-readable review envelope may expose only:

```text
baseline.commit
baseline.tree
baseline.parent
baseline.clean
lineage.anchor
lineage.patch_sources[]
lineage.status
scope.allowlist_digest
scope.exclusion_digest
validation.status
validation.no_mutation
rollback.reference
reason_codes[]
evidence_refs[]
limitations[]
```

The envelope must link to full evidence and may not hide excluded paths, collisions, validator
failures or staged-truth boundaries.

```text
INTERNAL_RECONSTRUCTION_COMPLEXITY=ENCAPSULATED_NOT_HIDDEN
USER_INTERFACE_CHANGED=false
AGENT_CAPABILITY_INTERFACE_CHANGED=false
EXTERNAL_INTERFACE_CHANGED=false
```

## 8. Risk Analysis

| Risk | Failure mode | Fail-closed control |
|-|-|-|
| wrong lineage | convenient clean branch is named baseline | full candidate classification, human anchor approval, no existing commit eligible |
| hidden changes | current dirty files or index bytes copied wholesale | per-path/hash allowlist; anchor OID comparison; dirty snapshot preservation |
| baseline contamination | Alibaba, Agent Evidence runtime, product launch or v2 files enter closure | exact forbidden set and zero-unlisted-path assertion |
| false clean state | empty status hides missing untracked inputs or validator mutation | commit-tree completeness plus before/after full-content snapshots |
| rollback ambiguity | branch name or moving ref is recorded | full closure commit/tree as pre-A rollback reference |
| v1.1 version split | staged 1.1.0 and working 1.1.1 are mixed | reject index reuse; bind exact approved 1.1.1 bytes/hunks |
| idempotency regression | v1.1 `mainline_guard.py` overwrites isolation fix | semantic collision gate; repeated direct/isolated checks |
| authority pre-creation | successor draft enters baseline as family member | exact Commit A absence check; detached evidence treatment |
| second truth source | manifest/report copies capability facts | references/digests only; canonical inventory remains sole source |
| mainline displacement | authority branch becomes project/product mainline | explicit non-displacement rule and G1 invalidation on mainline drift |
| historical deletion | Alibaba ancestors are removed to make history look clean | no orphan/rewrite/reset; exclude delta while preserving ancestry |
| role self-approval | executor chooses lineage and validates itself | G-3 separation model; Human Owner and Independent Validator required |

The highest hidden risk is semantic overwrite at `scripts/mainline_guard.py` and
`agent-index.json`: both contain necessary governance state and unrelated/generated state. A path
allowlist without hunk/after-hash assertions is insufficient.

## 9. Human Review Decision Packet

Human review must explicitly decide:

1. whether `f6ac41f4...` is accepted as the reconstruction lineage anchor;
2. whether `d0b3dd79...` and `18942ce1...` are accepted only as content-addressed idempotency
   provenance/oracle inputs;
3. the exact v1.1.1 working-tree bytes/hunks that supersede the staged 1.1.0 snapshot;
4. whether the approved product-registry mainline correction is accepted as a pre-baseline
   stabilization input without a product implementation/launch claim;
5. which preparation reports live in the baseline tree and which remain detached evidence;
6. the exact excluded-path/object inventory, including Alibaba and Agent Evidence runtime work;
7. the new, nonexistent worktree path and future branch name;
8. the role roster and mandatory separation defined in G-3;
9. the future one-commit closure rule and rollback acceptance criteria;
10. whether a separately authorized baseline-closure execution phase may begin.

Human acceptance of this design does not create a baseline or make G1 effective. A later execution
authorization must bind exact source hashes, input hashes, allowlist/exclusion digests, role IDs,
worktree path and stop conditions.

## 10. Final Status

```text
BASELINE_RECONSTRUCTION_PREPARATION_STATUS=COMPLETE
SOURCE_LINEAGE_ANALYSIS=COMPLETE_RECONSTRUCTION_REQUIRED
BASELINE_SCOPE=DESIGNED_FAIL_CLOSED
EXCLUSION_RULES=DESIGNED_FAIL_CLOSED
WORKTREE_RECONSTRUCTION_DESIGN=COMPLETE_NOT_EXECUTED
BASELINE_VALIDATION_GATE=DESIGNED_NOT_RUN
MIGRATION_BASELINE_COMMIT=UNRESOLVED
WORKTREE_CREATED=false
BASELINE_CREATED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
NEXT_ACTION=HUMAN_REVIEW_OF_BASELINE_RECONSTRUCTION
```

## 11. Validation and Scope Boundary

Task baseline before report creation:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
HEAD_TREE=def1f5fb06b8087a5c0fabd929be253f25faed67
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=90
BASELINE_STATUS_SHA256=a24b202317bd161988712f432900a08045464762f6ace143de0e481efa37b6f8
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
BASELINE_DIRTY_WORKTREE_CONTENT_SHA256=e59950bb0f0d877166fcb7950329cc5be639d447b0277a4c3d8fd58dfb30b6d5
BASELINE_BRANCH_REF_SHA256=ef752d4fc719c03f39caed5fb982ba22438905c40c31b553240d621c49fac602
BASELINE_WORKTREE_LIST_SHA256=f0de33fa58cba7c612df46fd252ffe482c29cca68ddcf2391a27f0c6a26af5c0
BASELINE_LOCAL_BRANCH_COUNT=4
BASELINE_WORKTREE_COUNT=4
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

Reviewed input hashes:

```text
SAEE_MIGRATION_BASELINE_PREPARATION_REPORT_SHA256=10db277ae39ee9c86abd8ac7ff104e0ff71aa1093e1f704d5bc0f543ba6fd1ff
SAEE_ROLE_ASSIGNMENT_AND_IMMUTABLE_MANIFEST_PREPARATION_SHA256=fed49fa6e48ac8d6b523da36911f196dce8cee7ee063b410df39b9fda9b1b3a3
SAEE_PRE_G1_CLOSURE_EXECUTION_PREPARATION_SHA256=0b3194567d0aec537b19bd709c739422ef2495c57a08fdc2cf2ac1686ee33c5f
SAEE_AUTHORITY_MIGRATION_EXECUTION_AUTHORIZATION_PACKAGE_SHA256=5c39ee5dfd4174f66d48cf50e383d261df2a14a922dc17c3bbc6fc76b3dc5b98
SAEE_DECISION_TRUTH_ALIGNMENT_EXECUTION_REPORT_SHA256=d517e46c02311a2407dc51ebf6f7a1fa9ce48f4ba6e87428a21b5b00e787f8fe
CAPABILITY_PACKAGE_MANIFEST_SHA256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
PROJECT_MEMORY_AGGREGATE_SHA256=31035f74b23a9ead0817fd9347cf45c22f5817392af0c5c40aaa6b80c3bba472
```

Required current-phase validation commands:

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
git diff --check
```

Only this preparation report may be added. No existing path, index entry, branch, worktree or Git
history may change.

Final validation and isolation result:

```text
SAEE_PROJECT_MEMORY_CHECK=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
GIT_DIFF_CHECK=PASS
FINAL_STATUS_ENTRIES=91
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=90
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=a24b202317bd161988712f432900a08045464762f6ace143de0e481efa37b6f8
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
FINAL_DIRTY_CONTENT_EXCLUDING_REPORT_SHA256=e59950bb0f0d877166fcb7950329cc5be639d447b0277a4c3d8fd58dfb30b6d5
FINAL_BRANCH_REF_SHA256=ef752d4fc719c03f39caed5fb982ba22438905c40c31b553240d621c49fac602
FINAL_WORKTREE_LIST_SHA256=f0de33fa58cba7c612df46fd252ffe482c29cca68ddcf2391a27f0c6a26af5c0
AUDIT_INPUT_HASH_GROUPS_UNCHANGED=7/7
ONLY_NEW_STATUS_ENTRY=reports/SAEE_BASELINE_RECONSTRUCTION_PREPARATION.md
PRE_EXISTING_PATHS_MODIFIED_BY_THIS_PHASE=0
LOCAL_BRANCH_COUNT_BEFORE=4
LOCAL_BRANCH_COUNT_AFTER=4
WORKTREE_COUNT_BEFORE=4
WORKTREE_COUNT_AFTER=4
STAGED_TASK_FILES=0
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
PR_CREATED=false
```

The unchanged status, staged patch, unstaged patch, dirty-content, branch-ref and worktree-list
digests prove that this phase preserved the pre-existing evidence surface and Git topology. The
only new path is this preparation report; no reconstruction action occurred.
