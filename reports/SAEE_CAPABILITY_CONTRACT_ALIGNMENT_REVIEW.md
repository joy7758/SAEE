# SAEE Capability Contract（能力契约）收敛审查

## 1. 结论

```text
CAPABILITY_CONTRACT_ALIGNMENT_REVIEW_STATUS=COMPLETE
CONTRACT_ALIGNMENT_CONCLUSION=CONTRACT_ALIGNMENT_REQUIRED
CANONICAL_PUBLIC_OPERATION=saee.evaluate_agent_run
INTERNAL_EXPERIMENT_OPERATION=evaluate_agent_run
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

唯一结论：`CONTRACT_ALIGNMENT_REQUIRED`（需要契约收敛）。

规范公开能力本身已经明确：`saee.evaluate_agent_run`（智能体运行评估）评估声明的智能体轨迹元数据
与固定就绪证据覆盖，规范实现是 `saee_backend/services/baidu_agent_readiness_service.py`，
规范入口是 `scripts/saee_agent_readiness_mcp_stdio.py`。

问题不在千帆兼容路由，也不在模块内部同名函数本身。问题在于另一个内部实验契约同时使用：

- 无命名空间操作名 `evaluate_agent_run`（智能体运行评估）；
- 规范能力标识 `saee.evaluate_agent_run`（智能体运行评估）；
- 完全不同的受控 Rehearsal Run（排演运行）输入与声明级 Evidence Adequacy（证据充分性）输出。

规范能力清单还把无命名空间别名 `evaluate_agent_run`（智能体运行评估）解析到规范公开能力，
而内部 MCP（模型上下文协议）和本地 HTTP（超文本传输协议）入口又用同一名称解释为内部排演评估。
智能体仅凭操作名无法稳定判断应提交哪一种输入，也无法稳定解释输出。

因此，当前的角色标签已经防止内部入口被错误列入公开两工具表面，但没有消除机器可发现契约的语义冲突。

## 2. 审查边界

本次仅审查现有事实，没有：

- 新建能力；
- 修改代码；
- 修改 MCP（模型上下文协议）；
- 修改 Schema（数据结构规范）；
- 修改规范能力清单；
- 引入 Goal Integrity（目标完整性）。

能力事实以 `capability-package/manifest.json#canonical_inventory`（规范能力清单）为唯一来源。
治理登记表、公开发现文件、内部能力包、代码和文档只作为投影或实现证据。

## 3. 语义族一：规范公开就绪评估

### 3.1 规范身份

```text
capability_id=saee.evaluate_agent_run
public_tool_name=saee.evaluate_agent_run
implementation_status=implemented
lifecycle_status=active
audience=public
role=canonical
stability=alpha
```

中文含义：规范公开的智能体运行就绪评估，本地 Alpha（早期试用）阶段。

### 3.2 真实输入

请求契约：`agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`。

| 字段 | 含义 |
|---|---|
| `request_id`（请求标识） | 调用请求标识 |
| `agent_id`（智能体标识） | 调用方声明的智能体标识，不是认证身份 |
| `task`（任务） | 非结构化任务摘要 |
| `trace.events`（轨迹事件） | 计划、工具调用、工具结果、检查和决策事件 |
| `evidence`（证据） | 固定四类证据的存在性声明与来源引用 |
| `customer_data_included=false`（未包含客户数据） | 本地输入边界 |

固定证据类型：

- `TEST_RESULT`（测试结果）；
- `ROLLBACK_PLAN`（回滚方案）；
- `PERMISSION_BOUNDARY`（权限边界）；
- `HUMAN_APPROVAL`（人工批准）。

如果事件声明为高影响或有外部影响，四类证据全部成为必需项；否则只要求测试结果。

### 3.3 真实输出

响应契约：`agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`。

输出包含：

- `readiness`（就绪状态）：继续、有条件、重新规划或停止；
- `score`（分数）：必需证据覆盖百分比，不是可靠性概率；
- 必需、已存在和缺失证据；
- 缺失证据映射出的风险；
- `CONTINUE`（继续）、`HUMAN_REVIEW_REQUIRED`（需要人工复核）、
  `REPLAN`（重新规划）或 `STOP`（停止）建议；
- 明确的非认证、非授权和非生产边界。

该语义不读取证据原文，不验证轨迹真实性，也不评估固定责任声明剖面。

### 3.4 属于该语义的入口

