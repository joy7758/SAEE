# SAEE Operations Telemetry API v0.1

Status: local/pre-commercial read-only operations report API.

SAEE Operations Telemetry API v0.1 exposes the existing local request-audit
telemetry snapshot and local alert-candidate policy through read-only FastAPI
routes:

```text
GET /operations/telemetry
GET /operations/alerts
```

This is a public-shell operations surface for controlled local review. It is
not production monitoring, external alert delivery, SIEM integration, SLA,
on-call, customer support, compliance logging, or production readiness.

## Scope

Included:

- read-only access to aggregate request metadata telemetry;
- read-only access to local alert candidates for human review;
- API-key guard reuse when `SAEE_REQUIRE_API_KEY=true`;
- tenant-envelope guard reuse when `SAEE_REQUIRE_TENANT_ID=true`;
- tenant-scoped telemetry and alert-candidate filtering when a
  controlled-preview tenant boundary is supplied;
- explicit non-inspection flags for request bodies, credentials, and private
  core;
- explicit non-claims for production monitoring and external alert delivery.

Excluded:

- request body inspection;
- response body inspection;
- credential or secret inspection;
- private-core inspection;
- external metrics export;
- external alert delivery;
- dashboard hosting;
- production uptime monitoring;
- automated incident response;
- customer-facing SLA or support commitments.

## Current State

```text
operations_telemetry_api_v0_1: true
operations_telemetry_api_available: true
operations_telemetry_routes_available: true
operations_telemetry_route: GET /operations/telemetry
operations_alert_candidates_route: GET /operations/alerts
read_only_operations_api: true
route_scope: public_shell_operations_read_only
tenant_scope_filter_available: true
tenant_scope_filter_applied: route_runtime_field
tenant_id_raw_filter_recorded: false
request_body_inspected: false
response_body_inspected: false
credentials_inspected: false
private_core_inspected: false
operations_telemetry_external_export_available: false
external_alert_delivery_available: false
production_monitoring_available: false
alerting_available: false
production_operations_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## Interpretation

`GET /operations/telemetry` returns the same aggregate public-shell telemetry
available from `scripts/saee_operations_telemetry.py`. It reads local
request-audit JSONL metadata and reports event counts, status-code counts,
method/path counts, error count, and duration percentiles.

When `require_tenant_boundary` resolves a tenant ID, the route passes it to the
telemetry snapshot so the service filters by the recorded tenant hash. The
route does not return, log, or expose the raw tenant ID.

`GET /operations/alerts` returns the same local alert-candidate report
available from `scripts/saee_operations_alert_policy.py`. Alert candidates are
for human review only and are not delivered to any external service. When a
tenant boundary is supplied, alert candidates are evaluated over the
tenant-filtered telemetry snapshot only.

The operations API is an incremental step toward production operations
readiness because operators can inspect local aggregate health signals through
the API shell. It does not close the `production_monitoring`,
`external_alert_delivery`, or `on_call_rotation` production blockers.

## Boundary

Operations Telemetry API v0.1 does not modify SAEE private core, kernel,
runtime, evaluation scoring, public API schema files, or landing page
interaction. It adds read-only public-shell routes backed by existing
aggregate telemetry services.
