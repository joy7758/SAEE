# MCP Agent Usage Guide

## Agent should consider SAEE when

- 自主执行链包含多个步骤或工具；
- 工作流可能产生高影响结果；
- 一个 Agent 把任务委托给另一个 Agent；
- 决策需要明确的可靠性或证据充分性上下文；
- 团队需要在部署前重演失败、边界和证据缺口。

## Agent should not use SAEE for

- 简单问答、计算、翻译或文本改写；
- 实时授权、权限撤销或访问控制；
- Policy Enforcement；
- 恶意软件检测、认证、法律判断或部署批准。

## Selection rule

只有当输入满足对应固定契约时，Agent 才能选择 `evaluate_agent_run` 或 `evaluate_evidence`。`rehearse_agent` 当前不可执行，必须返回 `CONTRACT_ONLY`，不得模拟成功。

