# SAEE External Customer Validation Local Session Launcher v0.1

Status: local_session_launcher_ready_human_external_session_required.

This package is the one-page local entry point for running a real external
customer or target-user validation session. The recommended path is locked to
the 12-question minimum session form. The facilitator is reference-only boundary support.
It also links the current primary action, the online experience preview, and
the post-session processor.

It does not contact customers, run a session, upload data, infer feedback, close
the `customer_validated` blocker, launch the product, or claim production
readiness.

## Human Flow

1. Optionally serve the repo locally:
   `python3 -m http.server 8876 --bind 127.0.0.1`
2. Open the launcher HTML.
3. Show the participant the online experience preview.
4. Open the local minimum-session form and ask the 12 minimum validation
   questions.
5. Generate JSON from the minimum-session form.
6. Save the JSON as
   `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
7. Run the post-session processor and existing validation commands.
