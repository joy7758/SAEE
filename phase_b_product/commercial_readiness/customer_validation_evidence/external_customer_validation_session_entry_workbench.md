# SAEE External Customer Validation Session Entry Workbench

Status: `local_static_human_entry_workbench_ready`.

This is a local static helper for a human reviewer. It converts one real
external customer or target-user session into a JSON shape that can later be
saved and imported by the existing session-entry importer.

It does not contact customers, upload data, call external services, run
validators, execute evidence builders, close blockers, launch the product, or
claim production readiness.

```yaml
external_customer_validation_session_entry_workbench_v0_1: true
status: local_static_human_entry_workbench_ready
workbench_html: phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html
review_checkbox_count: 25
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_workbench: 0
```

## How To Use

1. Open `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html` locally in a browser.
2. Fill it after a real external customer or target-user session.
3. Download or copy the generated JSON.
4. Save it as `external_customer_validation_session_entry.human_filled.local.json`.
5. Run `python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply`.

The importer and later validators still do not authorize a public customer
validation claim by themselves.
