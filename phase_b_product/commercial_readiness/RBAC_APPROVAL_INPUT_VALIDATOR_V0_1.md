# SAEE RBAC Approval Input Validator v0.1

rbac_approval_input_validator_v0_1: true
validator_scope: local_human_filled_rbac_input_pre_builder_check
default_validation_status: hold
default_input_complete: false
default_builder_ready: false
target_blocker_ids: rbac
required_review_key_count: 5
completed_review_key_count: 0
blockers_closed_by_validator: 0
rbac_approved_by_validator: false
rbac_available_by_validator: false
production_auth_evidence_built_by_validator: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
rbac_enforced_in_production: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether human-filled RBAC evidence input is complete and
boundary-safe before it is copied into the existing Phase 1 identity/tenant
evidence builder.

## Target Evidence Keys

- rbac_policy_approved
- role_matrix_reviewed
- tenant_role_boundary_reviewed
- least_privilege_reviewed
- admin_recovery_policy_reviewed

## Boundary

The validator is pre-builder input validation only. It does not contact an
identity provider, fetch JWKS, validate production tokens, enable production
authentication, enforce production RBAC, close blockers, modify
runtime/backend/kernel/API schema/private core, launch product, or claim
production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_validation.md`
- script: `scripts/saee_rbac_approval_input_validator.py`
- smoke: `scripts/saee_rbac_approval_input_validator_smoke.py`
