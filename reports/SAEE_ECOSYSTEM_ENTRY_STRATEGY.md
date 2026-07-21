# SAEE Ecosystem Entry Strategy

中文名称：SAEE 生态入口战略<br>
版本：`v1.0`<br>
阶段：`PHASE_1_CATEGORY_POSITIONING`

```text
ECOSYSTEM_ENTRY_STATUS=STRATEGY_ONLY
PARTNERSHIP_ESTABLISHED=false
OFFICIAL_INTEGRATION_ESTABLISHED=false
NEW_MCP_IMPLEMENTATION=false
NEW_PRODUCTION_CAPABILITY=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

## 1. 战略目标

让 Agent Framework、Cloud Agent Platform 和 Developer Ecosystem 逐渐形成共同认知：长期、多 Agent、自主运行需要一个连接 Identity、Execution Evidence、State Continuity 与 Governance 的可信基础设施层，SAEE 正在研究和建设该方向。

生态入口不是“尽快接入更多平台”，而是用统一类别语言、可复核当前能力、机器可读边界和合作研究问题，降低生态伙伴理解与评估 SAEE 的成本。

## 2. 生态对象

### 2.1 Agent Framework

典型关注：orchestration、handoff、checkpoint、memory、durable execution、tracing。

SAEE 入口问题：

- checkpoint 是否能证明身份和目标连续性；
- handoff 是否保留委托、上下文和责任；
- memory 如何标记来源、时效、冲突和撤销；
- 跨 framework 证据能否形成共同可信语义。

合作材料：framework-specific conceptual crosswalk、bounded evidence example、Current/Future matrix、non-claims。

### 2.2 Cloud Agent Platform

典型关注：tenant、IAM、deployment、observability、policy、marketplace 和 enterprise operations。

SAEE 入口问题：

- Agent 身份与 cloud workload identity 如何关联；
- 委托和权限如何随长任务传播、过期和撤销；
- telemetry 何时可以支持 evidence claim；
- 平台责任与企业责任如何保持可证明边界。

合作材料：architecture brief、identity/delegation research questions、evidence readiness sample、deployment non-claims。

### 2.3 Developer Ecosystem

典型关注：能否发现、理解、调用、验证和组合。

SAEE 入口：

- 清晰 README 与 Architecture Overview；
- `/for-agents`、`llms.txt`、agent index 与 canonical manifest；
- 最小本地 current-capability example；
- Future Direction research notes；
- source-backed technical articles。

## 3. 四类生态入口

### Entry A — Category Content

- 官网类别首页；
- SAEE Trust Infrastructure Whitepaper；
- Architecture Overview；
- “Why Observability Is Not Trust” 技术文章；
- “Checkpoint Is Not State Integrity” 技术文章；
- “Agent Identity Is Not Agent Authorization” 技术文章。

目标：先让生态理解问题，再讨论集成。

### Entry B — Agent-Readable Discovery

- 保留当前 MCP operation IDs 和实现，不在本阶段扩展；
- 通过现有 `llms.txt`、agent index、manifest 和 `/for-agents` 指向统一类别叙事；
- 每个 entry 明确 current operation、stability、evidence、non-claims；
- future direction 只链接研究文档，不暴露成可调用 operation。

### Entry C — Validation Materials

- current capability evidence packet；
- synthetic/local validation 边界；
- claim-to-evidence matrix；
- partner self-assessment checklist；
- negative cases：unauthenticated trace、missing delegation、stale memory、goal change without authority。

本阶段只设计材料，不创建新的 capability、Schema 或 MCP。

### Entry D — Collaboration Brief

合作入口应从“共同研究一个可验证缺口”开始，而不是直接宣称集成：

1. partner problem statement；
2. current platform responsibility；
3. SAEE research responsibility；
4. shared evidence question；
5. non-claims；
6. success/failure criteria；
7. consequential action gate。

## 4. MCP 入口原则

MCP 是生态发现和受限调用入口之一，不是 SAEE 类别本身。

当前阶段：

- 保留现有 `saee.evaluate_agent_run` 和 `saee.evaluate_evidence`；
- 不修改 MCP implementation；
- 不新增 Identity、State、Memory 或 Governance 工具；
- 不通过命名暗示完整长期可信基础设施已实现；
- 网站和文档可以解释未来组合关系，但必须指向 canonical current capability。

未来任何 MCP 变化都需要独立 capability inventory、duplicate-build check、Recommendation Gate、Schema review 和 human authorization。

## 5. 开发者体验战略

Phase 1 的开发者体验不是更复杂的 SDK，而是更短的理解路径：

```text
Discover category
  → Understand boundary
  → Inspect current capability
  → Run bounded local example
  → Review evidence and non-claims
  → Explore future research
