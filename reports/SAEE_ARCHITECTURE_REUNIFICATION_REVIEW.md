# SAEE Architecture Reunification（架构重新统一）只读审查

## 0. 结论

```text
ARCHITECTURE_REUNIFICATION_REVIEW_STATUS=COMPLETE
ARCHITECTURE_REUNIFICATION_CONCLUSION=ARCHITECTURE_ALIGNMENT_REQUIRED
```

结论选择 `ARCHITECTURE_ALIGNMENT_REQUIRED`（需要架构收敛）。

现有技术资产已经能够归入同一个 SAEE 主体，不需要创建第二套架构，也不需要新增能力；但当前权威表面仍存在术语与实现状态不完全一致的问题，尚不能判定为 `ARCHITECTURE_ALIGNED`（架构已经一致）。本结论要求的是后续进行有限的说明材料收敛，不授权修改代码、MCP（模型上下文协议）、Schema（数据结构规范）或能力清单。

## 1. 审查目标与边界

本次只读审查回答：POP（Persona Object Protocol，人格对象协议）、ARO（历史多义缩写）、Agent Evidence（智能体证据）、Evaluation（评估）和 MCP（模型上下文协议）如何归属于 SAEE 主体架构，以及哪些相邻项目只是实现、参考或迁移来源，不再作为独立战略主体。

本次没有：

- 修改代码、MCP（模型上下文协议）或 Schema（数据结构规范）；
- 新建能力或协议；
- 重新开启 Goal Integrity（目标完整性）或 State Integrity（状态完整性）副线；
- 把产品投影、参考仓库或历史名称升级为当前实现事实。

权威读取顺序为：开发宪法、治理入口与登记表、规范能力清单、架构与产品投影、历史报告。历史报告只提供证据和上下文，不覆盖当前规范清单。

## 2. 统一后的主体架构

SAEE 的主体与器官关系应按以下层级理解：

| 层级 | 规范归属 | 当前事实 | 不可升级的主张 |
| --- | --- | --- | --- |
| 项目主体 | SAEE（Silicon-Amplified Evolutionary Ecology，硅基放大演化生态） | 唯一总体项目主体 | 不能把证据、评估或治理投影改写成项目全部 |
| 工程核心 | Digital Biosphere Evolution Engine（数字生物圈进化引擎） | 开发宪法规定的工程核心 | 不能改写成审计优先或通用多智能体平台 |
| 身份参考 | POP（Persona Object Protocol，人格对象协议）参考仓库 | 提供人格与身份概念参考；未合并 | 不代表外部身份绑定已经实现 |
| 运行观察与排演 | SAEE 内部 Rehearsal（排演）与观察链 | 受控、本地、合成范围；内部入口为 `evaluate_rehearsal_run`（排演运行评估） | 不代表通用运行时观察层或生产运行时已经实现 |
| 证据与免疫 | SAEE Evidence and Immune Subsystem（SAEE 证据与免疫子系统） | 宪法归属已经确定；本地证据能力部分存在 | 不代表 Agent Evidence（智能体证据）源代码或运行时已经迁入 |
| 评估投影 | SAEE Evaluation（SAEE 评估） | 两项规范本地评估能力已经实现 | 不代表授权、认证、客户验证或生产就绪 |
| 生态接口 | MCP（模型上下文协议）与兼容适配器 | 规范本地标准输入输出服务已经存在 | 不代表公开网络服务或外部生态采用 |
| 客户目标投影 | SAEE Evidence（SAEE 证据）、SAEE Evaluation（SAEE 评估）、SAEE Governance（SAEE 治理） | 前两者分别为部分能力与本地实现；治理仍是未实现目标 | 目标版本不等于已经发布的产品版本 |

这套关系保持“一个主体、一个工程核心、多个器官和投影”，没有把相邻仓库重新包装成多个平行项目。

## 3. POP（人格对象协议）归属审查

### 3.1 归属结论

POP（Persona Object Protocol，人格对象协议）应归入 Agent World Identity Reference（智能体世界身份参考）层，为人格、角色和身份表达提供参考。

当前登记事实：

