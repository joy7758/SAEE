# SAEE Entry Decision Simulation v0.1

## 目标

本阶段用固定、合成、离线场景验证 Phase 14 进入决策门，而不改变当前 `HOLD` 状态。

> This simulation validates entry decision behavior. It does not authorize or execute external validation.

> 该模拟验证进入决策行为，不授权也不执行真实外部验证。

## 决策规则

| 条件 | 结果 | 执行授权 |
|---|---|---:|
| 存在关键必需缺口 | `HOLD` | `false` |
| 无关键缺口，但仍有必需缺口或独立复核未完成 | `CONDITIONAL_ENTRY_REVIEW` | `false` |
| 所有必需缺口均有独立验证关闭证据 | `ENTRY_READY` | `false` |
| 伪证据、伪复核、伪授权或伪采用 | `REJECTED` | `false` |

`REJECTED` 是模拟验证结果，不是 Phase 14 的进入决策状态。

## 场景

覆盖当前 HOLD、仅非关键缺口、全部独立验证关闭，以及伪关闭、伪复核、伪执行授权、伪采用证据。

## 边界

- 场景中的关闭证据均为合成输入，只用于分支测试。
- `ENTRY_READY` 不等于 `external_validation=true`，也不等于 `execution_authorized=true`。
- 不连接真实参与者，不访问网络，不处理客户数据，不执行外部世界。
- 当前真实决策对象继续为 `HOLD`。

