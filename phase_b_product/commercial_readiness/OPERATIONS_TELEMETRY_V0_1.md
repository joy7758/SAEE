# SAEE Operations Telemetry v0.1

Status: local pre-commercial telemetry snapshot.

SAEE Operations Telemetry v0.1 reads local request-audit JSONL metadata and
builds an aggregate public-shell operations snapshot. It is meant for local
review and controlled-preview diagnostics only.

This is not production monitoring, alerting, SIEM integration, incident
response, SLA, support process, or customer-facing operational assurance.

## Scope

Included:

- read local request metadata from `SAEE_REQUEST_AUDIT_PATH`;
- count events, methods, paths, status codes, errors, and invalid lines;
- count tenant-boundary audit metadata without grouping by raw tenant ID;
- filter local request-audit events by hashed tenant ID when a controlled-preview
  tenant boundary is supplied;
- summarize local duration min/median/p95/max;
- preserve explicit non-inspection flags for request body, credentials, and
  private core;
- expose a local CLI report.

Excluded:

- log tailing daemon;
- external metrics export;
- alert routing;
- dashboards;
- production uptime monitoring;
- incident response workflow;
- customer SLA or support commitment.

## CLI

```bash
python3 scripts/saee_operations_telemetry.py
```

## Current State

```text
operations_telemetry_v0_1: true
telemetry_source: request_audit_jsonl
local_operations_telemetry_available: true
operations_telemetry_external_export_available: false
local_alert_policy_available: true
external_alert_delivery_available: false
production_monitoring_available: false
alerting_available: false
incident_response_runbook_available: true
production_operations_ready: false
tenant_audit_metadata_available: true
tenant_boundary_checked_count: local_snapshot_field
tenant_scoped_request_count: local_snapshot_field
tenant_id_hash_recorded_count: local_snapshot_field
tenant_id_raw_recorded_count: local_snapshot_field
tenant_scope_filter_available: true
tenant_scope_filter_applied: local_snapshot_field
tenant_id_raw_filter_recorded: false
body_inspected: false
credentials_inspected: false
private_core_inspected: false
private_core_exposed: false
production_ready: false
customer_validated: false
product_launched: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## Snapshot Fields

The snapshot includes:

- `event_count`
- `invalid_line_count`
- `status_code_counts`
- `method_counts`
- `path_counts`
- `error_count`
- `tenant_audit_metadata_available`
- `tenant_boundary_checked_count`
- `tenant_scoped_request_count`
- `tenant_id_hash_recorded_count`
- `tenant_id_raw_recorded_count`
- `tenant_scope_filter_applied`
- `tenant_id_raw_filter_recorded`
- `duration_ms_min`
- `duration_ms_median`
- `duration_ms_p95`
- `duration_ms_max`
- `latest_timestamp`

The snapshot does not include request bodies, response bodies, credentials,
cookies, API keys, Authorization headers, raw tenant IDs, private-core
internals, fitness logic, selection logic, mutation logic, or lineage
internals.

When a controlled-preview tenant ID is supplied by the API tenant boundary, the
service hashes that tenant ID locally and filters the request-audit JSONL by
the recorded tenant hash. The raw tenant ID is not returned or recorded by the
filter.

## Boundary

Operations Telemetry v0.1 does not modify the private core, kernel, runtime,
evaluation scoring, public API schema, or landing page interaction. It only
reads local public-shell metadata that already exists.
