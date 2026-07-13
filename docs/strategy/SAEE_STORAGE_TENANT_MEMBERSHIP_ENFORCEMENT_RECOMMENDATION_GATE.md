# SAEE Storage Tenant Membership Enforcement Recommendation Gate

answer: recommend
recommendation_scope: factory_configured_controlled_preview_allowlist_membership_enforcement
development_blockers: 0
production_blockers_closed: 0

## 独立智能体建议

潜在中国客户要求智能体绕过 HTTP API 直接调用 service/storage 时，格式合法但未列入 `SAEE_ALLOWED_TENANT_IDS` 的租户仍必须被拒绝。独立智能体建议补齐该纵深防御。

## Evolution design check

- strengthened subsystem: `Evolutionary Archive / Rollback Immune System`
- improvement: 在归档读写入口统一执行配置化租户成员资格边界。
- safety: 只读取本地配置快照，不联网、不读取密钥、不迁移数据、不扩大权限。
- framing: 这是受控预览存储边界，不是 audit-first 核心，也不是通用多智能体框架。

## 验收范围

- factory 向 memory/SQLite 传递不可变 allowlist 快照。
- strict 模式对空、非法、缺失和未列入 allowlist 的 tenant fail closed。
- `create/save/exists/get/get_runs/get_metrics/list` 七类操作均直接覆盖。
- memory、SQLite、SQLite reload 和绕过 API 的直接调用均覆盖。
- API 与 storage 复用同一格式契约；storage 不依赖 `HTTPException`。
- 错误与证据不枚举合法 tenant ID。

## 不可越界

```yaml
tenant_authorization_enabled: false
membership_scope: configured_preview_allowlist_not_identity_authentication
production_tenant_storage_isolated: false
multi_tenant_production_ready: false
security_review_completed: false
privacy_legal_review_completed: false
customer_validated: false
production_ready: false
blockers_closed: 0
```

实现已将 API 与 storage 的格式校验收敛到 `saee_backend.config.tenant_id_format_valid`，消除重复正则漂移风险。

## Independent agent validation

```yaml
round_1_verdict: conditional
round_1_blockers: 1
round_2_verdict: recommend
round_2_blockers: 0
validation: agent_recommendation/storage_tenant_membership/run_001/independent_agent_validation.local.json
```
