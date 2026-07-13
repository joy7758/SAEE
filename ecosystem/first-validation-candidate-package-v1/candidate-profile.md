# 候选类别画像

## P0：MCP Agent Developer

这是类别，不是真实参与者身份。

适合原因：

- 能直接验证 SAEE 的 Agent-native 发现能力；
- 能使用本地 MCP Adapter 验证工具发现与 invocation contract；
- 不需要云平台权限、生产数据或复杂采购流程；
- 测试可由固定合成场景重复执行。

要验证的问题：

1. 能否从机器入口发现 SAEE？
2. 能否区分 `evaluate_agent_run`、`evaluate_evidence` 和 `rehearse_agent=CONTRACT_ONLY`？
3. 能否完成本地调用？
4. 能否把 `SUPPORTED` 限制为“满足剖面要求”？
5. 能否理解 SAEE 不提供授权、认证或部署批准？

## P1：Agent Framework Developer

可验证 SAEE 是否容易组合进工作流，但需要额外框架上下文。当前不选择具体框架或开发者。

## P2：Cloud Platform

潜在生态价值较高，但身份、网络、平台评审和权限复杂度更高，因此不是第一次最小验证的默认类别。
