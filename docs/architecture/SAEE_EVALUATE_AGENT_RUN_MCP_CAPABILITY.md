# SAEE internal `evaluate_rehearsal_run` MCP Capability（内部排演运行模型上下文协议能力）v0.1

状态：`implemented_local_in_memory_mcp_capability`。

## 1. 作用

该能力把 Phase（阶段）6.2 的内部 `evaluate_rehearsal_run` 加入现有固定本地 MCP Tool（模型上下文协议工具）注册表：

```text
MCP-like Tool Request
  ↓
evaluate_rehearsal_run handler
  ↓
Run schema + Trace/Evidence Export binding
  ↓
Existing Evidence Adequacy
  ↓
SUPPORTED / INSUFFICIENT_EVIDENCE / UNKNOWN
```

本地 Server 现在固定暴露两个只读 Tool：

1. `evaluate_evidence_adequacy`；
2. `evaluate_rehearsal_run`。

不支持动态 Tool 注册、插件、任意代码、URL、网络或外部工具执行。

## 2. 输入输出

输入必须包含完整且严格的 `rehearsal_run`。Handler 会验证 Run Schema、Trace
digest、Trace reference 和 Evidence Export binding。无效输入返回
`REJECTED_INPUT` 和稳定 reason code。

输出只包含：run/trace reference、claim type、assessment、profile result、缺失
字段、失败关系、reason codes、limitations 和 boundary statement。

## 3. 真实边界

```text
local_tool_registered=true
in_memory_invocation_available=true
standard_mcp_transport_available=false
public_endpoint_available=false
authentication_available=false
external_agent_connected=false
interoperability_validated=false
production_ready=false
```

因此这里的 “MCP Capability” 指机器可发现的固定本地 Tool 契约和 in-memory
调用实现，不代表官方 MCP SDK、stdio/network transport、Codex/Claude 实际连接
或公开服务已经完成。

## 4. 解释边界

`SUPPORTED` 只表示固定 Evidence Adequacy profile 满足。它不是任务成功、Agent
安全、合规、认证或部署许可。MCP 是传输/组合表面，不是信任权威。

## 5. 验证

```bash
python3 scripts/saee_evaluate_agent_run_mcp_smoke.py
python3 scripts/saee_local_mcp_prototype_smoke.py
```

推荐下一动作：审查 Phase 6.5 Design Partner protocol，使其演示新的真实本地
Rehearsal → Trace → Evidence → MCP 调用闭环；本任务不执行外部访谈。
