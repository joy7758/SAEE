# MCP Integration Flow

```text
Agent
  ↓
MCP Discovery
  ↓
SAEE Tool Selection
  ↓
Capability Runtime
  ↓
Reliability Context
  ↓
Agent Decision or Abstention
```

MCP Adapter 只把工具调用委托给 Capability Runtime。Agent 必须读取结果中的 reason codes、missing evidence 和 limitations。

```text
result != authorization
tool availability != permission
profile satisfied != event proved
```

