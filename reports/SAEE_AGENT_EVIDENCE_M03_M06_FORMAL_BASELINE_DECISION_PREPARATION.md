# SAEE Agent Evidence Integration（智能体证据集成）M03-M06 正式基线决策准备

## 0. 决策准备结论

本报告只记录正式基线选择前的建议处置和前置条件，不构成正式基线授权，不允许执行暂存、提交、推送、合并、迁移或运行时集成。

```text
FORMAL_BASELINE_DECISION_PREPARATION_STATUS=COMPLETE
A_CLASS_DECISION=ACCEPT_AS_FORMAL_BASELINE_CANDIDATES
A_CLASS_OBJECT_COUNT=21
B_CLASS_DECISION=KEEP_AS_EVIDENCE_REPORTS
B_CLASS_OBJECT_COUNT=3
D_CLASS_DECISION=REQUIRES_FUTURE_SCOPE_DECISION
D_CLASS_OBJECT_COUNT=3
FORMAL_BASELINE_AUTHORIZED=false
```

人话结论：

1. A 类二十一项可以进入正式基线候选集合，但“成为候选”不等于“已经允许暂存”。
2. B 类三项继续保持证据报告身份，可以陪同基线提供阶段证据，但不能成为能力契约、实现或规范事实源。
3. D 类三项的 M-07 活动字段选择 `REQUIRES_FUTURE_SCOPE_DECISION`（未来范围决策），本轮不选择 `KEEP_AS_HISTORICAL_PLAN`（保持历史计划）。
4. 当前九十九路径契约收敛补丁已应用但尚无独立正式历史锚点；M03-M06 正式基线不能在这个前置问题未解决时进入暂存。

```text
MAINLINE_DRIFT_DETECTED=false
```

本次命令继续服务于 `saee_agent_evidence_integration`（智能体证据集成）主线，没有开启 Trust Infrastructure（可信基础设施）、Goal Integrity（目标完整性）或 State Integrity（状态完整性）工程。

## 1. 决策输入与权威边界

### 1.1 直接输入

```text
INPUT_INVENTORY=reports/SAEE_AGENT_EVIDENCE_M03_M06_FORMAL_BASELINE_OBJECT_INVENTORY.md
INPUT_INVENTORY_SHA256=ff885c0df6b5618e689eab2aaf19055c0e12f4c86d5a5619330b0c368b02651b
INPUT_OBJECT_COUNT=27
INPUT_A_CLASS_COUNT=21
INPUT_B_CLASS_COUNT=3
INPUT_D_CLASS_COUNT=3
```

本报告继承对象清单中已经逐项绑定的路径、SHA-256（安全散列算法二百五十六位）、来源、许可证、角色和分类，不重新修改或生成任何一个被审查对象。

### 1.2 权威顺序

1. SAEE Development Constitution v1.1（SAEE 开发宪法第一点一版）；
2. 规范能力清单和治理登记表；
3. M-03 人工权利人决定与冻结来源记录；
4. 二十七项正式基线对象清单；
5. 本决策准备报告。

本报告不是能力事实源，也不能覆盖前四级权威。

### 1.3 当前阶段真值

```text
SOURCE_CODE_MIGRATED=false
RUNTIME_INTEGRATED=false
MERGE_COMPLETED=false
FORMAL_BASELINE_SELECTED=false
FORMAL_BASELINE_AUTHORIZED=false
```

## 2. A类：二十一项主线基线候选

### 2.1 回答

```text
A_CLASS_CAN_ENTER_FORMAL_BASELINE_CANDIDATE_SET=true
A_CLASS_TRACKING_AUTHORIZED=false
```

A 类可以进入正式基线候选，原因是这些对象均直接支撑 M03-M06 的受限净室路径，具有不可替代的主线角色，并已在对象清单中完成来源、许可证和散列绑定。

但它们当前仍是未跟踪材料；本报告只认可候选资格，不授权任何版本控制动作。

### 2.2 A类对象集合

