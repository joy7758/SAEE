#!/usr/bin/env python3
"""Smoke check for the SAEE controlled-preview environment template."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_preflight import evaluate_commercial_preflight


ENV_PATH = ROOT / "saee_backend/config_examples/controlled_preview.env.example"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/CONTROLLED_PREVIEW_ENV_TEMPLATE_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CONTROLLED_PREVIEW_ENV_TEMPLATE_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_CONTROLLED_PREVIEW_ENV_TEMPLATE_SMOKE: FAIL: {message}")


def parse_env_template(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        require("=" in line, f"invalid env line: {raw_line}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


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
    require(ENV_PATH.exists(), "env template missing")
    require(DOC_PATH.exists(), "readiness doc missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    env_text = ENV_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")
    gate = GATE_PATH.read_text(encoding="utf-8")
    values = parse_env_template(env_text)

    required_env = {
        "SAEE_ENV": "preview",
        "SAEE_ALLOWED_ORIGINS": "https://preview.example.invalid",
        "SAEE_REQUIRE_API_KEY": "true",
        "SAEE_API_KEY": "replace-with-random-preview-key-min-32-chars",
        "SAEE_REQUIRE_TENANT_ID": "true",
        "SAEE_ALLOWED_TENANT_IDS": "preview-tenant-001",
        "SAEE_STORAGE_BACKEND": "sqlite",
        "SAEE_REQUEST_AUDIT_ENABLED": "true",
        "SAEE_RETENTION_DAYS": "30",
        "SAEE_RETENTION_DRY_RUN": "true",
        "SAEE_SUPPORT_CONTACT": "replace-with-controlled-preview-support-mailbox-or-ticket-queue",
        "SAEE_SECURITY_CONTACT": "replace-with-controlled-preview-security-mailbox-or-ticket-queue",
        "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": "replace-with-local-production-auth-evidence-json-path",
        "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": "replace-with-local-production-privacy-security-legal-evidence-json-path",
        "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": "replace-with-local-production-billing-revenue-evidence-json-path",
        "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": "replace-with-local-production-tenant-storage-evidence-json-path",
        "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": "replace-with-local-production-customer-validation-evidence-json-path",
        "SAEE_RESTORE_DRILL_REPORT_PATH": "replace-with-path-to-passing-RESTORE_DRILL_REPORT.json",
    }
    for key, expected in required_env.items():
        require(values.get(key) == expected, f"{key} mismatch")

    forbidden_secret_patterns = [
        r"sk-[A-Za-z0-9]",
        r"ghp_[A-Za-z0-9]",
        r"AKIA[A-Z0-9]",
        r"-----BEGIN",
        r"password=",
    ]
    for pattern in forbidden_secret_patterns:
        require(not re.search(pattern, env_text, re.IGNORECASE), f"secret-like token found: {pattern}")

    with tempfile.TemporaryDirectory() as tmpdir:
        restore_report = write_restore_report(Path(tmpdir))
        runtime_values = dict(values)
        runtime_values["SAEE_RESTORE_DRILL_REPORT_PATH"] = str(restore_report)
        settings = load_settings(runtime_values)
        report = evaluate_commercial_preflight(settings)
    require(report["status"] == "pass", "template values must satisfy controlled preview preflight")
    require(report["public_use_required"] is True, "preview must require public-use controls")
    require(report["preview_auth_available"] is True, "preview auth must be available")
    require(report["production_ready"] is False, "production_ready must remain false")
    require(report["customer_validated"] is False, "customer_validated must remain false")
    require(report["product_launched"] is False, "product_launched must remain false")
    require(report["private_core_exposed"] is False, "private_core_exposed must remain false")
    require(report["payment_provider_configured"] is False, "payment provider must remain false")
    require(report["checkout_enabled"] is False, "checkout must remain false")
    require(report["support_contact_configured"] is True, "support contact must be configured")
    require(report["security_contact_configured"] is True, "security contact must be configured")
    require(report["customer_support_available"] is False, "customer support must remain false")
    require(report["vulnerability_management_available"] is False, "vulnerability management false")
    require(
        report["production_vulnerability_management_ready"] is False,
        "production vulnerability management false",
    )
    require(report["sla_available"] is False, "SLA must remain false")
    require(
        report["controlled_preview_restore_drill_passed"] is True,
        "restore drill evidence must pass after placeholder replacement",
    )
    require(report["production_restore_tested"] is False, "production restore tested must remain false")
    require(
        report["production_restore_policy_available"] is False,
        "production restore policy must remain false",
    )
    require(report["external_ai_assistant_tested"] is False, "external AI assistant tested must remain false")

    combined = "\n".join([doc, gate])
    required_tokens = [
        "controlled_preview_env_template_v0_1: true",
        "template_status: placeholder_only",
        "commercial_preflight_expected_status: pass_after_placeholders_replaced",
        "controlled_preview_possible: true",
        "production_auth_evidence_readiness_v0_1: true",
        "auth_evidence_path_configured_default: false",
        "auth_evidence_production_identity_provider_available_default: false",
        "auth_evidence_oauth_oidc_available_default: false",
        "auth_evidence_rbac_available_default: false",
        "production_privacy_security_legal_evidence_readiness_v0_1: true",
        "privacy_security_legal_evidence_path_configured_default: false",
        "privacy_security_legal_evidence_formal_security_review_completed_default: false",
        "privacy_security_legal_evidence_privacy_legal_review_completed_default: false",
        "privacy_security_legal_evidence_data_processing_agreement_available_default: false",
        "privacy_security_legal_evidence_vulnerability_management_available_default: false",
        "production_billing_revenue_evidence_readiness_v0_1: true",
        "billing_revenue_evidence_path_configured_default: false",
        "pricing_page_evidence_complete_default: false",
        "payment_provider_evidence_complete_default: false",
        "invoice_process_evidence_complete_default: false",
        "tax_review_evidence_complete_default: false",
        "refund_policy_evidence_complete_default: false",
        "tenant_billing_isolation_evidence_complete_default: false",
        "production_tenant_storage_evidence_readiness_v0_1: true",
        "tenant_storage_evidence_path_configured_default: false",
        "tenant_storage_isolation_evidence_complete_default: false",
        "production_tenant_storage_evidence_complete_default: false",
        "production_customer_validation_evidence_readiness_v0_1: true",
        "customer_validation_evidence_path_configured_default: false",
        "customer_validation_evidence_complete_default: false",
        "real_secret_in_template: false",
        "controlled_preview_security_contact_required: true",
        "security_contact_placeholder_only: true",
        "vulnerability_management_available: false",
        "production_vulnerability_management_ready: false",
        "controlled_preview_restore_drill_report_required: true",
        "restore_drill_report_placeholder_only: true",
        "restore_integrity_checks_passed_after_placeholder_replacement: true",
        "production_restore_tested: false",
        "production_restore_policy_available: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_contacted: false",
        "customer_validated: false",
        "product_launched: false",
        "production_ready: false",
        "public_sdk_released: false",
        "external_ai_assistant_tested: false",
        "external_validation_claim: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_production: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing doc/gate tokens: " + ", ".join(missing))

    forbidden_true_tokens = [
        "production_ready: true",
        "customer_validated: true",
        "product_launched: true",
        "payment_provider_configured: true",
        "checkout_enabled: true",
        "production_restore_tested: true",
        "production_restore_policy_available: true",
        "external_validation_claim: true",
        "private_core_exposed: true",
    ]
    found = [token for token in forbidden_true_tokens if token in combined]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms_paths = [
        "/saee_backend/config_examples/controlled_preview.env.example",
        "/phase_b_product/commercial_readiness/CONTROLLED_PREVIEW_ENV_TEMPLATE_V0_1.md",
        "/docs/strategy/SAEE_CONTROLLED_PREVIEW_ENV_TEMPLATE_RECOMMENDATION_GATE.md",
        "/scripts/saee_controlled_preview_env_template_smoke.py",
    ]
    missing_llms = [path for path in required_llms_paths if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("controlled_preview_env_template_v0_1", {})
    expected_index = {
        "status": "placeholder_only_controlled_preview_template",
        "controlled_preview_env_template_v0_1": True,
        "template_status": "placeholder_only",
        "commercial_preflight_expected_status": "pass_after_placeholders_replaced",
        "controlled_preview_possible": True,
        "controlled_preview_support_contact_required": True,
        "controlled_preview_security_contact_required": True,
        "controlled_preview_restore_drill_report_required": True,
        "real_secret_in_template": False,
        "support_contact_placeholder_only": True,
        "security_contact_placeholder_only": True,
        "restore_drill_report_placeholder_only": True,
        "restore_integrity_checks_passed_after_placeholder_replacement": True,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_contacted": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
    }
    for key, expected in expected_index.items():
        require(entry.get(key) == expected, f"agent-index {key} drift")

    print(
        "SAEE_CONTROLLED_PREVIEW_ENV_TEMPLATE_SMOKE: PASS "
        "template_status=placeholder_only "
        "preflight_pass_after_placeholder_replacement=true "
        "production_ready=false "
        "customer_validated=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
