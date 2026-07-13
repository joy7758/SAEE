# SAEE Support Evidence Runner v0.1

Status: local public-shell support process evidence generated for human review,
not production support readiness.

## Purpose

This runner converts the controlled-preview support readiness surface into a
local evidence JSON file. It helps commercial review see which support-process
materials are already demonstrated and which production support / SLA evidence
is still missing.

It strengthens the immune / support evidence surface. It does not modify
runtime behavior, backend route behavior, API schema, kernel, private core,
customer support channels, customer contact, support vendor contact, SLA
approval, or production on-call behavior.

## Entrypoints

```text
scripts/saee_support_evidence_runner.py
scripts/saee_support_evidence_runner_smoke.py
phase_b_product/commercial_readiness/support_evidence/
```

Generated evidence file:

```text
phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json
```

## What The Runner Verifies

- Controlled-preview support runbook material exists.
- Support case intake fields are available for manual review.
- A non-contractual SLA draft exists for review.
- Local case triage, case audit trail, engineering handoff, and support-process dry-run evidence can be recorded.
- The runner does not configure a support contact.
- The runner does not contact customers or support vendors.
- The runner does not approve SLA terms or legal terms.
- The runner does not start on-call rotation.

## What Remains Unproven

- Customer-facing support contact configuration.
- Staffed customer support process.
- Approved customer communication template.
- Human-approved SLA terms.
- Approved severity definitions, support hours, response targets, exclusions, and legal review.
- On-call rotation, escalation schedule, and incident commander assignment.

## Boundary Contract

```yaml
support_evidence_runner_v0_1: true
evidence_scope: local_public_shell_support_process_dry_run
evidence_file: phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json
default_status_after_evidence_generation: hold
case_triage_workflow_defined: true
support_case_audit_trail_available: true
handoff_to_engineering_defined: true
support_process_dry_run_recorded: true
customer_facing_support_contact_configured: false
staffed_support_process_defined: false
customer_communication_template_approved: false
human_approved_sla_terms: false
response_targets_approved: false
legal_review_completed: false
support_contact_available: false
customer_support_available: false
production_support_available: false
support_process_available: false
sla_available: false
on_call_rotation_available: false
production_ready: false
customer_validated: false
product_launched: false
public_sdk_released: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
```

## How To Run

```bash
python3 scripts/saee_support_evidence_runner.py
python3 scripts/saee_support_evidence_runner_smoke.py
```

The runner writes local evidence only. It does not configure
`SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH` by default and does not close the
production launch gate by itself.

## Recommendation Gate Result

Use this runner for local evidence generation and human commercial review.
Do not recommend it as production support readiness, customer support
readiness, SLA readiness, on-call readiness, or launch approval.
