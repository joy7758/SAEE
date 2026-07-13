# SAEE Invoice Process Approval Input Prompt v0.1

Status: hold_human_invoice_process_input_required.

plain_language_invoice_process_review_entry_v0_2: true
plain_language_status_label: 发票流程还没有批准，也没有启用
plain_language_next_action: 先由人审发票模板、开票流程、合同和对账边界，再填写本地证据模板。
plain_language_stop_point: 只到本地证据准备为止；没有单独批准，不创建发票、不发送发票、不签合同、不对账、不收款、不关闭阻塞项。
invoice_process_human_review_step_count: 4

This is a local, human-facing input prompt for the `invoice_process`
production blocker. It tells commercial, invoice, accounting, and support
owners which source-backed fields must be filled before the existing
invoice-process evidence builder can be considered in a separate request.

It does not create invoice templates, create or send invoices, sign contracts,
perform reconciliation, contact customers, collect payment, validate revenue,
close blockers, launch product, or claim production readiness.

## Summary

- invoice_process_approval_input_prompt_v0_1: true
- prompt_type: saee_invoice_process_approval_input_prompt
- prompt_scope: local_human_invoice_process_input_prompt_only
- status: hold_human_invoice_process_input_required
- target_blocker_ids: invoice_process
- required_metadata_field_count: 8
- required_invoice_process_evidence_item_count: 6
- completed_metadata_field_count: 0
- completed_invoice_process_evidence_item_count: 0
- builder_ready: false
- ready_for_evidence_builder: false
- invoice_process_approved: false
- invoice_process_ready: false
- invoice_created: false
- invoice_template_published: false
- invoice_sent_to_customer: false
- enterprise_contract_signed: false
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
| invoice_owner | true | false |
| accounting_owner | true | false |
| support_owner | true | false |
| review_record_reference | true | false |
| decision_summary | true | false |

## Invoice Process Evidence Keys

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| invoice_owner_named | true only after human approval | required | required | required | required | false |
| invoice_workflow_approved | true only after human approval | required | required | required | required | false |
| contract_handoff_defined | true only after human approval | required | required | required | required | false |
| billing_support_handoff_defined | true only after human approval | required | required | required | required | false |
| payment_reconciliation_tested | true only after human approval | required | required | required | required | false |
| bookkeeping_review_completed | true only after human approval | required | required | required | required | false |

## Commands

Copy the template:

```bash
cp phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_input.template.json phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_input.human_filled.local.json
```

Only after a separate human-approved evidence-builder execution request:

```bash
python3 scripts/saee_invoice_process_evidence_builder.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_input.human_filled.local.json
```

## Boundary

- codex_created_invoice: false
- codex_sent_invoice: false
- codex_signed_contract: false
- codex_performed_reconciliation: false
- invoice_process_claim_published: false
- invoice_process_completed_by_codex: false
- invoice_process_execution_authorized: false
- invoice_process_approved: false
- invoice_process_ready: false
- invoice_created: false
- invoice_template_published: false
- invoice_sent_to_customer: false
- enterprise_contract_signed: false
- payment_provider_configured: false
- checkout_enabled: false
- payment_link_created: false
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

先读发票流程审批输入提示，再复制模板并由人填写真实审批信息。填完后停止；evidence builder 执行、发票模板创建、发票发送、合同签署、对账、客户联系、收款、收入验证、阻塞项关闭和生产可用声明都需要单独批准。
