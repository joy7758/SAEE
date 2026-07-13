# SAEE Rehearsal Scenario Library v0.2 智能体推荐门

## 推荐问题

如果潜在客户需要在不触碰真实业务系统的前提下，演练代码发布、研究、运营、客服和安全智能体的典型失败模式，我会推荐当前程序吗？

## 结论

`recommend`

仅推荐为一个本地、合成、无外部副作用的场景契约库，用于智能体发现、选择和组合演练场景。

## 推荐理由

- 五类场景覆盖不同工作目标、状态、工具、约束、风险和证据目标；
- 全部场景可被机器读取并投影到同一 Stateful Agent Rehearsal Runtime 输入接口；
- 代码发布场景继续由已验证的 Release World 执行；另外四类场景明确保留工具实现缺口，不伪装成已执行；
- 不增加 Runtime、Evaluator、排行榜或生产能力；
- 所有场景保持 `external_world_actions=false`、`customer_data=false` 和 `production_ready=false`。

## 不推荐范围与处理

| 不推荐原因 | 处理 |
|---|---|
| Business 与 Customer 场景原先无合成工具实现 | Phase 7.0 通过共用 Operations Adapter 补齐，保持外部效果为 false |
| Research Evidence Review 已有专用研究世界 | 独立 Study 仍必须明确真实运行次数与失败，不从工具实现推断结果 |
| Security Boundary 已有专用只读安全世界 | 独立 Study 仍必须明确真实运行次数与失败，不把边界观察写成安全认证 |
| 场景库不是风险概率模型 | 每个风险都声明 `not_probability_measurement=true` |
| 场景数量不足以代表行业覆盖 | 文档明确 v0.2 仅为五类高价值起始场景 |

上述限制不阻止其作为内部场景契约库被推荐，但阻止任何生产、认证、市场验证或模型排名主张。

## Agent-Native 检查

1. 发现：通过 schema、固定目录、`agent-index.json`、`llms.txt` 和 Capability/Registry 引用发现。
2. 理解：每个场景明确列出目标、世界、工具、约束、注入风险、观察与证据目标。
3. 组合：每个场景都可稳定投影为 `task + environment_state + available_tools`；这不等于其专用工具已经实现。

## 演化设计检查

1. 强化：Ecological World Model、Counterfactual Simulation、Sandbox Development、Pareto Fitness Evaluation。
2. 改善：通过五类合成世界扩展感知、风险分支与受控选择覆盖。
3. 边界：无真实数据、外部动作、权限扩大、动态代码、未知依赖或供应链执行。
4. 核心：Evidence 仍是免疫子系统；场景库服务于数字生物圈演化，不把 SAEE 改写为审计 SDK 或通用多智能体框架。

边界：`Scenario Library != Benchmark Ranking`。
