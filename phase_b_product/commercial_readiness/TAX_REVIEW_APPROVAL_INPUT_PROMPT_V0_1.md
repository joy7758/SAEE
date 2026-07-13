# SAEE Tax Review Approval Input Prompt v0.1

Status: hold_human_tax_review_input_required.

plain_language_tax_review_entry_v0_2: true
plain_language_status_label: 税务审查还没有完成，也没有启用收税
plain_language_next_action: 先由人审目标地区、税务责任、发票文字和币种规则，再填写本地证据模板。
plain_language_stop_point: 只到本地证据准备为止；没有单独批准，不联系税务或法务顾问、不配置税率、不开始收税、不收款、不关闭阻塞项。
tax_review_human_review_step_count: 4

This is a local, human-facing input prompt for the `tax_review` production
blocker. It tells commercial, tax, accounting, legal, and billing owners which
source-backed fields must be filled before the existing tax-review evidence
builder can be considered in a separate request.

It does not contact tax advisors or legal counsel, complete tax review,
configure tax rates, start tax collection, collect payment, validate revenue,
close blockers, launch product, or claim production readiness.

## Summary

- tax_review_approval_input_prompt_v0_1: true
- prompt_type: saee_tax_review_approval_input_prompt
- prompt_scope: local_human_tax_review_input_prompt_only
- status: hold_human_tax_review_input_required
- target_blocker_ids: tax_review
- required_metadata_field_count: 9
- required_tax_review_evidence_item_count: 5
- completed_metadata_field_count: 0
- completed_tax_review_evidence_item_count: 0
- builder_ready: false
- ready_for_evidence_builder: false
- tax_review_completed: false
- tax_collection_ready: false
- tax_rate_configured: false
- tax_collection_started: false
- tax_exemption_process_available: false
- invoice_wording_published: false
- currency_policy_published: false
- customer_payment_collected: false
- revenue_validated: false
- blockers_closed_by_prompt: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Human Metadata To Fill

| Field | Required | Codex May Fill |
| --- | --- | --- |
| human_reviewer_name | true | false |
| review_date | true | false |
| commercial_owner | true | false |
| tax_owner | true | false |
| accounting_owner | true | false |
| legal_owner | true | false |
| billing_owner | true | false |
| review_record_reference | true | false |
| decision_summary | true | false |

## Tax Review Evidence Keys

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| tax_obligations_reviewed | true only after human approval | required | required | required | required | false |
| target_jurisdictions_reviewed | true only after human approval | required | required | required | required | false |
| tax_collection_approval_recorded | true only after human approval | required | required | required | required | false |
| invoice_wording_approved | true only after human approval | required | required | required | required | false |
| currency_policy_approved | true only after human approval | required | required | required | required | false |

## Commands

Copy the template:

```bash
cp phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_input.template.json phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_input.human_filled.local.json
```

Only after a separate human-approved evidence-builder execution request:

```bash
python3 scripts/saee_tax_review_evidence_builder.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_input.human_filled.local.json
```

## Boundary

- codex_contacted_tax_advisor: false
- codex_contacted_legal_counsel: false
- codex_configured_tax_collection: false
- codex_started_tax_collection: false
- tax_review_claim_published: false
- tax_review_completed_by_codex: false
- tax_review_execution_authorized: false
- tax_review_completed: false
- tax_rate_configured: false
- tax_collection_started: false
- tax_exemption_process_available: false
- invoice_wording_published: false
- currency_policy_published: false
- tax_advisor_contacted: false
- legal_counsel_contacted: false
- customer_payment_collected: false
- revenue_validated: false
- production_billing_enabled: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false

## Next Human Action

Copy the tax-review evidence template, fill all metadata fields, approve each tax-review evidence key only with source-backed human review, add source notes and artifact references, then stop. Evidence-builder execution, tax-advisor contact, legal counsel contact, tax-rate configuration, tax collection, payment collection, revenue validation, blocker closure, and production claims remain separate.
