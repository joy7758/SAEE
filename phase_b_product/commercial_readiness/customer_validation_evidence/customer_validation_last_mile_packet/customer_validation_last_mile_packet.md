# SAEE Customer Validation Last-Mile Packet v0.1

Status: `ready_for_real_external_customer_session_entry`.

Current blocker: `customer_validated`.

This packet is the shortest path from a real external customer or target-user
session to the existing local post-session processor. It does not run the
session, contact customers, infer feedback, close blockers, launch SAEE, or
claim production readiness.

## Use This Order

1. Run one real external customer or target-user session.
2. Ask the 12 minimum questions in:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md`

3. Open the locked minimum-session form:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`

4. Save the generated JSON exactly here:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

5. Then run:

```bash
python3 scripts/saee_external_customer_validation_post_session_processor.py
python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py
python3 scripts/mainline_guard.py
```

## Current State

```yaml
customer_validation_last_mile_packet_v0_1: true
status: ready_for_real_external_customer_session_entry
recommended_path_locked: true
recommended_path_id: minimum_session_packet
human_session_entry_exists: false
ready_for_post_session_processor: false
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_last_mile_packet: 0
```
