# How To Produce The Human-Filled Answer Sheet

1. Run a real external customer or target-user conversation.
2. Use `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_worksheet.md` as the Chinese interview worksheet.
3. Copy the answer skeleton into `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md`.
4. Fill every value from the real conversation.
5. Run:

```bash
python3 scripts/saee_customer_validation_answer_sheet_preflight.py
python3 scripts/saee_customer_validation_answer_sheet_preflight_smoke.py
```

Only when the preflight reports `ready_for_explicit_apply_request=true` should
you request a separate apply/import run.
