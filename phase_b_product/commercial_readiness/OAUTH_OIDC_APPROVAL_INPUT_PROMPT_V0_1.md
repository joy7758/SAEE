# SAEE OAuth/OIDC Approval Input Prompt

oauth_oidc_approval_input_prompt_v0_1: true
status: hold_human_oauth_oidc_approval_input_required
target_blocker_ids: oauth_oidc
required_metadata_field_count: 3
completed_metadata_field_count: 0
required_oauth_oidc_evidence_item_count: 5
completed_oauth_oidc_evidence_item_count: 0
builder_ready: false
ready_for_evidence_builder: false
oauth_oidc_available: false
oauth_oidc_available_by_prompt: false
production_identity_provider_available: false
production_tokens_validated_by_codex: false
production_auth_ready: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
OAuth/OIDC approval portion of the Phase 1 identity/tenant evidence input before
validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `evidence_source_notes`

## OAuth/OIDC Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Codex May Fill |
| --- | --- | --- | --- |
| `oauth_oidc_flow_approved` | set true only after human approval | required | false |
| `token_validation_test_recorded` | set true only after human approval | required | false |
| `claims_mapping_reviewed` | set true only after human approval | required | false |
| `session_expiry_policy_approved` | set true only after human approval | required | false |
| `auth_failure_handling_reviewed` | set true only after human approval | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_oauth_oidc_approval_input_validator.py --input phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, identity-provider contact,
JWKS fetch, production token validation, authentication enablement, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve OAuth/OIDC, fill evidence, contact identity
providers, fetch JWKS, validate production tokens, enable authentication,
execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, or claim production
readiness.
