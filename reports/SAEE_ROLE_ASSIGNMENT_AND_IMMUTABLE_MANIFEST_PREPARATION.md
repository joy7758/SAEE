# SAEE Role Assignment and Immutable Manifest Preparation

```text
report_id=SAEE_ROLE_ASSIGNMENT_AND_IMMUTABLE_MANIFEST_PREPARATION
phase=Phase_0.5.6G-3
mode=ROLE_AND_MANIFEST_DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
decision_truth_alignment=PASS
migration_baseline_commit=UNRESOLVED
g1_effective=false
```

本报告设计未来 Authority Migration 的角色体系和 Immutable Input Manifest。它不实际
任命角色，不创建 manifest、baseline、worktree、commit 或 authority family，也不修改
Project Memory、Constitution、successor、pointer、capability、schema、MCP 或 code。

## 1. Executive Boundary

```text
ROLE_MANIFEST_PREPARATION_STATUS=COMPLETE
ROLES_ASSIGNED=false
MANIFEST_CREATED=false
BASELINE_CREATED=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
```

Role names in this report are empty governance slots, not appointments. Manifest fields are a future
contract design, not a created schema or truth source. Human review is required before either design
can be used.

## 2. Role Assignment Design

### 2.1 Common appointment record

Every future role appointment must be a content-addressed record containing:

```text
role_assignment_id
role_name
actor_id
actor_type=HUMAN_OR_AI
scope
authorized_actions[]
prohibited_actions[]
evidence_responsibilities[]
appointed_by
accepted_by
appointed_at
accepted_at
expires_at_or_one_use_rule
conflict_check_result
record_sha256
```

A title, chat mention or inferred identity does not count as assignment. The actor must explicitly
accept the role and its prohibitions. Role reassignment changes the manifest input and invalidates
any prior G1 reconfirmation.

### 2.2 Human Authority Owner

Responsibilities:

- approve or reject G1 and G2;
- approve source lineage, exact allowlists, excluded paths, role roster and rollback triggers;
- approve the inactive-family scope and later exact activation diff;
- bind authorization to baseline, manifest, roles, scope, expiry and one-use semantics.

Permissions:

- issue, deny, expire or revoke a human authorization envelope;
- require revalidation or a new manifest after drift.

Prohibitions:

- must not approve automatically because a validator/report says PASS;
- must not infer consent from preparation work;
- must not delegate human authority to AI, a script or Project Memory;
- must not serve as Migration Executor or Independent Validator for the same authorized batch.

Evidence responsibility:

- sign or otherwise explicitly identify the authorization ID, exact hashes, scope, conditions,
  timestamp, expiry and invalidation rules.

```text
HUMAN_AUTHORITY_OWNER_MUST_BE_HUMAN=true
HUMAN_AUTHORITY_OWNER_ASSIGNED=false
```

### 2.3 Migration Executor

Responsibilities:

- create only the separately authorized worktree/branch;
- apply exact approved commits, patches and paths in the declared order;
- execute Commit A/B actions only after G1 becomes effective;
- stop on any mismatch, extra path, failed check or changed input.

Permissions:

- perform only the commands and file changes contained in the active one-use authorization.

Prohibitions:

- no allowlist expansion, opportunistic cleanup, unrelated fix or hidden refactor;
- no self-approval, independent validation of own batch or authority switch under G1;
- no push, PR, release, deployment or external claim without separate authorization.

Evidence responsibility:

- record commands, tool versions, before/after status, path/file hashes, commit/tree hashes and stop
  conditions.

```text
MIGRATION_EXECUTOR_ASSIGNED=false
MIGRATION_EXECUTOR_MAY_SELF_APPROVE=false
```

### 2.4 Independent Validator

Responsibilities:

- resolve the baseline and artifacts independently from full hashes;
- recompute manifest, file and tree digests;
- run validators, negative cases, no-mutation and allowlist checks;
- issue a signed/content-addressed `PASS` or `BLOCKED` receipt.

Permissions:

- read immutable inputs and execute approved read-only validation commands.

Prohibitions:

- no editing, staging, committing or repairing the batch being validated;
- no waiving a failure, changing expected output or granting G1/G2;
- cannot be the Migration Executor or Human Authority Owner for the same batch.

