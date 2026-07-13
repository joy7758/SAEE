# SAEE Agent Rehearsal Runtime MVP v0.1

状态：`implemented_local_controlled_synthetic_agent_runtime`。

## 1. 目标

本 MVP 恢复 SAEE 的第一产品入口：让一个 Agent 在版本化、隔离、无外部副作用
的场景中实际运行，生成 Trace，并导出与 Trace 摘要绑定的 Evidence Candidate。

```text
Scenario Contract
  ↓
Fixed Internal Agent Adapter
  ↓
In-memory Controlled Environment
  ↓
Trace Collector
  ↓
Evidence Candidate Export
```

它强化 `Ecological World Model`、`Counterfactual Simulation`、`Sandbox
Development`、`Pareto Fitness Evaluation` 和 `Evolutionary Archive / Rollback
Immune System` 之间的运行依赖，不改变 LCR-REDS 或 SAEE-MP。

## 2. 当前真正执行了什么

- `run_task()` 读取 allowlist 内的严格 Scenario；
- 仓库内固定策略 Agent 读取任务与 policy；
- Agent 选择拒绝、调用内存工具、处理工具成功或 timeout；
- Runtime 生成顺序化 Trace 和稳定摘要；
- Evidence Export 绑定 action、policy decision 与 Trace digest；
- CLI 对有效场景返回 0，对越界/无效输入返回 2。

首批场景：

1. baseline metadata inspection；
2. tool timeout and abstention；
3. instruction conflict and refusal。

## 3. 没有执行什么

- 没有调用真实 Codex、Claude、LangGraph、CrewAI 或百度千帆；
- 没有网络、subprocess、插件、动态 import、文件写入或未知代码；
- 没有执行外部工具或生产动作；
- 没有使用客户数据；
- 没有把 Trace 自动升级为 Evidence；
- 没有执行 Evidence Adequacy、Risk、Readiness 或部署决策。

因此：

```text
local_rehearsal_runtime_executed=true
fixed_internal_agent_executed=true
real_external_agent_executed=false
evidence_established=false
evaluate_agent_run_available=false
production_ready=false
```

## 4. Evidence Export 边界

Evidence Export 是可供下一层消费的候选包：它包含 action、policy decision、
Trace reference 和 digest。它不证明事件真实发生、身份被外部验证或授权有效，
也不是 Adequacy 结果。

Phase 6.2 才可以增加 `evaluate_agent_run`，并且只能复用现有 Evidence Adequacy
能力评估这些候选关系。`SUPPORTED` 仍不得解释为安全、合规或部署批准。

## 5. 使用

```bash
python3 scripts/saee_agent_rehearsal.py \
  --scenario agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json
```

验证：

```bash
python3 scripts/saee_agent_rehearsal_runtime_smoke.py
```

## 6. 下一边界

推荐下一项 PR：`SAEE Agent Capability Alpha: evaluate_agent_run v0.1`。

该 Alpha 之前不得连接真实外部 Agent。真实外部 Agent 接入必须另设 provider、
credential、cost、privacy、sandbox 和 human authorization gate。
