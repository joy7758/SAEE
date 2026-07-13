# SAEE Formal Security Review Approval Input Prompt

formal_security_review_approval_input_prompt_v0_1: true
status: hold_human_formal_security_review_input_required
target_blocker_id: formal_security_review
source_formal_security_review_approval_input_prompt_html: phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_prompt.html
local_static_formal_security_review_approval_input_prompt_html: true
browser_readable_formal_security_review_approval_input_prompt: true
plain_language_formal_security_review_approval_input_prompt_v0_2: true
formal_security_review_human_review_step_count: 5
plain_language_status_label: 正式安全审查还没有完成，也不能声称安全已审。
required_metadata_field_count: 5
completed_metadata_field_count: 0
required_formal_security_review_evidence_item_count: 7
completed_formal_security_review_evidence_item_count: 0
builder_ready: false
formal_security_review_available: false
formal_security_review_approved: false
formal_security_review_completed: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`formal_security_review` approval input before validator use.

## Metadata Fields To Fill

- `human_reviewer_name`
- `review_date`
- `security_review_owner`
- `report_reference`
- `decision_summary`

## Formal Security Review Keys To Review

| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |
| --- | --- | --- | --- | --- | --- | --- |
| `auth_and_tenant_boundary_reviewed` | set true only after human approval | required | required | required | required | false |
| `dependency_review_completed` | set true only after human approval | required | required | required | required | false |
| `formal_security_review_report` | set true only after human approval | required | required | required | required | false |
| `private_core_non_exposure_review_completed` | set true only after human approval | required | required | required | required | false |
| `public_shell_threat_model_reviewed` | set true only after human approval | required | required | required | required | false |
| `review_findings_triaged` | set true only after human approval | required | required | required | required | false |
| `storage_backup_and_restore_reviewed` | set true only after human approval | required | required | required | required | false |

## Copy Template

```bash
cp phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json
```

## Validate Human-Filled Input

```bash
python3 scripts/saee_formal_security_review_approval_input_validator.py --input phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json
```

## Stop Point

After validation, stop. Evidence-builder execution, security-review completion
claims, report approval, penetration testing, reviewer/vendor contact, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not perform or approve a security review, fill evidence,
contact reviewers or vendors, run penetration tests, inspect private core,
execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, process customer data,
or claim production readiness.
