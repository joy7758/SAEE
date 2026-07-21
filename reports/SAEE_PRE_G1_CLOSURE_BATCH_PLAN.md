# SAEE Pre-G1 Closure Batch Plan

```text
report_id=SAEE_PRE_G1_CLOSURE_BATCH_PLAN
phase=Phase_0.5.6D
mode=DESIGN_ONLY_NOT_EXECUTION
current_effective_authority=SAEE_Development_Constitution_v1.1
g1_human_authorization=RECEIVED_AS_PRIOR_INTENT
g1_effective=false
phase_0_5_7a_executed=false
```

本计划把 Gate G1 生效前的四个未闭合条件转化为顺序化、可审查、可验证的 future
closure batches。它不执行任何闭合动作，不修改 Project Memory、Constitution、代码或
authority pointer，也不把此前收到的人工 G1 批准升级为已经生效的执行授权。

现行项目主线仍是 SAEE 与 Agent Evidence Project 的受控合并；本治理计划只为保护该
主线的长期规则演化，不把 governance、review 或 migration 变成新的项目主线。

## 1. Current Boundary

当前事实：

- v1.1 是唯一 active repository development authority；
- `V2-F-001..V2-F-005` 已有 Phase 0.5.4 人工设计批准证据，但 Project Memory 仍记录为
  `PROPOSED_FREEZE` / `REQUIRED`；
- `Q-V2-001=OPEN`，`Q-V2-002=BLOCKED`；
- 当前主工作树是 dirty worktree，不是 migration baseline；
- 其他任务的 branch/worktree 无论是否 clean，均不属于本迁移授权范围；
- `MIGRATION_BASELINE_COMMIT`、immutable input manifest 和完整角色任命均未形成；
- `capability-package/manifest.json#canonical_inventory` 仍是唯一 capability fact source；
- v2 authority family、Commit A、Commit B 和 pointer switch 均未执行。

```text
G1_HUMAN_AUTHORIZATION=RECEIVED
G1_EFFECTIVE=false
DECISION_TRUTH_ALIGNMENT=NOT_EXECUTED
MIGRATION_BASELINE_COMMIT=UNDEFINED
IMMUTABLE_MANIFEST=NOT_CREATED
ROLES_ASSIGNED=false
ROLLBACK_REFERENCE=UNDEFINED
PHASE_0_5_7A_EXECUTION=false
```

收到的 G1 批准证明了人类执行意图，但它早于具体 baseline hash、manifest hash、角色、
allowlist digest 和 rollback reference。根据 authorization package 的 hash/scope/role
binding 规则，它不能单独令 G1 生效；闭合后必须重新确认。

## 2. Blocker 001 — Decision Truth Alignment Plan

### 2.1 State model

Decision state 与 Authority state 使用两条独立状态机：

```text
Decision state

PROPOSED
    ↓ explicit human design approval
APPROVED_DESIGN_DIRECTION
    ↓ separate explicit freeze approval and DCP linkage when required
FROZEN

Authority-family state

INACTIVE_CANDIDATE
    ↓ complete family + validation + separate activation approval + atomic switch
ACTIVE_AUTHORITY
```

本闭合批次的最高 decision target 是 `APPROVED_DESIGN_DIRECTION`。它不冻结新决定，不
修改既有 `F-001..F-005`，也不产生 `ACTIVE_AUTHORITY`。

### 2.2 Per-record closure matrix

