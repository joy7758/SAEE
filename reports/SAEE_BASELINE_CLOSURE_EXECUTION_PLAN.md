# SAEE Baseline Closure Execution Plan

```text
report_id=SAEE_BASELINE_CLOSURE_EXECUTION_PLAN
phase=Phase_0.5.6G-5
mode=CLOSURE_EXECUTION_DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
decision_truth_alignment=PASS
migration_baseline_commit=UNRESOLVED
g1_effective=false
phase_0_5_7a_authorized=false
```

本报告把 Phase 0.5.6G-4 的 reconstruction design 转换为未来可授权、可停止、可验收的
Baseline Closure execution plan。它不创建 branch、worktree、patch artifact、manifest、
candidate commit 或 baseline，不执行 `git add`/`git commit`，也不创建 Commit A/B、v2
authority family 或 authority pointer switch。

## 1. Executive Decision

未来可以通过一个受控 closure batch 产生 `MIGRATION_BASELINE_COMMIT`，但不能直接把
现有 HEAD、clean branch、dirty index 或任一 report 指定为 baseline。

Closure 必须分开三个事实：

```text
validated_candidate_tree
        ↓ separate human commit-creation approval
baseline_candidate_commit
        ↓ post-commit immutable manifest + independent validation + human designation
MIGRATION_BASELINE_COMMIT
```

`baseline_candidate_commit` 只是 Git commit。只有完成 post-commit gate 后，它才被登记为
`MIGRATION_BASELINE_COMMIT`。Commit creation、baseline designation 与 G1 reconfirmation
是三个不同授权事件。

```text
BASELINE_CLOSURE_PLAN_STATUS=COMPLETE
BASELINE_CLOSURE_EXECUTION_AUTHORIZED=false
BASELINE_CANDIDATE_COMMIT_CREATED=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
WORKTREE_CREATED=false
BASELINE_CREATED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
```

## 2. Reconstruction Delta Matrix

### 2.1 Classification rules

```text
INCLUDE
= required semantic/history content for a valid baseline; execution still requires exact hashes.

ALLOWLIST_REQUIRED
= conditionally admissible or collision-prone content; absent exact human path/hunk/hash approval,
  it is excluded and the gate blocks.

EXCLUDE
= forbidden from the closure delta. Inherited anchor bytes may remain as history, but cannot change
  or become migration authority input.
```

Every `INCLUDE` and `ALLOWLIST_REQUIRED` entry still requires exact sorted paths, before OIDs,
after SHA-256 values, mode/type, owner, reason and application order. Classification is not an
execution grant.

### 2.2 Matrix

