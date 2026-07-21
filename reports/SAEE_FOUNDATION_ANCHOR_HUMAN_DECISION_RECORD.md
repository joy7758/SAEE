# SAEE 基础锚点人工决定记录

日期：2026-07-17

## 0. 记录性质

本文件记录 `F1`（基础锚点第一阶段）六项精确授权候选的当前人工决定状态。

六项候选的人工决定已由当前对话确认：五项批准，一项暂时拒绝。批准只确认授权准备包中对应候选内容可以作为未来 `F1`（基础锚点第一阶段）候选，不授权修改来源文件，不授权建立 `F1`（基础锚点第一阶段）或 `P1`（契约父基线第一阶段），也不授权暂存、提交或推送。

```text
FOUNDATION_ANCHOR_HUMAN_DECISION_RECORD_STATUS=FINALIZED
HUMAN_DECISION_STATUS=FINALIZED_PARTIAL_APPROVAL
DECISION_CANDIDATE_COUNT=6
PENDING_DECISION_COUNT=0
APPROVED_DECISION_COUNT=5
REJECTED_DECISION_COUNT=0
TEMPORARILY_REJECTED_DECISION_COUNT=1
HUMAN_APPROVAL_RECORDED=true
PARTIAL_EXACT_CANDIDATE_APPROVAL_RECORDED=true
ALL_EXACT_CANDIDATES_APPROVED=false
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
```

## 1. 输入绑定

```text
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
AUTHORIZATION_PACKAGE=reports/SAEE_FOUNDATION_ANCHOR_EXACT_AUTHORIZATION_PACKAGE.md
AUTHORIZATION_PACKAGE_SHA256=1cd3ac0bf7b235efa4c528976f72ecf11ce4d5e9ed4bb3dcca63a17c6e8c6af8
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
```

本记录只引用授权准备包中已经冻结的精确内容和排除内容，不重新定义授权范围。

## 2. 人工决定登记

