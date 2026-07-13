# SAEE External Customer Validation Action Board

Current blocker: `customer_validated`.

The local human evidence inspection passed, but SAEE still needs at least one
real external customer or target-user validation session before customer
validation can be claimed.

## Recommended Path Locked

Use only the 12-question minimum session packet for the next real customer or
target-user session:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`

This keeps the next human step small: ask the 12 questions, save the generated
JSON, then run the importer and validator only after the human-created JSON
exists. Older interview/workbench routes remain reference-only.

| Step | Action | Open This | Who Executes |
| --- | --- | --- | --- |
| ECV-001 | 筛选一个真实外部目标用户 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md` | Human only |
| ECV-002 | 人工发送邀请草稿 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md` | Human only |
| ECV-003 | 会前确认同意和边界说明 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md` | Human only |
| ECV-004 | 只使用 12 个最小会话问题记录反馈 | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md<br>phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_FILLING_GUIDE.md` | Human only |
| ECV-005 | 用最小会话表单生成并保存 JSON | `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html` | Human only |
| ECV-006 | 人工结果存在后再导入并运行 validator | `scripts/saee_external_customer_validation_session_entry_importer.py --apply<br>scripts/saee_customer_validation_approval_input_validator.py` | Human only |

## Required Output

The next required human-created file is:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

After that file exists, use the existing importer and validator. Do not infer
missing feedback.

## Boundaries

- Codex may not contact customers.
- Codex may not run the external session.
- Codex may not infer customer feedback.
- `customer_validated=false` until real evidence is imported and accepted.
- `production_ready=false`.
- `product_launched=false`.
- `private_core_exposed=false`.
