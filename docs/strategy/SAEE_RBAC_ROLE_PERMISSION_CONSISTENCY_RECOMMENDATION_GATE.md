# SAEE RBAC Role-Permission Consistency Recommendation Gate

answer: recommend
recommend_for_local_phase_1_security_validation: true
recommend_for_production_auth_claim: false
recommend_for_external_identity_provider_contact: false
recommend_for_production_deployment: false

## Agent recommendation

如果潜在客户要求 SAEE 证明本地 RBAC 模板内部一致，我会推荐此检查。它不仅确认路由列出了角色，
还强制确认角色确实拥有路由要求的权限，并拒绝重复角色、重复路由、未知角色、通配符和正向生产声明。

## Evolution design check

- strengthened subsystem: `Evolutionary Archive / Rollback Immune System`
- improvement: 在进入生产身份接入前，阻止不一致授权模板进入演化档案或后续选择链路。
- safety: 只读取本地 JSON，不联系身份供应商、不获取 JWKS、不验证生产 token。
- framing: 这是数字生物圈公共壳层的权限免疫检查，不把 SAEE 改造成通用审计框架。

## Boundary

本地一致性通过不等于 `production_identity_provider`、`oauth_oidc` 或 `rbac` blocker 已关闭。
`production_auth_ready=false`、`external_identity_provider_contacted=false`、`blockers_closed=0`。
