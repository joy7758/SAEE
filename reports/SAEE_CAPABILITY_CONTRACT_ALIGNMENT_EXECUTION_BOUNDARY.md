# SAEE Capability Contract Alignment（SAEE 能力契约收敛）执行边界冻结

## 1. 边界结论

```text
CAPABILITY_CONTRACT_ALIGNMENT_EXECUTION_BOUNDARY_STATUS=COMPLETE
BOUNDARY_TYPE=PLAN_ONLY
CANONICAL_PUBLIC_OPERATION=saee.evaluate_agent_run
INTERNAL_CURRENT_OPERATION=evaluate_agent_run
INTERNAL_TARGET_OPERATION=evaluate_rehearsal_run
IMPLEMENTATION_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
```

本文件只冻结未来最小重命名的执行边界，不授权执行。

唯一允许提交后续人工授权的目标是：把现有内部排演语义的机器可发现名称
`evaluate_agent_run`（智能体运行评估）迁移到 `evaluate_rehearsal_run`（排演运行评估），
同时保持规范公开能力 `saee.evaluate_agent_run`（智能体运行评估）完全不变。

## 2. 主线与范围核查

```text
PROGRAM_MAINLINE=saee_agent_evidence_integration
AFFECTED_CUSTOMER_VERSION=SAEE_Evaluation
MAINLINE_DRIFT_DETECTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
NEW_CAPABILITY_CREATED=false
```

本计划服务 SAEE Evidence（SAEE 证据）与 SAEE Evaluation（SAEE 评估）的受控集成主线，
不是 Goal Integrity（目标完整性）研究、状态引擎、权限系统或新产品设计。

## 3. 公开能力保护范围

### 3.1 保护目标

```text
PUBLIC_OPERATION=saee.evaluate_agent_run
PUBLIC_ALIAS=evaluate_agent_run
PUBLIC_IMPLEMENTATION=saee_backend/services/baidu_agent_readiness_service.py
PUBLIC_ENTRYPOINT=scripts/saee_agent_readiness_mcp_stdio.py
PUBLIC_REQUEST=agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json
PUBLIC_RESPONSE=agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json
```

确认：`saee.evaluate_agent_run`（智能体运行评估）必须保持名称、输入、输出、实现、行为、发现入口和
非授权边界不变。

### 3.2 公开只读保护文件

以下文件在未来实施中必须保持逐字节不变：

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

### 3.3 同文件内的公开保护区

`capability-package/manifest.json` 同时包含规范能力清单和内部能力包投影。未来该文件虽然可能进入内部改名
白名单，但以下公开内容必须通过实施前后规范化摘要证明完全不变：

- `canonical_inventory.capabilities` 中 `capability_id=saee.evaluate_agent_run` 的完整对象；
- 规范公开 MCP（模型上下文协议）表面 `saee.agent_readiness_mcp_stdio`；
- 千帆兼容表面 `saee.qianfan_readiness_mcp_stdio`；
- 公开别名 `evaluate_agent_run`（智能体运行评估）的归属。

同理，`governance/registry/mcp-registry.json` 只允许修改内部入口
`saee.capability_package_mcp_stdio` 的工具列表；两个公开或兼容入口的对象必须保持不变。

### 3.4 公开行为保护断言

实施后必须继续满足：

```text
PUBLIC_TOOL_COUNT=2
PUBLIC_TOOLS=saee.evaluate_agent_run;saee.evaluate_evidence
PUBLIC_REQUEST_SEMANTICS_CHANGED=false
PUBLIC_RESPONSE_SEMANTICS_CHANGED=false
PUBLIC_IMPLEMENTATION_CHANGED=false
PUBLIC_ALIAS_OWNERSHIP_CHANGED=false
```

任一断言不成立，立即停止并回滚。

## 4. 未来允许修改范围

本节只是未来实施白名单候选。当前没有授权修改任何文件。

### 4.1 内部契约与投影白名单

