# SAEE Capability Contract Alignment（能力契约收敛）Phase 2.1（第二阶段一点一）范围扩展决策审查

日期：2026-07-17

## 1. 结论

本次只读审查不批准统一扩大白名单。四组阻塞对象具有不同的时间角色、消费路径和公开边界，不能作为同一批“旧内部名称残留”处理。

唯一分类如下：

| 对象 | 唯一分类 | 结论 |
|---|---|---|
| `PROJECT_STATUS.md` 中两个当前内部状态字段 | `REQUIRES_NEW_AUTHORIZATION`（需要新授权） | 属于活动当前真值，语义上需要迁移，但原授权没有覆盖该文件和准确字段 |
| `docs/release/SAEE_CAPABILITY_TRUTH_CONSISTENCY_VALIDATION.md` | `KEEP_AS_HISTORY`（保持历史） | 属于冻结版本的发布验证记录，不回写 |
| `sites/saee-commercial/public/agent-index.json` | `KEEP_PUBLIC_UNCHANGED`（保持公开不变） | 属于独立站点仓库的公开发现面，不纳入内部重命名补丁 |
| `sites/saee-commercial/dist/client/agent-index.json` | `KEEP_PUBLIC_UNCHANGED`（保持公开不变） | 属于公开索引的构建派生副本，不直接修改 |
| `agent-readable.md` 第 74 行 | `REQUIRES_NEW_AUTHORIZATION`（需要新授权） | 文件曾被列入白名单，但该准确对象未进入冻结命中登记 |

```text
ALLOW_MIGRATION_COUNT=0
KEEP_AS_HISTORY_COUNT=1
KEEP_PUBLIC_UNCHANGED_COUNT=2
REQUIRES_NEW_AUTHORIZATION_COUNT=2
IMPLEMENTATION_AUTHORIZED=false
```

这里的 `ALLOW_MIGRATION_COUNT=0` 不表示两个活动内部表面无需迁移，而是表示本次决策审查本身不把“语义上应迁移”自动升级为实施权限。

## 2. 审查边界

本次允许：

- 读取当前文件、消费路径、提交归属和隔离实施证据；
- 判断每个对象是活动真值、历史记录、公开发现面还是派生副本；
- 冻结后续授权需要的准确对象边界。

本次禁止并实际未执行：

- 修改代码、现有文档或索引；
- 修改 MCP（模型上下文协议）或 Schema（数据结构规范）；
- 恢复隔离迁移；
- 扩大白名单；
- 合并、暂存、提交或推送；
- 重新开启 Goal Integrity（目标完整性）副线。

## 3. `PROJECT_STATUS.md` 审查

### 3.1 对象角色

`PROJECT_STATUS.md` 不是单纯历史日志。它包含按主题维护的当前状态区块，并被 `scripts/mainline_guard.py`、多个状态协调器和 `agent-index.json`（智能体索引）引用。

本次命中的两个字段位于 `Agent Readiness Architecture v1.0`（智能体就绪架构第一版）当前真值区块：

```text
evaluate_agent_run_available=true
evaluate_agent_run_mcp_tool_registered=true
```

它们描述的是内部排演能力和内部工具登记，不是规范公开 `saee.evaluate_agent_run`（智能体运行评估）。因此：

```text
ACTIVE_INTERNAL_CONTRACT_SURFACE=true
HISTORICAL_STATUS_RECORD=false
PUBLIC_OPERATION_REFERENCE=false
```

### 3.2 处置决定

语义上，这两个字段应在未来准确迁移为内部排演名称；但是 `PROJECT_STATUS.md` 不在 Phase 2.1（第二阶段一点一）冻结文件白名单中，原授权明确禁止自动增加活动调用方。

唯一分类：

```text
PROJECT_STATUS_CLASSIFICATION=REQUIRES_NEW_AUTHORIZATION
```

未来若人工批准，只能授权以下两个准确字段及其当前区块，不得全文件替换：

```text
evaluate_agent_run_available
-> evaluate_rehearsal_run_available

evaluate_agent_run_mcp_tool_registered
-> evaluate_rehearsal_run_mcp_tool_registered
```

文件当前摘要：

```text
SHA256=59a7d6355372a5813479e8999e6a3e3b3784927af6c1773f347b05f8afcb9dea
TRACKED_IN_PARENT_REPOSITORY=true
```

## 4. 发布真值文档审查

### 4.1 对象角色

