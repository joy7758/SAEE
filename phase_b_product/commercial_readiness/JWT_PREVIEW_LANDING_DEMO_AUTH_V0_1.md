# SAEE JWT Preview Landing Demo Auth v0.1

Status: local landing demo can attach optional controlled-preview JWT headers; production auth remains false.

## Purpose

JWT Preview Landing Demo Auth v0.1 lets the local static landing demo call the
SAEE public API shell when controlled-preview JWT auth is enabled.

The landing script still works without auth by default. When a human operator
sets short browser-session values and an explicit local configuration object,
the `Run Demo Battle` request adds:

```text
Authorization: Bearer <local-preview-jwt>
X-SAEE-Role: <preview-role>
X-SAEE-Tenant-ID: <preview-tenant-id>
```

This connects the existing local landing demo to the existing JWT preview guard
and JWT preview token CLI. It does not add a login flow, contact an identity
provider, fetch JWKS, validate production tokens, expose private core, process
customer data, or claim production authentication readiness.

## Human Operator Flow

Generate a local preview token:

```bash
export SAEE_REQUIRE_JWT_PREVIEW_AUTH=true
export SAEE_SYNTHETIC_DATA_ONLY=true
export SAEE_PREVIEW_JWT_ISSUER="https://preview-idp.example.invalid/"
export SAEE_PREVIEW_JWT_AUDIENCE="saee-controlled-preview"
export SAEE_PREVIEW_JWT_HS256_SECRET="<local-controlled-preview-secret>"

TOKEN="$(python3 scripts/saee_jwt_preview_token.py \
  --subject preview-user-001 \
  --tenant-id tenant-alpha \
  --roles evaluator_operator \
  --ttl-seconds 3600)"
```

Start the local API and landing page with the controlled-preview auth variables
enabled. In the browser console for `http://127.0.0.1:8765/`, set a token that
expires with the browser tab and an explicit non-secret configuration object:

```javascript
sessionStorage.setItem("SAEE_PREVIEW_TOKEN", "<token-from-cli>");
window.__SAEE_LOCAL_DEMO_CONFIG__ = Object.freeze({
  previewRole: "evaluator_operator",
  previewTenantId: "tenant-alpha"
});
```

Then click `Run Demo Battle`.

To clear the local preview header values:

```javascript
sessionStorage.removeItem("SAEE_PREVIEW_TOKEN");
sessionStorage.removeItem("SAEE_PREVIEW_AUTHORIZATION");
delete window.__SAEE_LOCAL_DEMO_CONFIG__;
```

## Accepted Local Browser Keys

```text
SAEE_PREVIEW_TOKEN
SAEE_PREVIEW_AUTHORIZATION
__SAEE_LOCAL_DEMO_CONFIG__.previewRole
__SAEE_LOCAL_DEMO_CONFIG__.previewTenantId
```

`SAEE_PREVIEW_AUTHORIZATION` may contain either the full `Bearer ...` value or
the raw token. `SAEE_PREVIEW_TOKEN` may contain the raw token or a `Bearer ...`
value. Tokens are not read from persistent `localStorage`; the page does not
store or generate secrets. Closing the browser tab clears `sessionStorage`.

## Boundary

```yaml
jwt_preview_landing_demo_auth_v0_1: true
landing_demo_optional_preview_auth_headers: true
default_required: false
login_flow_available: false
browser_token_storage: session_only
browser_persistent_token_storage: false
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
blockers_closed_by_landing_demo_auth: 0
```

## Verification

```bash
python3 scripts/saee_landing_jwt_preview_auth_smoke.py
python3 scripts/saee_landing_page_smoke.py
python3 scripts/saee_landing_api_integration_smoke.py
python3 scripts/mainline_guard.py
```

Expected:

```text
SAEE_LANDING_JWT_PREVIEW_AUTH_SMOKE: PASS
```

## Non-Claims

This is not production OAuth/OIDC, SSO, JWKS validation, account lifecycle,
customer authorization approval, production RBAC, customer validation, product
launch evidence, or production-auth blocker closure.
