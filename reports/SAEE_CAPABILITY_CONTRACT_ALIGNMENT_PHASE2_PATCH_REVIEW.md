# SAEE Capability Contract Alignment（能力契约收敛）Phase 2（第二阶段）补丁人工审查

## 1. 审查结论

```text
PATCH_REVIEW_STATUS=COMPLETE
PATCH_DECISION=PATCH_REQUIRES_ADJUSTMENT
PHASE2_IMPLEMENTATION_COMPLETE=true
TECHNICAL_VALIDATION_PASS=true
MERGE_READY=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
EVALUATION_ALGORITHM_CHANGED=false
HISTORICAL_EVIDENCE_UNCHANGED=true
INTERNAL_RENAME_COMPLETE=false
IMPLEMENTATION_SCOPE=CONTRACT_ALIGNMENT_ONLY
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
```

结论只能选择 `PATCH_APPROVED_FOR_MERGE`（补丁批准合并）或
`PATCH_REQUIRES_ADJUSTMENT`（补丁需要调整）。本次选择：

```text
PATCH_REQUIRES_ADJUSTMENT
```

Phase 2（第二阶段）补丁已经形成可运行的内部新名称链，专项验证和
`Mainline Guard`（主线守卫）均可通过；但它仍不满足合并条件，原因不是公开能力漂移或评估算法改变，
而是：

1. 若干当前活动真值表面仍把旧内部名称作为可用能力和已注册工具；
2. 补丁修改了冻结迁移地图中要求额外人工授权的 `D3`（第三类额外授权）对象，并修改了 16 个未逐文件列入迁移地图的对象；
3. 一个历史结果兼容校验器使用全对象递归字符串替换，范围大于已知唯一历史命中；
4. `agent-index.json`（智能体索引）包含与名称收敛无关的动态时间戳变化；
5. 原始无索引差异中还包含 23 个忽略缓存文件的删除，必须明确排除在未来合并补丁之外。

因此，当前证据支持“主要迁移链能够工作”，但不支持
`INTERNAL_RENAME_COMPLETE=true`（内部重命名完成）或“补丁可以合并”。

## 2. 审查对象与边界

```text
TASK_ID=SAEE-CONTRACT-ALIGNMENT-PATCH-ADJUSTMENT-002
READ_ONLY_BASELINE=/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-attempt-001/baseline
IMPLEMENTATION_WORKSPACE=/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-attempt-001/workspace
BASELINE_TREE_SHA256=af6b4c777871dd5a4f8b60d987c64a110995060d203cf979ca08a00604604dd5
BASELINE_SOURCE_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
```

本审查只读取隔离基线与隔离实施副本，没有：

- 修改隔离补丁；
- 修改 SAEE（硅基放大演化生态）实现代码；
- 执行 `merge`（合并）、`git add`（暂存）、`git commit`（提交）或 `git push`（推送）；
- 修改公开 `MCP`（模型上下文协议）、公开 `Schema`（数据结构规范）或规范公开能力；
- 重新开启 Goal Integrity（目标完整性）副线。

为了独立重放验证，审查者仅把实施副本复制到一次性临时目录；权限调整和
`Mainline Guard`（主线守卫）产生的文件只存在于临时副本，不进入隔离补丁。

## 3. 阻塞发现

### 3.1 阻塞项一：活动内部旧名称仍存在

补丁把主要内部能力包、运行时、内部 `MCP`（模型上下文协议）、内部 `HTTP`（超文本传输协议）、
演示和模拟器迁移到 `evaluate_rehearsal_run`（排演运行评估），但以下当前活动表面仍声明旧内部语义：

| 活动对象 | 当前证据 | 判断 |
|---|---|---|
| `agent-interface/architecture/saee-agent-readiness-architecture.v1.json:99` | `evaluate_agent_run_available=true` | 当前真值字段，不是历史快照 |
| `agent-interface/architecture/saee-agent-readiness-architecture.v1.json:103` | `evaluate_agent_run_mcp_tool_registered=true` | 当前内部本地工具注册真值 |
| `scripts/saee_agent_readiness_architecture_smoke.py:113` | 强制旧可用性字段为真 | 活动校验器仍以旧名称为规范预期 |
| `scripts/saee_agent_readiness_architecture_smoke.py:126` | 强制旧工具注册字段为真 | 活动校验器仍以旧名称为规范预期 |
| `ecosystem/participant-package-v0.1/capability-reference.json:7` | `evaluate_agent_run` 与 `rehearse_agent` 并列 | 混合公开引用与内部工具，语义尚未消歧 |
| `agent-interface/ecosystem/saee-volcengine-capability-mapping.v0.1.json:8` | 未限定命名空间的 `evaluate_agent_run` | 设计投影仍未判定为公开或内部 |

