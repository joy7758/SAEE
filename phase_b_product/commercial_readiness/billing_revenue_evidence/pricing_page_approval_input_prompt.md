# SAEE Pricing Page Approval Input Prompt v0.1

Status: hold_human_pricing_page_input_required.

plain_language_pricing_page_review_entry_v0_2: true
plain_language_status_label: 定价页还没有批准，也没有发布
plain_language_next_action: 先由人审定价文案和价格边界，再填写本地证据模板。
plain_language_stop_point: 只到本地校验为止；没有单独批准，不发布定价页、不生成销售报价、不配置支付、不关闭阻塞项。
pricing_page_human_review_step_count: 4

This is a local, human-facing input prompt for the `pricing_page` production
blocker. It tells commercial, product, accounting, legal, and billing owners
which source-backed fields must be filled before the existing pricing-page
validator or evidence builder can be considered.

It does not approve pricing copy, publish a pricing page, create a sales offer,
configure a payment provider, enable checkout, collect payment, validate
revenue, close blockers, launch product, or claim production readiness.

## Summary

- pricing_page_approval_input_prompt_v0_1: true
- prompt_type: saee_pricing_page_approval_input_prompt
- prompt_scope: local_human_pricing_page_input_prompt_only
- status: hold_human_pricing_page_input_required
- target_blocker_ids: pricing_page
- required_metadata_field_count: 9
- required_pricing_page_evidence_item_count: 5
- completed_metadata_field_count: 0
- completed_pricing_page_evidence_item_count: 0
- builder_ready: false
- ready_for_validator: false
- ready_for_evidence_builder: false
- pricing_page_available: false
- pricing_page_published: false
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
| product_owner | true | false |
| accounting_owner | true | false |
| legal_owner | true | false |
| billing_owner | true | false |
| review_record_reference | true | false |
| decision_summary | true | false |

## Pricing Page Evidence Keys

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| human_approved_pricing_page_copy | true only after human approval | required | required | required | required | false |
| approved_plan_and_usage_terms | true only after human approval | required | required | required | required | false |
| legal_review_completed | true only after human approval | required | required | required | required | false |
| production_readiness_non_claim_reviewed | true only after human approval | required | required | required | required | false |
| pricing_page_publication_approval_recorded | true only after human approval | required | required | required | required | false |

## Commands

Copy the template:

```bash
cp phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.template.json phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json
```

After human input is complete, validate it locally:

```bash
python3 scripts/saee_pricing_page_approval_input_validator.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json
```

Only after a separate human-approved evidence-builder execution request:

```bash
python3 scripts/saee_pricing_page_evidence_builder.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json
```

## Boundary

- codex_approved_pricing_page: false
- codex_published_pricing_page: false
- codex_sent_sales_offer: false
- codex_contacted_customer: false
- codex_contacted_payment_provider: false
- codex_configured_payment_provider: false
- codex_enabled_checkout: false
- codex_collected_payment: false
- pricing_page_claim_published: false
- sales_offer_generated: false
- payment_provider_configured: false
- checkout_enabled: false
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

先读定价页草稿和审批输入提示，再复制模板并由人填写真实审批信息。填完后只运行本地 validator；不要发布定价页、生成销售报价、配置支付、执行 evidence builder、联系客户或声明生产可用。
