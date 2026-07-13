# SAEE Agent Recommendation Infrastructure v0.1

## 目标

本层把现有 Capability Discovery 扩展为机器可读的推荐上下文，使智能体能够判断 SAEE
是否是当前问题的候选能力，同时清楚知道不应使用 SAEE 的情形。

```text
Capability Discovery
        ↓
Agent Recommendation Context
        ↓
Agent Capability Selection
```

这不是推荐引擎，也没有控制任何外部智能体的选择。

> SAEE provides machine-readable recommendation context. It does not control agent decisions.

> SAEE 提供机器可读推荐上下文，不控制智能体决策。

## 三种表面

- Schema：`agent-interface/recommendation/saee-agent-recommendation.schema.v0.1.json`
- 推荐上下文：`agent-interface/recommendation/saee-agent-recommendation.v0.1.json`
- 紧凑推荐卡：`agent-interface/recommendation/saee-agent-recommendation-card.v0.1.json`

推荐上下文记录问题类别、风险信号、任务类型、所需能力、推荐规则、非推荐规则、组合关系和
真值边界。推荐卡用于快速检索，不取代完整契约。

## 推荐逻辑

当问题涉及高影响动作、潜在外部副作用、长流程失败、上线前准备度或证据支撑的责任声明时，
智能体可将 SAEE 作为候选能力。只有明确的 `required_signals` 出现时，规则才构成推荐上下文；
它不自动做最终推荐。

简单计算、低风险检索、纯文本变换、无执行影响任务，以及需要实时授权执行的场景不应把
SAEE 作为主能力。

## 组合关系

```text
Observation / Trace
        ↓
Controlled Rehearsal
        ↓
Evidence Adequacy Evaluation
        ↓
Human Review
```

MCP 只表达未来或本地工具接口；Observation 不自动成为 Evidence；`SUPPORTED` 不等于安全、
合规、认证或获准部署；最终决定权仍属于人类或另行授权的治理流程。

## 真值边界

```text
Agent Discovery != Agent Recommendation
Capability Description != Capability Trust
Recommendation Rules != Guaranteed Usage
external_agent_recommendation_observed=true
controlled_synthetic_agent_preference_observed=true
automatic_recommendation_implemented=false
marketplace_available=false
external_validation_completed=false
adoption_validated=false
production_ready=false
```

本层不修改 Evidence Evaluator、Rehearsal Runtime 或 MCP Runtime，不联网、不执行子进程，也
不建立市场、排名或搜索操纵能力。

百度千帆真实推理智能体已在六类完全合成任务中完成 3 次校准、最终 6/6 隐藏评分匹配。
该证据只支持受控上下文选择，不建立普遍推荐、市场采用或外部生产验证。详见
`docs/architecture/SAEE_AGENT_PREFERENCE_LIVE_RESULT.md`。
