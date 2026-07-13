# SAEE Operations Alert Policy v0.1

Status: local pre-commercial alert-candidate policy.

SAEE Operations Alert Policy v0.1 converts local request-audit telemetry into
deterministic alert candidates for human review. It helps a preview operator
notice local 5xx or latency signals before broader testing.

This is not production alerting, external notification delivery, production
monitoring, on-call rotation, SLA, support, or production readiness.

## Scope

Included:

- local deterministic alert-candidate evaluation;
- error-count, error-rate, and p95-latency threshold checks;
- aggregate request metadata only;
- tenant-scoped alert-candidate evaluation when the underlying telemetry
  snapshot is filtered by a controlled-preview tenant boundary;
- CLI report for local review;
- smoke test and mainline guard coverage;
- explicit separation between local alert candidates and production alerting.

Excluded:

- external alert delivery;
- webhook, email, pager, chat, or monitoring provider integration;
- production dashboarding;
- automated incident response execution;
- request body, credential, or private core inspection;
- product launch or customer validation.

## CLI

```bash
python3 scripts/saee_operations_alert_policy.py
```

## Current State

```text
operations_alert_policy_v0_1: true
local_alert_policy_available: true
alert_candidates_generated: true
telemetry_source: request_audit_jsonl
external_alert_delivery_available: false
alerting_available: false
production_monitoring_available: false
operations_telemetry_external_export_available: false
tenant_scope_filter_available: true
tenant_scope_filter_applied: local_snapshot_field
tenant_id_raw_filter_recorded: false
incident_response_runbook_available: true
support_readiness_v0_1: true
support_runbook_available: true
support_sla_draft_available: true
support_contact_configured: false
customer_support_available: false
production_support_available: false
on_call_rotation_available: false
sla_available: false
support_process_available: false
production_operations_ready: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
body_inspected: false
credentials_inspected: false
private_core_inspected: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## Thresholds

Initial local thresholds:

- `error_count >= 1`
- `error_rate >= 0.05`
- `duration_ms_p95 >= 2000`

These thresholds create local alert candidates only. They do not send alerts
and do not authorize production use.

## Interpretation

`local_alert_policy_available: true` means SAEE can inspect aggregate local
request metadata and produce alert candidates for a human reviewer.

`external_alert_delivery_available: false` means no external notification
channel exists. No webhook, email, chat, pager, or monitoring provider is
called.

`alerting_available: false` means SAEE still does not have production alerting.

When a controlled-preview tenant boundary is available, the alert policy uses
the tenant-filtered telemetry snapshot. It does not return or record raw tenant
IDs and does not inherit other tenants' local alert candidates into a
tenant-scoped report.

`production_operations_ready: false` remains unchanged. Production monitoring,
external alert delivery, on-call rotation, SLA, support process, and customer
validation are still required before production use.

## Boundary

Operations Alert Policy v0.1 does not modify the private core, kernel, runtime,
API schema, scoring, selection, mutation, lineage, or landing page interaction.
It only reads local aggregate request metadata when available.
