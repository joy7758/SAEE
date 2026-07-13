# SAEE JWT Preview Auth v0.1

Status: controlled-preview signed-token guard available; production OAuth/OIDC remains false.

## Purpose

JWT Preview Auth v0.1 adds an opt-in signed bearer-token boundary for the
public SAEE API shell. When enabled, SAEE validates a local HS256-signed preview
JWT, extracts `tenant_id` and `roles`, checks tenant boundaries, and evaluates
the token roles against the existing local RBAC route policy.

This improves controlled-preview authentication evidence because route access
can be tied to signed claims instead of a freely supplied `X-SAEE-Role` header.
It does not contact an identity provider, fetch JWKS, validate production
tokens, implement SSO, manage user accounts, expose private core, or claim
production authentication readiness.

## Configuration

Default local mode keeps JWT preview auth disabled.

```text
SAEE_REQUIRE_JWT_PREVIEW_AUTH=true
SAEE_SYNTHETIC_DATA_ONLY=true
SAEE_PREVIEW_JWT_ISSUER=https://preview-idp.example.invalid/
SAEE_PREVIEW_JWT_AUDIENCE=saee-controlled-preview
SAEE_PREVIEW_JWT_HS256_SECRET=<controlled-preview-secret>
SAEE_REQUIRE_TENANT_ID=true
SAEE_ALLOWED_TENANT_IDS=tenant-alpha
SAEE_REQUIRE_RBAC_ROLE=true
SAEE_RBAC_POLICY_PATH=phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json
```

Requests must include:

```text
Authorization: Bearer <local-preview-jwt>
```

Optional role selection may include:

```text
X-SAEE-Role: evaluator_operator
```

When JWT preview auth is enabled, `X-SAEE-Role` cannot create authority. If it
is provided, the selected role must already be present in the signed token's
`roles` claim.

## Required Preview Claims

```text
iss
sub
aud
exp
iat
tenant_id
roles
```

## Behavior

- Disabled by default for local demo compatibility.
- Requires `Authorization: Bearer <token>` only when explicitly enabled.
- Accepts only HS256 preview tokens signed with the configured local secret.
- Accepts an exact closed claim set; it does not accept `email` or arbitrary extra claims.
- Rejects invalid signature, wrong issuer, wrong audience, expired token,
  missing tenant, missing role, role/header mismatch, tenant/header mismatch,
  and route roles denied by the local RBAC policy.
- Applies only to public-shell routes and report/readiness surfaces.

## Boundary

```yaml
jwt_preview_auth_v0_1: true
controlled_preview_signed_token_guard_available: true
default_required: false
jwt_preview_auth_available_when_configured: true
jwt_preview_uses_local_hs256: true
jwt_preview_production_oidc: false
production_identity_provider_available: false
oauth_oidc_available: false
sso_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
external_identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
blockers_closed_by_jwt_preview_auth: 0
```

## Verification

```bash
python3 scripts/saee_jwt_preview_auth_smoke.py
python3 scripts/mainline_guard.py
```

Expected:

```text
SAEE_JWT_PREVIEW_AUTH_SMOKE: PASS
```

## Non-Claims

This is not production OAuth/OIDC, SSO, JWKS validation, account lifecycle,
customer authorization approval, production RBAC, or product launch evidence.
Production auth blockers remain open until separate human-approved production
identity-provider, OAuth/OIDC, RBAC enforcement, security review, customer-data,
and operations evidence exists.
