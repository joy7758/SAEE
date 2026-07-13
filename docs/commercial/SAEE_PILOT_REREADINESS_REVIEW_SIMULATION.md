# SAEE Pilot Re-readiness Review Simulation v0.1

## 1. Purpose / 目的

This simulation tests re-readiness review logic. It does not establish operational readiness or authorize a pilot.

该模拟测试重新审查逻辑，不建立运营就绪状态或授权 Pilot。

```text
Re-readiness Simulation != Real Re-readiness Review
Eligibility != Approval
Synthetic PASS != Pilot Authorization
```

## 2. Review Flow / 审查流程

```text
Synthetic Artifact Package
  -> Phase 5.7 Evidence Readiness Evaluator
  -> synthetic reassessment eligibility
  -> evidence-source separation
  -> readiness-state separation
  -> authorization separation
```

本阶段复用 Phase 5.7 的 Artifact/Gap/Verification/Reference 检查，不复制或放宽其规则。

## 3. Synthetic vs Real Separation / 合成与真实分离

合成输入必须同时声明：

```text
input_type=synthetic
evidence_source_claim=SYNTHETIC
```

如果合成 Artifact 被声明为 REAL，评估器返回 `REJECT`。当前实现不接受任何 real evidence 输入，也不声称具备真实证据验证能力。

完整合成包可以得到：

```text
simulation_result=ELIGIBLE_FOR_REVIEW
reassessment_eligible=true
synthetic_evidence_ready=true
```

但同一个输出始终保留：

```text
real_readiness_status=NOT_READY
real_readiness_changed=false
gaps_closed=false
pilot_authorized=false
execution_authorized=false
```

## 4. Scenario Results / 场景结果

| Scenario | Simulation result | Real readiness |
|---|---|---|
| `COMPLETE_SYNTHETIC_EVIDENCE_PACKAGE` | `ELIGIBLE_FOR_REVIEW` | `NOT_READY` |
| `SYNTHETIC_AS_REAL_CLAIM` | `REJECT` | `NOT_READY` |
| `READINESS_STATUS_ESCALATION` | `REJECT` | `NOT_READY` |
| `DECISION_GATE_CONFUSION` | `REJECT` | `NOT_READY` |
| `PARTIAL_ARTIFACT_PACKAGE` | `NOT_ELIGIBLE_FOR_REVIEW` | `NOT_READY` |

## 5. Decision Separation / 决策分离

重新审查资格只回答：合成 Artifact package 是否满足进入审查的结构条件。

它不回答：

- Gap 是否真实关闭；
- Readiness 是否升级；
- Pilot 是否批准；
- 执行是否授权；
- 外部验证是否完成。

尝试把 simulation PASS 转换为 `attempted_execution_authorized=true` 或 `attempted_pilot_authorized=true` 会被拒绝。尝试声明外部验证完成同样被拒绝。

## 6. Current Truth / 当前真值

```text
real_readiness_changed=false
real_readiness_status=NOT_READY
gaps_closed=false
reassessment_eligible=false
pilot_authorized=false
execution_authorized=false
external_validation_completed=false
production_ready=false
```

机器聚合结果保持 `reassessment_eligible=false`；合成完整包的 true 只存在于场景级结果中。

## 7. Limitations / 局限

- 没有真实 Artifact、证据、签名、审批或客户数据；
- 没有关闭 Gap、写入 Readiness 或运行真实 Decision Gate；
- 没有 Agent 接入、网络、MCP 部署或外部执行；
- 没有定义真实 Re-readiness Review 的法律、组织或操作责任；
- simulation eligibility 不能转译为任何真实权限。
