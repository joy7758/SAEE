# SAEE Assessment Availability v1.0

## 定义

```text
assessment_availability_rate
= successful_assessments / attempted_assessments
```

- `attempted_assessments`：进入固定、版本化评估契约的尝试数量。
- `successful_assessments`：产生可由统一适配器解释的闭合输出数量。
- `assessment unavailable`：契约、Provider、环境或结构化响应没有产生可评价对象。

## 为什么独立成一个维度

评估不可用只说明“本次固定评估没有得到可解释输出”。它不能自动说明：

- Agent 执行失败；
- Agent 不具备能力；
- Agent 不安全；
- 安全边界被违反；
- Evidence Adequacy 失败。

例如 Phase 6.8 中 GLM 的结构化输出失败被分类为 `CONTRACT_FAILURE` / `MODEL_RESPONSE_FAILURE`，并影响 Assessment Availability。由于没有形成闭合边界观察，其 Boundary Reliability 是 `NOT_ASSESSED`，不是 `OBSERVED_FAIL`。

## 解释限制

Assessment Availability Rate 是当前 Adapter、Provider、提示和 Schema 组合下的样本比例，不是长期 SLA、总体概率、模型排名或生产稳定性保证。
