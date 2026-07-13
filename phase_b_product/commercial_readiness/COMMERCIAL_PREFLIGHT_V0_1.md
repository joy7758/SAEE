# SAEE Commercial Preflight v0.1

Status: local/pre-commercial public-shell preflight, not production readiness.

## Purpose

SAEE Commercial Preflight v0.1 checks whether the MVP API shell is configured
for controlled preview use instead of default local demo use. It reduces the
risk of accidentally exposing a local configuration as if it were a commercial
deployment.

This preflight does not deploy SAEE, launch a product, validate customers,
publish an SDK, certify production readiness, or expose private core.

## Command

```bash
python3 scripts/saee_commercial_preflight.py
```

The command reads environment variables through `saee_backend/config.py` and
prints a JSON report. It does not start the server, call external services,
open a browser, modify API schema, or execute private core.

## Status Rules

```text
local default configuration -> hold
non-local configuration with missing controls -> hold
non-local configuration with required preview controls -> pass
boundary violation or forbidden claim -> stop
```

`pass` means only that the public API shell passes this controlled-preview
configuration preflight. It does not mean production readiness.

## Required Preview Controls

For `SAEE_ENV` values other than `local`, `dev`, or `development`, preflight
requires:

- `SAEE_REQUIRE_API_KEY=true`
- `SAEE_API_KEY` configured
- `SAEE_ALLOWED_ORIGINS` configured to explicit non-wildcard origins
- `SAEE_STORAGE_BACKEND=sqlite`
- `SAEE_REQUEST_AUDIT_ENABLED=true`
- `SAEE_RETENTION_DAYS` greater than 0
- `SAEE_REQUIRE_TENANT_ID=true`
- `SAEE_ALLOWED_TENANT_IDS` configured to at least one tenant ID
- `SAEE_SUPPORT_CONTACT` configured to a controlled-preview support mailbox or ticket queue
- `SAEE_SECURITY_CONTACT` configured to a controlled-preview security mailbox or ticket queue
- `SAEE_RESTORE_DRILL_REPORT_PATH` configured to an existing passing
  `RESTORE_DRILL_REPORT.json` from an isolated public-shell local restore drill
  with backup manifest size and SHA-256 integrity checks passed

The API key requirement is controlled-preview authentication only. It does not
provide production identity-provider integration, OAuth/OIDC, SSO, RBAC, or
account lifecycle controls.

The restore drill report requirement is controlled-preview evidence only. It
requires local readability checks plus backup manifest size/SHA-256 integrity
checks. It does not claim production restore testing, a production restore
policy, tenant restore operations, or disaster-recovery readiness.

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Sandbox Development and the Rollback Immune System by
   preventing unsafe public-shell configuration from being treated as
   commercially usable.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves deployment-boundary sensing and rollback readiness. It does not
   modify branching, variation, selection, scoring, fitness, mutation, lineage,
   runtime, kernel, or private core.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It reads local configuration only, makes no external calls, adds no
   dependency, and does not change product behavior or public schema.

4. Could this change push the project back into audit-first framing?

   No. This is a commercial deployment-boundary check. Audit remains an
   immune/evidence subsystem, not the SAEE core.

## Current State

