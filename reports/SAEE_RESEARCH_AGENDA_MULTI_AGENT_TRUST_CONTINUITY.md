# SAEE 多智能体可信连续性研究议程

日期：2026-07-17

## 0. 文件定位

本文件属于 Future Research（未来研究）与 Academic Positioning（学术定位），用于提出一个可研究、可区分、可证伪的上位研究议程。

它不是产品文档、技术规范、当前能力声明、实验授权或工程路线。

现有 `reports/SAEE_AGENT_STATE_INTEGRITY_RESEARCH_AGENDA.md`（智能体状态完整性研究议程）只作为一个历史子问题参考；本议程不恢复其工程副线，不继承其实现或实验授权，也不把状态完整性描述为当前能力。

```text
DOCUMENT_CLASS=FUTURE_RESEARCH_ACADEMIC_POSITIONING
RESEARCH_AGENDA_SCOPE=MULTI_AGENT_TRUST_CONTINUITY
FUTURE_RESEARCH_ONLY=true
PRODUCT_DOCUMENT=false
TECHNICAL_SPECIFICATION=false
CURRENT_CAPABILITY_CLAIM=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
```

## 第一部分：Research Category（研究类别）

候选研究类别：

> Multi-Agent Long-Running Trust Infrastructure（多智能体长期运行可信基础设施）

研究定义：

> 研究多个智能体在长期运行、交接、再委托和状态变化后，如何基于有限身份、执行、证据和治理信号，判断过去建立的可信依据是否仍支持当前有限主张，并显式保留不确定性、反证和重新确认条件。

候选学术核心：

> Trust Continuity Interpretation（可信连续性解释）

该类别不是“让智能体永远正确”，也不是把所有治理、身份、运行和可观测问题合并为一个平台。它研究的是：

1. 可信判断依赖了哪些前提；
2. 这些前提如何随时间和多主体协作变化；
3. 哪些证据能够支持连续性，哪些只能证明局部事实；
4. 何时需要重新评估、收缩结论或交给人类复核。

```text
RESEARCH_CATEGORY_STATUS=PROPOSED_ACADEMIC_CATEGORY
CATEGORY_RECOGNIZED_BY_FIELD=false
STANDARDIZED_CATEGORY=false
```

## 第二部分：Research Problem（研究问题）

### 2.1 为什么长期运行产生新问题

一次性智能体任务通常把目标、上下文、身份、权限和结果压缩在较短时间窗口内。长期、多智能体系统会经历：

- 模型、版本、运行实例和工具变化；
- 跨智能体任务交接与再委托；
- 证据来源、覆盖范围和时效变化；
- 上下文、记忆、计划和环境变化；
- 组织政策、权限和人工决定变化。

每一步局部合理，不代表最初可信条件仍然成立。单次身份认证、一次评估通过、一条完整轨迹或一个有效签名，都不足以自动证明长期连续性。

### 2.2 核心研究问题

> 当主体、证据、委托和状态持续变化时，系统如何判断过去的可信依据仍然有效、已经失效，或需要重新确认？

该问题可以分解为六个研究问题：

1. **RQ1 — 身份连续性**：哪些最小身份和版本信号足以支持“仍是同一可信主体关系”的有限结论？
2. **RQ2 — 证据连续性**：如何判断不同时间、运行时和主体产生的证据仍覆盖同一主张？
3. **RQ3 — 委托连续性**：如何区分合法交接、受限再委托、权限扩张和责任断裂？
4. **RQ4 — 状态连续性**：如何区分正常演化、解释充分的变化和无法追溯的状态偏离？
5. **RQ5 — 基础设施组合**：如何组合遥测、通信、身份和治理信号，而不复制这些系统？
6. **RQ6 — 决策效用**：连续性解释是否真的改善继续、暂停、重新确认或人工复核决定？

### 2.3 可证伪边界

如果未来研究发现：

- 普通可观测分析已经能同等回答上述问题；
- 连续性解释只增加文本和成本，不改善决策；
- 四类连续性无法形成稳定、可重复的标注；
- 所需信息必须依赖不可观察的模型内部状态；
- 研究必须先建造完整运行时或治理平台才能成立；

则该类别假设应被收缩、拆分或停止，而不是通过增加系统复杂度维持。

