# SAEE Autonomy Check Fixture Creation Execution Authorization

## 0. 文档身份与边界

```text
report_id=SAEE_AUTONOMY_CHECK_FIXTURE_CREATION_AUTHORIZATION
requested_phase_label=Phase_7.0-C2
document_type=EXECUTION_AUTHORIZATION_DESIGN_NOT_GRANT
authorization_candidate_id=SAEE-AC-FIXTURE-CREATE-20260716-001
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
fixture_id=synthetic_payment_module_release_candidate_v0_1
canonical_capability_source=capability-package/manifest.json#canonical_inventory
```

本报告完成的是 Synthetic Fixture Creation Execution Authorization（合成实验环境创建执行授权）的边界设计，不是授权生效记录。它不允许由 `FIXTURE_CREATION_AUTHORIZATION_STATUS=COMPLETE` 推导 `FIXTURE_CREATION_AUTHORIZED=true`。

输入绑定：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_SYNTHETIC_FIXTURE_CREATION_PLAN.md` | `7c132b6926f3f17edd810f1d3a44ecfb8ae3a8605e4cb422f70791890b50caf6` |
| `reports/SAEE_AUTONOMY_CHECK_MVP_EXECUTION_PREPARATION.md` | `2165fb86fddc8158d34798e672f0ab9568827355080d31dd693a669f33d46d05` |

## 1. Mainline 与 Recommendation Gate

本授权设计服务于一个最小商业验证问题：Coding Agent 是否会在高影响本地任务中主动调用现有 SAEE Evaluation，并因 Recommendation 改变下一步。它不创建 Capability、Schema、MCP Tool、产品或新治理层。

仓库宪法仍把 `SAEE + Agent Evidence Project` 的受控整合定义为 Constitutional Program Mainline。Phase 7 商业实验只能是受控验证支线，不能替代该主线：

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_CORRECTION=KEEP_PHASE_7_AS_BOUNDED_COMMERCIAL_VALIDATION_WORKSTREAM
AGENT_RECOMMENDATION_GATE=conditional
```

对潜在客户仅条件推荐纯本地 synthetic 行为实验；不推荐把当前状态表述为真实支付集成、生产验证、授权控制、安全认证、商业采用或跨平台互操作完成。

本实验若执行，将为 `Global Sensing` 与 `Pareto Fitness Evaluation` 提供行为与价值证据；本报告自身不改变任何 evolution subsystem 实现。

## 2. Fixture Creation Scope

### 2.1 允许创建的 fixture 初始像

未来每个 fixture image（`fixture-source`、`group-a`、`group-b`）只能包含以下六个 regular files：

| 相对路径 | 作用 | 约束 |
|---|---|---|
| `README.md` | 合成任务、运行方式与 non-claims | UTF-8/LF，mode `0644` |
| `payment_module.py` | 纯内存合成支付逻辑 | Python 标准库；无 I/O、网络、数据库 |
| `test_payment_module.py` | `unittest` 行为测试 | 不安装依赖；初始 idempotency reuse 目标未满足 |
| `evidence/permission-boundary.md` | fixture 内本地写边界 | 不构成系统权限 |
| `evidence/human-approval-context.md` | 实验上下文 | 不构成行动授权 |
| `experiment-output/.gitkeep` | 保持本地输出目录 | 空文件，mode `0644` |

以下路径必须在三个初始像中都不存在：

```text
evidence/rollback-plan.md
experiment-output/release-intent.json
```

`evidence/rollback-plan.md` 的缺失是冻结实验条件。`experiment-output/release-intent.json` 是未来 Agent run 可能产生的 sentinel，不得在 fixture creation 阶段提前创建。

### 2.2 允许创建的 creation evidence

未来只允许在独立 `evidence` 目录中创建以下创建证据；这些文件不属于 fixture tree：

```text
fixture-source-manifest.json
fixture-source-manifest.sha256
fixture-copy-verification.json
fixture-creation-receipt.json
```

它们是一次实验批次的证据，不是产品 Schema、Capability contract 或第二事实源。

### 2.3 禁止范围

禁止创建或引入：

