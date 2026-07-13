# SAEE Internal Reliability Benchmark Methodology Review v1.0

## 结论

```text
review_status=PASS_WITH_LIMITATIONS_TO_PHASE7_2
extended_benchmark_allowed=true
model_runs_repeated=0
methodology_corrections=2
```

Phase 7.0 的 45-run 内部基准具有完整、平衡的尝试矩阵和失败保留机制，但原始统一映射存在两个语义问题。本审查已在不重跑模型、不改变 Run Manifest、不删除失败的前提下完成保守修正。

## 1. 审查范围

- 3 个真实模型 Agent；
- 5 个既有合成场景；
- 每个 Agent–Scenario 单元 3 次重复；
- 45 个 Run Manifest；
- 45 个 Reliability Assessment；
- Failure Taxonomy、Evidence Adequacy 与统一报告口径。

## 2. 已通过项目

### 平衡矩阵

计划矩阵为 `3 × 5 × 3`，45 个尝试均有唯一 `run_id` 和 Run Manifest。

### 失败保留

32 次契约完成、12 次契约失败和 1 次 Provider/环境不可用全部保留。失败运行分类覆盖率为 100%。

### Assessment Availability 分离

未形成闭合输出的运行只在 Assessment Availability 中记录 `OBSERVED_FAIL`。没有证据支持时，Task、Recovery 和 Boundary 保持 `NOT_ASSESSED`。

### 无排名边界

没有总体分数、排行榜、胜者、安全认证、通用能力结论或生产部署授权。

## 3. 已修正问题

### MC-001：Task 与 Evidence 解耦

原映射把 `missing_evidence` 作为 Task Execution 的 `OBSERVED_PARTIAL` 条件。这混淆了“执行契约是否完成”与“证据关系是否充分”。

修正后：

- 契约完整运行的 Task Execution 为 `OBSERVED_PASS`；
- Evidence Adequacy 独立保留 PASS/FAIL；
- Task PASS 仍不代表业务任务正确或生产成功。

### MC-002：Recovery 需要明确机会

原映射把“没有重复工具调用”解释成 Recovery PASS，但没有证明运行中实际出现了恢复机会。

修正后：

- Phase 7.0 所有 Recovery 状态保守改为 `NOT_ASSESSED`；
- Phase 7.2 必须保存 `recovery_opportunity_observed`；
- 只有机会和响应均可观察时才评价 Recovery。

## 4. 修正后的维度统计

| 维度 | PASS | PARTIAL | FAIL | NOT_ASSESSED |
|---|---:|---:|---:|---:|
| Task Execution | 32 | 0 | 0 | 13 |
| Recovery | 0 | 0 | 0 | 45 |
| Boundary | 15 | 0 | 0 | 30 |
| Evidence | 23 | 0 | 9 | 13 |
| Assessment Availability | 32 | 0 | 13 | 0 |

## 5. 未解决限制

### 场景不可直接合并

Coding、Research、Security、Business 和 Customer 使用不同任务目标、失败注入和 Evidence Adequacy 关系。它们可以使用统一对象，但不能合并为一个“可靠性总分”。

### Adapter 混杂

`MODEL_RESPONSE_FAILURE` 和 `CONTRACT_FAILURE` 同时反映模型结构化输出行为、Prompt、Provider 和 Adapter 的兼容性。不能从当前数据中分离其因果贡献。

### 统计功效不足

每格 3 次重复不足以形成总体置信区间或长期可靠性概率。Phase 7.2 仍应定位为扩展内部观察，而不是统计认证。

### Selection Bias

Boundary 和 Evidence 的 PASS 只统计形成可评估对象的运行。不可用运行不能被当作 PASS，也不能直接当作 Boundary FAIL。

## 6. Phase 7.2 放行条件

1. 保留 Agent×Scenario 分层结果；
2. 新运行记录 `recovery_opportunity_observed`；
3. 保留所有契约失败和不可用运行；
4. 不生成总体分数、排名或胜者；
5. Evidence Profile 继续按场景解释；
6. 报告 Adapter、Provider 和模型版本混杂；
7. 扩展重复数，但不把样本比例称为总体概率。

## 7. 真值边界

本审查没有重跑模型，没有建立外部效度、安全认证、生产准备度或商业交付结论。
