# SAEE Authority Migration Preflight Resolution Plan

```text
report_id=SAEE_AUTHORITY_MIGRATION_PREFLIGHT_RESOLUTION_PLAN
phase=Phase_0.5.6B
plan_mode=DESIGN_ONLY_NOT_EXECUTION
current_effective_authority=SAEE_Development_Constitution_v1.1
v2_status=APPROVED_DESIGN_DIRECTION_NOT_ACTIVE
authority_migration_authorized=false
authority_switch_executed=false
```

本计划把 Phase 0.5.6 的四个硬阻塞转化为顺序化、可验证、可回滚的 future execution
gates。它不关闭 blocker 本身，不修改任何权威或事实表面，也不授权 Phase 0.5.7。

## 1. Planning Boundary

当前可确认：

- v1.1 是唯一 active repository development authority；
- v2 layered identity、Trust Semantic 和三产品方向已有人工设计批准证据；
- v2 仍是 non-normative successor draft；
- capability manifest、product truth、MCP truth、ecosystem truth 和 code 均不因本计划变化；
- 当前 dirty worktree 不应被清理、reset、stash、rebase 或直接转化为 migration baseline。

```text
BLOCKER_001_RESOLVED=false
BLOCKER_002_RESOLVED=false
BLOCKER_003_RESOLVED=false
BLOCKER_004_RESOLVED=false
PHASE_0_5_7_AUTHORIZED=false
```

## 2. Blocker 001 — Project Memory Truth Alignment

### 2.1 Current mismatch

Phase 0.5.4 preparation evidence records that `V2-F-001..V2-F-005` received explicit human design
approval. However:

- `v2-transition-decisions.md` still records five `PROPOSED_FREEZE` decisions and five
  `human_confirmation=REQUIRED` entries;
- `active-questions.md` still records `Q-V2-001` as open and `Q-V2-002` as blocked because the five
  decisions are unconfirmed;
- `decision-log.md` records Trust Semantic approval but not a canonical outcome for all five V2
  decisions;
- `scripts/saee_project_memory_check.py` validates fixed closed sets `F-001..005`, `Q-001..003` and
  `D-001..005`; it does not validate `V2-F-*`, `Q-V2-*` or additional decision IDs.

Therefore the current validator PASS proves legacy Project Memory structure, not V2 decision truth
alignment.

### 2.2 Decision status state machine

The decision lifecycle and authority lifecycle must remain separate:

```text
Decision lifecycle

PROPOSED
    ↓ explicit human design decision
APPROVED_DESIGN_DIRECTION
    ↓ explicit human freeze decision + required DCP linkage
FROZEN

Authority-family lifecycle

INACTIVE_CANDIDATE
    ↓ complete family + validation + independent activation authorization
ACTIVE_AUTHORITY
```

`ACTIVE_AUTHORITY` is not an individual decision status. It describes the authority family after an
atomic pointer switch. It must never overwrite a `FROZEN` decision or be inferred from Project
Memory alone.

| State | Allowed Project Memory surface | Authority effect | Human approval |
|---|---|---|---|
| `PROPOSED` | `v2-transition-decisions.md`, open question | none | not required to propose |
| `APPROVED_DESIGN_DIRECTION` | transition record + append-only decision receipt; related active question becomes resolved/archived | none | explicit design approval required |
| `FROZEN` | versioned `V2-F-*` frozen record linked to evidence and DCP where an existing Frozen Decision is affected | none by itself | explicit freeze approval required |
| `ACTIVE_AUTHORITY` | `current-state.md` projection + append-only activation receipt only after authoritative pointers and effective commit exist | activates no capability facts | separate activation approval required |

### 2.3 Frozen Decision boundary

- Existing `F-001..F-005` must not be edited, deleted or implicitly superseded.
- If a V2 decision changes an existing Frozen Decision, create a Decision Change Proposal naming the
  exact affected IDs, new evidence, impact, non-claims and rollback.