| 组别 | 文件路径 | 基线角色 |
| --- | --- | --- |
| 迁移治理 | `governance/migration/agent-evidence-source-provenance.v1.json` | 冻结来源、许可证和排除边界 |
| 迁移治理 | `governance/migration/agent-evidence-m03-owner-decision.v1.json` | 记录人工权利人受限净室授权 |
| 兼容包 | `agent-interface/integration/agent-evidence-compatibility/README.md` | 智能体可读入口与非能力边界 |
| 兼容包 | `agent-interface/integration/agent-evidence-compatibility/fixtures/invalid-counts.v0.1.json` | 来源完整性计数负例 |
| 兼容包 | `agent-interface/integration/agent-evidence-compatibility/fixtures/valid-pass.v0.1.json` | 未签名固定正例 |
| 兼容包 | `agent-interface/integration/agent-evidence-compatibility/fixtures/valid-signed.v0.1.json` | 合成签名固定正例 |
| 兼容包 | `agent-interface/integration/agent-evidence-compatibility/fixtures/valid-warn.v0.1.json` | 警告与缺失事件样例 |
| 内部契约 | `agent-interface/schemas/saee-agent-evidence-trait-adapter-input.v0.1.json` | 受限适配输入契约 |
| 内部契约 | `agent-interface/schemas/saee-agent-evidence-trait-adapter-result.v0.1.json` | 适配结果与真值边界契约 |
| 内部契约 | `agent-interface/schemas/saee-agent-evidence-evaluation-bridge-input.v0.1.json` | 评估桥接输入契约 |
| 内部契约 | `agent-interface/schemas/saee-agent-evidence-evaluation-bridge-result.v0.1.json` | 完整性与充分性分离结果契约 |
| 本地实现 | `saee_backend/services/agent_evidence_integrity.py` | 受限完整性原语 |
| 本地实现 | `saee_backend/services/agent_evidence_trait_adapter.py` | 净室性状适配器 |
| 本地实现 | `saee_backend/services/agent_evidence_evaluation_bridge.py` | 复用现有评估器的本地桥接器 |
| 专用校验 | `scripts/saee_agent_evidence_merge_readiness_check.py` | 来源、许可证与阶段真值校验 |
| 专用校验 | `scripts/saee_agent_evidence_trait_adapter_smoke.py` | 适配器冒烟校验（最小可运行校验） |
| 专用校验 | `scripts/saee_agent_evidence_evaluation_bridge_smoke.py` | 桥接器冒烟校验（最小可运行校验） |
| 单元测试 | `tests/test_agent_evidence_integrity.py` | 完整性行为测试 |
| 单元测试 | `tests/test_agent_evidence_trait_adapter.py` | 适配器与真值边界测试 |
| 单元测试 | `tests/test_agent_evidence_evaluation_bridge.py` | 桥接器和人工复核上限测试 |
| 单元测试 | `tests/test_agent_evidence_merge_readiness.py` | 迁移治理不可静默漂移测试 |

### 2.3 A类边界

A 类候选资格不代表：

- 新规范能力已经建立；
- 公开 MCP（模型上下文协议）或公开 Schema（数据结构规范）已经变化；
- 全部 Agent Evidence（智能体证据）源代码已经迁移；
- 外部运行时已经集成；
- SAEE Evidence（SAEE 证据）或 SAEE Evaluation（SAEE 评估）客户版本已经完成；
- 根仓库已经获得开源或外部分发许可证。

## 3. B类：三项证据报告

### 3.1 回答

```text
B_CLASS_KEEP_EVIDENCE_REPORT_IDENTITY=true
B_CLASS_CAN_BECOME_CAPABILITY_FACT_SOURCE=false
```

B 类必须保持证据报告身份。它们可以解释人工决定和本地校验结果，但不能成为能力状态、公开接口、许可证授权或迁移完成状态的独立权威。

### 3.2 B类对象集合

