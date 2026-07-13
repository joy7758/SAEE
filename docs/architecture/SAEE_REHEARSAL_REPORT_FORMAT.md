# SAEE Stateful Rehearsal Report Format v0.1

## 报告结构

```text
Agent
Scenario
Execution Summary
Observed Behavior
Risk Events
Evidence Assessment
Missing Evidence
Recommendation
Limitations
```

`Agent` 必须标识 provider gateway、model vendor、model、adapter version 和 execution reference。`Observed Behavior` 只使用 Observation Contract 中的动作、工具调用、输出摘要与状态变化。

## Recommendation

仅允许：

- `CONTINUE`：继续当前合成演练；
- `REPLAN`：调整合成任务或策略后重试；
- `HUMAN_REVIEW_REQUIRED`：重大外部动作需要独立授权门；这不是把人工参与者重新引入模型偏好验证；
- `STOP`：停止当前演练。

禁止：`APPROVED`、`CERTIFIED`、`SAFE`、`COMPLIANT`、`DEPLOYED`。

## 边界

报告是 Agent Readiness 决策材料，不是安全认证、合规证明、生产批准、法律判断或真实客户评估。Evidence 不足不等于系统不安全；Evidence `SUPPORTED` 也不等于系统安全。

