# SAEE Production Support / SLA Requirements v0.1

Status: requirements defined, implementation hold.

SAEE Production Support / SLA Requirements v0.1 defines the production support
requirements needed before SAEE can close the `sla`, `support_contact`, and
`customer_support` commercial launch blockers.

This is not a customer support desk, staffed support process, contractual SLA,
on-call rotation, support vendor integration, customer contact, or production
readiness.

## Current State

```text
production_support_sla_requirements_v0_1: true
requirements_status: requirements_defined_implementation_hold
support_blockers_covered_as_requirements:
- sla
- support_contact
- customer_support
production_support_sla_implemented: false
support_contact_available: false
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
task_candidates_executed: false
development_permission_granted: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
```

## Required Support Channels

Before production use, SAEE needs approved and tested support routes:

- `customer_support_email_or_ticket_queue`
- `security_contact_route`
- `billing_contact_route`
- `incident_escalation_route`
- `customer_notice_route`

These are requirements only. This package does not configure a mailbox,
ticketing system, chat channel, support vendor, or customer notification route.

## Required Support Roles

Before production use, SAEE needs named owners for:

- `support_owner`
- `triage_owner`
- `incident_commander`
- `technical_responder`
- `customer_communications_owner`
- `billing_support_owner`

These roles are not currently assigned by this package.

## Required SLA Terms

Before production use, any SLA must have human-approved terms for:

- `support_hours`
- `severity_definitions`
- `initial_response_targets`
- `update_cadence`
- `exclusions`
- `maintenance_window_policy`
- `credit_or_remedy_policy`
- `termination_and_refund_escalation`

The existing preview response targets remain non-contractual. They are not an
SLA and must not be represented as production support.

## Evidence Required Before Closing Blockers

### sla

Required evidence:

- `human_approved_sla_terms`
- `severity_definitions_approved`
- `support_hours_approved`
- `response_targets_approved`
- `exclusions_approved`
- `legal_review_completed`

### support_contact

Required evidence:

- `customer_facing_support_contact_configured`
- `support_contact_owner_named`
- `abuse_handling_path_defined`
- `customer_notice_route_defined`
- `support_contact_test_recorded`

### customer_support

Required evidence:

- `staffed_support_process_defined`
- `case_triage_workflow_defined`
- `support_case_audit_trail_available`
- `handoff_to_engineering_defined`
- `customer_communication_template_approved`
- `support_process_dry_run_recorded`

## Relationship To Preview Support Process v0.1

`PREVIEW_SUPPORT_PROCESS_V0_1.md` remains a controlled-preview support
readiness draft. It documents support case fields, severity classes, and
non-contractual response target drafts.

It does not close the production blockers covered here. A configured
`SAEE_SUPPORT_CONTACT` can support controlled-preview intake only. It is not
customer support, production support, SLA, or a staffed support process.

## Boundary

This requirements package does not modify product behavior, backend runtime,
API schema, kernel, private core, landing page interaction, scoring, selection,
mutation, lineage, customer contact state, or launch state. It only records
the production support and SLA evidence that would be required before a
separate human-approved implementation request.
