# SAEE On-call Approval Input Prompt

on_call_approval_input_prompt_v0_1: true
status: hold_human_on_call_input_required
target_blocker_id: on_call_rotation
required_metadata_field_count: 5
completed_metadata_field_count: 0
required_on_call_evidence_item_count: 3
completed_on_call_evidence_item_count: 0
builder_ready: false
ready_for_evidence_builder: false
on_call_rotation_available: false
on_call_rotation_approved: false
on_call_rotation_started: false
escalation_schedule_published: false
incident_commander_assigned: false
support_operations_started: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`on_call_rotation` evidence input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `on_call_owner`
- `incident_operations_owner`
- `decision_summary`

## On-call Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Evidence Slot | Evidence Reference | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `escalation_schedule_defined` | set true only after human approval | required | required | required | required | required | false |
| `incident_commander_named` | set true only after human approval | required | required | required | required | required | false |
| `on_call_rotation_defined` | set true only after human approval | required | required | required | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/support_evidence/on_call_evidence_input.template.json phase_b_product/commercial_readiness/support_evidence/on_call_evidence_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_on_call_approval_input_validator.py --input phase_b_product/commercial_readiness/support_evidence/on_call_evidence_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, on-call rotation start,
escalation schedule publication, incident commander assignment, support
operations, customer/vendor contact, blocker closure, launch, and
production-readiness claims require separate approvals.

## Boundary

This prompt does not start on-call rotation, publish escalation schedules,
assign incident commanders, start support operations, contact customers or
vendors, execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, or claim production
readiness.
