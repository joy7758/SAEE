# SAEE F1 模块登记最小闭环审查

日期：2026-07-17

## 0. 结论

本次审查确认：开发宪法校验器对 `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表）的直接依赖只有两个字面标记：

```text
agent-evidence-layer
SAEE Evidence and Immune Subsystem
```

校验器不读取 ARO（历史多义缩写）术语语义，不读取身份参考定位，不读取未来架构或产品生态描述，也不在该文件中直接校验未迁移字段。

但只满足两个字面标记不足以保持分阶段真值。语义安全的最小闭环还必须保留：宪法归属不等于源代码迁移、运行时集成或新增规范能力已经完成。

因此，最小闭环路径可以被定义，但本阶段不能宣布闭环已经实施：

1. 只改变模块名称和历史源仓库标记；
2. ARO（历史多义缩写）、当前证据充分性文字、模块定位、核心状态和公开状态逐字保持；
3. 只增加现有未迁移边界段落；
4. 不包含身份参考、英文发现摘要、未来架构或产品生态内容。

```text
F1_MODULE_REGISTRY_MINIMAL_CLOSURE_REVIEW_STATUS=COMPLETE
DIRECT_VALIDATOR_TOKEN_COUNT=2
SEMANTIC_MINIMUM_FACT_COUNT=3
MINIMAL_CLOSURE_CANDIDATE_DEFINED=true
MINIMAL_CLOSURE_IMPLEMENTED=false
MINIMAL_CLOSURE_AUTHORIZED=false
F1_SELF_VALIDATING_SET_CLOSURE_PATH_DEFINED=true
F1_SELF_VALIDATING_SET_COMPLETE=false
MAINLINE_DRIFT_DETECTED=false
```

## 1. 输入与快照绑定

```text
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
CONSTITUTION_VALIDATOR=scripts/saee_development_constitution_smoke.py
CONSTITUTION_VALIDATOR_SHA256=8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550
CONSTITUTION_DOCUMENT=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
CONSTITUTION_DOCUMENT_SHA256=37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c
CONSTITUTION_CONTRACT=agent-interface/governance/saee-development-constitution.v1.1.json
CONSTITUTION_CONTRACT_SHA256=df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0
MODULE_REGISTRY=docs/product/SAEE_MODULE_REGISTRY.md
MODULE_REGISTRY_HEAD_SHA256=bf8b64a9d734575f50965829a1427fe86fa16bc782453d0e45328d04a654e982
MODULE_REGISTRY_CURRENT_SHA256=eb47a4ade538ab77c18123440c345e26e90664ff72badba5491e1348b4b241da
DECISION_FINALIZATION=reports/SAEE_FOUNDATION_ANCHOR_HUMAN_DECISION_FINALIZATION.md
DECISION_FINALIZATION_SHA256=d66fff75bf7522d5a8cab890b29f2b117740b532ab86acb0bc8d640c13cbb68d
```

任一权威输入或模块登记表安全散列变化后，本审查不能直接用于未来授权。

## 2. 校验器为什么依赖模块登记表

### 2.1 代码机制

开发宪法校验器在第 56-95 行定义 `SURFACE_TOKENS`（表面标记集合）。其中模块登记表的要求是：

```python
"docs/product/SAEE_MODULE_REGISTRY.md": (
    "agent-evidence-layer",
    "SAEE Evidence and Immune Subsystem",
),
```

第 224-227 行逐个读取活动表面，并要求每个标记存在：

```python
for relative_path, tokens in SURFACE_TOKENS.items():
    text = (ROOT / relative_path).read_text(encoding="utf-8")
    for token in tokens:
        require(token in text, f"surface token missing: {relative_path}: {token}")
