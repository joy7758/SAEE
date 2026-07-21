# Memory Policy

## Mandatory startup order

所有 AI Agent 开始 SAEE 治理或变更工作前必须按以下路由顺序读取：

1. `governance/project-memory/`
2. `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
3. `governance/registry/`
4. `capability-package/manifest.json#canonical_inventory`

Project Memory 先读是为了减少重复讨论，不改变权威优先级。

## Authority precedence

```text
safety / law / explicit human authorization
                ↓
SAEE Development Constitution
                ↓
registry-specific authority and ADR
                ↓
canonical capability inventory for capability facts
                ↓
Project Memory decision routing
```

Project Memory 记录决策状态，不是事实数据库。外部系统、marketplace、runtime 和
capability 的当前事实必须从对应权威证据实时解析。

## Frozen Decision rule

如果问题已经存在 Frozen Decision：

- 禁止重新讨论同一已冻结路线；
- 允许检查新请求是否真正落在该冻结范围内；
- AI 不得自行解除冻结；
- AI 不得静默改写或删除历史决策。

## Decision Change Proposal

如果需要改变 Frozen Decision，必须先创建 Decision Change Proposal，至少包含：

1. 目标 Frozen Decision ID；
2. 新证据和证据来源；
3. 为什么现有决定不再成立；
4. Constitution、registry、capability 和 product 影响；
5. claims、non-claims 和 staged truth；
6. migration/rollback plan；
7. 明确人工确认记录。

没有人工确认时，提案只能保持 `PROPOSED`，Frozen Decision 继续有效。

## Active Question rule

- 只有尚未解决的问题进入 `active-questions.md`。
- 已冻结问题不得重复进入 Active Questions。
- 问题关闭后必须追加 decision-log 条目，并从 active list 移出；不得删除其历史证据。

## Decision Log rule

- `decision-log.md` 只追加，不静默重写。
- 纠错使用新 ID，并引用原 ID。
- 日志条目不是 capability、marketplace、runtime 或 production authority。

## Truth and inference rule

- AI 不得把推断升级为事实。
- AI 不得把 local pass、synthetic pass、package-ready、review、submission、approval、listing、customer validation 和 production readiness 合并为一个状态。
- 项目记忆与权威事实冲突时，以权威事实为准，并建立 Active Question 或 Decision Change Proposal。
- 时间敏感事实必须记录 evidence timestamp；没有当前证据时使用 `UNKNOWN`、`NOT_ESTABLISHED` 或对应 staged status。

## Prohibited uses

Project Memory 不得用于：

- 自动授权 commit、push、deploy、PR 或外部联系；
- 修改 capability inventory；
- 声称 marketplace approval、产品发布、客户验证或生产就绪；
- 直接合并 Agent Evidence 代码；
- 绕过 Constitution、registry validator 或人类 gate。
