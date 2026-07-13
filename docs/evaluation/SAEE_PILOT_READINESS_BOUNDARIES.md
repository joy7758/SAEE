# SAEE Pilot Readiness Boundaries v0.1

“Readiness review determines whether prerequisites are satisfied for a future pilot. It does not demonstrate that a pilot has been executed or validated.”

“就绪审查用于判断未来试点启动条件是否满足，不证明试点已经执行或完成验证。”

## Truth boundaries

- `NO_GO` 表示停止是正确结果，不表示实验失败。
- `GO` 只表示 matrix 的前提满足，不自动授权执行。
- 单一维度 `READY` 不等于整体 `GO`。
- Technical `READY` 只覆盖已引用的本地合成环境与 pipeline。
- Safety `READY` 只覆盖安全规则已定义；当关键数据或隐私条件缺失时，执行安全门仍为 `STOP`。
- readiness evaluator 不读取外部系统、不采集数据、不运行 Agent、不处理个人数据、不生成实验结果。
- 任何真实试点仍需单独、明确、可审计的执行授权。

当前固定状态：

```text
decision=NO_GO
execution_started=false
execution_approval_recorded=false
experiment_executed=false
external_validation_completed=false
scientific_result_claimed=false
production_ready=false
```

