# SAEE RBAC Preview Enforcement v0.1

Status: controlled-preview route guard available; production RBAC remains false.

## Purpose

RBAC Preview Enforcement v0.1 adds an opt-in public-shell route guard for
controlled preview environments. When enabled, SAEE checks `X-SAEE-Role`
against a local RBAC policy JSON before allowing access to public API routes.

This strengthens commercial auth preparation by turning the RBAC policy
template into executable local route-scope behavior. It does not validate OIDC
tokens, contact an identity provider, fetch JWKS, manage accounts, implement
SSO, expose private core, or claim production authentication readiness.

## Configuration

```text
SAEE_REQUIRE_RBAC_ROLE=true
SAEE_RBAC_POLICY_PATH=phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json
```

Requests must include:

```text
X-SAEE-Role: owner|admin|evaluator_operator|viewer|support_operator
```

## Behavior

- Default local mode keeps RBAC role enforcement disabled.
- When `SAEE_REQUIRE_RBAC_ROLE=true`, a local policy path is required.
- Missing `X-SAEE-Role` returns `401`.
- Roles not allowed for a route return `403`.
- Missing or malformed policy configuration returns `503`.
- The guard applies only to public-shell routes and public report/readiness
  surfaces.

## Boundary

```yaml
rbac_preview_enforcement_v0_1: true
controlled_preview_rbac_guard_available: true
default_required: false
preview_rbac_available_when_configured: true
rbac_enforced_in_controlled_preview: true
rbac_enforced_in_production: false
production_identity_provider_available: false
oauth_oidc_available: false
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
```

## Verification

```bash
python3 scripts/saee_rbac_preview_enforcement_smoke.py
python3 scripts/mainline_guard.py
```

Expected:

```text
SAEE_RBAC_PREVIEW_ENFORCEMENT_SMOKE: PASS
```

## Non-Claims

This is not production RBAC, OAuth/OIDC, SSO, identity-provider integration,
account lifecycle, customer authorization approval, or product launch evidence.
Production auth blockers remain open until separate human-approved production
identity-provider, OAuth/OIDC, RBAC enforcement, security review, and operations
evidence exists.