同一不一致还被投影到智能体可读表面：

- `agent-readable.md:8406`；
- `agent-readable.md:8413`；
- `agent-readable.md:8455`；
- `agent-readable.md:8468`；
- `agent-readable.md:8508`；
- `agent-readable.md:8514`；
- `agent-readable.md:8601`；
- `agent-readable.md:8624`。

这些内容会使智能体同时看到：

```text
CURRENT_INTERNAL_OPERATION=evaluate_rehearsal_run
ACTIVE_CURRENT_TRUTH=evaluate_agent_run
```

因此，实施报告中的：

```text
ACTIVE_INTERNAL_OLD_TOOL_REFERENCES=0
ACTIVE_INTERNAL_OLD_FIXED_IDENTIFIERS=0
INTERNAL_RENAME_COMPLETE=true
```

当前缺少充分证据支持。

必要调整不是全局替换。每个 `D3`（第三类额外授权）对象必须先固定：

```text
REFERENCE_CLASS=PUBLIC_OPERATION|INTERNAL_REHEARSAL_OPERATION|HISTORICAL_FACT|UNRESOLVED
```

- 若是 `PUBLIC_OPERATION`（公开操作），应明确写成 `saee.evaluate_agent_run`；
- 若是 `INTERNAL_REHEARSAL_OPERATION`（内部排演操作），应迁移到 `evaluate_rehearsal_run`；
- 若是 `HISTORICAL_FACT`（历史事实），应保留并从当前活动投影中隔离；
- 若仍是 `UNRESOLVED`（未解决），补丁不得合并。

### 3.2 阻塞项二：补丁范围没有与冻结白名单闭环

冻结调整计划已经明确：

- `D3`（第三类额外授权）对象不能自动纳入；
- 白名单外活动依赖必须停止；
- `ALLOWLIST_EXPANSION_AUTOMATIC=false`（禁止自动扩大白名单）；
- `NEW_HUMAN_AUTHORIZATION_REQUIRED=true`（需要新人工授权）。

补丁实际修改了以下三个 `D3`（第三类额外授权）文件：

- `ecosystem/mcp-entry-package-v1/mcp-tools.json`；
- `ecosystem/mcp-entry-package-v1/agent-usage-guide.md`；
- `agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json`。

实施报告在执行后把它们解释为内部投影，但冻结计划要求在实施前逐项判定并获得明确授权；
实施后的解释不能替代实施前授权。

此外，下列 16 个已修改文件没有以准确路径出现在冻结迁移地图中：

- `agent-readable.md`；
- `scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py`；
- `examples/ecosystem-demo-v1/mcp-demo.md`；
- `examples/ecosystem-demo-v1/agent-flow.md`；
- `examples/ecosystem-demo-v1/result-example.json`；
- `examples/ecosystem-demo-v1/README.md`；
- `examples/ecosystem-demo-v1/scenario/coding-agent-preflight.json`；
- `examples/agent-integrations/mcp-client-example/client_flow.md`；
- `examples/agent-integrations/mcp-client-example/README.md`；
- `examples/agent-integrations/mcp-client-example/example_config.json`；
- `docs/ecosystem/SAEE_ECOSYSTEM_ENTRY_PACKAGE_REVIEW.md`；
- `docs/release/SAEE_CAPABILITY_VERSION_POLICY.md`；
- `docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md`；
- `docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL.md`；
- `docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md`；
- `ecosystem/first-validation-candidate-package-v1/candidate-profile.md`。

其中多数变化与活动演示或说明同步有关，技术方向并非明显错误；问题是冻结计划采用逐文件白名单，
不能在补丁审查阶段用类别推断追认。应在新调整授权中逐文件确认，或从本补丁移除。

三个额外获授权实现文件的审查结果：

