# SAEE External Customer Validation Next Action v0.1

Status: hold_external_customer_validation_input_required.

This is the next-action packet for the remaining formal commercial blocker:
`customer_validated`. It does not contact customers, run an external pilot,
collect customer data, execute the evidence builder, close blockers, launch
SAEE, or claim production readiness.

## Current State

```yaml
external_customer_validation_next_action_v0_1: true
status: hold_external_customer_validation_input_required
current_goal_blocker: customer_validated
remaining_blocker_count: 1
local_evidence_lanes_passed: true
human_external_customer_validation_path_ready: true
result_entry_workbench: phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html
required_human_output: phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json
human_session_entry_exists: false
customer_validated: false
production_ready: false
product_launched: false
customer_contacted: false
private_core_exposed: false
blockers_closed_by_next_action: 0
```

## Human Procedure

1. Human tester opens the facilitator page and runs at least one real external
   customer or target-user demo or interview. Codex must not contact the
   participant.
2. Human tester opens the result-entry workbench:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html`

3. Human tester saves the generated JSON as:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

4. Run the existing post-session processor only after that real human-filled
   session-entry file exists:

```bash
python3 scripts/saee_external_customer_validation_post_session_processor.py
```

5. Stop. A processor pass still requires a separate commercial go/no-go update
   before any customer-validation or production-readiness claim.

## Checklist

| Step | Human Action | Required Evidence | Codex Allowed | Stop Condition |
| --- | --- | --- | --- | --- |
| CV-001 | Open the facilitator page and result-entry workbench. | facilitator page plus external_customer_validation_session_entry_workbench.html | False | Do not let Codex run the external session or invent feedback. |
| CV-002 | Run at least one real external customer or target-user demo/interview. | participant role, team type, current evaluation method, session date, and notes | False | No automated contact, no scraping, no external assistant calls. |
| CV-003 | Record scores for understanding, trust, decision influence, and repeat usage intent. | all required scores in range 1-5 | False | Do not infer scores from vague feedback. |
| CV-004 | Confirm all boundary flags remain false. | no secrets, no production data, no customer upload, no private core disclosure, no production-ready claim | False | Stop if any boundary flag becomes true. |
| CV-005 | Save the generated session-entry JSON at the required human output path. | external_customer_validation_session_entry.human_filled.local.json | False | Do not save internal self-review as external customer feedback. |
| CV-006 | Run the existing post-session processor after the human-filled session entry exists. | external_customer_validation_post_session_processor.local.json with processed status | True | Processor pass still does not publish a claim or close the blocker by itself. |
| CV-007 | Request a separate commercial go/no-go update only after processor outputs are reviewed. | separate explicit human go/no-go update request | False | No customer-validation or production-ready claim in this next-action packet. |

## Boundary

- codex_may_contact_customer=false
- codex_may_run_external_pilot=false
- codex_may_infer_customer_feedback=false
- evidence_builder_executed=false
- customer_validation_claim_allowed=false
- production_readiness_claim_allowed=false
- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
