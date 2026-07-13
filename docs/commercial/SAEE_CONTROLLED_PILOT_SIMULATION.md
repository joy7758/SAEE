# SAEE Controlled Pilot Simulation v0.1

## 1. Purpose / 目的

This simulation validates pilot governance logic. It does not execute an external pilot.

该模拟验证 Pilot 治理逻辑，不执行真实外部 Pilot。

它以本地、离线、合成输入验证未来受控 Pilot 的门依赖、失败关闭、停止、撤权、删除和产物保留逻辑。

```text
Simulation != Execution
Gate Passing != Real Authorization
Synthetic Agent != External Agent
Synthetic Data != Customer Data
```

## 2. State Model / 状态模型

```text
DESIGN_ONLY
  -> TECHNICAL_READY
  -> SECURITY_READY
  -> DATA_READY
  -> HUMAN_OWNER_ASSIGNED
  -> EXECUTION_AUTHORIZED
  -> PILOT_ACTIVE
  -> PILOT_TERMINATED
```

每次转换只能前进一个相邻状态。跳过强制状态、缺少 Gate、使用非合成引用，均失败关闭。`PILOT_TERMINATED` 是不可继续前进的终态。

`EXECUTION_AUTHORIZED` 和 `PILOT_ACTIVE` 只是模拟状态，不代表真实执行授权或 Pilot 启动。

## 3. Gate Model / Gate 模型

五道门分别为：

1. `TECHNICAL_READINESS`
2. `SECURITY_REVIEW`
3. `DATA_APPROVAL`
4. `HUMAN_RESPONSIBILITY_ASSIGNMENT`
5. `EXECUTION_AUTHORIZATION`

状态可以是 `NOT_READY`、`READY` 或 `APPROVED`。状态机只接受带合成 evidence/approval 引用的 `APPROVED`，但始终输出 `real_approval_granted=false`。

基础 Gate 模型保持所有门为 `NOT_READY`：

```text
all_gates_approved=false
approval_granted=false
pilot_start_authorized=false
```

## 4. Scenario Results / 场景结果

| Scenario | Result | Final state | Boundary |
|---|---|---|---|
| `COMPLETE_APPROVAL_PATH` | `PASS` | `PILOT_ACTIVE` | 仅证明合成路径顺序完整 |
| `MISSING_SECURITY_GATE` | `BLOCK` | `TECHNICAL_READY` | 缺安全门时不能继续 |
| `DATA_BOUNDARY_VIOLATION` | `STOP` | `PILOT_TERMINATED` | 越界后停止并清理 |
| `SECRET_EXPOSURE_DURING_PILOT` | `IMMEDIATE_TERMINATION` | `PILOT_TERMINATED` | secret 事件立即终止 |
| `NORMAL_TERMINATION` | `PASS` | `PILOT_TERMINATED` | 撤权、删除和保留闭环完成 |

两个 `PASS` 结果只代表模拟结果符合预期，不代表真实 Pilot 通过或完成。

## 5. Termination Process / 终止流程

```text
Stop condition
  -> terminate synthetic state
  -> revoke simulated access
  -> delete ephemeral synthetic data
  -> retain bounded result metadata
  -> PILOT_TERMINATED
```

模拟器不创建真实账号、Credential、Tenant、文件或数据库，因此撤权、删除和保留仅返回内存中的治理结果。它不声称真实数据已删除或真实访问已撤销。

## 6. Fail-Closed Properties / 失败关闭属性

- 强制 Gate 不可跳过；
- Gate 必须为 `APPROVED` 且引用必须显式标记为 synthetic；
- 数据越界触发 `STOP`；
- secret 暴露触发 `IMMEDIATE_TERMINATION`；
- 终止清理缺少任一步时，`cleanup_result=PENDING`；
- 结果中的真实 Pilot、客户验证、生产和外部执行字段必须保持 false。

## 7. Limitations / 局限

- 没有真实 Agent、客户、账户、认证或 Tenant Runtime；
- 没有 Secret Manager 或真实数据删除系统；
- 没有网络、MCP 部署、持久化或外部执行；
- 合成 approval reference 不代表审批人、签名或授权有效；
- 没有外部验证、客户采用、商业成功或生产就绪证据；
- 进入任何真实 Pilot 前仍需独立 Readiness Review 和明确人工授权。
