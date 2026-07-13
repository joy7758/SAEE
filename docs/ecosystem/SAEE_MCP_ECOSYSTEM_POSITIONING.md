# SAEE MCP Ecosystem Positioning

## Role Separation

```text
MCP = transport and discovery layer
SAEE = reliability capability provider
Authorization system = permission authority
```

MCP 让 Agent 枚举并调用工具；SAEE 对固定输入进行受控演练结果评估或证据充分性评估。MCP 的可调用性不证明能力可信、输入真实、调用获授权或结果可批准部署。

## Existing Surface

- MCP 设计：`docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md`
- Tool 定义：`capability-package/mcp-tool.json`
- 本地 Adapter：`agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json`
- 本地验证：`python3 scripts/saee_capability_mcp_adapter_smoke.py`

Global Agent Platforms 可以通过 MCP-backed tools 消费类似能力。例如 OpenAI Agents SDK 官方文档提供 MCP server/tool 配置，但 SAEE 尚未完成该 SDK 的互操作测试：<https://openai.github.io/openai-agents-python/mcp/>

## Priority

MCP 是优先级最高的生态入口，因为它最大化复用现有本地契约并降低平台专属适配。但下一步仍应是离线 Entry Package 和受控互操作测试，而不是公网 MCP 服务。

```text
mcp_local_adapter=true
remote_mcp_service=false
cross_vendor_interoperability_validated=false
mcp_trust_authority=false
marketplace_listed=false
production_ready=false
```

