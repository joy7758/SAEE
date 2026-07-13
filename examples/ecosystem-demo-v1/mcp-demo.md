# MCP 本地演示链

```text
Synthetic Agent
  -> tools/list
  -> evaluate_agent_run
  -> CapabilityMCPAdapter
  -> Capability Runtime
  -> canonical Agent Reliability Service
  -> bounded result
```

## 发现

本地 MCP Adapter 暴露三个工具描述：`evaluate_agent_run`、`evaluate_evidence` 和 `rehearse_agent`。可见性不等于授权。

## 调用

Agent 选择 `evaluate_agent_run`，Adapter 将请求委托给 Capability Runtime。Runtime 再调用唯一的 canonical service。Demo 不直接导入 evaluator，也不复制业务逻辑。

## 解释

调用结果只能映射为 `CONTINUE`、`REPLAN`、`HUMAN_REVIEW_REQUIRED` 或 `STOP` 的决策上下文。调用者仍需遵守自己的授权、策略和沙盒边界。

## 明确边界

这是 **Local MCP demonstration only**。仓库没有启动外部 MCP Server，没有连接外部 Agent，也没有证明 Claude、OpenAI、云平台或任何 Marketplace 的兼容性。