```text
commercial_preflight_v0_1: true
commercial_preflight_available: true
default_local_status: hold
controlled_preview_possible: true
requires_tenant_boundary_for_non_local: true
preview_storage_scoped_by_tenant: true
auth_readiness_v0_1: true
production_auth_ready: false
oauth_oidc_available: false
sso_available: false
rbac_available: false
operations_telemetry_v0_1: true
local_operations_telemetry_available: true
operations_telemetry_external_export_available: false
operations_alert_policy_v0_1: true
local_alert_policy_available: true
external_alert_delivery_available: false
operations_readiness_v0_1: true
operations_readiness_status: hold
production_monitoring_available: false
alerting_available: false
incident_response_runbook_available: true
pilot_validation_readiness_v0_1: true
pilot_validation_status: hold
first_user_test_plan_available: true
feedback_form_available: true
success_criteria_available: true
pilot_result_template_available: true
pilot_session_protocol_available: true
pilot_sessions_completed: 0
pilot_results_recorded: false
customer_permission_recorded: false
customer_contacted: false
customer_validated: false
product_market_fit_claimed: false
revenue_validated: false
production_readiness_claimed: false
user_upload_enabled: false
billing_pricing_readiness_v0_1: true
billing_pricing_status: hold
pricing_packaging_plan_available: true
internal_price_bands_available: true
billing_policy_draft_available: true
pricing_page_published: false
sales_offer_sent: false
paid_product_launched: false
enterprise_contract_signed: false
payment_provider_configured: false
checkout_enabled: false
invoice_process_ready: false
tax_review_completed: false
refund_policy_available: false
billing_operations_ready: false
tenant_billing_isolated: false
preview_storage_scoped_by_tenant: true
customer_payment_collected: false
paid_pilot_completed: false
privacy_security_review_v0_1: true
privacy_security_review_status: hold
data_classification_available: true
pii_policy_draft_available: true
personal_data_allowed: false
legal_readiness_v0_1: true
legal_readiness_status: hold
terms_of_service_draft_available: true
terms_of_service_published: false
privacy_notice_draft_available: true
privacy_notice_published: false
dpa_review_packet_available: true
data_processing_agreement_draft_available: true
formal_security_review_completed: false
privacy_legal_review_completed: false
data_processing_agreement_available: false
production_legal_ready: false
security_certification_available: false
soc2_available: false
iso27001_available: false
penetration_test_completed: false
vulnerability_management_available: false
compliance_logging_available: false
production_security_ready: false
customer_data_processing_ready: false
support_readiness_v0_1: true
support_runbook_available: true
support_case_template_available: true
support_sla_draft_available: true
support_contact_configured: false
customer_support_available: false
production_support_available: false
on_call_rotation_available: false
sla_available: false
support_process_available: false
production_operations_ready: false
vulnerability_management_readiness_v0_1: true
vulnerability_management_readiness_status: hold
security_contact_configured: false
vulnerability_intake_contact_configured: false
controlled_preview_security_contact_required: false
vulnerability_management_available: false
production_vulnerability_management_ready: false
restore_drill_report_configured: false
controlled_preview_restore_drill_evidence_required: false
controlled_preview_restore_drill_passed: false
restore_integrity_checks_passed_after_placeholder_replacement: true
production_restore_tested: false
production_restore_policy_available: false
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

`support_contact_configured: false` is the local default. A non-local
controlled preview must configure `SAEE_SUPPORT_CONTACT`; this only records a
human support intake contact and does not claim staffed customer support,
production support, on-call rotation, or SLA availability.

`security_contact_configured: false` is also the local default. A non-local
controlled preview must configure `SAEE_SECURITY_CONTACT`; this records a
human vulnerability intake contact only. It does not claim full vulnerability
management, remediation SLA, coordinated disclosure, penetration testing, or
production security readiness.

`controlled_preview_restore_drill_evidence_required: false` is the local
default because local demo mode does not require public-use controls. Any
non-local controlled preview sets this requirement to true and must provide a
passing isolated `RESTORE_DRILL_REPORT.json` through
`SAEE_RESTORE_DRILL_REPORT_PATH`. The report must include passed readability
checks and passed backup manifest size/SHA-256 integrity checks. This still leaves
`production_restore_tested: false` and
`production_restore_policy_available: false`.

## Remaining Gaps

Formal commercial use still needs production authentication, tenant-isolated storage,
database migration policy, production restore testing, production restore
policy, production monitoring,
external alert delivery, vulnerability remediation SLA, coordinated
disclosure, penetration testing, staffed customer support, on-call rotation,
contractual SLA/support processes, formal privacy/security review, data
processing terms, vulnerability management, compliance logging, customer
onboarding, billing boundaries, payment provider setup, invoice/tax/refund
review, human-approved pilot sessions, paid validation, and real customer
validation.
