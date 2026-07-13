# SAEE Agent Reliability Study v0.1：研究摘要

状态：本地研究草稿，未公开发表、未同行评审、未分配 DOI。

## 研究问题

同一个真实模型 Agent 在完全相同的受控任务中重复运行时，执行路径、风险发现、建议、证据结论和输出契约是否稳定？

## 方法

SAEE 将 DeepSeek、GLM 和 Doubao 通过 Volcengine Ark 放入相同的合成代码发布世界。每个 Agent 运行十次，共三十次。每次世界状态相互隔离；模型推理是真实的，代码、测试、批准、回滚和部署工具均为合成模拟。

## 结果

- 30 次计划执行全部被记录；
- 25 次完成封闭演练契约；
- 5 次 GLM 运行因最终 JSON 不符合契约而失败；
- DeepSeek 的完成运行出现 3 条工具路径；
- Doubao 的完成运行使用 1 条工具路径；
- 所有契约完成运行均发现测试失败和批准缺失；
- 所有契约完成运行的 Evidence 结论一致：授权动作和人工监督声明均缺少充分证据。

## 三项发现

1. Agent behavior may vary under identical environments.
2. Evidence assessment may remain stable despite behavioral differences.
3. Interface contract reliability is part of agent reliability.

## 如何解释

研究说明单次成功不足以描述 Agent 行为，也说明行为变化不一定导致 Evidence 判断变化。GLM 的契约失败进一步表明，Agent Reliability 是 Model、Adapter 与 Contract 的组合问题。

这些结果不构成模型排名、可靠性概率、安全认证或生产预测。完整方法、数据边界和复现入口见 `docs/research/SAEE_AGENT_RELIABILITY_STUDY_V0_1.md`。
