# SAEE Data Retention v0.1

Status: local/pre-commercial public-shell retention control, default dry-run.

## Purpose

SAEE Data Retention v0.1 adds a deterministic retention utility for public API
shell data. It covers only:

- SQLite public-shell experiment rows
- request audit JSONL metadata lines

It does not inspect request bodies, response bodies, credentials, private core,
fitness logic, selection logic, mutation logic, lineage internals, runtime
internals, or customer secrets.

## Controls

```text
SAEE_RETENTION_DAYS=0
SAEE_RETENTION_DRY_RUN=true
```

Default behavior is safe:

- `SAEE_RETENTION_DAYS=0` means no retention policy is configured.
- `SAEE_RETENTION_DRY_RUN=true` means no deletion occurs.
- Even with `--apply`, deletion only happens when `SAEE_RETENTION_DRY_RUN=false`.

## Command

Dry-run:

```bash
python3 scripts/saee_data_retention.py
```

Apply only after an independent agent has reviewed the dry-run receipt:

```bash
SAEE_RETENTION_DAYS=30 SAEE_RETENTION_DRY_RUN=false python3 scripts/saee_data_retention.py --apply
```

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive and Rollback Immune System governance by
   making local public-shell data retention explicit and reviewable.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive governance and rollback hygiene. It does not modify
   sensing, branching, variation, selection, scoring, fitness, mutation,
   lineage, runtime, kernel, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It uses the Python standard library, makes no external calls, defaults
   to dry-run, and only deletes after explicit `--apply` plus
   `SAEE_RETENTION_DRY_RUN=false`.

4. Could this change push the project back into audit-first framing?

   No. Data retention is a commercial boundary and immune/evidence hygiene
   layer, not the SAEE core.

## Current State

```text
data_retention_v0_1: true
retention_default_days: 0
retention_default_dry_run: true
sqlite_retention_available: true
request_audit_retention_available: true
apply_requires_explicit_flag: true
apply_requires_dry_run_false: true
symlink_paths_rejected: true
non_regular_paths_rejected: true
audit_rewrite_atomic: true
request_body_inspected: false
credentials_inspected: false
private_core_inspected: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
private_core_exposed: false
external_calls_made: false
production_ready: false
customer_validated: false
product_launched: false
```

## Remaining Gaps

Formal commercial use still needs tenant-specific retention policy, deletion
audit approval, backups before deletion, restore testing, legal/privacy review,
customer data processing terms, encryption policy, and production database
governance.

Before any agent-approved deletion operation, run the local public-shell backup
utility documented in `phase_b_product/commercial_readiness/DATA_BACKUP_V0_1.md`.
That backup utility is manual-only and is not a production backup/restore
policy.

After backup, use `phase_b_product/commercial_readiness/DATA_RESTORE_DRILL_V0_1.md`
to verify local public-shell backup readability in an isolated drill directory.
This remains local evidence only and is not production restore readiness.
