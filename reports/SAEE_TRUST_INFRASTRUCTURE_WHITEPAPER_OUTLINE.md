# SAEE Trust Infrastructure Whitepaper Outline

中文名称：SAEE 可信基础设施白皮书大纲<br>
拟定标题：**The Trust Layer for Long-Running Multi-Agent Systems**<br>
拟定副标题：**Why Identity, Execution Evidence, State Continuity and Governance Must Become Shared Infrastructure**<br>
版本：`v1.0-outline`<br>
阶段：`PHASE_1_CATEGORY_POSITIONING`

```text
WHITEPAPER_STATUS=OUTLINE_ONLY
INDUSTRY_PROBLEM_DEFINITION=true
PRODUCT_PROMOTION_PRIMARY=false
CURRENT_CAPABILITY_EXPANSION=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

## 1. 白皮书目的

白皮书不以宣传 SAEE 当前功能为中心，而是定义一个行业问题：当企业开始部署长期运行、跨 Agent 协作的自主系统时，现有 runtime、framework、observability、IAM 和日志为什么不足以形成持续信任。

预期读者：企业 Agent Platform Owner、CTO/CISO、AI Governance、IAM、Observability、Agent Framework 开发者、Cloud Agent Platform 和标准组织参与者。

## 2. Executive Thesis

核心论点：

> 下一代 Agent 基础设施的瓶颈，不再只是模型能力或任务编排，而是能否持续证明行为主体、目标、状态、记忆、证据和责任在长期运行中仍然保持可解释的连续性。

提出研究性类别名称：

`Multi-Agent Long-Running Trust Infrastructure`

提出研究性核心概念：

`Verifiable Agency Continuity`

二者都属于类别和架构假设，不是当前产品实现或已建立的正式标准。

## 3. 第一部分：为什么需要长期可信基础设施

### Chapter 1 — From Tasks to Persistent Agency

- Agent 从单次回答进入工具调用、持续会话、异步任务和多 Agent collaboration；
- task duration 增长如何改变故障传播和责任边界；
- 一次运行正确为什么不能证明长期系统可信；
- 多 Agent handoff 如何引入目标、权限、上下文和责任损失。

### Chapter 2 — The Enterprise Delegation Gap

- 企业为什么可以批准一次操作，却不敢无限期放权；
- 静态 token、单次审批和长期运行之间的张力；
- 权限随目标、风险、角色和时间变化时为什么需要连续判断；
- 撤销、过期、责任转移和 human authority 的位置。

### Chapter 3 — Six Continuity Requirements

1. Identity Continuity；
2. Goal Continuity；
3. State Continuity；
4. Memory Trustworthiness；
5. Execution Traceability；
6. Responsibility Provability。

本章应使用跨数小时、数天和跨 Agent 的同一企业 workflow 贯穿说明，而不是使用孤立 API 调用。

## 4. 第二部分：现有基础设施为什么不足

### Chapter 4 — Agent Frameworks Are Runtimes, Not Trust Authorities

- framework 的强项：编排、工具调用、handoff、checkpoint、恢复和 human-in-the-loop；
- checkpoint 证明保存过状态，不自动证明状态来源、目标连续性或责任合法性；
- framework-local identity 与跨组织 authenticated identity 的差异；
- 可恢复执行与可信执行的差异。

证据锚点：LangGraph 官方文档将 persistence 描述为 checkpoint、memory、time travel 与 fault tolerance；OpenAI Agents SDK 官方文档将 tracing 用于记录 run、tool call、handoff 与 guardrail。这些能力是重要输入，但不自动形成长期责任判断。

### Chapter 5 — Observability Is a Sensor, Not a Trust Decision

- traces、metrics、logs、events 和 semantic conventions 的作用；
- instrumentation、sampling、clock、export 与敏感数据对完整性的影响；
- “看见调用链”与“证明目标仍有效”的差异；
- 同一 trace 为什么可以支持不同甚至冲突的主张；
- trace 进入可信判断前需要 authenticity、provenance 和 claim binding。

### Chapter 6 — Ordinary Logs Are Producer Assertions

- 日志由谁产生、谁能修改、何时采样；
- append-only 能提高篡改可见性，但不能自动建立身份、委托和责任；
- event sequence 与 decision rationale 的差异；
- log retention 与 memory validity 的差异；
- 需要从“记录事件”转向“证明受限主张”。

### Chapter 7 — Protocols and IAM Solve Necessary but Partial Problems

- A2A：发现、通信、task lifecycle、异步长任务和授权请求；
- MCP：工具/资源访问以及 OAuth resource binding；
- SPIFFE：动态 workload identity；
- OAuth/GNAP：访问与委托授权；
- SCITT：signed statement、receipt 与 transparency；
- 为什么这些原语仍需要跨层解释，而不是被 SAEE 替代。

## 5. 第三部分：SAEE 提出的可信基础设施模型

### Chapter 8 — The Bounded Trust Transition

提出最小研究对象：

`Trusted Transition = Subject + Authority + Prior State + Goal + Context + Action + Evidence + Result + Responsibility`

说明这不是 Schema，也不是当前接口，而是分析框架。任一关键关系缺失时，输出应保留 `unknown`、`insufficient_evidence` 或 `human_review_required`。

### Chapter 9 — Five Core Objects

- Agent Identity；
- Agent State；
- Agent Memory；
- Agent Evidence；
- Agent Governance。

每个对象分别回答：定义、来源、生命周期、可信边界、跨 Agent 关系、撤销或失效条件，以及当前 SAEE 是否实现。

### Chapter 10 — Evidence-to-Trust Interpretation

- 为什么 SAEE 的潜在位置是 interpretation，而不是 runtime 或 actuator；
- claim-scoped evaluation；
- supported / unsupported / missing / contradictory / unauthenticated；
- Recommendation 与 Authorization 分离；
- last-known-valid context 的研究价值；
- 人类权力和外部 IAM/Policy 的最终控制位置。

### Chapter 11 — Architecture Hypothesis

白皮书主架构图：

```text
Agent Identity
      ↓