| Surface | Classification | Required treatment | Authority/product effect |
|-|-|-|-|
| source anchor `f6ac41f4b068377e7778e8c3d83b99bd8382debc` | `INCLUDE` | human must approve full commit/tree as parent; no current dirty bytes inherited | none; anchor only |
| exact idempotency semantics from `d0b3dd79...` | `ALLOWLIST_REQUIRED` | use content-addressed patch subset; verify against `18942ce1...`; never copy branch/worktree wholesale | validation behavior only |
| complete v1.1.1 authority family and mainline correction | `INCLUDE` | reconcile working v1.1.1 bytes against superseded staged 1.1.0; hunk-level collision control | preserves current v1.1 authority; no v2 activation |
| Decision Truth Alignment outcome | `INCLUDE` | include approved V2-F/P statuses, D-006, Q-V2 closure/blocker state and execution report | design truth only; v2 remains inactive |
| Project Memory complete family | `INCLUDE` | include all closed memory files required by validator; preserve append-only and frozen history | no authority grant |
| `scripts/saee_project_memory_check.py` | `INCLUDE` | exact G-1 after-hash; keep v1.1 active/v2 inactive/G1 false negative cases | governance validator exception |
| `tests/test_project_memory.py` | `INCLUDE` | exact G-1 after-hash and 15-case coverage | test-only |
| V2 principle approval in Project Memory | `INCLUDE` | preserve `V2-P-001..003=APPROVED_DESIGN_DIRECTION` and approval evidence | not Frozen/active |
| `SAEE_V2_CONSTITUTION_PRINCIPLE_CANDIDATE_REGISTRATION.md` | `ALLOWLIST_REQUIRED` | retain original `PROPOSED_DESIGN_PRINCIPLE` bytes as historical predecessor; do not rewrite to approved | evidence only |
| Trust Semantic approval receipt in Decision Log/transition decisions | `INCLUDE` | preserve bounded technical-role semantics and non-claims | no capability/object/schema |
| Trust Semantic decision/sync/acceptance reports | `ALLOWLIST_REQUIRED` | preferably detached evidence; if in tree, exact hashes and historical statuses must remain | evidence only |
| `governance/constitution-migration/v2-authority-successor-draft.md` | `EXCLUDE` | keep outside baseline tree as detached evidence; Commit A owns future family construction | no v2 family in baseline |
| all eight candidate Commit A v2 authority-family files | `EXCLUDE` | assert absent from candidate tree | prevents authority pre-creation |
| v2 authority pointer changes / Commit C hunks | `EXCLUDE` | every active pointer must remain v1.1 | no switch |
| current v1.1 pointer/mainline hunks in `AGENTS.md`, `.codex/*`, `llms.txt`, `governance/README.md`, `agent-index.json`, `mainline_guard.py` | `ALLOWLIST_REQUIRED` | allow only exact v1.1/mainline stabilization hunks; no v2 selector | preserves current routing |
| `capability-package/manifest.json` | `EXCLUDE` from delta | inherit exact anchor bytes; recompute raw and canonical-inventory digests | sole capability truth unchanged |
| `agent-index.json#capability_progress_ledger_v1` | `EXCLUDE` from delta | preserve canonical projection digest while allowing only approved Constitution hunk | no capability fact change |
| approved target-version product registry correction | `ALLOWLIST_REQUIRED` | only exact prior correction with `target_not_implemented` and false launch/customer/production states | no new product implementation/change |
| any other product file/status/copy | `EXCLUDE` | inherited OID unchanged | no product change |
| MCP registry, server, schema, tool or adapter | `EXCLUDE` | raw/canonical MCP digest unchanged | no MCP change |
| governance validators/tests required by v1.1, Project Memory and registry correction | `ALLOWLIST_REQUIRED` | exact approved code/test paths only; no application behavior | internal validation only |
| application/runtime/service/adapter code | `EXCLUDE` | zero paths in closure diff | no code/runtime product behavior |
| current Agent Evidence bridge/adapter/services/tests | `EXCLUDE` | preserve in current evidence worktree and separate mainline closure | mainline not displaced |
| Alibaba repair files, smoke and commercial status hunks | `EXCLUDE` | zero delta; inherited anchor OIDs unchanged; no current-state inference | commercial truth untouched |
| capability, migration and authority preparation reports | `ALLOWLIST_REQUIRED` | human decides baseline-tree versus detached evidence disposition | non-authoritative evidence |
| ignored output, generated state, cache, secrets, Provider evidence | `EXCLUDE` | zero imported paths; no dependency in normal baseline validation | non-portable/local state absent |
| any unlisted path, hunk, mode or generated timestamp | `EXCLUDE` | immediate stop | fail closed |

### 2.3 Required Project Memory content

The required closed Project Memory set is:

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

Observed planning aggregate over these inputs:

```text
PROJECT_MEMORY_PLUS_VALIDATOR_AGGREGATE_SHA256=42cbfbb38bbea146ec2cc4f37a41e203cb5acf8708338e58d6ef7ee6367f9439
```

This is an observed input digest, not a final approved patch digest. The future execution envelope
must recompute it after human disposition and before any worktree is created.

### 2.4 V1.1, principle and Trust Semantic boundaries

The staged Family A patch is historical v1.1.0 evidence:

```text
FAMILY_A_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FAMILY_A_STAGED_CURRENTNESS=SUPERSEDED_BY_V1_1_1
```

The observed working-over-index patch across the v1.1.1 correction surfaces is:

```text
V1_1_1_WORKTREE_OVER_INDEX_PATCH_SHA256=6d0a203b2a16bcf8f71dcecb061d90daf5e4de8c32d4bf99a882c32712aba36d
```

Neither digest is itself an executable closure patch. Future hunk isolation must produce one new,
exact `PB-02` patch digest that contains v1.1.1 and excludes Alibaba/timestamp/formatting residuals.

Principle and Trust Semantic history must remain two-stage:

```text
historical_candidate_report=PROPOSED_DESIGN_PRINCIPLE
later_project_memory_receipt=APPROVED_DESIGN_DIRECTION
frozen_decision=false
active_authority=false
```

Rewriting the historical candidate report to make all surfaces say “approved” is prohibited.

### 2.5 Truth-source digest policy

Observed planning digests:

