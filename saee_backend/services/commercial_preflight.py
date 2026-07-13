"""Commercial preflight checks for the SAEE MVP API shell.

The preflight layer reads public-shell settings and reports whether a
configuration is safe enough for a controlled preview. It does not start the
server, call external services, change API schema, or inspect private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import DEFAULT_LOCAL_ORIGINS, SaeeBackendSettings
from saee_backend.services.data_restore_drill import validate_restore_drill_report


PreflightSeverity = Literal["info", "blocker"]
PreflightStatus = Literal["pass", "hold", "stop"]


@dataclass(frozen=True)
class PreflightFinding:
    check_id: str
    severity: PreflightSeverity
    passed: bool
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "passed": self.passed,
            "message": self.message,
        }


def _finding(check_id: str, severity: PreflightSeverity, passed: bool, message: str) -> PreflightFinding:
    return PreflightFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def public_use_required(settings: SaeeBackendSettings) -> bool:
    return settings.environment.strip().lower() not in {"local", "dev", "development"}


def evaluate_commercial_preflight(settings: SaeeBackendSettings) -> dict[str, object]:
    """Return a deterministic preflight report for the public API shell."""

    public_use = public_use_required(settings)
    restore_drill_evidence = validate_restore_drill_report(settings.restore_drill_report_path)
    findings: list[PreflightFinding] = [
        _finding(
            "environment_scope",
            "info",
            True,
            "public-use preflight enforced for non-local environments"
            if public_use
            else "local environment detected; public-use controls are advisory",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false until a separate production readiness gate passes",
        ),
        _finding(
            "customer_validation_non_claim",
            "blocker",
            settings.customer_validated is False,
            "customer_validated must remain false until real customer validation is recorded",
        ),
        _finding(
            "product_launch_non_claim",
            "blocker",
            settings.product_launched is False,
            "product_launched must remain false until a separate launch gate passes",
        ),
        _finding(
            "production_auth_non_claim",
            "info",
            True,
            "production_auth_ready remains false; API key auth is controlled-preview only",
        ),
        _finding(
            "production_operations_non_claim",
            "info",
            True,
            "production_operations_ready remains false; monitoring, external alert delivery, on-call, SLA, and customer support are not configured",
        ),
        _finding(
            "privacy_security_review_non_claim",
            "info",
            True,
            "privacy/security readiness exists as a review draft only; formal review and certification remain false",
        ),
        _finding(
            "pilot_validation_non_claim",
            "info",
            True,
            "pilot validation readiness exists as a plan/template only; customer validation remains false",
        ),
        _finding(
            "billing_pricing_non_claim",
            "info",
            True,
            "billing and pricing readiness exists as review material only; published pricing, payment, and revenue validation remain false",
        ),
        _finding(
            "private_core_non_exposure",
            "blocker",
            settings.private_core_exposed is False,
            "private_core_exposed must remain false",
        ),
    ]

    if public_use:
        findings.extend(
            [
                _finding(
                    "api_key_required",
                    "blocker",
                    settings.require_api_key,
                    "non-local use must require X-SAEE-API-Key",
                ),
                _finding(
                    "api_key_configured",
                    "blocker",
                    settings.api_key_configured,
                    "non-local use must configure SAEE_API_KEY",
                ),
                _finding(
                    "cors_not_default_local",
                    "blocker",
                    settings.allowed_origins != DEFAULT_LOCAL_ORIGINS and "*" not in settings.allowed_origins,
                    "non-local use must configure explicit non-wildcard CORS origins",
                ),
                _finding(
                    "durable_storage_enabled",
                    "blocker",
                    settings.storage_backend == "sqlite",
                    "non-local use must enable SAEE_STORAGE_BACKEND=sqlite for local durable preview storage",
                ),
                _finding(
                    "request_audit_enabled",
                    "blocker",
                    settings.request_audit_enabled,
                    "non-local use must enable SAEE_REQUEST_AUDIT_ENABLED=true",
                ),
                _finding(
                    "retention_policy_configured",
                    "blocker",
                    settings.retention_days > 0,
                    "non-local use must configure SAEE_RETENTION_DAYS",
                ),
                _finding(
                    "tenant_id_required",
                    "blocker",
                    settings.require_tenant_id,
                    "non-local use must require X-SAEE-Tenant-ID",
                ),
                _finding(
                    "tenant_allowlist_configured",
                    "blocker",
                    bool(settings.allowed_tenant_ids),
                    "non-local use must configure SAEE_ALLOWED_TENANT_IDS",
                ),
                _finding(
                    "support_contact_configured",
                    "blocker",
                    bool(settings.support_contact),
                    "non-local controlled preview must configure SAEE_SUPPORT_CONTACT for human support intake",
                ),
                _finding(
                    "security_contact_configured",
                    "blocker",
                    bool(settings.security_contact),
                    "non-local controlled preview must configure SAEE_SECURITY_CONTACT for vulnerability intake",
                ),
                _finding(
                    "restore_drill_report_configured",
                    "blocker",
                    restore_drill_evidence["restore_drill_report_configured"] is True,
                    "non-local controlled preview must configure SAEE_RESTORE_DRILL_REPORT_PATH",
                ),
                _finding(
                    "restore_drill_report_passed",
                    "blocker",
                    restore_drill_evidence["controlled_preview_restore_drill_passed"] is True,
                    "non-local controlled preview must reference a passing isolated restore drill report",
                ),
            ]
        )

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    if blockers:
        status: PreflightStatus = "hold"
    else:
        status = "pass" if public_use else "hold"

    if blockers:
        next_action = "fix preflight blockers before controlled preview"
    elif not public_use:
        next_action = "keep local demo mode; configure non-local controls before controlled preview"
    else:
        next_action = "controlled preview configuration passes preflight; production readiness remains false"

    return {
        "preflight_type": "commercial_public_shell_preflight",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "product_launched": settings.product_launched,
        "public_sdk_released": settings.public_sdk_released,
        "private_core_exposed": settings.private_core_exposed,
        "auth_boundary_available": True,
        "auth_mode": settings.auth_mode,
        "preview_auth_available": settings.require_api_key and settings.api_key_configured,
        "production_auth_ready": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "sso_available": False,
        "rbac_available": False,
        "operations_readiness_available": True,
        "operations_readiness_status": "hold",
        "local_operations_telemetry_available": True,
        "operations_telemetry_external_export_available": False,
        "local_alert_policy_available": True,
        "external_alert_delivery_available": False,
        "production_monitoring_available": False,
        "alerting_available": False,
        "incident_response_runbook_available": True,
        "pilot_validation_readiness_v0_1": True,
        "pilot_validation_status": "hold",
        "first_user_test_plan_available": True,
        "feedback_form_available": True,
        "success_criteria_available": True,
        "pilot_result_template_available": True,
        "pilot_session_protocol_available": True,
        "pilot_sessions_completed": 0,
        "pilot_results_recorded": False,
        "customer_permission_recorded": False,
        "customer_contacted": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "user_upload_enabled": False,
        "billing_pricing_readiness_v0_1": True,
        "billing_pricing_status": "hold",
        "pricing_packaging_plan_available": True,
        "internal_price_bands_available": True,
        "billing_policy_draft_available": True,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_process_ready": False,
        "tax_review_completed": False,
        "refund_policy_available": False,
        "billing_operations_ready": False,
        "tenant_billing_isolated": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "privacy_security_review_v0_1": True,
        "privacy_security_review_status": "hold",
        "data_classification_available": True,
        "public_shell_data_map_available": True,
        "pii_policy_draft_available": True,
        "personal_data_allowed": False,
        "secret_handling_guidance_available": True,
        "third_party_processor_inventory_available": True,
        "legal_readiness_v0_1": True,
        "legal_readiness_status": "hold",
        "terms_of_service_draft_available": True,
        "terms_of_service_published": False,
        "terms_legal_review_completed": False,
        "privacy_notice_draft_available": True,
        "privacy_notice_published": False,
        "dpa_review_packet_available": True,
        "data_processing_agreement_draft_available": True,
        "customer_contract_template_available": False,
        "legal_approval_completed": False,
        "production_legal_ready": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "formal_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_available": False,
        "security_certification_available": False,
        "soc2_available": False,
        "iso27001_available": False,
        "penetration_test_completed": False,
        "vulnerability_management_available": False,
        "compliance_logging_available": False,
        "production_security_ready": False,
        "customer_data_processing_ready": False,
        "vulnerability_management_readiness_v0_1": True,
        "vulnerability_management_readiness_status": "hold",
        "vulnerability_disclosure_policy_draft_available": True,
        "security_contact_configured": bool(settings.security_contact),
        "vulnerability_intake_contact_configured": bool(settings.security_contact),
        "controlled_preview_security_contact_required": public_use,
        "vulnerability_triage_runbook_available": True,
        "vulnerability_remediation_sla_available": False,
        "coordinated_disclosure_available": False,
        "vulnerability_management_available": False,
        "production_vulnerability_management_ready": False,
        "support_readiness_v0_1": True,
        "support_runbook_available": True,
        "support_case_template_available": True,
        "support_sla_draft_available": True,
        "support_response_targets_documented": True,
        "support_contact_configured": bool(settings.support_contact),
        "customer_support_available": False,
        "production_support_available": False,
        "on_call_rotation_available": False,
        "sla_available": False,
        "support_process_available": False,
        "production_operations_ready": False,
        "restore_drill_report_configured": restore_drill_evidence[
            "restore_drill_report_configured"
        ],
        "restore_drill_report_exists": restore_drill_evidence["restore_drill_report_exists"],
        "controlled_preview_restore_drill_passed": restore_drill_evidence[
            "controlled_preview_restore_drill_passed"
        ],
        "controlled_preview_restore_drill_evidence_required": public_use,
        "restore_to_live_path": False,
        "production_restore_tested": False,
        "production_restore_policy_available": False,
        "preview_storage_scoped_by_tenant": settings.require_tenant_id
        and bool(settings.allowed_tenant_ids),
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": next_action,
    }
