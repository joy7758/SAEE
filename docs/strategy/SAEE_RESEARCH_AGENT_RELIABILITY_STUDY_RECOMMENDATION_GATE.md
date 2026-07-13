# SAEE Research Agent Evidence Reliability Study v0.2 推荐门

## 推荐问题

如果潜在客户需要观察研究 Agent 在固定合成资料下能否稳定引用证据、保持声明边界并表达不确定性，我会推荐当前程序吗？

## 结论

`recommend`

仅推荐为三模型、每模型五次、无外部检索的合成研究证据边界实验。

## 推荐理由

- 复用既有 Stateful Rehearsal、Observation、Evidence Adequacy 和 Reliability Analyzer；
- 四个工具全部作用于内存中的合成资料；
- 明确观察 Unsupported Claim、Missing Citation、Overconfidence 和 Evidence Boundary Violation；
- `AUTHORIZED_AGENT_ACTION` 只判断研究摘要动作是否受已观察边界约束，不判断事实真假；
- 不产生事实认证、知识排名、医学或法律结论。

## 不推荐范围

- 不推荐用作自动论文评审、事实核查服务或知识真实性认证；
- 单一合成资料集与每模型五次样本不能推广到真实研究能力；
- Evidence PASS 不等于结论为真；
- 不推荐用于客户数据、真实检索、生产决策或模型排名。

## Agent-Native 与演化检查

1. 发现：Scenario、World、Tool Contract、Study、Result、Report 和 Smoke 均有稳定文件入口。
2. 理解：明确何时用于研究声明证据边界，何时不能用于事实认证。
3. 组合：研究 Adapter 复用 Ark Client，Study 复用既有 Reliability Analyzer。
4. 强化：Ecological World Model、Counterfactual Simulation、Sandbox Development、Pareto Fitness Evaluation 与 Evolutionary Archive。
5. 边界：无网络搜索、真实资料、客户数据、外部动作或第二套 Evidence Evaluator。

边界：`Evidence Support Evaluation != Factual Truth Verification`。