```text
CAPABILITY_MANIFEST_RAW_SHA256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
CANONICAL_INVENTORY_CANONICAL_JSON_SHA256=33085f918206142edead466f086cad0d4f99b13cf9ac73f2750c31f452a6ad46
PRODUCT_REGISTRY_RAW_SHA256=62c9ee638a4e763e60d2290cdf6fa2bbeabf93373ced8fa4af084203146a316d
PRODUCT_REGISTRY_CANONICAL_JSON_SHA256=aed85e2c765aaf14211c0b4adebe80d81014e0689a075bfd4116374124eb5308
MCP_REGISTRY_RAW_SHA256=fdeda93c44104c61efcdcea2ea2703a919630a68b2af96b12438d45834258a76
MCP_REGISTRY_CANONICAL_JSON_SHA256=52fde49b1da494ec670e649c4e7b6c707d4ac250403de8271bb5a065172ea635
```

Final meanings:

- `CAPABILITY_DIGEST_MATCH=true`: baseline manifest/inventory equals the human-approved inherited
  anchor expectation; capability facts did not change.
- `PRODUCT_DIGEST_MATCH=true`: baseline product registry equals the human-approved expected digest.
  If the prior target-version correction is allowed, that corrected digest is the expectation; if
  not, closure remains blocked rather than choosing another product state.
- `MCP_DIGEST_MATCH=true`: MCP registry/projection equals the approved inherited expectation; no MCP
  change occurred.

Planning digests must be recomputed from the final candidate tree and cannot be copied as proof.

```text
RECONSTRUCTION_DELTA_MATRIX=COMPLETE_FAIL_CLOSED
RECONSTRUCTION_DELTA_APPROVED=false
```

## 3. Patch Application Strategy

### 3.1 Patch record contract

Every future patch bundle must have one immutable record:

```text
patch_bundle_id
source_kind=COMMIT_DIFF|TREE_SNAPSHOT|DETACHED_EVIDENCE
source_commit_full_hash_or_NONE
source_parent_full_hash_or_NONE
source_tree_oid
source_patch_sha256
approved_application_patch_sha256
approved_paths[]
approved_hunks_or_expected_after_hashes[]
before_object_oids[]
after_file_sha256[]
expected_result_tree_inventory_sha256
owner_role_id
owner_actor_id
approval_id
reason
application_order
forbidden_paths_digest
non_claims[]
```

`source_patch_sha256` proves provenance. `approved_application_patch_sha256` binds the exact subset
that may be applied. They may differ; a full source commit must never be treated as approved merely
because one of its concepts is needed.

### 3.2 Candidate patch bundles

| Bundle | Source | Source/observation digest | Future owner | Reason | Current state |
|-|-|-|-|-|-|
| `PB-00` | anchor commit `f6ac41f4...`, tree `def1f5fb...` | full commit/tree OIDs | Human Authority Owner | preserve current approved governance ancestry | `UNAPPROVED` |
| `PB-01` | commit `d0b3dd796aff...`; oracle tree `18942ce1...^{tree}=4e7f7e69...` | full source patch `b8c6fadec76fae47e90399c3cdf56e0f19aeaf4941a35552d9575236b25d8880` | unassigned source owner + Human Authority Owner | restore read-only/idempotent validation without importing branch | `SUBSET_UNDEFINED` |
| `PB-02` | current v1.1.1 working bytes over anchor/index | staged historical `31ad98d0...`; working-over-index observation `6d0a203b...` | Human Authority Owner | complete active v1.1.1 family and mainline rules | `EXACT_PATCH_UNDEFINED` |
| `PB-03` | G-1 Project Memory/validator/test/report snapshots | aggregate `42cbfbb38bbea146ec2cc4f37a41e203cb5acf8708338e58d6ef7ee6367f9439` | Human Authority Owner | preserve executed Decision Truth Alignment | `EXACT_FILES_OBSERVED_NOT_APPROVED` |
| `PB-04` | approved product-registry mainline correction | source patch observation `28f33be3f9ae80babc0c2d144b97245c40f37a725aada92e1c3b776f9f3b7a5c`; report `371885ea...` | Human Authority Owner | remove constitutional target-family contradiction without product promotion | `CONDITIONAL` |
| `PB-05` | principle/Trust Semantic/preflight reports | exact per-file hashes; candidate detached disposition | Evidence Recorder + Human Authority Owner | preserve decision lineage and non-claims | `DISPOSITION_UNDECIDED` |

All human/operational roles are currently unassigned. Role labels in this table are future required
owners, not appointments.

### 3.3 Application order

Future exact order:

