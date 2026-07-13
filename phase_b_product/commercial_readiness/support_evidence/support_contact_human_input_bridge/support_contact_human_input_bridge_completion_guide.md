# Support Contact Human Input Bridge Completion Guide

Use `support_contact_human_input_bridge_input.template.json` as the single
human-filled source for `support_contact`.

## Export Validator Inputs

```bash
python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py \
  --combined-input phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json
```

Then run the existing validators separately:

```bash
python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py \
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.from_bridge.human_filled.local.json

python3 scripts/saee_support_contact_approval_input_validator.py \
  --input phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.from_bridge.human_filled.local.json
```

This guide does not authorize evidence collection, support-contact publication,
support-contact tests, blocker closure, customer contact, or production claims.
