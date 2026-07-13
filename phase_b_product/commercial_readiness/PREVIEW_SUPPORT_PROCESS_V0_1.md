# SAEE Preview Support Process v0.1

Status: controlled-preview support readiness draft.

SAEE Preview Support Process v0.1 documents how a human operator should record
and triage support issues during local or controlled-preview evaluation. It is
intended to make support boundaries explicit before customer-facing use.

This is not a customer support desk, staffed ticket queue, contractual SLA,
on-call rotation, production support process, customer validation, or product
launch.

## Scope

Included:

- controlled-preview support runbook;
- support case record template;
- issue severity classes;
- non-contractual response target draft;
- escalation notes for human review;
- explicit non-claims for production support and SLA.

Excluded:

- default customer-facing support mailbox;
- ticketing system integration;
- contractual SLA;
- on-call rotation;
- production escalation schedule;
- customer notification workflow;
- external service calls.

## CLI

```bash
python3 scripts/saee_support_readiness.py
```

## Current State

```text
support_readiness_v0_1: true
support_runbook_available: true
support_case_template_available: true
support_sla_draft_available: true
support_response_targets_documented: true
support_contact_configured: false
customer_support_available: false
production_support_available: false
support_process_available: false
sla_available: false
on_call_rotation_available: false
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
customer_contacted: false
```

## Controlled Preview Contact Configuration

`SAEE_SUPPORT_CONTACT` may be set by a human operator before a controlled
preview:

```text
SAEE_SUPPORT_CONTACT=<controlled-preview-support-mailbox-or-ticket-queue>
```

When this value is present, readiness reports that a support contact is
configured for preview intake. The contact value itself is not returned by the
API readiness payload.

This setting does not create customer support, production support, an on-call
rotation, a contractual SLA, customer validation, or product launch. It only
removes the support-contact gap for controlled-preview preflight.

## Severity Classes

```text
S0 blocker: local API unavailable, data corruption suspected, or private-core boundary risk.
S1 high: evaluation result unavailable or materially misleading.
S2 medium: local demo or documentation issue that blocks a preview workflow.
S3 low: wording, usability, or clarification issue.
```

## Support Case Template

```json
{
  "case_id": "SUP-YYYYMMDD-001",
  "reported_at": "YYYY-MM-DDTHH:MM:SSZ",
  "environment": "local|controlled_preview",
  "severity": "S0|S1|S2|S3",
  "summary": "",
  "affected_surface": "api|landing|documentation|recommendation_material|operations",
  "reproduction_steps": [],
  "observed_result": "",
  "expected_result": "",
  "request_id": "",
  "tenant_id": "",
  "boundary_flags": {
    "private_core_exposed": false,
    "production_ready_claim": false,
    "customer_data_involved": false
  },
  "owner": "",
  "status": "new|triaged|mitigating|resolved|deferred",
  "notes": ""
}
```

## Draft Response Targets

These are non-contractual preview targets only:

- S0: same business day human review;
- S1: next business day human review;
- S2: within three business days if preview is active;
- S3: batch review before the next documentation update.

These targets are not an SLA and must not be represented as production support.

## Boundary

Preview Support Process v0.1 does not modify product behavior, backend routes,
API schema, runtime, kernel, scoring, selection, mutation, lineage, private
core, or landing page interaction. It does not contact customers or create a
support channel.
