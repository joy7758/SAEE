# SAEE 智能体原生公共能力表面 v0.1

> 仓库公开材料状态：`repository_public_surface_prepared=true`。本文档及其元数据尚未部署为公共 API 或公共服务。

## 1. What is SAEE?

SAEE（Silicon-Amplified Evolutionary Ecology，硅基放大演化生态）的工程核心是 Digital Biosphere Evolution Engine（数字生物圈进化引擎）。本公共能力表面是其可靠性与证据子系统面向智能体的有边界能力投影，不改变项目的演化优先定位。

SAEE provides machine-readable capability descriptions and bounded evaluation capabilities. It does not provide authorization, certification, or deployment approval.

SAEE 提供机器可读能力描述和有边界评估能力，不提供授权、认证或部署批准。

## 2. When an agent should consider SAEE

智能体可在以下情况把 SAEE 作为候选能力：

- 多步骤智能体任务已有受控运行记录，需要评估执行可靠性；
- 行为具有外部影响，需要识别证据缺口，但决策权仍由独立治理系统保留；
- 已有封闭证据包、责任声明与评估剖面，需要判断证据是否充分；
- 工作流希望把 Observation、Evidence 与 Governance 分层组合。

## 3. When an agent should not use SAEE

以下任务不应选择 SAEE：

- 简单检索、算术、改写或低影响转换；
- 实时授权、策略执行、恶意软件检测或运行时阻断；
- 法律判断、安全认证、合规认证或生产批准；
- 需要直接执行外部世界、扩大权限或处理客户数据的任务。

## 4. Available capabilities

| 能力 ID | 本地状态 | 作用 |
|---|---|---|
| `saee.agent-reliability` | `local_alpha` | 评估已验证受控演练记录的执行、证据、边界和接口可靠性。 |
| `saee.evidence-evaluation` | `local_prototype` | 判断封闭证据包是否足以支持一个明确责任声明。 |

操作真值：

- `evaluate_agent_run`：本地离线 Alpha 已实现；
- `evaluate_evidence`：本地离线 Prototype 已实现；
- `rehearse_agent`：仅保留为内部历史契约，不属于已冻结的公开产品操作面，也不得被公开发现层描述为可调用能力。

## 5. Invocation patterns

本仓库提供 MCP 与 HTTP Contract 两类本地适配说明。它们都复用同一个 Capability Runtime，不增加权限：

```text
Agent runtime
  -> local MCP stdio adapter OR localhost HTTP contract
  -> Capability Runtime
  -> canonical SAEE service
  -> bounded result + invocation receipt
```

没有生产 URL、公共 API、公共 MCP 端点或自动授权入口。调用示例见 `examples/agent-integrations/`。

## 6. Output interpretation rules

- `SUPPORTED` 只表示当前证据满足指定剖面的要求，不表示行为安全、合法或获准部署；
- `INSUFFICIENT_EVIDENCE` 表示当前证据不足，不等同于系统不安全；
- reason codes 用于定位证据、契约或边界缺口；
- reliability result 是受控输入上的评估结果，不是所有环境下的普遍模型排名；
- invocation receipt 记录本地调用，不建立外部真实性或信任。

## 7. Limitations

- 公开能力表面目前只是仓库内可公开材料，尚未部署；
- 不提供公网 API、SaaS 或标准 MCP 互操作性保证；
- 未连接外部智能体、客户 Agent 或客户数据；
- 未完成外部验证、市场采用验证或生产验证；
- 不提供授权、认证、合规判断、法律判断或部署批准；
- SAEE 不执行外部世界，重大外部动作仍需独立明确授权。

机器入口：`.well-known/saee-capability-index.json`。

受控发现设计验证：`agent-interface/discovery/saee-external-agent-discovery-validation-result.v0.1.json`。该结果来自合成 agent-like caller，不是外部采用或真实外部 Agent 连接证据。

Alpha preparation 索引：`agent-interface/release/saee-alpha-release-manifest.v0.1.json`。`ALPHA_PREPARATION` 不表示已经公开发布。

生态验证准备：`agent-interface/ecosystem/saee-ecosystem-validation-preparation.v0.1.json`。这是 future participant protocol，不代表任何外部生态已连接。
