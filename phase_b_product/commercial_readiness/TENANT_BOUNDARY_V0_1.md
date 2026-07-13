# SAEE Tenant Request Boundary v0.1

Status: local/pre-commercial tenant request guard, not production multi-tenancy.

## Purpose

SAEE Tenant Request Boundary v0.1 adds an optional request-envelope guard to
the public MVP API shell. When enabled, experiment routes require
`X-SAEE-Tenant-ID` and reject tenant IDs that are not listed in
`SAEE_ALLOWED_TENANT_IDS`.

This improves controlled-preview separation at the request boundary. The
public-shell storage layer also scopes memory and SQLite experiment records by
the validated tenant ID for controlled previews.

The tenant ID is also restricted to a key-safe identifier shape: it must start
with a letter or digit, use only letters, digits, dot, underscore, or hyphen,
and be at most 64 characters. This prevents malformed tenant headers or
allowlist entries from becoming storage-scope keys.

This does not create production tenant-isolated storage, tenant-specific
billing, production authorization, or production multi-tenant readiness.

## Environment Variables

```text
SAEE_REQUIRE_TENANT_ID=false
SAEE_ALLOWED_TENANT_IDS=
```

When `SAEE_REQUIRE_TENANT_ID=true`, requests to experiment endpoints must send:

```text
X-SAEE-Tenant-ID: <tenant-id>
```

The value must be present in `SAEE_ALLOWED_TENANT_IDS`, a comma-separated
allowlist.

Allowed tenant IDs must match:

```text
^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$
```

Invalid request tenant IDs are rejected before allowlist lookup. Invalid
allowlist configuration makes the backend readiness state
`configuration_error`.

## Readiness Fields

`GET /ready` reports:

```text
tenant_boundary_available: true
tenant_id_required: false
tenant_allowlist_configured: false
preview_storage_scoped_by_tenant: false
tenant_storage_isolated: false
tenant_billing_isolated: false
multi_tenant_production_ready: false
```

If `SAEE_REQUIRE_TENANT_ID=true` and `SAEE_ALLOWED_TENANT_IDS` is empty,
`/ready` returns `configuration_error`.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and the Rollback Immune System by making
   controlled-preview request boundaries explicit before evaluation requests
   enter the public-shell service layer.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves deployment-boundary sensing and preview rollback safety. It
   does not change sensing, branching, mutation, selection, scoring, fitness,
   lineage, runtime, kernel, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It is local configuration and request-header validation only. It adds
   no dependency, makes no external calls, does not alter API schema, and does
   not expose private internals.

4. Could this change push the project back into audit-first framing?

   No. This is a commercial request-boundary guard for SAEE's AI agent /
   strategy stability-evaluation wedge. Audit remains an immune/evidence
   subsystem.

## Current State

```text
tenant_boundary_v0_1: true
tenant_boundary_available: true
tenant_boundary_default_required: false
tenant_allowlist_available: true
tenant_header_name: X-SAEE-Tenant-ID
tenant_id_format_guard: true
preview_storage_scoped_by_tenant: true
tenant_storage_isolated: false
tenant_billing_isolated: false
tenant_authorization_policy_available: false
multi_tenant_production_ready: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
private_core_exposed: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
external_calls_made: false
```

## Remaining Gaps

Formal commercial multi-tenant use still requires production tenant-isolated
persistence, tenant-scoped audit ownership, production authentication and
authorization, account provisioning, billing boundaries, operational
monitoring, incident response, privacy review, and customer validation.
