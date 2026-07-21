# SAEE Demo Baseline Reconstruction Execution Authorization Preparation

```text
report_id=SAEE_DEMO_BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZATION_PREPARATION
requested_phase=Phase_6.1-B1-A2
report_mode=EXECUTION_AUTHORIZATION_DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
demo_role=integration_evidence_for_existing_SAEE_Evaluation
report_date=2026-07-15
```

## Executive Decision

未来 Demo baseline reconstruction 可以被设计成一个 one-use、anchor-bound、preimage-bound、
exact-delta-bound、role-bound、stop-point-bound 的执行批次，但当前没有授予该执行权。

安全 gate 顺序为：

```text
A2  authorization preparation                         CURRENT
 ↓
H0-R human reconstruction authorization               NOT_GRANTED
 ↓
R1/R2/R3/R4 in a new clean isolated worktree          NOT_EXECUTED
 ↓
Candidate B commit/tree                                NOT_CREATED
 ↓
V-B independent baseline qualification                NOT_RUN
 ↓
H1 human baseline acceptance + Demo authorization     NOT_READY
 ↓
six-path add-only Demo implementation                  NOT_AUTHORIZED
```

`H0-R` 只能授权构造并停在 Candidate B，不能授权 Demo。`H1` 继续沿用
`SAEE_AGENT_REVIEW_DEMO_EXECUTION_AUTHORIZATION_PACKAGE.md` 中的 baseline-bound 语义；它必须
基于已独立验证的 B、immutable preimage P、六路径 allowlist、角色和 stop point 作出显式人工
决定。

当前授权设计存在一个必须由 H0-R 人工裁决的 scope conflict：

```text
AUTHORITY_COMPLETE_REQUIRES=schemas/saee-development-constitution.schema.v1.1.json
CURRENT_HEAD_CONTAINS_AUTHORITY_SCHEMA=false
A2_GENERIC_SCHEMA_RULE=FORBIDDEN
```

推荐裁决是只为该已批准 authority-family artifact 建立一个 exact-byte carry-forward exception，
同时继续禁止任何 schema 语义变更、capability/runtime schema 变化和其他 `schemas/**` 路径。
若人类拒绝这一窄例外，则 H0-R 必须保持未授权，因为 Candidate B 无法同时满足
authority-complete 与 schema-forbidden 两项规则。

```text
AUTHORIZATION_DESIGN=COMPLETE_FAIL_CLOSED
H0_R_READY=CONDITIONAL_ON_HUMAN_SCOPE_RESOLUTION
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
H1_READY=false
```

本阶段只新增本报告；没有创建 baseline、branch、worktree、commit、preimage、rollback
reference 或 Demo 文件。

