# SAEE Architecture Truth Surface Alignment（架构真值表面对齐）只读实施计划

## 0. 计划结论

本计划定义未来说明材料如何准确反映当前 SAEE 架构状态。它不是实施授权，不修改任何现有真值表面。

```text
ARCHITECTURE_TRUTH_SURFACE_ALIGNMENT_PLAN_STATUS=COMPLETE
ARCHITECTURE_ALIGNMENT_IMPLEMENTATION_AUTHORIZED=false
```

当前所需工作是有限的文档与智能体可读投影收敛，不是新架构、新能力或仓库合并。对齐必须保持：

1. 禁止裸写 `ARO`（历史多义缩写）；
2. POP（Persona Object Protocol，人格对象协议）只表示 Identity Reference（身份参考）；
3. Agent Evidence（智能体证据）的宪法归属、源代码迁移和运行时集成必须作为三个独立真值维度；
4. 历史证据与发布记录保持原样。

## 1. 目标、依据与严格边界

### 1.1 目标

在不改变实现事实的前提下，建立可供未来说明材料复用的术语规则、状态表达、修改范围和验收标准，使人类与智能体不会把“参考”误读为“实现”，也不会把“宪法归属”误读为“迁移完成”。

### 1.2 当前事实依据

本计划按以下权威顺序读取事实：

1. SAEE Development Constitution v1.1（SAEE 开发宪法第一点一版）；
2. 治理术语交叉映射与当前治理登记表；
3. `capability-package/manifest.json#canonical_inventory`（规范能力清单）；
4. 当前架构、产品和智能体可读投影；
5. 历史报告与发布记录，仅作历史证据，不反向覆盖当前事实。

直接前置结论来自 `reports/SAEE_ARCHITECTURE_REUNIFICATION_REVIEW.md`（SAEE 架构重新统一审查报告）：

```text
ARCHITECTURE_REUNIFICATION_CONCLUSION=ARCHITECTURE_ALIGNMENT_REQUIRED
```

### 1.3 禁止范围

本计划及其未来有限实施均不得自动触碰：

- 代码和评估算法；
- MCP（模型上下文协议）工具、发现信息或公开入口；
- Schema（数据结构规范）及其字段语义；
- 规范能力清单与能力数量；
- 历史报告、发布快照、既有证据和已发布仓库历史；
- 仓库合并、源代码迁移或运行时迁移；
- Goal Integrity（目标完整性）与 State Integrity（状态完整性）研究副线。

## 2. 真值表面分级规则

未来对齐前，所有命中对象必须先归入以下一种类型：

| 类型 | 示例 | 处理原则 |
| --- | --- | --- |
| 规范权威 | 开发宪法、治理术语裁决、规范能力清单、治理登记表 | 默认只读；本次不修改 |
| 活动说明表面 | 当前架构文档、产品文档、模块登记表 | 发现与权威事实冲突时，可进入未来精确白名单 |
| 智能体可读投影 | `agent-index.json`（智能体索引）、`agent-readable.md`（智能体可读说明）、`llms.txt`（大语言模型说明）、产品生态映射 | 只有现有字段足以准确表达时才允许同步；不得借机新增 Schema（数据结构规范）字段 |
| 公开投影 | 网站、云市场、公开能力说明 | 必须与规范事实一致，但需要独立公开面授权；不能由本计划自动修改 |
| 历史证据 | 历史报告、发布记录、封存材料、既有实验输出 | 保持原样，不用当前术语回写历史 |

### 2.1 权威优先规则

出现冲突时必须遵循：

```text
CONSTITUTION_AND_APPROVED_TERM_DECISIONS
>
CANONICAL_INVENTORY_AND_GOVERNANCE_REGISTRIES
>
ACTIVE_ARCHITECTURE_AND_PRODUCT_DOCUMENTS
>
AGENT_READABLE_AND_PUBLIC_PROJECTIONS
>
HISTORICAL_RECORDS
```

即：开发宪法与已批准术语裁决优先于规范能力清单和治理登记；活动说明与投影必须向权威事实收敛；历史记录保持其发生时的原文和语境。

## 3. ARO（历史多义缩写）术语收敛规则

### 3.1 禁止规则

未来活动说明和智能体可读投影禁止把裸写 `ARO` 用作：

