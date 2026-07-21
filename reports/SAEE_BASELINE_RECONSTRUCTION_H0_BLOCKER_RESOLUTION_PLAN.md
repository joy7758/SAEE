# SAEE Baseline Reconstruction H0 Blocker Resolution Plan

```text
report_id=SAEE_BASELINE_RECONSTRUCTION_H0_BLOCKER_RESOLUTION_PLAN
requested_phase=Phase_6.1-B1-A3
report_mode=H0_BLOCKER_RESOLUTION_DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
demo_role=integration_evidence_for_existing_SAEE_Evaluation
report_date=2026-07-15
```

## Executive Decision

四个 H0-R blocker 均已形成可执行的 resolution design，但尚未被转换为有效 H0-R
authorization record。当前仍不能创建 branch、worktree、preimage、R1-R4 commits 或 Candidate
B。

本计划将四个 blocker 收敛为以下人工决定：

```text
BLOCKER_001_DECISION=APPROVE_ONE_EXACT_AUTHORITY_SCHEMA_CARRY_FORWARD_EXCEPTION
BLOCKER_002_DECISION=FREEZE_ONE_EXACT_PATH_HUNK_MANIFEST_AND_DIGEST
BLOCKER_003_DECISION=USE_R4_NON_SELF_REFERENTIAL_CANDIDATE_INPUT_MANIFEST_COMMIT
BLOCKER_004_DECISION=BIND_DISTINCT_EXECUTOR_VALIDATOR_AND_HUMAN_ROLLBACK_OWNER
```

只有 Human Authority Owner 在后续 H0-R record 中逐项确认 exact hash、manifest digest、角色和
位置后，才能设置：

```text
FUTURE_H0_R_DECISION=GRANTED
FUTURE_BASELINE_RECONSTRUCTION_EXECUTION_DECISION=AUTHORIZED
```

本报告本身不具有该授权效力。

```text
H0_BLOCKER_RESOLUTION_STATUS=COMPLETE
H0_RESOLUTION_DESIGN=COMPLETE_FAIL_CLOSED
H0_R_READINESS=CONDITIONAL
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
```

本阶段只新增本计划报告。没有修改 Schema 内容、Capability、MCP、Runtime、Evaluation、
Product Registry 或其他现有文件。

