# SAEE Controlled Preview Tenant Storage v0.1

controlled_preview_tenant_storage_v0_1: true
preview_storage_scoped_by_tenant: true
same_experiment_id_partitioned_by_tenant: true

Tenant storage keys reserve the `tenant:` prefix. Caller-supplied experiment
IDs beginning with that prefix are rejected so an unscoped record cannot be
mistaken for a tenant-scoped record during listing. This is a local
public-shell safety invariant, not production multi-tenant isolation.
New strict tenant keys use `tenant:v1:<sha256 tenant digest>:<experiment id>`;
raw tenant IDs are not written into new SQLite primary keys. Legacy raw-key
databases fail closed and require explicit archive or migration.
sqlite_reload_preserves_tenant_scope: true
tenant_scoped_experiment_listing: true
cross_tenant_write_partition_evidenced: true
storage_tenant_key_guard_available: true
invalid_storage_tenant_id_rejected: true
storage_tenant_membership_enforcement_available: true
unlisted_tenant_operations_denied: true
strict_allowlist_configuration_fail_closed: true
membership_scope: configured_preview_allowlist_not_identity_authentication
allowed_tenant_snapshot_requires_restart: true
tenant_storage_isolated: false
tenant_billing_isolated: false
tenant_authorization_policy_available: false
multi_tenant_production_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false

## Purpose

Controlled Preview Tenant Storage v0.1 scopes public-shell experiment records by
tenant ID when the existing `X-SAEE-Tenant-ID` request boundary is enabled.

The same `experiment_id` can exist under different preview tenants without one
tenant reading another tenant's result through the public service layer.

This is controlled-preview storage scoping only. It is not production
multi-tenancy, tenant authorization, tenant billing, production database
readiness, customer validation, or product launch.

## Behavior

When a route receives an allowlisted `X-SAEE-Tenant-ID`, the public service
layer passes that tenant ID to the storage layer. Memory and SQLite stores use a
tenant-scoped internal storage key while preserving the public response
`experiment_id`.

The storage layer also rejects unsafe direct-call tenant IDs before constructing
internal keys. Empty, whitespace-padded, delimiter-bearing, path-like, and
overlong tenant IDs cannot enter memory or SQLite persistence as tenant-scoped
keys.

Factory-created tenant-required stores take an immutable startup snapshot of
`SAEE_ALLOWED_TENANT_IDS`. They fail closed when the allowlist is empty or
invalid and reject format-valid but unlisted tenant IDs for all seven storage
operations. Configuration changes require a process restart. This membership
boundary does not authenticate the caller or prove tenant authorization.

Unscoped reads do not see tenant-scoped records. Tenant A reads tenant A records;
tenant B reads tenant B records.

`GET /experiment` returns public report summaries visible to the current
request scope. With tenant boundary enabled, tenant A sees only tenant A report
records, tenant B sees only tenant B report records, and unscoped listing does
not expose tenant-scoped records.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and the Rollback Immune System by
   reducing shared-preview data collision risk before broader controlled trials.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves preview archive separation and rollback safety. It does not
   modify scoring, fitness, selection, mutation, lineage, runtime, kernel, or
   private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It uses existing local storage and request-header boundaries, adds no
   dependency, makes no external calls, and keeps the listing response at the
   public report layer without exposing private runtime or scoring internals.
   Storage key construction now uses the same key-safe tenant ID format guard as
   the public request boundary.

4. Could this change push the project back into audit-first framing?

   No. This is commercial preview boundary hardening for SAEE's stability
   evaluation API shell.

## Verification

Run:

```bash
python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
python3 scripts/saee_tenant_storage_key_smoke.py
python3 scripts/mainline_guard.py
make check-controlled-preview-tenant-storage
```

Expected smoke output:

```text
SAEE_CONTROLLED_PREVIEW_TENANT_STORAGE_SMOKE: PASS
```

## Remaining Gaps

Formal commercial multi-tenant use still requires production identity, RBAC,
tenant authorization policy, tenant billing isolation, account provisioning,
production database review, operational monitoring, privacy/security review,
customer validation, and a separate production readiness gate.
