# SAEE Market Positioning Document

中文名称：SAEE 市场定位文档<br>
版本：`v1.0`<br>
阶段：`PHASE_1_CATEGORY_POSITIONING`<br>
项目：`SAEE Multi-Agent Long-Running Trust Infrastructure`<br>
日期：`2026-07-17`

```text
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
CATEGORY_POSITIONING_ACTIVE=true
PRODUCT_EXPANSION_AUTHORIZED=false
ARCHITECTURE_EXPANSION_AUTHORIZED=false
CURRENT_CAPABILITY_FACTS_CHANGED=false
FUTURE_DIRECTION_IS_CURRENT_CAPABILITY=false
```

## 1. 定位结论

SAEE 的未来市场类别定位是：

> **Multi-Agent Long-Running Trust Infrastructure**<br>
> 多智能体长期运行可信基础设施

SAEE 研究企业在大量 Agent 长期自主运行、跨 Agent 协作和跨会话延续时，如何持续理解并验证：

- 谁在行动；
- 行动继承了什么目标和委托；
- 状态与记忆如何变化；
- 什么证据支持当前判断；
- 谁对下一步负责；
- 何时必须停止、复核或重新授权。

SAEE 不以“让 Agent 更聪明”为类别入口，也不以某一个当前工具作为品牌总定义。SAEE 要占据的是企业从“能运行 Agent”进入“敢让多 Agent 长期运行”时所缺少的可信基础设施层。

## 2. 类别问题

AI Agent 正从一次性回答和短任务，进入持久会话、异步任务、跨系统工具调用与多 Agent 协作。Agent Framework 已经能够组织执行、handoff、checkpoint 和恢复；Observability 已经能够收集 trace、span、log 和 metric；身份与授权系统已经能够控制访问。

但这些层仍没有共同回答一个长期问题：

> 当主体、目标、上下文、状态、记忆、委托和风险在运行中持续变化时，为什么企业应当相信当前 Agent 的下一步仍然处于原始责任边界内？

因此，市场缺口不是“更多 Agent 功能”，而是 `Verifiable Agency Continuity`（可验证的行为主体连续性）。

## 3. 核心价值主张

### 面向企业

从一次性授权转向可持续、可收缩、可复核的 Agent 自主边界。

### 面向 Agent Platform

在 runtime、framework、observability、IAM 和 policy 之外，形成对身份、状态、记忆、证据和责任关系的受限可信解释。

### 面向开发者

让 Agent 的能力、当前状态、证据边界和非主张能够被其他 Agent 与工程团队发现、理解和组合。

### 面向生态伙伴

提供一个不替代既有协议和平台的中立类别：现有系统继续负责执行、通信、遥测与授权；SAEE 研究如何把这些输入组织成长期可信判断所需的证据关系。

## 4. 类别语言

### 主标签

`SAEE — Multi-Agent Long-Running Trust Infrastructure`

### 中文解释

`面向企业多智能体长期运行场景的可信基础设施方向`

### 核心句

`企业不只需要会工作的 Agent，还需要能够被长期信任的 Agent 系统。`

### 问题句

`Agent 能运行数小时、数天甚至更久，但企业如何确认它仍是同一个受托主体、仍在执行同一个目标、仍基于可信状态和记忆？`

### 类别链

`Identity → Execution Evidence → State Continuity → Governance → Trust Decision`

### 禁止使用的无证据语言

- “完整解决多智能体治理”；
- “企业级生产可信层已经就绪”；
- “已验证所有 Agent 身份”；
- “已实现长期状态连续性”；
- “自动判定法律或组织责任”；
- “支持所有 Agent Framework / Cloud Agent Platform”；
- “已成为行业标准”。

## 5. Current Capability 与 Future Direction

### Current Capability

根据 `capability-package/manifest.json#canonical_inventory`，当前可公开说明：

- `saee.evaluate_agent_run`：本地、确定性地评估声明式 trace metadata 与 required evidence coverage；
- `saee.evaluate_evidence`：对封闭的本地 evidence bundle 按明确要求检查，并返回缺失证据与受限 reason code；
- 一个 allowlisted、synthetic 的 OTel-style candidate mapping 已实现，但不等于 OTLP ingestion、OpenTelemetry conformance 或可信 trace；
- 当前判断是 `Recommendation`，不是 `Authorization`；
- 当前没有客户验证或生产就绪证明。

