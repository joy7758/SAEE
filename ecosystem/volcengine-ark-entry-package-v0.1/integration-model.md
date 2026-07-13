# Volcengine Ark Integration Model

```text
Ark Agent / Workflow
       ↓ potential Function Calling, MCP, or HTTP
SAEE Transport Adapter
       ↓ mandatory delegation
SAEE Capability Runtime
       ↓
Reliability / Evidence Result
```

方舟负责模型、Agent、身份、工具授权和执行环境；SAEE 只提供可靠性上下文。任何正式适配器都必须调用现有 Capability Runtime，不得直接导入底层 Evaluator。