| 文件 | 允许的最小变化 |
|---|---|
| `capability-package/manifest.json` | 只改内部工具表面、内部来源引用和内部操作对象中的旧名称 |
| `capability-package/mcp-tool.json` | 只改内部工具名及现有请求、响应引用 |
| `capability-package/openapi.yaml` | 只改内部路径和操作标识 |
| `capability-package/capability-card.json` | 只改内部操作名 |
| `capability-package/examples/evaluate-agent-run.json` | 未来改为排演语义文件名和操作标识，输入事实不变 |
| `agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json` | 未来改为内部排演能力卡名称和标识 |
| `agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json` | 未来改为排演语义文件名和固定能力标识，字段不变 |
| `agent-interface/mcp/saee-evaluate-agent-run-mcp-capability.v0.1.json` | 未来改为内部排演工具卡名称和标识 |
| `agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json` | 未来改为排演语义文件名和工具常量，字段不变 |
| `agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json` | 未来改为排演语义文件名，响应语义不变 |
| `agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json` | 只改内部工具清单 |
| `agent-interface/mcp/saee-capability-mcp-stdio-config.v0.1.json` | 只改内部工具清单 |
| `agent-interface/http/saee-capability-http-adapter.v0.1.json` | 只改内部路径映射 |
| `schemas/saee-capability-invocation-response.schema.v0.1.json` | 只替换内部操作枚举，不增加字段 |
| `schemas/saee-capability-invocation-receipt.schema.v0.1.json` | 只替换内部操作枚举，不增加字段 |
| `schemas/saee-capability-http-response.schema.v0.1.json` | 只替换内部操作枚举，不增加字段 |

文件重命名属于既有内部契约迁移，不得被登记为新 Schema（数据结构规范）或新能力。旧文件的来源与替代关系必须可追踪。

### 4.2 内部实现路由白名单

| 文件 | 允许的最小变化 |
|---|---|
| `saee_backend/services/capability_runtime/capability_invocation.py` | 更新内部已知操作常量 |
| `saee_backend/services/capability_runtime/capability_router.py` | 更新内部分派条件；继续调用原实现函数 |
| `saee_backend/services/capability_runtime/invocation_receipt.py` | 更新内部收据操作常量 |
| `saee_backend/services/capability_mcp_adapter.py` | 更新内部工具名、标题和调用映射 |
| `saee_backend/services/capability_http_adapter/http_request_handler.py` | 更新内部路径和操作映射 |
| `saee_backend/services/mcp_agent_run_tool_handler.py` | 更新早期内部工具处理器的机器名称 |
| `saee_backend/services/local_mcp_server.py` | 更新早期内部工具发现名称 |
| `scripts/saee_evaluate_agent_run.py` | 未来改为排演语义命令行文件名；仍委托原内部实现 |

`saee_backend/services/agent_run_capability.py` 不在允许修改范围。其模块内部函数名、算法、输入和输出保持不变。

### 4.3 当前测试和校验白名单

以下文件只允许同步内部名称和新增“公开契约不变、旧内部名不再活动发现”的断言：

- `scripts/saee_evaluate_agent_run_mcp_smoke.py`
- `scripts/saee_capability_runtime_smoke.py`
- `scripts/saee_capability_mcp_adapter_smoke.py`
- `scripts/saee_capability_http_adapter_smoke.py`
- `scripts/saee_capability_service_package_smoke.py`
- `scripts/saee_capability_alpha_release_smoke.py`
- `scripts/saee_local_mcp_prototype_smoke.py`
- `scripts/saee_canonical_capability_inventory_smoke.py`
- `scripts/saee_capability_truth_consistency_smoke.py`
- `scripts/saee_governance_registry_check.py`

如任一校验要求改变公开能力语义或回写历史快照，立即停止，不得扩大白名单。

### 4.4 当前文档与机器投影白名单

以下文件只允许同步“内部排演能力的新名称”和兼容说明：

- `docs/CAPABILITY_INVENTORY.md`
- `capability-package/README.md`
- `capability-package/limitations.md`
- `docs/architecture/SAEE_AGENT_CAPABILITY_ALPHA.md`
- `docs/architecture/SAEE_EVALUATE_AGENT_RUN_MCP_CAPABILITY.md`
- `docs/architecture/SAEE_CAPABILITY_RUNTIME_ALPHA.md`
- `docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md`
- `docs/architecture/SAEE_CAPABILITY_HTTP_ADAPTER_ALPHA.md`
- `docs/architecture/SAEE_LOCAL_MCP_PROTOTYPE.md`
- `README.md` 的当前内部能力区块，不含历史阶段记录；
- `agent-index.json` 的当前内部机器投影，不含规范公开能力对象；
- `llms.txt` 的当前内部契约索引，不含历史阶段记录；
- `governance/registry/mcp-registry.json` 的内部 MCP（模型上下文协议）入口对象。

