# SAEE Privacy Legal + DPA Approval Input Prompt v0.1

privacy_legal_dpa_approval_input_prompt_v0_1: true
status: hold_human_privacy_legal_dpa_input_required
target_blocker_ids: privacy_legal_review,data_processing_agreement
source_privacy_legal_dpa_approval_input_prompt_html: phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_prompt.html
local_static_privacy_legal_dpa_approval_input_prompt_html: true
browser_readable_privacy_legal_dpa_approval_input_prompt: true
plain_language_privacy_legal_dpa_approval_input_prompt_v0_2: true
privacy_legal_dpa_human_review_step_count: 5
plain_language_status_label: 隐私法律审查和 DPA 还没有完成，也不能声称可以正式处理客户数据。
required_metadata_field_count: 7
completed_metadata_field_count: 0
required_privacy_legal_evidence_item_count: 7
required_dpa_evidence_item_count: 6
required_total_evidence_item_count: 13
completed_total_evidence_item_count: 0
builder_ready: false
privacy_legal_review_completed: false
data_processing_agreement_available: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives human legal and privacy reviewers the shortest safe path for
filling the `privacy_legal_review` and `data_processing_agreement` input before
any separate evidence-builder request.

It is a prompt only. It does not perform legal review, create or approve a DPA,
contact legal counsel, send a DPA, process customer data, publish terms,
publish a privacy notice, close blockers, or claim production readiness.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `legal_owner`
- `privacy_owner`
- `dpa_owner`
- `review_record_reference`
- `decision_summary`

## Privacy Legal Evidence Keys

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| `privacy_notice_approved` | set true only after human approval | required | required | required | required | false |
| `terms_of_service_approved` | set true only after human approval | required | required | required | required | false |
| `data_inventory_reviewed` | set true only after human approval | required | required | required | required | false |
| `retention_policy_approved` | set true only after human approval | required | required | required | required | false |
| `subprocessor_inventory_reviewed` | set true only after human approval | required | required | required | required | false |
| `customer_data_processing_approved` | set true only after human approval | required | required | required | required | false |
| `legal_reviewer_recorded` | set true only after human approval | required | required | required | required | false |

## DPA Evidence Keys

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| `dpa_terms_approved` | set true only after human approval | required | required | required | required | false |
| `controller_processor_roles_defined` | set true only after human approval | required | required | required | required | false |
| `subprocessor_terms_approved` | set true only after human approval | required | required | required | required | false |
| `breach_notice_terms_approved` | set true only after human approval | required | required | required | required | false |
| `deletion_or_return_terms_approved` | set true only after human approval | required | required | required | required | false |
| `customer_dpa_template_available` | set true only after human approval | required | required | required | required | false |

## Commands

Copy the template:

```bash
cp phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_input.template.json phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_input.human_filled.local.json
```

Builder command, only after a separate explicit execution request:

```bash
python3 scripts/saee_privacy_legal_dpa_evidence_builder.py --input phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_input.human_filled.local.json
```

## Boundary

- builder_ready: false
- privacy_legal_review_completed: false
- data_processing_agreement_available: false
- legal_review_execution_authorized: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- legal_counsel_contacted: false
- customer_data_processed: false
- dpa_sent_to_customer: false
- codex_performed_legal_review: false
- codex_created_dpa: false
