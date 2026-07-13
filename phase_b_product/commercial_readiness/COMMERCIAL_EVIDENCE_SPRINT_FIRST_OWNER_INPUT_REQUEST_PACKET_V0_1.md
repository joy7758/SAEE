# SAEE First Owner Input Request Packet

first_owner_input_request_packet_v0_1: true
status: hold_human_first_owner_input_request_required
action_id: NEXT-001
first_blocker_id: support_contact
sequence_step_id: SEQ-001
request_packet_ready: true
required_human_field_count: 5
completed_human_field_count: 0
missing_human_field_count: 5
owner_assigned_by_codex: false
owner_contacted_by_codex: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_request_packet: 0
production_ready: false
customer_validated: false
product_launched: false
local_static_first_owner_input_request_html: true
browser_readable_first_owner_input_request: true
copy_ready_blank_json_template_in_html: true
source_first_owner_input_request_html: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.html
source_first_owner_input_template: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json
recommended_human_filled_input_path: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json

## Purpose

This packet turns the current commercial next action into a bounded human input request for the `support_contact` first-owner step.

## Required Human Fields

- `assigned_human_owner`
- `owner_contact_reference`
- `target_review_date`
- `owner_acknowledged_scope`
- `human_approval_reference`

## Human Procedure

1. Fill the five required fields in `first_owner_input_completion.csv` or provide them to the completion helper command.
2. Generate `first_owner_input.human_filled.local.json` with the completion helper.
3. Run the first-owner input validator on the generated JSON.
4. Stop. Evidence collection and blocker closure require later separate approvals.

## Browser-Readable Entry

`phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.html`

## Blank JSON Template

A human may fill the blank local template and save it as the recommended human-filled input path before running the validator.

- source template: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json`
- recommended filled input path: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json`
- do not include customer secrets, passwords, external account credentials, private-core content, or raw customer data.

## Command Template

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \
  --single-blocker-id support_contact \
  --assigned-human-owner "<human owner>" \
  --owner-contact-reference "<internal owner reference>" \
  --target-review-date "YYYY-MM-DD" \
  --owner-acknowledged-scope true \
  --human-approval-reference "<human approval record>" \
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

## Validator Command

```bash
python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py
```

## Boundary

This packet does not assign an owner, contact an owner, contact customers or vendors, collect evidence, execute tasks, close blockers, launch product, or claim production readiness.
