# SAEE Capability Contract Alignment（SAEE 能力契约收敛）实施计划

## 1. 结论

```text
CAPABILITY_CONTRACT_ALIGNMENT_IMPLEMENTATION_PLAN_STATUS=COMPLETE
IMPLEMENTATION_CONCLUSION=MINIMAL_RENAME_REQUIRED
CANONICAL_PUBLIC_OPERATION=saee.evaluate_agent_run
INTERNAL_TARGET_OPERATION=evaluate_rehearsal_run
INTERNAL_TARGET_CAPABILITY_ID=internal.saee.evaluate_rehearsal_run
PUBLIC_OPERATION_RENAME_REQUIRED=false
INTERNAL_IMPLEMENTATION_REDESIGN_REQUIRED=false
IMPLEMENTATION_AUTHORIZED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

唯一结论：`MINIMAL_RENAME_REQUIRED`（需要最小重命名）。

规范公开操作 `saee.evaluate_agent_run`（智能体运行评估）保持名称、请求、响应、实现和对外发现入口不变。
内部受控排演能力需要把机器可发现操作名从 `evaluate_agent_run`（智能体运行评估）收敛为
`evaluate_rehearsal_run`（排演运行评估），并把内部能力标识收敛为
`internal.saee.evaluate_rehearsal_run`（内部 SAEE 排演运行评估）。这只是现有内部能力的重命名和重新归类，
不是新建能力，也不改变评估算法。

本文件只是实施影响评估，不授权改名。当前 `Phase 1 Capability Alignment`（第一阶段能力对齐）仍未获授权。

## 2. 主线与治理核查

```text
PROGRAM_MAINLINE=saee_agent_evidence_integration
MAINLINE_DRIFT_DETECTED=false
AFFECTED_CUSTOMER_VERSION=SAEE_Evaluation
AFFECTED_EVOLUTION_SUBSYSTEM=Pareto_Fitness_Evaluation;Evolutionary_Archive_Rollback_Immune_System
CAPABILITY_FACT_CHANGE_PLANNED=false
```

本任务修复 `SAEE Evaluation`（SAEE 评估）入口的语义稳定性，服务 SAEE 与 Agent Evidence Project
（智能体证据项目）受控集成主线，没有重新开启 Goal Integrity（目标完整性）副线。

受影响能力分类：

| 对象 | 当前分类 | 本计划判断 |
|---|---|---|
| `saee.evaluate_agent_run`（智能体运行评估） | `implemented`（已实现）、`active`（活跃） | 规范公开能力，保持不变 |
| 内部排演运行评估 | 本地内部 Alpha（早期试用）实现，未形成独立规范公开能力 | 复用现有实现，只改内部机器身份 |
| 新能力 | 不存在 | 不创建 |

防重复建设判断：仓库已有两组实现和完整测试面；创建第三个评估器、复制内部实现或增加第二个规范公开入口均不允许。

智能体推荐门判断：

```text
CURRENT_AGENT_RECOMMENDATION=conditional
TARGET_AGENT_RECOMMENDATION_AFTER_ALIGNMENT=recommend
```

中文含义：当前只能有条件推荐精确名称 `saee.evaluate_agent_run`（智能体运行评估）；内部同名入口未消歧前，
不能向潜在客户推荐无命名空间入口。完成最小改名并通过全部校验后，规范公开入口才具备稳定推荐条件。

## 3. 全部引用盘点

使用仓库范围检索：

```bash
rg -n 'saee\.evaluate_agent_run|\bevaluate_agent_run\b' .
```

盘点结果：278 个文件、738 处命中。目录分布如下：

| 目录 | 文件数 | 处理原则 |
|---|---:|---|
| `reports/`（报告） | 65 | 历史证据，默认保持原文 |
| `docs/`（文档） | 47 | 只更新当前有效的内部契约文档 |
| `agent-interface/`（智能体接口） | 43 | 按公开与内部语义逐项分类 |
| `scripts/`（脚本） | 36 | 更新内部调用和校验，公开入口不动 |
| `saee_backend/`（SAEE 后端） | 20 | 只更新内部路由和适配器 |
| `cloud-entry-package/`（云入口包） | 13 | 公开或历史交付投影，默认不动 |
| `examples/`（示例） | 10 | 公开示例不动；内部排演示例同步 |
| `schemas/`（数据结构规范） | 8 | 只改现有内部枚举和引用，不新增语义 |
| `capability-package/`（能力包） | 7 | 同一文件中的规范清单区保持不变，内部操作区同步 |
| 仓库根文件 | 7 | 只更新当前机器发现区块，不改历史段落 |
| `phase_b_product/`（第二阶段产品快照） | 5 | 冻结快照，不回写 |
| `saee-agent-review-skill/`（SAEE 智能体评审技能） | 4 | 当前不改，继续引用公开规范入口 |
| `release/`（发布快照） | 4 | 历史发布证据，不回写 |
| `governance/`（治理） | 4 | 仅内部 MCP（模型上下文协议）工具清单未来同步 |
| `ecosystem/`（生态材料） | 4 | 按当前公开或历史投影处理 |
| `adapters/`（适配器） | 1 | 公开规范适配器，不动 |

命中不等于必须修改。完整处理采用以下四类：

1. 公开规范入口：保持不变；
2. 当前有效内部机器契约：未来最小改名；
3. 当前测试、文档和机器投影：随内部改名同步；
4. 历史报告、收据、发布包和冻结快照：保持原始名称，禁止全局替换。

## 4. 规范公开能力：必须保持不变

### 4.1 规范身份

```text
capability_id=saee.evaluate_agent_run
tool_name=saee.evaluate_agent_run
implementation=saee_backend/services/baidu_agent_readiness_service.py
entrypoint=scripts/saee_agent_readiness_mcp_stdio.py
```

真实输入：声明的任务、智能体标识、轨迹事件和四类证据存在性信息。

真实输出：就绪状态、证据覆盖百分比、缺失证据、风险和
`CONTINUE`（继续）、`HUMAN_REVIEW_REQUIRED`（需要人工复核）、`REPLAN`（重新规划）或
`STOP`（停止）建议。

### 4.2 不改文件

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

`capability-package/manifest.json#canonical_inventory`（规范能力清单）中的公开能力身份、实现、入口和
别名 `evaluate_agent_run`（智能体运行评估）也保持不变。该无命名空间别名未来只归规范公开能力使用。

