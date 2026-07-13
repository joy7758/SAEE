# SAEE Request Audit v0.1

Status: local pre-commercial request metadata audit, not production monitoring.

## Purpose

SAEE Request Audit v0.1 adds optional JSONL request metadata logging for the
public MVP API shell. It helps a local or preview operator correlate API
requests, failures, response status codes, and durations while preserving the
private-core boundary.

This is not a production observability platform, incident-response system,
customer monitoring system, compliance log archive, or production readiness
claim.

## Controls

```text
SAEE_REQUEST_AUDIT_ENABLED=false
SAEE_REQUEST_AUDIT_PATH=.saee_data/request_audit.jsonl
```

Default behavior keeps request audit logging disabled. When enabled, the API
shell appends one JSON object per request to the configured local JSONL file.
`.saee_data/` is ignored by git.

Both event construction and the final writer enforce the same closed schema.
Unknown fields, protected-field overrides, nested values, control characters,
credential-shaped strings, forged tenant hashes, and invalid types fail closed.

## Recorded Data

The audit event records public-shell metadata only:

- timestamp
- request_id
- HTTP method
- URL path
- HTTP status code
- duration_ms
- optional client_host
- optional error_type for unhandled exceptions
- tenant_boundary_checked
- tenant_id_present
- tenant_id_hash_recorded
- optional tenant_id_hash using SHA-256 when a tenant boundary resolves
- tenant_id_raw_recorded: false

It does not record request bodies, response bodies, API keys, Authorization
headers, cookies, raw tenant IDs, private-core internals, scoring internals,
fitness logic, selection logic, mutation logic, lineage internals, customer
secrets, or external assistant output.

## Readiness Output

`GET /ready` reports:

```text
request_audit_enabled: false | true
request_audit_path_configured: true
request_audit_log_available: false | true
production_ready: false
private_core_exposed: false
```

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive and Rollback Immune System support by
   giving the public shell minimal request-level evidence for local diagnosis.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive and rollback observability only. It does not change
   sensing, branching, variation, selection, fitness, mutation, lineage,
   simulation, runtime, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It adds no external dependency, makes no external calls, records no
   request body or credentials, and keeps logging disabled by default.

4. Could this change push the project back into audit-first framing?

   No. This is an operational boundary for the commercial API shell. Audit is
   treated as an immune/evidence subsystem, not the project core.

## Current State

```text
request_audit_v0_1: true
request_audit_default_enabled: false
request_audit_jsonl_available: true
request_audit_closed_schema: true
request_audit_writer_revalidation: true
request_body_recorded: false
credentials_recorded: false
private_core_recorded: false
tenant_audit_metadata_available: true
tenant_id_hash_recorded_when_available: true
tenant_id_raw_recorded: false
tenant_audit_ownership_available: false
production_monitoring_available: false
compliance_logging_available: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
private_core_exposed: false
production_ready: false
product_launched: false
customer_validated: false
```

## Remaining Gaps

Formal commercial use still needs tenant-aware audit ownership, retention and
deletion policy, log rotation, access control, privacy review, alerting,
incident-response workflow, operational dashboards, and production monitoring
integration. Current tenant metadata is only local public-shell evidence that
a request passed through the tenant boundary; it is not production tenant audit
ownership.