## 0. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED
```

Baseline governance 与 Demo 都是 supporting lane，不得取代当前受控 SAEE–Agent Evidence
integration mainline。H0-R 仅用于给一次 bounded Integration Evidence experiment 建立可信
输入，不得被解释为新产品、新 capability、新 protocol、新 authority 或 Phase 1 授权。

```text
MAINLINE_CORRECTION=AUTHORIZE_ONLY_A_BOUNDED_RECONSTRUCTION_FOR_EXISTING_EVALUATION_INTEGRATION_EVIDENCE
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PRODUCT_IDENTITY_CHANGED=false
PHASE_1_AUTHORIZED=false
SELF_ASSESSMENT_AUTHORIZES_CHANGE=false
```

## 1. Current Authorization State

### 1.1 Report pre-image

目标报告创建前：

```text
branch=feat/canonical-capability-inventory-routing-v1
head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
head_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
status_default_entry_count=113
status_all_untracked_entry_count=130
status_default_sha256=9b6542442ff790afdb52c049b01fc44700c0dc559441e294c838d447274189d0
status_all_untracked_sha256=3845fbbd96253ba226d5974b4bf45cdf8cdcd99be7872f3b5e014f3498c40f84
staged_patch_sha256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
unstaged_patch_sha256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
registered_worktree_count=4
stash_count=0
target_report_preexisting=false
```

这些值只用于证明本 A2 报告没有污染原有 mixed worktree。它们不是未来 P，也不允许 future
executor 将 dirty files wholesale 纳入 reconstruction。

### 1.2 Existing gates

```text
SOURCE_ANCHOR_RECOMMENDATION=f6ac41f4b068377e7778e8c3d83b99bd8382debc
SOURCE_ANCHOR_APPROVED=false
QUALIFIED_EXISTING_BASELINE=false
DEMO_BASELINE_COMMIT=UNRESOLVED
BASELINE_CREATED=false
H0_R_GRANTED=false
H1_BASELINE_BOUND_AUTHORIZATION=NOT_GRANTED
DEMO_IMPLEMENTATION_AUTHORIZED=false
```

Phase 6.1-B0.2 的 six-path candidate allowlist digests 保持：

```text
DEMO_ALLOWLIST_SHA256=2bbe259d7877ff55c42fcebec0ccecbd7d66060398ba2eb13f310cd8978d670d
DEMO_ADD_ONLY_SCOPE_SHA256=9d7de130e3882c111f7f56cb6e354c01d4e768b508e6f7567adc5993ef132626
```

它们是未来 H1 输入，不是 H0-R reconstruction scope。

## 2. Gate Model and Authorization Record

### 2.1 Gate separation

| Gate | Human decision | May do | Must stop before |
|-|-|-|-|
| A2 | review authorization design | only accept/reject this report | branch/worktree creation |
| H0-R | authorize exact reconstruction batch | create isolated W and R1-R4 commits | Demo path creation |
| V-B | independent technical qualification | read/validate B and emit detached evidence | baseline acceptance/repair |
| H1 | accept exact B and separately authorize bounded Demo | create six add-only Demo paths if both decisions are true | commit/push/external action |

`V-B PASS` 不是 human acceptance；`H1 baseline acceptance` 也不能自动推导
`DEMO_IMPLEMENTATION_AUTHORIZED=true`。同一 H1 packet 可以承载两个决定，但必须分别显式填写：

```text
baseline_acceptance_decision=ACCEPTED|REJECTED
demo_execution_decision=AUTHORIZED|NOT_AUTHORIZED
```

### 2.2 Required H0-R record

未来 H0-R 必须是 one-use record，至少绑定：

```text
authorization_id=<unique_H0_R_id>
authorization_type=BASELINE_RECONSTRUCTION_ONLY
authorized_by=<Human_Authority_Owner>
authorized_at=<timezone_qualified_timestamp>
expires_at=<explicit_timestamp_or_one_use_completion>
source_anchor_commit=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_anchor_tree=def1f5fb06b8087a5c0fabd929be253f25faed67
isolated_worktree_path=<new_exact_path>
reconstruction_branch=<new_exact_branch>
preimage_P_sha256=<detached_pre_reconstruction_manifest_digest>
path_hunk_manifest_sha256=<exact_allowlist_digest>
forbidden_scope_manifest_sha256=<exact_denylist_digest>
commit_sequence=R1,R2,R3,R4
executor=<assigned_identity>
independent_validator=<different_assigned_identity>
rollback_owner=<assigned_identity>
human_authority_owner=<human_identity>
stop_point=CANDIDATE_B_AND_DETACHED_VALIDATION_PACKET
branch_creation_allowed=true
worktree_creation_allowed=true
commit_allowed=ONLY_R1_R2_R3_R4_IN_ISOLATED_WORKTREE
push_allowed=false
external_action_allowed=false
demo_path_creation_allowed=false
authority_switch_allowed=false
```

字段缺失、过期、scope digest 漂移或角色未绑定时，authorization 无效。

### 2.3 H0-R cannot authorize

H0-R 永远不能授权：

- 修改 current shared worktree/index；
- 创建六个 Demo paths；
- 修改 capability/schema semantics/MCP/runtime/product/protocol；
- push、PR、release、deployment 或 external claim；
- 将 Candidate B 自动升级为 accepted baseline；
- 将 validator PASS 解释为 H1；
- 扩展权限或把 Agent 同时设为 human approver。

## 3. Execution Scope

### 3.1 Source model

未来 executor 只能使用：

```text
lineage_anchor=f6ac41f4b068377e7778e8c3d83b99bd8382debc
idempotency_patch_provenance=d0b3dd796aff58557d0f45e4abcf170c4a7eda51
idempotency_integration_oracle=18942ce16071390969e0814dc1f2fe0a0efed06d
approved_aggregate_inputs=<exact_content_addressed_files_or_hunks_only>
```

`d0b3dd796...` 和 `18942ce160...` 只提供 patch provenance/oracle，不允许整支 merge 或
wholesale cherry-pick。Current dirty tree 只提供待人工审查的 bytes，不是 execution input
set。

### 3.2 Allowed restoration classes

#### R1 — Authority Closure

Candidate exact-path family：

```text
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
agent-interface/governance/saee-development-constitution.v1.1.json
schemas/saee-development-constitution.schema.v1.1.json  # H0-R scope resolution required
docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md
scripts/saee_development_constitution_smoke.py
```

Allowed change type：将已经生效并经审查的 v1.1 authority family 以 exact approved bytes 闭合
到 committed lineage。禁止修改 identity、mainline、product family、v2 status、non-claims、
machine-contract semantics 或 validator assertions。

#### R2 — Governance Closure

Candidate exact-path family：

```text
governance/README.md                                      # Project Memory pointer hunk only
governance/project-memory/README.md
governance/project-memory/current-state.md
governance/project-memory/frozen-decisions.md
governance/project-memory/active-questions.md
governance/project-memory/rejected-options.md
governance/project-memory/decision-log.md
governance/project-memory/memory-policy.md
governance/project-memory/v2-transition-decisions.md
scripts/saee_project_memory_check.py
tests/test_project_memory.py
AGENTS.md                                                 # authority/mainline/startup hunks only
.codex/current_state.md                                   # authority/mainline pointer hunks only
.codex/rules.md                                           # authority/mainline rule hunks only
llms.txt                                                  # top authority pointer block only
agent-index.json                                          # authority metadata hunk only
scripts/mainline_guard.py                                 # approved validator routing hunk only
```

Allowed change type：闭合已经批准的 governance/Project Memory truth 与 agent-readable authority
pointers，使 validators 可在 baseline-contained clean worktree 中只读、可重复运行。

以下当前 dirty governance/product paths 不因 R2 自动获准：

```text
governance/registry/product-registry.json
governance/schemas/product.schema.json
scripts/saee_governance_registry_check.py
tests/test_governance_registry.py
docs/product/**
```

若 future manifest 证明其中某个 exact hunk 对 v1.1 closure 绝对必要，必须返回 H0-R 重新人工
批准；不得由 executor 自行扩大。

#### R3 — Accepted Design Inputs

只有人工 review 接受的 exact report bytes 可进入：

```text
reports/SAEE_EVALUATION_MVP_SPECIFICATION.md
reports/SAEE_AGENT_REVIEW_DEMO_IMPLEMENTATION_PLAN.md
reports/SAEE_AGENT_REVIEW_DEMO_BASELINE_PREPARATION.md
reports/SAEE_AGENT_REVIEW_DEMO_DELTA_MINIMIZATION.md
reports/SAEE_AGENT_REVIEW_DEMO_EXECUTION_AUTHORIZATION_PACKAGE.md
reports/SAEE_AGENT_REVIEW_DEMO_BASELINE_CLOSURE_REPORT.md
reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_PREPARATION.md
reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZATION_PREPARATION.md
```

这些 reports 是 provenance/design evidence，不是 capability、authority、schema、runtime 或
product truth source。任何未获 human acceptance 的报告必须从 R3 manifest 排除。

#### R4 — Candidate Baseline Closure

R4 只允许添加 H0-R 预先列明的 candidate input manifest / reconstruction receipt，内容限于：

- R1-R3 commit hashes 与 tree hashes；
- exact path/hunk manifest digest；
- P digest；
- validator command contract；
- forbidden invariants；
- executor 与 stop-point receipt。

R4 文件不能记录自己的 future commit hash，因为 Git commit 不能自包含其自身 hash。R4 完成
后，其 commit/tree 才被命名为 Candidate B；B 的 full hash/tree 必须记录在 detached
qualification record `Q-B` 中。

```text
R4_EMPTY_COMMIT_ALLOWED=false
R4_SELF_REFERENTIAL_HASH_ALLOWED=false
CANDIDATE_B=R4_COMMIT_AFTER_CREATION
B_HASH_RECORD_LOCATION=DETACHED_Q_B
```

如果 H0-R 未批准 exact R4 artifact path 与 content contract，则安全替代是：不创建空 R4，
令 `B=R3 tip`，并在 detached Q-B 中完成 designation。Executor 无权自行选择两种模式。

### 3.3 Allowed change semantics

所有 future allowed changes 必须满足：

```text
purpose=restore_existing_approved_closure
new_capability=false
new_product=false
new_protocol=false
runtime_behavior_change=false
evaluation_behavior_change=false
external_claim_change=false
```

每个 path/hunk entry 必须记录：

```text
path
change_type=ADD_EXACT|MODIFY_EXACT_HUNKS
source_role
source_commit_or_file
before_git_blob_or_absent
after_sha256
hunk_sha256_if_modified
reason
owner
validator
rollback_rule
```

目录 glob、`related files`、fuzzy patch 和 conflict 中整边选择都不是有效授权。

## 4. Forbidden Scope

### 4.1 Capability

```text
capability-package/manifest.json
capability-package/**
agent-index.json#capability_progress_ledger_v1
```

禁止 capability ID、status、implementation、lifecycle、claim/non-claim、route、alias 或 canonical
source 变化。`agent-index.json` 只可能允许 authority metadata exact hunk；capability projection
bytes 必须由 P/Q-B 比较证明未变。

### 4.2 Schema

```text
schemas/**
agent-interface/qianfan/**
governance/schemas/**
```

默认全部禁止新增、删除、重命名和语义修改。唯一待 H0-R 裁决的 candidate exception 是：

```text
path=schemas/saee-development-constitution.schema.v1.1.json
role=EXISTING_FROZEN_AUTHORITY_FAMILY_ARTIFACT
aggregate_preimage_sha256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
allowed_change=ADD_EXACT_BYTES_TO_CLOSE_ACTIVE_AUTHORITY_FAMILY
schema_semantics_change=false
```

该 exception 不扩展到任何其他 schema，也不代表创建新 schema。未获得明确人工批准时：

```text
AUTHORITY_SCHEMA_CARRY_FORWARD_AUTHORIZED=false
H0_R_EXECUTABLE=false
```

### 4.3 MCP

禁止 Tool 增删、改名、description、annotations、schema ref、route、transport、registry
classification、server command 或 public/official integration claim 变化。重点冻结：

```text
.mcp.json
governance/registry/mcp-registry.json
scripts/saee_agent_readiness_mcp_stdio.py
scripts/saee_qianfan_readiness_mcp_stdio.py
saee_backend/services/qianfan_readiness_mcp_adapter.py
```

### 4.4 Runtime and Evaluation

禁止 evaluator、score、threshold、recommendation、required Evidence、reason code、decision
mapping、network behavior 或 repository write behavior 变化。重点冻结：

```text
saee_backend/**
scripts/saee_agent_readiness_mcp_stdio.py
scripts/saee_qianfan_readiness_mcp_stdio.py
```

Governance validators 属于 closure tooling，不是 product runtime；即使如此，也只能按 R1/R2
exact hunks 修改，且不得改变 runtime/evaluation results。

### 4.5 Product, Protocol and external truth

禁止：

- 新产品、产品重命名、商业状态升级；
- 新 protocol、API、request/response contract 或 discovery mechanism；
- v2 activation、authority switch 或 Constitution semantic rewrite；
- official OpenAI/Anthropic/LangGraph/Qianfan/Bailian integration claim；
- customer validation、production readiness、deployment、pricing 或 launch claim；
- Agent Evidence source/runtime migration；
- Alibaba/commercial task bytes；
- 六个 Demo implementation paths。

## 5. Commit Strategy

### 5.1 Construction rules

未来只允许在 H0-R 指定的新 isolated worktree/branch 中创建 commits：

```text
R1=Authority_Closure
R2=Governance_Closure
R3=Accepted_Design_Inputs
R4=Candidate_Baseline_Closure
```

每个 commit 必须：

1. 以前一 accepted tree 为 parent；
2. diff 严格等于该 commit 的 exact manifest subset；
3. 不包含其他 worktree/index bytes；
4. commit 前后 `git diff --check`；
5. 运行该层最小 validators；
6. 完成后 worktree clean；
7. 记录 commit/tree/status/manifest digests；
8. 任一失败立即 stop，不进入下一 commit。

### 5.2 Prohibited Git behavior

```text
merge_whole_branch=false
cherry_pick_whole_commit=false
fuzzy_apply=false
reuse_current_index=false
clean_current_worktree=false
stash_current_worktree=false
reset_or_rebase_history=false
amend_after_evidence=false
push=false
```

### 5.3 Per-commit gate

| Commit | Required PASS before next | Stop condition |
|-|-|-|
| R1 | Constitution contract/schema/smoke; no capability/runtime diff | authority semantics or unapproved schema path changes |
| R2 | Project Memory + governance + mainline guard read-only checks | truth-source split, product change or validator mutation |
| R3 | report hash/approval manifest and no executable-surface diff | unapproved report or status claim upgrade |
| R4 | exact candidate manifest, clean tree, six Demo paths absent | self-reference, empty/extra commit or scope drift |

Candidate B is only a candidate. No validation process may add a fifth commit and silently rename it B；
any post-B repository mutation produces a new candidate and invalidates prior evidence。

## 6. Candidate Baseline B Requirements

Candidate B must provide one immutable commit/tree with：

| Closure group | Requirement |
|-|-|
| Authority | v1.1 family `5/5`, pointers agree, v2 remains inactive |
| Governance | Phase 0 registries resolvable; Project Memory `8/8`; validators present |
| Capability | canonical inventory and ledger remain reviewed `9/9`; no second truth source |
| Schemas | capability/runtime schema tree unchanged; authority schema equals approved exact bytes |
| MCP/runtime | canonical tools remain exactly two; behavior and route unchanged |
| Design inputs | every included report has recorded human acceptance and exact hash |
| Demo absence | all six Demo paths absent |
| Git state | clean checkout, no ignored/untracked required input |
| Provenance | R1-R4 parent chain, manifest digest, P digest and role receipts resolvable |

Required Candidate B record fields，stored in detached Q-B after B exists：

```text
candidate_baseline_commit=<full_40_character_B>
candidate_baseline_tree=<full_tree_hash>
parent_chain=<R1,R2,R3,R4_full_hashes>
candidate_file_manifest_sha256=<digest>
preimage_P_sha256=<digest>
validator_contract_sha256=<digest>
forbidden_invariant_manifest_sha256=<digest>
qualification_status=PASS|FAIL
```

```text
CANDIDATE_IS_ACCEPTED_BASELINE=false
VALIDATOR_PASS_AUTO_ACCEPTS_BASELINE=false
```

## 7. Immutable Preimage P

### 7.1 Timing and role

P 必须在创建 reconstruction worktree、应用 R1 之前冻结。它是 detached、content-addressed、
read-only input proof，不进入 current shared worktree，也不把 secrets 或文件内容复制进报告。

为避免“preimage”与“post-candidate evidence”混淆：

```text
P=PRE_RECONSTRUCTION_IMMUTABLE_INPUT_MANIFEST
Q-B=POST_CANDIDATE_INDEPENDENT_QUALIFICATION_RECORD
```

Phase 6.1-B0.2 的 `immutable_preimage_sha256` 明确指 P digest。

### 7.2 Required P fields

```text
format_version
created_at
created_by
source_anchor_commit
source_anchor_tree
shared_worktree_status_default_sha256
shared_worktree_status_all_sha256
shared_worktree_staged_patch_sha256
shared_worktree_unstaged_patch_sha256
approved_path_hunk_manifest_sha256
forbidden_scope_manifest_sha256
role_assignment_sha256
validator_command_manifest_sha256
sorted_file_records[]
```

每个 `sorted_file_records[]` 至少包含：

```text
path
truth_role
anchor_presence
anchor_git_blob_if_present
approved_input_sha256_if_carry_forward
expected_B_rule=BYTE_EQUAL_ANCHOR|BYTE_EQUAL_APPROVED_INPUT|AUTHORIZED_EXACT_HUNK
secret_or_personal_data=false
```

### 7.3 Minimum frozen surfaces

P 必须覆盖：

- `capability-package/manifest.json` 与 `agent-index.json` capability projection；
- all capability/runtime schemas and their deterministic tree digest；
- `.mcp.json`、MCP registry、canonical wrapper、adapter 与 tool metadata；
- evaluator/runtime services；
- product registry and current product truth；
- active Constitution family and authority pointers；
- Project Memory and governance registries；
- all validators used by V-B；
- six Demo path absence；
- exact R1-R4 candidate allowlist and denylist。

P 必须区分：

```text
FROZEN_AT_ANCHOR                 # B must keep same Git blob
APPROVED_CARRY_FORWARD_INPUT     # absent at anchor; B must equal approved SHA-256
AUTHORIZED_EXACT_HUNK            # only listed hunks may differ
FORBIDDEN_PATH                   # no delta permitted
REQUIRED_ABSENCE                 # Demo paths must remain absent
```

### 7.4 P integrity

```text
P_STORAGE=DETACHED_READ_ONLY
P_CAN_AUTHORIZE_EXECUTION=false
P_CAN_CHANGE_AFTER_H0_R=false
P_DIGEST_CHANGE_INVALIDATES_H0_R=true
P_CONTENT_INCLUDES_SECRETS=false
```

## 8. Validation Gate V-B

### 8.1 Independent procedure

Independent Validator 必须从 exact B 创建新的 read-only/validation worktree，不使用 executor
worktree，并执行：

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_qianfan_readiness_mcp_smoke.py
python3 scripts/saee_qoder_adapter_smoke.py
python3 scripts/saee_public_capability_surface_smoke.py
python3 -m unittest tests/test_project_memory.py tests/test_governance_registry.py
git diff --check
```

每个 validator 连续运行两次，分别记录 before/after `git status --short --untracked-files=all`
digest。任何新增、修改、删除或 required ignored artifact 都是 FAIL。

### 8.2 Delta proof

V-B 必须证明：

1. `git diff <anchor>..<B>` 只含 H0-R exact path/hunk manifest；
2. capability fact surfaces 满足 P 的 `BYTE_EQUAL_ANCHOR`；
3. capability/runtime schema tree 未改变；
4. authority schema 若获窄例外，则等于 P 中 approved SHA-256；
5. MCP tool count/IDs/routes/schema refs/runtime behavior 与 P 一致；
6. evaluator outputs、recommendations 与 deterministic smoke preimage 一致；
7. product identity/status/non-claims 未升级；
8. v1.1 authority active、v2 inactive；
9. 六个 Demo paths absent；
10. current shared worktree exclusion snapshot 未因 execution 改变。

### 8.3 Q-B output

Q-B 是 detached qualification evidence，必须记录每项 PASS/FAIL、B commit/tree、P digest、
validator logs digests 和 independent validator identity。Q-B 不得修改 B。

```text
V_B_RESULT_REQUIRED=PASS
PARTIAL_PASS_ALLOWED=false
VALIDATION_FIX_IN_PLACE_ALLOWED=false
FAILED_CANDIDATE_AUTO_REPAIR_ALLOWED=false
```

出现 FAIL 时，Independent Validator 只能报告。任何 correction 必须由新的 human-authorized
reconstruction batch 生成新的 candidate B2。

## 9. Role Separation

| Role | May | Must not |
|-|-|-|
| Human Authority Owner | approve H0-R scope；accept/reject B；authorize/deny Demo at H1 | 用模糊“继续”替代 exact record |
| Executor | 在 H0-R 范围创建 W、R1-R4、execution receipt | 验证/批准自己的 B；改 shared worktree；扩 scope |
| Independent Validator | checkout exact B；执行 V-B；生成 detached Q-B | 修改 B、修复失败、授予 H1 |
| Rollback Owner | 触发 stop、隔离 failed W/branch、保全 evidence、执行获准清理 | rewrite history、删除 shared dirty work、把 failed B 标为 accepted |

Minimum separation：

```text
executor != independent_validator
executor != human_authority_owner
independent_validator != human_authority_owner
rollback_owner explicitly_assigned=true
AI_AGENT_MAY_ACT_AS_HUMAN_AUTHORITY_OWNER=false
```

如人数限制导致一人承担 Executor 与 Rollback Owner，必须在 H0-R 明示例外；Independent
Validator 与 Human Authority Owner 仍不得与 Executor 合并。

## 10. Rollback and Invalidation

### 10.1 Rollback points

```text
construction_anchor=f6ac41f4b068377e7778e8c3d83b99bd8382debc
pre_execution_reference=P_digest
per_commit_references=R1,R2,R3,R4_commit_and_tree
candidate_reference=B_commit_plus_tree
qualification_reference=Q_B_digest
```

### 10.2 Failure handling

| Failure | Action |
|-|-|
| P/H0-R mismatch | do not create W；return to human review |
| unexpected patch/path | stop before commit；quarantine W；record evidence |
| R1/R2/R3/R4 validator fail | stop chain；do not amend/rebase；candidate not created/invalid |
| B qualification fail | Q-B=`FAIL`；retain rejected immutable candidate；new authorization required |
| post-B drift | invalidate Q-B/H1；construct new candidate under new H0-R |
| shared worktree drift | immediate stop；do not attempt automated cleanup |

Rollback means returning execution eligibility to the approved anchor/reference，not rewriting or
deleting history。Failed commits may remain forensic evidence but never become accepted baseline。

### 10.3 Automatic H0-R invalidation

H0-R becomes invalid if：

- source anchor/tree、P digest、path/hunk manifest、denylist or role changes；
- schema conflict is unresolved；
- any Demo path exists before H1；
- an authorized path needs a new hunk/source；
- validator mutates the worktree or depends on untracked state；
- capability、schema semantics、MCP、runtime、product or protocol changes；
- authorization expires or is consumed；
- commit chain differs from approved R1-R4 structure。

## 11. H1 Requirements

H1 只有在 V-B PASS 后才可准备。Required facts：

```text
H0_R_authorization_record_complete=true
R1_R2_R3_R4_chain_complete=true
candidate_B_commit_resolved=true
candidate_B_tree_resolved=true
preimage_P_digest_resolved=true
qualification_Q_B_digest_resolved=true
V_B_result=PASS
authority_complete=true
governance_complete=true
project_memory_aligned=true
capability_truth_unchanged=true
schema_truth_unchanged_or_exact_authority_carry_forward=true
MCP_runtime_unchanged=true
product_protocol_truth_unchanged=true
six_demo_paths_absent=true
shared_dirty_worktree_exclusion_unchanged=true
roles_assigned=true
```

H1 must bind：

```text
authorization_id=<unique_one_use_H1_id>
authorized_by=<Human_Authority_Owner>
authorized_at=<timezone_qualified_timestamp>
expires_at=<explicit_timestamp_or_one_use_completion>
baseline_acceptance_decision=ACCEPTED|REJECTED
demo_execution_decision=AUTHORIZED|NOT_AUTHORIZED
baseline_commit=<full_B>
baseline_tree=<full_tree_hash>
baseline_worktree=<future_isolated_Demo_worktree>
immutable_preimage_sha256=<P_digest>
qualification_record_sha256=<Q_B_digest>
allowlist_sha256=2bbe259d7877ff55c42fcebec0ccecbd7d66060398ba2eb13f310cd8978d670d
add_only_scope_sha256=9d7de130e3882c111f7f56cb6e354c01d4e768b508e6f7567adc5993ef132626
executor=<Demo_executor>
independent_validator=<different_identity>
rollback_owner=<assigned_identity>
stop_point=LOCAL_DEMO_AND_VALIDATION_PACKET
commit_allowed=false
push_allowed=false
external_action_allowed=false
```

只有 `baseline_acceptance_decision=ACCEPTED` 且
`demo_execution_decision=AUTHORIZED`，才可设置：

```text
H1_BASELINE_BOUND_AUTHORIZATION=GRANTED
DEMO_IMPLEMENTATION_AUTHORIZED=true
```

当前：

```text
H1_READINESS_STATUS=NOT_READY
H1_BASELINE_BOUND_AUTHORIZATION=NOT_GRANTED
DEMO_IMPLEMENTATION_AUTHORIZED=false
```

## 12. First-Principles Check

### 12.1 为什么 baseline 重建不能变成架构重写？

实验要隔离的变量是“Agent 是否会使用现有 SAEE Evaluation 结果改变下一步计划”。若重建
同时改变 architecture、capability、schema、MCP 或 evaluator，实验就无法区分决策变化来自
SAEE 现有能力还是新系统，baseline 也失去作为对照组的意义。

### 12.2 为什么必须限制 delta？

当前 aggregate worktree 混合多个任务。只有 exact path/hunk 与 content hash 能回答某个变化
来自哪一项人工批准、为何存在、如何验证、如何回滚。目录授权或“相关文件”会把 provenance
重新变成推断，正好破坏重建目标。

### 12.3 为什么未来 Agent 生态需要可追溯演进？

Agent 不只读取代码，也读取 capability manifest、schemas、MCP metadata、README、Project
Memory 和 evaluation language 并据此行动。若这些输入不能绑定到同一 commit/tree，Agent
即使得到相同 recommendation，也无法证明使用了相同规则。可追溯演进使每次结果都能回答：
基于哪个版本、哪个权威、哪个能力事实、哪个验证和哪项人工授权。

### 12.4 为什么 Candidate 不等于 Accepted？

Executor 只能证明“按授权构造了一个 commit”。Independent Validator 才能证明它满足 technical
invariants；Human Authority Owner 再决定是否接受和是否授权 Demo。把三者合并会让系统自己
构造、自己验证、自己批准自己的事实。

## 13. Human Review Decision Items

H0-R 前必须逐项人工决定：

1. 是否接受 `f6ac41f4...` 为 source anchor；
2. 是否批准 authority schema exact-byte carry-forward exception；
3. 是否批准 R1/R2/R3 的 exact path/hunk manifest；
4. 是否采用 R4 candidate receipt commit，或令 `B=R3 tip`；
5. 是否批准 P/Q-B detached evidence model；
6. 是否批准角色分离和 stop point；
7. 是否保持 push/external/Demo 权限为 false；
8. 是否授权另一个执行阶段创建 branch/worktree/R1-R4。

```text
H0_BLOCKER_001=AUTHORITY_SCHEMA_SCOPE_CONFLICT_UNRESOLVED
H0_BLOCKER_002=EXACT_PATH_HUNK_MANIFEST_NOT_CREATED
H0_BLOCKER_003=R4_ARTIFACT_MODE_NOT_SELECTED
H0_BLOCKER_004=ROLES_AND_EXECUTION_LOCATIONS_NOT_ASSIGNED
```

因此本报告完成的是 authorization preparation，不是 ready-to-run authorization token。

## 14. Input Integrity

```text
reports/SAEE_DEMO_BASELINE_RECONSTRUCTION_PREPARATION.md=9e659d1939362c5664fe2e342abaeba9d43060f2c5ecb4537ec0b062cd324a1b
reports/SAEE_AGENT_REVIEW_DEMO_EXECUTION_AUTHORIZATION_PACKAGE.md=d8782be652c3e20a74886a41bf74d8cd52ce3bf2f8fdeba4324cae9e7a8ed1a0
reports/SAEE_AGENT_REVIEW_DEMO_BASELINE_CLOSURE_REPORT.md=f048d4fa85696efc7a1b6b0d425dc09c2991176383450501d45cfd3312dc3a58
capability-package/manifest.json=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
agent-index.json=1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740
schemas/saee-development-constitution.schema.v1.1.json=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
scripts/saee_development_constitution_smoke.py=8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550
scripts/saee_project_memory_check.py=81b350e9b0358777e473f958dc572b2cda8e3e56f74864b5967a5b8928697c10
scripts/saee_governance_registry_check.py=06beb37f671e6bfdd4b47a39514aa86db74679e33648098bb9ac44ff77c520d5
```

These hashes identify A2 review inputs only。They do not create P or authorize future use of the
aggregate worktree bytes。

## 15. Final Status

```text
BASELINE_RECONSTRUCTION_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
AUTHORIZATION_DESIGN_STATUS=COMPLETE_FAIL_CLOSED
H0_R_HUMAN_REVIEW=PENDING
H0_R_GRANTED=false
BASELINE_RECONSTRUCTION_EXECUTION_AUTHORIZED=false
AUTHORITY_SCHEMA_CARRY_FORWARD_AUTHORIZED=false
EXACT_PATH_HUNK_MANIFEST_CREATED=false
PREIMAGE_P_CREATED=false
QUALIFICATION_Q_B_CREATED=false
BASELINE_CREATED=false
WORKTREE_CREATED=false
BRANCH_CREATED=false
COMMITS_CREATED=false
DEMO_IMPLEMENTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
H1_READY=false
H1_BASELINE_BOUND_AUTHORIZATION=NOT_GRANTED
DEMO_IMPLEMENTATION_AUTHORIZED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_BASELINE_RECONSTRUCTION_AUTHORIZATION_PREPARATION
```

## 16. Current-Phase Validation Record

本节只验证本 A2 报告没有改变现有治理、capability、MCP 或 runtime；不代表 future Candidate B
qualification，也不解除任何 H0 blocker。

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
POST_REPORT_STATUS_DEFAULT_ENTRY_COUNT=114
POST_REPORT_STATUS_ALL_UNTRACKED_ENTRY_COUNT=131
EXCLUDING_TARGET_STATUS_DEFAULT_ENTRY_COUNT=113
EXCLUDING_TARGET_STATUS_ALL_UNTRACKED_ENTRY_COUNT=130
EXCLUDING_TARGET_STATUS_DEFAULT_SHA256=9b6542442ff790afdb52c049b01fc44700c0dc559441e294c838d447274189d0
EXCLUDING_TARGET_STATUS_ALL_UNTRACKED_SHA256=3845fbbd96253ba226d5974b4bf45cdf8cdcd99be7872f3b5e014f3498c40f84
POST_REPORT_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
POST_REPORT_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
HEAD_UNCHANGED=true
REGISTERED_WORKTREE_COUNT_UNCHANGED=4
STASH_COUNT_UNCHANGED=0
SIX_DEMO_PATHS_ABSENT=true
ONLY_TARGET_REPORT_ADDED=true
```
