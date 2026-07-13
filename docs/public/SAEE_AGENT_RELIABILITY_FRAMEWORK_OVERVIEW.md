# SAEE Agent Reliability Framework 总览

```text
Agent
  ↓
Rehearsal Runtime
  ↓
Observation
  ↓
Reliability Framework
  ↓
Evidence Evaluation
  ↓
Report
```

## 各层职责

1. **Rehearsal Runtime** 在本地合成世界中推进受控、多轮状态变化，不执行外部世界。
2. **Observation** 记录声明的输入、行为和状态变化；Observation 不自动成为 Evidence。
3. **Reliability Framework** 按固定契约评估执行、证据与边界可靠性。
4. **Evidence Evaluation** 检查一个明确责任声明所需的字段与关系是否充分。
5. **Report** 投影评估结果、缺失项、理由码和限制，不作自动部署决策。

## 组合边界

SAEE 提供可靠性上下文，而不是权力。它可以与 observability、authorization、policy 和 execution 系统组合，但不替代这些系统。

```text
SAEE provides reliability context, not authority.
SAEE 提供可靠性上下文，不提供授权权力。
```

Alpha 只覆盖本地、合成、非生产使用；不存在公网 API、生产 MCP 服务、客户验证或采用证明。