## 5. 内部排演能力：最小改名对象

### 5.1 当前真实语义

内部实现接收完整 `rehearsal_run`（排演运行），验证轨迹摘要和证据导出绑定，并按固定
`AUTHORIZED_AGENT_ACTION`（已授权智能体行动）证据剖面返回
`SUPPORTED`（得到证据支持）或 `INSUFFICIENT_EVIDENCE`（证据不足）。

它没有公开能力的覆盖分数和就绪建议，也不接受公开请求结构。

### 5.2 冻结的目标名称

```text
internal_operation=evaluate_rehearsal_run
internal_capability_id=internal.saee.evaluate_rehearsal_run
internal_http_path=/capabilities/evaluate-rehearsal-run
```

名称含义：内部 SAEE 排演运行评估。

以下内容保持不变：排演运行输入、摘要绑定、固定声明剖面、充分性判断、原因码、限制和非授权边界。

### 5.3 未来必须同步的当前有效机器契约

| 类别 | 文件 | 最小动作 |
|---|---|---|
| 能力包内部操作 | `capability-package/manifest.json` | 只改内部操作区、内部 MCP（模型上下文协议）表面和内部来源引用；规范清单区不动 |
| 内部工具描述 | `capability-package/mcp-tool.json` | 工具名改为排演语义名称 |
| 内部 HTTP（超文本传输协议）描述 | `capability-package/openapi.yaml` | 只改内部路径和操作标识 |
| 内部能力卡 | `capability-package/capability-card.json` | 同步内部操作名 |
| 内部示例 | `capability-package/examples/evaluate-agent-run.json` | 文件与操作标识改为排演语义，输入事实不变 |
| 内部能力卡 | `agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json` | 文件和能力标识改为内部排演身份 |
| 内部输出契约 | `agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json` | 文件和固定能力标识改名，字段语义不变 |
| 内部 MCP（模型上下文协议）能力卡 | `agent-interface/mcp/saee-evaluate-agent-run-mcp-capability.v0.1.json` | 改为内部排演身份 |
| 内部 MCP（模型上下文协议）请求与响应 | `agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json`、`agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json` | 文件与工具常量改名，字段语义不变 |
| 内部适配器声明 | `agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json`、`agent-interface/mcp/saee-capability-mcp-stdio-config.v0.1.json` | 更新内部工具清单 |
| 内部 HTTP（超文本传输协议）声明 | `agent-interface/http/saee-capability-http-adapter.v0.1.json` | 更新内部路径映射 |
| 运行时路由 | `saee_backend/services/capability_runtime/capability_invocation.py`、`saee_backend/services/capability_runtime/capability_router.py` | 更新已知操作集合和分派条件 |
| 调用收据 | `saee_backend/services/capability_runtime/invocation_receipt.py` | 更新内部操作枚举和摘要元数据 |
| 内部 MCP（模型上下文协议）适配器 | `saee_backend/services/capability_mcp_adapter.py` | 更新工具定义、调用名和标题 |
| 内部 HTTP（超文本传输协议）适配器 | `saee_backend/services/capability_http_adapter/http_request_handler.py` | 更新内部路径与操作映射 |
| 早期内存原型 | `saee_backend/services/mcp_agent_run_tool_handler.py`、`saee_backend/services/local_mcp_server.py` | 更新内部工具发现名 |
| 内部命令行入口 | `scripts/saee_evaluate_agent_run.py` | 未来改为排演语义文件名；算法委托不变 |
| 治理投影 | `governance/registry/mcp-registry.json` | 只改内部入口的工具列表 |

