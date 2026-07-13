# SAEE On-call Evidence Builder v0.1

Status: local builder available; default output is hold.

on_call_evidence_builder_v0_1: true
builder_scope: human_filled_on_call_rotation_to_production_support_evidence
required_evidence_item_count: 3
default_output_status: hold
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0
production_support_available: false

## Purpose

This builder converts a human-filled on-call rotation input into local
production support/SLA evidence fields for the `on_call_rotation` group. It is
a commercial-readiness evidence intake surface, not support execution or
incident operations.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false
support_operations_started: false
production_on_call_claim_published: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/support_evidence/on_call_evidence_input.template.json`
- builder output: `phase_b_product/commercial_readiness/support_evidence/on_call_evidence_builder_output.local.json`
- support evidence output: `phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_on_call.local.json`
- report: `phase_b_product/commercial_readiness/support_evidence/on_call_evidence_builder_report.md`
- script: `scripts/saee_on_call_evidence_builder.py`
- smoke: `scripts/saee_on_call_evidence_builder_smoke.py`
