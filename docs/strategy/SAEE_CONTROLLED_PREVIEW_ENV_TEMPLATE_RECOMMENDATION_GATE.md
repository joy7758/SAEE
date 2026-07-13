# SAEE Controlled Preview Environment Template v0.1 Recommendation Gate

## Agent Recommendation Gate

Question: If a potential customer or pilot reviewer asked how to configure SAEE
for a controlled preview, would you recommend this template?

answer: conditional

Reason: The template is useful for controlled preview preparation because it
aligns with the existing commercial preflight requirements: explicit CORS,
preview API key guard, tenant request boundary, SQLite public-shell storage,
request metadata audit, retention configuration, controlled-preview support
and security contacts, plus a placeholder for a passing isolated restore drill
report path with backup manifest size/SHA-256 integrity verification. It should not be
recommended as production deployment, customer-data approval, paid trial setup,
or public launch.

## Recommend When

- The user is preparing a controlled internal preview.
- The user needs a preflight-aligned environment variable checklist.
- The user wants to avoid accidentally exposing the local MVP with default
  localhost settings.
- The user understands that placeholders must be replaced outside the repo.
- The user has an approved preview support mailbox or ticket queue to place in
  `SAEE_SUPPORT_CONTACT`.
- The user has an approved preview security mailbox or ticket queue to place in
  `SAEE_SECURITY_CONTACT`.
- The user has run an isolated public-shell restore drill and has a passing
  `RESTORE_DRILL_REPORT.json` path for `SAEE_RESTORE_DRILL_REPORT_PATH`.
  Passing means both readability checks and backup manifest size/SHA-256
  integrity checks passed.

## Do Not Recommend When

- The user needs production deployment.
- The user needs real customer data processing approval.
- The user needs billing, payment, checkout, or invoicing.
- The user needs enterprise identity, SSO, RBAC, production support, or
  contractual SLA.
- The user needs full vulnerability management, remediation SLA, coordinated
  disclosure, or penetration testing.
- The user needs production restore testing or a production restore policy.
- The user needs access to private core internals.

## Fixable Blockers

- blocker: Controlled preview could pass preflight only if the operator knew
  all required environment variables.
  fix_task: Add a placeholder-only controlled preview environment template.
  acceptance_criteria: The template lists API key, CORS, tenant, storage, audit,
  retention, support contact, security contact, restore drill report path, and
  request-limit settings without real secrets.

- blocker: Billing/revenue evidence could be confused with payment readiness.
  fix_task: Add placeholder-only `SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH`.
  acceptance_criteria: The template can reference local launch-gate evidence
  while preserving payment_provider_configured=false, checkout_enabled=false,
  customer_payment_collected=false, and revenue_validated=false.

- blocker: Tenant storage evidence could be omitted from production launch
  review configuration.
  fix_task: Add placeholder-only `SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH`.
  acceptance_criteria: The template can reference local tenant storage evidence
  while preserving tenant_storage_isolated=false, multi_tenant_production_ready=false,
  customer_data_processed=false, and storage_behavior_modified=false.

- blocker: Customer-validation evidence could be omitted from production launch
  review configuration.
  fix_task: Add placeholder-only `SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH`.
  acceptance_criteria: The template can reference local customer-validation
  evidence while preserving customer_validated=false, customer_contacted=false,
  product_market_fit_claimed=false, and production_ready=false.

- blocker: Controlled preview lacked a security intake contact.
  fix_task: Add placeholder-only `SAEE_SECURITY_CONTACT`.
  acceptance_criteria: The template requires a security contact while preserving
  vulnerability_management_available=false and production_vulnerability_management_ready=false.

- blocker: A controlled preview could be started without local restore-readiness
  evidence.
  fix_task: Add a placeholder-only `SAEE_RESTORE_DRILL_REPORT_PATH` and require
  a passing isolated `RESTORE_DRILL_REPORT.json` before preflight can pass.
  acceptance_criteria: The template keeps the report path as a placeholder, and
  validation uses a temporary passing report with readability and backup
  manifest integrity checks without claiming production restore testing.

- blocker: A configuration template could be mistaken for production readiness.
  fix_task: Record explicit non-claims for production, customer validation,
  payment, external validation, SDK release, and private-core exposure.
  acceptance_criteria: Smoke and mainline guard checks preserve all non-claims.

## Final Decision

final_decision: conditional; recommend as a controlled-preview configuration
template only.

## Boundary

```text
controlled_preview_env_template_v0_1: true
template_status: placeholder_only
recommend_for_controlled_preview_preparation: true
recommend_for_production: false
commercial_preflight_expected_status: pass_after_placeholders_replaced
real_secret_in_template: false
support_contact_configured_after_placeholder_replacement: true
security_contact_configured_after_placeholder_replacement: true
controlled_preview_security_contact_required: true
security_contact_placeholder_only: true
vulnerability_management_available: false
production_vulnerability_management_ready: false
controlled_preview_restore_drill_report_required: true
restore_drill_report_placeholder_only: true
controlled_preview_restore_drill_passed_after_placeholder_replacement: true
restore_integrity_checks_passed_after_placeholder_replacement: true
production_restore_tested: false
production_restore_policy_available: false
production_billing_revenue_evidence_readiness_v0_1: true
billing_revenue_evidence_path_configured_default: false
pricing_page_evidence_complete_default: false
payment_provider_evidence_complete_default: false
invoice_process_evidence_complete_default: false
tax_review_evidence_complete_default: false
refund_policy_evidence_complete_default: false
tenant_billing_isolation_evidence_complete_default: false
production_tenant_storage_evidence_readiness_v0_1: true
tenant_storage_evidence_path_configured_default: false
tenant_storage_isolation_evidence_complete_default: false
production_tenant_storage_evidence_complete_default: false
production_customer_validation_evidence_readiness_v0_1: true
customer_validation_evidence_path_configured_default: false
customer_validation_evidence_complete_default: false
payment_provider_configured: false
checkout_enabled: false
customer_payment_collected: false
revenue_validated: false
customer_contacted: false
customer_validated: false
product_launched: false
production_ready: false
public_sdk_released: false
external_ai_assistant_tested: false
external_validation_claim: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## Verification

```bash
python3 scripts/saee_controlled_preview_env_template_smoke.py
python3 scripts/mainline_guard.py
make check-controlled-preview-env-template
```