## 0. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED
```

Baseline reconstruction 是为了给第一个 Agent Review Demo 提供可信实验起点，不是新的治理
产品或无限延长的治理主线。当前项目主线仍是 controlled SAEE–Agent Evidence integration；
Demo 是 supporting Integration Evidence。

```text
MAINLINE_CORRECTION=CLOSE_ONLY_THE_FOUR_H0_BLOCKERS_THEN_RETURN_TO_BOUNDED_EXECUTION
NO_FURTHER_GOVERNANCE_LAYER_RECOMMENDED=true
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PRODUCT_IDENTITY_CHANGED=false
PHASE_1_AUTHORIZED=false
```

人工接受本计划后，推荐直接进入一个 exact、one-use 的 H0-R authorization decision；不再新增
概念层、产品层或平行 baseline protocol。

## 1. Current State and Pre-image

目标报告创建前：

```text
branch=feat/canonical-capability-inventory-routing-v1
head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
head_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
status_default_entry_count=114
status_all_untracked_entry_count=131
status_default_sha256=b67c5a327b2f9c9d9f8b187838478e3923937232ec5366da69db40fb58b75179
status_all_untracked_sha256=3c54cec1019354f3581ea2fd9e386b1787fa109c3969894d33d2006c70df4357
staged_patch_sha256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
unstaged_patch_sha256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
registered_worktree_count=4
stash_count=0
target_report_preexisting=false
```

Candidate future resources are currently absent：

```text
candidate_branch=codex/phase-6.1-b1-baseline-reconstruction
candidate_branch_exists=false
candidate_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-reconstruction
candidate_worktree_exists=false
candidate_evidence_root=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1
candidate_evidence_root_exists=false
candidate_R4_manifest=reports/SAEE_DEMO_BASELINE_CANDIDATE_INPUT_MANIFEST.json
candidate_R4_manifest_exists=false
```

这些是 H0-R 候选 bindings，不是创建指令。若人工选择其他位置，必须在 H0-R 中记录并重新
计算 role/location manifest digest。

## 2. BLOCKER_001 Resolution — Authority Schema Scope

### 2.1 Conflict

Current source anchor 不包含 active authority schema：

```text
source_anchor_commit=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_anchor_contains_authority_schema=false
authority_complete_requires_authority_schema=true
generic_schema_delta_allowed=false
```

如果机械执行“所有 `schemas/**` 均禁止”，Candidate B 将永远无法达到 v1.1 authority family
`5/5`。如果把它改写为一般 schema 许可，又会给 Demo reconstruction 打开核心契约变化通道。

### 2.2 Exact carry-forward exception

唯一推荐 exception：

```text
path=schemas/saee-development-constitution.schema.v1.1.json
change_type=ADD_EXACT
source_anchor_state=ABSENT
approved_input_role=ACTIVE_V1_1_AUTHORITY_FAMILY_ARTIFACT
approved_input_sha256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
schema_semantic_change=false
capability_schema_change=false
runtime_schema_change=false
other_schema_path_allowed=false
```

Carry-forward 的含义是：future executor 只能把 hash 与上述值完全相同的 bytes 放入 R1；
不能编辑、格式化、升级 `$id`、改变 required/enum/type、重命名文件或产生 v1.2/v2 schema。

### 2.3 Modify versus carry-forward

| Dimension | Modify — forbidden | Exact carry-forward — candidate allowed |
|-|-|-|
| Source | executor 生成或编辑 | 既有、已审查 aggregate input |
| Bytes | 与批准 hash 不同 | SHA-256 完全相同 |
| Semantics | 可能改变 contract | 不改变任何 contract semantics |
| Scope | 可扩展到其他 schema | 单一路径、单一 hash |
| Validation | 新 behavior 需要解释 | Constitution contract/smoke 重现既有 PASS |
| Authority | 可能创设新规则 | 只闭合当前已生效 v1.1 family |

### 2.4 Gate and failure rule

H0-R 必须显式包含：

```text
authority_schema_exception_decision=APPROVED
authority_schema_path=schemas/saee-development-constitution.schema.v1.1.json
authority_schema_sha256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
authority_schema_change_type=ADD_EXACT
```

缺少任一字段或实际 hash 不符：

```text
STOP_REASON=AUTHORITY_SCHEMA_EXACT_BYTE_MISMATCH
H0_R_GRANTED=false
```

```text
BLOCKER_001_RESOLUTION_PLAN=COMPLETE
BLOCKER_001_EXECUTION_CLOSED=false
AUTHORITY_SCHEMA_CONTENT_MODIFIED=false
```

## 3. BLOCKER_002 Resolution — Exact Path/Hunk Manifest

### 3.1 Manifest model

未来 H0-R 必须冻结一个 canonical、sorted、machine-readable execution manifest。每个 entry：

```text
sequence
commit_group=R1|R2|R3|R4
path
change_type=ADD_EXACT|MODIFY_EXACT_HUNKS
anchor_blob=ABSENT|<git_blob_oid>
approved_input_sha256
selected_hunk_ids[]
selected_hunk_sha256[]
explicitly_excluded_hunk_ids[]
truth_role
source_provenance
validator
rollback_rule
```

Manifest serialization 必须使用 UTF-8、sorted paths、stable key order 和 final newline，然后
记录：

```text
path_hunk_manifest_sha256=<future_digest>
```

H0-R 的授权对象是这个 digest，不是本报告里的自然语言列表。

### 3.2 R1 — ADD_EXACT candidate set

下列 5 路径在 source anchor 中均为 `ABSENT`：

| Path | Approved aggregate SHA-256 | Decision |
|-|-|-|
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | `37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c` | R1 candidate |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | `df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0` | R1 candidate |
| `schemas/saee-development-constitution.schema.v1.1.json` | `dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86` | R1 candidate; Blocker 001 exception required |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | `1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c` | R1 candidate |
| `scripts/saee_development_constitution_smoke.py` | `8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550` | R1 candidate |

R1 uses `ADD_EXACT` only。Any source edit invalidates the candidate manifest。

### 3.3 R2 — Project Memory ADD_EXACT candidate set

| Path | Approved aggregate SHA-256 |
|-|-|
| `governance/project-memory/README.md` | `196ba484271c2ee263906be6dd71768763337be506bb2487ba923048dc54d7e9` |
| `governance/project-memory/current-state.md` | `3b4e4b9b0c5f6c93ed55ad91a62c1b92b691642e9d498b797e2781742f143220` |
| `governance/project-memory/frozen-decisions.md` | `f102f6785cc1d31c64ec32790fc68d9db52f76ebb5f3232959fcdccdf0be86f5` |
| `governance/project-memory/active-questions.md` | `a7e8dc0d4c2bdc28b5f1b9ff67bc866cf40a7ca83c1542a907f5c04a4208c4fb` |
| `governance/project-memory/rejected-options.md` | `fbd6e5b55650c6fd0553282547781c85eeb5b077b873ce38cee0f8f1a0fa1615` |
| `governance/project-memory/decision-log.md` | `5ec745db774a63274eb5a9317fdf49f2067b4b73ca0d208c4709900c491eda81` |
| `governance/project-memory/memory-policy.md` | `7b8a1d5c63585294110176e419d4c5c64b5df0849705a799616fbca1b0fbafe6` |
| `governance/project-memory/v2-transition-decisions.md` | `f511f4dc2c15f3b39b399609f878cd51c1b30aaa4cec330f32466aef89773aea` |
| `scripts/saee_project_memory_check.py` | `81b350e9b0358777e473f958dc572b2cda8e3e56f74864b5967a5b8928697c10` |
| `tests/test_project_memory.py` | `11ca4aa238de5483303db97f786a17766a1d53abbdfcd694536c9848468627c4` |

这 10 路径在 anchor 中为 `ABSENT`，只允许 `ADD_EXACT`。Project Memory remains decision
routing，not capability/product/runtime truth。

### 3.4 R2 — MODIFY_EXACT_HUNKS candidate set

Existing files cannot be copied wholesale。The future manifest must select only these semantic
hunks：

| Path | Anchor blob | Candidate selected scope | Explicit exclusions |
|-|-|-|-|
| `governance/README.md` | `e7f01f201fe231b940813f4bd68ec5d07a325b77` | put Project Memory first; add its boundary text/tree entry/check commands | Agent Evidence migration file pointers and merge-readiness commands |
| `AGENTS.md` | `c5e83abfa426de783694e63ab98fd0c857ccbe47` | `Constitutional Program Mainline` section | no other startup/capability/product changes |
| `.codex/current_state.md` | `df9f61aab5626e37efbcc6ae5671a9f800f57847` | v1.1 authority, Evidence-subsystem ownership, non-migration truth, reuse-first focus | commercial/runtime status outside selected lines |
| `.codex/rules.md` | `832826e30f6458ea449294a9bcd3b6c5ba79c039` | Constitution authority section and constitution-first checklist | unrelated permissions or task rules |
| `llms.txt` | `8153556870c8ef76a69cdb86235cf23a94bc631a` | program mainline/secondary, three target versions, target non-claim, drift rule | migration-plan/source/adapter/truth lines unless separately authorized |
| `agent-index.json` | `c2df4fcc63f2479b63d8e2eb1bb7b25af1b83693` | only `development_constitution_v1_1` object | marketplace ordering/status, generated timestamps, capability ledger or any other object |
| `scripts/mainline_guard.py` | `b13e4e6268dd6ee1b2fab1f08a621d81266305d9` | add five v1.1 authority required paths and Constitution smoke invocation | all other guard/runtime/test changes |

The whole-current-file SHA-256 values are review evidence only，not authorization to copy the whole
file：

```text
governance/README.md=93d09d9d7e9651280a1a7132f8c1f122e29131cef4c15e93845558c1924d8b80
AGENTS.md=dda93831c03be32b0698c51bea04b9b6fff045f96c5912db61d08406626bceae
.codex/current_state.md=c70123abe45061080ee20a84aeaa0cec29f5ab4b092c4cbead608878ababf343
.codex/rules.md=c16108b4c15d597e9639fe02a16f2dab42960915d7774dd4328c964a77bcbbd3
llms.txt=e73c61c1bec1282f49ab5f012f77ae83e195b0a19d3688e5e2c90f036b971e07
agent-index.json=1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740
scripts/mainline_guard.py=2f9fc7da6032df51b3696c087f4b7caa22ecc0afb540e9554b2b5417f91edfd8
```

Before H0-R, a read-only manifest compiler must materialize selected lines into patch fragments and
compute each `selected_hunk_sha256`。If a selected semantic hunk cannot be isolated without taking an
excluded line，the manifest fails closed and the path remains unchanged。

### 3.5 R3 — Accepted design inputs ADD_EXACT set

| Path | SHA-256 |
|-|-|
| `reports/SAEE_EVALUATION_MVP_SPECIFICATION.md` | `bb50f1544f7cd51bc1ccb45b60e28219e8af66730843a97f06ca3e0db51b6635` |
| `reports/SAEE_AGENT_REVIEW_DEMO_IMPLEMENTATION_PLAN.md` | `c0eb4dc3aa618d2c537e78e6d936f711db0213c01d4684f9a41a75e8e851f915` |
| `reports/SAEE_AGENT_REVIEW_DEMO_BASELINE_PREPARATION.md` | `12d2c1b360a0babf343deff1353f832f403678844f7bbbf7e4edc8c8aaaf9bb7` |
| `reports/SAEE_AGENT_REVIEW_DEMO_DELTA_MINIMIZATION.md` | `a81e5b3907bc1aa2fa942cfd919b9a53ab92dbea592b68a3c8420f86be235b0c` |
| `reports/SAEE_AGENT_REVIEW_DEMO_EXECUTION_AUTHORIZATION_PACKAGE.md` | `d8782be652c3e20a74886a41bf74d8cd52ce3bf2f8fdeba4324cae9e7a8ed1a0` |
| `reports/SAEE_AGENT_REVIEW_DEMO_BASELINE_CLOSURE_REPORT.md` | `f048d4fa85696efc7a1b6b0d425dc09c2991176383450501d45cfd3312dc3a58` |
| `reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_PREPARATION.md` | `9e659d1939362c5664fe2e342abaeba9d43060f2c5ecb4537ec0b062cd324a1b` |
| `reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZATION_PREPARATION.md` | `a7ff76be14f3bd0e4d29cb0044d2d7332c3c69f25e45c6c65f473f3cfbd582ea` |
| `reports/SAEE_BASELINE_RECONSTRUCTION_H0_BLOCKER_RESOLUTION_PLAN.md` | `<hash_after_human_accepted_final_report>` |

本 A3 report 的 final hash 必须在 human review 后冻结，不能预先自填。所有 R3 reports 都是
design/provenance evidence，不是 capability truth。

### 3.6 Global forbidden path groups

Regardless of candidate allowlist，H0-R manifest must forbid：

```text
capability-package/**
agent-interface/qianfan/**
schemas/**                                    # except one exact R1 authority schema entry
governance/schemas/**
governance/registry/**
.mcp.json
saee_backend/**
docs/product/**
examples/saee-agent-review-demo/**
scripts/saee_agent_review_demo.py
scripts/saee_agent_review_demo_smoke.py
all Alibaba/commercial task paths
all unlisted paths
```

`agent-index.json` is a single exact-hunk exception，not a file-level permission。

```text
BLOCKER_002_RESOLUTION_PLAN=COMPLETE
EXACT_PATH_CANDIDATE_SET=DEFINED
EXACT_HUNK_SELECTION_RULE=DEFINED
PATH_HUNK_MANIFEST_CREATED=false
PATH_HUNK_MANIFEST_SHA256=UNRESOLVED
BLOCKER_002_EXECUTION_CLOSED=false
```

## 4. BLOCKER_003 Resolution — R4 Artifact Mode

### 4.1 Selected design

推荐并冻结为本计划的唯一 R4 mode：

```text
R4_MODE=NON_SELF_REFERENTIAL_CANDIDATE_INPUT_MANIFEST_COMMIT
R4_PATH=reports/SAEE_DEMO_BASELINE_CANDIDATE_INPUT_MANIFEST.json
R4_PATH_PREEXISTING=false
R4_CHANGE_TYPE=ADD_EXACT
R4_EMPTY_COMMIT=false
R4_RECORDS_OWN_COMMIT_HASH=false
```

R4 manifest 只记录已知输入：

```text
format_version
H0_R_authorization_id
source_anchor_commit
source_anchor_tree
preimage_P_sha256
R1_commit
R1_tree
R2_commit
R2_tree
R3_commit
R3_tree
path_hunk_manifest_sha256
forbidden_scope_manifest_sha256
validator_contract_sha256
role_assignment_sha256
required_absence_paths
stop_point=CANDIDATE_B
```

It must not contain `candidate_B_commit` or `candidate_B_tree`。After committing R4：

```text
Candidate_B_commit=R4_commit
Candidate_B_tree=R4_tree
```

Independent Validator records B full hashes in detached Q-B：

```text
Q_B_PATH=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1/<H0_R_authorization_id>/Q-B.json
Q_B_IN_CANDIDATE_TREE=false
```

This avoids empty commit and Git self-reference。If the R4 path already exists at execution time，
H0-R is invalid；executor may not overwrite it。

### 4.2 Minimality

R4 adds one machine-readable evidence file，not a schema、protocol、capability or product。No JSON
schema is created for it in this phase；its exact key set and serialization are frozen directly by
H0-R manifest and validator contract。

```text
BLOCKER_003_RESOLUTION_PLAN=COMPLETE
R4_MODE_SELECTED=NON_SELF_REFERENTIAL_CANDIDATE_INPUT_MANIFEST_COMMIT
R4_ARTIFACT_CREATED=false
BLOCKER_003_EXECUTION_CLOSED=false
```

## 5. BLOCKER_004 Resolution — Roles and Locations

### 5.1 Candidate role assignment

| Role | Candidate binding | Allowed | Forbidden |
|-|-|-|-|
| Human Authority Owner / Rollback Owner | `repository_owner_human` | approve H0-R；stop/revoke；accept/reject B；authorize/deny Demo | execute R1-R4；perform V-B；rewrite history |
| Executor | `codex_isolated_reconstruction_executor` | create exact W/branch/P/R1-R4 under H0-R | validate/approve own B；touch shared worktree；expand scope |
| Independent Validator | `independent_codex_validation_session` | checkout exact B in separate validation worktree；run V-B；emit detached Q-B | edit/fix B；reuse executor session/worktree；grant H1 |

Human Authority Owner and Rollback Owner are intentionally combined for this one bounded batch to
avoid adding another governance role。Executor and Independent Validator must remain different
execution identities and different worktrees。

### 5.2 Candidate location assignment

```text
reconstruction_branch=codex/phase-6.1-b1-baseline-reconstruction
reconstruction_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-reconstruction
validation_worktree=/Users/zhangbin/Documents/SAEE-worktrees/phase-6.1-b1-baseline-validation
detached_evidence_root=/Users/zhangbin/Documents/SAEE-baseline-evidence/phase-6.1-b1/<H0_R_authorization_id>
shared_worktree=/Users/zhangbin/Documents/SAEE
shared_worktree_access=READ_ONLY_HASH_VERIFICATION_ONLY
```

All candidate locations are currently uncreated。H0-R must bind exact absolute paths and prove no
path/branch collision before creation。

### 5.3 Identity requirements

H0-R must replace candidate role labels with auditable identities：

```text
executor_thread_or_session_id=<required>
independent_validator_thread_or_session_id=<required_and_different>
human_authority_owner_confirmation=<required>
rollback_owner_confirmation=<required>
```

Creating a fresh shell in the same executor session does not satisfy independence。A different
Agent/session must perform V-B。Neither Agent may claim human authority。

```text
BLOCKER_004_RESOLUTION_PLAN=COMPLETE
ROLE_MODEL_SELECTED=THREE_FUNCTIONS_TWO_AGENT_IDENTITIES_ONE_HUMAN_OWNER
EXECUTION_LOCATIONS_SELECTED_AS_CANDIDATES=true
ROLE_IDENTITIES_ASSIGNED=false
LOCATIONS_HUMAN_APPROVED=false
BLOCKER_004_EXECUTION_CLOSED=false
```

## 6. H0-R Readiness Gate

### 6.1 Required conditions

H0-R can be granted only when all conditions are true：

```text
human_accepts_source_anchor=true
human_approves_authority_schema_exact_byte_exception=true
authority_schema_sha256_matches=true
path_hunk_manifest_materialized=true
path_hunk_manifest_sha256_resolved=true
forbidden_scope_manifest_sha256_resolved=true
all_MODIFY_EXACT_HUNKS_fragments_independently_reviewed=true
R4_mode_human_approved=true
R4_path_absent=true
executor_identity_bound=true
independent_validator_identity_bound=true
rollback_owner_bound=true
execution_and_validation_locations_approved=true
candidate_branch_and_paths_absent=true
preimage_P_created_and_digest_resolved=true
shared_worktree_exclusion_snapshot_matches=true
six_Demo_paths_absent=true
push_external_Demo_authority=false
```

Current readiness：

```text
H0_R_READINESS=NOT_READY
H0_R_BLOCKER_COUNT=4
H0_R_GRANTED=false
```

The four blocker plans are complete，but their execution closures are not complete。Human approval of
this report may approve the resolution direction；it does not create P、manifest digests or role
session IDs。A valid H0-R record must bind those runtime facts before execution starts。

### 6.2 One-use H0-R stop point

Future H0-R：

```text
authorization_type=BASELINE_RECONSTRUCTION_ONLY
commit_sequence=R1,R2,R3,R4
stop_point=CANDIDATE_B_AND_DETACHED_Q_B
demo_implementation_authorized=false
push_authorized=false
external_action_authorized=false
authority_switch_authorized=false
```

H0-R is consumed when R4 is created or invalidated。It cannot be reused to fix V-B failures。

## 7. Rollback and Stop Rules

### 7.1 Before execution

If human review rejects any plan item，do nothing。No cleanup or normalization of the shared dirty
worktree is required or allowed。

### 7.2 During manifest/P preparation

If a source hash or selected hunk differs：

```text
STOP_REASON=PREIMAGE_OR_MANIFEST_DRIFT
BRANCH_CREATION_ALLOWED=false
WORKTREE_CREATION_ALLOWED=false
```

Return to human review with the exact difference。Do not silently recompute the approved digest。

### 7.3 During R1-R4

On any extra path/hunk、validator mutation、hash mismatch or role violation：

1. Executor stops immediately；
2. no next commit is created；
3. Rollback Owner quarantines W/branch and preserves P/logs；
4. shared worktree remains untouched；
5. candidate is `REJECTED` or `NOT_CREATED`；
6. a new H0-R authorization is required for any correction。

### 7.4 After Candidate B

V-B failure produces detached Q-B=`FAIL`。Independent Validator cannot repair B。Failed B remains
forensic evidence；no amend、rebase、reset or history deletion。A correction must be a newly authorized
candidate lineage。

### 7.5 Rollback references

```text
construction_anchor=f6ac41f4b068377e7778e8c3d83b99bd8382debc
construction_anchor_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
pre_execution_reference=<future_P_digest>
per_commit_references=<future_R1_R2_R3_R4_hashes>
candidate_reference=<future_B_commit_and_tree>
qualification_reference=<future_Q_B_digest>
```

```text
ROLLBACK_MODEL=APPEND_ONLY_FAIL_CLOSED_NO_HISTORY_REWRITE
ROLLBACK_EXECUTED=false
```

## 8. First-Principles Check

### 8.1 为什么严格限制重建范围？

Baseline 是实验对照，不是 feature branch。只有权威、治理与设计输入可以变化；Capability、
Schema semantics、MCP、Runtime、Evaluation、Product 和 Protocol 必须固定，Agent 的后续决策
差异才可归因于“使用 SAEE Evaluation”而不是系统被同时改写。

### 8.2 为什么 carry-forward 不是 schema 修改？

本计划不生成新 bytes，也不改变现有 bytes。它把已生效 authority family 中、hash 已冻结的
一个 artifact 从 aggregate input 原样放入 committed lineage。路径、内容、角色和验证全部
固定；任何一个 bit 改变都会失败。因此它恢复 provenance closure，不改变 contract。

### 8.3 为什么角色分离保护 baseline 可信？

Executor 证明“按 manifest 构造”；Independent Validator 证明“结果满足 invariants”；Human
Authority Owner 决定“是否接受并授权下一步”。如果一个身份同时执行三项，它可以用自己的
解释掩盖 scope drift 或验证失败，Candidate 就无法成为可信第三方输入。

### 8.4 为什么 A3 后应停止增加治理层？

这四个 blocker 已经被压缩成 exact hash、manifest、artifact mode 和 role bindings。再增加抽象
原则不会提高 Demo 证据质量。下一次有效进展只能来自 human H0-R decision 和一次受控 execution，
最终目标仍是让 Agent 真正调用现有 SAEE Evaluation。

## 9. Human Review Packet

Human review should answer exactly：

```text
SOURCE_ANCHOR_APPROVED=true|false
AUTHORITY_SCHEMA_EXACT_CARRY_FORWARD_APPROVED=true|false
R1_R2_R3_CANDIDATE_SCOPE_APPROVED=true|false
R4_MODE_APPROVED=true|false
ROLE_MODEL_APPROVED=true|false
CANDIDATE_LOCATIONS_APPROVED=true|false
H0_R_AUTHORIZATION_MAY_BE_PREPARED=true|false
```

Even all `true` values mean “prepare/bind the exact H0-R record”；they do not by themselves create
branch/worktree/commits unless the human decision explicitly includes the final P/manifest/role digests
and states `FUTURE_H0_R_DECISION=GRANTED`。

## 10. Input Integrity

```text
reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZATION_PREPARATION.md=a7ff76be14f3bd0e4d29cb0044d2d7332c3c69f25e45c6c65f473f3cfbd582ea
reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_PREPARATION.md=9e659d1939362c5664fe2e342abaeba9d43060f2c5ecb4537ec0b062cd324a1b
capability-package/manifest.json=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
```

These hashes identify A3 inputs only。They do not authorize reconstruction。

## 11. Final Status

```text
H0_BLOCKER_RESOLUTION_STATUS=COMPLETE
BLOCKER_001_RESOLUTION_PLAN=COMPLETE
BLOCKER_002_RESOLUTION_PLAN=COMPLETE
BLOCKER_003_RESOLUTION_PLAN=COMPLETE
BLOCKER_004_RESOLUTION_PLAN=COMPLETE
BLOCKER_001_EXECUTION_CLOSED=false
BLOCKER_002_EXECUTION_CLOSED=false
BLOCKER_003_EXECUTION_CLOSED=false
BLOCKER_004_EXECUTION_CLOSED=false
H0_R_READINESS=NOT_READY
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
PATH_HUNK_MANIFEST_CREATED=false
PREIMAGE_P_CREATED=false
BASELINE_CREATED=false
WORKTREE_CREATED=false
BRANCH_CREATED=false
COMMITS_CREATED=false
DEMO_IMPLEMENTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CONTENT_MODIFIED=false
MCP_CHANGED=false
RUNTIME_CHANGED=false
EVALUATION_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
CODE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_H0_BLOCKER_RESOLUTION_PLAN
```

## 12. Current-Phase Validation Record

本节只证明 A3 report 没有改变现有 truth surfaces，不代表 H0-R readiness。

```text
PROJECT_MEMORY_CHECK=PASS
GOVERNANCE_REGISTRY_CHECK=PASS
DEVELOPMENT_CONSTITUTION_SMOKE=PASS
CANONICAL_CAPABILITY_INVENTORY_SMOKE=PASS_9_OF_9
CAPABILITY_PROGRESS_LEDGER_SMOKE=PASS_9_OF_9
QIANFAN_READINESS_MCP_SMOKE=PASS_TOOLS_2_DEMOS_3
QODER_ADAPTER_SMOKE=PASS_TOOLS_2
GIT_DIFF_CHECK=PASS
REPORT_DIFF_CHECK=PASS_NO_WHITESPACE_ERRORS
POST_REPORT_STATUS_DEFAULT_ENTRY_COUNT=115
POST_REPORT_STATUS_ALL_UNTRACKED_ENTRY_COUNT=132
EXCLUDING_TARGET_STATUS_DEFAULT_ENTRY_COUNT=114
EXCLUDING_TARGET_STATUS_ALL_UNTRACKED_ENTRY_COUNT=131
EXCLUDING_TARGET_STATUS_DEFAULT_SHA256=b67c5a327b2f9c9d9f8b187838478e3923937232ec5366da69db40fb58b75179
EXCLUDING_TARGET_STATUS_ALL_UNTRACKED_SHA256=3c54cec1019354f3581ea2fd9e386b1787fa109c3969894d33d2006c70df4357
POST_REPORT_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
POST_REPORT_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
HEAD_UNCHANGED=true
REGISTERED_WORKTREE_COUNT_UNCHANGED=4
STASH_COUNT_UNCHANGED=0
CANDIDATE_BRANCH_EXISTS=false
CANDIDATE_WORKTREE_EXISTS=false
SIX_DEMO_PATHS_ABSENT=true
ONLY_TARGET_REPORT_ADDED=true
```