- If a V2 decision only restates an existing Frozen Decision, link it without creating a conflicting
  duplicate.
- Use the `V2-F-*` namespace for the V2 decision family; do not reuse legacy `F-*` IDs.
- `FROZEN` still does not mean v2 is active.

### 2.4 Future authorized alignment batch

The future alignment batch should be atomic and limited to:

1. update each `V2-F-001..005` outcome from `PROPOSED` to the human-confirmed design status;
2. create any required DCP linkage before freezing a decision that affects `F-001..005`;
3. record the five outcomes through an append-only decision receipt with evidence date and owner;
4. close `Q-V2-001` and rewrite `Q-V2-002` to its actual remaining blockers without deleting its
   historical evidence;
5. update the Project Memory current-state projection without changing capability/product facts;
6. version the Project Memory validator and tests so `V2-F-*`, `Q-V2-*` and new decision receipts are
   positively validated and invalid transitions are rejected;
7. run the old and new validation fixtures to prove historical entries remain valid.

The exact files and validator changes require a separate, human-approved allowlist. Until then no
Project Memory content changes are allowed.

### 2.5 Exit gate

```text
DECISION_APPROVAL_EVIDENCE=BOUND_TO_V2_F_001_THROUGH_V2_F_005
PROJECT_MEMORY_V2_DECISION_STATUS=APPROVED_DESIGN_DIRECTION_OR_FROZEN_AS_AUTHORIZED
LEGACY_FROZEN_DECISIONS=UNCHANGED_OR_DCP_LINKED
V2_ACTIVE_AUTHORITY_INFERRED_FROM_MEMORY=false
PROJECT_MEMORY_VALIDATOR_COVERS_V2_IDS=true
ACTIVE_V2_QUESTIONS_MATCH_CURRENT_BLOCKERS=true
DECISION_TRUTH_ALIGNMENT_PLAN=COMPLETE
```

## 3. Blocker 002 — Clean Isolated Migration Baseline

### 3.1 Principle

Do not clean the current dirty worktree. Do not use `git reset`, checkout restoration, stash,
mass staging or deletion to manufacture cleanliness. The current worktree remains an evidence source
whose existing changes belong to their original owners.

### 3.2 Baseline source selection

`HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc` is the current committed anchor, but it is not
automatically the migration baseline because many approved preparation surfaces are not represented
by that commit. The future baseline source must be selected through this sequence:

1. identify the latest commit with reproducible v1.1 family and mainline checks;
2. enumerate every required preflight artifact and classify it as committed, approved uncommitted,
   unrelated dirty or excluded;
3. reconstruct only approved inputs in a separate stabilization/migration worktree using
   content-addressed patches or approved commits;
4. produce a new candidate baseline commit only after its exact contents and lineage are human
   approved;
5. record that immutable commit as `MIGRATION_BASELINE_COMMIT`.

```text
CURRENT_HEAD_IS_AUTOMATIC_MIGRATION_BASELINE=false
MIGRATION_BASELINE_COMMIT=UNRESOLVED
```

### 3.3 Migration worktree design

Future candidate naming:

```text
branch=codex/saee-v2-authority-migration-v2-0
worktree=<separate approved path outside the current working tree>
```

The branch/worktree must be created only after explicit Git authorization. Creation is not
authorized by this plan.

Required properties:

- `git status --porcelain` is empty at the baseline;
- baseline branch starts from the approved immutable commit;
- no files are copied wholesale from the dirty worktree;
- each approved uncommitted input has a path, SHA-256, source/owner and reason;
- unrelated dirty files are excluded, not deleted;
- all validation commands run without changing tracked or untracked state.

### 3.4 Immutable input manifest

The future baseline manifest must include:

