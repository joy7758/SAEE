# SAEE 客户可控 Agent Adapter Contract v0.1

该契约只定义未来客户 Agent 接入前必须存在的机器可读边界，默认状态为：

```text
implementation_status=declared_disabled_not_implemented
enabled=false
human_activation_approved=false
customer_data_allowed=false
provider_network_allowed=false
external_world_actions_allowed=false
customer_agent_executed=false
```

它允许 Agent 和人工审查者提前判断 SAEE 需要哪些授权，但不实现 Codex、Claude Code、
LangGraph、CrewAI 或自定义客户 Agent 的连接。

任何未来激活都必须另建版本并提供：客户同意、合成/客户数据范围、凭据引用、成本上限、
沙箱、停止权、Provider 网络范围和独立回滚证据。不得通过修改当前实例中的 false 值来
启用 Adapter。

该契约强化 Agent World 的身份/意图边界和 Sandbox Development 的权限边界，不把 SAEE
变成通用 Agent Framework。

