# SAEE F1 隔离构造准备

日期：2026-07-17

## 0. 结论

本文件完成 `F1`（基础锚点第一阶段）六项精确对象的隔离构造准备，但发现一个执行前阻塞：严格从 `HEAD`（当前提交）开始并只加入这六项对象时，隔离环境缺少原始六项开发宪法核心对象中的全部增量，其中五个文件在 `HEAD`（当前提交）中完全不存在。

因此：

- 六项精确对象的隔离来源、构造顺序、排除范围和验证规则已经定义；
- 六项精确对象本身不能构成完整、可运行、可独立自验证的 `F1`（基础锚点第一阶段）；
- 不得为了通过校验而自动加入未授权的开发宪法核心对象；
- 本阶段不创建隔离工作区，不构造差异，不运行隔离候选验证。

```text
F1_ISOLATED_CONSTRUCTION_PREPARATION_STATUS=COMPLETE_WITH_SCOPE_BLOCKER
APPROVED_EXACT_OBJECT_COUNT=6
EXPECTED_CHANGED_PATH_COUNT=6
SIX_OBJECT_SCOPE_SUFFICIENT_FOR_F1=false
F1_CORE_AUTHORITY_DELTA_MISSING=true
ISOLATED_CONSTRUCTION_READY=false
ISOLATED_CONSTRUCTION_AUTHORIZED=false
ISOLATED_WORKSPACE_CREATED=false
F1_SELF_VALIDATION_EXECUTABLE=false
MAINLINE_DRIFT_DETECTED=false
```

## 1. 当前请求与批准范围

当前请求把以下六项声明为已批准精确对象：

```text
F1-EA-01
F1-EA-02
F1-EA-03
F1-EA-04
F1-EA-05
F1-EA-06R
```

其中 `F1-EA-06R`（第六项收窄候选）在上一份授权准备包中仍为待人工确认；本次请求将其列入“批准范围”，因此本准备文件只记录：

```text
F1_EA_06R_EXACT_SCOPE_APPROVAL_SOURCE=current_conversation_current_request
F1_EA_06R_EXACT_SCOPE_APPROVED_FOR_PREPARATION=true
F1_EA_06R_SOURCE_MODIFICATION_AUTHORIZED=false
F1_EA_06R_CONSTRUCTION_AUTHORIZED=false
```

这项记录只允许把 `F1-EA-06R` 纳入构造方案，不修改上一份历史准备包，也不授权实际构造。

### 1.1 输入绑定

```text
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
FIVE_OBJECT_DECISION_FINALIZATION=reports/SAEE_FOUNDATION_ANCHOR_HUMAN_DECISION_FINALIZATION.md
FIVE_OBJECT_DECISION_FINALIZATION_SHA256=d66fff75bf7522d5a8cab890b29f2b117740b532ab86acb0bc8d640c13cbb68d
F1_EA_06R_AUTHORIZATION_PREPARATION=reports/SAEE_F1_MODULE_REGISTRY_MINIMAL_CLOSURE_AUTHORIZATION_PREPARATION.md
F1_EA_06R_AUTHORIZATION_PREPARATION_SHA256=bce31dd6d567ca91175025f62d52a7362dbde1db9dc4d05a9f821ed45ddacf5d
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
```

## 2. 隔离来源方案

### 2.1 唯一允许来源

未来若获得隔离构造授权，基础必须是：

```text
ISOLATION_BASE_COMMIT=f6ac41f4b068377e7778e8c3d83b99bd8382debc
ISOLATION_BASE_REF=HEAD
SOURCE_WORKTREE_DIRTY_STATE_IMPORTED=false
SOURCE_INDEX_STATE_IMPORTED=false
SOURCE_UNTRACKED_FILES_IMPORTED=false
```

不得复制当前主工作区，因为当前主工作区同时包含九十九路径补丁、M03-M06（第三至第六里程碑）、商业投影、未来研究和已废止推进链材料。

### 2.2 推荐隔离形式

推荐未来使用本地独立克隆，而不是工作树链接、符号链接或硬链接。原因：独立克隆不会把隔离候选写入主仓库的工作树登记，也不会共享工作文件。

建议路径，仅为规划，不创建：

```text
PROPOSED_ISOLATED_PATH=/Users/zhangbin/Documents/SAEE-f1-isolated-construction-001
```

未来获授权后建议执行的命令形式为：

