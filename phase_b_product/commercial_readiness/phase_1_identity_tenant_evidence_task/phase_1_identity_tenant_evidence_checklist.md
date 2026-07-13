# SAEE Phase 1 Identity and Tenant Evidence Checklist

Use this checklist only after a human explicitly authorizes Phase 1
evidence collection. Codex must not contact an identity provider, fetch
JWKS, validate production tokens, run migrations, or process customer data.

## production_identity_provider

- [ ] `production_identity_provider_selected`
- [ ] `identity_provider_admin_owner_named`
- [ ] `oidc_issuer_verified`
- [ ] `oidc_audience_approved`
- [ ] `jwks_rotation_policy_reviewed`

## oauth_oidc

- [ ] `oauth_oidc_flow_approved`
- [ ] `token_validation_test_recorded`
- [ ] `claims_mapping_reviewed`
- [ ] `session_expiry_policy_approved`
- [ ] `auth_failure_handling_reviewed`

## rbac

- [ ] `rbac_policy_approved`
- [ ] `role_matrix_reviewed`
- [ ] `tenant_role_boundary_reviewed`
- [ ] `least_privilege_reviewed`
- [ ] `admin_recovery_policy_reviewed`

## tenant_storage_isolation

- [ ] `production_tenant_data_model_approved`
- [ ] `tenant_scoped_primary_keys_or_partitions_reviewed`
- [ ] `tenant_query_enforcement_design_reviewed`
- [ ] `tenant_storage_migration_plan_reviewed`
- [ ] `same_experiment_id_cross_tenant_partition_tests_passed`
- [ ] `cross_tenant_read_denial_tests_passed`
- [ ] `cross_tenant_write_denial_tests_passed`
- [ ] `tenant_scoped_listing_tests_passed`
- [ ] `tenant_scoped_report_endpoint_tests_passed`
- [ ] `tenant_scoped_audit_metadata_reviewed`
- [ ] `tenant_backup_restore_boundary_approved`
- [ ] `tenant_deletion_retention_boundary_approved`
- [ ] `tenant_storage_observability_plan_reviewed`
- [ ] `tenant_authorization_policy_reviewed`
- [ ] `tenant_secret_boundary_reviewed`
- [ ] `security_review_completed`
- [ ] `privacy_legal_review_completed`
- [ ] `customer_data_processing_non_claim_reviewed`

## Required Review Before Blocker Closure

- [ ] Human approval confirms evidence is real and current.
- [ ] Evidence JSON is parseable by the readiness checker.
- [ ] No forbidden boundary flag is set to true.
- [ ] Commercial go/no-go is rerun with explicit evidence paths.
- [ ] Separate human launch approval remains required.
