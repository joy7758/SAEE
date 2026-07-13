# SAEE RBAC Preview Enforcement Recommendation Gate

answer: conditional

recommend_for_controlled_preview_route_guard: true
recommend_for_production_auth: false
recommend_for_customer_data_processing: false
recommend_for_product_launch: false

## Question

If a potential customer asks whether SAEE has production RBAC, should this work
be recommended as the answer?

## Decision

Do not recommend this as production RBAC.

Recommend it only as a controlled-preview route guard for public-shell API
routes when a local RBAC policy has been explicitly configured.

## Reason

The change makes role-to-route authorization executable for local and
controlled-preview API usage. That reduces commercial preview risk because
read-only roles cannot run experiments and support roles can be scoped to
operations/readiness surfaces.

It is not production authentication because it does not validate identity
tokens, connect to an identity provider, fetch JWKS, manage account lifecycle,
prove SSO/OIDC, or complete security/legal/customer-data review.

## Boundary

```yaml
rbac_preview_enforcement_v0_1: true
controlled_preview_rbac_guard_available: true
recommend_for_controlled_preview_route_guard: true
recommend_for_production_auth: false
recommend_for_product_launch: false
rbac_enforced_in_controlled_preview: true
rbac_enforced_in_production: false
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
tokens_validated_in_production: false
```

## Next Action

Use this guard for controlled-preview authorization testing only. Keep the
production auth blockers open until real identity-provider, OAuth/OIDC, RBAC,
security review, customer-data, and operations evidence exists.
