# SAEE Auth/OIDC/RBAC Fixture Dry Run v0.1

Status: local fixture-only dry-run support for production-auth review.

This artifact records a deterministic local dry-run for OIDC-like claim
fixtures, negative auth cases, and RBAC route decisions. It exists to make the
future production identity-provider, OAuth/OIDC, and RBAC review path more
testable before real production-auth evidence is available.

## Recommendation Gate

answer: conditional

recommend_for_local_fixture_review: true
recommend_for_production_auth_implementation: false
recommend_for_production_launch: false

If a potential customer asks whether SAEE has production identity-provider,
OAuth/OIDC, or RBAC support, do not recommend this dry-run as production auth.
It is useful only as local evidence that the public-shell auth review path has
deterministic fixture coverage.

## What It Checks

- Token-like local fixtures contain the expected OIDC claim keys.
- Negative fixture cases reject missing tenant ID, wrong audience, expired
  token-like fixtures, and missing roles.
- Existing RBAC template route scopes make expected allow/deny decisions for
  owner, admin, evaluator operator, viewer, and support operator roles.

## What It Does Not Check

- It does not select a production identity provider.
- It does not contact an identity provider.
- It does not fetch JWKS.
- It does not validate signed production tokens.
- It does not approve OAuth/OIDC flow.
- It does not approve production RBAC policy.
- It does not enable production authentication.
- It does not enforce RBAC in production.
- It does not close production launch blockers.

## Entrypoints

```text
scripts/saee_auth_oidc_rbac_fixture_dry_run.py
scripts/saee_auth_oidc_rbac_fixture_dry_run_smoke.py
phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run/
```

Run:

```bash
python3 scripts/saee_auth_oidc_rbac_fixture_dry_run.py
python3 scripts/saee_auth_oidc_rbac_fixture_dry_run_smoke.py
```

## Boundary

```yaml
auth_oidc_rbac_fixture_dry_run_v0_1: true
evidence_scope: local_fixture_only_no_external_idp
local_fixture_token_validation_test_recorded: true
local_fixture_claims_mapping_reviewed: true
local_fixture_rbac_route_matrix_tested: true
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
identity_provider_contacted: false
jwks_fetched: false
tokens_validated_in_production: false
production_auth_enabled: false
rbac_enforced_in_production: false
blockers_closed_by_fixture_dry_run: 0
```

## Remaining Production Evidence

The production-auth blockers remain open until human-approved evidence exists
for a real identity provider, approved OAuth/OIDC flow, signed-token validation,
claims mapping, session expiry, auth failure handling, production RBAC policy,
least-privilege review, and admin recovery.