`docs/release/SAEE_CAPABILITY_TRUTH_CONSISTENCY_VALIDATION.md` 明确记录 `Phase 10.9`（第十阶段第九步）和 `v0.1`（第一小版本）时期的能力真值验证语义。其操作表保留：

```text
evaluate_agent_run = IMPLEMENTED
evaluate_evidence  = IMPLEMENTED
rehearse_agent     = CONTRACT_ONLY
```

该文档虽然仍由 `llms.txt`（大模型入口文件）、`agent-index.json`（智能体索引）和验证烟雾检查引用，但当前烟雾检查只验证其身份与非主张边界，不把文档中的旧操作表作为当前规范能力清单。隔离补丁中的真值一致性验证器也把冻结发布操作映射作为历史内部名称兼容输入，而不是回写发布记录。

因此它具有以下角色：

```text
RELEASE_VALIDATION_RECORD=true
HISTORICAL_EVIDENCE=true
CURRENT_CANONICAL_CAPABILITY_SOURCE=false
SAFE_TO_REWRITE_FOR_RENAME=false
```

### 4.2 处置决定

唯一分类：

```text
RELEASE_TRUTH_DOCUMENT_CLASSIFICATION=KEEP_AS_HISTORY
```

不得为了当前内部名称收敛修改该文档。未来当前契约说明必须引用规范能力清单或新增明确的当前边界说明，不能把历史发布记录改写成今天的事实。

文件当前摘要：

```text
SHA256=1bc20454a6d60cb61910f9e89111535c7408c28e3aff039bbee1ffd8151fed83
TRACKED_IN_PARENT_REPOSITORY=true
```

## 5. 两份站点智能体索引审查

### 5.1 来源与关系

`sites/saee-commercial` 是独立 Git（分布式版本控制系统）仓库，不属于父仓库追踪文件集合。

当前证据：

```text
SITE_REPOSITORY_HEAD=479b05b88f4938c2e69ef0ca786f4f714049a422
SITE_WORKTREE_CLEAN=true
PUBLIC_INDEX_SHA256=b83c1b81e085cc509d9a0d9af29e78a48d54776416db53f7be61928f0a39087a
DIST_INDEX_SHA256=b83c1b81e085cc509d9a0d9af29e78a48d54776416db53f7be61928f0a39087a
SITE_PUBLIC_EQUALS_DIST=true
ROOT_INDEX_EQUALS_SITE_PUBLIC=false
```

`public/agent-index.json` 是由站点测试直接读取并对外提供的公开发现文件；`dist/client/agent-index.json` 是构建产物中的字节相同副本。公开索引包含规范公开操作，也包含较早同步进去的内部架构投影。

这说明旧名称命中不是活动内部调用方，而是公开发现快照中的混合投影。直接修改它们会从“内部契约重命名”越界为“公开发现面同步”。

### 5.2 处置决定

两个对象分别分类为：

```text
SITE_PUBLIC_AGENT_INDEX_CLASSIFICATION=KEEP_PUBLIC_UNCHANGED
SITE_DIST_AGENT_INDEX_CLASSIFICATION=KEEP_PUBLIC_UNCHANGED
```

本轮不得：

- 手工修改公开索引；
- 直接修改构建副本；
- 把公开规范名称替换成内部名称；
- 把站点公开同步伪装成内部补丁收口。

站点公开索引与根索引不同步是一个已识别的公开投影边界问题，但不属于本轮内部契约迁移。若未来处理，必须单独审查公开投影来源、过滤规则、生成流程和发布授权；本报告不请求该授权。

## 6. `agent-readable.md` 第 74 行审查

### 6.1 对象角色

第 74 行位于当前 `SAEE Internal Agent Pilot Plan v1.0`（SAEE 内部智能体试点计划第一版）说明中：

```text
重要发现：evaluate_evidence 可直接复核授权证据；evaluate_agent_run 当前只支持 fixed internal rehearsal run，因此三次 Reliability Evaluation 使用明确标注的固定投影，direct_codex_evaluation_supported=false。
```

其中 `fixed internal rehearsal run` 表示“固定内部排演运行”，`Reliability Evaluation` 表示“可靠性评估”。

这不是公开 `saee.evaluate_agent_run`（智能体运行评估），也不是封存标题，而是对当前固定内部排演评估能力的说明。因此：

```text
ACTIVE_INTERNAL_EXPLANATION=true
PUBLIC_OPERATION_REFERENCE=false
HISTORICAL_FACT=false
```

