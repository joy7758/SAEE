# SAEE Agent Reliability Study v0.1 推荐门

## 推荐问题

如果潜在客户需要知道同一个 Agent 在相同受控条件下重复执行时是否出现行为、风险发现、建议或证据漂移，我会推荐当前程序吗？

## 结论

`recommend`

仅推荐为三模型、单合成场景、每模型十次的受控重复研究。

## 推荐理由

- 每次运行重新创建独立合成世界，固定初始状态、工具、策略和故障注入；
- 复用现有 AgentAdapter、SyntheticReleaseWorld、Observation 与 Evidence Adequacy；
- 分别记录执行路径、风险发现、建议、证据和恢复行为分布；
- 不合并为总分、不选赢家、不创建排行榜；
- Provider 错误或契约失败作为单次结果保存，不替换模型或伪造完成。

## 不推荐范围

- 10 次运行不足以估计总体可靠性概率；
- 单一 Coding Release 场景不能代表通用能力或生产表现；
- 不用于安全认证、部署批准、市场验证或采购排名；
- 不把本研究中的 `consistent_within_study` 解释为长期稳定保证。

## Agent-Native 检查

1. 发现：Study Schema、配置、结果、报告、Runner 和 Smoke 均有稳定文件入口。
2. 理解：明确相同 Agent、相同场景、重复隔离运行及五类稳定性指标。
3. 组合：Run Manager 接受固定 Agent Profile、Provider Client 和运行次数，并复用现有演练闭环。

## 演化设计检查

1. 强化：Counterfactual Simulation、Sandbox Development、Pareto Fitness Evaluation、Evolutionary Archive。
2. 改善：观察同一数字性状在重复环境中的行为分布与漂移。
3. 边界：只允许 Provider 推理网络；工具、状态和副作用均为合成。
4. 核心：可靠性档案服务于演化选择，不把 SAEE 重构为模型排行榜或通用 Agent Framework。

边界：`Repeated Observation != Reliability Probability`。
