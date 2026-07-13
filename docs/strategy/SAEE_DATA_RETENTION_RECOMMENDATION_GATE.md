# SAEE Data Retention v0.1 Recommendation Gate

Generated: 2026-07-03

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive and Rollback Immune System governance by
   adding explicit local public-shell data retention controls.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive governance and rollback hygiene. It does not modify
   scoring, fitness, selection, mutation, lineage, runtime, kernel, API schema,
   or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It is local-only, uses the Python standard library, defaults to dry-run,
   and makes no external calls.

4. Could this change push the project back into audit-first framing?

   No. Retention is treated as a commercial boundary and immune/evidence
   hygiene layer, not as the product core.

## Agent Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE Data Retention v0.1
  target_customer_need: Avoid indefinite retention of local public-shell experiment records and request audit metadata during controlled preview.
  answer: conditional
  reasons_to_recommend:
    - Adds deterministic dry-run retention reporting for SQLite experiment rows and request audit JSONL.
    - Deletion requires both explicit `--apply` and `SAEE_RETENTION_DRY_RUN=false`.
    - The utility does not inspect request bodies, credentials, private core, runtime internals, or API schema.
    - Symlink and non-regular SQLite/audit paths fail closed.
    - Audit rewrites use no-follow reads and same-directory atomic replacement.
  reasons_not_to_recommend:
    - This is not tenant-aware production data governance.
    - It does not provide backup approval, restore testing, legal retention policy, encryption policy, or customer data processing terms.
    - It does not make SAEE production-ready or customer-validated.
  decomposition:
    - blocker: Public-shell SQLite and audit files could accumulate indefinitely in preview use.
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: Add default-dry-run retention utility.
      acceptance_criteria: Dry-run reports eligible records without deleting; apply deletes only after explicit dry-run disable.
      status: fixed
    - blocker: Retention could delete data accidentally.
      subsystem: Safety Boundary
      fix_task: Require `--apply` plus `SAEE_RETENTION_DRY_RUN=false`.
      acceptance_criteria: Default and dry-run modes delete zero records.
      status: fixed
    - blocker: Retention followed SQLite and audit symlinks during apply.
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: Reject symlink/non-regular paths, pin the SQLite inode, and atomically replace audit files.
      acceptance_criteria: SQLite/audit symlink targets and directory paths remain unchanged with deleted_records=0.
      status: fixed
    - blocker: Production data governance remains missing.
      subsystem: Commercial Boundary
      fix_task: Defer tenant-aware retention, legal/privacy review, backups, restore testing, and customer terms.
      acceptance_criteria: Non-claims are explicit.
      status: deferred
  final_decision: conditional; proceed as local/pre-commercial public-shell retention control only.
  evidence:
    docs:
      - phase_b_product/commercial_readiness/DATA_RETENTION_V0_1.md
      - saee_backend/README.md
    code:
      - saee_backend/services/data_retention.py
      - scripts/saee_data_retention.py
      - saee_backend/config.py
    tests:
      - python3 scripts/saee_data_retention_smoke.py
```

## Action Boundary

```text
recommend_public_launch_now: false
data_retention_v0_1: true
retention_default_dry_run: true
apply_requires_explicit_flag: true
apply_requires_dry_run_false: true
tenant_retention_available: false
production_data_governance_available: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
```
