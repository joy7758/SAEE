# SAEE Controlled Pilot Execution Decision Gate v0.1

## 1. Purpose / 目的

This decision gate models whether a future controlled external Agent Pilot request must remain blocked, needs further review, satisfies a synthetic decision scenario, or must be terminated. It does not authorize a real Pilot.

本决策门模拟未来受控外部 Agent Pilot 申请应保持阻塞、继续审查、在合成场景中满足条件或被终止，不授权真实 Pilot。

```text
Decision Gate != Approval Authority
Readiness != Permission
Missing Evidence != Assumed Complete
```

默认原则：未知或缺失关键证据即 `HOLD`。

## 2. Decision States / 决策状态

### HOLD

触发条件：存在关键阻塞、Readiness 为 `NOT_READY`、缺安全审查、数据批准、人工责任人或执行授权。

当前真实状态：`HOLD`。

### CONDITIONAL_HOLD

仅用于没有关键阻塞、但仍有非关键准备工作或合成批准要素不完整的场景。执行仍被阻塞，`execution_authorized=false`。

### APPROVED_FOR_EXECUTION

只在合成测试中，当以下条件全部满足时产生：

- 合成 Readiness 为 `READY`；
- 没有 blocking gaps；
- 合成 Security/Data/Execution approval 均存在；
- 合成人工责任人已赋值；
- `synthetic_approval=true`。

该状态只验证规则的可达性，输出仍保持：

```text
execution_authorized=false
real_approval_exists=false
synthetic_decision_only=true
```

设计文档、模拟 PASS、无签名引用或缺失 evidence reference 不能生成该状态。

### TERMINATED

secret 暴露或 boundary breach 优先于全部批准条件，立即产生 `TERMINATED`。终止状态不代表真实 Pilot 已被操作，因为本阶段没有真实 Pilot。

## 3. Decision Rules / 决策规则

决策优先级：

```text
Safety violation
  -> TERMINATED
Critical gap or NOT_READY
  -> HOLD
No critical gap but preparation incomplete
  -> CONDITIONAL_HOLD
All synthetic requirements met
  -> APPROVED_FOR_EXECUTION (synthetic only)
```

任何真实执行、客户验证、生产就绪或 real approval 声明都会被拒绝。

## 4. Human Approval Boundary / 人工批准边界

- `human_approval_required=true` 必须始终保留；
- 合成 owner reference 必须显式使用 `synthetic:owner:`；
- 合成 approval evidence 必须显式使用 `synthetic:approval:`；
- 决策器不验证真实签名、组织权限或审批有效期；
- 真实执行只能由本模型之外、经过授权的人类治理流程决定。

## 5. Synthetic Scenarios / 合成场景

| Scenario | Decision | Real execution authority |
|---|---|---|
| `CURRENT_NOT_READY` | `HOLD` | false |
| `MISSING_DATA_APPROVAL` | `HOLD` | false |
| `MISSING_HUMAN_OWNER` | `HOLD` | false |
| `ALL_REQUIREMENTS_SYNTHETICALLY_MET` | `APPROVED_FOR_EXECUTION` | false |
| `SAFETY_VIOLATION` | `TERMINATED` | false |

## 6. Current Decision / 当前决策

```text
decision=HOLD
readiness_status=NOT_READY
blocking_gap_count=15
execution_authorized=false
real_approval_exists=false
pilot_executed=false
customer_validated=false
production_ready=false
```

## 7. Limitations / 局限

- 没有真实审批人、签名、认证、账户或执行授权；
- 没有连接 Agent、客户数据、Tenant Runtime 或 Secret Manager；
- 没有关闭 Phase 5.4 的任何阻塞；
- 合成 `APPROVED_FOR_EXECUTION` 不可转译为真实许可；
- 决策门不是认证、法律判断、合规结论或生产发布门。
