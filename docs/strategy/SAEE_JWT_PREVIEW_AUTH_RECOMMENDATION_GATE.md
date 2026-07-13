# SAEE JWT Preview Auth Recommendation Gate

answer: conditional

recommend_for_controlled_preview_signed_token_guard: true
recommend_for_production_auth: false
recommend_for_customer_data_processing: false
recommend_for_product_launch: false

## Question

If a potential customer asks whether SAEE has production OAuth/OIDC or
enterprise SSO, should this work be recommended as the answer?

## Decision

Do not recommend this as production OAuth/OIDC, SSO, or production RBAC.

Recommend it only as a controlled-preview signed-token guard for public-shell
API routes when the preview issuer, audience, local HS256 secret, tenant
allowlist, and local RBAC policy have been explicitly configured.

## Reason

The change improves preview safety by moving from spoofable role headers toward
signed local preview claims. SAEE can check tenant and role claims before public
report routes execute.

It is still not production authentication because it does not contact an
identity provider, fetch JWKS, validate RS256/production tokens, manage account
lifecycle, prove SSO/OIDC, or complete security/legal/customer-data review.

## Boundary

```yaml
jwt_preview_auth_v0_1: true
controlled_preview_signed_token_guard_available: true
recommend_for_controlled_preview_signed_token_guard: true
recommend_for_production_auth: false
recommend_for_product_launch: false
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

## Next Action

Use this guard for controlled-preview authorization testing only. Keep
production auth blockers open until real identity-provider, OAuth/OIDC, RBAC,
security review, customer-data, and operations evidence exists.