```bash
git clone --no-hardlinks --no-checkout /Users/zhangbin/Documents/SAEE /Users/zhangbin/Documents/SAEE-f1-isolated-construction-001
git -C /Users/zhangbin/Documents/SAEE-f1-isolated-construction-001 checkout --detach f6ac41f4b068377e7778e8c3d83b99bd8382debc
```

中文说明：第一条命令创建不使用硬链接的本地独立克隆；第二条命令把隔离目录固定到指定当前提交，并保持分离提交状态。上述命令本次均未执行。

```text
LOCAL_CLONE_CREATED=false
GIT_WORKTREE_CREATED=false
SYMLINK_CREATED=false
HARDLINK_CREATED=false
NETWORK_ACCESSED=false
```

### 2.3 隔离基线检查

未来隔离目录创建后，构造前必须证明：

```text
git rev-parse HEAD = f6ac41f4b068377e7778e8c3d83b99bd8382debc
git status --short = empty
git diff --name-only = empty
git diff --cached --name-only = empty
```

中文含义：隔离目录必须位于指定提交，工作树、差异和暂存区全部为空。

## 3. 六项精确构造对象

### 3.1 基线散列和目标散列

| 候选 | 路径 | `HEAD`（当前提交）文件 `SHA-256`（安全散列算法二百五十六位） | 精确目标内容 `SHA-256` | 未来构造方式 |
| --- | --- | --- | --- | --- |
| `F1-EA-01` | `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md`（免疫治理平面） | `b3ec55a41cc4567f4d3d4493e77dbf51790178a7e2004b34e9081d7f6d1a137d` | `170f36930014500506291ae1fb21758f5da3b41dd9a227c4ad99bbab3243cfd4` | 只增加已批准的智能体证据项目归属与未迁移边界段落 |
| `F1-EA-02` | `.codex/current_state.md`（编码智能体当前状态） | `1831cdda02766e888603a8c63dd281abf9761bc71d224cfff2ebbd78fa804c69` | `b1f798824d7aa5884734032af43025a0da822be630afeb435b826c6e2cfd6f3f` | 只加入已批准的八行当前状态事实 |
| `F1-EA-03` | `.codex/rules.md`（编码智能体规则） | `7965a546693189043a50a6d025abb2ad0db5292ea62dca95f47c2280a7a2341e` | `5ed8f0fd2e045e3f80b6c350a12499d5bceaf3e87cc4e0544af4b0981398420e` | 只加入宪法权威和修改前校验顺序 |
| `F1-EA-04` | `agent-index.json`（智能体索引） | `90f870a8cb6400096052def1615c878ea03c7558aef85c23d20618e1c5b8cccc` | `a1ff98c78b569b492501368d8983992d171532debfafa62d811160bd94de4f78` | 只增加 `development_constitution_v1_1` 顶层对象；目标散列为规范对象散列 |
| `F1-EA-05` | `llms.txt`（大语言模型说明） | `bd8cdf41a0323a5585698b99c7273054dc5cc248972b0bec94da4f2f7416e6e7` | `2f0fce7ef9eb350b52d8275d4c991e2cfe6101970bb3f7131c880b0b5e81d30d` | 只增加五行开发宪法投影 |
| `F1-EA-06R` | `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表） | `bf8b64a9d734575f50965829a1427fe86fa16bc782453d0e45328d04a654e982` | `e92a20f6f9bc6de4b126d0aa024a767b8d69ce19c0b2e6f2d9dc184c2a9024ef` | 只改变两个模块登记字段并增加未迁移边界段落 |

目标内容散列绑定精确对象或精确片段，不代表构造后整个文件散列。

### 3.2 未来构造顺序

如获得实际构造授权，顺序固定为：

1. 验证隔离基线提交和六个 `HEAD`（当前提交）文件散列；
2. 构造 `F1-EA-01`、`F1-EA-02`、`F1-EA-03` 三项人类与智能体可读治理表面；
3. 向智能体索引只插入 `F1-EA-04` 规范对象；
4. 向大语言模型说明只插入 `F1-EA-05` 五行；
5. 按 `F1-EA-06R` 只构造模块登记最小闭环；
6. 逐路径比较差异；
7. 执行允许的验证；
8. 停止，等待人工审查；不暂存、不提交、不建立基线。

```text
CONSTRUCTION_ORDER_FROZEN=true
EXPECTED_CHANGED_PATH_COUNT=6
GIT_ADD_ALLOWED=false
GIT_COMMIT_ALLOWED=false
```

## 4. 精确排除范围

隔离候选不得包含：

- `P1`（契约父基线第一阶段）对象；
- 九十九路径内部契约迁移；
- M03-M06（第三至第六里程碑）材料、源代码、适配器、桥接器、校验器或测试；
- Trust Infrastructure（可信基础设施）未来研究材料；
- 商业投影、客户状态、市场投影或发布状态；
- ARO（历史多义缩写）修改、解释、拆分或扩展；
- Identity Reference（身份参考）变化；
- 目标完整性、状态完整性或多智能体治理内容；
- 当前工作树中的其他未跟踪报告；
- 主线守卫变化；
- 新能力、新模型上下文协议或新数据结构规范。

```text
P1_OBJECTS_INCLUDED=false
NINETY_NINE_PATH_PATCH_INCLUDED=false
M03_M06_INCLUDED=false
TRUST_INFRASTRUCTURE_INCLUDED=false
COMMERCIAL_PROJECTION_INCLUDED=false
ARO_EXPANSION_INCLUDED=false
IDENTITY_REFERENCE_CHANGE_INCLUDED=false
NEW_CAPABILITY_CREATED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
```

## 5. 六项范围不足的证据

### 5.1 原始宪法核心对象状态

此前基础锚点对象选择和缺口分析确认的六项核心对象为：

| 核心对象 | `HEAD`（当前提交）状态 | 是否包含在本次六项批准范围 | 结果 |
| --- | --- | --- | --- |
| `AGENTS.md`（智能体启动规则）当前宪法增量 | 文件存在，但当前宪法增量不在 `HEAD`（当前提交） | 否 | 缺少当前主线和宪法启动规则 |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`（SAEE 开发宪法第一点一版） | 不存在 | 否 | 缺少人类可读宪法权威 |
| `agent-interface/governance/saee-development-constitution.v1.1.json`（开发宪法机器契约） | 不存在 | 否 | 缺少机器契约 |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md`（开发宪法推荐门） | 不存在 | 否 | 缺少推荐门和非主张证据 |
| `schemas/saee-development-constitution.schema.v1.1.json`（开发宪法数据结构规范） | 不存在 | 否 | 缺少机器契约结构校验 |
| `scripts/saee_development_constitution_smoke.py`（开发宪法校验器） | 不存在 | 否 | 无法执行要求的开发宪法校验 |

```text
F1_CORE_AUTHORITY_OBJECT_COUNT=6
F1_CORE_AUTHORITY_OBJECTS_INCLUDED=0
F1_CORE_AUTHORITY_PATHS_ABSENT_FROM_HEAD=5
F1_CORE_AUTHORITY_DELTA_EXCLUDED_COUNT=6
```

### 5.2 直接后果

严格执行“只包含六项精确对象”后：

```text
CONSTITUTION_DOCUMENT_PRESENT=false
CONSTITUTION_CONTRACT_PRESENT=false
CONSTITUTION_SCHEMA_PRESENT=false
CONSTITUTION_RECOMMENDATION_GATE_PRESENT=false
CONSTITUTION_VALIDATOR_PRESENT=false
CONSTITUTION_VALIDATION_EXECUTABLE=false
```

因此不能把六项投影对象称为完整 `F1`（基础锚点第一阶段），也不能声称自验证完成。

## 6. 验证方案

### 6.1 隔离基线验证

未来首先验证：

- 当前提交精确匹配；
- 隔离工作区为空；
- 六个目标路径的基线散列精确匹配；
- 没有导入主工作区索引、未跟踪文件或生成物。

### 6.2 六项差异验证

未来构造后必须满足：

```text
CHANGED_PATH_COUNT=6
CHANGED_PATH_SET=
docs/architecture/IMMUNE_GOVERNANCE_PLANE.md
.codex/current_state.md
.codex/rules.md
agent-index.json
llms.txt
docs/product/SAEE_MODULE_REGISTRY.md
```

逐对象验证：

- `F1-EA-01` 至 `F1-EA-03` 的片段散列精确匹配；
- `agent-index.json`（智能体索引）可以解析，且只有 `development_constitution_v1_1` 对象相对基线新增；
- `llms.txt`（大语言模型说明）只新增五行，不包含 M03-M06（第三至第六里程碑）或 `P1`（契约父基线第一阶段）名称迁移；
- 模块登记表只包含 `F1-EA-06R` 的两个语义变化和一个未迁移边界段落；
- ARO（历史多义缩写）、身份参考、产品生态、商业状态和未来架构逐字不变；
- `git diff --check`（差异格式检查）通过。

### 6.3 治理校验

`HEAD`（当前提交）包含：

```text
scripts/saee_governance_registry_check.py
```

因此治理登记校验可以在六项候选隔离树中执行，但通过只证明治理登记一致，不补足缺失的开发宪法权威对象。

```text
GOVERNANCE_VALIDATION_EXECUTABLE=true
GOVERNANCE_VALIDATION_EXECUTED=false
```

### 6.4 能力清单校验

`HEAD`（当前提交）包含：

```text
scripts/saee_canonical_capability_inventory_smoke.py
scripts/saee_capability_progress_ledger_smoke.py
capability-package/manifest.json
```

未来可以验证六项候选没有改变规范能力事实或机器投影，但通过不代表开发宪法自验证完成。

```text
CAPABILITY_INVENTORY_VALIDATION_EXECUTABLE=true
CAPABILITY_INVENTORY_VALIDATION_EXECUTED=false
CAPABILITY_FACT_CHANGE_EXPECTED=false
```

### 6.5 开发宪法校验和 `F1` 自验证

当前六项范围下无法执行：

```text
python3 scripts/saee_development_constitution_smoke.py
```

原因不是校验失败，而是校验器及其宪法、契约、数据结构规范和推荐门不在 `HEAD`（当前提交）或本次六项范围内。

```text
CONSTITUTION_VALIDATION_EXECUTABLE=false
F1_SELF_VALIDATION_EXECUTABLE=false
F1_SELF_VALIDATION_PASS=UNPROVEN
```

不得从主工作区临时调用校验器验证隔离树，否则会把隔离候选和主工作区工具链混合，破坏可复现性。

## 7. 构造前必须解决的范围决定

未来只能由人工选择以下一种路径：

### 路径 A：授权完整基础锚点范围

把原始六项开发宪法核心对象作为独立授权对象，与当前六项精确投影对象共同构造。

```text
PROPOSED_COMPLETE_F1_DELTA_OBJECT_COUNT=12
CORE_OBJECTS_REQUIRE_NEW_AUTHORIZATION=true
PATH_A_AUTHORIZED=false
```

这条路径可以继续追求独立自验证，但不能由本准备文件自动扩张。

### 路径 B：保持六项范围并降低声明

只构造六项投影对象，把结果称为“F1 投影候选”或“基础锚点缺口补丁候选”，不称为完整 `F1`（基础锚点第一阶段），也不要求其独立运行开发宪法校验。

```text
PATH_B_RESULT_IS_COMPLETE_F1=false
PATH_B_AUTHORIZED=false
```

本文件不替人工选择路径。

```text
F1_SCOPE_DECISION_REQUIRED=true
F1_SCOPE_DECISION_RECORDED=false
NEXT_SCOPE_DECISION=AUTHORIZE_CORE_SIX_OR_DOWNCLASSIFY_SIX_OBJECT_RESULT
```

## 8. 回滚与停止条件

即使未来获得构造授权，也必须在以下情况立即停止：

- 隔离目录已经存在；
- 当前提交或输入散列变化；
- 需要第七个变化路径；
- 需要从主工作区复制整文件；
- `agent-index.json`（智能体索引）出现商业或 `P1`（契约父基线第一阶段）对象；
- `llms.txt`（大语言模型说明）出现 M03-M06（第三至第六里程碑）材料；
- 模块登记表需要修改 ARO（历史多义缩写）或身份参考；
- 验证工具写回任何跟踪文件；
- 任何步骤需要暂存、提交或推送。

失败后只保留隔离路径、输入散列、差异清单和失败原因；不得把失败候选复制回主工作区。

## 9. 跑偏核查

本任务服务智能体证据集成主线的基础历史锚点准备，没有开启 `P1`（契约父基线第一阶段）、M03-M06（第三至第六里程碑）、可信基础设施、目标完整性或状态完整性副线。

发现的问题是授权集合不完整，不是主线漂移：

```text
MAINLINE_DRIFT_DETECTED=false
AUTHORIZATION_SCOPE_INCOMPLETE=true
UNAUTHORIZED_SCOPE_EXPANSION_EXECUTED=false
```

前序教训继续适用：精确片段批准不能替代完整权威集合；定向校验通过不能自动升级为独立自验证或提交授权。

## 10. 最终状态

本次只新增隔离构造准备报告。未创建克隆、工作树、分支、隔离目录或差异，未修改主工作区来源文件。

```text
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
ISOLATED_WORKSPACE_CREATED=false
F1_CONSTRUCTION_EXECUTED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_DECISION_ON_COMPLETE_F1_SCOPE
```
