# SAEE Capability Contract Alignment（SAEE 能力契约收敛）补丁调整计划

## 1. 计划状态与任务边界

```text
TASK_ID=SAEE-CONTRACT-ALIGNMENT-PATCH-ADJUSTMENT-002
PLAN_TYPE=INTERNAL_CONTRACT_MIGRATION_MAP_ONLY
PATCH_ADJUSTMENT_PLAN_COMPLETE=true
IMPLEMENTATION_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
RENAME_EXECUTED=false
```

本文件只重新定义内部 `evaluate_agent_run`（智能体运行评估）迁移到
`evaluate_rehearsal_run`（排演运行评估）的最小完整范围，不执行第二次修改，不追认第一次隔离补丁，
也不授权合并、暂存、提交或推送。

规范公开能力 `saee.evaluate_agent_run`（智能体运行评估）必须保持完全不变。

```text
PUBLIC_CAPABILITY_CHANGED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
SCHEMA_FIELD_SEMANTICS_CHANGED=false
EVALUATION_ALGORITHM_CHANGED=false
NEW_CAPABILITY_CREATED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
```

本任务服务 SAEE（硅基放大演化生态）与 Agent Evidence Integration（智能体证据集成）主线，
没有把治理、审计或 Goal Integrity（目标完整性）副线提升为主线。

## 2. 第一次补丁教训与调整原则

第一次补丁已经证明核心内部发现面可以迁移，但没有形成完整迁移闭环：

1. 工具注册表完成改名，不等于全部活动调用方完成改名；
2. 脚本退出码为零，不等于有效案例语义成功；
3. Schema（数据结构规范）中的固定名称、模拟器发现预期、演示请求和验证断言都是契约传播面；
4. 同一旧名称可能分别代表公开别名、内部工具、模块函数或历史事实，禁止全局替换；
5. `HEAD`（当前提交指针）相同，不等于治理基线相同；隔离工作区必须包含当前宪法、治理注册表和主线材料；
6. 白名单外文件不能在实施后由审查者追认，必须在实施前单独分类和授权；
7. 历史证据保留旧名称是事实保护，不是迁移遗漏；
8. 第二次实施必须以“完整依赖图迁移”为单位，而不是以“核心文件改名”为单位。

```text
GLOBAL_SEARCH_REPLACE_ALLOWED=false
EXIT_ZERO_AS_SEMANTIC_SUCCESS_ALLOWED=false
POST_HOC_ALLOWLIST_EXPANSION_ALLOWED=false
HISTORICAL_REWRITE_ALLOWED=false
```

## 3. 内部迁移对象完整清单

### 3.1 A 类：必须迁移的活动内部对象

只有被证明承载“内部排演语义”的活动对象才进入 A 类。所有变更仅限名称、固定标识、路由和对应说明；
字段含义、评估算法、原因码和证据判断不得改变。

#### A1. 内部能力包与活动契约

- `capability-package/manifest.json`：仅内部操作对象、内部工具列表和内部来源引用；规范公开对象为同文件禁改区；
- `capability-package/mcp-tool.json`：内部工具名与现有请求、响应引用；
- `capability-package/openapi.yaml`：内部路径与操作标识；
- `capability-package/capability-card.json`：内部操作名；
- `capability-package/examples/evaluate-agent-run.json`：内部排演样例的活动操作标识；文件路径是否改名见 D 类；
- `agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json`：内部能力卡固定标识；文件路径是否改名见 D 类；
- `agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json`：内部输出固定标识，字段保持不变；文件路径是否改名见 D 类；
- `agent-interface/mcp/saee-evaluate-agent-run-mcp-capability.v0.1.json`：内部 MCP（模型上下文协议）工具卡；
- `agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json`：内部请求工具常量，字段保持不变；
- `agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json`：内部响应身份，字段保持不变；
- `agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json`：内部工具发现列表；
- `agent-interface/mcp/saee-capability-mcp-stdio-config.v0.1.json`：内部标准输入输出配置中的工具列表；
- `agent-interface/http/saee-capability-http-adapter.v0.1.json`：内部 HTTP（超文本传输协议）路径映射；
- `schemas/saee-capability-invocation-response.schema.v0.1.json`：内部操作枚举；
- `schemas/saee-capability-invocation-receipt.schema.v0.1.json`：内部操作枚举；
- `schemas/saee-capability-http-response.schema.v0.1.json`：内部操作枚举。

