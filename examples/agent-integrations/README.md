# SAEE Agent Ecosystem Integration Examples Alpha

本目录只展示本地集成方式：MCP stdio、localhost HTTP 和零依赖通用 Framework Adapter。它不连接外部 Agent，不声明框架支持、采用、排名或生产部署。

先读取 `../../capability-package/manifest.json`，再根据 Runtime 选择以下 Transport：

- `mcp-client-example/`：本地 stdio Tool discovery 与调用。
- `http-agent-example/`：`127.0.0.1` HTTP 调用。
- `framework-agent-example/`：依赖注入式 Agent 决策点。

