# SAEE Authority Migration Execution Authorization Package

```text
package_id=SAEE_AUTHORITY_MIGRATION_EXECUTION_AUTHORIZATION_PACKAGE
phase=Phase_0.5.6C
package_mode=AUTHORIZATION_DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
future_candidate=SAEE_Development_and_Ecosystem_Constitution_v2.0
future_candidate_status=APPROVED_DESIGN_DIRECTION_NOT_ACTIVE
authority_migration_authorized=false
authority_switch_authorized=false
```

本授权包定义未来 Phase 0.5.7 的最小执行边界、角色、提交序列、证据与回滚条件。它不是
authorization grant，不执行 Git、Project Memory、authority family 或 pointer 变化。

## 1. Authorization Principle

Authority-family construction and authority activation must never share a blanket authorization.
The future workflow uses two independent human gates:

```text
Gate G1
Authorize inactive-family Commit A and validation Commit B only
        ↓ evidence review
Gate G2
Authorize atomic pointer-switch Commit C only
        ↓ immediate verification
Commit D
Record post-switch verification and activation receipt
```

Gate G1 cannot authorize Commit C. Gate G2 cannot be granted until Commit B identifies exact hashes,
the rollback rehearsal passes and the Human Authority Owner reviews the final pointer diff.

```text
BLANKET_PHASE_AUTHORIZATION_ALLOWED=false
VALIDATOR_PASS_IS_AUTHORIZATION=false
AI_AGENT_MAY_ACT_AS_HUMAN_AUTHORITY_OWNER=false
```

## 2. Migration Scope Allowlist

Every future authorization must bind an exact path list and SHA-256 allowlist digest. The following
paths are candidate scope only; none is currently authorized.

### 2.1 Pre-execution Decision Truth Alignment scope

This is a separate precondition batch, not Commit A or the authority switch:

```text
governance/project-memory/v2-transition-decisions.md
governance/project-memory/active-questions.md
governance/project-memory/current-state.md
governance/project-memory/decision-log.md
governance/project-memory/frozen-decisions.md
governance/project-memory/decision-change-proposals/<exact-human-approved-v2-dcp>.md
scripts/saee_project_memory_check.py
tests/test_project_memory.py
```

Rules:

- `frozen-decisions.md` and a new DCP enter the exact allowlist only if the Human Authority Owner
  explicitly freezes a V2 decision or changes an existing `F-*` decision;
- legacy `F-001..005`, `D-001..005` and their historical text are not silently rewritten;
- validator/test changes are limited to versioned V2 ID/state coverage and transition rejection;
- no Project Memory entry may set `ACTIVE_AUTHORITY` before a successful Commit C;
- this batch must complete and be committed into the approved clean baseline before Gate G1.

### 2.2 Authority Family Files — Commit A

Candidate exact paths:

```text
docs/architecture/SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_0.md
agent-interface/governance/saee-development-and-ecosystem-constitution.v2.0.json
schemas/saee-development-and-ecosystem-constitution.schema.v2.0.json
docs/strategy/SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_0_RECOMMENDATION_GATE.md
scripts/saee_development_and_ecosystem_constitution_v2_smoke.py
scripts/saee_authority_consistency_check.py
tests/test_saee_development_and_ecosystem_constitution_v2.py
tests/test_saee_authority_consistency.py
```

If deterministic fixtures are needed, their exact paths and hashes must be added to the human
authorization record before execution. Globs, directories and “related files” are not valid
allowlist entries.

Commit A creates a complete inactive family. It must contain:

- one human-readable v2.0 authority candidate;
- one closed machine contract and matching schema;
- one migration/development recommendation gate;
- one deterministic v2 validator and tests;
- one cross-surface Authority Consistency Check and mixed-pointer tests.

Commit A must not change any active authority pointer.

### 2.3 Validation Evidence Files — Commit B

Candidate new report paths:

```text
reports/SAEE_V2_AUTHORITY_FAMILY_VALIDATION_REPORT.md
reports/SAEE_V2_AUTHORITY_SWITCH_SIMULATION_REPORT.md
reports/SAEE_V2_ROLLBACK_REHEARSAL_REPORT.md
```

Commit B records read-only validation evidence over Commit A. It must not modify Commit A artifacts,
active pointers, Project Memory decisions, capability/product/MCP facts or runtime code. If
validation finds a defect, stop and create a separately reviewed correction commit before producing
a replacement Commit B.