- `persona-object-protocol`（人格对象协议仓库）在仓库登记表中是 `reference`（参考）对象；
- 迁移动作为 `KEEP`（保留），第一阶段不进行仓库合并；
- 规范能力清单中的 `saee.external_identity_binding`（SAEE 外部身份绑定）状态仍为 `missing`（缺失）；
- 现有能力评估报告没有发现 POP（人格对象协议）或人格版本绑定已在当前能力路径实现。

因此，POP（人格对象协议）可以说明“身份从哪里获得概念与契约参考”，不能说明“SAEE 已经具备可验证外部身份绑定”。

```text
POP_OWNERSHIP_LAYER=AGENT_WORLD_IDENTITY_REFERENCE
POP_REPOSITORY_MERGED=false
POP_RUNTIME_INTEGRATED=false
EXTERNAL_IDENTITY_BINDING_IMPLEMENTED=false
```

## 4. ARO（历史多义缩写）归属审查

### 4.1 术语裁决优先

当前治理术语裁决明确：裸写 `ARO`（历史多义缩写）至少曾表示 `aro-v0.8`（历史版本名）、ARO-Audit（ARO 审计）、Audit Record Object（审计记录对象），也曾被提议解释为 Agent Runtime Object（智能体运行对象）。新 SAEE 权威文本禁止继续使用裸写 `ARO`，只允许在迁移、术语交叉映射或反向测试语境中引用。

用户同步材料中的 Agent Runtime Observation（智能体运行观察）尚未登记为当前规范组件或能力。因此，本审查不能把它静默确认为 SAEE 的正式器官。

### 4.2 当前可确认归属

- ARO-Audit（ARO 审计）是 Evidence and Immune public reference（证据与免疫公开参考），不是 SAEE Execution Object（SAEE 执行对象），也不是生产控制平面；
- `aro-v0.8`（历史版本名）等历史资产只能保留明确命名空间；
- 当前运行观察事实由 SAEE 内部排演、轨迹、证据链和有限 Trace Normalization（轨迹规范化）承载；
- 通用 OTLP（开放遥测协议）接入、可信轨迹到证据转换、外部身份绑定和委托绑定仍未实现。

`docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表）仍使用裸写 `ARO`，与已经批准的术语裁决不一致。这是本次不能选择 `ARCHITECTURE_ALIGNED`（架构已经一致）的直接证据之一。

```text
BARE_ARO_CANONICAL=false
ARO_AUDIT_ROLE=EVIDENCE_AND_IMMUNE_REFERENCE
AGENT_RUNTIME_OBSERVATION_REGISTERED=false
GENERAL_RUNTIME_OBSERVATION_IMPLEMENTED=false
```

## 5. Agent Evidence（智能体证据）归属审查

### 5.1 宪法归属与迁移事实必须分开

Agent Evidence Project（智能体证据项目）在宪法上已经归入 SAEE Evidence and Immune Subsystem（SAEE 证据与免疫子系统）。该归属解决“属于哪个系统”，没有解决“代码和运行时是否已经迁入”。

当前事实：

- `agent-evidence-layer`（智能体证据层仓库）是外部子系统源与迁移来源，状态为 `MIGRATE`（迁移），尚未合并；
- `agent-evidence`（智能体证据参考仓库）是独立发布与引用身份，状态为 `KEEP`（保留）；
- SAEE Evidence（SAEE 证据）产品登记状态为 `partial`（部分）；
- `source_code_migrated=false`（源代码未迁移）；
- `runtime_integrated=false`（运行时未集成）；
- 当前工作区存在净室适配与评估桥接材料，但尚不能把未进入规范能力清单和正式版本历史的材料升级为完成集成。

```text
AGENT_EVIDENCE_CONSTITUTIONAL_OWNERSHIP=implemented
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
AGENT_EVIDENCE_INTEGRATION_COMPLETED=false
```

## 6. Evaluation（评估）核心入口审查

### 6.1 规范公开契约

当前规范评估入口只有：

- `saee.evaluate_agent_run`（智能体运行评估）；
- `saee.evaluate_evidence`（证据评估）。

两者均为 `implemented`（已实现）的本地确定性评估能力。前者评估声明的轨迹元数据和必需证据覆盖，后者评估封闭证据包相对于明确要求的覆盖情况。

它们不能证明：

- 声明轨迹已经通过外部认证；
- 现实事件一定发生；
- 可以部署或执行重大动作；
- 已完成客户验证或达到生产就绪。

### 6.2 内部排演契约

内部能力包使用 `evaluate_rehearsal_run`（排演运行评估），与公开 `saee.evaluate_agent_run`（智能体运行评估）已经完成名称分离。内部 `rehearse_agent`（排演智能体）仍是 `design_only`（仅设计）契约，不得升级为已实现公开能力。

因此，Evaluation（评估）入口本身已经对齐，不需要在本次架构统一中改名、增能或重设计。

```text
EVALUATION_PUBLIC_ENTRY_ALIGNED=true
EVALUATION_INTERNAL_ENTRY_ALIGNED=true
EVALUATION_AUTHORIZATION_CONTROL=false
```

## 7. MCP（模型上下文协议）生态入口审查

规范 MCP（模型上下文协议）表面是 `saee.agent_readiness_mcp_stdio`（SAEE 智能体就绪标准输入输出服务），本地公开契约只暴露两项规范评估能力。

其他表面必须保持分层：

- `saee.qianfan_readiness_mcp_stdio`（SAEE 千帆就绪标准输入输出服务）是兼容适配器，不是第二个规范入口；
- `saee.capability_package_mcp_stdio`（SAEE 能力包标准输入输出服务）是内部表面，使用内部排演名称；
- `saee.legacy_observed_trace_mcp_stdio`（SAEE 历史观察轨迹标准输入输出服务）是历史内部表面；
- Agent Evidence Receipt MCP（智能体证据收据模型上下文协议）仍属于独立外部产品表面，不能冒充 SAEE 规范入口。

当前 MCP（模型上下文协议）只达到本地规范契约状态，没有建立公开网络服务、客户验证或生产就绪。

```text
MCP_CANONICAL_SURFACE=saee.agent_readiness_mcp_stdio
MCP_CANONICAL_TOOL_COUNT=2
PUBLIC_NETWORK_MCP_DEPLOYED=false
MCP_ECOSYSTEM_ADOPTION_PROVEN=false
```

## 8. 不再作为独立战略主体的项目与资产

下列对象可以继续保留自己的来源、许可证、发布或引用身份，但在 SAEE 总体叙事中只表示实现、参考、迁移来源或生态投影：

| 对象 | 当前角色 | 不应再承担的角色 |
| --- | --- | --- |
| `agent-evidence-layer`（智能体证据层仓库） | Agent Evidence（智能体证据）的外部源与迁移来源 | 不应成为 SAEE 之外的第四个目标客户版本 |
| `agent-evidence`（智能体证据参考仓库） | 公开证据参考实现和独立引用身份 | 不应被描述为已经迁入的 SAEE 运行时 |
| `persona-object-protocol`（人格对象协议仓库） | 身份与人格契约参考 | 不应被描述为已实现的 SAEE 外部身份层 |
| ARO-Audit（ARO 审计）及历史 ARO（历史多义缩写）资产 | 证据、收据或审计格式参考 | 不应成为 SAEE 执行对象、运行时或独立战略主体 |
| Capability Package（能力包）、Rehearsal Runtime（排演运行时）与本地适配器 | SAEE 内部实现组件 | 不应升级为新的产品族或平行架构 |
| 千帆兼容封装、网站、云市场材料 | 兼容、分发或事实投影 | 不应成为能力事实和架构权威来源 |
| Digital Biosphere Architecture（数字生物圈架构）参考仓库 | 架构和词汇参考 | 不应被解释为已经并入的可运行源代码树 |

“不再作为独立战略主体”不等于删除仓库、抹除历史或取消独立许可证；它只限制 SAEE 当前主体架构中的叙事和权威关系。

## 9. 对齐缺口

### 9.1 必须收敛的说明表面

1. **ARO（历史多义缩写）术语冲突**：模块登记表仍裸写 `ARO`，违反已批准的术语裁决；必须在未来单独授权的说明材料变更中改为明确命名空间或具体来源。
2. **POP（人格对象协议）实现状态易被高估**：模块登记表把 Agent Identity（智能体身份）列为“是”，但规范能力清单显示外部身份绑定缺失；未来说明表面必须明确“参考存在”与“集成实现”是两种状态。
3. **Agent Evidence（智能体证据）归属易被误读为迁移完成**：宪法归属已经成立，但源代码和运行时迁移均未完成；所有架构图和产品说明必须继续同时显示这两个否定状态。

### 9.2 已经对齐、不得重复改造的部分

1. 公开 `saee.evaluate_agent_run`（智能体运行评估）和内部 `evaluate_rehearsal_run`（排演运行评估）已经分离；
2. 规范 MCP（模型上下文协议）表面和内部能力包表面已经分层；
3. SAEE Evidence（SAEE 证据）、SAEE Evaluation（SAEE 评估）、SAEE Governance（SAEE 治理）是固定目标投影，不应再创建第四套客户版本；
4. Goal Integrity（目标完整性）与 State Integrity（状态完整性）继续保持研究副线停止状态。

## 10. 指挥官命令核查与跑偏教训

```text
MAINLINE_DRIFT_DETECTED=false
```

本次命令要求只读归属审查，并明确禁止新增能力及重新开启研究副线，符合当前 `saee_agent_evidence_integration`（SAEE 智能体证据集成）主线。

需要继续保留的跑偏教训：

1. **归属不等于迁移**：相邻仓库属于 SAEE 子系统，不代表其代码、运行时或市场入口已经并入。
2. **参考不等于实现**：POP（人格对象协议）或 ARO-Audit（ARO 审计）仓库存在，不代表 SAEE 已实现身份绑定或通用运行观察。
3. **产品投影不等于项目核心**：Agent Readiness（智能体就绪）、Evidence（证据）和 Evaluation（评估）可以成为交付投影，但不能替代数字生物圈进化引擎的工程核心。
4. **接口不等于生态采用**：本地 MCP（模型上下文协议）可调用，不等于已经公开部署或被外部智能体生态采用。
5. **研究方向不等于当前能力**：Goal Integrity（目标完整性）、State Integrity（状态完整性）和 Temporal Trust Continuity（时间可信连续性）不能从愿景直接写入当前实现事实。
6. **统一不等于造平台**：本次统一只解决权威归属和语义边界，不授权新架构、新运行时或新治理层。

## 11. 最小后续动作建议

如人工接受本审查，下一步只应准备一次 Architecture Truth Surface Alignment（架构真值表面对齐）人工审查，限定于：

- 消除权威说明表面中的裸写 `ARO`；
- 把 POP（人格对象协议）明确为身份参考而非已实现绑定；
- 在 Agent Evidence（智能体证据）归属说明旁持续保留源代码未迁移、运行时未集成状态。

该建议不授权修改，且不应触碰评估算法、MCP（模型上下文协议）、Schema（数据结构规范）、规范能力清单或历史证据。

## 12. 非主张

本报告不证明：

- SAEE 已成为 Trust Infrastructure（可信基础设施）；
- POP（人格对象协议）已经集成；
- Agent Runtime Observation（智能体运行观察）已经成为规范组件；
- Agent Evidence（智能体证据）源代码或运行时已经迁入；
- MCP（模型上下文协议）已经公开部署；
- SAEE 已完成客户验证、商业验证或生产就绪；
- Goal Integrity（目标完整性）或 State Integrity（状态完整性）能力已经实现。

## 13. 最终状态

```text
ARCHITECTURE_REUNIFICATION_REVIEW_STATUS=COMPLETE
ARCHITECTURE_REUNIFICATION_CONCLUSION=ARCHITECTURE_ALIGNMENT_REQUIRED
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
SAEE_UMBRELLA_SUBJECT=true
ENGINEERING_CORE=DIGITAL_BIOSPHERE_EVOLUTION_ENGINE
POP_ROLE=IDENTITY_REFERENCE_NOT_INTEGRATED
BARE_ARO_CANONICAL=false
AGENT_RUNTIME_OBSERVATION_REGISTERED=false
AGENT_EVIDENCE_CONSTITUTIONAL_OWNERSHIP=implemented
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
EVALUATION_CANONICAL_ENTRY=saee.evaluate_agent_run;saee.evaluate_evidence
MCP_CANONICAL_SURFACE=saee.agent_readiness_mcp_stdio
PUBLIC_NETWORK_MCP_DEPLOYED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CHANGED=false
MCP_CHANGED=false
CODE_CHANGED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_ARCHITECTURE_ALIGNMENT_GAPS
```
