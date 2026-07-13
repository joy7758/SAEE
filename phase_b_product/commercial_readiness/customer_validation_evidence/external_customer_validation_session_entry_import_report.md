# SAEE External Customer Validation Session Entry Import Report

Status: hold_human_session_entry_required.

This importer prepares or converts one human-filled external customer validation
session entry into the existing customer-validation evidence input shape. It
does not contact customers, run sessions, infer feedback, execute the evidence
builder, close blockers, launch product, or claim production readiness.

## Summary

```yaml
external_customer_validation_session_entry_importer_v0_1: true
status: hold_human_session_entry_required
entry_template: phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.template.json
entry_input_exists: false
apply_requested: false
human_filled_output_written: false
ready_for_existing_customer_validation_validator: false
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_importer: 0
```

## Human Use

1. Copy `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.template.json` to `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
2. Fill it only from a real external customer or target-user session.
3. Run:

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --input phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json --apply
```

4. If import succeeds, run:

```bash
python3 scripts/saee_customer_validation_approval_input_validator.py --input phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json
```

The validator result still does not close `customer_validated` or authorize a
production-readiness claim.