Execution Evidence
      ↓
State Continuity
      ↓
Multi-Agent Governance
      ↓
Trust Decision Context
```

补充组合图：

```text
Agent Runtime / Framework
          ↓
      A2A / MCP
          ↓
Telemetry / Identity / Delegation / Transparency
          ↓
SAEE Evidence-to-Trust Interpretation
          ↓
Enterprise IAM / Policy / Human Authority
```

两张图都必须标注 `FUTURE ARCHITECTURE HYPOTHESIS`。

## 6. 第四部分：从类别到可验证研究

### Chapter 12 — Current SAEE Capability Boundary

以 canonical inventory 为唯一当前能力事实源：

| Capability | Current status | 可说 | 不可说 |
|---|---|---|---|
| `saee.evaluate_agent_run` | `implemented` / local bounded | 声明式 trace metadata 与 evidence coverage 的确定性评估 | trace authenticated、长期状态连续性、部署授权 |
| `saee.evaluate_evidence` | `implemented` / local bounded | 封闭 evidence bundle 的要求检查 | 真实事件证明、认证或法律责任 |
| OTel-style candidate mapping | `implemented` / experimental | allowlisted synthetic mapping | OTLP ingestion、OTel conformance、可信 telemetry |
| general trace normalization | `partial` | 受限 repository-defined input | arbitrary Agent trace normalization |
| trusted trace conversion | `missing` | 未来研究问题 | 当前可信证据转换 |
| external identity binding | `missing` | 未来研究问题 | 当前外部身份认证 |
| delegation binding | `missing` | 未来研究问题 | 当前端到端委托链 |

### Chapter 13 — Research and Validation Agenda

- Problem validation：企业是否把连续信任视为独立问题；
- Decision-value validation：相比普通 observability review 是否提高判断质量；
- Cross-runtime validation：概念是否能跨 framework 保持一致；
- Evidence-cost validation：状态与证据成本是否可接受；
- Responsibility validation：输出是否帮助责任分配而不冒充责任裁决；
- Standards validation：是否应形成 profile / conformance language，而不是新协议。

### Chapter 14 — Commercial Hypotheses and Stop Rules

- 候选价值：扩大受控 autonomy envelope；
- 候选买方：Agent Platform、Security/IAM、AI Governance、Internal Audit；
- 当前没有 willingness-to-pay 或 customer adoption 证明；
- 若 observability/IAM 已能以更低成本解决同一问题，应停止重复建设；
- 若研究只增加报告长度而不改善决策，应停止；
- 若类别叙事回到 audit-first，应纠正。

## 7. Non-Claims 专章

白皮书必须集中声明：

- SAEE 不是 Agent runtime；
- SAEE 不是日志或 observability 平台；
- SAEE 不是 IAM、policy enforcement 或自动批准系统；
- 当前没有完整状态管理、可信记忆、自主治理或责任裁决；
- 当前没有客户验证或生产就绪证明；
- 网站、白皮书和 architecture diagram 不等于 capability implementation；
- future direction 不等于 roadmap commitment。

## 8. 计划图表

1. Agent task → long-running agency 的风险变化图；
2. Framework / Observability / IAM / Trust Interpretation 职责分层图；
3. Identity → Evidence → State → Governance 主架构图；
4. bounded state transition 图；
5. Current Capability / Future Direction 双栏矩阵；
6. standards composition map；
7. staged validation ladder。

禁止使用没有来源的市场规模数字、采用率数字或“行业领先”排名。

## 9. 一手资料锚点

- NIST, AI Agent Standards Initiative: https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative
- NIST NCCoE, Software and AI Agent Identity and Authorization Concept Paper: https://www.nccoe.nist.gov/sites/default/files/2026-02/accelerating-the-adoption-of-software-and-ai-agent-identity-and-authorization-concept-paper.pdf
- A2A Protocol Specification: https://github.com/a2aproject/A2A/blob/main/docs/specification.md
- MCP Authorization: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- OpenTelemetry Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/
- SPIFFE Workload API: https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
- LangGraph Persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- OpenAI Agents SDK Tracing: https://openai.github.io/openai-agents-python/tracing/
- SCITT Architecture, RFC 9943: https://www.rfc-editor.org/rfc/rfc9943.html

## 10. 完稿门槛

```text
SOURCE_TRACEABILITY_REQUIRED=true
CURRENT_FUTURE_SEPARATION_REQUIRED=true
CANONICAL_INVENTORY_RECHECK_REQUIRED=true
CUSTOMER_CLAIM_REQUIRES_EVIDENCE=true
PRODUCTION_CLAIM_ALLOWED=false
WHITEPAPER_PUBLICATION_AUTHORIZED=false
```

白皮书 v1.0 只有在所有当前能力表述与 canonical inventory 一致、所有未来架构标记清晰、所有外部事实具有一手来源且 Non-Claims 完整时，才能进入 publication review。
