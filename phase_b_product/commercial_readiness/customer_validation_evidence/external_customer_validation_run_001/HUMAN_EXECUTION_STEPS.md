# Human Execution Steps

1. Select one real external customer or target user.
2. Use `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_interview_script.md` as the interview guide.
3. Use `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_feedback_form.template.md` to record the answers.
4. Do not ask for secrets, source code, production data, or customer data.
5. Open `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html` locally.
6. Enter the session summary and review checklist.
7. Save the JSON as:
   `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
8. After the file exists, run:

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply
python3 scripts/saee_customer_validation_approval_input_validator.py
python3 scripts/mainline_guard.py
make check
```

The session must be real. Internal founder review does not satisfy
`customer_validated`.