```text
PB-00 anchor checkout
    ↓
PB-01 idempotency semantics
    ↓
PB-02 v1.1.1 authority/mainline family
    ↓
PB-04 approved registry correction, only if separately allowlisted
    ↓
PB-03 Decision Truth + complete Project Memory family
    ↓
PB-05 approved evidence disposition
```

This order puts read-only validation infrastructure before validation-dependent governance content.
`PB-03` is applied after the v1.1.1 family it references. Evidence reports come last so they cannot
silently drive behavior.

After every bundle, the Executor must record before/after candidate-tree snapshots and compare only
the bundle allowlist. A conflict, fuzzy offset, rejected hunk, extra mode change or different
after-hash stops execution. Automatic conflict resolution and opportunistic cleanup are forbidden.

### 3.4 Forbidden source methods

```text
WHOLE_BRANCH_COPY=false
WHOLE_WORKTREE_COPY=false
CURRENT_INDEX_REUSE=false
DIRECTORY_GLOB_COPY=false
CHERRY_PICK_WHOLE_OTHER_TASK_COMMIT=false
MERGE_WHOLE_OTHER_TASK_BRANCH=false
OURS_THEIRS_BLANKET_RESOLUTION=false
UNAPPROVED_PATCH_REGENERATION=false
```

The future Executor may use a tool to apply an already approved patch, but the tool cannot decide
scope. Any regenerated patch receives a new digest and returns to human review.

```text
PATCH_APPLICATION_STRATEGY=COMPLETE_NOT_EXECUTED
PATCH_BUNDLES_CREATED=false
PATCHES_APPLIED=false
```

## 4. Clean Baseline Creation Flow

### 4.1 State machine

```text
PLAN_COMPLETE
    ↓ human approves delta, sources, roles, path and stop rules
CLOSURE_INPUTS_FROZEN
    ↓ separate Git/worktree authorization
ISOLATED_WORKTREE_CREATED
    ↓ exact ordered patch application
CANDIDATE_TREE_ASSEMBLED
    ↓ validation + exact staged tree binding
CANDIDATE_TREE_VALIDATED
    ↓ pre-commit closure execution manifest + human commit approval
COMMIT_CREATION_AUTHORIZED
    ↓ one closure commit
BASELINE_CANDIDATE_COMMIT_CREATED
    ↓ post-commit manifest + independent validation
BASELINE_CANDIDATE_VERIFIED
    ↓ explicit human designation
MIGRATION_BASELINE_DESIGNATED
```

Any drift moves the batch to `FAILED_RETAIN_EVIDENCE`; it never skips to a later state.

### 4.2 Step 0 — Preconditions

Before any worktree operation:

```text
RECONSTRUCTION_DELTA_APPROVED=true
PATCH_RECORDS_FROZEN=true
EXCLUSION_DIGEST_FROZEN=true
HUMAN_AUTHORITY_OWNER_ASSIGNED=true
MIGRATION_EXECUTOR_ASSIGNED=true
INDEPENDENT_VALIDATOR_ASSIGNED=true
ROLLBACK_OWNER_ASSIGNED=true
EVIDENCE_RECORDER_ASSIGNED=true
ROLE_SEPARATION_CHECK=PASS
FUTURE_WORKTREE_PATH_APPROVED=true
FUTURE_BRANCH_NAME_APPROVED=true
```

Current values do not satisfy these conditions.

### 4.3 Step 1 — Create isolated migration worktree

Only a new explicit authorization may create:

```text
future_branch=codex/saee-v2-authority-migration-v2-0
future_worktree=<new_nonexistent_human_approved_path>
```

The branch/path must not exist, must not reuse any of the four registered worktrees, and must not
touch the current dirty worktree.

### 4.4 Step 2 — Resolve approved source

Resolve the full `f6ac41f4...` commit and `def1f5fb...` tree. Record Git version, source object
availability, parent/ancestry proof and clean status. Branch names are informational only.

### 4.5 Step 3 — Apply exact approved patches

Apply `PB-01` through `PB-05` in the frozen order. Each bundle must match source and application
hashes, exact paths/hunks and expected after bytes. No unlisted path may change.

### 4.6 Step 4 — Validate candidate tree before commit

Run the complete baseline validator set over the assembled candidate. Record full tree/status before
and after every command. Validate twice where determinism is required. No validator may generate or
repair repository state.

The Executor then stages only the exact approved paths under the future closure authorization and
records:

```text
candidate_parent_commit
candidate_tree_oid
candidate_tree_inventory_sha256
staged_diff_sha256
staged_name_status
staged_path_count
unstaged_path_count=0
untracked_path_count=0
```

This future staging step is not executed by the present plan.

