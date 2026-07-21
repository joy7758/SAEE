# SAEE Goal Integrity Fixture Creation Readiness Plan

## Phase 8.0-D6.3 — Controlled Synthetic Fixture Design, Not Creation

```text
plan_id=SAEE-GI-P0-FIXTURE-READINESS-20260716-V1.1
plan_date=2026-07-16
plan_type=FIXTURE_CREATION_RULES_ONLY
closure_plan_sha256=36501278ba88d8ddd43571f189fc9f92d10c89bdbf9306351eed121831ca9417
evidence_root_plan_sha256=701f4641d00208f484f102af50d3aa19cb4ca522d3b1a29d848b3b4928809cc4
h3_comparator_human_decision=INITIAL_CLEAN_RESTART
h3_comparator_decision_source=HUMAN_SELECTION_OPTION_1_20260716
```

## Executive Decision

Goal Integrity P0 需要可重复的 synthetic coding environments，但本阶段只冻结 fixture creation readiness，
不创建 source、workspace、Evidence Root、runtime 或 Agent session。

本计划复用既有 fixture invariants：

- `reports/SAEE_AUTONOMY_CHECK_SYNTHETIC_FIXTURE_CREATION_PLAN.md` 的 repository isolation、byte-copy、
  tree-hash、sentinel 和 failure preservation；
- `reports/SAEE_AUTONOMY_CHECK_FIXTURE_CREATION_AUTHORIZATION.md` 的 no-symlink/no-worktree、copy verification、
  required absence、atomic grant 和 stop point；
- D4/D5 的 A/B/C detection module 与 D/restart recovery module 分离。

不创建第二套通用 fixture framework。

```text
DUPLICATE_BUILD_PREVENTED=true
FIXTURE_CREATION_AUTHORIZED=false
FIXTURE_CREATED=false
P0_EXECUTION_AUTHORIZED=false
```

## Commander Preflight and Method Correction

```text
COMMANDER_COMMAND_CHECK=WARNING
MAINLINE_DRIFT_DETECTED=true
DUPLICATE_BUILD_RISK=true
METHOD_CONFLICT_DETECTED=true
METHOD_CONFLICT_STATUS=RESOLVED_BY_HUMAN_SELECTION_OPTION_1
STAGED_TRUTH_RISK=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_FIXTURE_READINESS_PLAN
PROGRAM_MAINLINE_CHANGED=false
```

必须纠正“从同一 source 同时复制 A/B/C/D”的表述：

```text
A = B = C at initial repository preimage
D starts from the confirmed-drift snapshot
RESTART starts from the initial clean fixture
```

D 已收到 diagnosis、LKV 和 recovery recommendation，只能测试 recovery utility；若让 D 从 initial fixture 与
A/B/C 同跑，会把 detection、intervention timing 和 recovery 混成一个 treatment。H3 的 D 与 restart 共享同一个
confirmed drift intervention event 和 pre-intervention history，但在 intervention 后有意使用不同 workspace state：
D 保留有效工作，restart 丢弃运行中修改并从 initial clean fixture 重启。

# 1. Fixture Purpose

## 1.1 Research role

Fixture 是 P0 的受控 operational environment，用于回答：

- A/B/C 在相同 initial code、tests、constraints 和 injected pressure 下是否表现出不同 Goal continuity；
- B 的 Goal Anchor 是否减少 Objective/Scope/Constraint drift；
- C 的 Transition metadata 是否改善 change/drift/unresolved distinction；
- 对同一个 confirmed drift intervention event，D recovery recommendation 是否优于从 initial clean fixture 重启。

Fixture 不负责证明 Agent code quality、企业适用性或 production reliability。

## 1.2 Why isolation is mandatory

如果 fixture 位于 SAEE repository 或各 arm 分别生成，则结果可能来自：

- SAEE project context；
- dirty worktree；
- 不同 file bytes/modes；
- historical reports 或 Agent instructions；
- branch/worktree state；
- shared cache、memory 或上一 arm 的写入；
- hidden Trigger、MCP 或 expected label leakage。

所以 fixture source、arm copies、recovery snapshots 和 evidence receipts 必须分离。

# 2. External Location Boundary

## 2.1 Frozen candidate locations

D6.2 已把 Evidence Root 候选冻结为：

```text
EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001
```

为避免 Agent workspace 位于 Evidence Root 内并直接改写 evidence，本计划冻结一个 sibling workspace root：

```text
FIXTURE_WORKSPACE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001-workspaces
FIXTURE_WORKSPACE_ROOT_STATE_AT_PLAN_TIME=ABSENT
```

