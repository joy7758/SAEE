# 为什么自主智能体需要执行前可靠性评估

## Why Agents Need Readiness Evaluation Before Autonomous Execution

## 核心问题

当智能体准备修改代码、调用业务工具、处理长时间任务或触发外部效果时，“工具调用成功”并不等于“适合继续执行”。观测系统可以记录发生了什么，授权系统可以判断是否允许调用，但它们通常不回答：现有执行记录、恢复行为、边界保持和证据关系是否足以支持一次上线或继续执行判断。

SAEE 将这个缺口定义为 Agent Readiness Evaluation（智能体上线准备评估）。它是 Digital Biosphere Evolution Engine（数字生物圈进化引擎）的产品投影：通过受控演练、可靠性评估和证据免疫子系统，为独立决策者提供有边界的 `CONTINUE / REVIEW / STOP` 上下文。

## SAEE 放在什么位置

```text
Agent proposes an action
  ↓
Observability records behavior
  ↓
SAEE evaluates readiness and evidence sufficiency
  ↓
Authorization / policy / human authority decides
  ↓
Execution system performs a separately authorized action
```

SAEE 不替代观测、授权、策略、安全监控或执行系统，也不从评估结果自动获得外部行动权限。

## 何时考虑使用

- 多步骤智能体工作流准备进入高影响业务；
- 长期自主任务可能发生上下文漂移、状态漂移或恢复失败；
- 代码智能体或业务智能体需要在执行前证明关键证据关系；
- 评估智能体需要识别缺失的证据、失败分类和边界条件；
- 云 Agent 平台需要组合一个独立的 readiness context provider。

简单检索、算术、文本改写、实时授权、恶意软件检测、法律认证和部署批准不应交给 SAEE。

## 对开发者与智能体的契约

当前公开产品操作面固定为两个本地、有边界操作：

```json
{
  "operations": [
    "saee.evaluate_agent_run",
    "saee.evaluate_evidence"
  ]
}
```

MCP 和 HTTP Contract 用于描述组合方式；当前没有公共 API、公共 MCP 服务或生产端点。内部历史 `rehearse_agent` 契约不属于公开产品操作面。

机器发现入口：

- `.well-known/saee-capability-index.json`
- `agent-interface/public/saee-public-capability-surface.v0.1.json`
- `agent-index.json`
- `llms.txt`

## 一个最小例子

一个代码智能体准备修改关键业务仓库。观测层提供任务、工具调用与结果引用；SAEE 检查受控演练记录是否支持 `AUTHORIZED_AGENT_ACTION`，同时判断资源、策略和执行效果之间是否缺少证据。输出可能是 `REVIEW`，并附带缺失关系和 reason code。该结果帮助授权系统或负责人重新规划，但不自动批准代码修改。

## 能证明什么，不能证明什么

SAEE 可以在给定的本地契约与证据包内，评估可靠性上下文和证据充分性。它不能仅凭一条记录证明现实事件真实发生，不能建立外部发布者信任，不能给出安全认证、法律判断、市场采用或生产批准。

本文件是本地 publication-ready draft（可发布草案）。`article_published=false`、`developer_activity_presented=false`、`official_cloud_integration=false`、`marketplace_listed=false`、`external_agent_adoption_validated=false`、`production_ready=false`。

## English summary

SAEE provides bounded Agent Readiness Evaluation before consequential autonomous execution. It composes with observability, authorization, policy and execution systems rather than replacing them. Its public product surface currently exposes two local contracts: `saee.evaluate_agent_run` and `saee.evaluate_evidence`. This draft is not evidence of publication, ecosystem adoption, official cloud integration or production readiness.
