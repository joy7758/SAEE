# SAEE 阿里云百炼生态进入策略

## Current Evidence

仓库没有 SAEE 与百炼的模型、Agent、Workflow、MCP 或高代码应用实测记录。因此当前状态必须是 `not_tested`、`not_integrated`。

## Candidate Surfaces

1. **Custom MCP Service**：把现有 SAEE MCP 工具定义映射为百炼自定义 MCP 候选包；
2. **Agent Workflow Assessment**：在智能体或工作流运行后提交固定评估输入；
3. **High-code Application**：在不复制评估逻辑的情况下调用 SAEE Capability Runtime；
4. **Application Component**：未来可将评估服务作为组件，但必须保留“评估不授权部署”。

百炼官方文档显示 Agent 2.0 将外部工具以 MCP 接入，平台也支持工作流、高代码应用和自定义 MCP 服务：

- <https://help.aliyun.com/zh/model-studio/new-single-agent-application>
- <https://help.aliyun.com/zh/model-studio/custom-mcp>
- <https://help.aliyun.com/zh/model-studio/application-introduction>

## Recommended Entry

先做离线 Schema/Tool 对齐审查，再设计最小合成互操作测试。未经测试，不把官方文档中的平台能力解释为 SAEE 兼容性。

```text
bailian_tested=false
bailian_integrated=false
official_support=false
marketplace_submission=false
production_ready=false
```

