# SAEE Agent Readiness Benchmark v0.1

状态：`implemented_local_20_case_synthetic_benchmark`。

## 1. 目的

本 Benchmark 验证 SAEE 的 `Scenario → Rehearsal → Trace → Evidence Candidate
→ evaluate_agent_run` 闭环不只适用于单一样例。首批固定为 20 个本地合成
场景：

| 类别 | 数量 | 预期行为 |
|---|---:|---|
| Baseline | 4 | 完成只读任务 |
| Context Drift | 4 | 检测上下文不足并弃权 |
| Tool Failure | 4 | 检测工具异常并弃权 |
| Instruction Conflict | 4 | 拒绝越界指令 |
| Adversarial Input | 4 | 拒绝绕过策略、摘要或权限边界 |

每个 case 都实际执行固定内部策略 Agent，而不是仅做 JSON 字段检查。

## 2. 指标边界

Benchmark 输出：

- category coverage；
- completed / abstained / refused；
- `SUPPORTED` / `INSUFFICIENT_EVIDENCE`；
- expectation match；
- denied actions incorrectly supported；
- profile support rate。

`profile_support_rate` 只描述固定 Evidence Adequacy profile 在这组合成 case 中
的满足比例。它不是 Agent Accuracy、任务成功率、真实失败率或部署风险概率。

工具故障和上下文漂移 case 可以得到 `SUPPORTED`，因为动作与 allow policy 的
证据关系完整；与此同时 `task_success_established=false`。这正是 SAEE 区分
“证据充分性”和“任务表现”的必要边界。

## 3. 使用

```bash
python3 scripts/saee_agent_readiness_benchmark.py
python3 scripts/saee_agent_readiness_benchmark_smoke.py
```

## 4. 限制

- 全部 case 使用固定内部合成 Agent；
- 没有真实 Codex、Claude、LangGraph、CrewAI、百度千帆或客户 Agent；
- 没有网络、客户数据、生产工具或外部执行；
- 20 场景覆盖不等于外部泛化、市场验证或生产 readiness；
- Benchmark 不作安全、合规、认证或部署批准。

推荐下一项 PR：`SAEE evaluate_agent_run MCP Capability v0.1`。
