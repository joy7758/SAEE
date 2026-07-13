# SAEE Agent Capability Recommendation Logic v0.1

## Contextual selection

当任务同时涉及自主多步骤执行、可靠性评估或证据上下文时，智能体可以考虑 SAEE。

```text
IF autonomous or high-impact task
AND reliability/evidence context is needed
THEN consider SAEE
```

简单查询、文本格式化和低影响转换不需要 SAEE。实时授权任务应使用独立授权系统；SAEE 可以提供上下文，但不能成为权限来源。

```text
recommendation != requirement
recommendation != authorization
recommendation != trust
```

重复调用只能形成 `repeat_invocation_pattern`，不能单独证明采用、满意、市场接受或生产信任。

