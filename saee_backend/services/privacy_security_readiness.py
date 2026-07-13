"""Privacy and security review readiness for the SAEE public API shell.

This module records whether privacy and security review materials are ready
for controlled-preview review. It does not perform a legal review, certify
security controls, configure production security operations, contact external
services, inspect request bodies, or expose private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


PrivacySecurityReadinessStatus = Literal["pass", "hold", "stop"]
PrivacySecurityFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class PrivacySecurityReadinessFinding:
    check_id: str
    severity: PrivacySecurityFindingSeverity
    passed: bool
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "passed": self.passed,
            "message": self.message,
        }


def _finding(
    check_id: str,
    severity: PrivacySecurityFindingSeverity,
    passed: bool,
    message: str,
) -> PrivacySecurityReadinessFinding:
    return PrivacySecurityReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_privacy_security_readiness(
    settings: SaeeBackendSettings = SETTINGS,
) -> dict[str, object]:
    """Return deterministic privacy/security readiness for local preview use."""

    public_use = public_use_required(settings)
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires explicit privacy and security review"
            if public_use
            else "local environment detected; privacy/security readiness is advisory",
        ),
        _finding(
            "data_classification_available",
            "info",
            True,
            "public-shell data classes are documented for review",
        ),
        _finding(
            "pii_policy_draft_available",
            "info",
            True,
            "draft policy states that personal data should not be submitted to the local MVP",
        ),
        _finding(
            "secret_handling_guidance_available",
            "info",
            True,
            "secret-handling guidance keeps credentials out of request payloads and logs",
        ),
        _finding(
            "third_party_processor_inventory_available",
            "info",
            True,
            "current public shell records no external model API or assistant calls",
        ),
        _finding(
            "vulnerability_disclosure_policy_draft_available",
            "info",
            True,
            "draft vulnerability disclosure policy and triage guidance are available",
        ),
        _finding(
            "security_contact_configured",
            "blocker" if public_use else "info",
            bool(settings.security_contact) if public_use else True,
            "non-local controlled preview must configure SAEE_SECURITY_CONTACT"
            if public_use
            else "local demo mode does not require a security contact",
        ),
        _finding(
            "formal_security_review_missing",
            "blocker",
            False,
            "no formal security review, penetration test, or vulnerability management process is complete",
        ),
        _finding(
            "privacy_legal_review_missing",
            "blocker",
            False,
            "no legal privacy review, DPA, data processing terms, or customer data approval exists",
        ),
        _finding(
            "production_security_controls_missing",
            "blocker",
            False,
            "SOC 2, ISO 27001, production secrets management, SIEM, and compliance logging are not available",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false",
        ),
        _finding(
            "private_core_non_exposure",
            "blocker",
            settings.private_core_exposed is False,
            "private_core_exposed must remain false",
        ),
    ]

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    status: PrivacySecurityReadinessStatus = "hold" if blockers else "pass"

    return {
        "privacy_security_readiness_type": "controlled_preview_privacy_security_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "privacy_security_review_v0_1": True,
        "privacy_security_review_status": status,
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
        "vulnerability_management_readiness_v0_1": True,
        "vulnerability_management_readiness_status": "hold",
        "vulnerability_disclosure_policy_draft_available": True,
        "security_contact_configured": bool(settings.security_contact),
        "vulnerability_intake_contact_configured": bool(settings.security_contact),
        "controlled_preview_security_contact_required": public_use,
        "vulnerability_triage_runbook_available": True,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "formal_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_available": False,
        "security_certification_available": False,
        "soc2_available": False,
        "iso27001_available": False,
        "penetration_test_completed": False,
        "vulnerability_remediation_sla_available": False,
        "coordinated_disclosure_available": False,
        "vulnerability_management_available": False,
        "production_vulnerability_management_ready": False,
        "compliance_logging_available": False,
        "production_security_ready": False,
        "customer_data_processing_ready": False,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "product_launched": settings.product_launched,
        "public_sdk_released": settings.public_sdk_released,
        "private_core_exposed": settings.private_core_exposed,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": "complete formal privacy/legal review, security review, vulnerability process, and customer data terms before production use",
    }
