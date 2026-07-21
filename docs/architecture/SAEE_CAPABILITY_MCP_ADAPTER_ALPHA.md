# SAEE MCP Adapter Alpha v0.1

## 定位

MCP 是运输适配层，不是新的 SAEE 产品或 evaluator：

```text
MCP Host -> local stdio Adapter -> Capability Runtime -> canonical SAEE service
```

Adapter 使用 MCP `2025-11-25` 的 JSON-RPC 生命周期和 Tool schema 形态，支持 `initialize`、`notifications/initialized`、`ping`、`tools/list` 与 `tools/call`。

## Tools

- `evaluate_rehearsal_run`：委托 Phase（阶段）10.2 Runtime（运行时）。
- `evaluate_evidence`：委托 Phase 10.2 Runtime。
- `rehearse_agent`：同样委托 Runtime，但返回 `CONTRACT_ONLY`。

每个 Tool 都要求调用者显式声明无客户数据、无网络请求、无外部世界动作。Tool annotations 仅描述只读意图，不能作为信任或授权证明。

## 边界

```text
local_stdio_adapter_available=true
runtime_delegation_required=true
direct_evaluator_access=false
network_listener_available=false
public_service=false
oauth_available=false
multi_tenant=false
external_agent_connected=false
external_mcp_interoperability_validated=false
production_ready=false
```

本地协议 smoke 不等于第三方 MCP Host 互操作、外部采用或生产可用。

## 启动

```bash
python3 scripts/saee_capability_mcp_stdio.py
```

配置：`agent-interface/mcp/saee-capability-mcp-stdio-config.v0.1.json`。