### 4.7 Step 5 — Generate pre-commit Closure Execution Manifest

The pre-commit artifact binds the approved source, patch records, roles, exclusions, candidate tree
OID/inventory digest, staged diff and intended commit metadata. It is a detached authorization
envelope and is not the G-3 baseline manifest.

```text
artifact_role=CLOSURE_EXECUTION_MANIFEST
contains_actual_baseline_commit=false
contains_candidate_tree_oid=true
self_reference=false
location=DETACHED_EVIDENCE
```

### 4.8 Step 6 — Human commit-creation approval

Human Authority Owner reviews the exact candidate tree, staged diff, manifest hash, role records,
validator receipts and rollback rule. Approval is one-use and authorizes creation of one candidate
closure commit only. It does not designate the commit as baseline and does not activate G1.

### 4.9 Step 7 — Create one baseline candidate commit

Migration Executor creates exactly one commit whose:

```text
parent=<approved_source_commit>
tree=<approved_candidate_tree_oid>
scope=<approved_staged_diff_sha256>
message=<human-approved_fixed_message>
```

After creation, prove the worktree/index are clean and the actual parent/tree/diff equal the
pre-commit envelope. Any amend, squash, rebase or metadata-driven replacement invalidates approval.

```text
BASELINE_CANDIDATE_COMMIT_CREATED=true   # future state only
MIGRATION_BASELINE_COMMIT=UNRESOLVED     # remains until designation
```

### 4.10 Step 8 — Generate post-commit Immutable Baseline Manifest

Only now can the G-3 immutable manifest bind the actual full commit hash without self-reference:

```text
artifact_role=IMMUTABLE_BASELINE_MANIFEST
baseline_candidate_commit=<actual_full_hash>
baseline_tree_oid=<actual_tree>
parent_commit=<actual_parent>
closure_execution_manifest_sha256=<pre_commit_manifest_hash>
location=DETACHED_EVIDENCE
```

The manifest also binds all source, patch, role, truth-source, validator and rollback digests. It
must pass independent reconstruction and lifecycle verification before human designation.

### 4.11 Step 9 — Independent validation

Independent Validator resolves the candidate commit in a fresh approved location, not the
Executor's worktree. It recomputes every hash, reruns the full gate and issues `PASS` or `BLOCKED`.
The Validator cannot edit or repair the candidate.

### 4.12 Step 10 — Human baseline approval and designation

Human Authority Owner binds the actual candidate commit, tree, immutable manifest SHA-256,
independent receipt and rollback reference. Only this decision records:

```text
MIGRATION_BASELINE_COMMIT=<full_candidate_commit_hash>
BASELINE_CREATED=true
BASELINE_ACCEPTANCE=PASS
```

It does not authorize Commit A/B or activate G1.

```text
BASELINE_CREATION_FLOW=COMPLETE_DESIGN_NOT_EXECUTED
```

## 5. Baseline Acceptance Gate

### 5.1 Required conditions

The candidate becomes `MIGRATION_BASELINE_COMMIT` only if every condition is true:

```text
WORKTREE_CLEAN=true
SOURCE_LINEAGE_VERIFIED=true
PATCH_SCOPE_VERIFIED=true
PATCH_ORDER_VERIFIED=true
UNLISTED_PATH_COUNT=0
V1_1_AUTHORITY_FAMILY_COMPLETE=true
V2_AUTHORITY_FAMILY_ABSENT=true
ACTIVE_AUTHORITY_POINTERS=v1.1
DECISION_TRUTH_ALIGNMENT=PASS
VALIDATORS_PASS=true
VALIDATORS_NO_MUTATION=true
CAPABILITY_DIGEST_MATCH=true
PRODUCT_DIGEST_MATCH=true
MCP_DIGEST_MATCH=true
IMMUTABLE_MANIFEST_CREATED=true
IMMUTABLE_MANIFEST_VERIFIED=true
ROLE_ASSIGNMENTS_CONFIRMED=true
ROLE_SEPARATION_CHECK=PASS
ROLLBACK_REFERENCE_READY=true
INDEPENDENT_VALIDATION=PASS
HUMAN_BASELINE_APPROVAL=true
```

One false, missing, unknown or stale field blocks designation.

### 5.2 Required validator set

```text
python3 scripts/saee_project_memory_check.py
python3 -m unittest tests/test_project_memory.py
python3 scripts/saee_governance_registry_check.py
python3 -m unittest tests/test_governance_registry.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
git diff --check
make check
python3 scripts/mainline_guard.py
<hash-pinned read-only v1.1 authority consistency pre-check>
```

