# SAEE External Customer Validation Minimum Session Packet v0.1

Status: minimum_session_packet_ready_human_external_session_required.

This packet reduces the current `customer_validated` blocker to one small human
session. It reuses the existing
`external_customer_validation_session_entry.human_filled.local.json` schema and
the existing importer. It does not create a new validation standard.

## Human Output

After a real external customer or target-user session, either use the local
static form `minimum_session_form.html` or copy
`minimum_session_human_filled_template.local.json`, fill it, and save it as:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

Then run:

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --input phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json --apply
python3 scripts/saee_customer_validation_approval_input_validator.py --input phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json
python3 scripts/mainline_guard.py
make check
```

## Boundary

Codex may prepare the packet, but Codex may not contact the participant, run
the session, infer feedback, claim customer validation, claim production
readiness, or close blockers.
