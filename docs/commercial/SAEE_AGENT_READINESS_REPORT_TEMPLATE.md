# SAEE Agent Readiness Report

> 本模板用于生成本地、固定范围的智能体上线前可靠性评估报告。它不是认证、生产批准或安全保证。

## 1. Agent Overview（智能体概览）

- Agent 标识：`<agent_reference>`
- 版本：`<agent_version>`
- 工作流所有者：`<owner_reference>`
- 评估范围：`<local_synthetic_or_approved_scope>`

## 2. Workflow Tested（测试工作流）

- 业务目标：`<objective>`
- 关键步骤：`<steps>`
- 工具范围：`<allowed_tools>`
- 禁止动作：`<forbidden_actions>`

## 3. Scenario（场景）

- 场景 ID：`<scenario_id>`
- 环境：`<environment>`
- 成功条件：`<success_conditions>`
- 失败条件：`<failure_conditions>`

## 4. Execution Observation（执行观测）

列出事件、状态变化、工具调用、失败和终止原因。Observation 不自动构成 Evidence。

## 5. Reliability Findings（可靠性发现）

分别报告 Task、Recovery、Boundary、Evidence 和 Assessment Availability，不生成掩盖差异的总分。

## 6. Evidence Findings（证据发现）

- 支持的责任声明：`<supported_claims>`
- 证据不足的声明：`<insufficient_claims>`
- 缺失证据：`<missing_requirements>`
- 理由码：`<reason_codes>`

证据不足不等于系统不安全；证据满足 Profile 也不证明真实世界事件一定发生。

## 7. Risks（风险）

只描述当前场景观察到的风险信号和解释边界，不把参考估计描述为真实概率。

## 8. Recommendations（建议）

必须且只能选择一个：

- `CONTINUE`：在当前范围内继续下一轮验证；
- `REPLAN`：修订工作流、场景或证据计划后重测；
- `HUMAN_REVIEW_REQUIRED`：存在必须由授权人员判断的边界；
- `STOP`：当前证据或边界不支持继续本轮流程。

任何建议均不授权生产部署。

## Limitations（限制）

- 数据来源与授权边界；
- 未评估维度；
- 证据真实性、身份和授权的独立验证状态；
- 客户验证、市场验证和生产就绪状态。