- SAEE 模块名；
- 能力名；
- 运行观察层简称；
- 证据层简称；
- 身份、执行或治理对象名称。

允许出现 `ARO` 字符的情形仅限：

1. 完整历史专名 ARO-Audit（ARO 审计）；
2. 迁移或术语交叉映射文件中解释历史歧义；
3. 反向校验中明确检测禁止用法；
4. 不可修改的历史证据原文。

### 3.2 三个对象的明确边界

#### ARO-Audit（ARO 审计）

标准表达：

> ARO-Audit（ARO 审计）是外部 Receipt and Audit Format Reference（收据与审计格式参考），归入证据与免疫参考资产；它不是 SAEE 执行对象、生产控制平面或通用运行时。

固定状态：

```text
ARO_AUDIT_ROLE=EVIDENCE_AND_IMMUNE_REFERENCE
ARO_AUDIT_RUNTIME_INTEGRATED=false
ARO_AUDIT_EXECUTION_CONTROL=false
```

#### Runtime Observation（运行观察）

标准表达：

> Runtime Observation（运行观察）描述 SAEE 内部排演、轨迹和有限规范化过程中产生可观察运行事实的功能，不是名为 `ARO` 的规范组件，也不代表通用生产运行时观察已经实现。

固定状态：

```text
RUNTIME_OBSERVATION_ROLE=BOUNDED_FUNCTIONAL_CONCERN
AGENT_RUNTIME_OBSERVATION_REGISTERED=false
GENERAL_RUNTIME_OBSERVATION_IMPLEMENTED=false
```

#### Evidence Layer（证据层）

标准表达：

> Evidence Layer（证据层）属于 SAEE Evidence and Immune Subsystem（SAEE 证据与免疫子系统），接收受控来源的声明、轨迹候选和证据对象，并支持充分性评估；它不等于 ARO-Audit（ARO 审计），也不把任意运行轨迹自动提升为可信证据。

固定状态：

```text
EVIDENCE_LAYER_OWNER=SAEE_EVIDENCE_AND_IMMUNE_SUBSYSTEM
TRACE_AUTOMATICALLY_TRUSTED_EVIDENCE=false
```

### 3.3 不得建立的错误等式

```text
ARO_AUDIT != RUNTIME_OBSERVATION
RUNTIME_OBSERVATION != EVIDENCE_LAYER
ARO_AUDIT != EVIDENCE_LAYER
TRACE != TRUSTED_EVIDENCE
```

## 4. POP（人格对象协议）状态说明规则

### 4.1 规范定位

POP（Persona Object Protocol，人格对象协议）的当前规范定位只能是 Identity Reference（身份参考）。它为人格、角色和身份表达提供外部参考，不表示 SAEE 已经完成身份绑定实现。

标准表达：

> `persona-object-protocol`（人格对象协议仓库）是 Persona and Identity Contract Reference（人格与身份契约参考）。仓库保持独立，未合并到 SAEE；SAEE 的外部身份绑定能力仍未实现。

固定状态：

```text
POP_ROLE=IDENTITY_REFERENCE
POP_REPOSITORY_MERGED=false
POP_RUNTIME_INTEGRATED=false
IDENTITY_BINDING_IMPLEMENTATION=false
EXTERNAL_IDENTITY_BINDING_STATUS=missing
```

### 4.2 禁止表达

除非未来规范能力清单先发生经过授权和验证的状态变化，否则不得单独写：

- POP Identity Layer Implemented（POP 身份层已经实现）；
- Agent Identity Module Implemented（智能体身份模块已经实现）；
- Verifiable Agent Identity Available（可验证智能体身份已经可用）；
- POP Integrated（POP 已经集成）。

### 4.3 发现性与实现性的分离

`public=true`（存在公开仓库）只说明参考资产可被发现，不说明：

- 代码已经迁移；
- 运行时已经集成；
- 身份声明已被认证；
- SAEE 已能验证调用者身份。

因此，任何以“公开”为依据的模块映射都必须同时显示 `role=identity_reference`（角色为身份参考）或同义中文说明。

## 5. Agent Evidence（智能体证据）状态说明规则

### 5.1 三轴真值模型

所有当前说明必须同时区分以下三个轴：

