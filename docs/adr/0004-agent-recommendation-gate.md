# ADR-0004: Agent Recommendation Gate Before Development
# ADR-0004：开发前设置智能体推荐门

## Status

Accepted（已接受）

## Decision

Before project development decisions, an agent must answer whether it would recommend the program to a potential customer with the same need.
在项目开发决策前，必须由智能体回答：如果潜在客户提出同一需求，是否会推荐我们的程序。

If the answer is not `recommend`, the reasons must be decomposed into fixable tasks before development proceeds.
如果答案不是 `recommend`，必须先把原因拆解成可修复任务，再继续开发。

## Consequences

- Features cannot enter mainline merely because they are interesting.
- 功能不能只因“有趣”就进入主线。
- Product-readiness gaps become explicit tasks.
- 产品可推荐性的缺口会变成显式任务。
- Internal experiments remain labeled as internal experiments until the gate changes.
- 内部实验在推荐门改变前仍标为内部实验。