| Field | Requirement |
|---|---|
| baseline commit | full 40-character hash |
| parent/source lineage | source commit(s) and approved patch IDs |
| input inventory | exact allowlisted paths |
| input digests | SHA-256 for every Constitution, contract, schema, gate, validator, Project Memory and pointer input |
| capability digest | canonical inventory hash, expected change `NONE` |
| product/MCP digest | status baselines, expected change `NONE` |
| external state | timestamped narrow snapshots or explicitly excluded |
| owners | baseline owner, executor, independent reviewer, rollback owner |

### 3.5 Validation snapshot and rollback reference

Before any authority-family work:

```text
V1_1_CONSTITUTION_CHECK=PASS
PROJECT_MEMORY_CHECK=PASS
GOVERNANCE_REGISTRY_CHECK=PASS
CAPABILITY_LEDGER_CHECK=PASS
MAINLINE_GUARD=PASS_READ_ONLY
WORKTREE_CLEAN_BEFORE=PASS
WORKTREE_CLEAN_AFTER=PASS
```

Record two rollback references:

1. `MIGRATION_BASELINE_COMMIT`: start of inactive-family construction;
2. `PRE_SWITCH_COMMIT`: last validated commit before active pointer switch.

Neither reference authorizes a destructive reset. Rollback uses a new correction/revert commit.

### 3.6 Exit gate

```text
CURRENT_DIRTY_WORKTREE_CLEANED=false
CLEAN_ISOLATED_WORKTREE_CREATED=true
MIGRATION_BASELINE_COMMIT_RECORDED=true
IMMUTABLE_INPUT_MANIFEST=PASS
UNRELATED_DIRTY_CHANGE_COUNT=0
ROLLBACK_REFERENCES_RECORDED=true
VALIDATION_SNAPSHOT=PASS
MIGRATION_BASELINE_PLAN=COMPLETE
```

All values above except the plan status are future exit criteria and currently `NOT_EXECUTED`.

## 4. Blocker 003 — Authority Family Completion

### 4.1 Family structure

The inactive v2.0 authority family must be complete before activation authorization:

| Role | Future candidate | Required boundary |
|---|---|---|
| human-readable authority | `docs/architecture/SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_0.md` | additive successor; v1.1 preserved |
| machine-readable contract | `agent-interface/governance/saee-development-and-ecosystem-constitution.v2.0.json` | closed projection, not second Constitution |
| closed schema | `schemas/saee-development-and-ecosystem-constitution.schema.v2.0.json` | deterministic validation, no implicit fields |
| migration recommendation gate | versioned v2 migration/development gate | Agent recommendation and non-claims |
| v2 deterministic validator | `scripts/saee_development_and_ecosystem_constitution_v2_smoke.py` | positive/negative fixtures, no state mutation |
| authority consistency validator | `scripts/saee_authority_consistency_check.py` | current/expected pointer model and split-brain rejection |

The four requested family components are therefore supplemented by a closed schema and a dedicated
v2 validator because v1.1 Article 17 requires authority document, machine contract, schema,
recommendation gate and deterministic smoke to move together.

### 4.2 Authority document requirements

The v2.0 document must freeze:

- Theory Identity, Engineering Core and SAEE Architecture relationship;
- Product Identity and exactly three target customer versions;
- five readiness architecture layers;
- Trust Semantic as a bounded technical semantic role, not an identity/capability;
- Trust Claim as an Evidence/Evaluation relation, not an Object/Schema/Tool;
- OTel as optional Observation Source;
- controlled SAEE / Agent Evidence integration mainline;
- canonical capability fact-source pointer;
- historical preservation, external-action boundary and comprehensive Non-Claims;
- `supersedes` relationship and activation conditions without pretending activation occurred.

### 4.3 Machine contract and schema

The contract must be a closed, canonical projection with at least:

```text
constitution_id
version=2.0
status=inactive_candidate
supersedes
identity_hierarchy
engineering_core
program_mainline
readiness_architecture_layers
target_customer_versions
trust_semantic_role
trust_claim_relation
capability_fact_source
authority_precedence
historical_preservation
external_action_boundary
claims
non_claims
activation_requirements
```

