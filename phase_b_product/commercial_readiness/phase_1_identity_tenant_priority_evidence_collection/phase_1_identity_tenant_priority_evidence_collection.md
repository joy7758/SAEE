# SAEE Phase 1 Identity/Tenant Priority Evidence Collection v0.1

## Summary

- status: ready_for_human_review_not_execution
- required_evidence_item_count: 33
- local_public_shell_present_count: 16
- missing_production_evidence_count: 17
- accepted_for_blocker_closure_count: 0
- blockers_closed_by_collection: 0

## Blocker Summary

- `production_identity_provider`: required=5, local_public_shell=0, missing_production=5, ready_to_close=false
- `oauth_oidc`: required=5, local_public_shell=0, missing_production=5, ready_to_close=false
- `rbac`: required=5, local_public_shell=2, missing_production=3, ready_to_close=false
- `tenant_storage_isolation`: required=18, local_public_shell=14, missing_production=4, ready_to_close=false

## Priority Rows

| Record | Priority tier | Blocker | Evidence key | Builder field |
| --- | --- | --- | --- | --- |
| P1-ECP-001 | missing_production_evidence | production_identity_provider | identity_provider_admin_owner_named | evidence_review.identity_provider_admin_owner_named |
| P1-ECP-002 | missing_production_evidence | production_identity_provider | jwks_rotation_policy_reviewed | evidence_review.jwks_rotation_policy_reviewed |
| P1-ECP-003 | missing_production_evidence | production_identity_provider | oidc_audience_approved | evidence_review.oidc_audience_approved |
| P1-ECP-004 | missing_production_evidence | production_identity_provider | oidc_issuer_verified | evidence_review.oidc_issuer_verified |
| P1-ECP-005 | missing_production_evidence | production_identity_provider | production_identity_provider_selected | evidence_review.production_identity_provider_selected |
| P1-ECP-006 | missing_production_evidence | oauth_oidc | auth_failure_handling_reviewed | evidence_review.auth_failure_handling_reviewed |
| P1-ECP-007 | missing_production_evidence | oauth_oidc | claims_mapping_reviewed | evidence_review.claims_mapping_reviewed |
| P1-ECP-008 | missing_production_evidence | oauth_oidc | oauth_oidc_flow_approved | evidence_review.oauth_oidc_flow_approved |
| P1-ECP-009 | missing_production_evidence | oauth_oidc | session_expiry_policy_approved | evidence_review.session_expiry_policy_approved |
| P1-ECP-010 | missing_production_evidence | oauth_oidc | token_validation_test_recorded | evidence_review.token_validation_test_recorded |
| P1-ECP-011 | missing_production_evidence | rbac | admin_recovery_policy_reviewed | evidence_review.admin_recovery_policy_reviewed |
| P1-ECP-012 | missing_production_evidence | rbac | least_privilege_reviewed | evidence_review.least_privilege_reviewed |
| P1-ECP-013 | missing_production_evidence | rbac | rbac_policy_approved | evidence_review.rbac_policy_approved |
| P1-ECP-014 | local_public_shell_requires_human_approval | rbac | role_matrix_reviewed | evidence_review.role_matrix_reviewed |
| P1-ECP-015 | local_public_shell_requires_human_approval | rbac | tenant_role_boundary_reviewed | evidence_review.tenant_role_boundary_reviewed |
| P1-ECP-016 | missing_production_evidence | tenant_storage_isolation | privacy_legal_review_completed | evidence_review.privacy_legal_review_completed |
| P1-ECP-017 | missing_production_evidence | tenant_storage_isolation | security_review_completed | evidence_review.security_review_completed |
| P1-ECP-018 | missing_production_evidence | tenant_storage_isolation | tenant_authorization_policy_reviewed | evidence_review.tenant_authorization_policy_reviewed |
| P1-ECP-019 | missing_production_evidence | tenant_storage_isolation | tenant_secret_boundary_reviewed | evidence_review.tenant_secret_boundary_reviewed |
| P1-ECP-020 | local_public_shell_requires_human_approval | tenant_storage_isolation | cross_tenant_read_denial_tests_passed | evidence_review.cross_tenant_read_denial_tests_passed |
| P1-ECP-021 | local_public_shell_requires_human_approval | tenant_storage_isolation | cross_tenant_write_denial_tests_passed | evidence_review.cross_tenant_write_denial_tests_passed |
| P1-ECP-022 | local_public_shell_requires_human_approval | tenant_storage_isolation | customer_data_processing_non_claim_reviewed | evidence_review.customer_data_processing_non_claim_reviewed |
| P1-ECP-023 | local_public_shell_requires_human_approval | tenant_storage_isolation | production_tenant_data_model_approved | evidence_review.production_tenant_data_model_approved |
| P1-ECP-024 | local_public_shell_requires_human_approval | tenant_storage_isolation | same_experiment_id_cross_tenant_partition_tests_passed | evidence_review.same_experiment_id_cross_tenant_partition_tests_passed |
| P1-ECP-025 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_backup_restore_boundary_approved | evidence_review.tenant_backup_restore_boundary_approved |
| P1-ECP-026 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_deletion_retention_boundary_approved | evidence_review.tenant_deletion_retention_boundary_approved |
| P1-ECP-027 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_query_enforcement_design_reviewed | evidence_review.tenant_query_enforcement_design_reviewed |
| P1-ECP-028 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_scoped_audit_metadata_reviewed | evidence_review.tenant_scoped_audit_metadata_reviewed |
| P1-ECP-029 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_scoped_listing_tests_passed | evidence_review.tenant_scoped_listing_tests_passed |
| P1-ECP-030 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_scoped_primary_keys_or_partitions_reviewed | evidence_review.tenant_scoped_primary_keys_or_partitions_reviewed |
| P1-ECP-031 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_scoped_report_endpoint_tests_passed | evidence_review.tenant_scoped_report_endpoint_tests_passed |
| P1-ECP-032 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_storage_migration_plan_reviewed | evidence_review.tenant_storage_migration_plan_reviewed |
| P1-ECP-033 | local_public_shell_requires_human_approval | tenant_storage_isolation | tenant_storage_observability_plan_reviewed | evidence_review.tenant_storage_observability_plan_reviewed |

## How Human Owners Use This

1. Fill `phase_1_identity_tenant_evidence_input.priority.template.json` with
   source-backed production evidence.
2. Keep every boundary flag false unless a separate approved execution request
   exists.
3. Run the existing Phase 1 evidence builder with `--input` pointing to the
   priority template.
4. Run the existing Phase 1 evidence profile.

## What This Does Not Do

It does not collect evidence, contact identity providers, fetch JWKS, validate
production tokens, run storage migrations, process customer data, close
blockers, or claim production readiness.