### 2.4 Pointer Files — Commit C

The atomic switch candidate allowlist is exactly:

```text
AGENTS.md
.codex/rules.md
.codex/current_state.md
llms.txt
README.md
governance/README.md
governance/constitution-migration/authority-pointer-map.md
agent-index.json
scripts/mainline_guard.py
```

File-level inclusion does not authorize arbitrary edits:

| Path | Authorized future field/scope |
|---|---|
| `AGENTS.md` | authority family pointers and unchanged startup/mainline rules |
| `.codex/rules.md` | active authority pointer/routing only |
| `.codex/current_state.md` | active authority snapshot only |
| `llms.txt` | top authority discovery block only |
| `README.md` | authority reference and bounded identity explanation only |
| `governance/README.md` | authority/read-order pointer only |
| `authority-pointer-map.md` | switch status and concrete v2.0 mapping only |
| `agent-index.json` | additive v2 authority entry and active-authority selector only; capability ledger untouched |
| `scripts/mainline_guard.py` | route active v2/consistency checks while retaining v1.1 history and mainline guards |

Commit C cannot include authority-family construction, semantic cleanup, product copy, ecosystem
copy, formatting refactors or unrelated documentation changes.

### 2.5 Memory and Post-switch Evidence Files — Commit D

Candidate scope:

```text
reports/SAEE_V2_AUTHORITY_ACTIVATION_ACCEPTANCE_REPORT.md
governance/project-memory/current-state.md
governance/project-memory/decision-log.md
governance/constitution-migration/migration-checklist.md
```

Commit D records the actual Commit C hash, post-switch validator results, activation decision and
remaining non-claims. It does not perform the pointer switch. A Git commit cannot embed its own final
commit hash without a self-reference problem, so the actual Commit C hash belongs in Commit D.

Between C and D there is a provisional local-only window:

```text
ACTIVATION_PROVISIONAL_WINDOW=COMMIT_C_TO_COMMIT_D
PUSH_ALLOWED_DURING_PROVISIONAL_WINDOW=false
PR_ALLOWED_DURING_PROVISIONAL_WINDOW=false
DEPLOY_ALLOWED_DURING_PROVISIONAL_WINDOW=false
EXTERNAL_CLAIM_ALLOWED_DURING_PROVISIONAL_WINDOW=false
```

If post-switch validation fails, Commit D becomes a failure/rollback receipt only after the rollback
commit is created.

### 2.6 Allowlist status

```text
ACTIVATION_ALLOWLIST=CANDIDATE_EXACT_PATHS_DESIGNED
ACTIVATION_ALLOWLIST_AUTHORIZED=false
DIRECTORY_GLOB_AUTHORIZATION=false
UNLISTED_FILE_CHANGE_ALLOWED=false
```

## 3. Forbidden Change Set

The following are forbidden in every authority migration batch unless a later, independent workflow
explicitly authorizes them outside this migration:

| Forbidden change | Protected surface/boundary |
|---|---|
| capability status change | `capability-package/manifest.json#canonical_inventory` |
| capability ledger status change | `agent-index.json#capability_progress_ledger_v1` |
| product version/status change | `governance/registry/product-registry.json` |
| MCP tool/server/classification change | `governance/registry/mcp-registry.json` and MCP scripts |
| Trust capability, Trust Object, Trust Schema or Trust MCP creation | all capability/object/schema/tool surfaces |
| unrelated schema work | all schemas except the exact v2 authority schema in Commit A |
| application/runtime refactor | `saee_backend/`, service/adapter/CLI code and tests unrelated to authority validators |
| website/public copy changes | website and deployment surfaces |
| official integration/listing/adoption/production claims | external, marketplace and public status surfaces |
| Evidence/source lineage rewrite | Evidence artifacts, external repositories and provenance records |
| dirty-worktree cleanup | current worktree user-owned changes |
| external Git action | push, PR, release, tag or deployment without separate authorization |

The only governance-code exceptions are exact validator/test paths in the approved Commit A or
Decision Truth batch and the authority-routing-only `scripts/mainline_guard.py` change in Commit C.

```text
FORBIDDEN_CHANGE_SET=FROZEN
CAPABILITY_MANIFEST_CHANGE_ALLOWED=false
PRODUCT_REGISTRY_CHANGE_ALLOWED=false
MCP_CHANGE_ALLOWED=false
APPLICATION_CODE_CHANGE_ALLOWED=false
WEBSITE_CHANGE_ALLOWED=false
EXTERNAL_CLAIM_CHANGE_ALLOWED=false
```

