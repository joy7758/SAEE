# SAEE 证据研究 Artifact 架构说明

## 所属位置

本架构是 SAEE 数字生物圈进化引擎中的免疫／证据子系统，用于保存和复查智能体观察、证据对象及本地 claim 需求。它不是 SAEE 的全部架构，不是通用智能体工作流，也不授权数字生物直接执行外部世界。

## 研究数据流

```text
Observation Layer
        ↓
Candidate Evidence Mapping
        ↓
Evidence Object Layer
        ↓
Evidence Adequacy Layer
        ↓
Accountability Claim Evaluation
```

## Observation Layer

输入是系统声明观察到的 agent、action、tool、resource、timestamp 或 human 字段。v0.1 使用 OpenTelemetry 风格合成 JSON，不导入 SDK，不连接真实 collector，也不读取网络轨迹。

输出是未验证的观察值。该层回答“记录里出现了什么”，不回答“记录是否真实”。

## Candidate Evidence Mapping

映射器把允许的观察字段投影为候选证据字段，并标记 `PASS`、`PARTIAL` 或 `FAIL`。候选值仍然是不可信声明，缺少身份材料、授权对象、内容摘要或因果关系时不能升级为证据充分。

## Evidence Object Layer

资源解析收据等对象提供闭合 schema、规范化字段和本地摘要一致性检查。证据对象能够绑定多项声明，但摘要一致不等于签名，URI 合法不等于资源存在，publisher 字段存在不等于身份真实。

## Evidence Adequacy Layer

profile 针对四类 claim 指定必需字段和语义关系。evaluator 不仅检查字段数量，还检查 action 引用相等、审批早于动作和摘要因果绑定等关系。

`PASS` 的准确含义是：当前合成证据包满足当前本地 profile。它不把 claim 升级为现实事实。

## Accountability Claim Evaluation

输出包含 profile 需求是否满足、缺失项和原因码，同时保持：

```text
accountability_claim_established=false
underlying_events_proven=false
legal_validity_claimed=false
production_ready=false
```

## 核心断言

**Trace does not become evidence automatically.**

轨迹必须先经过候选映射、对象绑定和关系充分性检查；即使这些本地检查全部通过，也只能说明定义的本地需求得到满足，不能自动证明现实事件、法律责任或外部真实性。

## 层间失败传播

```text
观察字段缺失
  → 候选映射 FAIL

候选映射成功但缺少证据对象
  → 充分性 FAIL

证据字段齐全但关系错误
  → 充分性 FAIL

本地充分性 PASS
  → 仅 profile_requirements_satisfied=true
  → accountability_claim_established 仍为 false
```

这种分层让研究者可以定位失败发生在观察、对象、关系还是结论边界，而不把所有状态压缩成单一布尔值。