| 文件路径 | 保持身份 | 不得升级为 |
| --- | --- | --- |
| `reports/SAEE_AGENT_EVIDENCE_M03_OWNER_DECISION_PACKET.md` | M-03 人类可读决定报告 | 人工授权记录本体或能力事实源 |
| `reports/SAEE_AGENT_EVIDENCE_M04_M05_ADAPTER_REPORT.md` | M-04/M-05 本地结果报告 | 外部兼容、运行时集成或客户版本证明 |
| `reports/SAEE_AGENT_EVIDENCE_M06_EVALUATION_BRIDGE_REPORT.md` | M-06 本地结果报告 | 独立评估能力、授权系统或生产证明 |

### 3.3 与正式基线的关系

B 类可以作为正式基线的支持性旁证，但必须满足：

```text
B_CLASS_NORMATIVE_ROLE=false
B_CLASS_SUPPORTING_EVIDENCE_ROLE=true
```

即使未来与 A 类在同一受控历史检查点中出现，也必须保持路径、章节和能力登记上的非规范身份。

## 4. D类：三项需要未来范围决策的治理对象

### 4.1 选择

本次选择：

```text
D_CLASS_M07_FIELD_DECISION=REQUIRES_FUTURE_SCOPE_DECISION
KEEP_AS_HISTORICAL_PLAN_SELECTED=false
```

### 4.2 为什么不选择保持历史计划

三项对象目前都是机器可读治理表面，并继续使用活动字段表达 M-07 下一步：

| 文件路径 | 活动字段 | 当前风险 |
| --- | --- | --- |
| `governance/migration/agent-evidence-migration-crosswalk.v1.json` | `gate.next_authorized_work` | 把 M-07 设计表达成已授权下一步 |
| `governance/migration/agent-evidence-schema-compatibility.v1.json` | `gate.next_step` | 把兼容性结论继续路由到 M-07 |
| `governance/migration/saee-three-version-integration-plan.v1.json` | `next_gate.required_decision` | 把三版本计划的下一门指向 M-07 |

只在本报告中把它们称为“历史计划”，不会改变文件自身的机器语义。这样会产生“外部说明说历史、机器对象说活动”的真值冲突。因此本轮不能选择 `KEEP_AS_HISTORICAL_PLAN`（保持历史计划）。

### 4.3 当前处置

```text
D_CLASS_INCLUDED_IN_FORMAL_BASELINE_CANDIDATE_SET=false
D_CLASS_FILES_MODIFIED=false
D_CLASS_DELETED=false
M07_AUTHORIZED=false
```

D 类应保持未跟踪、未修改状态，等待未来单独决定：

1. 是否将其明确封存为历史规划快照；或
2. 是否在独立授权下修正活动下一步真值；或
3. 是否由新的、受控的当前计划对象取代。

上述任何选择都不属于本轮权限。

## 5. 建议的正式基线候选结构

如果未来人工授权，建议只形成以下逻辑结构：

```text
FORMAL_BASELINE_NORMATIVE_CANDIDATES=21
FORMAL_BASELINE_SUPPORTING_EVIDENCE_REPORTS=3
FORMAL_BASELINE_EXCLUDED_PENDING_SCOPE_DECISION=3
FORMAL_BASELINE_TOTAL_SELECTED_PATHS=24
```

二十四项选择路径内部仍分成两个角色：

- 二十一项 A 类：主线规范、实现、校验和测试候选；
- 三项 B 类：支持性证据报告。

三项 D 类不进入该候选集合。

本对象清单报告与本决策准备报告属于审查和决策表面，也不自动加入上述二十四项。若未来需要把它们纳入正式历史，必须在授权清单中单独列出。

## 6. 建立正式基线的前置条件

以下条件必须全部满足，才能请求正式基线执行授权。

### 条件一：输入对象保持不变

```text
INVENTORY_HASH_MATCH=true
A_CLASS_HASHES_MATCH=21/21
B_CLASS_HASHES_MATCH=3/3
D_CLASS_HASHES_MATCH=3/3
```

任何对象散列值变化都必须停止，重新进行对象清单审查。

### 条件二：九十九路径契约补丁先获得独立父基线

当前事实：