### 6.2 处置决定

`agent-readable.md` 虽在十六个文件白名单内，但授权同时冻结了准确对象登记，并禁止全文件或递归替换。第 74 行没有进入冻结登记，因此文件级白名单不能替代对象级授权。

唯一分类：

```text
AGENT_READABLE_LINE_74_CLASSIFICATION=REQUIRES_NEW_AUTHORIZATION
```

未来若人工批准，只能把该句中的内部能力引用迁移为 `evaluate_rehearsal_run`（内部排演运行评估），并保留以下边界：

- `evaluate_evidence`（证据评估）语义不变；
- 规范公开 `saee.evaluate_agent_run`（智能体运行评估）不变；
- `direct_codex_evaluation_supported=false` 不变；
- 不改写试点结果、次数或历史证据。

文件当前摘要：

```text
SHA256=9a2f8c480544710737f9853e2ce25a4b91f276817ab46b4018f4df300a7011f8
TRACKED_IN_PARENT_REPOSITORY=true
```

## 7. 对 Phase 2.1（第二阶段一点一）停止条件的影响

本次分类把原来的四组阻塞拆成三种处置：

1. 两个活动内部真值对象需要新的准确人工授权；
2. 一个发布验证文档作为历史保留，不再作为活动迁移缺口；
3. 两个站点索引作为公开发现面保持不变，不再作为内部调用方迁移缺口。

因此，若未来人类只批准 `PROJECT_STATUS.md` 的两个准确字段和 `agent-readable.md` 第 74 行，仍不得修改发布真值文档或站点索引。完成这两个准确对象后，精确分类验证应把剩余旧名称分为：

```text
PUBLIC_OPERATION
HISTORICAL_FACT
LOCAL_IMPLEMENTATION_SYMBOL
PUBLIC_PROJECTION_FROZEN
```

只有不存在未分类的 `ACTIVE_INTERNAL_OPERATION`（活动内部操作）时，才能重新判断内部迁移是否完整。

## 8. 指挥官命令核查与前次教训

本次命令服务于 SAEE（硅基放大演化生态）与 Agent Evidence Integration（智能体证据集成）主线中的契约稳定性，没有把治理审查提升为独立产品或能力，也没有重新启动目标完整性副线。

```text
PROGRAM_MAINLINE=saee_agent_evidence_integration
IMPLEMENTATION_SCOPE=CONTRACT_ALIGNMENT_ONLY
MAINLINE_DRIFT_DETECTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

前几轮跑偏和半迁移教训在本次形成以下约束：

1. 旧名称命中不等于错误，必须结合路径、对象、时间和受众分类；
2. 文件进入白名单不等于文件中所有对象都获授权；
3. 发布记录不能为适配当前实现而回写；
4. 公开发现副本不能作为内部调用方自动迁移；
5. 构建副本必须由来源驱动，不能直接手工修补；
6. 局部验证通过不等于迁移完整，更不等于补丁可合并；
7. 精确分类验证不能用递归名称替换掩盖遗漏。

## 9. 非主张

本报告不表示：

- 已经批准扩大 Phase 2.1（第二阶段一点一）文件或对象白名单；
- 已经修改任何阻塞对象；
- 已经恢复隔离补丁实施；
- 公开能力、公开 MCP（模型上下文协议）或公开 Schema（数据结构规范）已经变化；
- 内部迁移已经完成；
- 补丁已经可以合并；
- 站点公开索引已经同步；
- 新能力、新协议或目标完整性方向已经建立。

## 10. 最终状态

```text
PHASE2_1_SCOPE_EXPANSION_DECISION_STATUS=COMPLETE
BLOCKING_OBJECT_GROUPS_REVIEWED=4
BLOCKING_OBJECTS_CLASSIFIED=5
ALLOW_MIGRATION_COUNT=0
KEEP_AS_HISTORY_COUNT=1
KEEP_PUBLIC_UNCHANGED_COUNT=2
REQUIRES_NEW_AUTHORIZATION_COUNT=2
PUBLIC_CAPABILITY_CHANGED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
MIGRATION_EXECUTED=false
ALLOWLIST_EXPANDED=false
IMPLEMENTATION_AUTHORIZED=false
PATCH_APPROVED_FOR_MERGE=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_TWO_EXACT_INTERNAL_OBJECT_AUTHORIZATION_NEED
```
