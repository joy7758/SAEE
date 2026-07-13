# Integration Model

```text
Cloud Agent / Workflow
        ↓  transport only
MCP or bounded HTTP Adapter
        ↓
SAEE Capability Runtime
        ↓
Canonical Reliability / Evidence Services
        ↓
Bounded Assessment Result
```

平台负责 Agent、身份、授权、执行和基础设施。SAEE 只提供可靠性评估上下文。任何平台专属 Adapter 都必须委托现有 Capability Runtime，不能重写评估逻辑。