```text
CONTRACT_ALIGNMENT_PATCH_APPLIED=true
CONTRACT_ALIGNMENT_PATCH_PATH_COUNT=99
CONTRACT_ALIGNMENT_PATCH_FORMAL_HISTORY_STATUS=APPLIED_UNCOMMITTED
M03_M06_CONTRACT_PATCH_PATH_INTERSECTION=0
PARENT_BASELINE_STATUS=UNRESOLVED
```

建立 M03-M06 正式基线前，必须先为已批准的九十九路径契约收敛补丁建立独立、不可变、可引用的父基线。父基线可以是另行批准的版本控制历史检查点或等价的内容寻址基线，但不能与 M03-M06 二十四项选择路径混成一个未经区分的提交。

本报告不授权建立该父基线。

### 条件三：隔离重建

必须在新的隔离工作区中，从已确认父基线重建恰好二十四项选择路径：

```text
ISOLATED_RECONSTRUCTION_REQUIRED=true
SELECTED_PATH_COUNT_REQUIRED=24
UNRELATED_PATH_COUNT_ALLOWED=0
D_CLASS_PATH_COUNT_ALLOWED=0
GENERATED_NOISE_ALLOWED=0
```

不得携带当前其余工作区变化、缓存、生成文件或未来研究材料。

### 条件四：精确允许清单与散列清单

执行前必须形成一次性精确允许清单，至少记录：

- 父基线标识；
- 二十一项 A 类路径和散列；
- 三项 B 类路径和散列；
- 三项 D 类明确排除；
- 对象清单报告散列；
- 执行授权标识和消费规则。

禁止使用全局替换、目录整体暂存或模糊路径规则代替精确允许清单。

### 条件五：来源与许可证边界继续成立

```text
FROZEN_SOURCE_LICENSE=ALL_RIGHTS_RESERVED
BOUNDED_CLEAN_ROOM_GRANT_RECORDED=true
DIRECT_SOURCE_TEXT_COPY_AUTHORIZED=false
GIT_HISTORY_MERGE_AUTHORIZED=false
SAEE_ROOT_LICENSE_SELECTED=false
PUBLIC_DISTRIBUTION_AUTHORIZED=false
```

正式内部基线不能被解释为开源发布、外部分发、市场迁移或源实现复制授权。

### 条件六：能力和接口真值保持

必须证明：

```text
CANONICAL_CAPABILITY_COUNT=9
CANONICAL_CAPABILITY_INVENTORY_CHANGED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
NEW_CAPABILITY_CREATED=false
```

内部净室适配器和评估桥接器仍是迁移基础设施，不得通过形成基线被自动升级为公开规范能力。

### 条件七：隔离验证通过

至少需要在隔离候选集合上通过：

- 智能体证据迁移就绪校验；
- 适配器和桥接器专用校验；
- 相关单元测试；
- 规范能力清单校验；
- 能力台账校验；
- 能力真值一致性校验；
- 宪法校验；
- 治理登记表校验；
- `git diff --check`（版本差异格式检查）。

如运行主线守卫，必须在隔离环境中确认其不会产生未授权写入；验证工具产生的副作用不得进入候选集合。

### 条件八：单独人工授权

```text
FORMAL_BASELINE_HUMAN_AUTHORIZATION_REQUIRED=true
AUTHORIZATION_RECEIVED=false
```

未来授权必须明确：父基线、二十四项选择路径、三项 D 类排除、是否允许暂存、是否允许提交，以及停止线。不能从本报告自动推导实施权限。

## 7. 停止条件

出现以下任一情况必须停止：

1. 二十七项中任何对象的路径或散列发生变化；
2. 九十九路径补丁尚无独立父基线；
3. 隔离候选中出现三项 D 类对象；
4. 隔离候选混入当前其他工作区变化或生成噪声；
5. 规范能力清单、公开 MCP（模型上下文协议）或公开 Schema（数据结构规范）发生变化；
6. 净室材料被解释为源实现复制、外部兼容或生产证明；
7. 任何校验失败或产生未解释副作用；
8. 人工授权没有精确写明允许的版本控制动作。

