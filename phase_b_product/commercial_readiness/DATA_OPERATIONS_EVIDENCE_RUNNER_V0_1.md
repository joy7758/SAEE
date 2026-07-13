# SAEE Data Operations Evidence Runner v0.1

Status: local public-shell backup / restore evidence generated for human
review, not production data-operations readiness.

## Purpose

This runner converts existing local backup and isolated restore-drill helpers
into a local evidence JSON file. It helps commercial review see which
public-shell data-operations behaviors are already demonstrated and which
production restore evidence is still missing.

It strengthens the archive / rollback and operations evidence surface. It does
not modify runtime behavior, backend route behavior, API schema, kernel,
private core, production data paths, credentials, customer data, or live
restore behavior.

## Entrypoints

```text
scripts/saee_data_operations_evidence_runner.py
scripts/saee_data_operations_evidence_runner_smoke.py
phase_b_product/commercial_readiness/data_operations_evidence/
```

Generated evidence file:

```text
phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json
phase_b_product/commercial_readiness/data_operations_evidence/restore_test_plan.local.json
phase_b_product/commercial_readiness/data_operations_evidence/restore_test_report.local.json
```

## What The Runner Verifies

- A local public-shell SQLite experiment store can be backed up.
- A local public-shell request audit JSONL can be backed up.
- The backup can be restored into an isolated drill directory.
- Restored SQLite and JSONL files are readable.
- The drill does not restore into live paths.
- The drill does not restore credentials.
- The drill does not restore private-core materials.
- Local restore drill timing is recorded as local evidence.
- A local restore test plan is recorded for the isolated public-shell drill.
- A local restore test report is reviewed by deterministic checks.

## What Remains Unproven

- Production restore policy approval.
- Backup retention policy approval.
- Tenant restore boundary approval.
- Customer notification boundary approval.
- Incident response handoff approval.
- Any real production restore.

## Boundary Contract

```yaml
data_operations_evidence_runner_v0_1: true
evidence_scope: local_public_shell_backup_restore_drill
evidence_file: phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json
default_status_after_evidence_generation: hold
restore_tested: true
production_restore_tested: true
production_restore_policy_available: false
production_restore_policy_approved: false
production_data_operations_ready: false
restore_to_live_path_enabled: false
live_restore_performed: false
credentials_restored: false
private_core_restored: false
production_data_path_modified: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
```

## How To Run

```bash
python3 scripts/saee_data_operations_evidence_runner.py
python3 scripts/saee_data_operations_evidence_runner_smoke.py
```

The runner writes local evidence only. It does not configure
`SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH` by default and does not close
the production launch gate by itself.

## Recommendation Gate Result

Use this runner for local evidence generation and human commercial review.
Do not recommend it as production restore readiness, production backup policy,
customer-data operations approval, or launch approval.
