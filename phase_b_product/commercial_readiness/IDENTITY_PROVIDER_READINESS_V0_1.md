# SAEE Identity Provider Configuration Readiness v0.1

Status: configuration readiness layer added, production implementation hold.

This layer makes the production identity-provider inputs machine-readable for
future review. It checks whether OIDC issuer, audience, JWKS URL, and a local
RBAC policy file have been configured. The RBAC policy file must define required
roles, required permissions, and route scopes. It does not implement
OAuth/OIDC, fetch JWKS, validate tokens, enforce RBAC, contact an identity
provider, change API schema, or claim production authentication.

## Current Boundary

```text
identity_provider_config_readiness_v0_1: true
configuration_readiness_default_status: hold
production_oidc_issuer_configured_default: false
production_oidc_audience_configured_default: false
production_oidc_jwks_url_configured_default: false
production_oidc_configuration_present_default: false
production_rbac_policy_path_configured_default: false
required_rbac_roles_present_default: false
required_rbac_permissions_present_default: false
required_rbac_route_scopes_present_default: false
rbac_route_scope_matrix_parseable_default: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
external_identity_provider_contacted: false
jwks_fetched: false
tokens_validated: false
rbac_enforced: false
```

## Configuration Inputs

```text
SAEE_PRODUCTION_OIDC_ISSUER=
SAEE_PRODUCTION_OIDC_AUDIENCE=
SAEE_PRODUCTION_OIDC_JWKS_URL=
SAEE_PRODUCTION_RBAC_POLICY_PATH=
```

These values are inputs for future implementation review only. Setting them
does not enable production authentication. The readiness checker may report
configuration readiness as `pass` when the inputs are present and the local
RBAC policy file is parseable with required roles, permissions, and route
scopes, but these product-state fields remain false:

```text
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
```

## Expected RBAC Policy Shape

The optional local RBAC policy file is JSON with:

- a top-level `roles` array;
- each required role name;
- permissions assigned to roles;
- a `route_scopes` array mapping every public-shell route to a permission and
  allowed roles.

Use the generated template instead of hand-writing this file:

```bash
python3 scripts/generate_rbac_policy_template.py
```

Template path:

```text
phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json
```

The checker verifies that the file exists, is parseable JSON, contains the
required role names, contains the required permission vocabulary, and maps the
current public-shell routes to permissions. It does not enforce these roles on
routes.

## What This Improves

- Converts the top auth blockers into concrete configuration inputs.
- Gives a future implementer a deterministic pre-implementation check.
- Lets `/ready` report whether OIDC/RBAC inputs are missing without exposing
  secrets or contacting an identity provider.

## Non-Claims

- This is not production identity provider availability.
- This is not OAuth/OIDC implementation.
- This is not RBAC enforcement.
- This is not token validation.
- This is not JWKS fetching.
- This does not close commercial launch blockers.
- This does not make SAEE production-ready or customer-validated.

## Commands

```bash
python3 scripts/saee_identity_provider_readiness.py
python3 scripts/saee_identity_provider_readiness_smoke.py
python3 scripts/saee_rbac_policy_template_smoke.py
```
