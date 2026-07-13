# SAEE Refund Policy Approval Input Prompt v0.1

Status: hold_human_refund_policy_input_required.

plain_language_refund_policy_entry_v0_2: true
plain_language_status_label: 退款政策还没有批准，也没有发布
plain_language_next_action: 先由人审退款规则、取消流程、试用转付费和服务故障补偿边界，再填写本地证据模板。
plain_language_stop_point: 只到本地证据准备为止；没有单独批准，不发布退款政策、不处理退款、不配置支付平台退款、不收款、不关闭阻塞项。
refund_policy_human_review_step_count: 4

This is a local, human-facing input prompt for the `refund_policy` production
blocker. It tells commercial, accounting, legal, support, billing, payment,
and tenant-boundary owners which source-backed fields must be filled before
the existing refund-policy evidence builder can be considered in a separate
request.

It does not publish a refund policy, approve cancellation handling, process
refunds, configure payment-provider refund handling, collect payment, validate
revenue, close blockers, launch product, or claim production readiness.

## Summary

- refund_policy_approval_input_prompt_v0_1: true
- prompt_type: saee_refund_policy_approval_input_prompt
- prompt_scope: local_human_refund_policy_input_prompt_only
- status: hold_human_refund_policy_input_required
- target_blocker_ids: refund_policy
- required_metadata_field_count: 11
- required_refund_policy_evidence_item_count: 5
- completed_metadata_field_count: 0
- completed_refund_policy_evidence_item_count: 0
- builder_ready: false
- ready_for_evidence_builder: false
- refund_policy_available: false
- refund_policy_approved: false
- refund_policy_published: false
- refund_processed: false
- refund_issued_to_customer: false
- cancellation_process_available: false
- trial_conversion_policy_available: false
- service_failure_remedy_available: false
- refund_request_workflow_available: false
- payment_provider_refund_configured: false
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
| accounting_owner | true | false |
| legal_owner | true | false |
| support_owner | true | false |
| billing_owner | true | false |
| payment_owner | true | false |
| tenant_boundary_owner | true | false |
| review_record_reference | true | false |
| decision_summary | true | false |

## Refund Policy Evidence Keys

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| refund_policy_approved | true only after human approval | required | required | required | required | false |
| cancellation_process_approved | true only after human approval | required | required | required | required | false |
| trial_conversion_policy_approved | true only after human approval | required | required | required | required | false |
| service_failure_remedy_boundary_approved | true only after human approval | required | required | required | required | false |
| support_escalation_route_defined | true only after human approval | required | required | required | required | false |

## Commands

Copy the template:

```bash
cp phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_input.template.json phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_input.human_filled.local.json
```

Only after a separate human-approved evidence-builder execution request:

```bash
python3 scripts/saee_refund_policy_evidence_builder.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_input.human_filled.local.json
```

## Boundary

- codex_published_refund_policy: false
- codex_processed_refund: false
- codex_configured_refund_handling: false
- refund_policy_claim_published: false
- refund_policy_completed_by_codex: false
- refund_policy_execution_authorized: false
- refund_policy_available: false
- refund_policy_approved: false
- refund_policy_published: false
- refund_processed: false
- refund_issued_to_customer: false
- cancellation_process_available: false
- trial_conversion_policy_available: false
- service_failure_remedy_available: false
- refund_request_workflow_available: false
- payment_provider_refund_configured: false
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

Copy the refund-policy evidence template, fill all metadata fields, approve each refund-policy evidence key only with source-backed human review, add source notes and artifact references, then stop. Evidence-builder execution, refund-policy publication, refund processing, payment-provider refund configuration, payment collection, revenue validation, blocker closure, and production claims remain separate.
