# SAEE Agent Reliability Study Publication Draft v0.1 推荐门

## 推荐问题

如果潜在客户、研究智能体或开发团队需要理解 SAEE 如何研究智能体行为稳定性、证据一致性和输出契约可靠性，我会推荐当前草稿吗？

## 结论

`recommend`

仅推荐为一个本地、可审阅、可追溯、尚未外部发布的研究草稿与复现索引。

## 推荐理由

- 所有数字均直接引用 Phase 6.5 冻结结果，没有补跑、删减失败或推导总体概率；
- 清楚区分 30 次已执行、25 次契约完成和 5 次契约失败；
- 使用 Observable Metrics，不生成 Intelligence Score、总体排名或赢家；
- 复现包只引用场景、Profile、配置、Schema、结果和本地命令，不包含密钥、Provider 原始响应或私有日志；
- 同时提供完整研究稿、外部摘要和机器可读清单。

## 不推荐范围

- 尚未同行评审、外部验证、公开发布或分配 DOI；
- 单场景、每模型十次不能支持总体可靠性概率；
- 不能用于安全认证、采购排名、模型优劣或生产预测；
- 复现真实 Provider 运行仍需要复现者自行提供合法凭据并承担成本。

## Agent-Native 检查

1. 发现：研究稿、摘要、Manifest、README、复现说明和 Smoke 均有稳定路径。
2. 理解：报告明确研究问题、架构、方法、Observable Metrics、结果、发现和限制。
3. 组合：Manifest 为每个输入和产物提供路径、SHA-256、角色及公开边界。

## 演化设计检查

1. 强化：Evolutionary Archive / Rollback Immune System、Pareto Fitness Evaluation、Counterfactual Simulation。
2. 改善：把重复演练观察固化为可追溯研究资产和未来选择依据。
3. 边界：不复制 Provider payload，不暴露密钥，不执行新的外部动作。
4. 核心：Evidence 仍是免疫子系统；报告围绕数字生物圈中的受控演练与演化选择，不把项目改写为审计 SDK。

边界：`Publication Draft != External Publication`。