二者关系：

```text
Evidence Root:
  manifests, receipts, hashes, raw command evidence

Fixture Workspace Root:
  source fixture, arm workspaces, recovery workspaces
```

## 2.2 Forbidden location types

Fixture/Evidence paths 均禁止：

- SAEE repository descendant；
- Git repository 或 Git worktree；
- symlink、hard link、socket、FIFO、device；
- path traversal 或指向 home secrets；
- network mount 或 cloud-sync folder；
- 与先前 Autonomy Check fixture 混用；
- target 已存在时覆盖、清理或合并。

```text
GIT_REPOSITORY_CREATED=false
GIT_WORKTREE_CREATED=false
SYMLINKS_ALLOWED=false
HARDLINKS_ALLOWED=false
```

## 2.3 Access separation

- Fixture Author 只在获批 creation attempt 中写 `fixture-source`；
- Evidence Custodian 把 commands/manifests/receipts 写入 Evidence Root；
- Independent Validator 只读 source/copies 并复算；
- Agent under test 只写自己的 arm/recovery workspace；
- Agent 不写 fixture source、ground truth 或 Evidence Root；
- A/B/C session 不能看到其他 arm workspace。

# 3. Future Fixture Structure

以下结构只设计、不创建：

```text
SAEE-GI-P0-20260716-001-workspaces/
  fixture-source/
    P-S01/
    P-S02/
    P-S03/
    P-S04/
    P-S05/
    P-S06/
    P-S07/
    P-C01/
  execution-attempts/
    P-S01/
      arm-a/attempt-000001/
      arm-b/attempt-000001/
      arm-c/attempt-000001/
    ...
  recovery-snapshots/
    snapshot-000001/
      source/
      arm-d/attempt-000001/
      restart/attempt-000001/
    ...
```

Evidence Root 中只保存对应 evidence，不保存 Agent 的 live writable workspace：

```text
SAEE-GI-P0-20260716-001/
  case-inputs/
  fixtures/
  sessions/
  adjudication/
```

## 3.1 No evidence symlink in fixture

不得在 workspace 中创建指向 Evidence Root 的 symlink。workspace 与 receipt 的关联只存在于 Evidence Root 的
manifest/receipt 中，以 absolute path observation + tree hash + attempt ID 表达；Agent-visible tree 不包含 ground
truth/evidence link。

## 3.2 No arm packets in repository tree

A/B/C 的 experimental information packets 不写入 repository fixture tree：

- A：Prompt + repository context；
- B：A + Goal Anchor；
- C：B + Transition metadata。

这些 packets 通过 frozen stdin/user-prompt envelope 提供，并在 Evidence Root 单独 hash。否则 B/C tree 与 A 不同，
无法满足 initial fixture equivalence。

# 4. Initial State Binding

每个 case 在 fixture creation authorization 前必须有以下 binding：

```text
case_id
fixture_version
initial_repository_manifest
initial_repository_tree_sha256
initial_goal
goal_baseline_version
initial_constraints
initial_tests
initial_evidence_refs
allowed_evolution
forbidden_drift
injection_record_ref
expected_label_ref
expected_outcome
recovery_target_ref
external_effect_sentinel
```

## 4.1 Agent-visible vs hidden facts

Agent-visible：

- task prompt；
- repository files；
- arm-specific Goal/Transition packet；
- pre-registered injection when checkpoint is reached；
- tests and local sentinel boundary。

Hidden from Agent：

- expected label；
- first expected invalid transition；
- expected LKV；
- reviewer rubric answer key；
- arm mapping；
- other arm outputs。

任何 hidden fact 出现在 Agent-visible tree/prompt，使 attempt invalid。

## 4.2 Initial tests and expected outcome

- initial tests 必须在 source fixture 上先运行并保存 baseline result；
- test failure 若是 scenario 设计的一部分必须显式预注册；
- expected Outcome 与 Goal Integrity label 分开；
- tests pass 不自动表示 Goal preserved；
- sentinel 只能记录 local intent/state，不执行 merge、deploy、network 或 production action。

## 4.3 Source immutability

source fixture seal 后：

- files read-only；
- source tree hash 固定；
- 不作为 Agent workspace；
- 不运行会修改 source 的 test/cache command；
- 如需修复，保留旧 source attempt 并创建新 fixture version；
- 不在同一 attempt 原位修改。

# 5. Equivalence Model

## 5.1 A/B/C initial equivalence

每个 primary/control case：

```text
TREE_A_PRE = TREE_B_PRE = TREE_C_PRE = TREE_SOURCE
```

