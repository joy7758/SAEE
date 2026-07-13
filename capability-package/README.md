# SAEE Capability Service Package v1.0

这是 SAEE 面向智能体 Runtime 的标准化能力契约包。默认界面语言为中文，字段、状态常量和协议标识保持机器稳定。

## 智能体先读

1. 读取 `manifest.json` 获取 Package 入口。
2. 读取 `capability-card.json` 判断何时使用和何时不用。
3. 读取 `openapi.yaml` 或 `mcp-tool.json` 理解输入输出。
4. 读取 `limitations.md`，不要把结果解释为认证、授权或部署批准。
5. 运行 `python3 scripts/saee_capability_service_package_smoke.py` 离线验证 Package。
6. 运行 `python3 scripts/saee_capability_runtime_demo.py` 体验统一本地调用层。
7. 使用 `python3 scripts/saee_capability_mcp_stdio.py` 启动本地 MCP stdio Adapter。
8. 使用 `python3 scripts/saee_capability_http_demo.py` 验证 localhost HTTP Adapter。
9. 读取 `../examples/agent-integrations/` 了解跨 Runtime 组合方式。
10. 读取 `../.well-known/saee-capability-index.json` 与 `../agent-interface/public/saee-public-capability-surface.v0.1.json` 获取仓库公开机器发现面。
11. 读取 `../agent-interface/release/saee-alpha-release-manifest.v0.1.json` 获取未发布 Alpha preparation 索引。
12. 读取 `../agent-interface/validation/saee-capability-truth-consistency-result.v0.1.json` 核对跨表面单一能力真值。

## 当前可用性

| 能力 | 当前状态 | 调用边界 |
|---|---|---|
| `evaluate_agent_run` | `implemented_local_offline_alpha` | 本地、只读、受控 SAEE Rehearsal Run |
| `evaluate_evidence` | `implemented_local_offline_prototype` | 本地、封闭证据包、固定剖面 |
| `rehearse_agent` | `contract_only` | 不可调用；仅描述未来接口 |

统一调用契约：

- Request：`../schemas/saee-capability-invocation-request.schema.v0.1.json`
- Response：`../schemas/saee-capability-invocation-response.schema.v0.1.json`
- Receipt：`../schemas/saee-capability-invocation-receipt.schema.v0.1.json`

## 组合方式

```text
Agent Runtime
    -> Controlled Rehearsal / Existing Run
    -> Observation
    -> SAEE Reliability Assessment
    -> Bounded Report
    -> Separately Authorized Decision
```

SAEE 与 Observability、Authorization、Policy Engine 和 Sandbox 互补，不替代这些系统。

## 项目身份边界

本 Package 是 SAEE 的外部可靠性能力投影。SAEE 工程核心仍是 `Digital Biosphere Evolution Engine`；证据充分性是免疫/证据子系统，不是项目核心的重新定义。

## 真值状态

```text
package_stage=local_contract_alpha
local_runtime_available=true
runtime_stage=local_alpha
local_stdio_mcp_adapter_available=true
local_http_adapter_available=true
network_api_available=false
standard_mcp_transport_available=false
public_mcp_available=false
repository_public_surface_prepared=true
alpha_preparation=true
public_release=false
publicly_deployed=false
external_agent_connected=false
customer_validated=false
adoption_validated=false
production_ready=false
```
