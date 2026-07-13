# SAEE SLA Approval Input Prompt

sla_approval_input_prompt_v0_1: true
status: hold_human_sla_input_required
target_blocker_id: sla
required_metadata_field_count: 5
completed_metadata_field_count: 0
required_sla_evidence_item_count: 6
completed_sla_evidence_item_count: 0
builder_ready: false
ready_for_evidence_builder: false
sla_available: false
sla_approved: false
sla_published: false
legal_review_completed: false
support_hours_published: false
response_targets_published: false
support_operations_started: false
source_sla_approval_input_prompt_html: phase_b_product/commercial_readiness/support_evidence/sla_approval_input_prompt.html
local_static_sla_approval_input_prompt_html: true
browser_readable_sla_approval_input_prompt: true
plain_language_sla_approval_input_prompt_v0_2: true
sla_human_review_step_count: 4
plain_language_status_label: SLA 还没有批准，也没有发布，不能对外承诺服务响应。
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`sla` approval input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `sla_terms_owner`
- `legal_reviewer_name`
- `decision_summary`

## SLA Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Evidence Slot | Owner Named | Legal/Commercial Review | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `exclusions_approved` | set true only after human approval | required | required | required | required | required | false |
| `human_approved_sla_terms` | set true only after human approval | required | required | required | required | required | false |
| `legal_review_completed` | set true only after human approval | required | required | required | required | required | false |
| `response_targets_approved` | set true only after human approval | required | required | required | required | required | false |
| `severity_definitions_approved` | set true only after human approval | required | required | required | required | required | false |
| `support_hours_approved` | set true only after human approval | required | required | required | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/support_evidence/sla_evidence_input.template.json phase_b_product/commercial_readiness/support_evidence/sla_evidence_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_sla_approval_input_validator.py --input phase_b_product/commercial_readiness/support_evidence/sla_evidence_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, SLA approval, SLA
publication, support-hours publication, response-target publication, legal
review completion, support operations, customer/vendor contact, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve SLA terms, publish SLA terms, complete legal
review, publish support hours, publish response targets, start support
operations, contact customers or vendors, execute the evidence builder, close
blockers, launch product, modify runtime/backend/kernel/API schema, expose
private core, or claim production readiness.