The schema must reject unknown fields, missing non-claims, a fourth product, Trust Semantic as highest
identity/capability, SECO as implemented, capability status facts and mixed authority state.

### 4.4 Deterministic validators

The v2 validator must verify document/contract/schema equivalence and reject at least:

1. Trust Semantic replacing Theory or Engineering identity;
2. governance/audit/ecosystem secondary lane replacing the integration mainline;
3. a sixth Trust runtime/authority layer;
4. Trust Claim Object/Schema/Capability/MCP claims;
5. SECO implemented/runtime claims;
6. Autonomous as fourth target product;
7. authority migration changing canonical capability facts;
8. OTel compliance/authenticity/OTLP claims without evidence;
9. official integration, listing or production status promotion;
10. deletion of the v1.1 historical family.

The Authority Consistency Check must validate both current inactive mode and simulated expected active
mode without editing repository pointers. It must reject every mixed v1.1/v2 pointer combination.

### 4.5 Construction and activation separation

Inactive-family construction and pointer activation must be separate reviewed batches:

```text
Batch C1 = add inactive v2.0 family + validators; no active pointer changes
Batch C2 = validate v1.1, v2.0 and coexistence; no active pointer changes
Batch D  = independent human activation authorization
Batch E  = atomic pointer switch only
```

### 4.6 Exit gate

```text
CONCRETE_V2_VERSION=2.0
V2_AUTHORITY_DOCUMENT=VALID_INACTIVE_CANDIDATE
V2_MACHINE_CONTRACT=PASS
V2_CLOSED_SCHEMA=PASS
V2_RECOMMENDATION_GATE=PASS
V2_DETERMINISTIC_VALIDATOR=PASS
AUTHORITY_CONSISTENCY_CHECK=PASS
V1_1_V2_COEXISTENCE=PASS
CANONICAL_CAPABILITY_DIGEST=NO_CHANGE
V2_ACTIVE=false
AUTHORITY_FAMILY_COMPLETION_PLAN=COMPLETE
```

All family artifacts remain uncreated by this plan.

## 5. Blocker 004 — Activation and Rollback Closure

### 5.1 Activation allowlist

Only after Phases A-C pass and a separate human activation authorization is recorded may the atomic
pointer switch touch:

```text
AGENTS.md
.codex/rules.md
.codex/current_state.md
llms.txt
README.md authority entry only
governance/README.md authority/read-order entry only
agent-index.json authority entry only
scripts/mainline_guard.py authority routing only
```

An activation receipt may be appended to authorized Project Memory only after the switch validates.
The pointer batch must not include:

- `capability-package/manifest.json` or capability projection status changes;
- product, MCP, external-system or asset registry changes;
- application/runtime code, schemas unrelated to the already validated authority family, website or
  ecosystem adapter changes;
- cleanup of unrelated dirty files;
- Evidence lineage rewrites or source repository changes.

### 5.2 Activation acceptance

Pre-switch requirements:

```text
DECISION_TRUTH_ALIGNMENT=PASS
CLEAN_ISOLATED_BASELINE=PASS
INACTIVE_V2_AUTHORITY_FAMILY=PASS
V1_1_VALIDATOR=PASS
V2_VALIDATOR=PASS
AUTHORITY_CONSISTENCY_CHECK=PASS
NEGATIVE_CASES=PASS
CANONICAL_CAPABILITY_DIGEST=NO_CHANGE
ROLLBACK_DRY_RUN=PASS
UNRELATED_DIRTY_CHANGE_COUNT=0
EXACT_ACTIVATION_DIFF=APPROVED
HUMAN_ACTIVATION_AUTHORIZATION=GRANTED
```

The switch must be one narrow commit. Post-switch all active pointers must resolve to the same v2.0
family and effective commit, while v1.1 remains readable as historical/rollback authority.

