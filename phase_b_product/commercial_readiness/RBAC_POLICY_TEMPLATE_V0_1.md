# SAEE RBAC Policy Template v0.1

Status: template-only RBAC policy surface for future production-auth review.

This document records a machine-readable RBAC policy template for SAEE's public
API shell. The template supports the identity-provider configuration readiness
check by defining required roles, permissions, and route scopes.

It does not enforce RBAC. It does not implement OAuth/OIDC, validate tokens,
contact an identity provider, fetch JWKS, change backend route behavior, change
the API schema, or modify the private core.

A separate controlled-preview route guard may consume this template through
`SAEE_RBAC_POLICY_PATH`. The template itself remains template-only and does not
create production authentication or close production auth blockers.

## Files

- `phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json`
- `phase_b_product/commercial_readiness/rbac_policy_templates/README.md`
- `scripts/generate_rbac_policy_template.py`
- `scripts/saee_rbac_policy_template_smoke.py`

## Required Roles

- `owner`
- `admin`
- `evaluator_operator`
- `viewer`
- `support_operator`

## Required Permissions

- `admin:manage`
- `audit:read`
- `experiment:create`
- `experiment:read`
- `experiment:run`
- `operations:read`
- `readiness:read`
- `support:read`
- `support:triage`

## Route Scope Coverage

The template maps the current public-shell routes to required permissions:

- `GET /health`
- `GET /ready`
- `GET /commercial/status`
- `GET /experiment`
- `POST /experiment/create`
- `POST /experiment/run`
- `GET /experiment/{experiment_id}/stability`
- `GET /experiment/{experiment_id}/failures`
- `GET /experiment/{experiment_id}/ranking`
- `GET /experiment/{experiment_id}/survival`
- `GET /operations/telemetry`
- `GET /operations/alerts`
- `GET /readiness/billing-pricing`
- `GET /readiness/data-operations`
- `GET /readiness/legal`
- `GET /readiness/operations`
- `GET /readiness/privacy-security`
- `GET /readiness/support`
- `GET /readiness/vulnerability`

## Machine-Readable Status

```yaml
rbac_policy_template_v0_1: true
policy_status: template_only_not_enforced
required_roles_defined: true
required_permissions_defined: true
required_route_scopes_defined: true
identity_provider_config_readiness_can_use_template: true
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
rbac_enforced: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_route_behavior_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
external_identity_provider_contacted: false
jwks_fetched: false
tokens_validated: false
production_auth_blockers_closed_by_template: 0
```

## Boundary

This template improves commercial-auth preparation by making the future RBAC
shape explicit and testable. It is not an authorization subsystem and must not
be described as production-ready authentication.

The production launch blockers `production_identity_provider`, `oauth_oidc`,
and `rbac` remain open until a separate human-approved implementation and
evidence review exists.
