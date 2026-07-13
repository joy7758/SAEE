# SAEE Tenant Storage Isolation Evidence Runner v0.1

Status: local public-shell evidence generated for human review, not production
tenant storage isolation.

## Purpose

This runner converts the existing controlled-preview tenant storage behavior
into a local evidence JSON file. It helps commercial review see which
tenant-scoped public-shell behaviors are already demonstrated and which
production evidence is still missing.

It strengthens the archive / rollback and controlled preview evidence surface.
It does not change the SAEE runtime, kernel, private core, production database,
or customer-data processing state. It records the current public-shell tenant
write partitioning, report-read isolation, and listing isolation evidence.
It also records a local storage model boundary review for tenant-scope fields,
partition keys, query enforcement design, and migration-plan requirements.
It also records a local operations boundary review for tenant-scoped audit
metadata, backup/restore scope, deletion/retention scope, and observability
labels. That operations boundary is still local review evidence only.

## Entrypoints

```text
scripts/saee_tenant_storage_isolation_evidence_runner.py
scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py
phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/
```

Generated evidence file:

```text
phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json
phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_model_boundary.local.json
phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_model_boundary.md
phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_operations_boundary.local.json
phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_operations_boundary.md
```

## What The Runner Verifies

- Same public experiment ID can be stored separately under `tenant-a` and
  `tenant-b`.
- Tenant-scoped memory records return tenant-specific recommendations.
- Tenant-scoped SQLite records survive reload.
- Unscoped reads do not see tenant-scoped records.
- Tenant-scoped listing returns only the current tenant's public report records.
- Unscoped listing does not expose tenant-scoped records.
- Tenant-scoped report reads return the correct tenant record.
- Controlled-preview tenant request validation rejects missing and invalid
  tenant IDs.
- Tenant storage model boundary is locally reviewed.
- Tenant-scoped primary keys or partitions are locally reviewed.
- Tenant query enforcement design is locally reviewed.
- Tenant storage migration plan is locally reviewed as a required plan only;
  no migration is executed.
- Tenant-scoped audit metadata boundary is locally reviewed.
- Tenant backup / restore boundary is locally approved as a non-live,
  tenant-scoped operator-review requirement.
- Tenant deletion / retention boundary is locally approved as requiring tenant
  scope and legal/privacy review before customer data.
- Tenant storage observability plan is locally reviewed as aggregate,
  tenant-labeled, no-body-inspection telemetry only.

## What Remains Unproven

- Production tenant data model review is local-public-shell review only, not
  production deployment approval.
- Production tenant authorization policy.
- Cross-tenant write denial at production authorization level. The local public
  shell proves tenant-key write partitioning only.
- Tenant listing endpoint behavior at production authorization level. The local
  public shell proves `GET /experiment` tenant-scoped listing only.
- Live tenant backup, restore, deletion, retention enforcement, and external
  observability operation.
- Live production database migration.
- Security review.
- Privacy / legal review.
- Customer-data processing approval.

## Boundary Contract

```yaml
tenant_storage_isolation_evidence_runner_v0_1: true
evidence_scope: local_public_shell_tenant_storage_isolation
evidence_file: phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json
default_status_after_evidence_generation: hold
production_tenant_storage_evidence_complete: false
same_experiment_id_cross_tenant_partition_tests_passed: true
cross_tenant_read_denial_tests_passed: true
cross_tenant_write_denial_tests_passed: true
tenant_scoped_report_endpoint_tests_passed: true
tenant_scoped_listing_tests_passed: true
tenant_storage_model_evidence_complete: true
production_tenant_data_model_approved: true
tenant_scoped_primary_keys_or_partitions_reviewed: true
tenant_query_enforcement_design_reviewed: true
tenant_storage_migration_plan_reviewed: true
tenant_operations_evidence_complete: true
tenant_scoped_audit_metadata_reviewed: true
tenant_backup_restore_boundary_approved: true
tenant_deletion_retention_boundary_approved: true
tenant_storage_observability_plan_reviewed: true
tenant_storage_isolated: false
production_tenant_storage_isolated: false
multi_tenant_production_ready: false
tenant_authorization_enabled: false
production_tenant_storage_enabled: false
storage_behavior_modified: false
production_database_modified: false
migration_executed: false
customer_data_processed: false
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
python3 scripts/saee_tenant_storage_isolation_evidence_runner.py
python3 scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py
```

The runner writes local evidence only. It does not configure
`SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH` by default and does not close
the production launch gate by itself.

## Recommendation Gate Result

Use this runner for local evidence generation and human commercial review.
Do not recommend it as production multi-tenancy, tenant authorization,
customer-data processing approval, production storage isolation, or launch
approval.