必须同时验证：

```text
same_relative_paths=true
same_entry_types=true
same_file_bytes=true
same_file_modes=true
same_required_absences=true
same_tree_sha256=true
separate_writable_locations=true
```

不比较 mtime、inode 或 absolute path；它们预期不同且不属于 content equivalence。

## 5.2 Copy method

未来只能：

1. 从 sealed source manifest 读取 allowlist；
2. 逐 path 创建独立 regular file/directory；
3. byte-copy file content；
4. 恢复冻结 mode；
5. 拒绝 allowlist 外 entry 和所有 link/device；
6. 复算 manifest/tree hash；
7. source/A/B/C hashes 全等后 seal pre-session receipt。

禁止分别生成 A/B/C 内容、共享同一 writable directory、copy caches 或在 copy 后“修补到一致”。

## 5.3 D/restart recovery comparator

Human review 选择 option 1，保持 D3.1/D4 的 canonical `initial clean restart` 语义：

```text
H3_COMPARATOR_SEMANTIC=RECOVERY_FROM_CONFIRMED_DRIFT_VS_INITIAL_CLEAN_RESTART
INTERVENTION_EVENT_D=INTERVENTION_EVENT_RESTART
PRE_INTERVENTION_HISTORY_D=PRE_INTERVENTION_HISTORY_RESTART
TREE_D_PRE=TREE_CONFIRMED_DRIFT_SNAPSHOT
TREE_RESTART_PRE=TREE_INITIAL_CLEAN_FIXTURE
RUNTIME_D=RUNTIME_RESTART
REMAINING_BUDGET_D=REMAINING_BUDGET_RESTART
COMPARISON_WINDOW=POST_INTERVENTION
```

两者在同一个 confirmed drift event 后分流：

- D 保留 confirmed-drift snapshot 中仍有效的工作，并接收 Drift Diagnosis + LKV Candidate + bounded Recovery Suggestion；
- restart 丢弃运行中 workspace 修改，从同一 case 的 initial clean fixture 创建 fresh writable copy，只接收 initial Goal +
  clean restart instruction，不接收 D packet。

两者不要求 intervention 后的 tree hash 相等，因为“保留有效工作”和“从零重启”正是 treatment difference。
它们必须绑定同一个 case、initial source hash、Goal baseline、drift event、runtime、remaining budget、stop rules 和
post-intervention measurement window。pre-intervention cost 作为 shared sunk cost 单独记录，不伪装成 D 或 restart
独有成本。

```text
H3_COMPARATOR_SEMANTIC_STATUS=RESOLVED_INITIAL_CLEAN_RESTART
H3_EXECUTION_AUTHORIZED=false
```

语义歧义已关闭，但这不关闭 G2/G3/G6，也不授权创建 recovery snapshot、restart copy 或执行 H3。

## 5.4 Pre/post separation

- `TREE_*_PRE` 永久保留；
- session 后生成新 `TREE_*_POST`；
- post differences 是实验结果，不覆盖 pre hash；
- post trees 之间不要求相等；
- A/B/C 不得复用上一 arm 的 post workspace。

# 6. Drift Injection Boundary

## 6.1 Pre-registration requirements

每个 injection 必须在模型调用前冻结：

```text
injection_id
case_id
injection_type
delivery_channel
semantic_trigger
earliest_checkpoint
latest_checkpoint
payload_sha256
expected_affected_goal_fields
expected_label_ref
no_injection_behavior
abort_rule
```

## 6.2 Delivery rules

- 同一 case 的 A/B/C 使用相同 injection payload、channel 和 semantic trigger；
- injection 只在 pre-registered checkpoint condition 成立时递送；
- 若 latest checkpoint 前未到达，记录 `INJECTION_NOT_DELIVERED`，不得换位置补注入；
- 不根据 Agent 行为临时增强、弱化或重写 injection；
- injection 不含 expected label、Goal Drift 字样或 reviewer answer；
- controls `P-S06`、`P-S07`、`P-C01` 按 D5 明确为 no-drift/transition controls；
- runtime operator 不能在结果不理想时增加第二次 injection；
- injection failure 作为 experiment protocol failure 保留。

## 6.3 Allowed injection classes

只允许 D5 registry 已定义的 synthetic pressure：

- scope-expansion诱因；
- platform-expansion诱因；
- architecture-substitution诱因；
- proxy-goal诱因；
- research-to-execution诱因；
- authorized transition control；
- unresolved proposal control；
- allowed-evolution control。

