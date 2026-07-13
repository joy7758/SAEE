# SAEE JWT Preview Operator Packet v0.1

Status: controlled-preview token generator available; production OAuth/OIDC remains false.

## Purpose

JWT Preview Operator Packet v0.1 gives a human operator a local way to mint a
short-lived HS256 bearer token for the existing SAEE controlled-preview JWT
guard.

It improves controlled-preview usability because a reviewer can now start the
local API shell with preview JWT auth enabled, generate a signed local token,
and call protected public-shell routes without hand-writing JWT segments.

It does not contact an identity provider, fetch JWKS, validate production
tokens, implement OAuth/OIDC, manage accounts, process customer data, expose
private core, close production auth blockers, or claim production readiness.

## Operator Flow

Set local controlled-preview environment variables:

```bash
export SAEE_REQUIRE_JWT_PREVIEW_AUTH=true
export SAEE_SYNTHETIC_DATA_ONLY=true
export SAEE_PREVIEW_JWT_ISSUER="https://preview-idp.example.invalid/"
export SAEE_PREVIEW_JWT_AUDIENCE="saee-controlled-preview"
export SAEE_PREVIEW_JWT_HS256_SECRET="<local-controlled-preview-secret>"
export SAEE_REQUIRE_TENANT_ID=true
export SAEE_ALLOWED_TENANT_IDS="tenant-alpha"
export SAEE_REQUIRE_RBAC_ROLE=true
export SAEE_RBAC_POLICY_PATH="phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json"
```

Generate a local preview token:

```bash
python3 scripts/saee_jwt_preview_token.py \
  --subject preview-user-001 \
  --tenant-id tenant-alpha \
  --roles evaluator_operator \
  --ttl-seconds 3600
```

Use JSON output when an operator needs the bearer header and claim summary:

```bash
python3 scripts/saee_jwt_preview_token.py \
  --subject preview-user-001 \
  --tenant-id tenant-alpha \
  --roles evaluator_operator,viewer \
  --ttl-seconds 3600 \
  --json
```

The CLI reads `SAEE_PREVIEW_JWT_HS256_SECRET` from the process environment. It
does not write the secret to disk and the smoke test verifies that the secret is
not printed in CLI output.

## Local Protected Route Example

Start the API with the same environment, then use the token as a bearer header:

```bash
TOKEN="$(python3 scripts/saee_jwt_preview_token.py \
  --subject preview-user-001 \
  --tenant-id tenant-alpha \
  --roles evaluator_operator \
  --ttl-seconds 3600)"

curl \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-SAEE-Role: evaluator_operator" \
  http://127.0.0.1:8000/ready
```

This is a controlled-preview public-shell check only. It is not production
identity-provider authentication.

## Boundary

```yaml
jwt_preview_operator_packet_v0_1: true
controlled_preview_token_generator_available: true
default_required: false
uses_existing_jwt_preview_guard: true
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
blockers_closed_by_operator_packet: 0
```

## Verification

```bash
python3 scripts/saee_jwt_preview_operator_packet_smoke.py
python3 scripts/saee_jwt_preview_auth_smoke.py
python3 scripts/mainline_guard.py
```

Expected:

```text
SAEE_JWT_PREVIEW_OPERATOR_PACKET_SMOKE: PASS
```

## Non-Claims

This packet is not production OAuth/OIDC, SSO, JWKS validation, account
lifecycle, customer authorization approval, production RBAC, customer
validation, product launch evidence, or production-auth blocker closure.
