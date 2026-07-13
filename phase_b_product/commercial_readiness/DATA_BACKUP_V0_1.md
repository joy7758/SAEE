# SAEE Data Backup v0.1

Status: local/pre-commercial public-shell backup utility, manual-only.

## Purpose

SAEE Data Backup v0.1 adds a manually triggered local backup utility for public
API shell data. It covers only:

- SQLite public-shell experiment report database file
- request audit JSONL metadata file

It does not inspect request bodies, response bodies, credentials, private core,
fitness logic, selection logic, mutation logic, lineage internals, runtime
internals, or customer secrets.

## Controls

```text
SAEE_BACKUP_DIR=.saee_backups
backup_default_automatic: false
restore_tested: false
local_restore_drill_available: true
production_restore_policy_available: false
```

Default behavior is conservative:

- no backup runs unless a human invokes the command;
- backups are written under `SAEE_BACKUP_DIR`;
- `.saee_backups/` is ignored by git;
- the backup manifest records file size and SHA-256 for each copied public-shell
  artifact;
- the backup manifest explicitly records non-production and no-private-core
  boundaries.

## Command

Manual local backup:

```bash
python3 scripts/saee_data_backup.py --label pre-retention-review
```

The command creates a timestamped directory containing `BACKUP_MANIFEST.json`
and copies any existing public-shell SQLite and request audit JSONL files. The
manifest records per-file size and SHA-256 so an isolated restore drill can
verify that restored files match the backed-up artifacts.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive and Rollback Immune System governance by
   making local public-shell backup artifacts explicit before retention or
   controlled-preview review.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive and rollback hygiene. It does not modify sensing,
   branching, variation, selection, scoring, fitness, mutation, lineage,
   runtime, kernel, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It uses the Python standard library, makes no external calls, copies
   only explicitly configured local public-shell files, and never copies
   `.env`, `.secrets`, private core, or unknown repositories.

4. Could this change push the project back into audit-first framing?

   No. Backup is a commercial data-governance boundary and archive hygiene
   control, not the SAEE product core.

## Current State

```text
data_backup_v0_1: true
backup_default_automatic: false
sqlite_backup_available: true
request_audit_backup_available: true
backup_integrity_manifest_available: true
backup_file_hash_algorithm: sha256
restore_tested: false
production_backup_policy_available: false
tenant_backup_available: false
request_body_inspected: false
request_body_extracted: false
credentials_inspected: false
credentials_copied: false
private_core_inspected: false
private_core_copied: false
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

Formal commercial use still needs restore testing, off-host backup handling,
tenant-aware backup policy, encryption and key management policy, retention
approval workflow, customer data processing terms, production database
governance, and disaster recovery runbooks.

See `phase_b_product/commercial_readiness/DATA_RESTORE_DRILL_V0_1.md` for the
isolated local public-shell restore drill. That drill does not provide
production restore testing, tenant restore, or disaster recovery readiness.
