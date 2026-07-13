# SAEE Customer Validation Approval Input Prompt v0.1

customer_validation_approval_input_prompt_v0_1: true
prompt_scope: local_human_customer_validation_input_prompt_only
status: hold_human_customer_validation_input_required
target_blocker_ids: pilot_results,customer_validated
source_customer_validation_approval_input_prompt_html: phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html
local_static_customer_validation_approval_input_prompt_html: true
browser_readable_customer_validation_approval_input_prompt: true
plain_language_customer_validation_approval_input_prompt_v0_2: true
customer_validation_human_review_step_count: 5
plain_language_status_label: 客户验证还没有完成，也不能对外声称已验证。
required_review_key_count: 25
required_session_text_field_count: 5
required_session_score_field_count: 4
required_session_boundary_false_key_count: 5
completed_session_count: 0
builder_ready: false
pilot_results_recorded: false
customer_validation_approved: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt tells a human reviewer exactly how to fill the local customer
validation input before running the existing approval input validator and
before requesting evidence-builder execution.

## Boundary

Prompt only. It does not contact customers, run pilot sessions, infer missing
results, collect customer data, publish validation claims, create testimonials
or case studies, close blockers, modify runtime/backend/kernel/API schema or
private core, launch product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json`
- prompt JSON: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.local.json`
- prompt markdown: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.md`
- prompt HTML: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html`
- validator output: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.local.json`
- script: `scripts/saee_customer_validation_approval_input_prompt.py`
- smoke: `scripts/saee_customer_validation_approval_input_prompt_smoke.py`