## 4. Role Separation Model

| Role | May do | May approve | Must not do |
|---|---|---|---|
| Human Authority Owner | review evidence, bind scope/hash/roles, grant or deny G1/G2 and rollback authority | only role that grants authority activation | act by implication or treat validator PASS as approval |
| Migration Executor | create approved worktree and apply exact authorized commits | nothing | expand allowlist, validate own work as independent, self-authorize |
| Independent Validator | run read-only validators, compare hashes/diffs, sign PASS/BLOCKED receipt | validation result only, not activation | edit the batch, waive a failed check, become Executor for same commit |
| Rollback Owner | hold baseline/pre-switch refs and execute pre-authorized correction commit on trigger | rollback execution within pre-approved trigger set | reset/rewrite/force-push or delete v2 evidence |
| Evidence Recorder | record commands, hashes, outputs, approvals, commit/rollback receipts | nothing | become a capability/product/external-state authority |

Mandatory separation:

```text
HUMAN_AUTHORITY_OWNER_IS_HUMAN=true
MIGRATION_EXECUTOR_MAY_SELF_APPROVE=false
INDEPENDENT_VALIDATOR_EQUALS_EXECUTOR=false
ROLLBACK_OWNER_IDENTIFIED_BEFORE_COMMIT_C=true
EVIDENCE_RECORDER_GRANTS_AUTHORITY=false
```

If one human holds multiple operational roles, each action must still be role-stamped, and a separate
Independent Validator must review Commit C. No AI Agent, report or validator can substitute for the
Human Authority Owner.

```text
ROLE_MODEL=FROZEN_CANDIDATE_PENDING_HUMAN_APPROVAL
```

## 5. Commit Boundary

### Precondition — Approved clean baseline

Before Commit A, Decision Truth Alignment must be committed and validated on a clean isolated
migration worktree. The baseline commit, input manifest, capability digest and rollback refs must be
recorded. The current dirty worktree is never Commit A's source by default.

### Commit A — Inactive v2 Authority Family

```text
purpose=ADD_COMPLETE_INACTIVE_V2_0_FAMILY
active_pointer_change=false
capability_fact_change=false
status=NOT_EXECUTED
```

### Commit B — Validation Evidence

```text
purpose=RECORD_V1_1_V2_COEXISTENCE_NEGATIVE_CASE_AND_ROLLBACK_REHEARSAL_EVIDENCE
authority_artifact_change=false
active_pointer_change=false
status=NOT_EXECUTED
```

Commit B's hash and report digests become mandatory inputs to Gate G2.

### Commit C — Atomic Authority Switch

```text
purpose=SWITCH_ALL_ACTIVE_POINTERS_TO_ONE_CONCRETE_V2_0_FAMILY
requires_gate=G2_HUMAN_ACTIVATION_AUTHORIZATION
mixed_pointer_state_allowed=false
status=NOT_EXECUTED
```

Commit C is one commit and only the exact pointer allowlist may change. No amend, squash or scope
growth is allowed after G2 without invalidating authorization and returning to review.

### Commit D — Post-switch Verification

```text
purpose=RECORD_COMMIT_C_HASH_POST_SWITCH_RESULTS_AND_ACTIVATION_RECEIPT
pointer_change=false
status=NOT_EXECUTED
```

Commit D is created only if all post-switch checks pass. If any check fails, create rollback Commit R
first and record a failure receipt instead.

### Commit R — Correction/Revert Rollback

```text
purpose=RESTORE_ALL_ACTIVE_POINTERS_TO_PRE_SWITCH_V1_1_STATE
deletes_v2_family=false
rewrites_history=false
status=NOT_EXECUTED
```

```text
COMMIT_A_STATUS=NOT_EXECUTED
COMMIT_B_STATUS=NOT_EXECUTED
COMMIT_C_STATUS=NOT_EXECUTED
COMMIT_D_STATUS=NOT_EXECUTED
COMMIT_R_STATUS=NOT_EXECUTED
COMMIT_BOUNDARY=FROZEN_CANDIDATE_PENDING_HUMAN_APPROVAL
```

## 6. Activation Gates

### Gate G1 — Phase 0.5.7 inactive-family execution entry