### Future Direction

以下属于未来战略，不是当前能力：

- Agent Identity continuity；
- end-to-end delegation binding；
- trusted trace-to-evidence conversion；
- cross-agent State Continuity；
- Agent Memory trust；
- longitudinal Goal / Context continuity；
- Multi-Agent Governance；
- Trust Decision Infrastructure；
- responsibility determination。

## 6. 竞争与组合边界

| 相邻类别 | 主要职责 | SAEE 不替代 | SAEE 研究的缺口 |
|---|---|---|---|
| Agent Framework | 编排、handoff、checkpoint、恢复 | runtime 与开发框架 | checkpoint 之间的身份、目标和责任连续性 |
| Observability | 收集和展示运行信号 | trace、log、metric 平台 | 信号能否支持具体可信主张 |
| IAM / Authorization | 身份认证、权限与访问控制 | 企业授权系统 | 委托、状态变化与证据是否仍匹配当前权限 |
| Policy Engine | 规则匹配与执行控制 | policy enforcement | 决策上下文是否完整、来源是否可信 |
| Security Scanner | 漏洞、配置和供应链风险检测 | 安全检测产品 | 长期行为主体与状态责任链 |
| A2A / MCP | Agent 通信、发现和工具访问 | transport 与协议 | 跨协议长期可信解释 |

## 7. 目标受众与购买中心假设

以下是待验证假设，不是客户证据：

1. **Enterprise Agent Platform Owner**：希望扩大 Agent 自主范围，但需要连续状态和责任证据。
2. **Security / IAM Leader**：希望知道 Agent 获得权限后是否仍在原始委托范围内。
3. **AI Governance / Model Risk Team**：需要把模型风险扩展为长期 Agent 行为风险。
4. **Internal Audit / Compliance**：需要可复核的决策和责任材料，但不希望只得到更多日志。
5. **Agent Framework / Cloud Platform Partner**：需要一个可组合的可信解释层，而不是另一个 runtime。

```text
CUSTOMER_PROBLEM_VALIDATED=false
WILLINGNESS_TO_PAY_VALIDATED=false
BUYER_CONFIRMED=false
PARTNER_CONFIRMED=false
```

## 8. 市场叙事层级

1. **定义时代变化**：Agent 正从短任务走向长期、多 Agent、自主运行。
2. **定义企业阻力**：最大的阻力不是模型不会做，而是企业无法持续证明它仍应被放权。
3. **定义基础设施缺口**：身份、目标、状态、记忆、证据与责任没有形成连续信任链。
4. **定义 SAEE 方向**：SAEE 正在研究和建设这一可信基础设施层。
5. **展示当前证据**：当前只展示受限、真实的 Evidence / Evaluation 能力。
6. **展示未来路线**：把 Identity、State、Memory、Governance 明确标成 Future Direction。
7. **提供生态入口**：Whitepaper、Architecture Overview、GitHub、agent-readable surfaces 和合作研究入口。

## 9. Category Positioning 成功指标

Phase 1 不以代码量、功能数或生产用户数作为完成标准。主要指标为：

- 外部访问者能在 30 秒内复述 SAEE 的类别；
- 访问者不会把 SAEE 误解为日志、单 Agent 工具或安全扫描器；
- 网站与 GitHub 都能清楚区分 `Current Capability` 和 `Future Direction`；
- Agent 能从 README、`llms.txt`、`agent-index.json` 与 Architecture Overview 发现同一类别语言；
- 生态伙伴能够判断 SAEE 与 framework、observability、IAM、A2A 和 MCP 的组合边界；
- 至少产生可复核的开发者理解、生态对话或合作研究信号；
- 没有把 research、local validation、public website、customer validation 与 production readiness 合并。

## 10. 停止条件

若类别建设开始要求修改当前主线代码、扩展 MCP、增加未验证 capability、复制相邻基础设施或把未来方向写成当前产品，应立即停止并回到本定位文档。

```text
WEBSITE_POSITIONING_MAY_CHANGE=true
GITHUB_NARRATIVE_MAY_CHANGE=true
WHITEPAPER_OUTLINE_MAY_CHANGE=true
ECOSYSTEM_RESEARCH_MAY_CHANGE=true
CURRENT_RUNTIME_MAY_CHANGE=false
CURRENT_MCP_MAY_CHANGE=false
CURRENT_SCHEMA_MAY_CHANGE=false
```
