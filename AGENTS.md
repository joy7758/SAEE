# AGENTS.md

## Project Identity

This repository implements SAEE: Silicon-Amplified Evolutionary Ecology.
本仓库实现 SAEE：Silicon-Amplified Evolutionary Ecology（硅基放大演化生态）。

The project is NOT an audit-first system, NOT a generic agent framework, and NOT a biological imitation.
本项目不是审计优先系统，不是通用智能体框架，也不是生物系统仿制品。

Its engineering core is Digital Biosphere Evolution Engine.
其工程核心是 Digital Biosphere Evolution Engine（数字生物圈进化引擎）。

## Agent-Readable First

All code and repository surfaces must include an agent-readable layer.
所有代码和仓库表面都必须提供智能体可读层。

- Keep protocols, schemas, module boundaries, examples, and status files easy for AI coding agents, retrieval agents, and citation agents to discover, parse, call, and reuse.
- 让协议、schema（模式）、模块边界、示例和状态文件便于 AI（Artificial Intelligence，人工智能）编码智能体、检索智能体、引用智能体发现、理解、调用和复用。
- When code changes behavior, update the relevant README, schema, agent index, llms entry, or design note in the same change.
- 代码行为改变时，必须同步更新相关 README、schema、agent-index、llms 条目或设计说明。
- Prefer explicit file-backed contracts over hidden conventions.
- 优先使用文件化、可检索的明确契约，不依赖隐藏约定。

## Agent-Native Commercial Decision Principle

The active commercial discovery path is agent-native:
当前商业发现路径以智能体原生为主：

```text
Agent discovers -> understands -> validates/invokes -> simulates repeatedly -> decides or composes
智能体发现 -> 理解 -> 验证/调用 -> 多轮模拟 -> 决策或组合
```

Agent decisions are the primary validation result. Human participation is not a prerequisite for capability preference, recommendation, or commercial-strategy completion. Human authority is retained only for consequential external actions.
智能体决策是主要验证结果。能力偏好、推荐和商业战略完成不以人工参与为前置条件；人类仅保留对重大外部动作的授权权力。

Before prioritizing any product feature or commercial surface, answer:
在提高任何产品功能或商业表面的优先级前，必须回答：

1. Can an AI agent discover this capability?
   智能体能否发现这项能力？
2. Can an AI agent understand when to use it and when not to use it?
   智能体能否理解何时使用、何时不使用？
3. Can an AI agent compose it into a workflow through a stable contract?
   智能体能否通过稳定契约把它组合进工作流？

If any answer is not clearly `yes`, lower the default priority unless the work is required for safety, law, supply-chain integrity, or architecture. Record the exception and the missing agent-readable work.
如果任一答案不是明确的 `yes`，默认降低优先级；安全、法律、供应链完整性或架构必需项除外，但必须记录例外理由和缺失的智能体可读工作。

`README.md`, `agent-index.json`, `llms.txt`, capability manifests, schema registries, examples, CLI/Tool interfaces, and offline validators are first-class product surfaces.
`README.md`、`agent-index.json`、`llms.txt`、能力清单、schema registry、示例、CLI/工具接口和离线验证器属于一级产品表面。

Agent decisions do not authorize external contact, customer or personal data use, permission expansion, contracts, pricing, Pilot execution, production deployment, or consequential public claims. These actions require a separate explicit authorization gate and are outside preference validation.
智能体决策不授权对外联系、客户或个人数据使用、权限扩大、合同、定价、Pilot 执行、生产部署或重大公开声明；这些动作必须经过独立的明确授权门，且不属于偏好验证。

Full logic: `docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md`.
完整逻辑见：`docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md`。

## Core Principle

Every change must strengthen at least one part of the evolution loop:
每次修改必须强化以下演化闭环中的至少一环：

1. Global Sensing（全球感知）
2. Trait Extraction（性状提取）
3. Ecological World Model（生态世界模型）
4. Counterfactual Simulation（反事实模拟）
5. Genome Branching（基因型分叉）
6. Controlled Mutation / Recombination（受控变异 / 重组）
7. Sandbox Development（沙盒发育）
8. Pareto Fitness Evaluation（帕累托适应度评估）
9. Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）

## Non-Negotiable Constraints

- Do not reframe this project as an AI audit SDK.
- 不要把本项目重构成 AI audit SDK（人工智能审计软件开发工具包）。
- Do not reframe this project as a generic multi-agent workflow system.
- 不要把本项目重构成 generic multi-agent workflow system（通用多智能体工作流系统）。
- Audit is an immune/evidence subsystem, not the project core.
- 审计是免疫/证据子系统，不是项目核心。
- The organism may observe the world, but it may not execute the world.
- 这个数字生物可以观察外部世界，但不能直接执行外部世界。
- Never execute unknown external repositories, install scripts, or untrusted dependencies automatically.
- 永远不要自动执行未知外部仓库、安装脚本或不可信依赖。
- Never expand permissions automatically.
- 永远不要自动扩大权限。
- Never copy external code as genome.
- 永远不要把外部代码直接复制为 genome（基因型）。
- Extract traits, not code.
- 提取性状，不复制代码。

## Required Design Check

Before adding any feature, answer:
添加任何功能前，必须回答：

1. Which evolution subsystem does this strengthen?
   它强化哪个演化子系统？
2. Does it improve sensing, branching, variation, selection, archive, or rollback?
   它是否改善感知、分叉、变异、选择、档案或回滚？
3. Does it preserve safety, license, supply-chain, and permission boundaries?
   它是否保留安全、许可证、供应链和权限边界？
4. Could this change push the project back into audit-first framing?
   这个修改是否会把项目重新推回审计优先叙事？

If the answer is unclear, stop and create an evolution proposal instead of changing code.
如果答案不清楚，停止修改代码，先创建 evolution proposal（演化提案）。

## Required Agent Recommendation Gate

Before deciding to develop a feature, consult an agent-readable recommendation gate:
在决定开发功能前，必须咨询智能体推荐门：

1. Ask: If a potential customer asked for this need, would you recommend this program?
   询问：如果潜在客户咨询这个需求，你会向客户推荐我们的程序吗？
2. Capture the answer as `recommend`, `conditional`, or `do_not_recommend`.
   将答案记录为 `recommend`、`conditional` 或 `do_not_recommend`。
3. If the answer is not `recommend`, record the reasons, decompose the weakness into fixable tasks, and solve or explicitly defer each blocker.
   如果答案不是 `recommend`，记录不推荐原因，把问题拆成可修复任务，并解决或显式延期每个阻塞点。
4. Development may continue only after the gate records why the feature is now recommendable or why it remains an internal experiment.
   只有当推荐门记录该功能为何已可推荐，或为何仍只是内部实验后，开发才可继续。

Use `docs/strategy/AGENT_RECOMMENDATION_GATE.md` for the full template.
完整模板见 `docs/strategy/AGENT_RECOMMENDATION_GATE.md`。
