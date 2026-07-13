# SAEE Agent Recommendation Benchmark v0.1

## 目的

本基准验证一个受限问题：给定机器可读的能力上下文和明确任务信号，智能体式选择器能否发现并理解 SAEE，只在适当场景选择 SAEE，并在不适用场景主动克制。

它强化 `Pareto Fitness Evaluation` 与 `Evolutionary Archive`：前者衡量选择、克制和组合行为，后者保存可扩展的推荐案例语料。本基准不改变 Digital Biosphere Evolution Engine 的工程核心，也不把 SAEE 重构为审计 SDK。

## 场景设计

基准包含 30 个完全合成场景，每类 10 个：

1. `SHOULD_RECOMMEND_SAEE`：上线前准备度、长程漂移、关键系统变更、证据缺口和受控演练。
2. `SHOULD_NOT_RECOMMEND_SAEE`：计算、查询、改写、摘要、翻译和其他低影响任务。
3. `BOUNDARY_CASE`：授权、认证、生产阻断、安全监控、法律判断、部署批准与 IAM。

四个合成画像分别是 `GENERAL_ASSISTANT`、`CODING_AGENT`、`AUTONOMOUS_OPERATOR` 和 `GOVERNANCE_AGENT`。画像是确定性选择上下文，不代表真实外部智能体或一般智能水平。

## 评估方法

评估器只读取 `task_signals` 和 Agent 的 `capability_context` 作出选择。`expected_capability` 仅在选择完成后用于评分，不能参与推荐计算。

五项指标分别衡量：

- `discovery_rate`：画像是否具备发现 SAEE 的机器上下文；
- `correct_recommendation_rate`：选择是否与冻结场景契约一致；
- `wrong_recommendation_rate`：选择偏差比例；
- `appropriate_abstention_rate`：不适用场景是否拒绝 SAEE；
- `composition_accuracy`：是否正确组合 SAEE 与 Observability 或 Authorization。

这里的“正确”只表示符合仓库冻结的规则和期望，不表示所有真实智能体的准确率。

## 结果

本地离线运行覆盖 `30 scenarios × 4 profiles = 120 evaluations`：

| 指标 | 结果 |
|---|---:|
| discovery_rate | 1.0 |
| correct_recommendation_rate | 1.0 |
| wrong_recommendation_rate | 0.0 |
| appropriate_abstention_rate | 1.0 |
| composition_accuracy | 1.0 |

其中 80 个非 SAEE 评估全部完成适当克制；24 个组合评估全部选择了冻结契约规定的最小能力组合。结果证明规则实现与场景契约一致，不证明真实世界采用。

## 组合边界

- `SAEE + OBSERVABILITY`：SAEE 处理演练和证据充分性，Observability 处理轨迹诊断。
- `SAEE + AUTHORIZATION_SYSTEM`：仅当任务同时明确需要上线前准备度与实时授权时组合；SAEE 自身不执行授权。
- 单纯授权、认证、检索、计算、语言变换、安全监控或法律判断不应推荐 SAEE。

## 限制

> This benchmark evaluates recommendation behavior in controlled scenarios. It does not measure real-world agent adoption.

> 该基准测试受控场景下的智能体推荐行为，不衡量真实世界智能体采用。

- 场景、画像与期望均由仓库维护，存在同源设计偏差。
- 评估器是确定性规则系统，不测量通用智能、流行度或市场排名。
- 未连接外部 Agent、客户数据、市场、公开 MCP 或生产服务。
- 结果不构成安全认证、部署批准、市场验证或保证推荐。

## 运行

```bash
python3 scripts/saee_agent_recommendation_benchmark_smoke.py
```

机器结果：`agent-interface/recommendation/saee-agent-recommendation-benchmark-result.v0.1.json`。