| Record | Current state | Immediate target | Approval evidence to bind | Authority effect |
|---|---|---|---|---|
| `V2-F-001` | `PROPOSED_FREEZE`; confirmation `REQUIRED` | `APPROVED_DESIGN_DIRECTION`; confirmation `CONFIRMED` | Phase 0.5.4 explicit approval + approved preparation package, exact identity hierarchy | none |
| `V2-F-002` | `PROPOSED_FREEZE`; confirmation `REQUIRED` | `APPROVED_DESIGN_DIRECTION`; confirmation `CONFIRMED` | Phase 0.5.4 explicit approval + approved preparation package, asset ownership boundary | none |
| `V2-F-003` | `PROPOSED_FREEZE`; confirmation `REQUIRED` | `APPROVED_DESIGN_DIRECTION`; confirmation `CONFIRMED` | Phase 0.5.4 explicit approval + approved preparation package, ARO/SECO non-claim | none |
| `V2-F-004` | `PROPOSED_FREEZE`; confirmation `REQUIRED` | `APPROVED_DESIGN_DIRECTION`; confirmation `CONFIRMED` | Phase 0.5.4 explicit approval + approved preparation package, exactly three target products | none |
| `V2-F-005` | `PROPOSED_FREEZE`; confirmation `REQUIRED` | `APPROVED_DESIGN_DIRECTION`; confirmation `CONFIRMED` | Phase 0.5.4 explicit approval + approved preparation package, capability/interface/channel boundary | none |
| `Q-V2-001` | `OPEN` | close as `RESOLVED_BY_APPROVED_DESIGN_DIRECTION` | one append-only decision receipt binding all five outcomes | none |
| `Q-V2-002` | `BLOCKED` with stale/partial blockers | remain `BLOCKED` until all G1 conditions pass; then close as `RESOLVED_FOR_INACTIVE_FAMILY_EXECUTION_ONLY` | baseline, manifest, roles, rollback and new human G1 confirmation | authorizes at most Commit A/B; does not activate v2 |

Closing `Q-V2-001` means removing it from the active-question list only after its complete historical
question, outcome and evidence are preserved in an append-only decision-log receipt. It does not
delete history. `Q-V2-002` must first be rewritten to name the actual remaining Pre-G1 blockers; it
may be closed only by the later G1 revalidation receipt.

### 2.3 Future exact change scope

The future Decision Truth Alignment batch requires a separate, human-approved allowlist. Its
candidate maximum scope is:

```text
governance/project-memory/v2-transition-decisions.md
governance/project-memory/active-questions.md
governance/project-memory/decision-log.md
governance/project-memory/current-state.md
governance/project-memory/README.md
governance/project-memory/memory-policy.md
scripts/saee_project_memory_check.py
tests/test_project_memory.py
```

Rules for the batch:

1. use an append-only new decision-log ID; do not edit existing log receipts;
2. preserve `F-001..F-005` byte-for-byte; `frozen-decisions.md` is excluded;
3. record approval source, date, approver role, exact five outcomes and non-claims;
4. state that `APPROVED_DESIGN_DIRECTION != FROZEN != ACTIVE_AUTHORITY`;
5. update the current-state projection only for decision truth and remaining G1 blockers;
6. do not copy capability, product, MCP, ecosystem or runtime facts into Project Memory;
7. treat every path not explicitly approved as forbidden.

If a future human decision requests `FROZEN`, that is a different batch. It must determine whether a
DCP is required and cannot be inferred from this plan or the prior G1 approval.

### 2.4 Validator requirements

The future Project Memory validator and tests must:

- positively validate `V2-F-001..V2-F-005`, `Q-V2-001..002` and the new append-only receipt;
- enforce the allowed decision transitions and reject skipping from `PROPOSED` to
  `ACTIVE_AUTHORITY`;
- reject `ACTIVE_AUTHORITY` as an individual V2 decision state;
- require approval evidence for `APPROVED_DESIGN_DIRECTION`;
- require DCP linkage before any future change to an existing Frozen Decision;
- ensure closed questions are absent from the active list but retained in the decision log;
- reject duplicate IDs, missing evidence, rewritten legacy receipts and capability facts in memory;
- pass both legacy fixtures and new V2 positive/negative fixtures without mutating the worktree.

Decision Truth exit criteria:

```text
V2_F_001_THROUGH_V2_F_005=APPROVED_DESIGN_DIRECTION
Q_V2_001=RESOLVED_WITH_APPEND_ONLY_EVIDENCE
Q_V2_002=BLOCKED_ON_ACTUAL_PRE_G1_CONDITIONS
LEGACY_FROZEN_DECISIONS=UNCHANGED
PROJECT_MEMORY_VALIDATOR_COVERS_V2_IDS=true
ACTIVE_AUTHORITY_CREATED=false
DECISION_TRUTH_ALIGNMENT=PASS
DECISION_TRUTH_CLOSURE_PLAN=COMPLETE
```

All exit criteria except the plan status remain future, not executed.

## 3. Blocker 002 — Migration Baseline Closure Plan

### 3.1 Source selection

`MIGRATION_BASELINE_COMMIT` is not selected by choosing whichever worktree is currently clean. The
Human Authority Owner must approve a source lineage that satisfies all of the following:

1. starts from a committed, reproducible SAEE lineage with the v1.1 historical family readable;
2. contains the separately approved Decision Truth Alignment closure;
3. contains only explicitly approved stabilization/preflight inputs;
4. excludes unrelated dirty files, other-task patches and unapproved branch state;
5. preserves the controlled SAEE / Agent Evidence integration mainline;
6. records source commit(s), patch IDs, owners and SHA-256 for every imported input.

The current `HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc` is an observed committed anchor,
not an automatically approved migration baseline. The current dirty worktree may be used only as a
read-only evidence location for a specifically approved, content-addressed input; it must never be
used wholesale, cleaned, stashed, reset or relabeled as the migration worktree.

### 3.2 New isolated worktree

After source selection and separate Git authorization, create one new dedicated worktree at a new
human-approved path. It must not reuse the current worktree or any pre-existing worktree from another
task.

Future naming candidate only:

```text
branch=codex/saee-v2-authority-migration-v2-0
worktree=<new_human_approved_path_not_current_and_not_existing_task_worktree>
```

The creation command, path and source hash must appear in the future execution receipt. This plan
does not create the branch or worktree.

### 3.3 Baseline construction and validation

Future sequence:

1. approve `BASE_SOURCE_COMMIT` and the exact pre-G1 input allowlist;
2. create the new isolated worktree from that full commit hash;
3. apply only approved Decision Truth/stabilization commits or content-addressed patches;
4. require `git status --porcelain` to be empty;
5. create a dedicated closure commit through a separate Git authorization;
6. run the baseline validators and prove they do not change status;
7. record the resulting full 40-character hash as `MIGRATION_BASELINE_COMMIT`;
8. freeze its tree hash, parent lineage, validator outputs and allowlist digest.