新增 injection class 需要新 preregistration version，不能在 P0 中途添加。

# 7. Fixture Hashing and Receipt

## 7.1 Canonical manifest entries

manifest 递归枚举 regular files 和 directories；每个 entry 至少包含：

```text
relative_path
entry_type
mode
size
content_sha256
```

directory 的 `size/content_sha256` 使用固定 null convention；所有 entries 按 UTF-8 relative path 递归字典序排序。
manifest 不包含 absolute path、mtime、inode、uid/gid 或 host-specific metadata。

## 7.2 Tree hash

```text
TREE_SHA256 = SHA256(canonical_manifest_bytes)
```

canonical manifest 使用 UTF-8、recursive lexicographic key ordering、LF、final newline。tree hash 计算 3 次必须一致。

manifest 存在 Evidence Root，不放入被 hash 的 fixture tree。

## 7.3 Required receipts

future creation 至少产生：

```text
fixture-creation-authorization.json
fixture-source-manifest.json
fixture-source-receipt.json
fixture-copy-verification.json
fixture-required-absence-verification.json
fixture-test-baseline.json
fixture-sentinel-binding.json
fixture-boundary-observation.json
fixture-creation-receipt.json
```

## 7.4 Verification predicate

```text
FixtureCopyValid(case) :=
    source_manifest_complete=true
AND no_forbidden_entry_type=true
AND paths_A=paths_B=paths_C=paths_source
AND bytes_A=bytes_B=bytes_C=bytes_source
AND modes_A=modes_B=modes_C=modes_source
AND absences_A=absences_B=absences_C=absences_source
AND tree_A=tree_B=tree_C=tree_source
AND hash_determinism=3/3
AND workspaces_are_distinct=true
AND evidence_root_unchanged_except_new_receipts=true
```

# 8. Failure Preservation

## 8.1 Attempt states

```text
ALLOCATED
WRITING
VALIDATING
SEALED_COMPLETE
INVALID_PRESERVED
FAILED_BEFORE_WRITE
```

每个 creation attempt 从开始就使用最终不可复用 ID；不得删除失败目录后重用同一 ID。

## 8.2 Creation failure

保存：

- human authorization；
- command、stdout、stderr；
- precondition checks；
- partial workspace paths/files；
- expected vs actual manifest；
- failure stage/class；
- SAEE repository boundary observation；
- `FIXTURE_CREATED=false` receipt。

partial source/copies 标记 `INVALID_PRESERVED`，不得用于 session。

## 8.3 Validation failure

以下均 fail-closed：

- file/path/mode/hash mismatch；
- unexpected symlink/hardlink/device；
- required absence 不成立；
- tests/sentinel boundary 不成立；
- Agent-visible label leakage；
- Evidence Root chain verification fail；
- concurrent modification；
- source/A/B/C 不等价。

不允许在同一 attempt “补文件后重新验证”。

## 8.4 Normal completion and retention

fixture creation 完成后也不自动清理：

- source 保持 read-only；
- pre-session copies 只在 session authorization 后使用；
- creation receipts 保留；
- no Agent session automatically starts；
- deletion/disposition 需要 future human decision。

# 9. Fixture and Evidence Relationship

## 9.1 Distinction

```text
Fixture = controlled mutable object on which an Agent may act
Evidence = immutable/logically write-once record about fixture creation and change
```

fixture source 与 initial copies 是 experiment assets；manifest、hash、command、failure、pre/post diff 和 decision
才是 evidence records。

## 9.2 Evidence flow

```text
Human fixture authorization
  ↓ evidence receipt
Source creation attempt
  ↓ manifest/hash/failure evidence
A/B/C copy attempt
  ↓ equivalence evidence
Pre-session seal
  ↓ pre-tree evidence
Future Agent session
  ↓ events/diff/tests/post-tree evidence
Human/independent review
```

Agent 不直接写 Evidence Root。Executor/capture process 将 raw streams 交给 Evidence Custodian sealing。

## 9.3 No evidentiary circularity

- fixture manifest 不由被测 Agent 生成或自证；
- ground truth 不来自 Agent output；
- post-session tests 不覆盖 initial tests；
- receipt hash 不证明世界事实真实，只证明 bytes/lineage consistency；
- Evidence Root existence 不证明 fixture valid；需要 independent verification。

# 10. Gate Closure Relation

## 10.1 Preconditions for fixture creation authorization

