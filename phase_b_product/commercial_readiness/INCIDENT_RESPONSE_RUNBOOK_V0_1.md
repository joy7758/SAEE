# SAEE Incident Response Runbook v0.1

Status: local/pre-commercial incident response runbook available.

This runbook gives SAEE a documented manual incident response procedure for
the MVP public shell. It is not an alerting system, on-call rotation, SLA,
support process, production monitoring service, customer support desk, or
production readiness certification.

## Scope

Included:

- manual incident severity classification;
- first-response checklist for the local/controlled-preview API shell;
- containment steps for public-shell failures;
- rollback and shutdown guidance for local preview services;
- evidence capture checklist using public-shell logs and request metadata;
- post-incident review template;
- explicit non-claim boundary for production operations.

Excluded:

- automated alerting;
- external monitoring provider integration;
- on-call rotation;
- SLA or support commitment;
- customer notification workflow;
- production incident management platform;
- private-core inspection or disclosure.

## Severity Levels

```text
SEV-1: Public shell unavailable, repeated 5xx errors, suspected data exposure,
       or private-core boundary risk.
SEV-2: Demo/API degraded, repeated failed evaluations, storage/audit failure,
       or unsafe configuration detected.
SEV-3: Documentation, local demo, telemetry, or non-customer-impacting issue.
```

## First Response Checklist

1. Confirm scope: local demo, controlled preview, or production claim risk.
2. Check `/health` and `/ready`.
3. Confirm `production_ready=false`, `private_core_exposed=false`, and
   `product_launched=false` remain true boundary states.
4. If request audit is enabled, preserve the local JSONL metadata file.
5. Do not inspect request bodies, credentials, Authorization headers, cookies,
   or private-core internals.
6. If private-core exposure is suspected, stop the public shell and move the
   issue to human review before any restart.
7. Record the incident in a local review note before changing configuration.

## Containment Actions

Allowed manual actions:

- stop the local API process;
- disable controlled-preview API access by removing or rotating the preview
  API key;
- set `SAEE_ENV=local` before restarting local-only service;
- set `SAEE_REQUEST_AUDIT_ENABLED=false` if audit logging itself is unsafe;
- preserve logs and JSONL metadata for human review;
- run local smoke checks after containment.

Forbidden actions:

- do not modify private core, kernel, runtime, fitness, selection, mutation, or
  lineage internals during incident response;
- do not contact customers from this runbook;
- do not publish status pages, releases, SDKs, or launch claims;
- do not call external AI assistants or external model APIs;
- do not export logs to third-party monitoring without a separate approval.

## Recovery Checklist

Run local checks before marking the incident locally contained:

```bash
python3 scripts/mainline_guard.py
python3 scripts/saee_mvp_api_smoke.py
python3 scripts/saee_commercial_boundary_smoke.py
python3 scripts/saee_commercial_preflight_smoke.py
python3 scripts/saee_operations_readiness_smoke.py
```

If the API shell is restarted, verify:

```text
GET /health
GET /ready
POST /experiment/run with a local demo request
```

## Post-Incident Review Template

```text
incident_id:
date:
severity:
surface:
summary:
detected_by:
customer_impact: none|unknown|potential|confirmed
private_core_exposed: false
production_ready_claim_added: false
product_launched: false
customer_contacted: false
root_cause:
containment:
recovery_checks:
follow_up_candidates:
requires_human_approval: true
```

## Current State

```text
incident_response_runbook_v0_1: true
incident_response_runbook_available: true
automated_alerting_available: false
on_call_rotation_available: false
sla_available: false
support_process_available: false
production_monitoring_available: false
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

## Boundary

This runbook improves commercial operations documentation only. It does not
change SAEE evaluation behavior, API schema, landing page interaction, private
core, kernel, runtime, fitness logic, selection logic, mutation logic, or
lineage internals.
