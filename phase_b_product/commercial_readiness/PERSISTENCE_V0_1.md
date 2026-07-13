# SAEE Persistence v0.1

Status: local durable persistence option, not production database readiness.

## Purpose

SAEE Persistence v0.1 adds an optional SQLite-backed store for the public MVP
API shell. It lets a controlled local or preview deployment retain completed
experiment results across process restarts without modifying the private core,
evaluation logic, API schema, runtime, or landing page interaction.

## Controls

```text
SAEE_STORAGE_BACKEND=memory
SAEE_STORAGE_PATH=.saee_data/saee_mvp.sqlite3
```

Supported backends:

- `memory`: default local demo behavior; data is lost on process restart.
- `sqlite`: local durable store for public-shell experiment results.

`.saee_data/` is ignored by git so local experiment databases are not committed.

## Stored Data

The SQLite store persists only public MVP report-layer data:

- `EvaluationRunSummary`
- stability reports
- failure reports
- survival curves
- comparison ranking
- public run records
- public metric records
- aggregate public agent outputs

It does not store private SAEE kernel, fitness, selection, mutation, lineage,
runtime internals, customer data, or external trace payloads.

## Readiness Output

`GET /ready` reports:

```text
storage_backend: memory | sqlite
storage_path_configured: true
durable_persistence: false | true
production_ready: false
private_core_exposed: false
```

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive access by making public MVP reports
   recoverable across API shell restarts.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive persistence only. It does not change sensing, branching,
   mutation, selection, fitness, lineage, rollback, runtime, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It uses Python standard-library SQLite only, adds no external
   dependency, performs no external calls, and stores only public-shell report
   data.

4. Could this change push the project back into audit-first framing?

   No. This is report persistence for long-term AI agent / policy stability
   evaluation, not an audit SDK.

## Current State

```text
persistence_v0_1: true
default_storage_backend: memory
durable_persistence_option: true
sqlite_store_available: true
production_database_ready: false
tenant_isolation_available: false
backup_restore_policy_available: false
public_shell_backup_available: true
local_restore_drill_available: true
restore_tested: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
private_core_exposed: false
production_ready: false
product_launched: false
customer_validated: false
```

## Remaining Gaps

Formal commercial use still needs a production database decision, migrations,
tenant isolation, tenant-aware retention policy, production backups, production
restore testing, encryption policy, operational monitoring, and access-control
integration.

See `phase_b_product/commercial_readiness/DATA_BACKUP_V0_1.md` for the manual
local public-shell backup utility. That utility does not provide production
backup/restore policy or restore testing.

See `phase_b_product/commercial_readiness/DATA_RESTORE_DRILL_V0_1.md` for the
isolated local public-shell restore drill. That utility does not provide
production restore testing or tenant restore.

See `phase_b_product/commercial_readiness/DATA_RETENTION_V0_1.md` for the
local/pre-commercial dry-run retention utility. That utility does not make the
SQLite store production database ready.
