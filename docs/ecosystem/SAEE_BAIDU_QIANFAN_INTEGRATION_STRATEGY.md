# SAEE 百度千帆生态进入策略

## Current Evidence

仓库已有千帆真实模型在完全合成世界中的受控演练、AppBuilder/函数托管相关本地桥接研究和提供商数据边界记录。这些证据不证明千帆原生 MCP 已兼容 SAEE，也不证明任何官方集成。

## Candidate Surfaces

1. **Agent Evaluation Service**：由 AppBuilder Agent 或 Workflow 在发布前调用 SAEE 的固定评估契约；
2. **Capability Tool**：将只读评估操作表达为 MCP 组件；
3. **Developer Workflow**：通过本地 SDK/CLI 生成评估输入，再消费结构化结果；
4. **Workflow Component**：在固定工作流中显式传递输入输出，不由模型推断部署授权。

千帆官方文档显示 AppBuilder 支持自主规划 Agent、工作流 Agent、SDK 和 MCP 组件/Server 路径：

- <https://cloud.baidu.com/doc/qianfan-docs/s/tm983fszw>
- <https://cloud.baidu.com/doc/qianfan/s/0mh4stqhc>
- <https://cloud.baidu.com/doc/qianfan/s/zmh4stqex>

## Recommended Entry

优先复用现有受控千帆测试经验，新增“SAEE MCP 工具契约能否被 AppBuilder 正确发现、传参和解释”的本地模拟；在此之前不得声称支持千帆。

```text
qianfan_controlled_model_evidence=true
qianfan_native_mcp_support_for_saee_proven=false
official_qianfan_integration=false
marketplace_submission=false
production_ready=false
```

