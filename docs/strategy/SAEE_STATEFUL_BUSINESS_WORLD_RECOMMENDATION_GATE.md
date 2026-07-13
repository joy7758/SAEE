# SAEE 有状态合成业务世界推荐门

状态：`recommend_for_stateful_synthetic_business_rehearsal`。

## 推荐问题

如果潜在客户希望在智能体上线前验证其面对多步骤业务状态、失败测试和部署前置条件时
是否会停止高影响动作，我会推荐当前 SAEE 吗？

## 初始答案

`conditional`。

v0.2 已证明真实千帆推理模型会选择合成工具、处理 timeout 和拒绝冲突指令，但世界仍
接近单步 fixture，尚不能证明 Agent 会在状态变化后重新判断。

## 阻塞分解

| 阻塞 | 修复 | 验收 | 状态 |
|---|---|---|---|
| 没有业务状态演化 | 新增合成 SaaS Release World | 工具调用产生可验证 revision 与 before/after digest | 本任务处理 |
| 没有多步骤证据收集 | 读取变更记录、运行测试、检查发布状态 | 千帆自主完成至少三类观察后提交 | 本任务处理 |
| 高影响动作边界不清 | 增加始终无外部效果的合成部署请求 | 前置条件不满足时 Agent 不应调用；即使调用也不部署 | 本任务处理 |
| 评分可能影响 Agent | 隐藏独立评分剖面 | profile ID、预期 disposition、reason code 不进入 prompt | 本任务处理 |
| 客户 Adapter 尚无激活契约 | 增加默认关闭契约 | `enabled=false` 且所有授权为 false | 本任务处理 |
| 客户 Agent 仍未接入 | 后续独立批准 | 客户同意、数据、凭据、成本、沙箱和停止权齐备 | 延期 |

## Required Design Check

1. 强化 `Ecological World Model`、`Counterfactual Simulation`、`Sandbox Development`、
   `Pareto Fitness Evaluation` 和 Archive/Rollback。
2. 状态变化只发生在进程内合成世界，不执行外部世界。
3. 不运行未知代码、不访问真实 Repo/DB/API、不接受客户数据、不扩大权限。
4. Evidence 记录世界变化但不成为项目核心；商业入口仍是 Agent Rehearsal。

## 最终决定

达到以上验收后：

```text
recommend_for_stateful_synthetic_business_rehearsal
```

不得解释为客户 Agent 验证、真实部署演练、风险概率、安全认证或部署批准。

