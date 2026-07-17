# SAEE 火山方舟生态进入策略

## Current Evidence

仓库已有火山方舟网关下 DeepSeek、GLM 和豆包模型的受控演练/可靠性研究记录，以及本地 Capability Runtime、MCP Adapter 和 HTTP Adapter。这证明供应商网关调用和本地评估链曾被观察，不证明方舟 Agent、AgentKit 或 MCP 已与 SAEE 集成。

## Candidate Surfaces

1. **Agent Tool**：把内部 `evaluate_rehearsal_run` 和 `evaluate_evidence` 映射为只读评估工具；
2. **MCP**：将现有本地 MCP 契约适配为方舟可消费的受控服务定义；
3. **HTTP Capability**：在独立认证、租户隔离和数据边界完成后评估 HTTP 接入；
4. **Evaluation Workflow**：在 Agent 发布前工作流中增加 SAEE Assessment 步骤。

火山方舟官方文档显示 Responses API 支持内置工具与 Function Calling，并列出 MCP/Remote MCP 路径：

- <https://www.volcengine.com/docs/82379/1958524?lang=zh>
- <https://www.volcengine.com/docs/82379/?lang=zh>

## Recommended Entry

先做纯本地 MCP tool schema 对齐和固定合成调用，随后才能设计方舟控制台/AgentKit 接入包。不得上传当前仓库、私有代码或密钥作为验证手段。

```text
ark_provider_observations_exist=true
official_ark_integration=false
ark_agent_adapter_validated=false
marketplace_submission=false
production_ready=false
```