`make check` and direct mainline validation are admitted only after `PB-01` idempotency semantics are
present and verified. They must run twice, preserve full worktree content and not require ignored
Provider evidence. The pre-check confirms all active pointers remain v1.1 and all Commit A family
paths are absent; it cannot become a second authority source.

### 5.3 Role gate

Mandatory separation for the same closure batch:

```text
HUMAN_AUTHORITY_OWNER_IS_HUMAN=true
HUMAN_AUTHORITY_OWNER_NE_MIGRATION_EXECUTOR=true
HUMAN_AUTHORITY_OWNER_NE_INDEPENDENT_VALIDATOR=true
MIGRATION_EXECUTOR_NE_INDEPENDENT_VALIDATOR=true
ROLLBACK_OWNER_CONFIRMED=true
EVIDENCE_RECORDER_GRANTS_AUTHORITY=false
```

The Executor may generate manifest bytes but cannot verify or approve them. The Independent
Validator may issue a validation result but cannot designate the baseline. Human approval cannot be
inferred from this plan or a PASS result.

### 5.4 Candidate commit identity rule

```text
GIT_COMMIT_EXISTS=true
```

is necessary but insufficient. Before designation:

```text
BASELINE_CANDIDATE_COMMIT_CREATED=true
BASELINE_CREATED=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
```

After all gate conditions and explicit designation:

```text
BASELINE_CANDIDATE_COMMIT_CREATED=true
BASELINE_CREATED=true
MIGRATION_BASELINE_COMMIT=<full_hash>
```

### 5.5 G1 relationship

Baseline acceptance closes only the clean-baseline blocker. It does not reactivate G1. G1 still
requires actual role assignments, the verified G1 immutable input manifest, rollback readiness and
a new human reconfirmation binding exact A/B scope.

```text
BASELINE_PASS_AUTO_ACTIVATES_G1=false
G1_REACTIVATION_AFTER_BASELINE=CONDITIONAL_NOT_AUTOMATIC
COMMIT_A_B_AUTHORIZED_BY_BASELINE=false
COMMIT_C_AUTHORIZED_BY_BASELINE=false
```

Current acceptance state:

```text
WORKTREE_CLEAN=NOT_APPLICABLE_NO_WORKTREE
SOURCE_LINEAGE_VERIFIED=false
PATCH_SCOPE_VERIFIED=false
VALIDATORS_PASS=NOT_RUN_ON_CANDIDATE
CAPABILITY_DIGEST_MATCH=NOT_VERIFIED_ON_CANDIDATE
PRODUCT_DIGEST_MATCH=NOT_VERIFIED_ON_CANDIDATE
MCP_DIGEST_MATCH=NOT_VERIFIED_ON_CANDIDATE
IMMUTABLE_MANIFEST_CREATED=false
ROLE_ASSIGNMENTS_CONFIRMED=false
HUMAN_BASELINE_APPROVAL=false
BASELINE_ACCEPTANCE_GATE=BLOCKED_NOT_EXECUTED
```

## 6. Baseline Rollback Strategy

### 6.1 Failure before worktree creation

No Git or filesystem state has changed. Mark the authorization/envelope `REJECTED` or `EXPIRED` and
retain its hash. The current dirty worktree remains untouched.

### 6.2 Failure during patch application or pre-commit validation

Stop immediately. Do not clean, reset, restore, stash or force the candidate. Record:

```text
failed_bundle_id
last_accepted_tree_snapshot
actual_status_and_diff_hash
validator_or_hash_failure
unapplied_bundle_ids[]
```

Retain the isolated failed worktree for evidence until the Evidence Recorder and Human Authority
Owner decide its disposition. No commit is created and no current worktree path changes.

### 6.3 Failure after pre-commit manifest but before commit

Invalidate the closure execution manifest. Any changed tree, patch, role, validator result or
metadata rule requires a new artifact and new human review. Do not edit the manifest in place.

### 6.4 Failure after candidate commit but before baseline designation

The commit remains immutable evidence with status `REJECTED_BASELINE_CANDIDATE`. Do not reset,
rewrite, amend, squash, force-push or delete it. Options require new human authorization:

1. create a correction child commit and treat that child as a new candidate; or
2. reconstruct again from the approved source anchor on a new branch/path.

Neither option changes the current working tree or makes the failed candidate authoritative.

### 6.5 Failure after baseline designation but before Commit A

Invalidate the immutable manifest and G1 inputs. Preserve the designated baseline as historical
evidence. A new correction/reconstruction candidate must pass the full gate and receive a new human
designation. Active v1.1 authority remains unchanged.

