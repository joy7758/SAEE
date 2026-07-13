# SAEE Agent Reliability Framework v1.0：来源映射

## 目的

本框架把已冻结的演练、证据和推荐观察映射为统一的 `Agent Reliability Assessment Object`。它不重跑实验、不合并成总分、不比较模型优劣，也不把不同场景视为可直接互换。

```text
Agent Run
  -> Observation Events
  -> Reliability Assessment
  -> Existing Evidence Assessment
  -> Bounded Readiness Report
```

## 五个可靠性维度

| 维度 | 回答的问题 | 不代表 |
|---|---|---|
| `task_execution_reliability` | 固定运行契约内观察到怎样的执行完成情况？ | 通用任务能力 |
| `recovery_reliability` | 是否观察到重规划、升级或重复工具处理？ | 长期恢复概率 |
| `boundary_reliability` | 是否保持声明的合成权限与动作边界？ | 安全认证 |
| `evidence_reliability` | 既有 Evidence Adequacy 关系是否满足？ | 事实真值 |
| `assessment_availability` | 固定评估契约是否产生可评价输出？ | Agent 能力或安全性 |

每个维度只能使用：`OBSERVED_PASS`、`OBSERVED_PARTIAL`、`OBSERVED_FAIL`、`NOT_ASSESSED`。

## 来源映射

| 既有来源 | 映射维度 |
|---|---|
| Coding Agent Release Reliability v0.1 | 执行、恢复、证据、评估可用性 |
| Research Agent Evidence Reliability v0.2 | 执行、证据、评估可用性 |
| Security Boundary Reliability v0.3 | 执行、边界、证据、评估可用性 |
| Stateful Business Rehearsal v0.3 | 执行、恢复、评估可用性 |
| Agent Recommendation Benchmark v0.1 | 评估可用性 |
| Evidence Adequacy Evaluator v0.1 | 证据可靠性 |

机器映射：[saee-reliability-source-mapping.v1.0.json](../../agent-interface/reliability/saee-reliability-source-mapping.v1.0.json)。

## 关键解释边界

- `CONTRACT_FAILURE` 与 `MODEL_RESPONSE_FAILURE` 首先影响 `assessment_availability`，不能自动写成任务失败或安全失败。
- 未被来源直接观察的维度必须为 `NOT_ASSESSED`。
- 跨来源报告保留各场景和样本限制，不计算总分、平均模型分或胜者。
- `all_existing_studies_mapped=true` 表示当前列举的文件有显式映射，不表示外部研究覆盖完整。

## 当前限制

这些来源具有不同任务、样本量、Provider 和时间点。统一对象解决语义和机器组合问题，不解决统计可比性、外部效度或生产预测问题。