`saee_backend/services/agent_run_capability.py#evaluate_agent_run` 是模块作用域内部函数。模块路径已经消歧，
其函数名不是本轮契约收敛的必要改动；为减少风险，首轮实施不改该函数。

现有 Schema（数据结构规范）只允许重命名固定标识和引用，不允许新增字段、改变输入输出含义或形成第三套契约。

## 6. 测试、文档与机器投影同步范围

### 6.1 必须同步的测试

- `scripts/saee_evaluate_agent_run_mcp_smoke.py`
- `scripts/saee_capability_runtime_smoke.py`
- `scripts/saee_capability_mcp_adapter_smoke.py`
- `scripts/saee_capability_http_adapter_smoke.py`
- `scripts/saee_capability_service_package_smoke.py`
- `scripts/saee_capability_alpha_release_smoke.py`
- `scripts/saee_local_mcp_prototype_smoke.py`

如这些校验仍读取冻结的历史包，应保留旧断言并新增“历史名称不属于当前活动发现面”的边界断言，不能回写历史包。

### 6.2 必须同步的当前文档

- `docs/CAPABILITY_INVENTORY.md`
- `capability-package/README.md`
- `capability-package/limitations.md`
- `docs/architecture/SAEE_AGENT_CAPABILITY_ALPHA.md`
- `docs/architecture/SAEE_EVALUATE_AGENT_RUN_MCP_CAPABILITY.md`
- `docs/architecture/SAEE_CAPABILITY_RUNTIME_ALPHA.md`
- `docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md`
- `docs/architecture/SAEE_CAPABILITY_HTTP_ADAPTER_ALPHA.md`
- `docs/architecture/SAEE_LOCAL_MCP_PROTOTYPE.md`

`README.md`、`agent-index.json` 和 `llms.txt` 只更新当前发现区块与当前契约索引；历史阶段记录原样保留。
`AGENTS.md` 的规范指针、启动规则和防重复建设流程没有变化，因此无需更新。

### 6.3 必须增强的校验

未来实施必须扩展现有校验，而不是新建第二套真值检查器：

1. `scripts/saee_canonical_capability_inventory_smoke.py`：确认公开别名不被内部活动工具占用；
2. `scripts/saee_capability_truth_consistency_smoke.py`：比较活动操作的请求、响应和语义族；
3. `scripts/saee_governance_registry_check.py`：确认内部工具列表使用排演语义名称；
4. `scripts/saee_capability_service_package_smoke.py`：确认内部包不再宣称公开规范身份；
5. 公开表面校验：确认对外仍然只有 `saee.evaluate_agent_run` 与 `saee.evaluate_evidence`。

## 7. 兼容策略与停止条件

### 7.1 兼容策略