| 候选编号 | 精确对象 | 当前对象 `SHA-256`（安全散列算法二百五十六位） | 决定 | 决定人 | 决定时间 | 决定理由 |
| --- | --- | --- | --- | --- | --- | --- |
| `F1-EA-01` | `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md:27-42`（免疫治理平面第 27-42 行） | `170f36930014500506291ae1fb21758f5da3b41dd9a227c4ad99bbab3243cfd4` | `APPROVE`（批准） | `current_conversation`（当前对话） | `2026-07-17T05:30:10+08:00` | 建立最小基础锚点，避免混入 P1（契约父基线第一阶段）迁移和架构真值对齐内容 |
| `F1-EA-02` | `.codex/current_state.md:9-11,21,31-32,46-47`（编码智能体当前状态指定段落） | `b1f798824d7aa5884734032af43025a0da822be630afeb435b826c6e2cfd6f3f` | `APPROVE`（批准） | `current_conversation`（当前对话） | `2026-07-17T05:30:10+08:00` | 建立最小基础锚点，避免混入 P1（契约父基线第一阶段）迁移和架构真值对齐内容 |
| `F1-EA-03` | `.codex/rules.md:3-12,39-46`（编码智能体规则指定段落） | `5ed8f0fd2e045e3f80b6c350a12499d5bceaf3e87cc4e0544af4b0981398420e` | `APPROVE`（批准） | `current_conversation`（当前对话） | `2026-07-17T05:30:10+08:00` | 建立最小基础锚点，避免混入 P1（契约父基线第一阶段）迁移和架构真值对齐内容 |
| `F1-EA-04` | `agent-index.json#development_constitution_v1_1`（智能体索引开发宪法对象） | `a1ff98c78b569b492501368d8983992d171532debfafa62d811160bd94de4f78` | `APPROVE`（批准） | `current_conversation`（当前对话） | `2026-07-17T05:30:10+08:00` | 建立最小基础锚点，避免混入 P1（契约父基线第一阶段）迁移和架构真值对齐内容 |
| `F1-EA-05` | `llms.txt:24-28`（大语言模型说明第 24-28 行） | `2f0fce7ef9eb350b52d8275d4c991e2cfe6101970bb3f7131c880b0b5e81d30d` | `APPROVE`（批准） | `current_conversation`（当前对话） | `2026-07-17T05:30:10+08:00` | 建立最小基础锚点，避免混入 P1（契约父基线第一阶段）迁移和架构真值对齐内容 |
| `F1-EA-06` | `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表中的候选基础事实对象） | `c4c3df5aef9a12dead75b21ab1de102e434098f6d72a59f23ecdeec062b65e9e` | `REJECT_TEMPORARILY`（暂时拒绝） | `current_conversation`（当前对话） | `2026-07-17T05:30:10+08:00` | 建立最小基础锚点，避免混入 P1（契约父基线第一阶段）迁移和架构真值对齐内容 |

表中前三项、第五项的安全散列绑定精确行内容；第四项绑定按键排序后的规范机器对象；第六项绑定授权准备包中的候选目标，而不是当前包含裸写 ARO（历史多义缩写）的原始行。

## 3. 单项状态

### 3.1 `F1-EA-01`

```text
CANDIDATE_ID=F1-EA-01
OBJECT=docs/architecture/IMMUNE_GOVERNANCE_PLANE.md:27-42
DECISION=APPROVE
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
CANDIDATE_CONTENT_APPROVED=true
SOURCE_MODIFICATION_AUTHORIZED=false
```

### 3.2 `F1-EA-02`

```text
CANDIDATE_ID=F1-EA-02
OBJECT=.codex/current_state.md:9-11,21,31-32,46-47
DECISION=APPROVE
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
CANDIDATE_CONTENT_APPROVED=true
SOURCE_MODIFICATION_AUTHORIZED=false
```

### 3.3 `F1-EA-03`

```text
CANDIDATE_ID=F1-EA-03
OBJECT=.codex/rules.md:3-12,39-46
DECISION=APPROVE
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
CANDIDATE_CONTENT_APPROVED=true
SOURCE_MODIFICATION_AUTHORIZED=false
```

### 3.4 `F1-EA-04`

```text
CANDIDATE_ID=F1-EA-04
OBJECT=agent-index.json#development_constitution_v1_1
DECISION=APPROVE
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
CANDIDATE_CONTENT_APPROVED=true
SOURCE_MODIFICATION_AUTHORIZED=false
```

### 3.5 `F1-EA-05`

```text
CANDIDATE_ID=F1-EA-05
OBJECT=llms.txt:24-28
DECISION=APPROVE
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
CANDIDATE_CONTENT_APPROVED=true
SOURCE_MODIFICATION_AUTHORIZED=false
```

### 3.6 `F1-EA-06`

```text
CANDIDATE_ID=F1-EA-06
OBJECT=docs/product/SAEE_MODULE_REGISTRY.md#confirmed_F1_facts_only
DECISION=REJECT_TEMPORARILY
DECISION_MAKER=current_conversation
DECISION_TIMESTAMP=2026-07-17T05:30:10+08:00
DECISION_REASON=建立最小基础锚点，避免混入P1迁移和架构真值对齐内容
CANDIDATE_CONTENT_APPROVED=false
SOURCE_MODIFICATION_AUTHORIZED=false
INCLUDED_IN_F1=false
REVIEW_REQUIRED_BEFORE_FUTURE_INCLUSION=true
```

第六项已暂时拒绝并继续采用失败关闭。当前第 10 行、裸写 ARO（历史多义缩写）、身份参考对齐和模块登记表整文件均不得纳入 `F1`（基础锚点第一阶段）。

## 4. 决定效力与剩余缺口

`F1-EA-01` 至 `F1-EA-05` 的批准只确认授权准备包中的精确候选内容。它们不批准整文件，也不批准来源文件修改。

`F1-EA-06` 暂时拒绝后，当前最小集合不包含模块登记表的宪法投影。由于开发宪法校验器仍读取该表面的归属事实，当前集合不能声称已经形成独立自验证的 `F1`（基础锚点第一阶段）。

```text
APPROVED_MINIMAL_CANDIDATE_COUNT=5
MODULE_REGISTRY_CANDIDATE_INCLUDED=false
F1_SELF_VALIDATING_SET_COMPLETE=false
F1_BASELINE_READY=false
```

任何单项批准都不自动授权：

- 修改来源文件；
- 建立隔离工作区；
- 构造或暂存差异；
- 建立 `F1`（基础锚点第一阶段）；
- 建立或重算 `P1`（契约父基线第一阶段）；
- 修改九十九路径补丁；
- 修改 M03-M06（第三至第六里程碑）材料。

若未来重新考虑 `F1-EA-06`，必须重新进行精确范围审查或明确接受授权准备包中的候选目标；不得把本次暂时拒绝解释成默许当前整行进入基础锚点。

## 5. 边界确认

```text
SOURCE_FILES_CHANGED=false
NINETY_NINE_PATH_PATCH_CHANGED=false
M03_M06_CHANGED=false
WHOLE_FILE_AUTHORIZATION_GRANTED=false
SOURCE_FILE_MODIFICATION_AUTHORIZED=false
F1_CONSTRUCTION_AUTHORIZED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
```

本记录没有重新打开目标完整性、状态完整性、可信基础设施或实验治理副线。

## 6. 最终状态

```text
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_FOUNDATION_ANCHOR_DECISION_FINALIZATION
```