## 第三部分：Trust Continuity Framework（可信连续性框架）

### 3.1 Identity Continuity（身份连续性）

研究对象：主体、模型、版本、工作负载、角色和身份绑定关系如何随时间变化。

主要问题：

- 声明身份与可验证身份之间有什么差异？
- 模型或运行实例变化后，哪些身份属性仍可继承？
- 子智能体与父智能体之间的身份关系如何表达？
- 身份凭证仍有效时，角色和目的变化是否需要重新解释？

候选证据：外部身份系统记录、版本信息、工作负载身份、签名关系和运行来源。

边界：身份连续性不等于一次认证成功；SAEE 不签发身份或凭证。

### 3.2 Evidence Continuity（证据连续性）

研究对象：证据与主张之间的来源、覆盖、时间、修订和冲突关系。

主要问题：

- 不同运行时和智能体产生的证据能否组合？
- 证据何时过期、被替代或失去适用性？
- 签名、收据、轨迹和人工记录分别能支持什么？
- 新证据与旧证据冲突时，连续性结论如何收缩？

候选证据：轨迹、日志、收据、散列、签名、来源记录、评估结果和反证。

边界：Evidence（证据）不等于 Reality（现实）；证据存在不证明内容真实、完整或足够。

### 3.3 Delegation Continuity（委托连续性）

研究对象：任务在委托、拆分、交接和再委托过程中的范围、时效、接受者和责任关系。

主要问题：

- 哪些字段能够区分合法交接与未经授权扩张？
- 委托有效期、目标范围和停止条件如何传递？
- 多次再委托后，责任和限制如何保持可追溯？
- 执行能力仍可用时，如何识别原始委托条件已经失效？

候选证据：任务记录、通信事件、委托来源、接受记录、范围、有效期和人工决定。

边界：委托连续性解释不授予权限，也不替代身份与访问管理系统。

### 3.4 State Continuity（状态连续性）

研究对象：可观察任务状态与已知基线、允许变化、关键约束和证据之间的关系。

主要问题：

- 什么是最小可观察状态，而不是模型内部思想？
- 如何区分正常更新、合法重新规划与无法解释的偏离？
- 多个检查点之间的变化如何追溯？
- 过去有效的判断在什么条件下必须重新评估？

候选证据：声明目标、关键约束、计划版本、行动记录、结果、检查点和变化理由。

边界：State Continuity（状态连续性）是未来研究，不代表当前存在 State Engine（状态引擎）、Goal Engine（目标引擎）或持续监控能力。

### 3.5 四方向关系

```text
Identity Continuity（身份连续性）
        +
Evidence Continuity（证据连续性）
        +
Delegation Continuity（委托连续性）
        +
State Continuity（状态连续性）
        ↓
Trust Continuity Interpretation（可信连续性解释）
        ↓
有限结论、缺口、不确定性与重新确认条件
```

四个方向不是四个当前产品，也不要求建立统一总分。

## 第四部分：Relation To Existing Infrastructure（与现有基础设施关系）

本研究必须组合现有基础设施，不以学术类别卡位为理由重复建设。

| 现有基础设施 | 它主要解决什么 | 可提供的研究输入 | 本议程不替代 |
| --- | --- | --- | --- |
| OpenTelemetry（开放遥测） | 轨迹、日志、指标、事件和资源语义 | 执行过程、时间、工具调用和运行上下文 | 采集器、传输规范、存储和可观测后端 |
| MCP（模型上下文协议） | 工具与资源发现、连接和调用传输 | 工具调用、资源来源、请求与结果引用 | 工具协议、连接器、服务运行和授权传输 |
| A2A（智能体通信） | 智能体发现、通信、任务和长任务协作 | 交接、委托、任务状态和跨智能体事件 | 通信协议、任务执行和协作运行时 |
| IAM（身份与访问管理） | 身份、角色、凭证和访问权限 | 主体身份、角色、权限与变化记录 | 身份签发、认证、访问决策和权限执行 |
| Governance Platform（治理平台） | 策略、审批、风险、合规和组织控制 | 策略版本、人工决定、控制结果和例外 | 策略执行、暂停机制、合规认定和最终治理权 |

候选关系：