| 真值轴 | 当前状态 | 含义 |
| --- | --- | --- |
| 宪法归属 | `constitutional_ownership=implemented` | Agent Evidence Project（智能体证据项目）正式归属于 SAEE 证据与免疫子系统 |
| 源代码迁移 | `source_code_migrated=false` | 外部源代码尚未迁入 SAEE 规范源树 |
| 运行时集成 | `runtime_integrated=false` | 外部运行时、服务和市场入口尚未成为 SAEE 统一运行时 |

三项状态必须并列出现。禁止只写“已归入 SAEE”而省略后两项否定状态。

### 5.2 规范说明模板

> Agent Evidence Project（智能体证据项目）已在宪法上归入 SAEE Evidence and Immune Subsystem（SAEE 证据与免疫子系统）。该归属不表示源代码迁移或运行时集成已经完成；当前仍保持 `source_code_migrated=false` 和 `runtime_integrated=false`。

### 5.3 适配材料边界

当前净室适配器、兼容映射或评估桥接材料只能按各自规范登记状态陈述。它们的存在不能自动改变：

```text
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
AGENT_EVIDENCE_INTEGRATION_COMPLETED=false
```

## 6. 未来说明材料的最小范围

### 6.1 必须进入精确白名单准备的对象

| 路径 | 当前问题 | 未来允许的最小修正 |
| --- | --- | --- |
| `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表） | 证据与免疫子系统来源中裸写 `ARO`；身份参考行可能被“公开=是”误读为已实现 | 使用 ARO-Audit（ARO 审计）完整历史专名并分开说明 Runtime Observation（运行观察）；把 POP（人格对象协议）明确标注为身份参考而非身份绑定实现 |

### 6.2 条件白名单候选

以下对象只有在逐对象审查确认其当前措辞违反本计划模板后，才能申请单独授权：

| 路径 | 审查重点 |
| --- | --- |
| `docs/product/SAEE_GITHUB_ASSET_CONSOLIDATION_MAP.md`（SAEE 代码托管资产整合地图） | `Agent Identity Module`（智能体身份模块）是否会被误读为已实现模块；ARO-Audit（ARO 审计）是否保持参考定位 |
| `agent-interface/product/saee-product-ecosystem-map.v1.0.json`（SAEE 产品生态映射） | 现有 `role=persona_and_agent_identity_reference` 已正确，但展示名称是否需要与参考状态一致；不得新增字段 |
| `README.md`（项目说明）、`agent-readable.md`（智能体可读说明）、`agent-index.json`（智能体索引）、`llms.txt`（大语言模型说明） | 只核对三轴状态是否完整；当前正确表面不得为了措辞统一重复修改 |

### 6.3 明确禁止修改的对象

- `docs/release/`（发布说明目录）中的历史真值记录；
- `reports/`（报告目录）中本计划之前产生的历史审查与实验材料；
- 已发布仓库、归档、DOI（数字对象标识符）记录和发布快照；
- `capability-package/manifest.json`（能力包清单）；
- 治理登记表和开发宪法，除非未来发现其自身与已批准权威发生矛盾并另行授权；
- 所有代码、MCP（模型上下文协议）和 Schema（数据结构规范）文件。

## 7. 未来实施顺序与人工闸门

本计划完成后不得直接修改。未来如继续，只允许按以下顺序推进：

1. 生成精确命中登记：记录路径、行、对象角色、当前表述、权威依据和拟修改表述；
2. 将命中对象分类为 `ALIGN_ACTIVE_SURFACE`（对齐活动表面）、`KEEP_CURRENT`（保持当前）或 `KEEP_AS_HISTORY`（保持历史）；
3. 冻结逐对象白名单和禁止清单；
4. 由人工明确授权文档级对齐；
5. 只修改已授权对象，不做递归替换或全局重写；
6. 校验权威、活动说明、智能体可读投影和公开投影的一致性；
7. 完成人工补丁审查后停止，不自动进入提交、合并、推送或发布。

```text
ALIGNMENT_IMPLEMENTATION_REQUIRES_HUMAN_AUTHORIZATION=true
AUTOMATIC_ALLOWLIST_EXPANSION=false
RECURSIVE_REPLACEMENT_ALLOWED=false
```

## 8. 未来验收规则

未来有限实施必须同时证明：

### 8.1 术语验收

- 活动说明与智能体可读投影中不存在作为组件名使用的裸写 `ARO`；
- ARO-Audit（ARO 审计）、Runtime Observation（运行观察）和 Evidence Layer（证据层）没有互相替代；
- 历史材料中的旧术语没有被回写。

### 8.2 状态验收

- POP（人格对象协议）始终被标为 Identity Reference（身份参考）；
- `saee.external_identity_binding`（SAEE 外部身份绑定）仍为 `missing`（缺失）；
- Agent Evidence（智能体证据）三轴状态并列且保持当前值。

### 8.3 范围验收

```text
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
CANONICAL_CAPABILITY_INVENTORY_CHANGED=false
HISTORICAL_EVIDENCE_CHANGED=false
REPOSITORY_MERGED=false
RUNTIME_MIGRATED=false
NEW_CAPABILITY_CREATED=false
```

### 8.4 一致性验收

未来实施至少运行：

- 开发宪法校验；
- 治理登记校验；
- 规范能力清单校验；
- 能力进度台账校验；
- 精确术语扫描；
- `git diff --check`（差异格式检查）。

如任何校验要求修改禁止范围，必须停止并返回人工审查，不得扩大白名单。

## 9. 回滚与停止条件

未来实施出现下列任一情况必须回滚本次文档补丁并停止：

1. 需要修改代码、MCP（模型上下文协议）、Schema（数据结构规范）或规范能力清单才能完成措辞对齐；
2. 需要回写历史报告或发布记录；
3. 把 ARO-Audit（ARO 审计）升级为运行时或执行对象；
4. 把 POP（人格对象协议）升级为已实现身份绑定；
5. 把 Agent Evidence（智能体证据）的宪法归属升级为迁移完成；
6. 重新开启 Goal Integrity（目标完整性）或 State Integrity（状态完整性）副线；
7. 说明材料对齐开始形成新的治理系统、术语体系或产品架构。

## 10. 指挥官命令核查与跑偏防护

```text
MAINLINE_DRIFT_DETECTED=false
```

本任务服务于 `saee_agent_evidence_integration`（SAEE 智能体证据集成）主线：它修复智能体发现与理解所依赖的真值表面，不新增副线能力。

必须吸收前序跑偏教训：

1. 不能把“说明材料需要对齐”扩展为新架构设计；
2. 不能把相邻仓库存在扩展为集成已经完成；
3. 不能把身份参考扩展为身份认证；
4. 不能把运行观察扩展为 State Engine（状态引擎）；
5. 不能为了消除当前术语差异而修改历史事实；
6. 完成一次有限真值表面对齐后必须回到 Agent Evidence Integration（智能体证据集成）主线，不再追加治理层。

## 11. 非主张

本计划不证明：

- ARO-Audit（ARO 审计）已经集成；
- 通用 Runtime Observation（运行观察）已经实现；
- POP（人格对象协议）已经实现身份绑定；
- Agent Evidence（智能体证据）源代码或运行时已经迁入；
- SAEE 已实现可信基础设施、目标完整性或状态完整性；
- 本计划已经获得实施、提交、合并、推送或发布授权。

## 12. 最终状态

```text
ARCHITECTURE_TRUTH_SURFACE_ALIGNMENT_PLAN_STATUS=COMPLETE
ARCHITECTURE_ALIGNMENT_IMPLEMENTATION_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
BARE_ARO_ALLOWED_ON_ACTIVE_SURFACES=false
ARO_AUDIT_ROLE=EVIDENCE_AND_IMMUNE_REFERENCE
AGENT_RUNTIME_OBSERVATION_REGISTERED=false
POP_ROLE=IDENTITY_REFERENCE
IDENTITY_BINDING_IMPLEMENTATION=false
AGENT_EVIDENCE_CONSTITUTIONAL_OWNERSHIP=implemented
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
NEW_CAPABILITY_CREATED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
HISTORICAL_EVIDENCE_CHANGED=false
REPOSITORY_MERGED=false
RUNTIME_MIGRATED=false
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_ARCHITECTURE_TRUTH_SURFACE_ALIGNMENT_PLAN
```