Evidence responsibility:

- record independent actor/session/environment ID, input hashes, validator/script/interpreter
  versions, commands, exit codes, output hashes, status-before/after and limitations.

```text
INDEPENDENT_VALIDATOR_ASSIGNED=false
INDEPENDENT_VALIDATOR_MAY_EDIT=false
INDEPENDENT_VALIDATOR_GRANTS_AUTHORITY=false
```

### 2.5 Rollback Owner

Responsibilities:

- hold the baseline and pre-switch full-hash references;
- confirm rollback triggers and correction/revert acceptance criteria before execution;
- execute a pre-authorized rollback when an enumerated trigger occurs;
- prove the restored result tree and rerun post-rollback validation.

Permissions:

- create only the authorized correction/revert commit within the trigger set and scope.

Prohibitions:

- no destructive reset, history rewrite, force push or evidence deletion;
- no new migration, activation or unrelated correction during rollback;
- cannot treat rollback success as new authority approval.

Evidence responsibility:

- preserve trigger, failed commit, baseline/pre-switch reference, correction commit, result tree,
  validator outputs and unresolved blocker.

```text
ROLLBACK_OWNER_ASSIGNED=false
HISTORY_REWRITE_ALLOWED=false
FORCE_PUSH_ALLOWED=false
```

### 2.6 Evidence Recorder

Responsibilities:

- preserve hashes, commands, approvals, receipts, role records, manifest versions and timestamps;
- maintain the chronological evidence index and retention digest;
- preserve staged truth and link to canonical sources.

Permissions:

- record and package already authorized evidence without changing its semantic status.

Prohibitions:

- no capability/product/MCP/external fact changes;
- no authority grant, approval inference, evidence rewriting or silent deletion;
- no substitution for Human Authority Owner or Independent Validator.

Evidence responsibility:

- publish an append-only index with source, owner, retention location, byte hash and supersession/
  invalidation relationship.

```text
EVIDENCE_RECORDER_ASSIGNED=false
EVIDENCE_RECORDER_GRANTS_AUTHORITY=false
```

## 3. Role Conflict Analysis

### 3.1 Mandatory separation

For the same batch/commit:

```text
HUMAN_AUTHORITY_OWNER_NE_MIGRATION_EXECUTOR=true
HUMAN_AUTHORITY_OWNER_NE_INDEPENDENT_VALIDATOR=true
MIGRATION_EXECUTOR_NE_INDEPENDENT_VALIDATOR=true
AI_NE_HUMAN_AUTHORITY_OWNER=true
```

These three authority-bearing functions—decision/approval, execution and independent validation—
must be performed by distinct actors. No single actor may decide, execute and validate its own batch.

For Commit C, Rollback Owner must also be distinct from the Migration Executor so a split-brain
activation can be corrected without relying on the actor that produced it.

```text
COMMIT_C_EXECUTOR_NE_ROLLBACK_OWNER=true
```

### 3.2 Conditional combinations

| Combination | Allowed? | Conditions |
|---|---:|---|
| Human Authority Owner + Rollback Owner | conditional | trigger set pre-approved, actions role-stamped, Independent Validator remains separate |
| Human Authority Owner + Evidence Recorder | conditional | recorder role grants no authority and another actor verifies evidence digest |
| Migration Executor + Evidence Recorder | conditional | raw command log is immutable and Independent Validator verifies it |
| Independent Validator + Evidence Recorder | conditional | recorder work is passive; validation inputs cannot be edited |
| Rollback Owner + Evidence Recorder | conditional | correction evidence independently verified |
| Migration Executor + Rollback Owner for Commit A/B | discouraged/conditional | only pre-authorized revert scope; never Commit C; independent validation required |
| Migration Executor + Independent Validator | no | direct self-validation conflict |
| Human Authority Owner + Migration Executor | no | approval/execution conflict |
| Human Authority Owner + Independent Validator | no | approval cannot masquerade as independent validation |

An AI Agent may be explicitly appointed as Executor, read-only Independent Validator in a separate
session/environment, Rollback operator or Evidence Recorder. It can never be Human Authority Owner.
The same AI identity/session cannot be both Executor and Independent Validator.