当前规范清单记录 `usage_evidence=UNKNOWN`（使用证据未知）。因此未来实施前必须先检索活动调用方，
不能直接假设旧内部名称无人使用。

默认迁移规则：

1. 新内部工具列表只发布 `evaluate_rehearsal_run`（排演运行评估）；
2. 无命名空间 `evaluate_agent_run`（智能体运行评估）只解析到规范公开能力；
3. 历史报告、收据、发布包和冻结快照保留旧名称；
4. 如果发现活动内部调用方，允许短期、非发现式、明确标记弃用的兼容路由；
5. 兼容路由必须记录替代名称、调用方、移除条件和期限；移除前契约状态只能标记为迁移中；
6. 不得把内部排演能力加入规范公开能力清单作为第二个正式能力。

### 7.2 停止条件

出现以下任一情况必须停止实施并申请人工复核：

- 需要修改规范公开请求或响应语义；
- 需要重写内部评估算法；
- 需要新建能力、第二个规范入口或第三套 Schema（数据结构规范）；
- 活动外部调用方依赖旧内部排演语义且没有可验证迁移路径；
- 全部引用无法区分当前投影与历史证据；
- Goal Integrity（目标完整性）或其他副线被重新加入改名范围；
- Phase 1 Capability Alignment（第一阶段能力对齐）仍未授权却开始修改实现。

## 8. 最小实施顺序

未来获得独立授权后，严格按以下顺序执行：

1. 记录当前公开与内部契约的文件摘要和调用方盘点；
2. 冻结公开规范入口及无命名空间别名归属；
3. 重命名内部能力标识、工具名、路径和现有 Schema（数据结构规范）固定值；
4. 更新内部运行时路由和适配器，不改评估算法；
5. 更新内部测试、当前文档和机器投影；
6. 增强现有真值一致性校验；
7. 运行公开、内部、兼容、治理和主线校验；
8. 只有全部活动发现面不再存在双语义时，才可记录 `CONTRACT_ALIGNED`（契约一致）。

建议作为一次受控变更完成，避免出现“文档已改名、运行时仍旧名”或“内部已改名、机器投影仍旧名”的半迁移状态。

## 9. 未来验收命令

```bash
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_truth_consistency_smoke.py
python3 scripts/saee_capability_service_package_smoke.py
python3 scripts/saee_capability_mcp_adapter_smoke.py
python3 scripts/saee_capability_http_adapter_smoke.py
python3 scripts/saee_public_capability_surface_smoke.py
python3 scripts/saee_qianfan_readiness_mcp_smoke.py
git diff --check
```

验收必须同时证明：

- 公开规范入口名称、请求、响应和行为未变；
- 内部活动发现面只使用排演语义名称；
- 旧内部名称不再与公开别名形成活动双语义；
- 历史证据未被回写；
- 没有新能力、评估器、规范入口或数据结构规范；
- `GOAL_INTEGRITY_SECONDARY_LANE=STOPPED`（目标完整性副线停止）继续成立。

## 10. 非主张

本计划不表示：

- 已实施重命名；
- 已修改代码、MCP（模型上下文协议）或 Schema（数据结构规范）；
- 已创建新能力；
- 内部排演能力已经成为公开产品；
- 外部开发者已经验证；
- 客户验证、产品发布或生产就绪已经成立；
- Goal Integrity（目标完整性）副线已经重新开启。

## 11. 最终状态

```text
CAPABILITY_CONTRACT_ALIGNMENT_IMPLEMENTATION_PLAN_STATUS=COMPLETE
IMPLEMENTATION_CONCLUSION=MINIMAL_RENAME_REQUIRED
CANONICAL_PUBLIC_OPERATION=saee.evaluate_agent_run
CANONICAL_PUBLIC_OPERATION_CHANGED=false
INTERNAL_CURRENT_OPERATION=evaluate_agent_run
INTERNAL_TARGET_OPERATION=evaluate_rehearsal_run
INTERNAL_TARGET_CAPABILITY_ID=internal.saee.evaluate_rehearsal_run
UNQUALIFIED_PUBLIC_ALIAS_RESERVED=true
INTERNAL_EVALUATOR_REUSED=true
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
IMPLEMENTATION_AUTHORIZED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_CAPABILITY_CONTRACT_ALIGNMENT_IMPLEMENTATION_PLAN
```