```

每一步都应回答：

- 它是什么；
- 何时使用；
- 何时不使用；
- 当前是否实现；
- 结果能证明什么；
- 结果不能授权什么。

## 6. 技术内容计划

### Category-defining articles

1. `The Missing Trust Layer for Long-Running Multi-Agent Systems`；
2. `Why Agent Frameworks Cannot Prove Agency Continuity`；
3. `Observability Shows Events; Trust Requires Evidence Relationships`；
4. `Agent Memory Needs Provenance, Expiry and Revocation`；
5. `From Access Tokens to Verifiable Delegation Chains`；
6. `Recommendation Is Not Authorization`。

### Standards crosswalk articles

1. A2A and long-running task state；
2. MCP authorization and resource binding；
3. OpenTelemetry as evidence input, not evidence authority；
4. SPIFFE workload identity and Agent Identity boundary；
5. SCITT transparency receipts as a reusable primitive；
6. NIST Agent Identity and Authorization research questions。

所有文章都优先引用标准、官方文档和研究论文，不使用无来源的行业数字。

## 7. 合作材料包

```text
00_CATEGORY_ONE_PAGER
01_ARCHITECTURE_OVERVIEW
02_CURRENT_VS_FUTURE_MATRIX
03_STANDARDS_COMPOSITION_MAP
04_CURRENT_CAPABILITY_EVIDENCE_PACKET
05_PARTNER_RESEARCH_QUESTIONNAIRE
06_NON_CLAIMS_AND_AUTHORITY_BOUNDARY
```

材料包只用于 discovery、technical review 和 research conversation。它不等于 partnership、official integration、pilot authorization 或 customer validation。

## 8. 分阶段进入路线

### Stage 1 — Category Legibility

- 官网、Whitepaper Outline、Market Positioning、GitHub Narrative 完成；
- 人类和 Agent 都能复述 category 与 Current/Future 边界；
- 没有新增 product capability。

### Stage 2 — Ecosystem Problem Validation

- 让 framework/cloud/developer Agent 审阅问题定义；
- 记录 `recommend / conditional / do_not_recommend` 与原因；
- 验证该问题是否独立于 observability、IAM 和 framework persistence；
- 不进行对外 consequential action，除非单独授权。

### Stage 3 — Standards Composition Research

- 对 A2A、MCP、OpenTelemetry、SPIFFE、OAuth/GNAP、SCITT 做角色 crosswalk；
- 找出可以复用的标准和真正缺失的解释关系；
- 若现有标准已经解决，不重复建设。

### Stage 4 — Bounded Ecosystem Experiment

只有在问题和组合价值被证明后，才能提出独立实验建议。实验不得自动升级为 official integration、product capability 或 production claim。

## 9. 生态成功指标

- framework/cloud/developer 三类对象都能准确描述 SAEE 不替代什么；
- agent-readable entry 可以发现 category、current capabilities 和 future non-claims；
- technical article 产生高质量引用、讨论或 independently reproducible review；
- 至少出现一个明确的 ecosystem problem-fit signal；
- 没有将平台名称、文档引用或一次会谈写成合作、认证或采用；
- 没有因生态入口建设修改主线 code、MCP 或 capability facts。

## 10. Agent Recommendation Gate

```text
RECOMMEND_CATEGORY_AND_PROBLEM_RESEARCH=recommend
RECOMMEND_CURRENT_BOUNDED_LOCAL_EVALUATION=conditional
RECOMMEND_COMPLETE_TRUST_INFRASTRUCTURE_PRODUCT=do_not_recommend
```

不推荐完整产品的原因：external identity binding、delegation binding、trusted trace conversion、longitudinal state continuity、trusted memory、multi-agent governance 和 responsibility determination 均未实现或未验证。

## 11. Stop Rules

- 若生态入口被解释为 production integration，停止；
- 若 partner logo 被用来暗示合作，停止；
- 若 future capability 被加入 current operation list，停止；
- 若为了 category positioning 修改 MCP 或主线 runtime，停止；
- 若市场叙事开始以 audit-first 取代 SAEE engineering core，纠正；
- 若 Goal Integrity 副线被重新激活为产品扩张，保持 `GOAL_INTEGRITY_SECONDARY_LANE=STOPPED`。
