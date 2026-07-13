# SAEE Formal Security Review Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_formal_security_review_input_prompt: true
recommend_for_security_review_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_security_review_execution: false
recommend_for_private_core_inspection: false
recommend_for_penetration_test: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`formal_security_review` approval template. It makes the required metadata and
review evidence keys explicit without performing or approving a security review.

## Boundary

- target_blocker_id: formal_security_review
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- formal_security_review_available: false
- formal_security_review_approved: false
- formal_security_review_completed: false
- private_core_inspected_by_codex: false
- penetration_test_run_by_codex: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