Minimum baseline checks:

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
git diff --check
WORKTREE_CLEAN_BEFORE=PASS
WORKTREE_CLEAN_AFTER=PASS
```

`scripts/mainline_guard.py` becomes an additional required baseline check only after its clean-checkout
and no-mutation behavior is proven on the selected lineage. A validator that creates or changes
tracked/untracked state fails the baseline.

### 3.4 Rollback reference

For G1/Commit A-B, the rollback reference is the immutable full hash of
`MIGRATION_BASELINE_COMMIT`, plus its tree hash and parent. If Commit A or B fails, recovery uses an
authorized correction/revert commit whose result tree equals the baseline tree; destructive reset,
history rewrite, force push and deletion of evidence are forbidden.

`PRE_SWITCH_COMMIT` is a later G2 reference and cannot be invented at G1.

Baseline exit criteria:

```text
CURRENT_DIRTY_WORKTREE_USED_AS_BASELINE=false
OTHER_TASK_WORKTREE_USED=false
NEW_ISOLATED_WORKTREE=PASS
BASE_SOURCE_LINEAGE=HUMAN_APPROVED
MIGRATION_BASELINE_COMMIT=DEFINED
BASELINE_VALIDATION=PASS_NO_MUTATION
ROLLBACK_REFERENCE=DEFINED
BASELINE_CLOSURE_PLAN=COMPLETE
```

All exit criteria except the plan status remain future, not executed.

## 4. Blocker 003 — Immutable Input Manifest Plan

### 4.1 Role and storage model

The immutable input manifest is a content-addressed G1 evidence artifact, not a Constitution,
authority pointer, capability fact source, product registry or MCP registry. It references canonical
sources; it does not copy their live facts into a second truth surface.

To avoid a circular dependency in which a manifest contains the hash of the commit that contains
itself, the preferred future model is:

1. finalize and validate `MIGRATION_BASELINE_COMMIT`;
2. generate the manifest as a detached, read-only G1 evidence artifact outside the migration
   worktree;
3. calculate and record `manifest_sha256`;
4. have the Independent Validator verify it against a fresh checkout of the baseline;
5. bind the exact manifest hash in the human G1 reconfirmation;
6. preserve the identical bytes later in Commit B evidence without changing their meaning.

The detached evidence location and retention owner must be explicitly approved before generation.
No untracked sidecar may be left in the clean migration worktree.

### 4.2 Required manifest fields

| Field | Required content |
|---|---|
| `manifest_version` | closed schema/version identifier |
| `authorization_id` | one-use G1 authorization identity |
| `baseline_commit` | full 40-character `MIGRATION_BASELINE_COMMIT` |
| `baseline_tree` | Git tree hash |
| `source_lineage` | parent commits, approved patch/commit IDs and source owners |
| `approved_files` | exact sorted allowlist; no globs |
| `sha256` | per-file SHA-256 plus aggregate allowlist digest |
| `capability_digest` | canonicalized digest of `capability-package/manifest.json#canonical_inventory`, expected change `NONE` |
| `product_digest` | canonicalized digest of the authoritative product registry, expected change `NONE` |
| `mcp_digest` | canonicalized digest of the authoritative MCP registry and referenced canonical MCP projection, expected change `NONE` |
| `constitution_digest` | v1.1 document/contract/schema/gate/validator input hashes |
| `project_memory_digest` | approved post-alignment Project Memory aggregate digest |
| `forbidden_set_digest` | frozen list of paths/file classes prohibited from Commit A/B |
| `rollback_reference` | baseline commit/tree and correction/revert acceptance rule |
| `owner` | Human Authority Owner, manifest producer and retention owner identifiers |
| `roles` | executor, independent validator, rollback owner and evidence recorder IDs |
| `timestamp` | timezone-qualified creation time |
| `validator_results` | command, executable hash/version, exit code and output artifact hash |
| `non_claims` | no authority activation, capability, product, MCP, ecosystem or production status change |

The closed manifest schema must reject missing fields, duplicate paths, relative ambiguity, globs,
unknown fields, hash mismatches, role collisions and any capability/product/MCP status copied as a
new authority.

### 4.3 Production and invalidation point

The manifest is produced only after Decision Truth Alignment and baseline validation pass, and after
all roles have stable identifiers. It is produced before human G1 reconfirmation and before Commit A.

Any change to the baseline commit/tree, approved files, per-file hashes, role assignments,
validators, allowlist, forbidden set, digests or rollback reference invalidates the manifest and the
reconfirmation. Regeneration requires independent validation and a new human G1 decision.

```text
IMMUTABLE_MANIFEST_SOURCE=FROZEN_BASELINE_ONLY
IMMUTABLE_MANIFEST_SELF_REFERENCE=false
SECOND_TRUTH_SOURCE_CREATED=false
IMMUTABLE_MANIFEST_PLAN=COMPLETE
```

## 5. Blocker 004 — Role Assignment Plan

### 5.1 Required role record

Each appointment must have a stable human-readable identifier, scope, start/expiry or one-use rule,
timestamp and explicit acceptance. Role names without identities do not satisfy G1.

