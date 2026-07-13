# SAEE Production Identity Provider Evidence Builder Request Template v0.1

production_identity_provider_evidence_builder_request_template_v0_1: true
status: hold_human_evidence_builder_request_required
target_blocker_id: production_identity_provider
target_builder: scripts/saee_phase1_identity_tenant_evidence_builder.py
request_template_ready: true
request_approved: false
evidence_builder_execution_authorized: false
evidence_builder_executed: false
blockers_closed_by_request_template: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This artifact provides the separate human approval request template required
after the production identity-provider approval input validator passes and
before the Phase 1 identity/tenant evidence builder is run.

It is a request template only. It does not run the builder, collect production
evidence, contact identity providers, fetch JWKS, validate production tokens,
enable production auth, close blockers, launch product, or claim production
readiness.

## Files

- template: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.template.json`
- status: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.local.json`
- report: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.md`
- completion CSV: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.csv`
- script: `scripts/saee_production_identity_provider_evidence_builder_request_template.py`
- smoke: `scripts/saee_production_identity_provider_evidence_builder_request_template_smoke.py`

## Boundary

- request_approved: false
- evidence_builder_execution_authorized: false
- evidence_builder_executed: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- production_auth_enabled: false
- production_ready: false
- blockers_closed_by_request_template: 0
