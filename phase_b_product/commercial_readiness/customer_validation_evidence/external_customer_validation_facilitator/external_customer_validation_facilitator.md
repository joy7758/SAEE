# SAEE External Customer Validation Facilitator

Current blocker: `customer_validated`.

Use this page when a human is ready to run one real external customer or
target-user session. Internal founder review is not enough.

## Session Flow

1. Screen the participant:
   `external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md`
2. Send the invitation manually:
   `external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md`
3. Read consent and boundary text before the session:
   `external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md`
4. Run the interview:
   `external_customer_validation_interview_script.md`
5. Record feedback:
   `external_customer_validation_feedback_form.template.md`
6. Enter the result:
   `external_customer_validation_session_entry_workbench.html`
7. Save the output as:
   `external_customer_validation_session_entry.human_filled.local.json`

## Import Only After Real Human Result Exists

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply
python3 scripts/saee_customer_validation_approval_input_validator.py
python3 scripts/mainline_guard.py
make check
```

## Boundary

- Codex may not contact the participant.
- Codex may not run the external session.
- Codex may not infer feedback.
- No production data, customer data, secrets, or private workflow internals.
- No production-ready claim.
- No customer-validation claim until evidence is imported and accepted.
