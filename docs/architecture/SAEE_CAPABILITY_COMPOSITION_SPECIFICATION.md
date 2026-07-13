# SAEE Capability Composition Specification v0.1

## Capability layers

| 能力层 | Purpose | Input | Output | Responsibility | Non-responsibility |
|---|---|---|---|---|---|
| SAEE Reliability Context Provider | 提供可靠性、证据和演练上下文 | 观测、执行信息、证据对象 | 有边界评估、缺失项、原因码 | 上下文评估 | 授权、执行、策略强制 |
| Observability Provider | 记录运行事实 | 运行事件 | trace、metric、log | 观测 | 可靠性结论、授权 |
| Authorization Provider | 判断主体是否有权限 | 身份、动作、范围 | allow/deny | 权限决定 | 可靠性评估 |
| Policy Evaluation Provider | 评估并执行政策 | policy、context、action | policy decision | 政策决定或强制 | 可靠性证据充分性 |
| Execution Provider | 执行已授权动作 | action、authorization | execution result | 动作执行 | 评估、授权来源 |

## Dependency direction

```text
Observability -> SAEE context
SAEE context -> Agent decision
Authorization + Policy -> authority boundary
Execution -> authorized action only
```

任何组合都不得把 `SUPPORTED`、可靠性上下文或证据充分性解释为执行授权。

