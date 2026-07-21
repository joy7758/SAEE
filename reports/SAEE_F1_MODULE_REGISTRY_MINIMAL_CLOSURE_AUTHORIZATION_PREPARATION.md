# SAEE F1 模块登记最小闭环授权准备

日期：2026-07-17

## 0. 状态与结论

本文件根据 `reports/SAEE_F1_MODULE_REGISTRY_MINIMAL_CLOSURE_REVIEW.md`（SAEE F1 模块登记最小闭环审查）生成 `F1-EA-06R`（第六项收窄候选）的精确授权候选。

本文件不是授权决定，不修改 `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表）或开发宪法校验器，不建立 `F1`（基础锚点第一阶段）或 `P1`（契约父基线第一阶段）。

```text
F1_EA_06R_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
F1_EA_06R_TARGET_DEFINED=true
F1_EA_06R_AUTHORIZATION_DECISION=PENDING_HUMAN_CONFIRMATION
F1_EA_06R_AUTHORIZED=false
F1_EA_06R_IMPLEMENTED=false
F1_EA_06R_REPLACES_F1_EA_06=false
MAINLINE_DRIFT_DETECTED=false
```

## 1. 权威输入绑定

```text
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
MINIMAL_CLOSURE_REVIEW=reports/SAEE_F1_MODULE_REGISTRY_MINIMAL_CLOSURE_REVIEW.md
MINIMAL_CLOSURE_REVIEW_SHA256=986ed5563c4db78d6d108fcbeb53d44900696ffd4960ff54d740661087221b67
SOURCE_FILE=docs/product/SAEE_MODULE_REGISTRY.md
SOURCE_FILE_HEAD_SHA256=bf8b64a9d734575f50965829a1427fe86fa16bc782453d0e45328d04a654e982
SOURCE_FILE_CURRENT_SHA256=eb47a4ade538ab77c18123440c345e26e90664ff72badba5491e1348b4b241da
CONSTITUTION_CONTRACT=agent-interface/governance/saee-development-constitution.v1.1.json
CONSTITUTION_CONTRACT_SHA256=df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0
CONSTITUTION_SCHEMA=schemas/saee-development-constitution.schema.v1.1.json
CONSTITUTION_SCHEMA_SHA256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
CONSTITUTION_VALIDATOR=scripts/saee_development_constitution_smoke.py
CONSTITUTION_VALIDATOR_SHA256=8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550
```

任一输入安全散列或当前提交变化后，本准备包必须失效并重新审查。

## 2. 请求语义与规范字段对齐

### 2.1 历史源仓库与 SAEE 角色

请求中的“模块名称：`agent-evidence-layer`”按现有宪法契约收敛为：

```text
legacy_source_repository_name=agent-evidence-layer
saee_role=evidence_and_immune_subsystem
saee_display_role=SAEE Evidence and Immune Subsystem
```

中文含义：`agent-evidence-layer` 是历史源仓库标记；其在 SAEE 中的正式角色是 SAEE 证据与免疫子系统。不得把历史仓库名改写成新的 SAEE 模块名称或新能力名称。

```text
REQUESTED_MODULE_LABEL_NORMALIZED=true
NEW_MODULE_CREATED=false
NEW_CAPABILITY_CREATED=false
```

### 2.2 宪法归属状态值

请求中的：

```text
constitutional_ownership=true
```

表达的中文含义是“宪法归属成立”。现有机器契约和数据结构规范采用的规范字面值是：

```text
constitutional_ownership=implemented
```

数据结构规范在 `schemas/saee-development-constitution.schema.v1.1.json:118`（开发宪法数据结构规范第一百一十八行）把该字段定义为字符串常量 `implemented`（已落实），不是布尔值。因此精确候选必须保持规范值：

```text
REQUESTED_HUMAN_MEANING=constitutional_ownership_true
CANONICAL_TARGET_LITERAL=constitutional_ownership_implemented
SCHEMA_FIELD_TYPE_CHANGED=false
SCHEMA_FIELD_SEMANTICS_CHANGED=false
```

这不是否定人工意图，而是避免授权准备包引入新的字段类型和第二套状态语义。

## 3. 候选身份

```text
CANDIDATE_ID=F1-EA-06R
CANDIDATE_NAME=MODULE_REGISTRY_MINIMAL_CLOSURE
PROPOSED_SUCCESSOR_TO=F1-EA-06
PREDECESSOR_DECISION=REJECT_TEMPORARILY
TARGET_FILE=docs/product/SAEE_MODULE_REGISTRY.md
TARGET_SEMANTIC_CHANGE_COUNT=3
TARGET_LINE_COUNT=2
TARGET_CONTENT_SHA256=e92a20f6f9bc6de4b126d0aa024a767b8d69ce19c0b2e6f2d9dc184c2a9024ef
```

`F1-EA-06R`（第六项收窄候选）只有在新的人工决定明确批准后，才能取代上一版暂时拒绝的 `F1-EA-06`（原第六项候选）。

## 4. 精确允许目标

### 4.1 允许目标一：模块登记行中的两个字段变化

相对 `HEAD`（当前提交）第 10 行，只允许：

#### 变化一：SAEE 角色名称

```text
FROM=Evidence / Immune Subsystem
TO=SAEE Evidence and Immune Subsystem
```

中文含义：把旧的证据与免疫子系统显示名称收敛为宪法规定的 SAEE 证据与免疫子系统。

#### 变化二：历史源仓库标记

```text
FROM=agent-evidence
TO=agent-evidence-layer（历史产品名 Agent Evidence Receipt）
```

中文含义：把旧的来源标记收敛为宪法登记的历史源仓库名，并保留历史产品名。

#### 候选目标行

```markdown
| SAEE Evidence and Immune Subsystem | `agent-evidence-layer`（历史产品名 `Agent Evidence Receipt`）、ARO、当前 Evidence Adequacy | 证据充分性与回滚免疫支持 | 否 | 部分 |
```

候选行中的 ARO（历史多义缩写）、当前 Evidence Adequacy（证据充分性）、“证据充分性与回滚免疫支持”、核心状态和公开状态均为保持内容，不属于授权变化。

### 4.2 允许目标二：未迁移边界说明

只允许增加以下边界段落：

```markdown
`agent-evidence-layer` 的架构归属已由 `SAEE Development Constitution v1.1` 纳入 SAEE，但其源代码历史和仓库边界在迁移门完成前继续保留。当前只可声明 `constitutional_ownership=implemented`；不得据此声明 `source_code_migrated=true`、`runtime_integrated=true` 或新增规范 capability 已实现。
```

规范含义冻结为：

```text
constitutional_ownership=implemented
source_code_migrated=false
runtime_integrated=false
new_canonical_capability_implemented=false
```

这段文字只建立宪法归属和未迁移边界，不改变能力清单、运行时、模型上下文协议或数据结构规范。

## 5. 精确排除内容

以下对象不属于 `F1-EA-06R`（第六项收窄候选），未来授权也不得默认为允许：

### 5.1 ARO（历史多义缩写）

禁止：

- 重新定义 ARO（历史多义缩写）；
- 删除、拆分、扩写或重新归类 ARO（历史多义缩写）；
- 声称 ARO（历史多义缩写）已经成为运行观察层或证据层；
- 把 ARO（历史多义缩写）纳入此次候选的语义变化计数。

```text
ARO_TERM_CHANGED=false
ARO_TERM_SEMANTICS_AUTHORIZED=false
```

### 5.2 身份参考

禁止修改第 11 行 `Agent Identity`（智能体身份）或 `persona-object-protocol`（人格对象协议）的定位、公开状态和来源关系。

```text
IDENTITY_REFERENCE_CHANGED=false
IDENTITY_REFERENCE_INCLUDED=false
```

### 5.3 产品、商业和未来架构

禁止：

- 修改英文发现摘要；
- 修改产品生态、公开能力、商业状态或客户状态；
- 引入未来架构、可信基础设施、目标完整性或状态完整性描述；
- 修改“核心”或“公开”列；
- 修改九十九路径内部契约迁移内容；
- 修改 M03-M06（第三至第六里程碑）材料。

```text
PRODUCT_ECOSYSTEM_CHANGED=false
COMMERCIAL_STATE_CHANGED=false
FUTURE_ARCHITECTURE_CHANGED=false
NINETY_NINE_PATH_PATCH_CHANGED=false
M03_M06_CHANGED=false
```

### 5.4 当前工作树中超出最小目标的文字

当前第 10 行相对 `HEAD`（当前提交）还增加了“证据收据、完整性”定位。该增加不是开发宪法校验器的必要事实，也不在本候选允许范围内。

```text
EXPANDED_POSITIONING_TEXT_INCLUDED=false
```

## 6. 未来构造约束

即使未来人工批准 `F1-EA-06R`（第六项收窄候选），还必须另行授权构造。构造时必须：

1. 从 `HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc`（当前提交）隔离生成目标；
2. 只形成第 10 行两个语义变化和一个未迁移边界段落；
3. 逐字证明 ARO（历史多义缩写）、当前证据充分性、模块定位、核心状态和公开状态未变化；
4. 证明第 11 行身份参考和第 28 行英文发现摘要未变化；
5. 运行开发宪法校验器；
6. 不使用当前整文件复制、全局替换或递归替换；
7. 不暂存、提交或建立基线，除非另有明确授权。

```text
ISOLATED_CONSTRUCTION_REQUIRED=true
ISOLATED_CONSTRUCTION_AUTHORIZED=false
WHOLE_FILE_COPY_ALLOWED=false
GLOBAL_REPLACEMENT_ALLOWED=false
RECURSIVE_REPLACEMENT_ALLOWED=false
```

## 7. 未来验收要求

未来只有同时满足以下条件，才能把 `F1-EA-06R`（第六项收窄候选）标记为构造完成：

```text
TARGET_CONTENT_SHA256=e92a20f6f9bc6de4b126d0aa024a767b8d69ce19c0b2e6f2d9dc184c2a9024ef
VALIDATOR_TOKEN_AGENT_EVIDENCE_LAYER_PRESENT=true
VALIDATOR_TOKEN_EVIDENCE_IMMUNE_SUBSYSTEM_PRESENT=true
CANONICAL_OWNERSHIP_LITERAL_PRESERVED=true
SOURCE_CODE_MIGRATED_FALSE_PRESERVED=true
RUNTIME_INTEGRATED_FALSE_PRESERVED=true
ARO_TERM_CHANGED=false
IDENTITY_REFERENCE_CHANGED=false
PRODUCT_ECOSYSTEM_CHANGED=false
SCHEMA_CHANGED=false
MCP_CHANGED=false
```

开发宪法校验通过只证明候选满足当前宪法与表面标记要求，不自动授权基础锚点建立、提交或后续 `P1`（契约父基线第一阶段）。

## 8. 人工决定槽位

本准备包不代替人工决定。当前保持：

```text
CANDIDATE_ID=F1-EA-06R
DECISION=PENDING_HUMAN_CONFIRMATION
DECISION_MAKER=NOT_RECORDED
DECISION_REASON=NOT_RECORDED
CANDIDATE_CONTENT_APPROVED=false
SOURCE_FILE_MODIFICATION_AUTHORIZED=false
F1_CONSTRUCTION_AUTHORIZED=false
```

未来决定只能选择：

- `APPROVE`（批准）：只批准本文件的精确候选内容；
- `REJECT`（拒绝）：候选继续留在 `F1`（基础锚点第一阶段）之外。

## 9. 跑偏核查

本任务直接服务智能体证据集成主线的基础锚点闭环，没有重新打开 ARO（历史多义缩写）、身份参考、产品生态、商业状态、目标完整性、状态完整性或可信基础设施副线。

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
MAINLINE_DRIFT_DETECTED=false
SECONDARY_LANE_REOPENED=false
```

关键方法修正已经记录：历史源仓库标记不等于模块名称；“宪法归属成立”的人类含义不允许改写规范字段类型。

## 10. 最终状态

本次只新增授权准备报告。模块登记表、校验器、模型上下文协议、数据结构规范、九十九路径补丁和 M03-M06（第三至第六里程碑）材料均未修改。

```text
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_DECISION_ON_F1_EA_06R
```
