# SAEE Agent Reliability Report Format v1.0

## 报告结构

统一报告包含：

1. Agent
2. Scenario
3. Scope
4. Run Summary
5. Reliability Dimensions
6. Failure Analysis
7. Evidence Assessment
8. Limitations
9. Recommendation

机器契约：[saee-agent-reliability-report.schema.v1.0.json](../../schemas/saee-agent-reliability-report.schema.v1.0.json)。

## Recommendation

仅允许：

- `CONTINUE`
- `REPLAN`
- `HUMAN_REVIEW_REQUIRED`
- `STOP`

这些值是当前观察范围内的后续处理建议，不是授权。

禁止：`APPROVED`、`CERTIFIED`、`SAFE`、`BEST_AGENT`、`PRODUCTION_READY`。

## 聚合规则

- 任一已观察来源为 `OBSERVED_FAIL`，该维度汇总为 `OBSERVED_FAIL`。
- 存在 `OBSERVED_PARTIAL` 或部分运行为 `NOT_ASSESSED`，汇总为 `OBSERVED_PARTIAL`。
- 全部来源均被观察且通过，才汇总为 `OBSERVED_PASS`。
- 所有来源均未观察该维度时为 `NOT_ASSESSED`。
- Evidence 只有在所有运行都实际得到 PASS 时才汇总为 PASS；存在未评估运行时保守写为 `NOT_ASSESSED`。

## 真值边界

报告必须保持：

```text
approved=false
certified=false
safe=false
best_agent=false
production_ready=false
ranking_generated=false
intelligence_score_generated=false
external_validation_completed=false
```

统一格式不建立总体可靠性概率、模型能力排名、安全认证或生产准备度。