G1 may authorize only Commit A and Commit B. All conditions must be evidenced:

```text
DECISION_TRUTH_ALIGNMENT=PASS
CLEAN_ISOLATED_BASELINE=PASS
IMMUTABLE_INPUT_MANIFEST=PASS
V1_1_BASELINE_VALIDATION=PASS
CANONICAL_CAPABILITY_DIGEST=RECORDED_NO_CHANGE_EXPECTED
EXACT_A_B_ALLOWLIST=HUMAN_APPROVED
ROLE_ASSIGNMENTS=CONFIRMED
ROLLBACK_REFS=RECORDED
G1_HUMAN_AUTHORIZATION=GRANTED
```

Current status:

```text
G1_HUMAN_AUTHORIZATION=NOT_GRANTED
PHASE_0_5_7_A_B_EXECUTION_AUTHORIZED=false
```

### Gate G2 — Commit C authority switch

G2 is a new authorization decision after Commit B. It requires:

```text
DECISION_TRUTH_ALIGNMENT=PASS
CLEAN_BASELINE_STILL_PASS=true
AUTHORITY_FAMILY=PASS_INACTIVE
V1_1_VALIDATOR=PASS
V2_VALIDATOR=PASS
AUTHORITY_CONSISTENCY_VALIDATOR=PASS
MIXED_POINTER_NEGATIVE_CASES=PASS
ROLLBACK_DRY_RUN=PASS
CANONICAL_CAPABILITY_DIGEST=NO_CHANGE
PRODUCT_MCP_ECOSYSTEM_DIGESTS=NO_CHANGE
COMMIT_B_EVIDENCE_HASH=BOUND
EXACT_COMMIT_C_DIFF=HUMAN_APPROVED
INDEPENDENT_VALIDATOR=PASS
ROLLBACK_OWNER=CONFIRMED
G2_HUMAN_AUTHORIZATION=GRANTED
```

Current status:

```text
G2_HUMAN_AUTHORIZATION=NOT_GRANTED
AUTHORITY_SWITCH_AUTHORIZED=false
```

### Authorization invalidation

Any of the following invalidates G1 or G2 and requires a new human review:

- baseline commit, input hash or allowlist digest changes;
- a role or owner changes;
- any unlisted path enters the diff;
- a validator result changes or becomes non-reproducible;
- Commit A/B is amended after its evidence was approved;
- capability/product/MCP/external truth digest changes;
- rollback reference or procedure changes;
- current authority changes before the authorized action;
- the one-use authorization has already been consumed.

```text
AUTHORIZATION_BINDING=ONE_USE_BASELINE_HASH_SCOPE_ROLE_AND_COMMIT_BOUND
AUTHORIZATION_SCOPE_EXPANSION_ALLOWED=false
ACTIVATION_GATE=DESIGNED_NOT_GRANTED
```

## 7. Rollback Gate

### Rollback triggers

Rollback is mandatory if:

- any active pointer remains on v1.1 while another points to v2.0;
- any required post-switch validator fails;
- v2 document, contract, schema, gate or validator hashes do not match Commit B evidence;
- v1.1 historical family becomes unreadable;
- canonical capability, product, MCP or external-state truth changes;
- mainline, identity, Trust Semantic, product-family or Non-Claims drift is detected;
- an unlisted file appears in Commit C;
- post-switch checks mutate the worktree.

### Rollback authority

Gate G2 must pre-authorize Rollback Owner to create Commit R when a listed trigger occurs. This avoids
leaving a known split-brain state active while waiting for a second discretionary decision. Push/PR
of Commit R still requires the same separate external Git authorization as any other commit.

### Rollback procedure

1. freeze Commit D, later phases, push, PR, release, deployment and external claims;
2. compare Commit C against its parent `PRE_SWITCH_COMMIT`;
3. create Commit R restoring every pointer-allowlist file to the v1.1 value from
   `PRE_SWITCH_COMMIT`;
4. retain Commit A/B and v2 artifacts as inactive failed-candidate evidence;
5. run v1.1, Project Memory, governance, capability ledger, mainline and authority consistency
   checks;
6. prove canonical capability and Evidence lineage hashes remain unchanged;
7. record trigger, Commit C, Commit R, validator output and unresolved blocker;
8. do not reset, rewrite history, force push or delete evidence.

### Rollback acceptance