#### A2. 内部运行时路由与工具发现

- `saee_backend/services/capability_runtime/capability_invocation.py`；
- `saee_backend/services/capability_runtime/capability_router.py`；
- `saee_backend/services/capability_runtime/invocation_receipt.py`；
- `saee_backend/services/capability_mcp_adapter.py`；
- `saee_backend/services/capability_http_adapter/http_request_handler.py`；
- `saee_backend/services/mcp_agent_run_tool_handler.py`；
- `saee_backend/services/local_mcp_server.py`；
- `scripts/saee_evaluate_agent_run.py` 中的活动内部调用标识；文件路径是否改名见 D 类。

内部实现函数可以继续使用模块局部函数名 `evaluate_agent_run`（智能体运行评估），前提是它不进入机器发现面、
收据身份或公开契约。此次迁移针对契约身份，不强制进行无语义收益的函数重构。

#### A3. 第一次遗漏的活动演示

- `scripts/saee_capability_runtime_demo.py`；
- `scripts/saee_capability_http_demo.py`。

两个演示必须从“退出码为零”升级为语义断言：标记为有效的内部排演案例必须真实返回成功，
不得返回 `UNKNOWN`（未知）、`REJECTED`（拒绝）或 `CAPABILITY_OPERATION_UNDECLARED`（能力操作未声明）。

#### A4. 第一次遗漏的模拟器、干运行和固定发现名称

- `schemas/saee-mcp-dry-integration-trace.schema.v0.1.json`；
- `schemas/saee-synthetic-mcp-agent.schema.v0.1.json`；
- `saee_backend/services/mcp_ecosystem_discovery_simulator.py`；
- `saee_backend/services/mcp_ecosystem_dry_integration.py`；
- `saee_backend/services/mcp_result_interpretation_validator.py`；
- `saee_backend/services/first_external_validation_simulation.py`；
- `scripts/saee_mcp_ecosystem_dry_integration_smoke.py`；
- `scripts/saee_first_external_validation_simulation_smoke.py`；
- `agent-interface/mcp/mcp-dry-integration-scenarios/RELIABILITY_ASSESSMENT_TASK.json`；
- `agent-interface/ecosystem/first-validation-simulation-scenarios/02-successful-tool-invocation.json`。

这些文件只允许同步内部工具发现名称、内部调用名称和对应固定预期；不得改变案例事实或结果标签。

#### A5. 活动内部验证与测试

- `scripts/saee_agent_capability_alpha_smoke.py`；
- `scripts/saee_evaluate_agent_run_mcp_smoke.py`；
- `scripts/saee_capability_runtime_smoke.py`；
- `scripts/saee_capability_mcp_adapter_smoke.py`；
- `scripts/saee_capability_http_adapter_smoke.py`；
- `scripts/saee_capability_service_package_smoke.py`；
- `scripts/saee_capability_alpha_release_smoke.py`；
- `scripts/saee_local_mcp_prototype_smoke.py`；
- `scripts/saee_canonical_capability_inventory_smoke.py`；
- `scripts/saee_capability_truth_consistency_smoke.py`；
- `scripts/saee_governance_registry_check.py`。

测试只能同步内部预期，并增加以下反向断言：公开能力不变、旧内部工具不能再被活动发现、
历史材料中的旧名称不被误判为活动依赖。

#### A6. 活动集成样例与评估器输入

