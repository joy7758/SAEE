# SAEE RBAC Policy Templates v0.1

Status: template only; RBAC is not enforced.

This directory contains a local machine-readable RBAC policy template for future
production-auth implementation review. It supports the identity-provider
configuration readiness check but does not enable OAuth/OIDC, SSO, token
validation, route authorization, or production authentication.

Template:

- `production_rbac_policy.template.json`

Required roles:

admin, evaluator_operator, owner, support_operator, viewer

Required permissions:

admin:manage, audit:read, experiment:create, experiment:read, experiment:run, operations:read, readiness:read, support:read, support:triage

Boundary:

- No runtime modified.
- No backend route behavior modified.
- No kernel modified.
- No API schema modified.
- No identity provider contacted.
- No JWKS fetched.
- No token validated.
- No RBAC enforcement enabled.
- No production authentication readiness claimed.
- No private core exposed.
