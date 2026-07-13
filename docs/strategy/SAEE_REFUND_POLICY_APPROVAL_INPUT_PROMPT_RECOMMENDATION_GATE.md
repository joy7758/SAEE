# SAEE Refund Policy Approval Input Prompt Recommendation Gate

answer: recommend_for_human_refund_policy_input_prompt

reason: The prompt makes the refund-policy approval evidence requirements
agent-readable, browser-readable, and human-fillable without publishing a
refund policy, approving cancellation handling, processing refunds, configuring
payment refund handling, collecting payment, or executing refund work.

plain_language_refund_policy_entry_v0_2: true
plain_language_status_label: 退款政策还没有批准，也没有发布
plain_language_next_action: 先由人审退款规则、取消流程、试用转付费和服务故障补偿边界，再填写本地证据模板。
plain_language_stop_point: 只到本地证据准备为止；没有单独批准，不发布退款政策、不处理退款、不配置支付平台退款、不收款、不关闭阻塞项。

recommend_for_refund_policy_publication: false
recommend_for_cancellation_process_approval: false
recommend_for_refund_processing: false
recommend_for_payment_provider_refund_configuration: false
recommend_for_payment_collection: false
recommend_for_revenue_validation: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

status: hold_human_refund_policy_input_required
required_metadata_field_count: 11
required_refund_policy_evidence_item_count: 5
builder_ready: false
ready_for_evidence_builder: false
refund_policy_available: false
refund_policy_approved: false
refund_policy_published: false
refund_processed: false
refund_issued_to_customer: false
cancellation_process_available: false
trial_conversion_policy_available: false
service_failure_remedy_available: false
refund_request_workflow_available: false
payment_provider_refund_configured: false
customer_payment_collected: false
revenue_validated: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

boundary:
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- refund_policy_published: false
- refund_processed: false
- payment_provider_refund_configured: false
- customer_payment_collected: false
- revenue_validated: false

next_action: Human owners may copy the refund-policy evidence template and
fill the required fields. Evidence-builder execution remains a separate step.
