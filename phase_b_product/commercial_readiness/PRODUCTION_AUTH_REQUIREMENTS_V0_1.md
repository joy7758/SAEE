# SAEE Production Auth Requirements v0.1

Status: requirements defined, implementation hold.

This packet defines the minimum production authentication and authorization
requirements needed before SAEE can close the `production_identity_provider`,
`oauth_oidc`, and `rbac` commercial launch blockers.

It does not implement production authentication. It does not contact identity
providers, call external services, modify backend behavior, modify API schema,
modify runtime, modify kernel, expose private core, launch product, contact
customers, or claim production readiness.

## Current Boundary

```text
production_auth_requirements_v0_1: true
requirements_status: requirements_defined_implementation_hold
production_auth_implemented: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
account_lifecycle_available: false
session_management_available: false
tenant_authorization_available: false
admin_recovery_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
task_candidates_executed: false
development_permission_granted: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
external_identity_provider_contacted: false
```

## Required OIDC Claims

- `iss`
- `sub`
- `aud`
- `exp`
- `iat`
- `tenant_id`
- `roles`

可选闭合字段仅为 `nbf` 与 `jti`。`email`、`email_verified`、`phone`、`name`、`address` 明确禁止进入当前合成身份契约；本地智能体验证不依赖真人身份或个人信息。

这些是生产契约边界。SAEE 已具有 provider-neutral、本地离线、签名夹具专用的验证核心，但尚未验证任何生产 OIDC token，也未接入真实身份提供方。

## Role Matrix

| Role | Allowed scope | Forbidden scope |
| --- | --- | --- |
| owner | tenant settings, admins, billing contacts, all tenant reports, public-shell report export | private core, runtime, kernel, tenant-boundary bypass |
| admin | preview API keys, operator access, audit metadata, all tenant reports | private core, runtime, kernel, billing terms without owner |
| evaluator_operator | create/run experiments, own reports, tenant reports | user management, cross-tenant reports, auth settings, private core |
| viewer | tenant reports, static recommendation materials | experiment execution, user management, private core |
| support_operator | request metadata, incident records, support summaries | request bodies, credentials, private core, customer data mutation |

## Evidence Required Before Closing Auth Blockers

### `production_identity_provider`

- selected identity provider
- tenant issuer mapping
- key rotation policy
- operator runbook
- security review

### `oauth_oidc`

- issuer validation
- audience validation
- JWKS cache policy
- token expiry handling
- callback and logout flow
- negative authentication tests

### `rbac`

- approved role matrix
- route permission map
- tenant boundary tests
- admin recovery test
- support access limits test

## Non-Claims

- This is not production authentication.
- This is not OAuth/OIDC implementation.
- This is not RBAC implementation.
- This does not close commercial launch blockers.
- This does not authorize development or production launch.
- This does not make SAEE production-ready or customer-validated.