- `saee_backend/services/agent_integration_evaluator.py`；
- `saee_backend/services/ecosystem_demo_validator.py`；
- `saee_backend/services/ecosystem_entry_package_validator.py`；
- `schemas/saee-ecosystem-validation-candidate.schema.v0.1.json`；
- `agent-interface/integration/examples/correct-mcp-agent.json`；
- `agent-interface/integration/examples/authorization-confusion-agent.json`；
- `agent-interface/integration/examples/result-overinterpretation-agent.json`；
- `agent-interface/mcp/invocation-evaluation/examples/correct-mcp-agent.json`；
- `agent-interface/mcp/invocation-evaluation/examples/boundary-aware-agent.json`；
- `agent-interface/mcp/invocation-evaluation/examples/wrong-tool-selection-agent.json`；
- `agent-interface/mcp/invocation-evaluation/examples/response-overinterpretation-agent.json`；
- `agent-interface/mcp/invocation-evaluation/examples/invalid-mcp-caller.json`。

仅当这些对象明确指向内部能力包工具时才迁移；若逐项核查发现某对象指向公开
`saee.evaluate_agent_run`（智能体运行评估），立即移入 B 类并保持不变。

#### A7. 当前智能体可读说明与内部投影

- `docs/CAPABILITY_INVENTORY.md` 的当前内部能力区块；
- `capability-package/README.md`；
- `capability-package/limitations.md`；
- `docs/architecture/SAEE_AGENT_CAPABILITY_ALPHA.md`；
- `docs/architecture/SAEE_EVALUATE_AGENT_RUN_MCP_CAPABILITY.md`；
- `docs/architecture/SAEE_CAPABILITY_RUNTIME_ALPHA.md`；
- `docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md`；
- `docs/architecture/SAEE_CAPABILITY_HTTP_ADAPTER_ALPHA.md`；
- `docs/architecture/SAEE_LOCAL_MCP_PROTOTYPE.md`；
- `docs/ecosystem/SAEE_MCP_DRY_INTEGRATION_VALIDATION.md` 的当前契约说明；
- `docs/ecosystem/SAEE_FIRST_EXTERNAL_VALIDATION_SIMULATION.md` 的当前契约说明；
- `README.md` 的当前内部能力区块；
- `agent-index.json` 的当前内部机器投影；
- `llms.txt` 的当前内部契约索引；
- `governance/registry/mcp-registry.json` 的内部 MCP（模型上下文协议）对象。

同一文件中的公开能力对象、历史阶段记录和宪法指针属于禁改区。任何无法按对象级摘要隔离的文件不得修改。

### 3.2 B 类：禁止修改的公开和规范对象

以下公开能力及其行为、名称、输入、输出、工具发现、别名归属必须逐字节或对象级摘要保持不变：

- `saee_backend/services/baidu_agent_readiness_service.py`；
- `agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`；
- `agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`；
- `scripts/saee_agent_readiness_mcp_stdio.py`；
- `scripts/saee_qianfan_readiness_mcp_stdio.py`；
- `saee_backend/services/qianfan_readiness_mcp_adapter.py`；
- `scripts/saee_qianfan_readiness_host.py`；
- `saee_backend/services/marketplace_assessment_delivery.py`；
- `.mcp.json`；
- `.well-known/saee-capability-index.json`；
- `agent-interface/public/saee-public-capability-surface.v0.1.json`；
- `agent-interface/product/saee-agent-readiness-capability.v2.json`；
- `docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md`；
- `capability-package/manifest.json#canonical_inventory` 中 `capability_id=saee.evaluate_agent_run` 的完整公开对象；
- `capability-package/manifest.json` 中 `saee.agent_readiness_mcp_stdio` 与 `saee.qianfan_readiness_mcp_stdio` 的完整对象；
- `governance/registry/mcp-registry.json` 中上述两个公开或兼容 MCP（模型上下文协议）对象；
- 所有公开云入口、公开市场材料和公开工具表面中的 `saee.evaluate_agent_run`（智能体运行评估）。

