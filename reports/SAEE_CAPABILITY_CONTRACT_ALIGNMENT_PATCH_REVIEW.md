# SAEE Capability Contract Alignment（SAEE 能力契约收敛）隔离补丁人工审查

## 1. 审查结论

```text
PATCH_REVIEW_STATUS=COMPLETE
PATCH_DECISION=PATCH_REQUIRES_ADJUSTMENT
PATCH_APPROVED_FOR_MERGE=false
PATCH_MODIFIED_DURING_REVIEW=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
```

结论只能选择 `PATCH_REQUIRES_ADJUSTMENT`（补丁需要调整）。

规范公开能力、公开 MCP（模型上下文协议）、公开 Schema（数据结构规范）和历史证据均保持不变；
但内部重命名尚未覆盖全部活动调用方，现有演示与验证出现可复现回归，隔离基线也未包含当前宪法主线材料。
因此不能把当前补丁判定为满足合并条件。

本审查只新增本报告，没有修改隔离工作区中的代码、契约、测试或实施报告。

## 2. 审查对象与基线

```text
PATCH_WORKTREE=/Users/zhangbin/Documents/SAEE-contract-alignment-attempt-001
PATCH_BASELINE_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
MAIN_WORKTREE_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
PATCH_TRACKED_FILES_CHANGED=47
PATCH_REPORT_FILES_CREATED=1
```

两个工作区绑定同一 `HEAD`（当前提交指针），但主工作区存在大量尚未提交的宪法、治理、主线集成和
Agent Evidence（智能体证据）材料。隔离工作区只包含该提交的旧状态，因此“提交指针相同”不等于“治理基线相同”。

## 3. 六项审查结果

| 审查项 | 结论 | 证据 |
|---|---|---|
| `internal.saee.evaluate_rehearsal_run`（内部排演运行评估）是否完全替代旧内部入口 | 未完全替代 | 当前核心内部 MCP（模型上下文协议）、HTTP（超文本传输协议）和运行时已使用新名，但多个活动脚本、Schema（数据结构规范）和模拟器仍使用旧内部名，并造成实际失败 |
| `saee.evaluate_agent_run`（智能体运行评估）是否保持不变 | 是 | 规范能力对象前后完全相同；13 个公开保护文件逐字节无差异 |
| 公开 MCP（模型上下文协议）是否未变化 | 是 | 两个公开或兼容 MCP（模型上下文协议）表面及注册表对象前后相同；运行时发现仍为 `saee.evaluate_agent_run`、`saee.evaluate_evidence` |
| 公开 Schema（数据结构规范）是否未变化 | 是 | 千帆公开请求、响应 Schema（数据结构规范）和公开能力表面均无差异 |
| 历史证据是否未修改 | 是 | `release/**`、`phase_b_product/**` 和既有 `reports/**` 无受跟踪差异；仅实施报告为新增文件 |
| 基线是否满足合并要求 | 否 | 隔离基线缺少当前宪法文件，`mainline_guard.py`（主线守卫）无法通过；主工作区另有大量未提交主线变化 |

## 4. 已通过部分

### 4.1 当前核心内部发现面

实测结果：

```text
INTERNAL_TOOLS=evaluate_rehearsal_run;evaluate_evidence;rehearse_agent
EARLY_LOCAL_TOOLS=evaluate_evidence_adequacy;evaluate_rehearsal_run
LEGACY_INTERNAL_CALL_REJECTED=true
```

说明：当前能力包 MCP（模型上下文协议）适配器和早期本地工具注册表已经不再发现旧内部工具名。

### 4.2 公开能力和公开 MCP（模型上下文协议）

规范公开能力对象比较：

```text
PUBLIC_CAPABILITY_OBJECT_EQUAL=true
PUBLIC_MCP_SURFACE_EQUAL[saee.agent_readiness_mcp_stdio]=true
PUBLIC_MCP_SURFACE_EQUAL[saee.qianfan_readiness_mcp_stdio]=true
PUBLIC_MCP_REGISTRY_EQUAL[saee.agent_readiness_mcp_stdio]=true
PUBLIC_MCP_REGISTRY_EQUAL[saee.qianfan_readiness_mcp_stdio]=true
PUBLIC_TOOLS=saee.evaluate_agent_run;saee.evaluate_evidence
```

以下公开保护文件与隔离基线逐字节相同：

- `saee_backend/services/baidu_agent_readiness_service.py`
- `agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`
- `agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`
- `scripts/saee_agent_readiness_mcp_stdio.py`
- `scripts/saee_qianfan_readiness_mcp_stdio.py`
- `saee_backend/services/qianfan_readiness_mcp_adapter.py`
- `scripts/saee_qianfan_readiness_host.py`
- `saee_backend/services/marketplace_assessment_delivery.py`
- `.mcp.json`
- `.well-known/saee-capability-index.json`
- `agent-interface/public/saee-public-capability-surface.v0.1.json`
- `agent-interface/product/saee-agent-readiness-capability.v2.json`
- `docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md`

### 4.3 历史证据

没有修改既有发布快照、封存结果或历史报告。实施补丁通过比较时兼容映射解释旧发布名称，未回写历史文件。

```text
HISTORICAL_EVIDENCE_MODIFIED=false
RELEASE_SNAPSHOT_MODIFIED=false
PHASE_B_SNAPSHOT_MODIFIED=false
```

## 5. 阻塞合并的问题

### 5.1 活动内部调用方未完成迁移

以下仍可执行或仍参与当前校验的文件继续使用旧内部名称：

