# SAEE Controlled Evaluation Prototype v0.1

“This prototype evaluates controlled synthetic evidence conditions. It does not represent real agent deployment or external validation.”

“该原型评估受控合成证据条件，不代表真实智能体部署或外部验证。”

## Purpose

本原型把 PR-9 的评估协议转成可重复运行的本地研究管线。它回答：给定研究者控制的合成场景和不同证据条件，现有 SAEE Evidence Adequacy evaluator 会对选定 claim 返回什么本地 profile 结果？

它不评估智能体能力、任务质量、执行速度、生产可靠性、安全认证或现实性能。

```text
Synthetic Scenario ≠ Real Agent Execution
Generated Trace ≠ Observed Production Trace
Evaluation Output ≠ Real-world Performance
Metric Calculation ≠ Scientific Result
```

## Architecture

```text
Controlled synthetic scenario JSON
        ↓
Schema validation
        ↓
Evidence Condition Generator
        ├─ TRACE_ONLY
        ├─ TRACE_PLUS_RECEIPT
        ├─ TRACE_RECEIPT_RELATIONSHIPS
        └─ COMPLETE_SAEE_PACKAGE
        ↓
Existing evaluate_evidence_adequacy()
        ↓
Claim-condition records
        ↓
Raw metric counts and local result artifact
```

核心充分性逻辑没有复制到 prototype。`saee_backend/services/saee_evaluation_prototype.py` 直接调用 `saee_backend.services.evidence_adequacy.evaluate_evidence_adequacy`。条件生成器只删减输入证据，不实现引用、时间、范围或因果判断。

## Scenario Model

场景 schema：

`agent-interface/schemas/saee-evaluation-scenario.schema.json`

每个场景明确记录：

- `scenario_id` 和受控任务描述；
- 合成 agent identity；
- observed actions；
- resources；
- authorization context；
- human oversight context；
- execution effects；
- 单一 expected claim；
- evaluator 使用的 claim evidence package；
- A/B/C/D 的参考期望；
- truth boundary。

当前数据集包含 8 个场景，每类 claim 2 个：

| Claim | 场景 |
|---|---|
| `RESOURCE_AUTHENTICITY` | 完整资源收据；缺少 digest |
| `AUTHORIZED_AGENT_ACTION` | 完整授权；action reference mismatch |
| `HUMAN_OVERSIGHT` | 完整审批；approval after action |
| `EXECUTION_BOUNDARY` | 完整因果绑定；causal digest mismatch |

所有身份、URI、摘要、审批、动作和效果都是合成值。保留域 `.invalid` 不会被访问。

## Evidence Conditions

### A. `TRACE_ONLY`

只保留 claim 对应的最小观察字段，例如 action、requested resource、human identity 或 receipt/effect identifier。需要证据对象或关系的字段被移除。

### B. `TRACE_PLUS_RECEIPT`

加入结构化 receipt/log 内容，但对 authorization、human oversight 和 execution boundary 仍移除范围、时间或 causal relationship 字段。对于 `RESOURCE_AUTHENTICITY`，资源收据本身已经是该 v0.1 profile 的关系对象，因此 B 可以与 C/D 形成平台期。

### C. `TRACE_RECEIPT_RELATIONSHIPS`

保留源场景声明的完整 profile evidence，包括关系字段。若源场景包含 action mismatch、late approval 或 causal digest mismatch，生成器不会修复它。

### D. `COMPLETE_SAEE_PACKAGE`

保留源场景中的完整 claim package。当前 v0.1 profile 没有额外的外部验证材料输入，因此 C 与 D 对 evaluator 可以相同。原型显式记录这一点，不伪造新的真实性证据。

### Generator invariants

- 深拷贝输入，绝不修改原场景；
- 只删除已有 evidence leaf；
- 不补造缺失字段；
- 条件顺序固定；
- 不读取其他路径、网络或外部资源。

## Evaluation Runner

runner 对 8 个场景分别生成四个条件，共产生 32 个 claim-condition 记录。每条记录包含：

- scenario 与 condition；
- claim type；
- `PASS/FAIL`；
- missing requirements；
- failed relationships；
- reference expectation match；
- relationship count；
- false-accountability 和 truth-boundary flags。

CLI：

```bash
python3 scripts/saee_agent_cli.py run-evaluation-prototype \
  --input agent-interface/evaluation/scenarios/
```

输出根标识：

```text
result_type=SAEE_EVALUATION_PROTOTYPE_RESULT
```

## Metrics

指标模块只报告原始计数、分母与公式：

1. False Accountability Rate；
2. Claim Support Coverage；
3. Evidence Relationship Completeness；
4. Missing Evidence Identification。

它固定：

```text
overall_accuracy_score_emitted=false
overall_performance_score_emitted=false
system_superiority_score_emitted=false
scientific_result_claimed=false
```

当前结果 artifact：

`agent-interface/evaluation/results/prototype-results.v0.1.json`

其中的 `0/23`、`9/9`、`29/72` 和 `32/32` 只是该固定本地合成数据集的回归计数，不是现实准确率、性能或外部比较结论。

## Validation

```bash
make check-saee-evaluation-prototype
```

聚焦 smoke 检查：场景 schema、四条件生成、不修改输入、现有 evaluator 复用、结果 artifact 一致、5 次确定性以及无网络/子进程/外部执行边界。

## Limitations

- 没有运行真实 Agent、LLM、GitHub、collector、外部 API 或工具；
- 没有使用真实用户或生产数据；
- 没有实现 PR-9 的概念 baseline；
- 8 个场景由研究者策划，参考期望不是独立标注；
- 没有 pilot、样本量估计、统计推断或置信区间；
- 没有外部复现、第三方验证或现实泛化结论；
- 本地 profile PASS 不证明真实事件、身份、授权、因果或法律责任；
- `production_ready=false` 保持不变。
