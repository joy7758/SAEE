# SAEE On-call Approval Input Validator v0.1

on_call_approval_input_validator_v0_1: true
validator_scope: local_human_filled_on_call_input_pre_builder_check
default_validation_status: hold
default_input_complete: false
default_builder_ready: false
target_blocker_id: on_call_rotation
required_on_call_evidence_item_count: 3
blockers_closed_by_validator: 0
on_call_rotation_approved_by_validator: false
on_call_rotation_available_by_validator: false
on_call_rotation_started_by_validator: false
escalation_schedule_published_by_validator: false
incident_commander_assigned_by_validator: false
production_support_available_by_validator: false
support_contact_available_by_validator: false
customer_support_available_by_validator: false
sla_available_by_validator: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether the human-filled on-call evidence input is
complete and boundary-safe before it is passed to the existing on-call evidence
builder.

## Boundary

The validator is pre-builder input validation only. It does not start an
on-call rotation, publish an escalation schedule, assign an incident commander,
contact customers or vendors, start support operations, collect evidence, close
blockers, modify runtime/backend/kernel/API schema/private core, launch
product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/support_evidence/on_call_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_validation.md`
- script: `scripts/saee_on_call_approval_input_validator.py`
- smoke: `scripts/saee_on_call_approval_input_validator_smoke.py`