```text
ROLE_SEPARATION_RULES=COMPLETE_FAIL_CLOSED
ROLE_CONFLICT_CHECK_REQUIRED=true
ROLE_ASSIGNMENTS_CURRENTLY_VALID=false
ROLES_ASSIGNED=false
```

## 4. Immutable Input Manifest Design

### 4.1 Manifest identity and purpose

The future manifest is a detached, content-addressed G1 authorization input. It binds one clean
baseline, one role roster, one exact A/B scope and one rollback reference. It references canonical
truth sources; it does not become a Constitution, capability inventory, product registry or MCP
registry.

Proposed lifecycle identity:

```text
manifest_id=SAEE_G1_INPUT_<baseline_commit_short>_<unique_timestamp_or_sequence>
manifest_version=<closed_format_version>
authorization_id=<future_one_use_G1_authorization_id>
```

No ID or artifact is created by this report.

### 4.2 Required structure

| Field | Required content |
|---|---|
| `manifest_id` | unique immutable artifact identity |
| `manifest_version` | closed format version |
| `authorization_id` | one-use G1 authorization identity |
| `current_authority` | exact active authority ID and hashes |
| `baseline_commit` | full commit OID, not branch name |
| `baseline_tree_oid` | Git tree OID from baseline commit |
| `parent_commit` | direct parent of baseline commit |
| `source_lineage` | anchor, replayed commit/patch IDs, order, owners and reasons |
| `approved_paths` | exact byte-sorted paths; no globs/directories |
| `excluded_paths` | exact paths, observed status/hash, owner and exclusion reason |
| `file_sha256` | per-approved-file SHA-256 over repository bytes |
| `tree_sha256` | SHA-256 of the canonical complete tree inventory described below |
| `approved_paths_digest` | SHA-256 of canonical approved-path records |
| `excluded_paths_digest` | SHA-256 of canonical excluded-path records |
| `capability_digest` | raw and canonical JSON digests of canonical capability inventory |
| `product_digest` | raw and canonical JSON digests of authoritative product registry |
| `mcp_digest` | raw and canonical JSON digests of authoritative MCP registry/projection |
| `authority_family_digest` | v1.1 document/contract/schema/gate/validator hashes |
| `project_memory_digest` | accepted G-1 Project Memory aggregate digest |
| `principle_input_digests` | exact approved V2-P wording/source hashes if Commit A uses them |
| `expected_commit_a_b_scope` | exact path/hunk/after-hash or expected-tree model |
| `validator_versions` | command, executable/script hash, interpreter/tool version and expected assertions |
| `owner_records` | role assignment IDs and record hashes for all five roles |
| `timestamp` | timezone-qualified generation/verification/freeze times |
| `rollback_reference` | baseline commit/tree, triggers, owner and acceptance rule |
| `expiry_and_one_use` | expiry, consumption and invalidation semantics |
| `non_claims` | no activation, capability/product/MCP/ecosystem/production effect |

### 4.3 Canonical hashing rules

`file_sha256` hashes exact repository bytes. Line-ending normalization is forbidden.

`tree_sha256` is separate from `baseline_tree_oid`. It is computed over a byte-sorted canonical tree
inventory containing for every entry:

```text
path
git_mode
object_type
git_object_oid
file_sha256_or_gitlink_oid
```

The canonical serializer, separator bytes, UTF-8/path handling, symlink handling and submodule
handling must be versioned in the manifest format. Two verifiers over the same tree must produce the
same SHA-256.

Structured JSON digests record both:

1. raw file SHA-256; and
2. canonical JSON SHA-256 using a declared serializer/version.

This prevents formatting-only differences from hiding semantic drift while preserving exact bytes.

```text
MANIFEST_DESIGN=COMPLETE
MANIFEST_SCHEMA_CREATED=false
MANIFEST_CREATED=false
SECOND_TRUTH_SOURCE_CREATED=false
```

## 5. Manifest Lifecycle

### 5.1 State machine

```text
DESIGN_ONLY
    ↓ human accepts design + roles assigned + baseline defined
GENERATED_UNVERIFIED
    ↓ Independent Validator recomputes all inputs
VERIFIED
    ↓ Human Authority Owner binds exact manifest_sha256
FROZEN_FOR_G1
    ↓ authorized Commit A/B scope is consumed
CONSUMED

Any drift before consumption
    ↓
INVALIDATED

Time limit reached without use
    ↓
EXPIRED
```

