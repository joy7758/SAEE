"""Configuration boundary for the SAEE MVP API shell.

This module keeps deployment-facing settings outside the private SAEE core.
Defaults preserve the local demo behavior; commercial hardening can be enabled
with environment variables without changing the public API contract.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Mapping


DEFAULT_LOCAL_ORIGINS = (
    "http://127.0.0.1:8765",
    "http://localhost:8765",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
)

FALSE_VALUES = {"", "0", "false", "no", "off"}
DEFAULT_MAX_AGENTS = 100
DEFAULT_MAX_REPEAT_RUNS = 10_000
DEFAULT_MAX_TIME_HORIZON = 100_000
DEFAULT_MAX_PAYLOAD_BYTES = 1_048_576
DEFAULT_STORAGE_BACKEND = "memory"
DEFAULT_STORAGE_PATH = ".saee_data/saee_mvp.sqlite3"
DEFAULT_REQUEST_AUDIT_PATH = ".saee_data/request_audit.jsonl"
DEFAULT_RETENTION_DAYS = 0
DEFAULT_BACKUP_DIR = ".saee_backups"
DEFAULT_RESTORE_DRILL_DIR = ".saee_restore_drills"
DEFAULT_ALLOWED_TENANT_IDS: tuple[str, ...] = ()
DEFAULT_SUPPORT_CONTACT = ""
DEFAULT_SECURITY_CONTACT = ""
DEFAULT_RESTORE_DRILL_REPORT_PATH = ""
DEFAULT_PRODUCTION_OIDC_ISSUER = ""
DEFAULT_PRODUCTION_OIDC_AUDIENCE = ""
DEFAULT_PRODUCTION_OIDC_JWKS_URL = ""
DEFAULT_PRODUCTION_RBAC_POLICY_PATH = ""
DEFAULT_RBAC_POLICY_PATH = ""
DEFAULT_PREVIEW_JWT_ISSUER = ""
DEFAULT_PREVIEW_JWT_AUDIENCE = ""
DEFAULT_PREVIEW_JWT_HS256_SECRET = ""
DEFAULT_PRODUCTION_AUTH_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_SUPPORT_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_OPERATIONS_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH = ""
DEFAULT_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH = ""
TENANT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _csv(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    return items or default


def tenant_id_format_valid(tenant_id: str) -> bool:
    return bool(TENANT_ID_PATTERN.fullmatch(tenant_id))


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in FALSE_VALUES


def _int(value: str | None, default: int, minimum: int = 1) -> int:
    if value is None:
        return default
    try:
        parsed = int(value.strip())
    except ValueError:
        return default
    if parsed < minimum:
        return default
    return parsed


@dataclass(frozen=True)
class SaeeBackendSettings:
    """Public-shell deployment settings.

    These flags describe the API shell boundary. They are not claims of
    production readiness, customer validation, public SDK release, or private
    core exposure.
    """

    environment: str
    allowed_origins: tuple[str, ...]
    require_api_key: bool
    api_key_configured: bool
    max_agents: int
    max_repeat_runs: int
    max_time_horizon: int
    max_payload_bytes: int
    storage_backend: str
    storage_path: str
    request_audit_enabled: bool
    request_audit_path: str
    retention_days: int
    retention_dry_run: bool
    backup_dir: str
    restore_drill_dir: str
    require_tenant_id: bool
    allowed_tenant_ids: tuple[str, ...]
    synthetic_data_only: bool
    require_rbac_role: bool
    rbac_policy_path: str
    require_jwt_preview_auth: bool
    require_bound_tenant_authorization: bool
    preview_jwt_issuer: str
    preview_jwt_audience: str
    preview_jwt_hs256_secret_configured: bool
    support_contact: str
    security_contact: str
    restore_drill_report_path: str
    production_oidc_issuer: str
    production_oidc_audience: str
    production_oidc_jwks_url: str
    production_rbac_policy_path: str
    production_auth_evidence_path: str
    production_support_evidence_path: str
    production_data_operations_evidence_path: str
    production_operations_evidence_path: str
    production_privacy_security_legal_evidence_path: str
    production_billing_revenue_evidence_path: str
    production_tenant_storage_evidence_path: str
    production_customer_validation_evidence_path: str
    production_ready: bool = False
    customer_validated: bool = False
    public_sdk_released: bool = False
    product_launched: bool = False
    private_core_connected: bool = False
    private_core_exposed: bool = False

    @property
    def auth_mode(self) -> str:
        if self.require_jwt_preview_auth and self.preview_jwt_hs256_secret_configured:
            return "jwt_preview"
        if self.require_jwt_preview_auth:
            return "jwt_preview_required_unconfigured"
        if self.require_api_key and self.api_key_configured:
            return "api_key_preview"
        if self.require_api_key:
            return "api_key_required_unconfigured"
        return "local_none"

    @property
    def ready(self) -> bool:
        if not self.synthetic_data_only:
            return False
        if self.require_api_key and not self.api_key_configured:
            return False
        if self.require_tenant_id and not self.allowed_tenant_ids:
            return False
        if self.require_tenant_id and any(
            not tenant_id_format_valid(tenant_id) for tenant_id in self.allowed_tenant_ids
        ):
            return False
        if self.require_rbac_role and not self.rbac_policy_path:
            return False
        if self.require_jwt_preview_auth and (
            not self.preview_jwt_hs256_secret_configured
            or not self.preview_jwt_issuer
            or not self.preview_jwt_audience
            or not self.rbac_policy_path
        ):
            return False
        if self.require_jwt_preview_auth and (
            not self.require_tenant_id or not self.allowed_tenant_ids
        ):
            return False
        if self.require_tenant_id and self.require_rbac_role and not self.require_jwt_preview_auth:
            return False
        if self.require_bound_tenant_authorization and not (
            self.require_jwt_preview_auth
            and self.require_tenant_id
            and bool(self.allowed_tenant_ids)
            and bool(self.rbac_policy_path)
        ):
            return False
        return True

    def readiness_payload(self) -> dict[str, object]:
        return {
            "status": "ready" if self.ready else "configuration_error",
            "environment": self.environment,
            "api_key_required": self.require_api_key,
            "api_key_configured": self.api_key_configured,
            "auth_boundary_available": True,
            "auth_mode": self.auth_mode,
            "preview_auth_available": self.require_api_key and self.api_key_configured,
            "jwt_preview_auth_available": self.require_jwt_preview_auth
            and self.preview_jwt_hs256_secret_configured
            and bool(self.preview_jwt_issuer)
            and bool(self.preview_jwt_audience)
            and bool(self.rbac_policy_path),
            "jwt_preview_auth_required": self.require_jwt_preview_auth,
            "bound_tenant_authorization_required": self.require_bound_tenant_authorization,
            "bound_tenant_authorization_chain_complete": self.require_bound_tenant_authorization
            and self.ready,
            "header_asserted_tenant_role_authorization_allowed": False,
            "synthetic_data_only": self.synthetic_data_only,
            "real_customer_data_allowed": False,
            "deidentification_proven": False,
            "general_dlp_available": False,
            "jwt_preview_issuer_configured": bool(self.preview_jwt_issuer),
            "jwt_preview_audience_configured": bool(self.preview_jwt_audience),
            "jwt_preview_hs256_secret_configured": self.preview_jwt_hs256_secret_configured,
            "jwt_preview_uses_local_hs256": self.require_jwt_preview_auth,
            "jwt_preview_production_oidc": False,
            "identity_provider_config_readiness_v0_1": True,
            "production_oidc_issuer_configured": bool(self.production_oidc_issuer),
            "production_oidc_audience_configured": bool(self.production_oidc_audience),
            "production_oidc_jwks_url_configured": bool(self.production_oidc_jwks_url),
            "production_oidc_configuration_present": bool(
                self.production_oidc_issuer
                and self.production_oidc_audience
                and self.production_oidc_jwks_url
            ),
            "production_rbac_policy_path_configured": bool(
                self.production_rbac_policy_path
            ),
            "rbac_preview_enforcement_available": True,
            "rbac_role_required": self.require_rbac_role,
            "rbac_policy_path_configured": bool(self.rbac_policy_path),
            "preview_rbac_available": self.require_rbac_role
            and bool(self.rbac_policy_path),
            "external_identity_provider_contacted": False,
            "production_identity_provider_available": False,
            "oauth_oidc_available": False,
            "sso_available": False,
            "rbac_available": False,
            "production_auth_ready": False,
            "production_auth_evidence_readiness_v0_1": True,
            "production_auth_evidence_path_configured": bool(
                self.production_auth_evidence_path
            ),
            "max_agents": self.max_agents,
            "max_repeat_runs": self.max_repeat_runs,
            "max_time_horizon": self.max_time_horizon,
            "max_payload_bytes": self.max_payload_bytes,
            "storage_backend": self.storage_backend,
            "storage_path_configured": bool(self.storage_path),
            "durable_persistence": self.storage_backend == "sqlite",
            "request_audit_enabled": self.request_audit_enabled,
            "request_audit_path_configured": bool(self.request_audit_path),
            "request_audit_log_available": self.request_audit_enabled,
            "local_operations_telemetry_available": True,
            "operations_telemetry_source": "request_audit_jsonl",
            "operations_telemetry_external_export_available": False,
            "local_alert_policy_available": True,
            "external_alert_delivery_available": False,
            "operations_readiness_available": True,
            "operations_readiness_status": "hold",
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
            "security_contact_configured": bool(self.security_contact),
            "vulnerability_intake_contact_configured": bool(self.security_contact),
            "controlled_preview_security_contact_required": self.environment.strip().lower()
            not in {"local", "dev", "development"},
            "vulnerability_triage_runbook_available": True,
            "vulnerability_remediation_sla_available": False,
            "coordinated_disclosure_available": False,
            "vulnerability_management_available": False,
            "production_vulnerability_management_ready": False,
            "support_readiness_v0_1": True,
            "production_support_evidence_readiness_v0_1": True,
            "production_support_evidence_path_configured": bool(
                self.production_support_evidence_path
            ),
            "production_data_operations_evidence_readiness_v0_1": True,
            "production_data_operations_evidence_path_configured": bool(
                self.production_data_operations_evidence_path
            ),
            "production_operations_evidence_readiness_v0_1": True,
            "production_operations_evidence_path_configured": bool(
                self.production_operations_evidence_path
            ),
            "production_privacy_security_legal_evidence_readiness_v0_1": True,
            "production_privacy_security_legal_evidence_path_configured": bool(
                self.production_privacy_security_legal_evidence_path
            ),
            "production_billing_revenue_evidence_readiness_v0_1": True,
            "production_billing_revenue_evidence_path_configured": bool(
                self.production_billing_revenue_evidence_path
            ),
            "production_tenant_storage_evidence_readiness_v0_1": True,
            "production_tenant_storage_evidence_path_configured": bool(
                self.production_tenant_storage_evidence_path
            ),
            "production_customer_validation_evidence_readiness_v0_1": True,
            "production_customer_validation_evidence_path_configured": bool(
                self.production_customer_validation_evidence_path
            ),
            "support_runbook_available": True,
            "support_case_template_available": True,
            "support_sla_draft_available": True,
            "support_response_targets_documented": True,
            "support_contact_configured": bool(self.support_contact),
            "customer_support_available": False,
            "production_support_available": False,
            "on_call_rotation_available": False,
            "sla_available": False,
            "support_process_available": False,
            "production_operations_ready": False,
            "commercial_preflight_available": True,
            "commercial_preflight_required_for_public_use": True,
            "data_retention_available": True,
            "retention_policy_configured": self.retention_days > 0,
            "retention_days": self.retention_days,
            "retention_dry_run": self.retention_dry_run,
            "data_backup_available": True,
            "backup_dir_configured": bool(self.backup_dir),
            "backup_default_automatic": False,
            "restore_drill_available": True,
            "restore_drill_dir_configured": bool(self.restore_drill_dir),
            "restore_drill_default_automatic": False,
            "restore_drill_report_configured": bool(self.restore_drill_report_path),
            "controlled_preview_restore_drill_evidence_required": self.environment.strip().lower()
            not in {"local", "dev", "development"},
            "production_restore_policy_available": False,
            "restore_tested": False,
            "tenant_boundary_available": True,
            "tenant_id_required": self.require_tenant_id,
            "tenant_allowlist_configured": bool(self.allowed_tenant_ids),
            "preview_storage_scoped_by_tenant": self.require_tenant_id
            and bool(self.allowed_tenant_ids),
            "tenant_storage_isolated": False,
            "tenant_billing_isolated": False,
            "multi_tenant_production_ready": False,
            "production_ready": self.production_ready,
            "customer_validated": self.customer_validated,
            "public_sdk_released": self.public_sdk_released,
            "product_launched": self.product_launched,
            "private_core_connected": self.private_core_connected,
            "private_core_exposed": self.private_core_exposed,
        }


def load_settings(env: Mapping[str, str] | None = None) -> SaeeBackendSettings:
    source = os.environ if env is None else env
    environment = source.get("SAEE_ENV", "local").strip() or "local"
    return SaeeBackendSettings(
        environment=environment,
        allowed_origins=_csv(source.get("SAEE_ALLOWED_ORIGINS"), DEFAULT_LOCAL_ORIGINS),
        require_api_key=_bool(source.get("SAEE_REQUIRE_API_KEY")),
        api_key_configured=bool(source.get("SAEE_API_KEY", "").strip()),
        max_agents=_int(source.get("SAEE_MAX_AGENTS"), DEFAULT_MAX_AGENTS),
        max_repeat_runs=_int(source.get("SAEE_MAX_REPEAT_RUNS"), DEFAULT_MAX_REPEAT_RUNS),
        max_time_horizon=_int(source.get("SAEE_MAX_TIME_HORIZON"), DEFAULT_MAX_TIME_HORIZON),
        max_payload_bytes=_int(source.get("SAEE_MAX_PAYLOAD_BYTES"), DEFAULT_MAX_PAYLOAD_BYTES),
        storage_backend=source.get("SAEE_STORAGE_BACKEND", DEFAULT_STORAGE_BACKEND).strip().lower()
        or DEFAULT_STORAGE_BACKEND,
        storage_path=source.get("SAEE_STORAGE_PATH", DEFAULT_STORAGE_PATH).strip()
        or DEFAULT_STORAGE_PATH,
        request_audit_enabled=_bool(source.get("SAEE_REQUEST_AUDIT_ENABLED")),
        request_audit_path=source.get("SAEE_REQUEST_AUDIT_PATH", DEFAULT_REQUEST_AUDIT_PATH).strip()
        or DEFAULT_REQUEST_AUDIT_PATH,
        retention_days=_int(source.get("SAEE_RETENTION_DAYS"), DEFAULT_RETENTION_DAYS, minimum=0),
        retention_dry_run=_bool(source.get("SAEE_RETENTION_DRY_RUN"), default=True),
        backup_dir=source.get("SAEE_BACKUP_DIR", DEFAULT_BACKUP_DIR).strip()
        or DEFAULT_BACKUP_DIR,
        restore_drill_dir=source.get("SAEE_RESTORE_DRILL_DIR", DEFAULT_RESTORE_DRILL_DIR).strip()
        or DEFAULT_RESTORE_DRILL_DIR,
        require_tenant_id=_bool(source.get("SAEE_REQUIRE_TENANT_ID")),
        allowed_tenant_ids=_csv(source.get("SAEE_ALLOWED_TENANT_IDS"), DEFAULT_ALLOWED_TENANT_IDS),
        synthetic_data_only=_bool(
            source.get("SAEE_SYNTHETIC_DATA_ONLY"),
            default=environment.strip().lower() in {"local", "dev", "development"},
        ),
        require_rbac_role=_bool(source.get("SAEE_REQUIRE_RBAC_ROLE")),
        rbac_policy_path=source.get(
            "SAEE_RBAC_POLICY_PATH",
            source.get("SAEE_PRODUCTION_RBAC_POLICY_PATH", DEFAULT_RBAC_POLICY_PATH),
        ).strip(),
        require_jwt_preview_auth=_bool(source.get("SAEE_REQUIRE_JWT_PREVIEW_AUTH")),
        require_bound_tenant_authorization=_bool(
            source.get("SAEE_REQUIRE_BOUND_TENANT_AUTHORIZATION")
        ),
        preview_jwt_issuer=source.get(
            "SAEE_PREVIEW_JWT_ISSUER", DEFAULT_PREVIEW_JWT_ISSUER
        ).strip(),
        preview_jwt_audience=source.get(
            "SAEE_PREVIEW_JWT_AUDIENCE", DEFAULT_PREVIEW_JWT_AUDIENCE
        ).strip(),
        preview_jwt_hs256_secret_configured=bool(
            source.get("SAEE_PREVIEW_JWT_HS256_SECRET", DEFAULT_PREVIEW_JWT_HS256_SECRET).strip()
        ),
        support_contact=source.get("SAEE_SUPPORT_CONTACT", DEFAULT_SUPPORT_CONTACT).strip(),
        security_contact=source.get("SAEE_SECURITY_CONTACT", DEFAULT_SECURITY_CONTACT).strip(),
        restore_drill_report_path=source.get(
            "SAEE_RESTORE_DRILL_REPORT_PATH", DEFAULT_RESTORE_DRILL_REPORT_PATH
        ).strip(),
        production_oidc_issuer=source.get(
            "SAEE_PRODUCTION_OIDC_ISSUER", DEFAULT_PRODUCTION_OIDC_ISSUER
        ).strip(),
        production_oidc_audience=source.get(
            "SAEE_PRODUCTION_OIDC_AUDIENCE", DEFAULT_PRODUCTION_OIDC_AUDIENCE
        ).strip(),
        production_oidc_jwks_url=source.get(
            "SAEE_PRODUCTION_OIDC_JWKS_URL", DEFAULT_PRODUCTION_OIDC_JWKS_URL
        ).strip(),
        production_rbac_policy_path=source.get(
            "SAEE_PRODUCTION_RBAC_POLICY_PATH", DEFAULT_PRODUCTION_RBAC_POLICY_PATH
        ).strip(),
        production_auth_evidence_path=source.get(
            "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_AUTH_EVIDENCE_PATH,
        ).strip(),
        production_support_evidence_path=source.get(
            "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_SUPPORT_EVIDENCE_PATH,
        ).strip(),
        production_data_operations_evidence_path=source.get(
            "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH,
        ).strip(),
        production_operations_evidence_path=source.get(
            "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_OPERATIONS_EVIDENCE_PATH,
        ).strip(),
        production_privacy_security_legal_evidence_path=source.get(
            "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH,
        ).strip(),
        production_billing_revenue_evidence_path=source.get(
            "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH,
        ).strip(),
        production_tenant_storage_evidence_path=source.get(
            "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH,
        ).strip(),
        production_customer_validation_evidence_path=source.get(
            "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH",
            DEFAULT_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH,
        ).strip(),
    )


SETTINGS = load_settings()
