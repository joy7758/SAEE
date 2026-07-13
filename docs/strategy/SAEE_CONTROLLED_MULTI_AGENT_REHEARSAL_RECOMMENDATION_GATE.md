# SAEE Controlled Multi-Agent Rehearsal Evaluation v0.1 推荐门

## 推荐问题

如果潜在客户需要观察不同真实模型智能体在完全相同的合成发布压力下如何行动、发现风险、产生证据和升级，我会推荐当前程序吗？

## 结论

`recommend`

仅推荐为本地、受控、单场景、无外部副作用的行为差异实验。

## 推荐理由

- 固定场景、初始状态、工具、约束和故障注入，只改变模型；
- 每个 Agent 拥有独立世界实例，不共享状态；
- 复用既有 `AgentAdapter`、`SyntheticReleaseWorld` 和 Evidence Adequacy；
- 输出行为、风险、恢复、证据与升级五类观察，不计算综合分、名次或赢家；
- 模型不可用时记录 `unavailable`，不替换、不补齐、不伪造。
- Provider Gateway 与 Model Vendor 分离：Ark 与千帆都可能承载多个模型厂商；本实验只固定使用 Ark 的三个已指定模型。千帆多模型目录已观察，但不纳入本实验，也不代表其跨厂商演练已经验证。

## 不推荐范围

- 不推荐用来判断通用智能、模型优劣或生产表现；
- 不推荐解释为安全认证、部署批准、市场验证或公开 Benchmark；
- 不推荐把一次 API 运行解释为稳定性或可靠性统计；
- 不推荐在当前实验中接入真实仓库、客户数据或生产系统。

## Agent-Native 检查

1. 发现：Schema、Agent Profile、结果、报告和 CLI 都有稳定文件入口。
2. 理解：明确同一场景、固定变量、可观察指标及禁止排名边界。
3. 组合：`run_comparison_experiment()` 接受 Provider clients，并复用现有演练闭环。

## 演化设计检查

1. 强化：Counterfactual Simulation、Sandbox Development、Pareto Fitness Evaluation、Evolutionary Archive。
2. 改善：在控制变量条件下观察不同数字性状的行为分支与风险响应。
3. 边界：只允许 Ark 模型推理网络；所有工具与状态均为内存合成，无外部执行。
4. 核心：比较数据服务于演化选择与档案，不把 SAEE 重构为排行榜或通用多智能体框架。

边界：`Behavior Comparison != Intelligence Ranking`。
