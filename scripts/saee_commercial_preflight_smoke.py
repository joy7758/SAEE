#!/usr/bin/env python3
"""Smoke check for SAEE commercial preflight v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_preflight import evaluate_commercial_preflight


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_COMMERCIAL_PREFLIGHT_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_COMMERCIAL_PREFLIGHT_SMOKE: FAIL: missing finding {check_id}")


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


def main() -> None:
    local = evaluate_commercial_preflight(load_settings({}))
    require(local["preflight_type"] == "commercial_public_shell_preflight", "wrong preflight type")
    require(local["public_use_required"] is False, "local environment must not require public-use controls")
    require(local["status"] == "hold", "default local config must remain hold, not pass")
    require(local["production_ready"] is False, "preflight must preserve production false")
    require(local["production_auth_ready"] is False, "preflight must preserve production auth false")
    require(local["oauth_oidc_available"] is False, "preflight must preserve OIDC false")
    require(local["sso_available"] is False, "preflight must preserve SSO false")
    require(local["rbac_available"] is False, "preflight must preserve RBAC false")
    require(local["operations_readiness_available"] is True, "preflight must report operations readiness")
    require(local["local_operations_telemetry_available"] is True, "preflight must report telemetry")
    require(local["operations_telemetry_external_export_available"] is False, "preflight telemetry export false")
    require(local["local_alert_policy_available"] is True, "preflight must report alert policy")
    require(local["external_alert_delivery_available"] is False, "preflight alert delivery false")
    require(local["operations_readiness_status"] == "hold", "preflight operations readiness must hold")
    require(local["production_monitoring_available"] is False, "preflight must preserve monitoring false")
    require(local["alerting_available"] is False, "preflight must preserve alerting false")
    require(local["incident_response_runbook_available"] is True, "preflight must report incident runbook")
    require(local["pilot_validation_readiness_v0_1"] is True, "preflight must report pilot validation")
    require(local["pilot_validation_status"] == "hold", "preflight pilot validation hold")
    require(local["pilot_sessions_completed"] == 0, "preflight pilot sessions zero")
    require(local["pilot_results_recorded"] is False, "preflight pilot results false")
    require(local["customer_permission_recorded"] is False, "preflight customer permission false")
    require(local["customer_contacted"] is False, "preflight customer contact false")
    require(local["customer_validated"] is False, "preflight customer validation false")
    require(local["user_upload_enabled"] is False, "preflight user upload false")
    require(local["billing_pricing_readiness_v0_1"] is True, "preflight must report billing/pricing")
    require(local["billing_pricing_status"] == "hold", "preflight billing/pricing hold")
    require(local["pricing_page_published"] is False, "preflight pricing page false")
    require(local["sales_offer_sent"] is False, "preflight sales offer false")
    require(local["payment_provider_configured"] is False, "preflight payment provider false")
    require(local["checkout_enabled"] is False, "preflight checkout false")
    require(local["invoice_process_ready"] is False, "preflight invoice false")
    require(local["tax_review_completed"] is False, "preflight tax false")
    require(local["billing_operations_ready"] is False, "preflight billing ops false")
    require(local["customer_payment_collected"] is False, "preflight payment collected false")
    require(local["revenue_validated"] is False, "preflight revenue false")
    require(local["privacy_security_review_v0_1"] is True, "preflight must report privacy/security")
    require(local["privacy_security_review_status"] == "hold", "preflight privacy/security must hold")
    require(local["data_classification_available"] is True, "preflight must report data classification")
    require(local["personal_data_allowed"] is False, "preflight personal data false")
    require(local["legal_readiness_v0_1"] is True, "preflight must report legal readiness")
    require(local["legal_readiness_status"] == "hold", "preflight legal readiness must hold")
    require(local["terms_of_service_draft_available"] is True, "preflight terms draft true")
    require(local["terms_of_service_published"] is False, "preflight terms published false")
    require(local["privacy_notice_draft_available"] is True, "preflight privacy notice draft true")
    require(local["privacy_notice_published"] is False, "preflight privacy notice published false")
    require(local["dpa_review_packet_available"] is True, "preflight DPA packet true")
    require(local["data_processing_agreement_draft_available"] is True, "preflight DPA draft true")
    require(local["production_legal_ready"] is False, "preflight production legal false")
    require(local["formal_security_review_completed"] is False, "preflight formal security false")
    require(local["privacy_legal_review_completed"] is False, "preflight privacy legal false")
    require(local["security_certification_available"] is False, "preflight certification false")
    require(local["production_security_ready"] is False, "preflight production security false")
    require(local["support_readiness_v0_1"] is True, "preflight must report support readiness")
    require(local["support_runbook_available"] is True, "preflight must report support runbook")
    require(local["support_contact_configured"] is False, "preflight support contact false")
    require(local["customer_support_available"] is False, "preflight customer support false")
    require(local["production_support_available"] is False, "preflight production support false")
    require(local["production_operations_ready"] is False, "preflight must preserve operations false")
    require(local["private_core_exposed"] is False, "preflight must preserve private core false")
    require(local["external_calls_made"] is False, "preflight must not make external calls")
    require(local["api_schema_modified"] is False, "preflight must not modify API schema")
    require(local["runtime_modified"] is False, "preflight must not modify runtime")
    require(local["kernel_modified"] is False, "preflight must not modify kernel")

    unsafe_preview = evaluate_commercial_preflight(load_settings({"SAEE_ENV": "preview"}))
    require(unsafe_preview["public_use_required"] is True, "preview must require public-use controls")
    require(unsafe_preview["status"] == "hold", "unsafe preview must hold")
    require(finding(unsafe_preview, "api_key_required")["passed"] is False, "preview must require API key")
    require(finding(unsafe_preview, "cors_not_default_local")["passed"] is False, "preview must reject default CORS")
    require(finding(unsafe_preview, "durable_storage_enabled")["passed"] is False, "preview must require durable storage")
    require(finding(unsafe_preview, "request_audit_enabled")["passed"] is False, "preview must require request audit")
    require(
        finding(unsafe_preview, "retention_policy_configured")["passed"] is False,
        "preview must require retention policy",
    )
    require(
        finding(unsafe_preview, "tenant_id_required")["passed"] is False,
        "preview must require tenant ID guard",
    )
    require(
        finding(unsafe_preview, "tenant_allowlist_configured")["passed"] is False,
        "preview must require tenant allowlist",
    )
    require(
        finding(unsafe_preview, "support_contact_configured")["passed"] is False,
        "preview must require support contact",
    )
    require(
        finding(unsafe_preview, "security_contact_configured")["passed"] is False,
        "preview must require security contact",
    )
    require(
        finding(unsafe_preview, "restore_drill_report_configured")["passed"] is False,
        "preview must require restore drill report path",
    )
    require(
        finding(unsafe_preview, "restore_drill_report_passed")["passed"] is False,
        "preview must require passing restore drill report",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        restore_report = write_restore_report(Path(tmpdir))
        safe_preview = evaluate_commercial_preflight(
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
                }
            )
        )
    require(safe_preview["status"] == "pass", "safe preview must pass preflight")
    require(safe_preview["blocker_count"] == 0, "safe preview must have no blockers")
    require(safe_preview["production_ready"] is False, "safe preview must not claim production")
    require(safe_preview["preview_auth_available"] is True, "safe preview must report preview auth")
    require(safe_preview["production_auth_ready"] is False, "safe preview must not claim production auth")
    require(safe_preview["legal_readiness_v0_1"] is True, "safe preview legal readiness true")
    require(safe_preview["terms_of_service_published"] is False, "safe preview terms published false")
    require(safe_preview["privacy_notice_published"] is False, "safe preview privacy published false")
    require(
        safe_preview["data_processing_agreement_available"] is False,
        "safe preview DPA available false",
    )
    require(safe_preview["production_legal_ready"] is False, "safe preview production legal false")
    require(
        safe_preview["production_security_ready"] is False,
        "safe preview must not claim production security",
    )
    require(
        safe_preview["production_operations_ready"] is False,
        "safe preview must not claim production operations",
    )
    require(safe_preview["customer_validated"] is False, "safe preview must not claim customer validation")
    require(safe_preview["pilot_sessions_completed"] == 0, "safe preview must not claim pilot sessions")
    require(safe_preview["pilot_results_recorded"] is False, "safe preview must not claim pilot results")
    require(safe_preview["pricing_page_published"] is False, "safe preview must not claim pricing")
    require(safe_preview["revenue_validated"] is False, "safe preview must not claim revenue")
    require(safe_preview["payment_provider_configured"] is False, "safe preview must not claim payment provider")
    require(
        safe_preview["support_contact_configured"] is True,
        "safe preview must report configured support contact",
    )
    require(
        safe_preview["customer_support_available"] is False,
        "safe preview must not claim customer support",
    )
    require(
        safe_preview["security_contact_configured"] is True,
        "safe preview must report configured security contact",
    )
    require(
        safe_preview["vulnerability_management_available"] is False,
        "safe preview must not claim vulnerability management",
    )
    require(
        safe_preview["production_vulnerability_management_ready"] is False,
        "safe preview must not claim production vulnerability management",
    )
    require(safe_preview["sla_available"] is False, "safe preview must not claim SLA")
    require(
        safe_preview["controlled_preview_restore_drill_passed"] is True,
        "safe preview must validate restore drill evidence",
    )
    require(
        safe_preview["production_restore_tested"] is False,
        "safe preview must not claim production restore testing",
    )
    require(
        safe_preview["production_restore_policy_available"] is False,
        "safe preview must not claim production restore policy",
    )
    require(safe_preview["product_launched"] is False, "safe preview must not claim launch")
    require(safe_preview["private_core_exposed"] is False, "safe preview must not expose private core")
    require(
        finding(safe_preview, "tenant_id_required")["passed"] is True,
        "safe preview must require tenant ID guard",
    )
    require(
        finding(safe_preview, "tenant_allowlist_configured")["passed"] is True,
        "safe preview must configure tenant allowlist",
    )
    require(
        finding(safe_preview, "support_contact_configured")["passed"] is True,
        "safe preview must configure support contact",
    )
    require(
        finding(safe_preview, "security_contact_configured")["passed"] is True,
        "safe preview must configure security contact",
    )
    require(
        finding(safe_preview, "restore_drill_report_passed")["passed"] is True,
        "safe preview must validate restore drill report",
    )

    doc = (ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_PREFLIGHT_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_COMMERCIAL_PREFLIGHT_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("commercial_preflight_v0_1: true" in doc, "preflight doc missing state")
    require("auth_readiness_v0_1: true" in doc, "preflight doc missing auth readiness")
    require("operations_telemetry_v0_1: true" in doc, "preflight doc missing telemetry")
    require("operations_alert_policy_v0_1: true" in doc, "preflight doc missing alert policy")
    require("local_alert_policy_available: true" in doc, "preflight doc alert policy true")
    require("external_alert_delivery_available: false" in doc, "preflight doc alert delivery false")
    require("pilot_validation_readiness_v0_1: true" in doc, "preflight doc pilot validation true")
    require("pilot_sessions_completed: 0" in doc, "preflight doc pilot sessions zero")
    require("pilot_results_recorded: false" in doc, "preflight doc pilot results false")
    require("customer_validated: false" in doc, "preflight doc customer validation false")
    require("customer_contacted: false" in doc, "preflight doc customer contact false")
    require("user_upload_enabled: false" in doc, "preflight doc user upload false")
    require("billing_pricing_readiness_v0_1: true" in doc, "preflight doc billing/pricing true")
    require("billing_pricing_status: hold" in doc, "preflight doc billing/pricing hold")
    require("pricing_page_published: false" in doc, "preflight doc pricing false")
    require("sales_offer_sent: false" in doc, "preflight doc offer false")
    require("payment_provider_configured: false" in doc, "preflight doc payment false")
    require("checkout_enabled: false" in doc, "preflight doc checkout false")
    require("invoice_process_ready: false" in doc, "preflight doc invoice false")
    require("tax_review_completed: false" in doc, "preflight doc tax false")
    require("billing_operations_ready: false" in doc, "preflight doc billing ops false")
    require("customer_payment_collected: false" in doc, "preflight doc payment collected false")
    require("revenue_validated: false" in doc, "preflight doc revenue false")
    require("privacy_security_review_v0_1: true" in doc, "preflight doc privacy/security true")
    require("legal_readiness_v0_1: true" in doc, "preflight doc legal readiness true")
    require("terms_of_service_draft_available: true" in doc, "preflight doc terms draft true")
    require("terms_of_service_published: false" in doc, "preflight doc terms published false")
    require("privacy_notice_draft_available: true" in doc, "preflight doc privacy draft true")
    require("privacy_notice_published: false" in doc, "preflight doc privacy published false")
    require("dpa_review_packet_available: true" in doc, "preflight doc DPA packet true")
    require(
        "data_processing_agreement_draft_available: true" in doc,
        "preflight doc DPA draft true",
    )
    require("production_legal_ready: false" in doc, "preflight doc production legal false")
    require("formal_security_review_completed: false" in doc, "preflight doc formal review false")
    require("privacy_legal_review_completed: false" in doc, "preflight doc privacy review false")
    require("production_security_ready: false" in doc, "preflight doc production security false")
    require("support_readiness_v0_1: true" in doc, "preflight doc support readiness true")
    require("support_contact_configured: false" in doc, "preflight doc support contact false")
    require("customer_support_available: false" in doc, "preflight doc customer support false")
    require("SAEE_SECURITY_CONTACT" in doc, "preflight doc missing security contact")
    require("security_contact_configured: false" in doc, "preflight doc security contact false")
    require(
        "vulnerability_management_available: false" in doc,
        "preflight doc vulnerability management false",
    )
    require(
        "production_vulnerability_management_ready: false" in doc,
        "preflight doc production vulnerability false",
    )
    require("SAEE_RESTORE_DRILL_REPORT_PATH" in doc, "preflight doc missing restore report path")
    require("restore_drill_report_configured: false" in doc, "preflight doc restore report default false")
    require(
        "controlled_preview_restore_drill_passed: false" in doc,
        "preflight doc restore drill pass default false",
    )
    require(
        "restore_integrity_checks_passed_after_placeholder_replacement: true" in doc,
        "preflight doc restore integrity pass after placeholder replacement",
    )
    require("production_restore_tested: false" in doc, "preflight doc production restore tested false")
    require(
        "production_restore_policy_available: false" in doc,
        "preflight doc production restore policy false",
    )
    require("operations_readiness_v0_1: true" in doc, "preflight doc missing operations readiness")
    require("production_ready: false" in doc, "preflight doc must preserve production false")
    require("production_auth_ready: false" in doc, "preflight doc must preserve auth false")
    require("production_operations_ready: false" in doc, "preflight doc must preserve operations false")
    require("answer: conditional" in gate, "preflight gate must remain conditional")
    require("recommend_public_launch_now: false" in gate, "preflight gate must not recommend launch")

    print(
        "SAEE_COMMERCIAL_PREFLIGHT_SMOKE: PASS "
        "default_local_hold=true "
        "unsafe_preview_hold=true "
        "safe_preview_pass=true "
        "local_alert_policy_available=true "
        "external_alert_delivery_available=false "
        "local_support_contact_configured=false "
        "safe_preview_support_contact_configured=true "
        "safe_preview_security_contact_configured=true "
        "production_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