| Role | Permission | Prohibited action | Evidence responsibility | Current assignment |
|---|---|---|---|---|
| Human Authority Owner | approve source lineage, exact allowlists, roles, rollback and G1 reconfirmation | infer approval from a report/validator; delegate human authority to AI | sign authorization ID, hashes, scope, conditions and one-use rule | human approval source exists; stable role record pending |
| Migration Executor | create the separately authorized worktree and apply only approved Commit A/B changes | expand scope, approve own work, switch pointers, push/PR without authorization | command log, before/after status, commit/tree/file hashes | unassigned |
| Independent Validator | reproduce hashes/checks from a fresh baseline and issue PASS/BLOCKED | edit the reviewed batch, waive failure, equal Executor for the same batch | validator versions, outputs, negative cases, no-mutation proof | unassigned |
| Rollback Owner | hold baseline reference and execute only the pre-authorized correction/revert path on a trigger | destructive reset, history rewrite, force push, delete evidence | trigger receipt, baseline/result tree proof and post-rollback checks | unassigned |
| Evidence Recorder | preserve approvals, manifest, commands, hashes and staged-truth receipts | grant authority or become capability/product/MCP fact source | complete chronological evidence index and retention hash | unassigned |

Codex may be nominated as Migration Executor or Evidence Recorder in a future explicit appointment,
but this plan does not appoint it. An AI Agent cannot be Human Authority Owner. The Independent
Validator for Commit A/B must not be the same actor/session that produced the batch.

### 5.2 Separation and fail-closed rules

```text
HUMAN_AUTHORITY_OWNER_IS_HUMAN=true
MIGRATION_EXECUTOR_MAY_SELF_APPROVE=false
INDEPENDENT_VALIDATOR_EQUALS_EXECUTOR=false
ROLLBACK_OWNER_ACCEPTED_BEFORE_G1=true
EVIDENCE_RECORDER_GRANTS_AUTHORITY=false
UNASSIGNED_ROLE_FAILS_CLOSED=true
```

The role record is part of the immutable manifest binding. Reassignment invalidates G1 and requires
a regenerated manifest, independent revalidation and new human reconfirmation.

```text
ROLE_ASSIGNMENT_PLAN=COMPLETE
ROLES_ASSIGNED=false
```

## 6. G1 Revalidation Gate

G1 may become effective only after the four closure batches produce evidence and the Human Authority
Owner reconfirms the exact resulting package. Evaluation order is fail-closed:

```text
DECISION_TRUTH_ALIGNMENT=PASS
MIGRATION_BASELINE_COMMIT=DEFINED
IMMUTABLE_MANIFEST=PASS
ROLES_ASSIGNED=true
ROLLBACK_REFERENCE=DEFINED
HUMAN_G1_RECONFIRMATION=true
```

The reconfirmation must bind at least:

```text
authorization_id
MIGRATION_BASELINE_COMMIT
baseline_tree
manifest_sha256
Commit_A_B_allowlist_digest
forbidden_set_digest
role_identifiers
rollback_reference
scope=COMMIT_A_AND_COMMIT_B_ONLY
one_use=true
expiry_or_invalidation_rule
```

The earlier human G1 approval remains valid evidence of intent but does not satisfy
`HUMAN_G1_RECONFIRMATION=true`, because the bound values did not yet exist. A reconfirmation grants
no Commit C, pointer switch, push, PR, release, ecosystem development or external claim authority.

```text
G1_REVALIDATION_GATE=DEFINED_FAIL_CLOSED
G1_REVALIDATION_CURRENT_RESULT=BLOCKED
G1_EFFECTIVE=false
```

## 7. Closure Order

```text
Batch P1 — Decision Truth Alignment
        ↓ independent Project Memory validation
Batch P2 — Baseline source approval and new isolated worktree
        ↓ clean closure commit + no-mutation baseline validation
Batch P3 — Role appointments and rollback acceptance
        ↓ stable role identifiers
Batch P4 — Detached immutable manifest generation
        ↓ independent hash/schema validation
Batch P5 — Human G1 reconfirmation bound to all exact values
        ↓
Gate G1 may become effective for Commit A/B only
```

Failure or drift in any earlier batch stops all later batches. No batch in this plan is currently
authorized or executed.

## 8. Risk Analysis