```text
EXISTING_INFRASTRUCTURE_RELATIONSHIP=COMPOSITION_NOT_SUBSTITUTION
NEW_PROTOCOL_PROPOSED=false
RUNTIME_REPLACEMENT_PROPOSED=false
AUTHORITY_REPLACEMENT_PROPOSED=false
```

研究输出只能形成 Decision Context（决策上下文），不能自动获得 Authorization（授权）或 Execution（执行）权力。

## 第五部分：SAEE Current Position（SAEE 当前定位）

### 5.1 当前主线

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
```

当前实际定位：

1. Agent Evidence Integration（智能体证据集成）；
2. Evaluation（评估）；
3. Readiness（就绪判断）。

当前 `saee.evaluate_agent_run`（智能体运行评估）和 `saee.evaluate_evidence`（证据评估）只能在各自受限契约内评估声明证据、要求覆盖和就绪建议。它们不能自动判断四类连续性，也不能认证现实事件或授权行动。

```text
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
TRUST_CONTINUITY_EVALUATION_IMPLEMENTED=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
```

### 5.2 未来学术方向

> Trust Continuity Interpretation（可信连续性解释）

未来研究可以探索表示、测量、数据集、基准、标注一致性和决策效用，但任何研究设计都必须先证明它提供了超出普通日志审查、可观测分析和治理规则的增量价值。

```text
TRUST_CONTINUITY_INTERPRETATION_IMPLEMENTED=false
FUTURE_RESEARCH_ONLY=true
```

### 5.3 研究推进顺序

若未来获得独立授权，建议的学术顺序是：

1. 定义有限主张和可观察变量；
2. 建立合法变化与连续性失败的标注边界；
3. 在单一方向上验证可测量性；
4. 与普通可观测审查和人工审查比较；
5. 只有出现增量价值后，才研究跨方向组合；
6. 只有研究成立后，才讨论系统或产品实现。

该顺序是研究建议，不是执行授权。

## 第六部分：Non-Claims（不声明事项）

当前 SAEE 没有：

- 完整 Multi-Agent Long-Running Trust Infrastructure（多智能体长期运行可信基础设施）；
- State Engine（状态引擎）；
- Goal Engine（目标引擎）；
- 完整身份连续性能力；
- 完整证据连续性能力；
- 完整委托连续性能力；
- 完整状态连续性能力；
- 自动治理；
- 自动授权；
- 自动执行控制；
- 已验证客户、收入或生产部署。

本议程也不声明：

- SAEE 已经解决智能体幻觉、漂移或长期可靠性；
- 当前评估器可以判断目标或状态连续性；
- 研究类别已经获得学术共同体或标准组织认可；
- OpenTelemetry（开放遥测）、MCP（模型上下文协议）、A2A（智能体通信）、IAM（身份与访问管理）或治理平台已经与 SAEE 完成集成；
- 未来研究已经获得实验、工程、产品或发布授权。

## 7. 研究质量与停止条件

未来研究必须：

- 使用可观察证据，不声称读取模型内部思想；
- 区分正常变化、合法变化和连续性失败；
- 预先定义标注、指标、成本和停止条件；
- 保存负面结果；
- 与现有基础设施和普通审查方法比较；
- 不以增加文档、字段或治理层数量作为成功指标。

出现以下任一情况应停止或收缩：

- 无法获得稳定真值；
- 误报导致合理智能体变化被系统性阻止；
- 成本超过决策增益；
- 结果可以被更简单的现有方法完全复制；
- 研究副线开始取代 Agent Evidence Integration（智能体证据集成）主线。

## 8. 最终状态

```text
RESEARCH_AGENDA_PREPARATION_STATUS=COMPLETE
RESEARCH_CATEGORY_STATUS=PROPOSED_ACADEMIC_CATEGORY
DOCUMENT_CLASS=FUTURE_RESEARCH_ACADEMIC_POSITIONING
DUPLICATE_RESEARCH_IMPLEMENTATION_CREATED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CURRENT_MAINLINE_UNCHANGED=true
FUTURE_RESEARCH_ONLY=true
CURRENT_CAPABILITY_UNCHANGED=true
F1_BASELINE_UNCHANGED=true
P1_UNCHANGED=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
NEW_CAPABILITY_CREATED=false
MAINLINE_DRIFT_DETECTED=false
```
