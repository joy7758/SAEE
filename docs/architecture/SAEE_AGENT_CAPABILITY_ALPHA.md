# SAEE Agent Capability Alpha: `evaluate_agent_run` v0.1

状态：`implemented_local_offline_alpha`。

## 1. 能力

`evaluate_agent_run` 消费 Phase 6.1 的严格 Rehearsal Run：

```text
Rehearsal Run
  ↓ validate schema and Trace digest
Evidence Candidate Export
  ↓ verify Trace binding
Existing Evidence Adequacy Profile
  ↓
SUPPORTED / INSUFFICIENT_EVIDENCE
```

它复用 `AUTHORIZED_AGENT_ACTION` profile，不创建第二套评估逻辑。基线和工具
timeout 场景的授权证据关系满足 profile；指令冲突场景的 deny decision 必须返回
`INSUFFICIENT_EVIDENCE`。这并不表示 timeout 场景任务成功，也不表示拒绝场景
不安全。

## 2. 输出边界

允许输出：

- `SUPPORTED`；
- `INSUFFICIENT_EVIDENCE`；
- missing requirements；
- failed relationships；
- reason codes；
- limitations。

禁止解释为：

- `APPROVED`；
- `SAFE`；
- `COMPLIANT`；
- `CERTIFIED`；
- deployment authorization；
- task success。

## 3. 使用

```bash
python3 scripts/saee_evaluate_agent_run.py \
  --scenario agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json
```

验证：

```bash
python3 scripts/saee_agent_capability_alpha_smoke.py
```

## 4. 当前限制

该 Alpha 是本地 Python/CLI 能力，不是公开 API、标准 MCP Tool 或认证服务。
上游仍是固定内部合成 Agent；没有验证 Codex、Claude、LangGraph、CrewAI、百度
千帆、客户 Agent 或生产 Trace。

当前：

```text
evaluate_agent_run_available=true
agent_callable_runtime=true
public_api_available=false
public_mcp_available=false
real_external_agent_validated=false
customer_validated=false
production_ready=false
```

推荐下一项 PR：`SAEE Agent Readiness Scenario Benchmark v0.1`。
