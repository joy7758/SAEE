#!/usr/bin/env python3
"""Smoke check for SAEE commercial go/no-go aggregation."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_COMMERCIAL_GO_NO_GO_SMOKE: FAIL: {message}")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def write_restore_report(tmp: Path) -> Path:
    report_path = tmp / "RESTORE_DRILL_REPORT.json"
    report_path.write_text(
        json.dumps(
            {
                "restore_drill_type": "public_shell_local_restore_drill",
                "status": "pass",
                "copied_file_count": 2,
                "readable_file_count": 2,
                "integrity_checked_file_count": 2,
                "integrity_passed_file_count": 2,
                "restore_integrity_checks_passed": True,
                "restore_to_live_path": False,
                "production_restore_tested": False,
                "production_restore_policy_available": False,
                "credentials_restored": False,
                "private_core_restored": False,
                "runtime_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return report_path


def write_data_ops_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "DATA_OPERATIONS_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "data_operations_evidence_type": "production_data_operations_evidence",
                "production_like_restore_test_plan_approved": True,
                "isolated_restore_environment_used": True,
                "restore_integrity_checks_passed": True,
                "rto_rpo_observed_and_recorded": True,
                "tenant_scope_validated_if_customer_data_exists": True,
                "restore_test_report_reviewed": True,
                "production_restore_policy_approved": True,
                "backup_retention_policy_approved": True,
                "tenant_restore_boundary_approved": True,
                "credential_secret_exclusion_reviewed": True,
                "customer_notification_boundary_approved": True,
                "incident_response_handoff_approved": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "backend_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "customer_contacted": False,
                "production_data_path_modified": False,
                "restore_to_live_path_enabled": False,
                "live_restore_performed": False,
                "credentials_restored": False,
                "private_core_restored": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_auth_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "AUTH_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "auth_evidence_type": "production_auth_evidence",
                "production_identity_provider_selected": True,
                "identity_provider_admin_owner_named": True,
                "oidc_issuer_verified": True,
                "oidc_audience_approved": True,
                "jwks_rotation_policy_reviewed": True,
                "oauth_oidc_flow_approved": True,
                "token_validation_test_recorded": True,
                "claims_mapping_reviewed": True,
                "session_expiry_policy_approved": True,
                "auth_failure_handling_reviewed": True,
                "rbac_policy_approved": True,
                "role_matrix_reviewed": True,
                "tenant_role_boundary_reviewed": True,
                "least_privilege_reviewed": True,
                "admin_recovery_policy_reviewed": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "backend_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "customer_contacted": False,
                "identity_provider_contacted": False,
                "jwks_fetched": False,
                "tokens_validated_in_production": False,
                "production_auth_enabled": False,
                "rbac_enforced_in_production": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_support_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "SUPPORT_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "support_evidence_type": "production_support_sla_evidence",
                "customer_facing_support_contact_configured": True,
                "support_contact_owner_named": True,
                "abuse_handling_path_defined": True,
                "customer_notice_route_defined": True,
                "support_contact_test_recorded": True,
                "staffed_support_process_defined": True,
                "case_triage_workflow_defined": True,
                "support_case_audit_trail_available": True,
                "handoff_to_engineering_defined": True,
                "customer_communication_template_approved": True,
                "support_process_dry_run_recorded": True,
                "human_approved_sla_terms": True,
                "severity_definitions_approved": True,
                "support_hours_approved": True,
                "response_targets_approved": True,
                "exclusions_approved": True,
                "legal_review_completed": True,
                "on_call_rotation_defined": True,
                "escalation_schedule_defined": True,
                "incident_commander_named": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "customer_contacted": False,
                "support_vendor_contacted": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_operations_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "OPERATIONS_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "operations_evidence_type": "production_operations_evidence",
                "production_monitoring_plan_approved": True,
                "metrics_coverage_approved": True,
                "slo_dashboard_defined": True,
                "log_retention_reviewed": True,
                "monitoring_dry_run_recorded": True,
                "external_alert_channel_configured": True,
                "alert_routing_policy_approved": True,
                "alert_delivery_test_recorded": True,
                "alert_failure_handling_defined": True,
                "incident_escalation_path_defined": True,
                "alert_acknowledgement_process_defined": True,
                "on_call_rotation_defined": True,
                "escalation_schedule_defined": True,
                "incident_commander_named": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "backend_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "customer_contacted": False,
                "alert_provider_contacted": False,
                "monitoring_vendor_contacted": False,
                "production_monitoring_deployed": False,
                "external_alert_delivery_enabled": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_privacy_security_legal_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "PRIVACY_SECURITY_LEGAL_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence",
                "formal_security_review_report": True,
                "public_shell_threat_model_reviewed": True,
                "auth_and_tenant_boundary_reviewed": True,
                "storage_backup_and_restore_reviewed": True,
                "dependency_review_completed": True,
                "private_core_non_exposure_review_completed": True,
                "review_findings_triaged": True,
                "privacy_notice_approved": True,
                "terms_of_service_approved": True,
                "data_inventory_reviewed": True,
                "retention_policy_approved": True,
                "subprocessor_inventory_reviewed": True,
                "customer_data_processing_approved": True,
                "legal_reviewer_recorded": True,
                "dpa_terms_approved": True,
                "controller_processor_roles_defined": True,
                "subprocessor_terms_approved": True,
                "breach_notice_terms_approved": True,
                "deletion_or_return_terms_approved": True,
                "customer_dpa_template_available": True,
                "security_contact_configured": True,
                "coordinated_disclosure_policy_approved": True,
                "triage_owner_named": True,
                "severity_model_approved": True,
                "remediation_targets_approved": True,
                "vulnerability_case_dry_run_recorded": True,
                "advisory_publication_policy_approved": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "backend_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "external_model_api_called": False,
                "customer_contacted": False,
                "security_vendor_contacted": False,
                "legal_counsel_contacted": False,
                "customer_data_processed": False,
                "customer_data_processing_started": False,
                "dpa_sent_to_customer": False,
                "terms_published": False,
                "privacy_notice_published": False,
                "production_security_enabled": False,
                "vulnerability_management_operational": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_billing_revenue_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "BILLING_REVENUE_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "billing_revenue_evidence_type": "production_billing_revenue_evidence",
                "human_approved_pricing_page_copy": True,
                "approved_plan_and_usage_terms": True,
                "legal_review_completed": True,
                "production_readiness_non_claim_reviewed": True,
                "pricing_page_publication_approval_recorded": True,
                "payment_provider_selected": True,
                "test_mode_configuration_reviewed": True,
                "checkout_enablement_approval_required": True,
                "webhook_signature_validation_tested": True,
                "payment_event_redaction_reviewed": True,
                "security_review_completed": True,
                "invoice_owner_named": True,
                "invoice_workflow_approved": True,
                "contract_handoff_defined": True,
                "payment_reconciliation_tested": True,
                "billing_support_handoff_defined": True,
                "bookkeeping_review_completed": True,
                "target_jurisdictions_reviewed": True,
                "tax_obligations_reviewed": True,
                "invoice_wording_approved": True,
                "currency_policy_approved": True,
                "tax_collection_approval_recorded": True,
                "refund_policy_approved": True,
                "cancellation_process_approved": True,
                "trial_conversion_policy_approved": True,
                "service_failure_remedy_boundary_approved": True,
                "support_escalation_route_defined": True,
                "tenant_billing_account_model_approved": True,
                "tenant_invoice_partitioning_tested": True,
                "tenant_payment_event_partitioning_tested": True,
                "cross_tenant_billing_access_tests_passed": True,
                "billing_audit_metadata_policy_approved": True,
                "tenant_billing_retention_policy_approved": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "backend_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "customer_contacted": False,
                "payment_provider_contacted": False,
                "tax_advisor_contacted": False,
                "legal_counsel_contacted": False,
                "pricing_page_published": False,
                "sales_offer_sent": False,
                "paid_product_launched": False,
                "enterprise_contract_signed": False,
                "payment_provider_configured": False,
                "checkout_enabled": False,
                "payment_provider_live_mode_enabled": False,
                "payment_link_created": False,
                "invoice_sent_to_customer": False,
                "tax_collection_started": False,
                "refund_policy_published": False,
                "production_billing_enabled": False,
                "customer_payment_collected": False,
                "paid_pilot_completed": False,
                "revenue_validated": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_tenant_storage_evidence(tmp: Path) -> Path:
    evidence_path = tmp / "TENANT_STORAGE_EVIDENCE.json"
    evidence_path.write_text(
        json.dumps(
            {
                "tenant_storage_evidence_type": "production_tenant_storage_evidence",
                "production_tenant_data_model_approved": True,
                "tenant_scoped_primary_keys_or_partitions_reviewed": True,
                "tenant_query_enforcement_design_reviewed": True,
                "tenant_storage_migration_plan_reviewed": True,
                "same_experiment_id_cross_tenant_partition_tests_passed": True,
                "cross_tenant_read_denial_tests_passed": True,
                "cross_tenant_write_denial_tests_passed": True,
                "tenant_scoped_listing_tests_passed": True,
                "tenant_scoped_report_endpoint_tests_passed": True,
                "tenant_scoped_audit_metadata_reviewed": True,
                "tenant_backup_restore_boundary_approved": True,
                "tenant_deletion_retention_boundary_approved": True,
                "tenant_storage_observability_plan_reviewed": True,
                "tenant_authorization_policy_reviewed": True,
                "tenant_secret_boundary_reviewed": True,
                "security_review_completed": True,
                "privacy_legal_review_completed": True,
                "customer_data_processing_non_claim_reviewed": True,
                "production_ready": False,
                "customer_validated": False,
                "product_launched": False,
                "public_sdk_released": False,
                "private_core_exposed": False,
                "runtime_modified": False,
                "backend_modified": False,
                "kernel_modified": False,
                "api_schema_modified": False,
                "external_calls_made": False,
                "customer_contacted": False,
                "customer_data_processed": False,
                "customer_data_processing_started": False,
                "production_database_modified": False,
                "storage_behavior_modified": False,
                "migration_executed": False,
                "live_customer_data_migrated": False,
                "tenant_storage_isolated": False,
                "production_tenant_storage_isolated": False,
                "multi_tenant_production_ready": False,
                "tenant_authorization_enabled": False,
                "production_tenant_storage_enabled": False,
                "cross_tenant_access_tests_claimed_as_external_validation": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def main() -> None:
    local = evaluate_commercial_go_no_go(load_settings({}))
    require(local["go_no_go_type"] == "commercial_readiness_go_no_go", "wrong report type")
    require(local["commercial_status"] == "hold", "local default must hold")
    require(local["controlled_preview_status"] == "hold", "local default preview must hold")
    require(local["production_launch_status"] == "hold", "production launch must hold")
    require(local["controlled_preview_preflight_status"] == "hold", "local preflight must hold")
    require(local["production_blocker_count"] > 0, "production blockers must be listed")
    require(local["boundary_violation_count"] == 0, "local report must have no boundary violations")
    require(local["production_ready"] is False, "production_ready must remain false")
    require(local["customer_validated"] is False, "customer_validated must remain false")
    require(local["product_launched"] is False, "product_launched must remain false")
    require(local["legal_readiness_v0_1"] is True, "legal readiness must be visible")
    require(local["legal_readiness_status"] == "hold", "legal readiness must hold")
    require(local["terms_of_service_draft_available"] is True, "terms draft true")
    require(local["terms_of_service_published"] is False, "terms published false")
    require(local["privacy_notice_draft_available"] is True, "privacy notice draft true")
    require(local["privacy_notice_published"] is False, "privacy notice published false")
    require(local["dpa_review_packet_available"] is True, "DPA review packet true")
    require(local["data_processing_agreement_available"] is False, "DPA available false")
    require(local["customer_data_processing_ready"] is False, "customer data false")
    require(local["production_legal_ready"] is False, "production legal false")
    require(local["private_core_exposed"] is False, "private_core_exposed must remain false")
    require(local["external_calls_made"] is False, "must not make external calls")
    require(local["api_schema_modified"] is False, "must not modify API schema")
    require(local["runtime_modified"] is False, "must not modify runtime")
    require(local["kernel_modified"] is False, "must not modify kernel")

    required_blockers = {
        "production_identity_provider",
        "rbac",
        "tenant_storage_isolation",
        "production_monitoring",
        "external_alert_delivery",
        "formal_security_review",
        "privacy_legal_review",
        "data_processing_agreement",
        "pilot_results",
        "customer_validated",
        "payment_provider",
        "invoice_process",
        "tax_review",
        "tenant_billing_isolation",
        "restore_tested",
    }
    missing_blockers = sorted(required_blockers - blocker_ids(local))
    require(not missing_blockers, "missing expected blockers: " + ", ".join(missing_blockers))

    with tempfile.TemporaryDirectory() as tmpdir:
        restore_report = write_restore_report(Path(tmpdir))
        auth_evidence = write_auth_evidence(Path(tmpdir))
        support_evidence = write_support_evidence(Path(tmpdir))
        data_ops_evidence = write_data_ops_evidence(Path(tmpdir))
        operations_evidence = write_operations_evidence(Path(tmpdir))
        privacy_security_legal_evidence = write_privacy_security_legal_evidence(
            Path(tmpdir)
        )
        billing_revenue_evidence = write_billing_revenue_evidence(Path(tmpdir))
        tenant_storage_evidence = write_tenant_storage_evidence(Path(tmpdir))
        safe_preview = evaluate_commercial_go_no_go(
            load_settings(
                {
                    "SAEE_ENV": "preview",
                    "SAEE_ALLOWED_ORIGINS": "https://preview.saee.local",
                    "SAEE_REQUIRE_API_KEY": "true",
                    "SAEE_API_KEY": "local-preview-key",
                    "SAEE_STORAGE_BACKEND": "sqlite",
                    "SAEE_REQUEST_AUDIT_ENABLED": "true",
                    "SAEE_RETENTION_DAYS": "30",
                    "SAEE_REQUIRE_TENANT_ID": "true",
                    "SAEE_ALLOWED_TENANT_IDS": "preview-tenant",
                    "SAEE_SUPPORT_CONTACT": "support@example.invalid",
                    "SAEE_SECURITY_CONTACT": "security@example.invalid",
                    "SAEE_RESTORE_DRILL_REPORT_PATH": str(restore_report),
                    "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(auth_evidence),
                    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(support_evidence),
                    "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(
                        data_ops_evidence
                    ),
                    "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(
                        operations_evidence
                    ),
                    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
                        privacy_security_legal_evidence
                    ),
                    "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(
                        billing_revenue_evidence
                    ),
                    "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(
                        tenant_storage_evidence
                    ),
                }
            )
        )
    require(safe_preview["controlled_preview_status"] == "go", "safe preview should be go")
    require(safe_preview["controlled_preview_preflight_status"] == "pass", "safe preview preflight pass")
    require(safe_preview["commercial_status"] == "hold", "commercial status must still hold")
    require(safe_preview["production_launch_status"] == "hold", "production launch must still hold")
    require(
        safe_preview["production_data_operations_evidence_status"] == "pass",
        "safe preview data operations evidence pass",
    )
    require(
        safe_preview["production_operations_evidence_status"] == "pass",
        "safe preview operations evidence pass",
    )
    require(
        safe_preview["production_auth_evidence_status"] == "pass",
        "safe preview auth evidence pass",
    )
    require(
        safe_preview["production_support_evidence_status"] == "pass",
        "safe preview support evidence pass",
    )
    require(
        safe_preview["production_privacy_security_legal_evidence_status"] == "pass",
        "safe preview privacy/security/legal evidence pass",
    )
    require(
        safe_preview["production_billing_revenue_evidence_status"] == "pass",
        "safe preview billing/revenue evidence pass",
    )
    require(
        safe_preview["production_tenant_storage_evidence_status"] == "pass",
        "safe preview tenant storage evidence pass",
    )
    require(
        safe_preview["auth_evidence_production_identity_provider_available"] is True,
        "safe preview auth evidence identity provider true",
    )
    require(
        safe_preview["auth_evidence_oauth_oidc_available"] is True,
        "safe preview auth evidence OAuth/OIDC true",
    )
    require(
        safe_preview["auth_evidence_rbac_available"] is True,
        "safe preview auth evidence RBAC true",
    )
    require(
        safe_preview["support_evidence_customer_support_available"] is True,
        "safe preview support evidence customer support true",
    )
    require(
        safe_preview["support_evidence_sla_available"] is True,
        "safe preview support evidence SLA true",
    )
    require(
        safe_preview["support_evidence_on_call_rotation_available"] is True,
        "safe preview support evidence on-call true",
    )
    require(
        safe_preview["data_ops_evidence_restore_tested"] is True,
        "safe preview data ops restore evidence true",
    )
    require(
        safe_preview["data_ops_evidence_production_restore_policy_available"] is True,
        "safe preview data ops policy evidence true",
    )
    require(
        safe_preview["operations_evidence_production_monitoring_available"] is True,
        "safe preview operations monitoring evidence true",
    )
    require(
        safe_preview["operations_evidence_external_alert_delivery_available"] is True,
        "safe preview operations alert evidence true",
    )
    require(
        safe_preview["operations_evidence_on_call_rotation_available"] is True,
        "safe preview operations on-call evidence true",
    )
    require(
        safe_preview["privacy_security_legal_evidence_formal_security_review_completed"]
        is True,
        "safe preview formal security review evidence true",
    )
    require(
        safe_preview["privacy_security_legal_evidence_privacy_legal_review_completed"]
        is True,
        "safe preview privacy legal review evidence true",
    )
    require(
        safe_preview[
            "privacy_security_legal_evidence_data_processing_agreement_available"
        ]
        is True,
        "safe preview DPA evidence true",
    )
    require(
        safe_preview[
            "privacy_security_legal_evidence_vulnerability_management_available"
        ]
        is True,
        "safe preview vulnerability management evidence true",
    )
    for field in [
        "billing_revenue_evidence_pricing_page_complete",
        "billing_revenue_evidence_payment_provider_complete",
        "billing_revenue_evidence_invoice_process_complete",
        "billing_revenue_evidence_tax_review_complete",
        "billing_revenue_evidence_refund_policy_complete",
        "billing_revenue_evidence_tenant_billing_isolation_complete",
    ]:
        require(safe_preview[field] is True, f"safe preview {field} true")
    for field in [
        "tenant_storage_evidence_model_complete",
        "tenant_storage_evidence_isolation_complete",
        "tenant_storage_evidence_operations_complete",
        "tenant_storage_evidence_security_privacy_complete",
    ]:
        require(safe_preview[field] is True, f"safe preview {field} true")
    safe_preview_blockers = blocker_ids(safe_preview)
    require("restore_tested" not in safe_preview_blockers, "restore_tested evidence should close blocker")
    require(
        "production_restore_policy" not in safe_preview_blockers,
        "production_restore_policy evidence should close blocker",
    )
    for blocker in ["production_monitoring", "external_alert_delivery", "on_call_rotation"]:
        require(blocker not in safe_preview_blockers, f"{blocker} evidence should close blocker")
    for blocker in ["production_identity_provider", "oauth_oidc", "rbac"]:
        require(blocker not in safe_preview_blockers, f"{blocker} evidence should close blocker")
    for blocker in ["sla", "support_contact", "customer_support"]:
        require(blocker not in safe_preview_blockers, f"{blocker} evidence should close blocker")
    require(
        "tenant_storage_isolation" not in safe_preview_blockers,
        "tenant storage evidence should close blocker",
    )
    for blocker in [
        "formal_security_review",
        "privacy_legal_review",
        "data_processing_agreement",
        "vulnerability_management",
    ]:
        require(blocker not in safe_preview_blockers, f"{blocker} evidence should close blocker")
    for blocker in [
        "pricing_page",
        "payment_provider",
        "invoice_process",
        "tax_review",
        "refund_policy",
        "tenant_billing_isolation",
    ]:
        require(blocker not in safe_preview_blockers, f"{blocker} evidence should close blocker")
    require(
        safe_preview_blockers == {"pilot_results", "customer_validated"},
        "complete evidence should leave only real customer validation blockers",
    )
    require(safe_preview["production_blocker_count"] > 0, "safe preview still needs production blockers")
    require(safe_preview["boundary_violation_count"] == 0, "safe preview no boundary violations")
    require(safe_preview["production_ready"] is False, "safe preview must not claim production")
    require(safe_preview["customer_validated"] is False, "safe preview must not claim customer validation")
    require(safe_preview["product_launched"] is False, "safe preview must not claim launch")
    require(safe_preview["legal_readiness_v0_1"] is True, "safe preview legal readiness")
    require(safe_preview["legal_readiness_status"] == "hold", "safe preview legal hold")
    require(safe_preview["terms_of_service_published"] is False, "safe preview no terms publication")
    require(safe_preview["privacy_notice_published"] is False, "safe preview no privacy publication")
    require(safe_preview["data_processing_agreement_available"] is False, "safe preview no DPA")
    require(safe_preview["customer_data_processing_ready"] is False, "safe preview no customer data")
    require(safe_preview["production_legal_ready"] is False, "safe preview no production legal")
    require(safe_preview["private_core_exposed"] is False, "safe preview must not expose private core")
    require(safe_preview["external_ai_assistant_tested"] is False, "safe preview must not claim external AI test")

    doc = (ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_GO_NO_GO_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_COMMERCIAL_GO_NO_GO_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    combined = "\n".join([doc, gate])
    required_tokens = [
        "commercial_go_no_go_v0_1: true",
        "commercial_status: hold",
        "controlled_preview_status: go_if_preflight_passes",
        "production_launch_status: hold",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "legal_readiness_v0_1: true",
        "legal_readiness_status: hold",
        "terms_of_service_published: false",
        "privacy_notice_published: false",
        "data_processing_agreement_available: false",
        "customer_data_processing_ready: false",
        "production_legal_ready: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "production_auth_evidence_status_default: hold",
        "auth_evidence_production_identity_provider_available_default: false",
        "auth_evidence_oauth_oidc_available_default: false",
        "auth_evidence_rbac_available_default: false",
        "production_data_operations_evidence_status_default: hold",
        "data_ops_evidence_restore_tested_default: false",
        "data_ops_evidence_production_restore_policy_available_default: false",
        "production_operations_evidence_status_default: hold",
        "operations_evidence_production_monitoring_available_default: false",
        "operations_evidence_external_alert_delivery_available_default: false",
        "operations_evidence_on_call_rotation_available_default: false",
        "production_privacy_security_legal_evidence_status_default: hold",
        "privacy_security_legal_evidence_formal_security_review_completed_default: false",
        "privacy_security_legal_evidence_privacy_legal_review_completed_default: false",
        "privacy_security_legal_evidence_data_processing_agreement_available_default: false",
        "privacy_security_legal_evidence_vulnerability_management_available_default: false",
        "production_billing_revenue_evidence_status_default: hold",
        "billing_revenue_evidence_pricing_page_complete_default: false",
        "billing_revenue_evidence_payment_provider_complete_default: false",
        "billing_revenue_evidence_invoice_process_complete_default: false",
        "billing_revenue_evidence_tax_review_complete_default: false",
        "billing_revenue_evidence_refund_policy_complete_default: false",
        "billing_revenue_evidence_tenant_billing_isolation_complete_default: false",
        "answer: conditional",
        "recommend_for_controlled_preview_go_no_go: true",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_GO_NO_GO_V0_1.md",
        "/docs/strategy/SAEE_COMMERCIAL_GO_NO_GO_RECOMMENDATION_GATE.md",
        "/saee_backend/services/commercial_go_no_go.py",
        "/scripts/saee_commercial_go_no_go.py",
        "/scripts/saee_commercial_go_no_go_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    print(
        "SAEE_COMMERCIAL_GO_NO_GO_SMOKE: PASS "
        "local_commercial_status=hold "
        "safe_preview_status=go "
        "production_launch_status=hold "
        f"production_blockers={safe_preview['production_blocker_count']} "
        "production_ready=false "
        "customer_validated=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
