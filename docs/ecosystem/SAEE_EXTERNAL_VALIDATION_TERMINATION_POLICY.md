# SAEE External Validation Termination Policy v0.1

## Immediate stop conditions

- `CREDENTIAL_EXPOSURE`
- `CUSTOMER_DATA_RECEIVED`
- `UNAUTHORIZED_EXECUTION`
- `FALSE_ADOPTION_CLAIM`
- `BOUNDARY_VIOLATION`

## Required response

立即停止当前 session；禁止重试、继续调用、扩大权限或复制敏感载荷。仅保留最小化事件类型、时间、范围引用和处置状态。后续恢复需要独立明确授权和新的范围对象。

## Authority boundary

验证器可以 fail closed，但不能联系参与者、撤销外部账号、执行外部修复或作出法律/安全认定。