- `scripts/saee_capability_runtime_demo.py`
- `scripts/saee_capability_http_demo.py`
- `schemas/saee-mcp-dry-integration-trace.schema.v0.1.json`
- `schemas/saee-synthetic-mcp-agent.schema.v0.1.json`
- `saee_backend/services/mcp_ecosystem_discovery_simulator.py`
- `saee_backend/services/mcp_ecosystem_dry_integration.py`
- `saee_backend/services/mcp_result_interpretation_validator.py`
- `saee_backend/services/first_external_validation_simulation.py`
- `scripts/saee_mcp_ecosystem_dry_integration_smoke.py`
- `agent-interface/mcp/mcp-dry-integration-scenarios/RELIABILITY_ASSESSMENT_TASK.json`

另有若干生态示例、架构真值字段和集成示例仍使用旧无命名空间名称。部分可以保留为历史事实，
但补丁没有提供逐项“公开别名／内部模块函数／冻结历史证据／活动调用方”分类清单。

因此当前实施报告中的：

```text
INTERNAL_RENAME_COMPLETE=true
```

不能成立。

### 5.2 活动演示出现语义回归

`scripts/saee_capability_runtime_demo.py` 仍发送旧操作名。脚本退出码虽然为零，但其标记为
`VALID_EVALUATE_AGENT_RUN`（有效智能体运行评估）的案例实际返回：

```text
operation=UNKNOWN
status=REJECTED
reason_codes=CAPABILITY_OPERATION_UNDECLARED
```

`scripts/saee_capability_http_demo.py` 同样继续使用旧路径和旧操作名，所谓有效案例实际返回：

```text
http_status=404
operation=UNKNOWN
status=REJECTED
reason_codes=CAPABILITY_OPERATION_UNDECLARED
```

这不是单纯说明文字残留，而是当前可运行入口的行为回归。

### 5.3 两项现有验证失败

独立复验结果：

```text
saee_mcp_ecosystem_dry_integration_smoke.py=FAIL
reason=MCP_DRY_ADAPTER_DISCOVERY_MISMATCH

saee_first_external_validation_simulation_smoke.py=FAIL
reason=MCP_DRY_ADAPTER_DISCOVERY_MISMATCH
```

失败原因是模拟器仍预期旧工具列表，而当前适配器已经暴露新内部名称。

### 5.4 三个修改文件超出冻结白名单

按照 `SAEE_CAPABILITY_CONTRACT_ALIGNMENT_EXECUTION_BOUNDARY.md`（SAEE 能力契约收敛执行边界）逐项比较，
以下受跟踪修改不在冻结白名单中：

- `saee_backend/services/agent_run_capability.py`
- `saee_backend/services/capability_runtime/capability_registry_loader.py`
- `saee_backend/services/capability_truth_consistency_validator.py`

其中 `agent_run_capability.py` 还被原执行边界明确列为不应修改的内部评估实现文件。当前变化只涉及固定身份值，
没有发现算法变化；但文件范围仍需要新的明确授权或改为白名单内的适配方式，不能由审查者自行追认。

### 5.5 隔离基线不具备当前主线真值

隔离工作区的 `scripts/mainline_guard.py`（主线守卫）在进入能力校验前即失败：

```text
SAEE_CODEX_CONTEXT_CHECK: FAIL
missing=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
MAINLINE_GUARD=FAIL
```

该文件和相关治理材料存在于主工作区的未提交变化中，而不在隔离基线提交里。因此当前补丁无法证明它与
最新 SAEE Development Constitution（SAEE 开发宪法）及 Agent Evidence Integration（智能体证据集成）主线可合并。

## 6. 调整要求

补丁再次提交人工审查前，至少需要：

1. 把全部活动内部调用方、演示、Schema（数据结构规范）和模拟器迁移到
   `evaluate_rehearsal_run`（排演运行评估）；冻结历史证据保持原文。
2. 对全部剩余 `evaluate_agent_run` 命中建立逐项分类，无法分类的命中继续作为阻塞。
3. 修复运行时演示和 HTTP（超文本传输协议）演示，使“有效案例”真实返回成功，而不是仅退出码为零。
4. 使 MCP（模型上下文协议）干运行集成和首次外部验证模拟重新通过。
5. 对三个白名单外文件选择其一：恢复修改，或取得明确的白名单扩张授权。
6. 在包含当前宪法、治理注册表和 Agent Evidence Integration（智能体证据集成）主线真值的干净基线上重建补丁。
7. 让完整主线守卫通过；不得把“旧基线缺文件”解释为补丁通过。
8. 更新实施报告，使状态反映迁移尚未完成，直至上述条件全部关闭。

## 7. 非主张

本报告不表示：

- 内部重命名方案错误；
- 公开能力发生变化；
- 历史证据被污染；
- 补丁已合并、已提交或已推送；
- SAEE（硅基放大演化生态）已发布或生产就绪；
- 审查建议本身授权任何合并动作。

## 8. 最终状态

```text
PATCH_REVIEW_STATUS=COMPLETE
PATCH_DECISION=PATCH_REQUIRES_ADJUSTMENT
INTERNAL_RENAME_COMPLETE=false
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
HISTORICAL_EVIDENCE_UNCHANGED=true
ACTIVE_CALLER_MIGRATION_COMPLETE=false
ACTIVE_DEMO_REGRESSION_DETECTED=true
EXISTING_VALIDATION_FAILURES=2
FROZEN_ALLOWLIST_EXCEEDED=true
CURRENT_GOVERNANCE_BASELINE_INCLUDED=false
MAINLINE_GUARD_PASS=false
PATCH_APPROVED_FOR_MERGE=false
PATCH_MODIFIED_DURING_REVIEW=false
CODE_MODIFIED_DURING_REVIEW=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PATCH_ADJUSTMENT_REQUIREMENTS
```
