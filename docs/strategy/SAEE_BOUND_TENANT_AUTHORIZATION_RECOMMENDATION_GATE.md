# SAEE Bound Tenant Authorization Recommendation Gate

answer_before_fix: conditional
development_blockers_before_fix: 4
production_recommendation: do_not_recommend
production_blockers_closed: 0
final_independent_agent_verdict: recommend
final_independent_agent_blockers: 0
final_negative_cases: 14/14

## 潜在客户推荐问题

若中国市场客户要求“智能体调用 SAEE 时，租户身份与 API、RBAC、service、storage
必须绑定并 fail closed”，修复前只可在严格 JWT controlled preview 条件下推荐，
不推荐生产部署。

## 修复分解

1. 使用不可变 `AuthorizedPrincipalContext` 绑定 subject、tenant、signed roles、route 和 permission。
2. secure store 拒绝裸 tenant 字符串，factory 原子传递完整链配置。
3. header 自报 tenant/role 与 JWT 部分链不能返回 `ready=true`。
4. `/health`、`/ready` 明确为非租户 probe，并统一 API-key/JWT/RBAC 身份依赖。

## Evolution design check

- strengthened subsystem: `Evolutionary Archive / Rollback Immune System`
- improvement: 让档案写入和读取只接受同一已认证租户上下文，阻断跨租户旁路。
- safety: 仅本地合成 JWT、临时 SQLite 和固定 RBAC template；不联网、不读取真实密钥。
- framing: 授权是档案免疫边界，不是 SAEE 的工程核心，不改变数字生物圈进化引擎定位。

## 生产边界

```yaml
tenant_authorization_policy_reviewed: false
production_identity_provider_available: false
oauth_oidc_available: false
jwks_fetched: false
tokens_validated_in_production: false
tenant_authorization_enabled: false
rbac_available: false
production_auth_ready: false
production_tenant_storage_isolated: false
security_review_completed: false
privacy_legal_review_completed: false
production_ready: false
customer_validated: false
blockers_closed: 0
```

## 最终独立智能体复核

第三轮独立复核确认 Memory/SQLite 对裸 tenant、伪造 capability、空 principal、
伪造 auth source 和 create/run/read permission confusion 均 fail closed，最终
`recommend`、0 blocker。推荐只覆盖单进程 controlled preview；capability 没有独立
expiry/jti，不得缓存或跨进程复用。