公开工具面必须继续满足：

```text
PUBLIC_TOOL_COUNT=2
PUBLIC_TOOLS=saee.evaluate_agent_run;saee.evaluate_evidence
PUBLIC_ALIAS_OWNERSHIP_CHANGED=false
PUBLIC_REQUEST_SEMANTICS_CHANGED=false
PUBLIC_RESPONSE_SEMANTICS_CHANGED=false
```

### 3.3 C 类：只保留历史名称的对象

以下材料记录当时真实契约，旧名称必须原样保留：

- `reports/**` 中既有报告，本计划和未来获授权的实施报告除外；
- `release/**`；
- `phase_b_product/**`；
- `docs/pilot/results/**`；
- `agent-interface/pilot/**`；
- `agent-interface/release/saee-alpha-release-manifest.v0.1.json`；
- `agent-interface/mcp/saee-mcp-dry-integration-result.v0.1.json`；
- `agent-interface/ecosystem/saee-first-external-validation-simulation-result.v0.1.json`；
- 已封存的演示结果、收据、试验观察、失败证据和发布记录；
- 既有 `commit`（提交）历史。

历史文件允许在新的迁移报告中建立“旧名称到新名称”的解释映射，但禁止回写原文件。

```text
HISTORICAL_NAME_RETENTION_REQUIRED=true
HISTORICAL_EVIDENCE_REWRITE_ALLOWED=false
```

### 3.4 D 类：需要额外人工授权的对象

以下对象不能在第二次实施中被自动纳入，必须先给出对象语义和必要性，再获得明确授权：

#### D1. 第一次越出白名单的实现文件

- `saee_backend/services/agent_run_capability.py`；
- `saee_backend/services/capability_runtime/capability_registry_loader.py`；
- `saee_backend/services/capability_truth_consistency_validator.py`。

其中第一个文件包含内部评估实现。若固定 `capability_id`（能力标识）必须迁移，应授权“只改固定身份值”；
算法、输入、输出、原因码和判断逻辑仍为禁改区。若可由适配层完成，则恢复这三个文件的第一次补丁变化。

#### D2. 文件路径重命名

- `scripts/saee_evaluate_agent_run.py`；
- `capability-package/examples/evaluate-agent-run.json`；
- `agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json`；
- `agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json`；
- `agent-interface/mcp/saee-evaluate-agent-run-mcp-capability.v0.1.json`；
- `agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json`；
- `agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json`。

第二次补丁默认允许修改文件内容中的内部固定名称，但不默认授权路径改名。路径改名会扩大引用面和回滚面，
必须单独批准并提供旧路径兼容策略；不得借此创建第二套 Schema（数据结构规范）。

#### D3. 语义归属尚未确定的架构与外部投影

- `agent-interface/architecture/saee-agent-readiness-architecture.v1.json`；
- `docs/architecture/SAEE_AGENT_READINESS_ARCHITECTURE_V1.md`；
- `scripts/saee_agent_readiness_architecture_smoke.py`；
- `ecosystem/mcp-entry-package-v1/mcp-tools.json`；
- `ecosystem/mcp-entry-package-v1/agent-usage-guide.md`；
- `ecosystem/participant-package-v0.1/capability-reference.json`；
- `agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json`；
- `agent-interface/ecosystem/saee-volcengine-capability-mapping.v0.1.json`；
- `docs/ecosystem/SAEE_VOLCENGINE_ARK_INTEGRATION_STRATEGY.md`；
- `agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json`。

这些文件可能引用内部排演工具，也可能投影公开能力。实施前必须逐项判定：

```text
REFERENCE_CLASS=PUBLIC_OPERATION|INTERNAL_REHEARSAL_OPERATION|HISTORICAL_FACT|UNRESOLVED
```