`AGENTS.md` 的权威指针、主线和防重复建设规则没有变化，不在白名单中。

### 4.5 白名单扩张规则

```text
ALLOWLIST_EXPANSION_AUTOMATIC=false
ALLOWLIST_EXPANSION_REQUIRES_HUMAN_REVIEW=true
```

发现白名单外活动依赖时，必须停止并报告；不得以“测试需要”“文档同步”或“顺手清理”为由自动加入。

## 5. 禁止修改范围

### 5.1 永久禁改对象

- 第 3 节全部公开能力文件和公开对象；
- `saee_backend/services/agent_run_capability.py` 中的内部评估算法；
- 规范能力清单中 `saee.evaluate_agent_run`（智能体运行评估）的公开能力对象；
- 新能力、新评估器、第三套请求或响应契约；
- Goal Integrity（目标完整性）、State Integrity（状态完整性）及其研究材料。

### 5.2 历史证据禁改区

- `reports/**`（报告目录），本执行边界文件及后续获授权的实施结果报告除外；
- `release/**`（发布快照目录）；
- `phase_b_product/**`（第二阶段产品快照目录）；
- 已封存的试验观察、执行结果、收据和失败证据；
- 已有发布包、旧生态候选包和旧交付包中的历史快照；
- 既有 `commit`（提交）历史。

历史文件保留旧名称，因为它记录的是当时真实契约。禁止全局替换、批量改写或为了当前一致性重写过去。

### 5.3 外部与后果性动作禁区

- 不允许部署、发布或修改公开服务；
- 不允许访问客户数据；
- 不允许扩大权限；
- 不允许修改云市场、网站或外部仓库；
- 不允许自动执行 `git add`（Git 暂存）、`git commit`（Git 提交）或 `git push`（Git 推送）。

```text
GLOBAL_SEARCH_REPLACE_ALLOWED=false
HISTORICAL_EVIDENCE_REWRITE_ALLOWED=false
PUBLIC_CONTRACT_CHANGE_ALLOWED=false
NEW_CAPABILITY_ALLOWED=false
EXTERNAL_ACTION_ALLOWED=false
```

## 6. 工作区隔离要求

未来实施开始前必须全部满足：

1. 使用独立、干净、可删除的工作区，不在当前混合修改工作区实施；
2. 绑定一个明确的基线 `commit`（提交）标识；
3. `git status --porcelain`（Git 工作区状态输出）为空；
4. 记录实施分支或隔离工作区身份，但创建动作必须另获授权；
5. 生成第 3 节公开保护文件的实施前 SHA-256（安全哈希算法 256 位）摘要；
6. 对 `capability-package/manifest.json#canonical_inventory` 中公开能力对象生成规范化摘要；
7. 对 `governance/registry/mcp-registry.json` 中两个公开或兼容入口生成规范化摘要；
8. 生成第 4 节允许修改文件的实施前清单和摘要；
9. 记录旧内部名称的活动调用方盘点结果；
10. 绑定失败证据保存位置和非破坏性回滚点；
11. 记录一次性人工授权标识、授权所有者、精确范围和过期条件；
12. 保持无网络、无外部动作、无自动重试、无模型替换。

只要有一项不满足：

```text
EXECUTION_WORKSPACE_READY=false
IMPLEMENTATION_MUST_NOT_START=true
```

当前状态：

```text
ISOLATED_CLEAN_WORKSPACE_BOUND=false
BASELINE_COMMIT_BOUND=false
PUBLIC_PREIMAGE_HASHES_BOUND=false
ACTIVE_CALLER_INVENTORY_COMPLETE=false
ROLLBACK_POINT_BOUND=false
IMPLEMENTATION_AUTHORIZED=false
```

## 7. 回滚条件与方式

### 7.1 立即回滚条件

出现以下任一情况立即停止：

- 公开保护文件摘要变化；
- 规范公开能力对象或公开别名归属变化；
- 公开工具数量或名称变化；
- 内部评估算法、请求字段或响应字段变化；
- 需要修改白名单之外的文件；
- 发现未登记活动调用方；
- 历史证据被修改；
- 任一确定性校验失败；
- 旧内部名仍出现在活动工具发现面；
- 新内部名与既有能力发生冲突；
- 出现主线漂移或副线扩张。

### 7.2 回滚方式