### 5.3 Rollback plan

Rollback triggers include:

- any mixed active pointer;
- v2 document/contract/schema mismatch;
- v1.1 historical family missing;
- canonical capability digest drift;
- mainline, identity, product-family or Non-Claims drift;
- validator mutation of repository state;
- unrelated file in the activation diff;
- post-switch required check failure.

Rollback procedure:

1. stop all later semantic/ecosystem work;
2. identify `PRE_SWITCH_COMMIT` and failed activation commit;
3. create an explicitly authorized correction/revert commit restoring all pointer allowlist files to
   v1.1 consistently;
4. keep v2 artifacts present but mark the family inactive/failed candidate; do not delete it;
5. rerun v1.1, Project Memory, governance, capability ledger, mainline and consistency checks;
6. prove canonical inventory and Evidence lineage hashes remain unchanged;
7. append failure reason, failed commit, rollback commit and unresolved blocker to the decision log;
8. do not use destructive reset, history rewrite or force push.

### 5.4 Owner model

| Role | Responsibility | May not do |
|---|---|---|
| Human Authority Owner | approves decision freeze, exact allowlists, activation and rollback | infer approval from validator PASS |
| Baseline Owner | attests source lineage, immutable manifest and clean worktree | approve own activation alone |
| Migration Executor | applies only approved C/E batches | broaden scope or self-authorize |
| Independent Validation Reviewer | verifies validators, hashes, negative cases and exact diff | modify the batch being reviewed |
| Rollback Owner | holds pre-switch reference and executes authorized correction | use destructive history operations |
| Evidence Recorder | records receipts, commits, hashes and staged truth | become capability/product/external fact authority |

One person may hold multiple operational roles only if the Human Authority Owner still performs a
separate explicit approval and the record shows which role acted at each gate.

### 5.5 Exit gate

```text
ACTIVATION_ALLOWLIST_FROZEN=true
OWNER_MODEL_CONFIRMED=true
ROLLBACK_OWNER_CONFIRMED=true
ROLLBACK_DRY_RUN=PASS
PRE_SWITCH_COMMIT_RECORDED=true
INDEPENDENT_REVIEW=PASS
HUMAN_ACTIVATION_AUTHORIZATION=GRANTED
ACTIVATION_ROLLBACK_PLAN=COMPLETE
```

All values above except the plan status are future exit criteria and currently `NOT_EXECUTED` or
`NOT_GRANTED`.

## 6. Migration Safety Impact

| Protected truth | Plan effect | Required invariant |
|---|---|---|
| v1.1 history | no change; future additive successor | Constitution/contract/schema/gate/validator retained |
| Git history | no change; future correction/revert only | no reset, rewrite, deletion or force push |
| Evidence lineage | no change | names, digests, provenance and source boundaries preserved |
| capability truth | no change | canonical inventory remains sole fact source; digest frozen |
| product truth | no change | exactly three targets; implementation/release statuses unchanged |
| MCP truth | no change | interface classifications and canonical server remain unchanged |
| ecosystem truth | no change | no official integration/listing/adoption/production promotion |
| current dirty worktree | no cleanup | isolate rather than mutate |

```text
V1_1_HISTORY_IMPACT=NONE
GIT_HISTORY_IMPACT=NONE
EVIDENCE_LINEAGE_IMPACT=NONE
CAPABILITY_TRUTH_IMPACT=NONE
PRODUCT_TRUTH_IMPACT=NONE
MCP_TRUTH_IMPACT=NONE
ECOSYSTEM_TRUTH_IMPACT=NONE
MIGRATION_SAFETY_IMPACT=PASS_DESIGN_ONLY
```

## 7. Future Execution Sequence

```text
Phase A — Decision Truth Alignment
        ↓
Phase B — Clean Isolated Baseline
        ↓
Phase C — Inactive Authority Family Completion
        ↓
Phase D — Independent Activation Authorization
        ↓
Phase E — Atomic Authority Switch
```