`UNRESOLVED`（未解决）数量不为零时不得开始实施。

## 4. 第二次实施白名单定义

### 4.1 允许修改文件

未来单次实施授权的默认白名单由 A1 至 A7 构成，但须同时满足：

1. 文件位于包含当前治理基线的新隔离工作区；
2. 该文件中的每个旧名称命中已标记为内部活动契约；
3. 同文件公开对象和历史区块已建立实施前摘要；
4. 变更只涉及内部名称、固定标识、路由、发现预期和必要说明；
5. 变更后没有增加能力、字段、协议、原因码或算法分支。

### 4.2 禁止修改文件

- B 类全部文件和公开对象；
- C 类全部历史材料；
- SAEE Development Constitution（SAEE 开发宪法）及其机器契约；
- Agent Evidence Integration（智能体证据集成）的来源、许可证、交叉映射和迁移治理材料；
- `AGENTS.md`；
- Goal Integrity（目标完整性）和 State Integrity（状态完整性）研究材料；
- D 类中未获得额外授权的全部对象；
- 任何未列入白名单的文件。

### 4.3 需要额外授权文件

需要额外授权的准确清单为 D1、D2 和 D3。发现新的白名单外活动依赖时：

```text
STOP_REQUIRED=true
ALLOWLIST_EXPANSION_AUTOMATIC=false
NEW_HUMAN_AUTHORIZATION_REQUIRED=true
```

不得在实施中临时扩大范围。

## 5. 新隔离工作区基线要求

第一次隔离工作区只绑定旧提交，缺少主工作区尚未形成正式基线的当前宪法和主线材料，因此不能复用。
第二次实施前必须建立新的、干净的、可归因的隔离基线；本计划不创建该工作区。

新基线必须同时包含：

1. 当前 `SAEE Development Constitution v1.1`（SAEE 开发宪法 1.1 版）：
   - `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`；
   - `agent-interface/governance/saee-development-constitution.v1.1.json`；
   - `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md`；
2. 当前治理入口、注册表和校验器：
   - `governance/README.md`；
   - `governance/constitution/constitution-alignment.md`；
   - `governance/registry/asset-registry.json`；
   - `governance/registry/repository-registry.json`；
   - `governance/registry/capability-crosswalk.json`；
   - `governance/registry/mcp-registry.json`；
   - `governance/registry/product-registry.json`；
3. 当前规范能力清单和机器投影：
   - `capability-package/manifest.json#canonical_inventory`；
   - `agent-index.json#capability_progress_ledger_v1`；
4. 当前 Agent Evidence Integration（智能体证据集成）主线材料，包括已接受的来源、许可证、
   Schema crosswalk（数据结构规范交叉映射）、复用和迁移门；
5. 当前项目记忆与主线守卫所需文件；
6. 一个明确、可复现的基线 `commit`（提交）或经人工接受的只读基线快照。

实施前必须记录：

```text
BASELINE_ID=
BASELINE_TREE_SHA256=
CONSTITUTION_SHA256=
GOVERNANCE_REGISTRY_SHA256=
CANONICAL_INVENTORY_SHA256=
PUBLIC_PREIMAGE_RECEIPT=
ALLOWLIST_PREIMAGE_RECEIPT=
```

若当前主工作区的治理和主线材料仍未形成可归因基线，不得从混合工作区直接复制成第二次补丁。

## 6. 未来实施顺序

本节只定义顺序，不授权执行。