| 入口 | 角色 | 是否独立语义 |
|---|---|---|
| `saee_backend/services/baidu_agent_readiness_service.py#evaluate_agent_run` | 规范实现函数 | 是该语义的实现源 |
| `scripts/saee_agent_readiness_mcp_stdio.py` | 规范本地 MCP（模型上下文协议）入口 | 否，调用规范实现 |
| `scripts/saee_qianfan_readiness_mcp_stdio.py` | 千帆兼容入口 | 否，与规范入口共享适配器 |
| `scripts/saee_qianfan_readiness_host.py` | 提供方函数别名与规范操作映射 | 否，最终调用规范操作 |
| `saee_backend/services/marketplace_assessment_delivery.py` | 人工交付评估包内部委托 | 否，直接调用规范实现 |
| `.mcp.json` | 新本地集成的发现配置 | 否，启动规范入口 |
| `.well-known/saee-capability-index.json` | 仓库机器发现入口 | 否，指向规范公开两操作表面 |
| `agent-interface/public/saee-public-capability-surface.v0.1.json` | 公开能力描述 | 否，声明规范操作但不提供运行时 |

千帆侧 `saee_evaluate_agent_run`（智能体运行评估）只是提供方不支持点号时的函数别名，
它明确映射回 `saee.evaluate_agent_run`（智能体运行评估），输入输出语义没有变化，因此不是冲突来源。

## 4. 语义族二：内部排演证据充分性评估

### 4.1 内部身份

当前内部材料同时使用以下身份：

```text
operation=evaluate_agent_run
legacy_capability_id=saee.evaluate_agent_run
mcp_capability_id=saee.mcp.evaluate_agent_run
audience=internal
role=internal_or_experimental
```

中文含义：内部受控排演运行的证据充分性评估。

### 4.2 真实输入

核心输入不是公开就绪请求，而是完整 `rehearsal_run`（排演运行）：

- 受 `agent-interface/rehearsal/saee-agent-rehearsal-run.v0.1.schema.json` 约束；
- 包含运行、轨迹和 Evidence Export（证据导出）；
- 要求轨迹摘要与证据导出绑定；
- 固定声明类型为 `AUTHORIZED_AGENT_ACTION`（已授权智能体行动）；
- 只接受 SAEE 内部受控排演投影，不接受规范公开入口的声明轨迹请求。

MCP（模型上下文协议）内部请求契约：
`agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json`。

其真实参数只有：

```text
arguments.rehearsal_run
```

### 4.3 真实输出

核心输出不是覆盖分数与就绪建议，而是：

- `SUPPORTED`（得到证据支持）或 `INSUFFICIENT_EVIDENCE`（证据不足）；
- `PASS`（通过）或 `FAIL`（失败）的固定剖面结果；
- `missing_requirements`（缺失要求）；
- `failed_relationships`（失败关系）；
- 固定声明类型 `AUTHORIZED_AGENT_ACTION`（已授权智能体行动）；
- 不代表任务成功、安全、合规、认证或部署批准。

核心响应契约：`agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json`。

内部 MCP（模型上下文协议）响应投影：
`agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json`。

### 4.4 属于该语义的入口

| 入口 | 角色 | 实际行为 |
|---|---|---|
| `saee_backend/services/agent_run_capability.py#evaluate_agent_run` | 内部核心函数 | 校验排演运行、摘要绑定和固定声明剖面 |
| `scripts/saee_evaluate_agent_run.py` | 内部命令行入口 | 先执行本地排演，再调用内部核心函数 |
| `saee_backend/services/mcp_agent_run_tool_handler.py` | 早期内存工具处理器 | 暴露无命名空间 `evaluate_agent_run` |
| `saee_backend/services/local_mcp_server.py` | 早期无传输内存原型 | 在两工具列表中暴露内部操作 |
| `saee_backend/services/capability_runtime/capability_router.py` | 内部能力运行时路由 | 要求 `payload.rehearsal_run` |
| `scripts/saee_capability_mcp_stdio.py` | 内部能力包 MCP（模型上下文协议）入口 | 暴露无命名空间内部操作 |
| `/capabilities/evaluate-agent-run`（智能体运行评估本地路径） | 本地主机 HTTP（超文本传输协议）入口 | 路由到内部能力运行时 |
| `capability-package/openapi.yaml` | 内部能力包接口投影 | 描述排演语义而非规范公开语义 |
| `capability-package/mcp-tool.json` | 内部工具契约投影 | 描述排演语义而非规范公开语义 |
| `capability-package/capability-card.json` | 内部能力包发现卡 | 把操作描述为已验证排演运行评估 |
| `capability-package/examples/evaluate-agent-run.json` | 内部调用示例 | 提交 `rehearsal_run`（排演运行） |
| `agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json` | 历史内部能力卡 | 使用规范标识但描述内部排演语义 |