| Phase | Input | Output gate | Current status |
|---|---|---|---|
| A | human V2 approval evidence + Project Memory policy | `DECISION_TRUTH_ALIGNMENT=PASS` | `NOT_EXECUTED` |
| B | approved source lineage + exact input manifest | `CLEAN_ISOLATED_BASELINE=PASS` | `NOT_EXECUTED` |
| C | successor draft + frozen v2.0 family design | `INACTIVE_V2_AUTHORITY_FAMILY=PASS` | `NOT_EXECUTED` |
| D | A-C evidence + rollback rehearsal + exact activation diff | `HUMAN_ACTIVATION_AUTHORIZATION=GRANTED` | `NOT_EXECUTED` |
| E | approved atomic allowlist + pre-switch commit | `V2_ACTIVE_POINTERS_CONSISTENT=PASS` | `NOT_EXECUTED` |

Failure in any phase stops later phases. Phase E completion would only change repository development
authority; it would not authorize ecosystem development, capability status changes or external
actions.

## 8. New Split-Brain Prevention Rules

The preflight plan must not introduce a new authority split:

1. Project Memory records decision state but never activates authority;
2. the human-readable Constitution is authority, while its contract/schema are closed projections;
3. the capability manifest remains the only capability fact source;
4. inactive v2 artifacts may coexist with v1.1 only when every active pointer still names v1.1;
5. active switch is atomic across the exact pointer allowlist;
6. no product, capability, MCP or ecosystem semantic batch is mixed with pointer activation;
7. a PASS report cannot authorize its own execution;
8. rollback keeps the failed v2 candidate for evidence instead of deleting history.

```text
SECOND_CONSTITUTION_AUTHORITY_CREATED_BY_PLAN=false
SECOND_CAPABILITY_FACT_SOURCE_CREATED=false
MIXED_ACTIVE_POINTERS_ALLOWED=false
VALIDATOR_SELF_APPROVAL_ALLOWED=false
```

## 9. Final Gate

The four blocker resolution designs are complete, but the blockers remain unresolved until their
future gates are executed and independently accepted.

```text
PREFLIGHT_PLAN_STATUS=COMPLETE
BLOCKER_001_PLAN=COMPLETE
BLOCKER_002_PLAN=COMPLETE
BLOCKER_003_PLAN=COMPLETE
BLOCKER_004_PLAN=COMPLETE
BLOCKER_001_RESOLVED=false
BLOCKER_002_RESOLVED=false
BLOCKER_003_RESOLVED=false
BLOCKER_004_RESOLVED=false
AUTHORITY_MIGRATION_EXECUTED=false
AUTHORITY_SWITCH=false
CODE_CHANGED=false
PHASE_0_5_7_AUTHORIZED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PREFLIGHT_PLAN
```

## 10. Validation and Change Boundary

Task baseline:

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES=99
BASELINE_STATUS_SHA256=6470a773d30560e63b89d029891ef31de896c04b3556ac5f024e595cf50079c1
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

Required validation commands:

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/saee_project_memory_check.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/saee_governance_registry_check.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/saee_development_constitution_smoke.py
git diff --check
```

All required checks were run before and after report creation. Final scope audit:

```text
FINAL_STATUS_ENTRIES=100
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=99
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=6470a773d30560e63b89d029891ef31de896c04b3556ac5f024e595cf50079c1
AUDIT_INPUT_HASHES_UNCHANGED=21/21
ONLY_NEW_STATUS_ENTRY=reports/SAEE_AUTHORITY_MIGRATION_PREFLIGHT_RESOLUTION_PLAN.md
STAGED_TASK_FILES=0
```

The existing Project Memory validator is expected to PASS its legacy contract; that PASS does not
close Blocker 001 because the validator currently does not cover the V2 ID namespaces described
above.

```text
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
CONSTITUTION_CHANGE=NONE
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