### 6.6 Rollback invariants

```text
CURRENT_WORKTREE_IMPACT=NONE
ACTIVE_AUTHORITY_IMPACT=NONE
V1_1_HISTORY_DELETED=false
FAILED_CANDIDATE_DELETED=false
DESTRUCTIVE_RESET_ALLOWED=false
HISTORY_REWRITE_ALLOWED=false
FORCE_PUSH_ALLOWED=false
EVIDENCE_DELETION_ALLOWED=false
```

The accepted full baseline commit/tree becomes the future pre-A rollback reference only after
designation. Before designation, the source anchor is the recovery point and the candidate is merely
evidence.

```text
BASELINE_ROLLBACK_STRATEGY=COMPLETE_DESIGN_NOT_EXECUTED
```

## 7. Complexity Encapsulation Check

Patch archaeology, tree OIDs, dual manifests, validation receipts and role records remain internal
migration controls. They do not change the Agent, user, product, MCP or ecosystem interface.

A future Agent-readable envelope may expose:

```text
closure.state
source.commit
source.tree
patches.scope_digest
patches.status
candidate.commit
candidate.tree
candidate.clean
manifest.pre_commit_sha256
manifest.post_commit_sha256
validation.status
roles.confirmed
rollback.reference
baseline.designated
g1.effective
reason_codes[]
evidence_refs[]
limitations[]
```

The simple envelope must link to full evidence and cannot hide an unassigned role, conditional
product disposition, excluded mainline work, failed validator or unapproved patch.

```text
INTERNAL_BASELINE_COMPLEXITY=ENCAPSULATED_NOT_HIDDEN
AGENT_INTERFACE_CHANGED=false
USER_INTERFACE_CHANGED=false
PRODUCT_INTERFACE_CHANGED=false
EXTERNAL_INTERFACE_CHANGED=false
```

## 8. Risk Analysis

| Risk | Failure mode | Control/stop condition |
|-|-|-|
| wrong patch source | source branch/worktree copied instead of exact commit bytes | full commit/parent/tree and source patch hashes; no whole-branch method |
| hidden file inclusion | globs, generated files or mixed `agent-index.json` hunks enter | exact path/hunk/after-hash allowlist; unlisted count must be zero |
| baseline contamination | Alibaba, runtime, MCP, capability or v2 family enters closure | frozen forbidden digest; anchor OID equality for all excluded paths |
| validator gap | only three local smokes pass while mainline mutates or lacks assertions | full gate, repeated idempotency, negative cases and independent rerun |
| self approval | Executor assembles, validates and designates its own commit | mandatory role separation and human-only designation |
| false clean baseline | status is empty but wrong/missing tree content is committed | exact tree OID/inventory, commit-parent/diff comparison and fresh resolution |
| manifest self-reference | pre-commit manifest tries to contain unknown final commit hash | dual-artifact model: tree-bound pre-commit + commit-bound post-commit manifest |
| v1.1 split | staged 1.1.0 mixed with working 1.1.1 | new PB-02 after-hash set; staged snapshot is historical only |
| idempotency regression | v1.1 mainline guard overwrites isolation repair | PB-01 first, semantic collision assertions, double validation |
| product truth ambiguity | prior target correction mistaken for new product change | PB-04 conditional human allowlist and fixed non-production digest |
| decision history rewrite | proposed principle report silently changed to approved | preserve candidate report bytes plus later D-006 approval receipt |
| G1 over-promotion | baseline PASS treated as Commit A/B authority | separate G1 reconfirmation; baseline does not activate G1 |
| mainline displacement | authority closure branch becomes product mainline | explicit non-displacement; invalidate on integration-mainline drift |
| rollback ambiguity | moving branch used instead of immutable hash | source anchor before designation; full commit/tree after designation |

The most important new control is the dual-manifest boundary. Without it, the plan would either
approve a commit whose final identity is unknown or create an impossible self-referential manifest.

## 9. Human Review Decisions

Human review must decide:

1. whether the G-4 recommended anchor `f6ac41f4...` is accepted;
2. the exact `PB-01` idempotency subset and its application patch digest;
3. the exact `PB-02` v1.1.1 hunk/after-hash set;
4. whether `PB-04` product registry correction is admitted as prior governance truth;
5. which principle/Trust Semantic/preflight reports enter the tree versus detached evidence;
6. the exact forbidden path/object digest;
7. all five role assignments and separation proof;
8. the future branch and new worktree path;
9. the pre-commit closure manifest format and one-use commit approval;
10. the post-commit immutable baseline manifest and designation gate;
11. whether a separately scoped baseline closure execution authorization may be prepared.

