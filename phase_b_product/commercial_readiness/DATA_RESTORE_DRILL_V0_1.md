# SAEE Data Restore Drill v0.1

Status: local/pre-commercial public-shell restore drill, isolated and manual-only.

## Purpose

SAEE Data Restore Drill v0.1 verifies that a local public-shell backup can be
read in an isolated drill directory and still match the backup manifest
integrity metadata. It covers only:

- SQLite public-shell experiment report backup files
- request audit JSONL metadata backup files

It does not restore into live paths, recover production service, restore
credentials, restore private core, inspect request bodies, inspect response
bodies, modify runtime, modify kernel, or change the API schema.

## Controls

```text
SAEE_RESTORE_DRILL_DIR=.saee_restore_drills
restore_drill_default_automatic: false
restore_to_live_path: false
production_restore_policy_available: false
```

Default behavior is conservative:

- no restore drill runs unless an authorized intelligent agent invokes the command;
- drills are written under `SAEE_RESTORE_DRILL_DIR`;
- `.saee_restore_drills/` is ignored by git;
- the drill copies backup files into an isolated directory, checks readability,
  and verifies file size plus SHA-256 against `BACKUP_MANIFEST.json`;
- live storage and audit paths are not overwritten.
- manifest must be a regular non-symlink file inside the configured backup root;
- manifest directory, fixed target names, size and SHA-256 metadata are closed and verified;
- source files are opened without following symlinks before copying.

## Command

Run after creating a local backup:

```bash
python3 scripts/saee_data_restore_drill.py --backup-dir .saee_backups/<backup-run-dir> --label restore-check
```

or:

```bash
python3 scripts/saee_data_restore_drill.py --backup-manifest .saee_backups/<backup-run-dir>/BACKUP_MANIFEST.json
```

The command creates a timestamped drill directory containing
`RESTORE_DRILL_REPORT.json`. The report records readability and integrity
results separately; if a copied backup file no longer matches the manifest
hash, the drill status is `hold`.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive and Rollback Immune System governance by
   checking that local public-shell backup artifacts are readable before any
   retention or controlled-preview data handling.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive and rollback hygiene. It does not modify sensing,
   branching, variation, selection, scoring, fitness, mutation, lineage,
   runtime, kernel, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It uses the Python standard library, makes no external calls, restores
   only to an isolated drill directory, and does not touch live storage paths,
   `.env`, `.secrets`, private core, or unknown repositories.

4. Could this change push the project back into audit-first framing?

   No. Restore drill is a commercial data-governance and archive hygiene
   control, not the SAEE product core.

## Current State

```text
data_restore_drill_v0_1: true
restore_drill_default_automatic: false
restore_to_live_path: false
local_restore_drill_completed_by_smoke: true
restore_integrity_checks_passed: true
forged_manifest_rejected: true
manifest_bound_to_configured_backup_root: true
source_symlink_followed: false
production_restore_tested: false
production_restore_policy_available: false
tenant_restore_available: false
request_body_inspected: false
response_body_inspected: false
credentials_inspected: false
credentials_restored: false
private_core_inspected: false
private_core_restored: false
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

Formal commercial use still needs production restore testing, off-host backup
handling, tenant-aware restore policy, encryption and key management policy,
recovery time objectives, disaster recovery runbooks, customer data processing
terms, and production database governance.