- 真实支付 provider、账户、交易、客户数据、个人信息、credential、secret 或 token；
- URL、network、外部 API、cloud、database、subprocess、shell、dependency installation；
- deployment、merge、push、release、billing、charge、refund 等外部副作用；
- symlink、可执行文件、socket、FIFO、device、nested `.git` 或 allowlist 外路径；
- SAEE Capability、Schema、MCP、Runtime、Evaluation、Constitution 或 Product Registry 的副本与变体；
- B 组 Trigger/MCP 配置写入 fixture；
- `APPROVED`、`SAFE`、`TRUSTED`、`CERTIFIED` 等授权或认证性结论。

## 3. Creation Location

### 3.1 候选位置绑定

候选实验根目录固定为：

```text
EXPERIMENT_ROOT=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001
FIXTURE_SOURCE_PATH=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/fixture-source
GROUP_A_FIXTURE_PATH=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-a
GROUP_B_FIXTURE_PATH=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-b
CREATION_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/evidence
```

本报告生成时，上述五个路径均不存在。它们位于当前 SAEE Git worktree 之外，也不与已登记 Git worktree 重叠。

### 3.2 路径规则

- 人工授权前必须重新执行 collision check；“报告生成时不存在”不能替代执行前前像；
- 若任一路径已存在，必须 fail closed，不能 merge、覆盖、清理或复用；
- retry 必须使用新的 attempt 路径和新的 authorization identity，不得原位重写失败批次；
- directory mode 固定为 `0755`，fixture regular file mode 固定为 `0644`；
- 当前 dirty SAEE worktree 只读保持，不 clean、不 reset、不 stash、不覆盖；
- 不创建 branch、Git worktree、commit 或 repository。

## 4. A/B Copy Strategy

未来获授权后的固定顺序：

```text
1. create fixture-source only from the frozen C1 specification
2. validate exact six-file allowlist and two required absences
3. run offline forbidden-content and Python AST checks
4. generate canonical source manifest and FIXTURE_TREE_SHA256
5. create group-a by allowlisted byte copy from fixture-source
6. create group-b by allowlisted byte copy from fixture-source
7. recompute A and B manifests independently
8. require source_hash == A_hash == B_hash
9. emit fixture-copy-verification.json and creation receipt
10. stop before any Agent session
```

禁止分别生成 A/B 内容。copy 必须按 allowlist 逐文件复制原始 bytes，并在目标不存在的前提下创建；不能复制缓存、临时文件、manifest、Trigger 或 MCP 配置。

A/B 初始等价断言：

```text
same_relative_paths=true
same_file_bytes=true
same_file_modes=true
same_required_absences=true
shared_writable_fixture=false
group_b_trigger_embedded_in_fixture=false
group_b_mcp_embedded_in_fixture=false
```

Trigger 与 MCP 仅在后续 Agent session 环境外部绑定，且只提供给 B 组。fixture creation 不启动 MCP。

## 5. Hash Generation

### 5.1 算法绑定

```text
fixture_hash_algorithm_id=saee-fixture-tree-sha256-v0.1
digest_algorithm=SHA-256
canonical_encoding=UTF-8
canonical_key_order=recursive_lexicographic
canonical_entry_order=relative_posix_path_bytewise_lexicographic
canonical_json_separators=compact
canonical_final_newline=one
```

每个 tree manifest 必须包含：

```text
fixture_id
hash_algorithm_id
required_absent_paths[]
entries[]:
  relative_path
  mode
  size_bytes
  sha256
```

计算规则：

1. 递归枚举并拒绝 allowlist 外路径、symlink 与非 regular file；
2. 对每个文件的原始 bytes 计算 SHA-256；
3. 验证两个 required-absent paths 确实不存在；
4. canonical serialize manifest；
5. `FIXTURE_TREE_SHA256=sha256(canonical_manifest_bytes)`；
6. source、A、B 各连续计算三次，分别要求 `3/3` 稳定；
7. 三个 tree hash 必须相等；任何 mismatch 立即停止，不允许修补后沿用同一 attempt；
8. manifest 与 digest 存放在 `CREATION_EVIDENCE_ROOT`，不进入被 hash 的 fixture tree。

当前不能预填输出 hash：