| Skipped condition | Primary risk | Failure mode | Required control |
|---|---|---|---|
| Decision Truth Alignment | authority split brain | preparation says approved while Project Memory says proposed; agents infer incompatible states | state-machine validation + append-only approval receipt |
| Clean Migration Baseline | wrong baseline | unrelated dirty or other-task content enters Commit A/B; rollback cannot reconstruct source | new dedicated worktree + human-approved full commit lineage |
| Immutable Input Manifest | untraceable migration | inputs, owners and before hashes cannot be reproduced; later evidence binds a different tree | detached content-addressed manifest + independent verification |
| Role Assignment | self approval | executor, validator and approver collapse into one actor/session | explicit identities + executor/validator separation + human-only authority owner |

Additional hidden-drift risks:

- treating `APPROVED_DESIGN_DIRECTION` as `FROZEN` or `ACTIVE_AUTHORITY`;
- turning the manifest or Project Memory into a second capability/product/MCP truth source;
- using a clean worktree owned by another task without lineage authorization;
- allowing G1 approval to float across changed hashes, roles or allowlists;
- including pointer, runtime, schema, MCP, product, ecosystem or current dirty cleanup changes in a
  Pre-G1 batch;
- using validator PASS as permission to execute or activate.

```text
AUTHORITY_SPLIT_BRAIN_CONTROL=DESIGNED
WRONG_BASELINE_CONTROL=DESIGNED
UNTRACEABLE_MIGRATION_CONTROL=DESIGNED
SELF_APPROVAL_CONTROL=DESIGNED
HIDDEN_DRIFT_RESOLVED=false
```

## 9. Safety and Non-Claims

This plan preserves:

- v1.1 Constitution, contract, schema, recommendation gate and validator;
- Git history and correction/revert-only rollback semantics;
- existing Evidence lineage and Agent Evidence provenance boundaries;
- canonical capability inventory as the sole capability fact source;
- product, MCP, external-system and ecosystem staged truth;
- the current dirty worktree without cleanup or mutation;
- the separation between inactive authority-family construction and later authority activation.

It does not claim that v2 is active, Phase 0.5.7A has begun, ecosystem development is authorized,
official integration exists, or any product is launched, customer validated or production ready.

## 10. Final Decision

The four closure mechanisms are sufficiently specified for human review. The conditions themselves
remain unexecuted and G1 remains ineffective.

```text
PRE_G1_PLAN_STATUS=COMPLETE
DECISION_TRUTH_CLOSURE_PLAN=COMPLETE
BASELINE_CLOSURE_PLAN=COMPLETE
IMMUTABLE_MANIFEST_PLAN=COMPLETE
ROLE_ASSIGNMENT_PLAN=COMPLETE
G1_REVALIDATION_GATE=DEFINED_FAIL_CLOSED
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
EXECUTION_STARTED=false
CODE_CHANGED=false
AUTHORITY_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PRE_G1_PLAN
```

## 11. Validation and Change Boundary

Task baseline before report creation:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=84
BASELINE_STATUS_SHA256=2252eca9bd9d93cecf1106fceac6bb3cb07fe5e263d3233be74d5b558338cd5c
TARGET_REPORT_EXISTED_AT_BASELINE=false
CAPABILITY_MANIFEST_SHA256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
```

Required validation commands:

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
git diff --check
```

Final scope evidence is recorded after validation. The only permitted task-created path is this
report.

Validation result:

```text
SAEE_PROJECT_MEMORY_CHECK=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
GIT_DIFF_CHECK=PASS
FINAL_STATUS_ENTRIES=85
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=84
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=2252eca9bd9d93cecf1106fceac6bb3cb07fe5e263d3233be74d5b558338cd5c
AUDIT_INPUT_HASHES_UNCHANGED=6/6_GROUPS
ONLY_NEW_STATUS_ENTRY=reports/SAEE_PRE_G1_CLOSURE_BATCH_PLAN.md
STAGED_TASK_FILES=0
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
```