`FROZEN_FOR_G1` is an immutable-evidence lifecycle state, not a constitutional Frozen Decision.

### 5.2 Creation time

Generate only after:

- `MIGRATION_BASELINE_COMMIT` and tree are defined and independently validated;
- the dedicated migration worktree is clean before and after validators;
- all five roles have accepted stable role assignment IDs;
- exact approved/excluded paths and rollback reference are available.

The manifest is created outside the migration worktree as a detached read-only artifact. It must not
leave an untracked sidecar in the baseline tree.

### 5.3 Verification and freeze

The Migration Executor may generate the bytes. The Evidence Recorder retains them and computes the
artifact hash. The Independent Validator must independently reconstruct every field from a fresh
resolution of the baseline commit. The Rollback Owner verifies the rollback reference. The Human
Authority Owner then accepts or rejects the exact `manifest_sha256`.

No actor may edit a manifest in place after verification. A correction creates a new manifest ID,
new hash, new validation receipt and new human review.

### 5.4 Invalidation conditions

The manifest immediately becomes invalid if any of the following changes:

- baseline commit/tree/parent or source lineage;
- approved/excluded path, file hash, expected A/B scope or forbidden set;
- capability/product/MCP/authority/Project Memory/principle digest;
- role assignment, owner, validator version, rollback reference or active authority;
- validation result, no-mutation result, expiry or one-use consumption state;
- any unlisted path enters Commit A/B;
- artifact bytes no longer match the Human Authority Owner's accepted hash.

Invalidation returns G1 to ineffective and requires a new manifest plus human reconfirmation.

```text
MANIFEST_LIFECYCLE=COMPLETE_DESIGN
MANIFEST_CURRENT_STATE=NOT_CREATED
MANIFEST_FROZEN_FOR_G1=false
```

## 6. Baseline and Commit Relationship

### 6.1 Baseline binding

The baseline commit exists before the manifest. The manifest records its full commit/tree IDs and
recomputable tree SHA-256. Therefore the manifest cannot be part of the commit it identifies.

```text
MANIFEST_SELF_REFERENCE_ALLOWED=false
MANIFEST_LOCATION=DETACHED_EVIDENCE_ARTIFACT
BASELINE_COMMIT=UNRESOLVED
```

### 6.2 Commit A and B

The G1 manifest binds the baseline and exact expected Commit A/B scope. Commit A's actual commit and
tree hashes cannot safely be embedded in the earlier baseline manifest unless they are precomputed
without circular metadata. Instead:

1. manifest binds the exact allowed paths, expected file/tree/diff hashes and authorizing scope;
2. Commit A receipt records actual parent/commit/tree/diff hashes and proves equality to the
   manifest expectation;
3. Commit B records independent validation over Commit A and the original manifest hash;
4. any amended Commit A or changed evidence invalidates G1 and requires a new manifest/review.

### 6.3 Commit C

Commit C is not covered by the G1 manifest. After Commit B, G2 requires a separate activation
manifest/envelope binding:

- validated Commit B input;
- `PRE_SWITCH_COMMIT`;
- exact pointer diff and expected result tree;
- rollback rehearsal and Rollback Owner;
- independent validation and new Human Authority Owner authorization.

```text
G1_MANIFEST_AUTHORIZES_COMMIT_A_B_ONLY=true
G1_MANIFEST_AUTHORIZES_COMMIT_C=false
COMMIT_C_REQUIRES_SEPARATE_G2_MANIFEST=true
```

## 7. Complexity Encapsulation Check

Role records, tree inventories, per-file hashes and validation receipts remain internal governance
details. Users, external developers and ecosystem consumers receive no new interface.

Agents may receive one simple machine-readable readiness envelope rather than the entire internal
mechanism:

```text
roles.assigned
roles.separation_pass
baseline.defined
baseline.clean
manifest.id
manifest.sha256
manifest.verified
rollback.ready
g1.reconfirmation
g1.effective
reason_codes[]
evidence_refs[]
limitations[]
```

