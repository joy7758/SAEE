# SAEE Production Identity Provider Decision Packet v0.1

Status: ready_for_human_review_not_execution.

This packet narrows the first Phase 1 commercial blocker,
`production_identity_provider`, into a human decision surface. It helps a human
owner compare identity-provider options and decide whether the existing Phase 1
evidence input should be filled.

It does not select or contact an identity provider, fetch JWKS, validate
production tokens, enable production authentication, enforce RBAC, modify
backend behavior, close blockers, launch product, contact customers, or claim
production readiness.

## Target Blocker

```text
blocker_target: production_identity_provider
owner_lane: engineering_security
status: ready_for_human_review_not_execution
production_identity_provider_available: false
blockers_closed_by_packet: false
```

## Evidence Mapping

| Evidence key | Blocker | Builder path | Requirement |
| --- | --- | --- | --- |
| `production_identity_provider_selected` | `production_identity_provider` | `evidence_review.production_identity_provider_selected` | human source note required |
| `identity_provider_admin_owner_named` | `production_identity_provider` | `evidence_review.identity_provider_admin_owner_named` | human source note required |
| `oidc_issuer_verified` | `production_identity_provider` | `evidence_review.oidc_issuer_verified` | human source note required |
| `oidc_audience_approved` | `production_identity_provider` | `evidence_review.oidc_audience_approved` | human source note required |
| `jwks_rotation_policy_reviewed` | `production_identity_provider` | `evidence_review.jwks_rotation_policy_reviewed` | human source note required |

## Human Review Steps

1. List one to three candidate identity providers in the template.
2. Record the human owner for production identity administration.
3. Review issuer, audience, and JWKS rotation evidence.
4. Record a rollback or disable plan.
5. Only after approval, copy source-backed values into the Phase 1 evidence
   builder input.

## Existing Builder

Use the existing builder after human evidence exists:

```bash
python3 scripts/saee_phase1_identity_tenant_evidence_builder.py --json \
  --input phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json
```

## Non-Claims

- production_identity_provider_available: false
- oauth_oidc_available: false
- rbac_available: false
- production_auth_ready: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- blockers_closed_by_packet: false