1. 停止，不自动重试；
2. 保存失败差异、命令记录、校验输出和文件摘要；
3. 只撤销隔离工作区中的本次改名补丁；
4. 不触碰当前主工作区和用户既有修改；
5. 恢复到绑定的基线；
6. 复验公开保护区；
7. 输出失败报告并等待新的人工授权。

禁止使用 `git reset --hard`（Git 强制重置）或无路径范围的破坏性恢复。

```text
NO_RETRY=true
DESTRUCTIVE_ROLLBACK_ALLOWED=false
FAILED_ATTEMPT_EVIDENCE_PRESERVED=true
AUTHORIZATION_CONSUMED_AFTER_FIRST_ATTEMPT=true
```

## 8. 实施后验证项目

### 8.1 公开能力不变验证

- 第 3 节公开文件 SHA-256（安全哈希算法 256 位）摘要前后一致；
- `capability-package/manifest.json` 公开能力对象规范化摘要一致；
- `governance/registry/mcp-registry.json` 公开或兼容入口摘要一致；
- 公开工具仍然只有 `saee.evaluate_agent_run` 与 `saee.evaluate_evidence`；
- 公开请求、响应和推荐结果的确定性样例前后一致。

### 8.2 内部改名完整性验证

- 内部活动工具列表只出现 `evaluate_rehearsal_run`（排演运行评估）；
- 内部 HTTP（超文本传输协议）活动路径只使用 `/capabilities/evaluate-rehearsal-run`；
- 内部能力标识只使用 `internal.saee.evaluate_rehearsal_run`；
- 旧内部名称的剩余命中只能属于公开别名、模块内部函数或历史证据；
- 所有无法分类的旧名称命中数量为零；
- 内部输入、输出、充分性判断和原因码与实施前一致。

### 8.3 必须运行的校验

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

### 8.4 验收门

只有同时满足以下状态，才能把实施结果提交人工复核：

```text
PUBLIC_CONTRACT_UNCHANGED=true
INTERNAL_ACTIVE_SURFACE_RENAMED=true
INTERNAL_SEMANTICS_UNCHANGED=true
HISTORICAL_EVIDENCE_UNCHANGED=true
UNCLASSIFIED_OLD_NAME_REFERENCES=0
ALL_REQUIRED_VALIDATORS_PASS=true
NEW_CAPABILITY_CREATED=false
```

即使全部满足，也不自动授权暂存、提交、推送、发布或对外声明。

## 9. 指挥官命令核查与跑偏预防

```text
MAINLINE_DRIFT_DETECTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

本边界吸收前几次跑偏教训：

1. 边界计划完成不等于实施授权；
2. 最小改名不得发展成新能力、新 Schema（数据结构规范）或新 MCP（模型上下文协议）；
3. 不能因为发现更多引用就自动扩大文件白名单；
4. 不能为了当前名称一致而改写历史证据；
5. 不能在混合工作区中制造无法归因的结果；
6. 校验通过只证明对应本地边界，不代表外部可用或生产就绪；
7. 契约收敛服务证据与评估主线，不得重新开启状态完整性副线。

## 10. 非主张

本计划不表示：

- 已经修改代码、MCP（模型上下文协议）或 Schema（数据结构规范）；
- 已经执行重命名；
- 已经修改公开能力；
- 已经创建隔离工作区、分支、回滚点或摘要清单；
- 已经获得实施授权；
- 契约已经一致；
- 已经完成外部验证、客户验证、发布或生产准备。

## 11. 最终状态

```text
CAPABILITY_CONTRACT_ALIGNMENT_EXECUTION_BOUNDARY_STATUS=COMPLETE
PUBLIC_CAPABILITY_PROTECTION_DEFINED=true
INTERNAL_RENAME_ALLOWLIST_DEFINED=true
PROHIBITED_SCOPE_DEFINED=true
WORKSPACE_ISOLATION_REQUIREMENTS_DEFINED=true
ROLLBACK_CONDITIONS_DEFINED=true
POST_IMPLEMENTATION_VALIDATION_DEFINED=true
IMPLEMENTATION_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
PUBLIC_CAPABILITY_CHANGED=false
NEW_CAPABILITY_CREATED=false
ISOLATED_WORKSPACE_CREATED=false
RENAME_EXECUTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_CAPABILITY_CONTRACT_ALIGNMENT_EXECUTION_BOUNDARY
```
