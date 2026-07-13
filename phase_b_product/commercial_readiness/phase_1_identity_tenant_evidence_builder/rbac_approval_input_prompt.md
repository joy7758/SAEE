# SAEE RBAC Approval Input Prompt

rbac_approval_input_prompt_v0_1: true
status: hold_human_rbac_approval_input_required
target_blocker_ids: rbac
required_metadata_field_count: 3
completed_metadata_field_count: 0
required_rbac_evidence_item_count: 5
completed_rbac_evidence_item_count: 0
builder_ready: false
ready_for_evidence_builder: false
rbac_available: false
rbac_available_by_prompt: false
rbac_enforced_in_production: false
production_auth_ready: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the RBAC
approval portion of the Phase 1 identity/tenant evidence input before validator
use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `evidence_source_notes`

## RBAC Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Codex May Fill |
| --- | --- | --- | --- |
| `rbac_policy_approved` | set true only after human approval | required | false |
| `role_matrix_reviewed` | set true only after human approval | required | false |
| `tenant_role_boundary_reviewed` | set true only after human approval | required | false |
| `least_privilege_reviewed` | set true only after human approval | required | false |
| `admin_recovery_policy_reviewed` | set true only after human approval | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_rbac_approval_input_validator.py --input phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, RBAC enforcement, production
auth enablement, blocker closure, launch, and production-readiness claims require
separate approvals.

## Boundary

This prompt does not approve RBAC, fill evidence, enforce production RBAC,
enable authentication, contact identity providers, fetch JWKS, validate
production tokens, execute the evidence builder, close blockers, launch product,
modify runtime/backend/kernel/API schema, expose private core, or claim
production readiness.