```

中文含义：校验器把模块登记表视为智能体可读架构投影，检查宪法中的证据项目归属是否已经出现在模块发现表面。

### 2.2 依赖目的

这项依赖不用于证明：

- 源代码已经迁移；
- 运行时已经集成；
- 证据能力已经生产就绪；
- 产品生态已经建立；
- ARO（历史多义缩写）或身份参考已经集成。

它只用于防止三种真值分叉：

1. 宪法说智能体证据项目已经归属 SAEE，但模块登记表仍把它显示成平行或旧名称模块；
2. 人类可读宪法和智能体可读发现表面不一致；
3. 后续智能体从模块登记表发现资产时，绕过当前主线与未迁移边界。

### 2.3 权威来源

开发宪法第 76-83 行定义：

- 历史源仓库名为 `agent-evidence-layer`；
- 正式角色为 `SAEE Evidence and Immune Subsystem`（SAEE 证据与免疫子系统）；
- 架构和治理归属不替代代码来源证明。

机器契约第 53-82 行进一步冻结：

```text
constitutional_ownership=implemented
source_code_adoption=not_performed
runtime_integration=not_performed
overall_classification=partial
```

因此，模块登记表是宪法的活动发现投影，不是第二个能力事实源，也不是迁移完成证明。

## 3. 直接校验最小值与语义安全最小值

### 3.1 直接校验最小值

校验器要通过模块登记表检查，只需要：

| 必要标记 | 含义 | 当前位置 |
| --- | --- | --- |
| `SAEE Evidence and Immune Subsystem` | 证据项目在 SAEE 中的正式子系统名称 | 当前第 10 行模块名称单元格 |
| `agent-evidence-layer` | 智能体证据项目的历史源仓库标记 | 当前第 10 行来源单元格 |

```text
VALIDATOR_MINIMUM_FACT_COUNT=2
VALIDATOR_REQUIRES_ARO=false
VALIDATOR_REQUIRES_IDENTITY_REFERENCE=false
VALIDATOR_REQUIRES_PRODUCT_ECOSYSTEM=false
VALIDATOR_REQUIRES_FUTURE_ARCHITECTURE=false
VALIDATOR_REQUIRES_MIGRATION_BOUNDARY_IN_MODULE_REGISTRY=false
```

### 3.2 语义安全最小值

为避免“出现两个标记”被过度解释成迁移完成，最小基础锚点还应绑定第三类事实：

```text
constitutional_ownership=implemented
source_code_migrated=false
runtime_integrated=false
new_canonical_capability_implemented=false
```

当前模块登记表第 24 行已经表达这组边界。该段落不涉及 ARO（历史多义缩写）、身份参考、未来架构或产品生态。

```text
SEMANTIC_MINIMUM_FACT_COUNT=3
MINIMUM_FACT_1=subsystem_role
MINIMUM_FACT_2=agent_evidence_constitutional_ownership
MINIMUM_FACT_3=not_migrated_boundary
```

## 4. 当前三个候选来源为什么都不能直接使用

### 4.1 只继承 `HEAD`（当前提交）版本

`HEAD`（当前提交）第 10 行为：

```markdown
| Evidence / Immune Subsystem | `agent-evidence`、ARO、当前 Evidence Adequacy | 证据充分性与回滚免疫支持 | 否 | 部分 |
```

它缺少校验器要求的两个精确标记。因此：

```text
HEAD_INHERIT_ONLY_CLOSES_VALIDATOR=false
```

### 4.2 整体采用当前工作树文件

当前工作树第 10 行同时包含必要事实、ARO（历史多义缩写）、当前证据充分性和扩展后的模块定位；第 11 行还有身份参考对象，第 28 行是英文发现与生态边界摘要。

整文件采用会违反精确范围审查和第六项暂时拒绝决定。因此：

```text
CURRENT_WHOLE_FILE_INCLUSION_ALLOWED=false
```

### 4.3 直接采用上一版 `F1-EA-06`

上一版候选试图同时处理模块行、未迁移边界和英文发现摘要，并改变 ARO（历史多义缩写）处理方式。人工决定已记录：

```text
F1-EA-06=REJECT_TEMPORARILY
```

该候选不能自动恢复，也不能被本审查视作批准。

## 5. 最小闭环候选

建议未来如需重新申请，只能建立收窄候选：

```text
CANDIDATE_ID=F1-EA-06R
CANDIDATE_ROLE=MODULE_REGISTRY_MINIMAL_CLOSURE
CANDIDATE_AUTHORIZED=false
```

### 5.1 第 10 行的允许变化

相对 `HEAD`（当前提交），只允许两个语义变化：

1. 模块名称：

```text
Evidence / Immune Subsystem
↓
SAEE Evidence and Immune Subsystem
```

2. 历史源仓库标记：

```text
agent-evidence
↓
agent-evidence-layer（历史产品名 Agent Evidence Receipt）
```

以下内容必须逐字保持 `HEAD`（当前提交）语义，不属于授权变化：

```text
ARO
当前 Evidence Adequacy
证据充分性与回滚免疫支持
核心=否
公开=部分
```

因此候选目标行只能是：

```markdown
| SAEE Evidence and Immune Subsystem | `agent-evidence-layer`（历史产品名 `Agent Evidence Receipt`）、ARO、当前 Evidence Adequacy | 证据充分性与回滚免疫支持 | 否 | 部分 |
```

这行包含 ARO（历史多义缩写）作为未变化上下文，但不授权修改、解释、拆分或扩展 ARO（历史多义缩写）。

### 5.2 未迁移边界段落

只允许加入当前第 24 行已有边界：

```markdown
`agent-evidence-layer` 的架构归属已由 `SAEE Development Constitution v1.1` 纳入 SAEE，但其源代码历史和仓库边界在迁移门完成前继续保留。当前只可声明 `constitutional_ownership=implemented`；不得据此声明 `source_code_migrated=true`、`runtime_integrated=true` 或新增规范 capability 已实现。
```

中文含义：只确认宪法归属；源代码历史和仓库边界继续保留；不得声称源代码迁移、运行时集成或新规范能力已实现。

### 5.3 候选目标摘要

```text
F1_EA_06R_TARGET_LINE_COUNT=2
F1_EA_06R_TARGET_SHA256=e92a20f6f9bc6de4b126d0aa024a767b8d69ce19c0b2e6f2d9dc184c2a9024ef
F1_EA_06R_SOURCE_FILE_MODIFICATION_REQUIRED=true
F1_EA_06R_SOURCE_FILE_MODIFICATION_AUTHORIZED=false
```

这里的两行指第 10 行候选目标和未迁移边界段落，不表示它们在最终文件中必须相邻。

## 6. 明确排除

未来候选不得包含：

- 修改、删除、解释或扩展 ARO（历史多义缩写）；
- 第 11 行身份参考定位；
- 第 28 行英文发现摘要；
- 未来架构、产品生态、公开能力或运行时描述；
- 当前第 10 行新增的“证据收据、完整性”定位扩展；
- 任何九十九路径内部契约名称；
- 任何 M03-M06（第三至第六里程碑）适配器或评估桥接器事实；
- 任何能力清单、模型上下文协议或数据结构规范变化。

```text
ARO_TERM_CHANGED=false
ARO_TERM_SEMANTICS_AUTHORIZED=false
IDENTITY_REFERENCE_INCLUDED=false
FUTURE_ARCHITECTURE_INCLUDED=false
PRODUCT_ECOSYSTEM_INCLUDED=false
```

## 7. 闭环判断

本审查解决的是“最小闭环应该长什么样”，不是“闭环已经完成”。

要把当前五项已批准候选推进为可独立自验证的候选集合，仍需要：

1. 对 `F1-EA-06R` 进行新的人工决定；
2. 明确授权构造最小差异；
3. 在隔离树中证明模块登记表只有上述两个语义变化和一个未迁移边界段落；
4. 运行开发宪法校验器并确认没有额外路径或生成物；
5. 另行决定是否授权建立 `F1`（基础锚点第一阶段）。

```text
REQUIRES_NEW_HUMAN_DECISION_FOR_F1_EA_06R=true
REQUIRES_ISOLATED_CONSTRUCTION_AUTHORIZATION=true
F1_BASELINE_READY=false
F1_BASELINE_AUTHORIZED=false
```

不得通过修改校验器、整文件暂存或把当前模块登记表视为 `HEAD`（当前提交）继承对象来绕过缺口。

## 8. 跑偏核查

本次审查直接服务智能体证据集成主线的基础锚点，不是架构真值表面对齐实施，也没有重新打开 ARO（历史多义缩写）、身份参考、目标完整性、状态完整性或可信基础设施副线。

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
MAINLINE_DRIFT_DETECTED=false
SECONDARY_LANE_REOPENED=false
```

前序教训继续适用：定向校验通过不等于基础锚点可提交；旧暂存链和旧第六项候选不能自动提供当前授权。

## 9. 未执行事项与最终状态

本次只新增审查报告。未修改模块登记表、开发宪法校验器、ARO（历史多义缩写）术语、身份参考定位或其他来源文件。

```text
MODULE_REGISTRY_CHANGED=false
CONSTITUTION_VALIDATOR_CHANGED=false
ARO_TERM_CHANGED=false
IDENTITY_REFERENCE_CHANGED=false
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_F1_MODULE_REGISTRY_MINIMAL_CLOSURE
```
