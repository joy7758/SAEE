# SAEE Production Restore Policy Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_restore_policy_input_prompt: true
recommend_for_policy_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_restore_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`production_restore_policy` approval template. It makes the required metadata
and policy evidence keys explicit without approving policy or executing restore.

## Boundary

- target_blocker_id: production_restore_policy
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_restore_policy_available: false
- production_restore_policy_approved: false
- live_restore_performed: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
