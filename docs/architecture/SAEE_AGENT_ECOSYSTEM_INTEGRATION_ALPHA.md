# SAEE Agent Ecosystem Integration Examples Alpha v0.1

> SAEE integration examples demonstrate capability invocation patterns. They do not demonstrate external adoption or production deployment.

> SAEE 集成示例展示能力调用方式，不代表外部采用或生产部署。

## 集成架构

```text
Local Agent Runtime
-> Capability Discovery
-> MCP stdio or localhost HTTP
-> Capability Runtime
-> Reliability / Evidence Result
-> Interpretation Contract
```

三个示例均为仓库内本地模式：MCP、HTTP、通用 Framework。没有真实客户 Agent、外部 Framework 包、Marketplace 或公网服务。

## 解释规则

- `SUPPORTED`：固定剖面要求满足；不表示 approved、certified、safe、deployed 或 authorization granted。
- `INSUFFICIENT_EVIDENCE`：存在缺失证据或不完整关系，应 `REPLAN`、人工复核或停止。
- `REJECTED_INPUT`：没有完成有效评估，应 `STOP`。
- `CONTRACT_ONLY`：能力没有实现，应 `STOP`。

本阶段评估 Discovery、Invocation、Interpretation 和 Boundary，不评估 Agent intelligence，不排名 Framework 或模型。

