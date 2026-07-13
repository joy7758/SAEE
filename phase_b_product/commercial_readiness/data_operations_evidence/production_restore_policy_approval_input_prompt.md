# SAEE Production Restore Policy Approval Input Prompt

production_restore_policy_approval_input_prompt_v0_1: true
status: hold_human_restore_policy_approval_input_required
target_blocker_id: production_restore_policy
required_metadata_field_count: 7
completed_metadata_field_count: 0
required_policy_evidence_item_count: 6
completed_policy_evidence_item_count: 0
builder_ready: false
production_restore_policy_available: false
production_restore_policy_approved: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`production_restore_policy` approval input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `data_operations_owner`
- `security_owner`
- `privacy_legal_owner`
- `incident_response_owner`
- `decision_summary`

## Policy Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Evidence Slot | Codex May Fill |
| --- | --- | --- | --- | --- |
| `backup_retention_policy_approved` | set true only after human approval | required | required | false |
| `credential_secret_exclusion_reviewed` | set true only after human approval | required | required | false |
| `customer_notification_boundary_approved` | set true only after human approval | required | required | false |
| `incident_response_handoff_approved` | set true only after human approval | required | required | false |
| `production_restore_policy_approved` | set true only after human approval | required | required | false |
| `tenant_restore_boundary_approved` | set true only after human approval | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_production_restore_policy_approval_input_validator.py --input phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, restore-policy publication,
live restore, blocker closure, launch, and production-readiness claims require
separate approvals.

## Boundary

This prompt does not approve policy, fill evidence, run restore, touch live data
paths, contact customers or vendors, execute the evidence builder, close
blockers, launch product, modify runtime/backend/kernel/API schema, expose
private core, or claim production readiness.
