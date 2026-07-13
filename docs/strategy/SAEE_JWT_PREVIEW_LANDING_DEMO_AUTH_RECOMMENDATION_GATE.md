# SAEE JWT Preview Landing Demo Auth Recommendation Gate

answer: conditional

recommend_for_controlled_preview_landing_demo_auth: true
recommend_for_production_auth: false
recommend_for_customer_data_processing: false
recommend_for_product_launch: false

## Question

If a potential customer asks whether the local SAEE landing demo can be tried
against the controlled-preview JWT guard, should this work be recommended?

## Decision

Recommend it only as a controlled-preview local demo convenience. It lets a
human operator attach an existing preview JWT, role, and tenant header to the
local `Run Demo Battle` request.

Do not recommend it as login, production OAuth/OIDC, enterprise SSO, production
RBAC, customer authorization, or production launch readiness.

## Reason

The change closes a local usability gap: once JWT preview auth is enabled, the
static landing demo needs a way to send the bearer token to the public API
shell. The implementation reads a token from an explicit runtime value or
short-lived `sessionStorage`, and reads role and tenant identifiers from an
explicit local configuration object. It does not use persistent `localStorage`,
render API values through `innerHTML`, or hardcode tokens or secrets.

It remains non-production because it does not contact an identity provider,
fetch JWKS, validate production tokens, manage accounts, provide a login flow,
or complete security/legal/customer-data review.

## Boundary

```yaml
jwt_preview_landing_demo_auth_v0_1: true
landing_demo_optional_preview_auth_headers: true
recommend_for_controlled_preview_landing_demo_auth: true
recommend_for_production_auth: false
recommend_for_product_launch: false
login_flow_available: false
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
private_core_exposed: false
runtime_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
external_identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
blockers_closed_by_landing_demo_auth: 0
browser_persistent_token_storage: false
dynamic_html_insertion: false
```

## Next Action

Use the landing auth header support for controlled-preview local demo testing
only. Keep production auth blockers open until real identity-provider,
OAuth/OIDC, RBAC, security review, customer-data, and operations evidence
exists.
