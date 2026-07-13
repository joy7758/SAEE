# SAEE Capability Composition Model v0.1

## Composition

```text
Agent Task
  + Observability records
  + SAEE Reliability / Evidence Context
  + Authorization System
  + Policy Engine
  -> Agent Decision
```

SAEE 的角色是 `decision_context_provider`。它接收受控执行信息、观测引用或证据对象，输出可靠性评估、证据充分性、缺失要求、原因码和限制。

SAEE 不提供：

- 身份和权限；
- 外部执行；
- 实时阻断；
- 安全监控或认证；
- 部署批准。

因此：

```text
context != authority
composition != replacement
discovery != mandatory use
```

