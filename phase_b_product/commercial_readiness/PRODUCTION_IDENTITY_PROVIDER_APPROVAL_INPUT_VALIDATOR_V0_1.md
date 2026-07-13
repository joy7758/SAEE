# SAEE Production Identity Provider Approval Input Validator v0.1

production_identity_provider_approval_input_validator_v0_1: true
validator_scope: local_human_filled_production_identity_provider_input_pre_builder_check
default_validation_status: hold
default_input_complete: false
default_builder_ready: false
target_blocker_ids: production_identity_provider
required_review_key_count: 5
completed_review_key_count: 0
blockers_closed_by_validator: 0
production_identity_provider_selected_by_validator: false
production_identity_provider_approved_by_validator: false
production_identity_provider_available_by_validator: false
production_auth_evidence_built_by_validator: false
codex_contacted_identity_provider: false
codex_fetched_jwks: false
codex_validated_production_tokens: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether human-filled production identity-provider input
is complete and boundary-safe before it is copied into existing Phase 1
identity/tenant evidence builders.

## Boundary

The validator is pre-builder input validation only. It does not select or
contact an identity provider, fetch JWKS, validate production tokens, enable
production authentication, enforce production RBAC, close blockers, modify
runtime/backend/kernel/API schema/private core, launch product, or claim
production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json`
- validation output: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.md`
- script: `scripts/saee_production_identity_provider_approval_input_validator.py`
- smoke: `scripts/saee_production_identity_provider_approval_input_validator_smoke.py`