## 8. 只读验证结果

```text
A_CLASS_PATH_SET_MATCH=21/21
B_CLASS_PATH_SET_MATCH=3/3
D_CLASS_PATH_SET_MATCH=3/3
PROTECTED_OBJECT_HASH_MISMATCH_COUNT=0
INPUT_INVENTORY_HASH_UNCHANGED=true
CANONICAL_CAPABILITY_INVENTORY_HASH_UNCHANGED=true
MCP_REGISTRY_HASH_UNCHANGED=true
PRODUCT_REGISTRY_HASH_UNCHANGED=true
```

以下校验通过：

- 宪法校验；
- 规范能力清单校验；
- 治理登记表校验；
- A、B、D 三类路径集合与输入清单的精确比较。

宪法校验继续确认：当前主线为智能体证据集成，源代码未整体迁移，运行时未集成，生产就绪状态为假。

## 9. 历史跑偏教训核查

### 8.1 准备完成不等于授权完成

本报告完成只表示决策材料已准备，不表示正式基线已经选定、技术条件已经闭合或执行已经授权。

### 8.2 不让旧计划字段恢复已停止副线

三项 D 类对象中的 M-07 字段不能借“正式基线”名义重新成为当前路线。未来范围决策必须独立进行。

### 8.3 不把证据报告升级成能力事实

B 类报告只能解释已发生的人工决定和本地校验，不得取代机器授权记录、规范能力清单或实现证据。

### 8.4 不把两个正确补丁混成一个不可解释历史

九十九路径契约收敛补丁与 M03-M06 二十四项选择路径都可能各自合理，但在没有父子基线和独立授权时混合提交，会破坏来源与责任边界。

## 10. 下一步

当前唯一允许的下一步是人工审查本决策准备报告，确认：

1. 是否接受 A 类二十一项的候选资格；
2. 是否接受 B 类三项的证据报告身份；
3. 是否接受 D 类选择 `REQUIRES_FUTURE_SCOPE_DECISION`（未来范围决策）；
4. 是否同意先解决九十九路径契约补丁的独立父基线，再讨论 M03-M06 正式基线授权。

在人工确认前：

```text
FORMAL_BASELINE_AUTHORIZED=false
GIT_ADD_EXECUTED=false
COMMIT_EXECUTED=false
PUSH_EXECUTED=false
MERGE_EXECUTED=false
```

## 11. 最终状态

```text
SAEE_AGENT_EVIDENCE_M03_M06_FORMAL_BASELINE_DECISION_PREPARATION_STATUS=COMPLETE
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
A_CLASS_CAN_ENTER_FORMAL_BASELINE_CANDIDATE_SET=true
A_CLASS_OBJECT_COUNT=21
A_CLASS_TRACKING_AUTHORIZED=false
B_CLASS_KEEP_EVIDENCE_REPORT_IDENTITY=true
B_CLASS_OBJECT_COUNT=3
B_CLASS_CAN_BECOME_CAPABILITY_FACT_SOURCE=false
D_CLASS_M07_FIELD_DECISION=REQUIRES_FUTURE_SCOPE_DECISION
D_CLASS_OBJECT_COUNT=3
D_CLASS_INCLUDED_IN_FORMAL_BASELINE_CANDIDATE_SET=false
FORMAL_BASELINE_TOTAL_SELECTED_PATHS=24
PARENT_BASELINE_STATUS=UNRESOLVED
FORMAL_BASELINE_SELECTED=false
FORMAL_BASELINE_AUTHORIZED=false
SOURCE_CODE_MIGRATION_EXECUTED=false
RUNTIME_INTEGRATION_EXECUTED=false
CANONICAL_CAPABILITY_INVENTORY_CHANGED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
NEW_CAPABILITY_CREATED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
COMMIT_EXECUTED=false
PUSH_EXECUTED=false
MERGE_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_M03_M06_FORMAL_BASELINE_DECISION_PREPARATION
```
