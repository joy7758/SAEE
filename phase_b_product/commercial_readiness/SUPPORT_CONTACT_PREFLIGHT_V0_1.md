# SAEE Support Contact Preflight v0.1

support_contact_preflight_v0_1: true
status: local_preflight_available
blocker_target: support_contact
preflight_scope: local_candidate_support_contact_review
support_contact_published: false
support_contact_test_performed: false
customer_contacted: false
support_vendor_contacted: false
customer_support_available: false
production_support_available: false
sla_available: false
on_call_rotation_available: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
blockers_closed_by_preflight: 0

## Purpose

This preflight checks whether a local operator has provided a candidate support
contact value for human review through `SAEE_SUPPORT_CONTACT`.

It exists to reduce friction before the `support_contact` blocker review. It
does not publish the contact, send a test message, contact customers, contact
vendors, create a support desk, approve SLA terms, start on-call rotation,
close blockers, launch product, or claim production readiness.

## Input

Optional local environment variable:

```text
SAEE_SUPPORT_CONTACT
```

The preflight records only whether a value exists, a coarse channel type, and a
redacted placeholder. It must not expose the raw support contact value.

## Outputs

```text
phase_b_product/commercial_readiness/support_evidence/support_contact_preflight.local.json
phase_b_product/commercial_readiness/support_evidence/support_contact_preflight.md
```

## Status Rules

```text
hold_missing_candidate:
  No local candidate support contact is configured.

ready_for_human_review:
  A local candidate support contact is configured and redacted for review.

stop:
  A boundary violation is detected.
```

## Boundary

This preflight is not production support evidence by itself. A human must still
review the candidate contact route, owner, abuse handling, customer notice
route, privacy/security constraints, and test record before any support-contact
evidence can be considered.

Even when the preflight reports `ready_for_human_review`, these remain false:

```text
support_contact_published: false
support_contact_test_performed: false
customer_support_available: false
production_support_available: false
production_ready: false
customer_validated: false
blockers_closed_by_preflight: 0
```

