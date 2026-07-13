# SAEE 证据充分性基准剖面 v0.1

## 目的

本基准回答一个有限问题：给定明确的 `claim_type`，当前合成证据包是否满足仓库内 Evidence Adequacy Profile 定义的字段和关系要求？

“This benchmark evaluates whether available evidence relationships are sufficient to support defined accountability claims. It does not prove that underlying events occurred.”

“该基准评估现有证据关系是否足以支持明确的责任声明，但不证明底层事件一定真实发生。”

本基准不是：

- 模型智能测试；
- 智能体任务性能测试；
- 运行速度或吞吐量测试；
- 商业产品排行榜；
- 安全认证；
- 法律有效性或监管合规评估；
- SAEE 对 Microsoft、OpenTelemetry、IETF 或其他工具的优越性比较。

## 核心区分

```text
Trace ≠ Evidence
Evidence Object ≠ Accountability Claim
Schema Validity ≠ Evidence Adequacy
```

一个场景 `PASS` 只表示合成证据包满足当前本地 profile。runner 始终保留：

```text
event_occurrence_proven=false
legal_accountability_established=false
external_validation_claimed=false
benchmark_superiority_claimed=false
certification_claimed=false
production_ready=false
```

## 场景模型

数据集位于：

`agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json`

每个场景包含：

- `scenario_id`
- `claim_type`
- `scenario_description`
- `evidence_level`
- `available_evidence`
- `evidence_inputs`
- `expected_result`
- `expected_missing_requirements`
- `expected_reason_codes`
- `limitations`

`evidence_inputs` 使用仓库内固定正例 fixture 和显式 JSON Pointer 变换。runner 只允许四个 canonical Evidence Adequacy 正例路径，不接受任意文件或外部路径。

## 四个证据层级

### `LEVEL_0_TRACE_ONLY`

只有智能体、动作、资源或人类身份的观察值。3 个场景全部应失败，因为观察值没有发布者、策略决定、审批上下文或因果证据。

### `LEVEL_1_RECEIPT`

存在结构化收据或记录对象。对象存在可以支持部分对象绑定，但不保证引用正确或因果成立。

### `LEVEL_2_RECEIPT_WITH_RELATIONSHIPS`

收据和关系字段同时存在。该层特意包含字段齐全但关系错误的反例，以避免把充分性简化为字段计数。

### `LEVEL_3_COMPLETE_EVIDENCE_PACKAGE`

针对选定 claim，当前本地 profile 要求的资源、授权、审批或因果关系完整且一致。`PASS` 仍不证明现实事件或外部真实性。

## 为什么不是字段数量测试

以下三个场景没有缺失字段，但必须失败：

- `eab-l1-action-receipt-mismatched-reference`：action 与 policy decision 指向不同动作；
- `eab-l2-human-approval-after-action`：审批晚于动作；
- `eab-l2-execution-digest-mismatch`：因果链接摘要与资源／效果摘要不一致。

它们分别触发引用、时间和因果摘要关系错误。

## 指标

### Claim Coverage

按 claim 报告本地 profile `PASS/场景数`。它不是现实责任声明覆盖率，也不是产品得分。

### Level Coverage

按证据层级报告 `PASS/3`，用于观察关系增加后本地充分性支持范围的变化。

### Missing Evidence Accuracy

报告 evaluator 实际缺失路径是否与场景预期完全一致，例如 `12/12`。这是合成预期匹配计数，不是统计学习准确率。

### Reason Code Accuracy

报告稳定原因码是否与数据集预期完全一致。

### False Positive Count

当场景预期 `FAIL`、evaluator 却返回 `PASS` 时计为 false positive。该指标不等同于现实世界假阳性率，因为数据集完全合成。

### Boundary Safety

任何场景若把 `accountability_claim_established`、事件发生、身份验证、法律认定或生产状态升级为 `true`，都计入边界违规。

## v0.1 结果基线

```text
总场景：12
PASS：5
FAIL：7
LEVEL_0：0/3
LEVEL_1：1/3
LEVEL_2：1/3
LEVEL_3：3/3
expected_result_matches：12/12
missing_evidence_accuracy：12/12
reason_code_accuracy：12/12
false_positive_count：0
boundary_violation_count：0
```

这些值是固定数据集的回归基线，不是 SAEE 的“准确率”、能力排名或外部验证结果。

## 运行方式

```bash
python3 scripts/saee_agent_cli.py benchmark-evidence-adequacy \
  --input agent-interface/benchmarks/evidence-adequacy/
```

聚焦 smoke：

```bash
python3 scripts/saee_evidence_adequacy_benchmark_smoke.py
```

## 限制

- 所有身份、动作、资源、审批和效果均为合成值。
- 示例中的 `.invalid` host 是保留的合成标识，runner 不访问它们。
- 不使用真实 agent trace、OpenTelemetry SDK、外部策略系统或身份系统。
- 数据集只覆盖四个 v0.1 claim 和十二个策划场景，不能估计真实场景分布。
- 场景预期由本地 profile 语义制定，不是独立第三方标注。
- 没有密码学身份认证、外部签名验证、法律事实判断或监管认可。
- 结果不能用于比较外部框架、供应商或商业产品。

该 benchmark 强化 Pareto Fitness Evaluation 和 Evolutionary Archive 对证据评估器自身的可复核性，不改变 SAEE 数字生物的运行时权限或外部执行边界。
