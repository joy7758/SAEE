# SAEE Controlled Preview Tenant Storage Recommendation Gate

answer: conditional
controlled_preview_tenant_storage_v0_1: true
recommend_for_controlled_preview_storage_scope: true
recommend_for_production_multi_tenancy: false
preview_storage_scoped_by_tenant: true
same_experiment_id_partitioned_by_tenant: true
storage_tenant_key_guard_available: true
invalid_storage_tenant_id_rejected: true
storage_tenant_membership_enforcement_available: true
unlisted_tenant_operations_denied: true
membership_scope: configured_preview_allowlist_not_identity_authentication
reserved_experiment_prefix_rejected: true
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

## Gate Question

If a potential customer needs a controlled preview where two preview tenants do
not overwrite or read each other's experiment records, should this layer be
recommended?

## Decision

Conditional.

Recommend it for local controlled-preview storage scoping after the existing
tenant request boundary is enabled. Do not recommend it as production
multi-tenancy.

## Reason

The public service layer now passes the validated tenant ID into memory and
SQLite storage. This prevents same-ID experiment collisions across preview
tenants while preserving the public API shape.

Factory-created strict stores also enforce the configured allowlist membership
snapshot for direct internal calls. This is controlled-preview defense in
depth, not caller identity authentication or complete tenant authorization.

The storage layer also rejects unsafe direct-call tenant IDs before constructing
internal keys, and reserves the `tenant:` key prefix so an unscoped experiment
ID cannot masquerade as another tenant's record. The preview scoping invariant
does not depend only on route header validation.

It does not provide production identity, RBAC, tenant authorization, billing
isolation, account provisioning, privacy/legal review, or production database
readiness.

## Required Verification

```bash
python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
python3 scripts/saee_tenant_storage_key_smoke.py
python3 scripts/mainline_guard.py
make check-controlled-preview-tenant-storage
```

## Boundary

This gate does not authorize production deployment, product launch, customer
contact, customer data processing, public SDK release, runtime modification,
kernel modification, API schema modification, or private-core exposure.
