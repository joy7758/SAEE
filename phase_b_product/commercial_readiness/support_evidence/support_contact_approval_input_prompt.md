# SAEE Support Contact Approval Input Prompt

support_contact_approval_input_prompt_v0_1: true
status: hold_human_support_contact_input_required
target_blocker_id: support_contact
required_metadata_field_count: 4
completed_metadata_field_count: 0
required_support_contact_evidence_item_count: 5
completed_support_contact_evidence_item_count: 0
candidate_contact_slot_count: 2
minimum_completed_contact_slot_count: 1
completed_contact_slot_count: 0
builder_ready: false
ready_for_evidence_builder: false
support_contact_available: false
support_contact_approved: false
support_contact_configured: false
support_contact_published: false
support_contact_test_performed: false
customer_facing_support_contact_configured: false
support_operations_started: false
source_support_contact_approval_input_prompt_html: phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_prompt.html
local_static_support_contact_approval_input_prompt_html: true
browser_readable_support_contact_approval_input_prompt: true
plain_language_support_contact_approval_input_prompt_v0_2: true
support_contact_human_review_step_count: 4
plain_language_status_label: 客户支持入口还没有批准，也没有启用。
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`support_contact` decision input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `selected_support_contact_channel`
- `decision_summary`

## Support Contact Evidence Keys To Review

| Evidence Key | Review Flag | Source Note | Codex May Fill |
| --- | --- | --- | --- |
| `abuse_handling_path_defined` | set true only after human approval | required | false |
| `customer_facing_support_contact_configured` | set true only after human approval | required | false |
| `customer_notice_route_defined` | set true only after human approval | required | false |
| `support_contact_owner_named` | set true only after human approval | required | false |
| `support_contact_test_recorded` | set true only after human approval | required | false |

## Candidate Contact Slots To Fill

| Slot ID | Contact Channel | Redacted Display Value | Owner Named | Abuse Handling | Customer Notice Route | Test Plan | Source Note | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `support_contact_candidate_a` | required | required | required | required | required | required | required | false |
| `support_contact_candidate_b` | required | required | required | required | required | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_support_contact_approval_input_validator.py --input phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, support-contact approval,
support-contact publication, support-contact tests, customer/vendor contact,
blocker closure, launch, and production-readiness claims require separate
approvals.

## Boundary

This prompt does not approve, configure, publish, or test a support contact;
contact customers or vendors; execute the evidence builder; close blockers;
launch product; modify runtime/backend/kernel/API schema; expose private core;
or claim production readiness.
