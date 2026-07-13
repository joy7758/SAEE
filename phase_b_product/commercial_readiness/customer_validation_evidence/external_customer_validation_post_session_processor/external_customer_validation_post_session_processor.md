# SAEE External Customer Validation Post-Session Processor

Status: hold_human_session_entry_missing.

This local processor links the existing customer-validation session importer,
approval-input validator, evidence builder, production customer-validation
readiness checker, and commercial go/no-go checker.

It does not run customer sessions, contact customers, infer feedback, close
blockers, launch the product, claim customer validation, or claim production
readiness.

## Current Inputs

- recommended_path_locked: true
- recommended_path_id: `minimum_session_packet`
- recommended_form: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`
- recommended_questions: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md`
- human_entry_path: `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`
- human_entry_exists: false
- import_status: hold_human_session_entry_required
- approval_validation_status: not_run
- evidence_builder_ran: false
- readiness_status: not_run
- commercial_go_no_go_status: not_run

## If Human Entry Is Missing

Open:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`

Ask the 12-question minimum session to one real external customer or target
user, then save the generated JSON exactly here:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

After that file exists, run:

```bash
python3 scripts/saee_external_customer_validation_post_session_processor.py
python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py
```

## Boundary

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blockers_closed_by_processor: 0