This envelope must link to full evidence and may not hide conflicts or failed checks. Agent-readable
does not mean exposing internal complexity as a public API, nor does it authorize external use.

```text
INTERNAL_GOVERNANCE_COMPLEXITY=ENCAPSULATED_NOT_HIDDEN
USER_INTERFACE_CHANGED=false
AGENT_CAPABILITY_INTERFACE_CHANGED=false
EXTERNAL_ECOSYSTEM_INTERFACE_CHANGED=false
```

## 8. G1 Revalidation Requirement

G1 can become effective only when all of the following are simultaneously true:

```text
DECISION_TRUTH_ALIGNMENT=PASS
BASELINE_DEFINED=true
BASELINE_VALIDATION=PASS_NO_MUTATION
MANIFEST_DESIGN_ACCEPTED=true
MANIFEST_CREATED=true
MANIFEST_VERIFIED=true
MANIFEST_FROZEN_FOR_G1=true
ROLES_ASSIGNED=true
ROLE_SEPARATION_CHECK=PASS
ROLLBACK_REFERENCE_DEFINED=true
HUMAN_G1_RECONFIRMATION=true
```

The human reconfirmation must bind the exact baseline commit/tree, manifest SHA-256, A/B allowlist
digest, role assignment record hashes, rollback reference, scope, expiry and one-use rule.

Current result:

```text
DECISION_TRUTH_ALIGNMENT=PASS
BASELINE_DEFINED=false
MANIFEST_DESIGN_ACCEPTED=false
MANIFEST_CREATED=false
MANIFEST_VERIFIED=false
ROLES_ASSIGNED=false
ROLLBACK_REFERENCE_DEFINED=false
HUMAN_G1_RECONFIRMATION=false
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
```

Validator PASS, design completion or prior human intent cannot substitute for the final bound human
reconfirmation.

## 9. Human Review Checklist

Human review should decide:

1. whether the mandatory/conditional role separation matrix is accepted;
2. the future stable identity and appointment mechanism for each role;
3. whether the canonical manifest fields and hashing rules are sufficient;
4. the detached evidence retention location and owner;
5. whether G1 and G2 must use separate manifests as designed;
6. whether Phase 0.5.6G-4 may prepare baseline reconstruction without creating it.

No role assignment or manifest lifecycle transition occurs merely because the design is accepted.

## 10. Final Status

```text
ROLE_MANIFEST_PREPARATION_STATUS=COMPLETE
ROLE_SEPARATION_RULES=COMPLETE_FAIL_CLOSED
MANIFEST_DESIGN=COMPLETE
MANIFEST_LIFECYCLE=COMPLETE_DESIGN
ROLES_ASSIGNED=false
MANIFEST_CREATED=false
BASELINE_CREATED=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
G1_EFFECTIVE=false
PHASE_0_5_7A_AUTHORIZED=false
AUTHORITY_CHANGED=false
CODE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_ROLE_AND_MANIFEST_PREPARATION
```

## 11. Validation and Scope Boundary

Task baseline before report creation:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=89
BASELINE_STATUS_SHA256=14c5f0a123daeab3fc2ea66764b3ff6d4c178e31a28e4ba6f024086f74dc1f8a
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

Final validation and isolation result:

```text
SAEE_PROJECT_MEMORY_CHECK=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
GIT_DIFF_CHECK=PASS
FINAL_STATUS_ENTRIES=90
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=89
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=14c5f0a123daeab3fc2ea66764b3ff6d4c178e31a28e4ba6f024086f74dc1f8a
AUDIT_INPUT_HASH_GROUPS_UNCHANGED=6/6
ONLY_NEW_STATUS_ENTRY=reports/SAEE_ROLE_ASSIGNMENT_AND_IMMUTABLE_MANIFEST_PREPARATION.md
PRE_EXISTING_PATHS_MODIFIED_BY_THIS_PHASE=0
STAGED_TASK_FILES=0
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
PR_CREATED=false
```

The unchanged status digest excluding this report demonstrates that the pre-existing dirty worktree
was preserved byte-for-byte at the Git status surface. The six unchanged input hash groups confirm
that the reviewed Project Memory, constitution-migration family, capability truth source, active
constitution and preparation inputs were not modified by this phase.
