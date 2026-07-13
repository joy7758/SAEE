# SAEE Operations On-call Rotation Approval Input Prompt

operations_on_call_rotation_approval_input_prompt_v0_1: true
status: hold_human_operations_on_call_rotation_input_required
target_blocker_id: on_call_rotation
required_metadata_field_count: 5
completed_metadata_field_count: 0
required_on_call_rotation_evidence_item_count: 3
completed_on_call_rotation_evidence_item_count: 0
builder_ready: false
on_call_rotation_available: false
on_call_rotation_approved: false
on_call_rotation_started: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`on_call_rotation` operations approval input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `on_call_rotation_owner`
- `operations_reviewer_name`
- `decision_summary`

## On-call Rotation Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Evidence Slot | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| `escalation_schedule_defined` | set true only after human approval | required | required | required | required | false |
| `incident_commander_named` | set true only after human approval | required | required | required | required | false |
| `on_call_rotation_defined` | set true only after human approval | required | required | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_input.template.json phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_operations_on_call_rotation_approval_input_validator.py --input phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, on-call activation,
escalation schedule publication, incident commander assignment, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve on-call rotation, fill evidence, publish
escalation schedules, assign incident commanders, touch live operations paths,
contact customers or vendors, execute the evidence builder, close blockers,
launch product, modify runtime/backend/kernel/API schema, expose private core,
or claim production readiness.
