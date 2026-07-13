# SAEE Invoice Process Approval Input Validator v0.1

invoice_process_approval_input_validator_v0_1: true
validator_scope: local_human_filled_invoice_process_input_pre_builder_check
default_validation_status: hold
default_input_complete: false
default_builder_ready: false
target_blocker_id: invoice_process
required_invoice_process_evidence_item_count: 6
blockers_closed_by_validator: 0
invoice_process_approved_by_validator: false
invoice_process_ready_by_validator: false
invoice_created_by_validator: false
invoice_template_published_by_validator: false
invoice_sent_to_customer_by_validator: false
contract_signed_by_validator: false
reconciliation_performed_by_validator: false
customer_payment_collected_by_validator: false
revenue_validated_by_validator: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether the human-filled invoice-process input is
complete and boundary-safe before it is passed to the existing invoice process
evidence builder.

## Boundary

The validator is pre-builder input validation only. It does not approve an
invoice process, create invoice templates, create or send invoices,
sign contracts, perform reconciliation, collect payment, validate revenue,
collect evidence, close blockers, modify runtime/backend/kernel/API schema or
private core, launch product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_approval_input_validation.md`
- script: `scripts/saee_invoice_process_approval_input_validator.py`
- smoke: `scripts/saee_invoice_process_approval_input_validator_smoke.py`
