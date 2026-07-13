# SAEE Capability Version Policy

## 版本层级

| 版本 | 含义 | 兼容承诺 |
|---|---|---|
| `0.x` | Research / Alpha | 允许调整，但每次变更必须提供明确迁移说明和真值边界。 |
| `1.x` | Stable capability | 同一 major 内保持已发布 schema、操作名与结果语义向后兼容。 |
| `2.x` 及后续 major | Breaking changes | 允许不兼容变更，但必须提供新旧映射、弃用周期和迁移路径。 |

当前版本是 `0.1.0`，状态仅为 `ALPHA_PREPARATION`。

## Schema compatibility

- Alpha schema 默认 `additionalProperties=false`；新增必填字段属于契约变化；
- 同一 minor 内不得静默放宽拒绝规则；
- schema `$id`、版本字段与文件名必须一致；
- 破坏性 schema 变更必须新建版本，不能原地改写稳定版本。

## Operation compatibility

- 操作 ID 是机器接口：`evaluate_agent_run`、`evaluate_evidence`、`rehearse_agent`；
- 已实现操作不得在同一版本内改变为不同语义；
- `rehearse_agent=contract_only` 不能被文档或适配器假装为已实现；
- Transport Adapter 不能绕过 Canonical Capability Runtime。

## Deprecation policy

- 弃用必须先标记 `deprecated`，给出 replacement 和最后支持版本；
- Alpha 可以缩短弃用周期，但必须更新 manifest、changelog、agent-index 与 `llms.txt`；
- 已弃用契约不能在无迁移说明时直接删除。

## Migration expectations

- 消费者必须读取 `version.json` 和 release manifest，而不是猜测版本；
- major 迁移必须验证输入、输出、reason codes、状态常量和边界字段；
- 迁移不自动授权外部调用、客户数据或生产部署。
