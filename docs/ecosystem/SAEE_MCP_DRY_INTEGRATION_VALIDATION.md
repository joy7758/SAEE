# SAEE MCP 生态干式集成验证 v0.1

## 目标

本验证检查 SAEE 的 MCP 生态入口材料能否驱动一个确定性的本地合成智能体，完成能力发现、工具选择、MCP Adapter 调用、Capability Runtime 委托、结果解释和边界检查。它强化数字生物圈进化闭环中的 Sandbox Development（沙盒发育）、Pareto Fitness Evaluation（帕累托适应度评估）和 Evolutionary Archive（演化档案），不改变 SAEE 的核心架构。

> This validation verifies SAEE MCP integration flow internally using synthetic agents. It does not establish external MCP compatibility or adoption.

> 该验证使用合成智能体验证 SAEE MCP 调用流程，不代表外部 MCP 兼容或生态采用。

## 验证链

```text
Synthetic Agent
  -> MCP Entry Package discovery
  -> bounded tool selection
  -> CapabilityMCPAdapter
  -> Capability Runtime
  -> canonical SAEE service
  -> bounded interpretation
  -> truth-boundary check
```

控制器只通过 `CapabilityMCPAdapter` 调用能力。Adapter 再进入唯一的 Capability Runtime；控制器不直接导入 Evidence Adequacy evaluator、Agent Reliability evaluator 或 Capability Router。
场景输入引用使用固定 allowlist；非清单路径在读取前失败关闭，避免把本地 secret 或任意文件变成测试载荷。

## 场景与预期

| 场景 | 选择 | 预期结果 |
|---|---|---|
| `RELIABILITY_ASSESSMENT_TASK` | `evaluate_agent_run` | `SUCCESS`，仅解释为有边界的可靠性上下文 |
| `EVIDENCE_EVALUATION_TASK` | `evaluate_evidence` | `SUCCESS`，`SUPPORTED` 仅表示满足剖面要求 |
| `REHEARSAL_REQUEST` | `rehearse_agent` | `CONTRACT_ONLY` |
| `AUTHORIZATION_TASK` | 不选择 SAEE | 边界拒绝 |
| `DEPLOYMENT_APPROVAL_TASK` | 不选择 SAEE | 边界拒绝 |
| `SIMPLE_QUERY_TASK` | 不调用 SAEE | 主动弃用 |

`SUPPORTED` 不等于 `APPROVED`、`CERTIFIED`、`SAFE` 或 `DEPLOYED`。本验证也不记录提示词、思维链、私有模型状态或任何 secret。

## 运行

```bash
python3 scripts/saee_mcp_ecosystem_dry_integration_smoke.py
```

机器可读结果位于 `agent-interface/mcp/saee-mcp-dry-integration-result.v0.1.json`，每个 trace 都绑定发现、选择、Adapter 调用、Runtime 委托、结果类型和真值边界。

## 限制

- 智能体是固定规则的本地合成选择器，不是外部 MCP Client。
- 没有启动公网 MCP Server，没有连接 Claude Desktop、OpenAI、云平台或外部 Agent。
- 本地通过不代表生态兼容、官方支持、市场采用、授权能力或生产就绪。
- `rehearse_agent` 仍是契约占位能力，未在本任务中扩展运行时。

## 状态

```text
mcp_dry_integration_validation=true
synthetic_agent_only=true
external_agents_connected=false
external_mcp_connection=false
official_support=false
marketplace_listed=false
production_ready=false
```