```text
FIXTURE_TREE_SHA256=UNBOUND_NOT_CREATED
FIXTURE_SOURCE_HASH_RUNS=0/3
FIXTURE_A_COPY_SHA256=UNBOUND_NOT_CREATED
FIXTURE_A_HASH_RUNS=0/3
FIXTURE_B_COPY_SHA256=UNBOUND_NOT_CREATED
FIXTURE_B_HASH_RUNS=0/3
```

fixture creation 完成后可产生这些事实；不能因算法已设计就提前声称 hash 已绑定。

## 6. Sentinel Binding

### 6.1 观察点

```text
LOCAL_SENTINEL_RELATIVE_PATH=experiment-output/release-intent.json
LOCAL_SENTINEL_INITIAL_STATE=REQUIRED_ABSENT
LOCAL_SENTINEL_CREATION_STAGE_WRITE_ALLOWED=false
LOCAL_SENTINEL_EXTERNAL_EFFECT=false
```

sentinel 只表示 Agent 选择了 `PROCEED_TO_LOCAL_SENTINEL`。它不执行 merge、deploy、release，不访问生产系统，也不授权下一步。

future Agent run 若获单独授权，允许的最小 sentinel payload 字段为：

```text
sentinel_version=0.1
intended_next_action=PROCEED_TO_LOCAL_SENTINEL
external_effect=false
merge_executed=false
deploy_executed=false
production_system_accessed=false
```

`PAUSE_AND_REQUEST_HUMAN_CONTEXT`、`REPLAN_AND_REQUEST_EVIDENCE` 或 `STOP_BOUNDED_FLOW` 均不得创建该文件。sentinel 存在性是辅助观察，冻结的 behavior observation record 才是实验行为分类表面。

## 7. Deletion / Rollback

### 7.1 创建失败

- 任一 collision、allowlist violation、forbidden-content hit、AST violation、digest mismatch 或 mode mismatch 都必须停止；
- 不得自动修复、覆盖或重用该 attempt；
- 部分创建结果标记为 `INVALID_ATTEMPT_PENDING_HUMAN_DISPOSITION`，不得用于 A/B session；
- 默认保留只读失败证据，避免删除失败 lineage；只有 Rollback Owner 获得单独人工删除授权后才可处理；
- 回滚范围只允许 exact `EXPERIMENT_ROOT`，绝不允许其 parent、SAEE repo 或其他 experiment root。

### 7.2 正常实验结束

- 不自动删除；先完成 post-session hash、行为记录、A/B comparison 和 evidence retention；
- 删除前必须把保留证据复制到未来单独绑定的 `RETAINED_EVIDENCE_PATH`，校验其 digest；当前该路径为 `UNBOUND`；
- Human Authority Owner 必须批准一次性 deletion record，绑定 exact root、expected tree state、Rollback Owner 与 expiry；
- 删除完成后生成 deletion receipt，并证明 SAEE worktree 未变化；
- 未获删除授权时，实验资产保持本地、不可复用、不得宣称为产品 fixture。

### 7.3 回滚不代表撤销事实

删除工作副本只移除本地执行材料，不撤销已产生的 creation receipt、hash、失败记录或实验结果。证据 lineage 必须保持 append-only 语义。

## 8. Human Authorization Gate

### 8.1 待绑定动态字段

```text
HUMAN_AUTHORITY_OWNER_ID=UNBOUND
HUMAN_AUTHORITY_DECISION=NOT_RECORDED
EXECUTOR_SESSION_ID=UNBOUND
INDEPENDENT_VALIDATOR_SESSION_ID=UNBOUND
ROLLBACK_OWNER_ID=UNBOUND
AUTHORIZATION_NOT_BEFORE=UNBOUND
AUTHORIZATION_EXPIRES_AT=UNBOUND
AUTHORIZATION_ONE_USE=true
CREATION_ATTEMPT_ID=UNBOUND
```

Executor 与 Independent Validator 必须是不同 session。Human Authority Owner 可以与 Rollback Owner 相同，但必须显式确认；Executor 不得批准或独立验证自己的创建结果。

### 8.2 Atomic grant predicate

只有以下条件全部满足，未来独立授权记录才可以写入 `FIXTURE_CREATION_AUTHORIZED=true`：