这些入口共享内部排演实现，不是十种不同算法；但它们共同扩大了同名语义冲突的发现面。
测试、基准、示例调用方和交付脚本中出现的同名调用，按其最终委托的上述实现归类，不另算新的契约语义。

## 5. 两类契约的不可互换差异

| 比较项 | 规范公开语义 | 内部排演语义 |
|---|---|---|
| 操作名 | `saee.evaluate_agent_run` | `evaluate_agent_run`，部分材料仍写 `saee.evaluate_agent_run` |
| 输入主体 | 声明轨迹与固定四类证据 | 完整 SAEE 排演运行与证据导出 |
| 轨迹要求 | 事件列表，无摘要绑定要求 | 轨迹摘要必须与证据导出绑定 |
| 证据模型 | 存在性声明 | 固定责任声明剖面的字段与关系 |
| 核心计算 | 必需证据覆盖百分比 | 声明剖面充分性校验 |
| 输出主状态 | 就绪状态和行动前建议 | 支持或证据不足 |
| 分数 | 0 至 100 覆盖百分比 | 无覆盖分数 |
| 固定声明类型 | 无 | `AUTHORIZED_AGENT_ACTION`（已授权智能体行动） |
| 适用对象 | 新本地外部智能体集成 | 内部受控排演与历史实验 |
| 可否互换请求 | 不可以 | 不可以 |
| 可否互换响应解释 | 不可以 | 不可以 |

两者都属于只读、非授权评估，但共同边界不能消除输入输出语义差异。

## 6. 冲突证据

### 6.1 规范别名冲突

规范能力清单为 `saee.evaluate_agent_run`（智能体运行评估）声明无命名空间别名
`evaluate_agent_run`（智能体运行评估）。规范解析器对两种输入都返回公开命名空间入口。

与此同时，内部能力包的工具列表、运行时、HTTP（超文本传输协议）路径和契约继续把
`evaluate_agent_run`（智能体运行评估）解释为排演语义。

结果：同一无命名空间名称由“使用哪个服务配置”决定输入输出语义，而不是由名称稳定决定。

### 6.2 规范能力标识复用冲突

`agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json` 把内部排演契约的
`capability_id`（能力标识）写成 `saee.evaluate_agent_run`（智能体运行评估）。

这与规范能力清单中同一标识的公开就绪语义不同，属于直接的标识语义冲突。

### 6.3 单一清单内的双重投影

`capability-package/manifest.json` 前部的规范能力清单把该能力定义为声明轨迹与证据覆盖评估；
同一文件后部的能力包操作又把无命名空间 `evaluate_agent_run`（智能体运行评估）定义为排演评估，
并把历史内部能力卡列为 `canonical_local_sources`（规范本地来源）之一。

这会让只读取能力包而未解析规范清单优先级的智能体得到不同结论。

### 6.4 当前校验的覆盖缺口

现有能力真值一致性校验能够核对：

- 公开操作集合；
- 能力身份、状态和生命周期；
- 协议与公开边界；
- 发布、采用和生产状态。

它没有比较公开与内部同名操作的请求 Schema（数据结构规范）、响应 Schema（数据结构规范）、
计算语义或别名占用。因此校验通过与“同名契约已经收敛”并不等价。

内部校验输出中的 `canonical_agent_run_alpha_reused=true`（复用了内部规范排演实现）是历史内部命名，
不能覆盖规范能力清单已经冻结的公开规范实现。

## 7. 规范公开能力与内部实验能力归属

### 7.1 规范公开能力

唯一规范公开能力是：

```text
saee.evaluate_agent_run
```

中文：智能体运行就绪评估。

其规范实现、请求、响应与入口分别是：

```text
implementation=saee_backend/services/baidu_agent_readiness_service.py
request=agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json
response=agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json
entry=scripts/saee_agent_readiness_mcp_stdio.py
```

### 7.2 内部实验能力

以下语义只属于内部实验：

> 对受控 SAEE 排演运行的轨迹摘要绑定与固定责任声明证据充分性进行评估。

其核心实现是 `saee_backend/services/agent_run_capability.py`，不应继续与规范公开能力共享机器标识。

