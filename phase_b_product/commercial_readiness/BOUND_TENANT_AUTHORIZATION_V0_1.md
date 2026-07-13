# 绑定式租户授权链 v0.1

bound_tenant_authorization_v0_1: true
scope: local_controlled_preview_jwt_principal_tenant_rbac_storage_binding
development_blockers_before_fix: 4
negative_cases: 14/14
tenant_authorization_policy_reviewed: false
production_auth_ready: false
production_ready: false
blockers_closed: 0
independent_agent_verdict: recommend
independent_agent_blockers: 0

安全模式通过 `SAEE_REQUIRE_BOUND_TENANT_AUTHORIZATION=true` 显式开启。该模式要求：

- 本地 HS256 preview JWT 已签名且 issuer/audience 完整；
- JWT 包含 tenant 和 roles；
- tenant allowlist 非空；
- RBAC policy 可解析且 canonical route 被允许；
- factory 创建的 memory/SQLite store 要求不可变 `AuthorizedPrincipalContext`；
- context 使用 preview JWT secret 域分离签发 HMAC capability，store 校验来源和操作 permission；
- 裸 tenant、角色伪造、租户切换、未知路由和部分配置全部 fail closed。

`/health` 与 `/ready` 是非租户探针：前者只返回最小健康状态，后者只返回配置状态；
二者执行 API-key、JWT 和 RBAC 身份依赖，但不代表业务租户授权或生产就绪。

本功能不实现生产 OIDC/SSO、JWKS、算法轮换、账号生命周期、正式 tenant policy 审批、
生产 RLS、正式安全复核或隐私/法律复核。HS256 仅限本地 controlled preview。
HMAC capability 没有独立 expiry/jti，只能在当前进程的请求链中短期使用，不得长期
缓存或跨进程复用。