1. `P0_BASELINE`（基线阶段）：绑定新隔离工作区、清洁状态、基线摘要和一次性授权；
2. `P1_PUBLIC_PREIMAGE`（公开前像阶段）：保存 B 类文件和同文件公开对象摘要；
3. `P2_REFERENCE_CLASSIFICATION`（引用分类阶段）：把全部旧名称命中分类为公开、内部、历史、局部函数或未解决；
4. `P3_CORE_MIGRATION`（核心迁移阶段）：按 A1、A2 修改内部契约与路由；
5. `P4_CALLER_MIGRATION`（调用方迁移阶段）：按 A3 至 A6 修改演示、模拟器、样例和测试；
6. `P5_AGENT_READABLE_SYNC`（智能体可读同步阶段）：按 A7 同步当前说明和机器投影；
7. `P6_RESIDUAL_AUDIT`（残留审查阶段）：确认旧名称剩余命中全部可解释；
8. `P7_VALIDATION`（验证阶段）：执行第 7 节全部验证；
9. `P8_REPORT`（报告阶段）：生成实施报告并停止，等待人工补丁审查。

任一步出现白名单外依赖、公开摘要变化或未解决引用，立即停止，不进入下一步。

## 7. 迁移完成后的验证要求

### 7.1 公开能力验证

- B 类逐字节保护文件摘要前后一致；
- `capability-package/manifest.json` 中规范公开能力对象摘要一致；
- `governance/registry/mcp-registry.json` 中公开或兼容 MCP（模型上下文协议）对象摘要一致；
- 公开工具仍只有 `saee.evaluate_agent_run` 与 `saee.evaluate_evidence`；
- 公开请求、响应、结果和非授权边界保持一致；
- 千帆、公共 MCP（模型上下文协议）和云入口现有校验通过。

### 7.2 内部工具发现验证

- 当前内部能力包发现：`evaluate_rehearsal_run`、`evaluate_evidence`、`rehearse_agent`；
- 早期本地内部发现：`evaluate_rehearsal_run`、`evaluate_evidence_adequacy`；
- 旧内部 `evaluate_agent_run` 调用被拒绝；
- 新内部调用成功并返回原有评估语义；
- 活动内部能力身份仅为 `internal.saee.evaluate_rehearsal_run`。

### 7.3 MCP（模型上下文协议）发现验证

- 能力包 MCP（模型上下文协议）适配器发现列表与内部注册表一致；
- 干运行模拟器发现列表与真实适配器一致；
- 首次外部验证模拟不再出现 `MCP_DRY_ADAPTER_DISCOVERY_MISMATCH`（MCP 干运行适配器发现不匹配）；
- 公开 MCP（模型上下文协议）发现列表完全不变。

### 7.4 Schema（数据结构规范）验证

- 活动内部固定工具名、操作枚举和能力标识全部迁移；
- 字段集合、必填字段、数据类型和含义不变；
- 公开 Schema（数据结构规范）逐字节不变；
- 历史 Schema（数据结构规范）和封存结果不回写；
- 没有创建第三套 Schema（数据结构规范）。

### 7.5 演示验证

- `scripts/saee_capability_runtime_demo.py` 的有效案例真实成功；
- `scripts/saee_capability_http_demo.py` 的有效案例真实成功；
- 演示不得把 `UNKNOWN`（未知）、`REJECTED`（拒绝）或 404 状态作为成功；
- 输出仍明确内部排演评估不是授权。

### 7.6 模拟器与集成样例验证

- `scripts/saee_mcp_ecosystem_dry_integration_smoke.py` 通过；
- `scripts/saee_first_external_validation_simulation_smoke.py` 通过；
- 正确调用、错误工具选择、授权混淆和结果过度解释案例保持原标签；
- 仅工具名称变化，案例事实和评价逻辑不变。

### 7.7 残留命中分类验证

对整个仓库重新检索旧名称。每个剩余命中必须属于以下一类：

```text
PUBLIC_OPERATION_REFERENCE
HISTORICAL_FACT
MODULE_LOCAL_FUNCTION
FROZEN_FILE_PATH
```

验收条件：

```text
UNCLASSIFIED_OLD_NAME_REFERENCES=0
ACTIVE_INTERNAL_OLD_TOOL_REFERENCES=0
ACTIVE_INTERNAL_OLD_FIXED_IDENTIFIERS=0
```

### 7.8 必须通过的治理和回归校验

