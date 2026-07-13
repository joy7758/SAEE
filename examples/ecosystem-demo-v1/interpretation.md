# 结果解释规则

## `SUPPORTED` 的唯一含义

```text
SUPPORTED = profile requirements satisfied
```

中文：`SUPPORTED` 只表示当前输入满足指定证据剖面的要求。

## 不表示

`SUPPORTED` 不表示：

- `APPROVED`：获得批准；
- `CERTIFIED`：通过认证；
- `SAFE`：系统安全；
- `DEPLOYED`：已经部署；
- `COMPLIANT`：满足法律或监管要求。

## 建议的含义

`CONTINUE / REPLAN / HUMAN_REVIEW_REQUIRED / STOP` 是调用者可组合的 decision context（决策上下文），不是 SAEE 对外部世界的执行命令。尤其是 `CONTINUE`，也不能绕过调用者自己的授权、策略、沙盒或人工重大动作门。