Approval of this plan alone does not authorize any Git or migration action.

## 10. Final Status

```text
BASELINE_CLOSURE_PLAN_STATUS=COMPLETE
RECONSTRUCTION_DELTA_MATRIX=COMPLETE_FAIL_CLOSED
PATCH_APPLICATION_STRATEGY=COMPLETE_NOT_EXECUTED
BASELINE_CREATION_FLOW=COMPLETE_DESIGN_NOT_EXECUTED
BASELINE_ACCEPTANCE_GATE=DESIGNED_BLOCKED_NOT_EXECUTED
BASELINE_ROLLBACK_STRATEGY=COMPLETE_DESIGN_NOT_EXECUTED
BASELINE_CLOSURE_EXECUTION_AUTHORIZED=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
WORKTREE_CREATED=false
BASELINE_CREATED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
NEXT_ACTION=HUMAN_REVIEW_OF_BASELINE_CLOSURE_PLAN
```

## 11. Validation and Scope Boundary

Task baseline before report creation:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
HEAD_TREE=def1f5fb06b8087a5c0fabd929be253f25faed67
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=91
BASELINE_STATUS_SHA256=baedf515bbbceea762a19b91e9500d80a7dd6cba9f38601e00d78c2f5207873a
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
BASELINE_DIRTY_WORKTREE_CONTENT_SHA256=fb732563d10db5a235c2081cc09787fdd295c1e40b0a3e7e0f803de8c4530fd0
BASELINE_BRANCH_REF_SHA256=ef752d4fc719c03f39caed5fb982ba22438905c40c31b553240d621c49fac602
BASELINE_WORKTREE_LIST_SHA256=f0de33fa58cba7c612df46fd252ffe482c29cca68ddcf2391a27f0c6a26af5c0
BASELINE_LOCAL_BRANCH_COUNT=4
BASELINE_WORKTREE_COUNT=4
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

Reviewed input hashes:

```text
SAEE_BASELINE_RECONSTRUCTION_PREPARATION_SHA256=9330cb6f91563ce0bd45999d17387f5a8e44cedc44a48fa7f5244b568c689ef4
SAEE_ROLE_ASSIGNMENT_AND_IMMUTABLE_MANIFEST_PREPARATION_SHA256=fed49fa6e48ac8d6b523da36911f196dce8cee7ee063b410df39b9fda9b1b3a3
SAEE_PRE_G1_CLOSURE_EXECUTION_PREPARATION_SHA256=0b3194567d0aec537b19bd709c739422ef2495c57a08fdc2cf2ac1686ee33c5f
SAEE_DECISION_TRUTH_ALIGNMENT_EXECUTION_REPORT_SHA256=d517e46c02311a2407dc51ebf6f7a1fa9ce48f4ba6e87428a21b5b00e787f8fe
SAEE_AUTHORITY_MIGRATION_EXECUTION_AUTHORIZATION_PACKAGE_SHA256=5c39ee5dfd4174f66d48cf50e383d261df2a14a922dc17c3bbc6fc76b3dc5b98
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

Only this plan report may be added. No existing file, index entry, branch, worktree, commit or Git
history may change.

Final validation and isolation result:

```text
SAEE_PROJECT_MEMORY_CHECK=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
GIT_DIFF_CHECK=PASS
FINAL_STATUS_ENTRIES=92
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=91
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=baedf515bbbceea762a19b91e9500d80a7dd6cba9f38601e00d78c2f5207873a
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
FINAL_DIRTY_CONTENT_EXCLUDING_REPORT_SHA256=fb732563d10db5a235c2081cc09787fdd295c1e40b0a3e7e0f803de8c4530fd0
FINAL_BRANCH_REF_SHA256=ef752d4fc719c03f39caed5fb982ba22438905c40c31b553240d621c49fac602
FINAL_WORKTREE_LIST_SHA256=f0de33fa58cba7c612df46fd252ffe482c29cca68ddcf2391a27f0c6a26af5c0
AUDIT_INPUT_HASH_GROUPS_UNCHANGED=7/7
ONLY_NEW_STATUS_ENTRY=reports/SAEE_BASELINE_CLOSURE_EXECUTION_PLAN.md
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

The unchanged status, staged/unstaged patches, dirty-content aggregate, branch refs and worktree
registry prove that the plan did not perform closure execution. No candidate commit, baseline,
manifest, branch or worktree was created.