未来实施至少运行：

```bash
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_truth_consistency_smoke.py
python3 scripts/saee_capability_service_package_smoke.py
python3 scripts/saee_capability_runtime_smoke.py
python3 scripts/saee_capability_mcp_adapter_smoke.py
python3 scripts/saee_capability_http_adapter_smoke.py
python3 scripts/saee_mcp_ecosystem_dry_integration_smoke.py
python3 scripts/saee_first_external_validation_simulation_smoke.py
python3 scripts/saee_public_capability_surface_smoke.py
python3 scripts/saee_qianfan_readiness_mcp_smoke.py
python3 scripts/mainline_guard.py
git diff --check
```

当前阶段不运行内部重命名后的回归校验；上述命令只是未来验收清单。

## 8. 回滚策略

### 8.1 立即停止条件

出现任一情况立即停止：

- B 类公开文件或公开对象摘要变化；
- 公开工具名称、数量、输入或输出变化；
- Schema（数据结构规范）字段语义变化；
- 评估算法、原因码或证据判断变化；
- 新增能力、协议或第三套契约；
- 发现未登记活动依赖；
- D 类文件在无额外授权时发生变化；
- 历史证据或发布快照被修改；
- 任一演示仅退出码成功但语义失败；
- 任一必需校验失败；
- 主线守卫失败或 Goal Integrity（目标完整性）副线被重新开启。

### 8.2 回滚方式

1. 停止，不自动重试；
2. 保存失败差异、命令记录、摘要和校验输出；
3. 只撤销新隔离工作区中本次授权范围内的补丁；
4. 不触碰主工作区、第一次失败补丁和用户已有修改；
5. 恢复绑定的只读基线并复验公开前像；
6. 把失败尝试标记为只读证据；
7. 输出失败报告并等待新的人工授权。

禁止使用 `git reset --hard`（Git 强制重置）或无路径边界的破坏性回滚。

```text
NO_RETRY=true
DESTRUCTIVE_ROLLBACK_ALLOWED=false
FAILED_ATTEMPT_EVIDENCE_PRESERVED=true
AUTHORIZATION_CONSUMED_AFTER_FIRST_ATTEMPT=true
```

## 9. 第二次实施授权前置条件

只有全部满足，才可以请求第二次实施授权：

```text
CURRENT_GOVERNANCE_BASELINE_BOUND=true
AGENT_EVIDENCE_MAINLINE_BASELINE_BOUND=true
PUBLIC_PREIMAGE_HASHES_BOUND=true
ACTIVE_REFERENCE_CLASSIFICATION_COMPLETE=true
UNRESOLVED_REFERENCE_COUNT=0
ALLOWLIST_V2_HUMAN_ACCEPTED=true
EXTRA_AUTHORIZATION_DECISIONS_RECORDED=true
ROLLBACK_POINT_BOUND=true
IMPLEMENTATION_AUTHORIZED=true
```

本计划本身不满足最后一项，也不能自动升级授权。

## 10. 非主张

本计划不表示：

- 第二次补丁已实施；
- 第一次补丁已批准合并；
- 公开能力发生变化；
- 内部迁移已经完成；
- 新 Schema（数据结构规范）或新 MCP（模型上下文协议）已经创建；
- 任何文件路径重命名已获授权；
- SAEE（硅基放大演化生态）已外部可用、客户验证或生产就绪；
- Goal Integrity（目标完整性）或 State Integrity（状态完整性）副线已经重启。

## 11. 最终状态

```text
PATCH_ADJUSTMENT_PLAN_COMPLETE=true
IMPLEMENTATION_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
RENAME_EXECUTED=false
PUBLIC_CAPABILITY_CHANGED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
SCHEMA_FIELD_SEMANTICS_CHANGED=false
EVALUATION_ALGORITHM_CHANGED=false
NEW_CAPABILITY_CREATED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PATCH_ADJUSTMENT_PLAN
```
