# SAEE 受控真实推理智能体演练推荐门

状态：`recommend_for_controlled_reasoning_agent_in_synthetic_world`。

## 推荐问题

如果潜在客户需要在智能体上线前，让一个真实推理模型进入完全合成、无外部副作用
的业务世界完成任务，我会推荐 SAEE 吗？

## 初始答案

`do_not_recommend`。

原因：现有 Phase 6.1 只运行仓库内固定规则状态机。它能够验证 Scenario、Trace 和
Evidence Candidate 管线，但不能观察真实推理模型的工具选择、拒绝、重试或失败处理。

## 阻塞分解

| 阻塞 | 修复任务 | 验收标准 | 状态 |
|---|---|---|---|
| 没有真实推理智能体 | 增加百度千帆受控 Adapter | Provider 实际返回自主 tool call；凭据仅来自环境变量 | 本任务处理 |
| 结果由场景预先决定 | 把评分剖面与 Agent 可见 Scenario 分离 | 评分剖面摘要不进入 Provider prompt；运行后独立评分 | 本任务处理 |
| 没有可交互模拟世界 | 增加固定内存工具 | 只执行合成读取、合成失败和合成策略拒绝；无外部效果 | 本任务处理 |
| 当前状态表述过强 | 收紧 Phase 6.1 与产品链状态 | 区分固定规则管线、真实推理演练和生产就绪 | 本任务处理 |
| 真实客户 Agent 未接入 | 后续建立 Customer Adapter Gate | 客户授权、数据、成本、沙箱和停止权均有独立证据 | 延期 |

## Required Design Check

1. 强化的演化子系统：`Ecological World Model`、`Counterfactual Simulation`、
   `Sandbox Development`、`Pareto Fitness Evaluation` 和
   `Evolutionary Archive / Rollback Immune System`。
2. 改善的是模拟世界中的感知、选择和回滚证据，不是外部世界执行能力。
3. Provider 只接收合成任务；工具全部在内存中执行；不执行未知代码、不访问客户数据、
   不自动扩大权限。
4. Evidence 仍是免疫/证据子系统。产品入口回到 Rehearsal，不把 SAEE 重构成审计 SDK。

## 最终决定

满足以上边界后，结论为：

```text
recommend_for_controlled_reasoning_agent_in_synthetic_world
```

不推荐范围保持不变：真实生产 Agent、客户数据、外部工具执行、部署批准、安全认证、
合规判断和通用 Agent 编排。