```text
G0_SOURCE_INTEGRITY=PASS
G1_PREREGISTRATION_ACCEPTANCE=PASS
G6_EVIDENCE_PRESERVATION=PASS
FIXTURE_WORKSPACE_ROOT_PRECONDITION=ABSENT
FIXTURE_AUTHOR_BOUND=true
INDEPENDENT_VALIDATOR_BOUND=true
CASE_INPUT_AUTHORIZATION_RECEIVED=true
FIXTURE_CREATION_AUTHORIZATION_RECEIVED=true
```

当前均未满足或未全部满足；本 plan 不关闭 gate。

## 10.2 G2 case-input closure

G2 需要 7 primary + `P-C01` 的 prompt、Goal/Transition packets、injection、answer key、LKV 和 hashes 全部冻结，
并通过 label-leakage review。Fixture source 不得在 G2 前创建。

## 10.3 G3 fixture closure predicate

```text
G3_FIXTURE_PASS :=
    G2=PASS
AND G6=PASS
AND fixture_source_created=true
AND source_manifest_verified=true
AND all_case_tests_baselined=true
AND all_required_absences_verified=true
AND A_B_C_copy_equivalence=PASS
AND injection_bindings_verified=true
AND local_sentinel_boundary=PASS
AND failure_preservation_smoke=PASS
AND independent_validator_result=PASS
AND evidence_receipt_chain=PASS
AND saee_repository_unchanged=true
AND blocking_issues=[]
```

## 10.4 What G3 does not authorize

即使 G3 PASS：

```text
RUNTIME_CREATED=false
MODEL_INVOKED=false
AGENT_SESSION_CREATED=false
EXPERIMENT_EXECUTED=false
P0_EXECUTION_AUTHORIZED=false
```

G3 只表示 fixture 资产准备完成。

# 11. Risks and Stop Conditions

| Risk | Stop rule |
|---|---|
| A/B/C source drift | any path/bytes/mode/hash mismatch -> invalid attempt |
| H3 comparator semantic drift | if restart receives confirmed-drift files, or D starts clean, invalidate and stop |
| Arm packet leaks into tree | invalid; recreate new attempt/version |
| Ground-truth leakage | invalid; preserve and stop |
| Agent sees other arm | invalid comparison |
| Fixture/evidence root mixed | stop; no Agent direct evidence writes |
| Reuse of old Autonomy Check fixture | prohibited; concepts may be reused, bytes/state may not |
| Runtime injection altered live | invalid protocol attempt |
| Source test mutates fixture | invalid source; new version required |
| Hidden cache/memory | stop until isolation is proven |
| Real customer/production data | stop immediately |
| Fixture planning becomes product framework | stop duplicate expansion |
| Mainline displacement | pause secondary research lane |

# 12. Non-Claims

本 plan 不代表：

- Evidence Root、fixture source、A/B/C copies、D/restart snapshots 已创建；
- G2、G3 或 G6 已关闭；
- A/B/C/D 是一个单一可直接比较的 execution experiment；
- H3 recovery/restart fixture、runtime 或 execution 已获授权；
- synthetic fixture 等于真实 enterprise environment、真实 user behavior 或 production workload；
- fixture validation 证明 Goal Anchor、Transition metadata 或 Recovery 有效；
- Agent、model、runtime、MCP 或 external service 已调用；
- Goal Plugin、Schema、Capability 或 product 已实现；
- SAEE repository mainline 已改变。

# 13. Final Status

```text
FIXTURE_CREATION_READINESS_PLAN_STATUS=COMPLETE
FIXTURE_WORKSPACE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/goal-integrity-p0/SAEE-GI-P0-20260716-001-workspaces
FIXTURE_WORKSPACE_ROOT_STATE_AT_PLAN_TIME=ABSENT
FIXTURE_CREATION_AUTHORIZED=false
FIXTURE_SOURCE_CREATED=false
FIXTURE_CREATED=false
EVIDENCE_ROOT_CREATED=false
G2_CASE_INPUT_STATUS=OPEN
G3_FIXTURE_STATUS=OPEN
H3_COMPARATOR_SEMANTIC_STATUS=RESOLVED_INITIAL_CLEAN_RESTART
H3_EXECUTION_AUTHORIZED=false
RUNTIME_CREATED=false
ANNOTATORS_BOUND=false
AGENT_SESSION_CREATED=false
EXPERIMENT_EXECUTED=false
MODEL_INVOKED=false
MCP_INVOKED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
PROTOCOL_CREATED=false
MCP_CHANGED=false
SKILL_CHANGED=false
CODE_CHANGED=false
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_FIXTURE_READINESS_PLAN
PROGRAM_MAINLINE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_FIXTURE_PLAN
```
