# SAEE MCP Ecosystem Entry Package v1

真实生态验证入口门：`real_validation_entry_gate_reference=agent-interface/ecosystem/saee-real-ecosystem-validation-entry-decision.v0.1.json`。当前结论为 `HOLD`；该引用不授权外联或执行。

内部智能体 Pilot 计划：`internal_agent_pilot_reference=agent-interface/pilot/saee-internal-agent-pilot-plan.v0.1.json`。当前已有内部执行结果，但不构成外部验证。

内部执行结果：`internal_agent_pilot_execution_reference=agent-interface/pilot/saee-internal-agent-pilot-execution-result.v1.0.json`。三次真实内部 Codex 运行已记录，仍保持 `external_validation=false`。

本包用于让 MCP 客户端、Agent Runtime 和生态评审者发现并理解 SAEE 的本地可靠性能力。

## Purpose

```text
Agent reliability assessment capability
```

## Package Contents

- `capability-card.json`：能力和真值边界；
- `mcp-tools.json`：三个工具及实现状态；
- `agent-usage-guide.md`：何时使用和弃权；
- `integration-flow.md`：发现、调用和解释链；
- `limitations.md`：未完成能力。

本包不启动服务、不注册公网工具、不建立授权或外部互操作证明。

五分钟本地生态 Demo：`examples/ecosystem-demo-v1/README.md`。该引用只帮助开发者和评审智能体理解 SAEE，不代表外部集成或采用。