| 文件 | 结果 |
|---|---|
| `saee_backend/services/agent_run_capability.py` | 反向名称归一化后与基线实现一致；评估算法、原因码和证据判断未改变 |
| `saee_backend/services/capability_runtime/capability_registry_loader.py` | 新增内部来源解析条件分支；属于契约注册兼容逻辑，不是评估算法，但超出纯字符串替换 |
| `saee_backend/services/capability_truth_consistency_validator.py` | 新增历史名称归一化和内部操作状态条件分支；不是评估算法，但应在授权中明确为兼容逻辑 |

当前不能认定存在隐藏评估算法变化；但后两个条件分支需要被明确纳入“名称、标识和引用迁移”的授权解释，
不能依赖补丁完成后的追认。

### 3.3 阻塞项三：历史结果校验归一化范围过宽

`scripts/saee_first_external_validation_simulation_smoke.py:33-42` 新增递归函数，
对整个历史结果对象中的每个字符串执行：

```text
evaluate_agent_run -> evaluate_rehearsal_run
```

实际冻结结果中只有一个已知旧名称命中：

```text
integration_observations[1]
```

全对象递归替换会让未来任何位置出现的旧名称都被静默改写后再比较，降低校验器发现非预期旧名称传播的能力。
这不修改历史文件本身，但会放宽历史兼容校验边界。

必要调整：只归一化已登记的准确字段和值，并增加反向断言，证明除该字段外没有其他旧内部名称命中。

相比之下，`scripts/saee_mcp_ecosystem_dry_integration_smoke.py` 的归一化只处理已知工具发现字段、
已选工具字段及其摘要，范围是有界的。

### 3.4 阻塞项四：存在与名称收敛无关的索引变化

`agent-index.json:20406` 的 `generated_at`（生成时间）从基线时间更新为：

```text
2026-07-16T16:45:44.265765+00:00
```

该变化与内部工具名称、固定标识或引用迁移无关，应从补丁恢复，或由单独的索引再生成授权解释。

同文件还把两个 `recommended_next_pr`（历史建议字段）改写为兼容性说明。该方向符合“历史建议字段不应继续作为活动路线”的治理原则，
但它仍属于路线元数据语义变化，不应隐含在纯内部重命名补丁中。

### 3.5 原始差异包含忽略缓存删除

基线快照含有 23 个 `__pycache__`（Python 字节码缓存目录）或 `.pyc`（Python 字节码文件），
实施副本中不存在。它们在原始无索引差异中表现为删除，但：

- 当前仓库没有跟踪任何 `.pyc`（Python 字节码文件）；
- `.gitignore`（Git 忽略规则）明确忽略这些文件；
- 它们不属于 92 个实施源文件。

未来生成可合并补丁时必须明确排除这些缓存删除，不能把它们计入授权变更。

## 4. 通过项

### 4.1 公开能力保护

独立比较确认：

```text
PUBLIC_PROTECTED_FILES_EQUAL=13/13
PUBLIC_CAPABILITY_OBJECT_EQUAL=true
PUBLIC_MCP_OBJECTS_EQUAL=2/2
PUBLIC_TOOL_COUNT=2
PUBLIC_TOOLS=saee.evaluate_agent_run;saee.evaluate_evidence
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
PUBLIC_ALIAS_OWNERSHIP_CHANGED=false
```

公开请求、响应、公开实现、公开工具发现以及规范能力清单中的
`saee.evaluate_agent_run` 完整对象均保持不变。

### 4.2 字段语义和评估算法保护

九个内部 `Schema`（数据结构规范）在反向名称归一化后与基线完全一致：

```text
INTERNAL_SCHEMA_NAME_NORMALIZED_EQUAL=9/9
SCHEMA_FIELD_SEMANTICS_CHANGED=false
SCHEMA_REQUIRED_FIELDS_CHANGED=false
SCHEMA_TYPES_CHANGED=false
SCHEMA_NEW_FIELDS_ADDED=false
```

内部评估实现 `saee_backend/services/agent_run_capability.py` 在反向名称归一化并忽略文件末尾空行后与基线一致：

```text
INTERNAL_EVALUATION_IMPLEMENTATION_NAME_NORMALIZED_EQUAL=true
EVALUATION_ALGORITHM_CHANGED=false
REASON_CODES_CHANGED=false
EVIDENCE_DECISION_LOGIC_CHANGED=false
```

### 4.3 历史证据保护

以下目录与基线逐文件一致：

- `release/**`；
- `phase_b_product/**`；
- `docs/pilot/results/**`；
- `agent-interface/pilot/**`；
- `agent-interface/release/**`；
- `output/**`。

