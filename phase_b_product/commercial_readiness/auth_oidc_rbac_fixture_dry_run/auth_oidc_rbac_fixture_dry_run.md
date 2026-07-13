# SAEE Auth/OIDC/RBAC Fixture Dry Run v0.1

Status: local fixture dry-run only; production auth remains unavailable.

## Purpose

This dry-run records deterministic local checks for token-like OIDC claim
fixtures, negative auth cases, and the local RBAC route matrix. It is meant to
make future production-auth review more concrete without contacting an identity
provider or changing product behavior.

## What Was Checked

- Required claims: `iss, sub, aud, exp, iat, tenant_id, roles`
- Expected issuer: `https://idp.example.invalid/`
- Expected audience: `saee-controlled-preview`
- Local RBAC template: `phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json`
- Negative fixture cases for missing tenant ID, wrong audience, expiry, and missing roles.

## Fixture Claim Cases

| Case | Description | Expected Accept | Actual Accept | Passed |
| --- | --- | --- | --- | --- |
| OIDC-FIX-001 | valid local fixture claims | True | True | True |
| OIDC-FIX-002 | missing tenant_id claim | False | False | True |
| OIDC-FIX-003 | wrong audience claim | False | False | True |
| OIDC-FIX-004 | expired fixture token | False | False | True |
| OIDC-FIX-005 | missing roles claim | False | False | True |

## RBAC Route Cases

| Case | Route | Role | Expected Allowed | Actual Allowed | Passed |
| --- | --- | --- | --- | --- | --- |
| RBAC-FIX-001 | GET /operations/telemetry | owner | True | True | True |
| RBAC-FIX-002 | GET /operations/alerts | support_operator | True | True | True |
| RBAC-FIX-003 | POST /experiment/run | evaluator_operator | True | True | True |
| RBAC-FIX-004 | POST /experiment/create | viewer | False | False | True |
| RBAC-FIX-005 | POST /experiment/run | support_operator | False | False | True |
| RBAC-FIX-006 | GET /health |  | False | False | True |

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

This dry-run does not validate signed production tokens and does not close the
production identity-provider, OAuth/OIDC, or RBAC blockers.