## 8. 是否需要重新命名或明确边界

结论：需要契约收敛，优先重新命名内部机器可发现操作；只增加文档边界不足。

### 8.1 保持不变的名称

- 保留 `saee.evaluate_agent_run`（智能体运行评估）作为唯一规范公开名称；
- 保留千帆兼容入口的同名路由；
- 提供方函数别名可以保留，但必须继续一对一映射规范公开语义。

### 8.2 应收敛的内部名称

建议未来在单独授权下，把内部机器可发现操作改成能够表达排演语义的名称，例如：

```text
internal.saee.evaluate_rehearsal_run
```

中文：内部 SAEE 排演运行评估。

如果内部传输不接受点号，可使用：

```text
evaluate_rehearsal_run
```

中文：排演运行评估。

本报告不批准具体改名，也不创建新能力；该名称只是现有内部能力的消歧候选。

### 8.3 无命名空间别名规则

必须在未来收敛决策中二选一：

1. 将 `evaluate_agent_run`（智能体运行评估）无命名空间别名永久保留给规范公开能力，
   内部工具停止占用；或
2. 取消规范公开能力的无命名空间别名，只允许精确调用 `saee.evaluate_agent_run`（智能体运行评估）。

不允许继续让规范解析器和内部工具服务器同时拥有同一无命名空间名称的不同契约。

### 8.4 不必作为首要改动的内部函数名

两个 Python（蟒蛇编程语言）模块内部函数都叫 `evaluate_agent_run`（智能体运行评估），
由于模块路径不同，程序调用可以明确区分。首要冲突是工具名、能力标识、契约卡和别名，
不是模块作用域内的函数名。未来可以为可读性调整函数名，但不是契约收敛的必要前提。

## 9. 智能体推荐门判断

```text
AGENT_RECOMMENDATION_GATE=conditional
```

中文：有条件推荐。

如果潜在客户要求本地、只读的声明证据就绪评估，可以推荐使用精确命名的
`saee.evaluate_agent_run`（智能体运行评估）。

如果客户或智能体通过无命名空间名称、能力包 MCP（模型上下文协议）或本地 HTTP（超文本传输协议）
发现能力，当前存在提交错误请求或误解输出的风险。在内部操作完成消歧前，不应把这些入口推荐为统一客户契约。

## 10. 最小收敛顺序

未来若获得修改授权，最小顺序应是：

1. 冻结 `saee.evaluate_agent_run`（智能体运行评估）的公开输入、输出和实现为唯一规范语义；
2. 决定无命名空间别名归属；
3. 对内部排演工具采用明确的内部名称或停止机器发现；
4. 修正历史内部能力卡的能力标识，不改变内部算法；
5. 为旧内部名称提供有期限、显式标注的兼容说明；
6. 扩展真值一致性校验，使其能够发现同名操作的请求与响应语义冲突；
7. 运行全部公开、内部、兼容和治理校验后，再判断契约是否达到 `CONTRACT_ALIGNED`（契约一致）。

这些动作属于未来收敛工作，不在本次只读审查授权内。

## 11. 非主张

本报告不表示：

- 已经改名；
- 已经修改任何 Schema（数据结构规范）；
- 已经弃用内部工具；
- 已经修改 MCP（模型上下文协议）；
- 已经创建新能力；
- 已经实现公开服务、客户验证或生产就绪；
- 已经重新开启 Goal Integrity（目标完整性）副线。

## 12. 最终状态

```text
CAPABILITY_CONTRACT_ALIGNMENT_REVIEW_STATUS=COMPLETE
CONTRACT_ALIGNMENT_CONCLUSION=CONTRACT_ALIGNMENT_REQUIRED
CANONICAL_PUBLIC_OPERATION=saee.evaluate_agent_run
CANONICAL_PUBLIC_SEMANTICS=DECLARED_TRACE_AND_READINESS_EVIDENCE_COVERAGE
INTERNAL_EXPERIMENT_OPERATION=evaluate_agent_run
INTERNAL_EXPERIMENT_SEMANTICS=CONTROLLED_REHEARSAL_EVIDENCE_ADEQUACY
UNQUALIFIED_ALIAS_COLLISION=true
CAPABILITY_ID_SEMANTIC_COLLISION=true
INTERNAL_OPERATION_RENAME_RECOMMENDED=true
PUBLIC_OPERATION_RENAME_RECOMMENDED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_CAPABILITY_CONTRACT_ALIGNMENT
```