`reports/**`（报告目录）的唯一新增差异是 Phase 2（第二阶段）实施报告。

```text
HISTORICAL_EVIDENCE_UNCHANGED=true
RELEASE_SNAPSHOT_UNCHANGED=true
EXISTING_REPORTS_REWRITTEN=false
```

### 4.4 独立验证重放

在一次性临时可写副本中独立重放：

```text
TARGETED_VALIDATIONS_PASS=24/24
MAINLINE_GUARD_PASS=true
DIFF_WHITESPACE_ERRORS=0
```

`Mainline Guard`（主线守卫）第一次重放因临时副本继承只读文件权限，无法写入自生成模板而停止；
只在临时副本恢复所有者写权限后，主线守卫完整通过。该第一次停止属于审查环境权限问题，
不是补丁逻辑失败，也没有修改隔离补丁。

技术校验通过只能证明当前测试集合接受补丁。由于活动架构校验器本身仍断言旧内部名称，
它不能反向证明内部迁移已完整。

## 5. 六项审查结论

| 审查项 | 结论 | 说明 |
|---|---|---|
| 内部新入口是否完全替代旧入口 | 不通过 | 主要运行链已迁移，但活动架构、智能体可读投影和部分生态投影仍保留旧内部真值 |
| 规范公开能力是否保持不变 | 通过 | 公开对象、公开实现、公开请求响应和公开工具面均保持一致 |
| 公开 `MCP`（模型上下文协议）是否未变化 | 通过 | 两个公开或兼容对象逐对象一致；变化只出现在内部对象 |
| 公开 `Schema`（数据结构规范）是否未变化 | 通过 | 公开请求响应逐字节一致；内部九个结构仅固定名称迁移 |
| 历史证据是否未修改 | 通过 | 冻结目录一致；仅新增实施报告 |
| 基线差异是否完全可归因 | 不通过 | 存在白名单外文件、递归归一化、动态时间戳和忽略缓存删除 |

## 6. 合并前必须完成的最小调整

1. 对全部 `D3`（第三类额外授权）对象完成逐文件语义分类；
2. 迁移或明确命名空间化当前活动架构和智能体可读表面中的旧内部名称；
3. 对 16 个未列入冻结迁移地图的已修改文件进行新人工白名单绑定，或从补丁移除；
4. 把历史结果归一化限制到准确已登记字段，并新增“其他位置不得命中旧名称”的断言；
5. 恢复 `agent-index.json` 中与名称迁移无关的动态时间戳和未单独授权的路线元数据变化；
6. 明确排除 23 个忽略缓存删除；
7. 重新运行专项验证、公开契约比较和 `Mainline Guard`（主线守卫）；
8. 重新提交只读人工补丁审查。

本报告不授权上述调整，也不授权合并。

## 7. 回滚信息

当前隔离实施副本可以原样保留为第二次迁移尝试证据。若重新实施：

1. 从只读基线或经人工接受的新基线创建新的隔离副本；
2. 不使用 `git reset --hard`（Git 强制重置）；
3. 不修改主工作区已有用户变更；
4. 不自动重试；
5. 不回写历史报告、发布快照或既有证据；
6. 没有新的明确调整授权前，保持当前补丁不变。

## 8. 非主张

本报告不表示：

- 公开 `saee.evaluate_agent_run` 已改变；
- Phase 2（第二阶段）技术实现无价值；
- 内部评估算法发生改变；
- 新能力、新协议或第三套契约已经创建；
- 当前补丁已经合并、提交或推送；
- SAEE（硅基放大演化生态）已经生产就绪；
- Goal Integrity（目标完整性）副线已经重新开启。

## 9. 最终状态

```text
PHASE2_PATCH_REVIEW_STATUS=COMPLETE
PATCH_DECISION=PATCH_REQUIRES_ADJUSTMENT
PATCH_APPROVED_FOR_MERGE=false
MERGE_READY=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
SCHEMA_FIELD_SEMANTICS_CHANGED=false
EVALUATION_ALGORITHM_CHANGED=false
HISTORICAL_EVIDENCE_UNCHANGED=true
INTERNAL_RENAME_COMPLETE=false
NO_NEW_CAPABILITY=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
IMPLEMENTATION_SCOPE=CONTRACT_ALIGNMENT_ONLY
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PHASE2_PATCH_ADJUSTMENT_FINDINGS
```