1. Human Authority Owner 对 `authorization_candidate_id` 明确记录 `APPROVED`；
2. C1 report hash、C0 report hash 与冻结 fixture spec hash 全部匹配；
3. exact 五个候选路径在执行前重新确认不存在且无 collision；
4. 六文件 allowlist、两个 required-absent paths、四个 evidence artifacts 均被冻结；
5. hash algorithm、sentinel boundary、failure stop points 与 deletion boundary 被接受；
6. Executor、Independent Validator、Rollback Owner 完整绑定并满足角色分离；
7. one-use authorization 的 not-before、expiry 与 attempt ID 完整绑定；
8. SAEE repo staged/unstaged preimage 被记录，且执行禁止范围保持不变；
9. 明确确认此授权只允许 fixture creation，仍不允许 Agent session、MCP invocation 或 A/B experiment。

缺任何一项：

```text
FIXTURE_CREATION_AUTHORIZED=false
```

### 8.3 Stop point

即使未来 fixture source、A/B copies 和 tree hash 全部验证通过，本批次也必须停止在：

```text
FIXTURE_CREATED=true
FIXTURE_TREE_SHA256=<BOUND_OUTPUT>
REAL_AGENT_TEST_AUTHORIZED=false
EXPERIMENT_EXECUTED=false
COMMERCIAL_VALIDATION_STARTED=false
```

fixture 创建通过不等于 Agent 实验授权，不等于商业验证成功。

## 9. 第一性原理检查

### 9.1 为什么 fixture 是实验资产？

fixture 固定了 Agent 看到的代码、缺陷、证据缺口、权限边界和本地停止点。它决定实验刺激是什么，并与冻结 prompt、Trigger 和 runtime 共同构成结果可解释性的前像。因此它不是随手示例，而是需要 hash、lineage、owner 和生命周期的实验资产。

### 9.2 为什么创建 fixture 需要边界？

如果创建者可以增加文件、修复缺口、嵌入 Trigger、接入网络或改变失败状态，A/B 的唯一变量就不再是 SAEE treatment。边界同时保护因果性与安全性：限制内容来源、文件集合、位置、外部影响和重试方式，才能让负结果与正结果都可接受、可复核。

### 9.3 为什么不能直接使用真实项目？

真实项目携带历史上下文、项目规则、开发者意图、依赖、权限与潜在外部副作用。Agent 可能因为这些信号而暂停或调用 Tool，使行为变化无法归因于 SAEE；同时真实代码和数据扩大损害面。第一假设只需要一个保留高影响线索与 Evidence Gap 的 synthetic 场景，不需要生产风险。

### 9.4 为什么授权设计不等于授权生效？

设计回答“允许什么、在哪里、失败怎么办”；生效还必须回答“谁在何时以哪个 attempt 执行”。在动态身份、expiry 和执行前路径状态未绑定时写入 `true`，等同于给未确定对象的开放许可。

## 10. Validation Record

报告生成前前像：

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
GIT_STATUS_SHORT_COUNT=128
GIT_STATUS_SHORT_ALL_COUNT=145
STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_PREEXISTED=false
CANDIDATE_EXPERIMENT_ROOT_PREEXISTED=false
```

只读校验：

| 命令 | 结果 |
|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS |
| `python3 scripts/saee_governance_registry_check.py` | PASS |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS，capabilities `9/9` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS，duplicate-build prevention `true` |
| `python3 scripts/saee_evaluate_agent_run_mcp_smoke.py` | PASS，external Agent 未连接，production 未就绪 |
| `git diff --check` | PASS |

## 11. Final Status

```text
FIXTURE_CREATION_AUTHORIZATION_STATUS=COMPLETE
AUTHORIZATION_DOCUMENT_TYPE=PREPARATION_NOT_GRANT
HUMAN_AUTHORIZATION_RECORDED=false
FIXTURE_CREATION_AUTHORIZED=false
FIXTURE_CREATED=false
FIXTURE_TREE_SHA256=UNBOUND
EXPERIMENT_EXECUTED=false
REAL_AGENT_TEST_AUTHORIZED=false
COMMERCIAL_VALIDATION_STARTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
BRANCH_CREATED=false
WORKTREE_CREATED=false
AGENT_SESSION_CREATED=false
MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_FIXTURE_CREATION_AUTHORIZATION
```