```text
ALL_ACTIVE_POINTERS_RESTORED_TO_V1_1=PASS
V1_1_VALIDATOR=PASS
PROJECT_MEMORY_CHECK=PASS
GOVERNANCE_CHECK=PASS
CAPABILITY_LEDGER_CHECK=PASS
MAINLINE_GUARD=PASS
AUTHORITY_CONSISTENCY_CHECK=PASS_V1_1_ACTIVE
CANONICAL_CAPABILITY_DIGEST=NO_CHANGE
EVIDENCE_LINEAGE=NO_CHANGE
WORKTREE_CLEAN_AFTER_ROLLBACK=PASS
```

```text
RESET_ALLOWED=false
HISTORY_REWRITE_ALLOWED=false
FORCE_PUSH_ALLOWED=false
ROLLBACK_GATE=DESIGNED_NOT_EXECUTED
```

## 8. Evidence Requirements

Every gate and commit receipt must record:

| Evidence | Required value |
|---|---|
| timestamp | timezone-qualified |
| role identity | Human Owner / Executor / Validator / Rollback Owner / Recorder |
| authorization ID | unique, one-use, scope-bound |
| baseline | full commit hash and worktree path |
| input manifest | path, before SHA-256, owner and source lineage |
| allowlist | exact paths plus allowlist digest |
| forbidden set | frozen digest/version |
| commit evidence | parent hash, commit hash, tree hash, exact name-status and patch hash |
| file evidence | before/after hash for every changed file |
| validator evidence | command, executable hash/version, exit code and complete result artifact |
| fact invariants | capability/product/MCP/external truth before/after digests |
| approval record | decision, approver, timestamp, scope, conditions and expiry/one-use marker |
| rollback evidence | pre-switch hash, trigger, owner, rehearsal/actual commit and verification |
| non-claims | no capability/product/ecosystem/production implication |

For Commit C, Commit B must contain the exact expected pointer diff hash. Commit D records the actual
Commit C hash and proves the actual diff equals the approved expected diff.

```text
EVIDENCE_REQUIREMENTS=COMPLETE_DESIGN
MISSING_EVIDENCE_FAILS_CLOSED=true
```

## 9. Current Authorization Decision

This package freezes a candidate authorization design only. It does not grant G1, G2, Git, migration,
activation, rollback execution, push, PR, release or ecosystem authority.

```text
AUTHORIZATION_PACKAGE_STATUS=COMPLETE
AUTHORITY_MIGRATION_AUTHORIZED=false
PHASE_0_5_7_AUTHORIZED=false
PHASE_0_5_7_A_B_EXECUTION_AUTHORIZED=false
AUTHORITY_SWITCH_AUTHORIZED=false
ROLLBACK_EXECUTION_AUTHORIZED=false
CODE_CHANGE=false
POINTER_CHANGE=false
NEXT_ACTION=HUMAN_REVIEW_OF_AUTHORIZATION_PACKAGE
```

## 10. Validation and Change Boundary

Task baseline:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=100
BASELINE_STATUS_SHA256=935de9792ae14fed0a94e63de4d3bd01961de53743949baf4fd95b84edfceff5
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

Required checks:

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/saee_project_memory_check.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/saee_governance_registry_check.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/saee_development_constitution_smoke.py
git diff --check
```

All required checks were run before and after package creation. Final scope audit:

```text
FINAL_STATUS_ENTRIES=101
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=100
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=935de9792ae14fed0a94e63de4d3bd01961de53743949baf4fd95b84edfceff5
AUDIT_INPUT_HASHES_UNCHANGED=20/20
ONLY_NEW_STATUS_ENTRY=reports/SAEE_AUTHORITY_MIGRATION_EXECUTION_AUTHORIZATION_PACKAGE.md
STAGED_TASK_FILES=0
```

```text
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
CONSTITUTION_CHANGE=NONE
V2_SUCCESSOR_CHANGE=NONE
PROJECT_MEMORY_CHANGE=NONE
AUTHORITY_POINTER_CHANGE=NONE
AGENTS_CHANGE=NONE
CAPABILITY_MANIFEST_CHANGE=NONE
SCHEMA_CHANGE=NONE
MCP_CHANGE=NONE
CODE_CHANGE=NONE
PRODUCT_CHANGE=NONE
ECOSYSTEM_STATE_CHANGE=NONE
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
PULL_REQUEST_CREATED=false
```
