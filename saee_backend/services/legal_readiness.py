"""Legal and DPA readiness for the SAEE public API shell.

This module records whether legal review materials are ready for human review.
It does not perform legal review, approve terms, publish policies, contact
customers, enable customer data processing, or expose private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


LegalReadinessStatus = Literal["pass", "hold", "stop"]
LegalReadinessFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class LegalReadinessFinding:
    check_id: str
    severity: LegalReadinessFindingSeverity
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
    severity: LegalReadinessFindingSeverity,
    passed: bool,
    message: str,
) -> LegalReadinessFinding:
    return LegalReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_legal_readiness(settings: SaeeBackendSettings = SETTINGS) -> dict[str, object]:
    """Return deterministic legal/DPA readiness for controlled-preview review."""

    public_use = public_use_required(settings)
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires explicit legal approval before customer data use"
            if public_use
            else "local environment detected; legal readiness is advisory",
        ),
        _finding(
            "terms_of_service_draft_available",
            "info",
            True,
            "draft terms-of-service review packet is available for human/legal review",
        ),
        _finding(
            "privacy_notice_draft_available",
            "info",
            True,
            "draft privacy notice review packet is available for human/legal review",
        ),
        _finding(
            "dpa_review_packet_available",
            "info",
            True,
            "DPA review checklist is available, but no customer DPA is approved",
        ),
        _finding(
            "customer_data_use_not_approved",
            "blocker",
            False,
            "customer data processing is not approved by legal review",
        ),
        _finding(
            "legal_review_missing",
            "blocker",
            False,
            "privacy legal review and terms approval are not complete",
        ),
        _finding(
            "dpa_not_available",
            "blocker",
            False,
            "data processing agreement is not approved or available for customers",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false",
        ),
        _finding(
            "customer_validation_non_claim",
            "blocker",
            settings.customer_validated is False,
            "customer_validated must remain false until real customer validation is recorded",
        ),
        _finding(
            "private_core_non_exposure",
            "blocker",
            settings.private_core_exposed is False,
            "private_core_exposed must remain false",
        ),
    ]

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    status: LegalReadinessStatus = "hold" if blockers else "pass"

    return {
        "legal_readiness_type": "controlled_preview_legal_dpa_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "legal_readiness_v0_1": True,
        "legal_readiness_status": status,
        "terms_of_service_draft_available": True,
        "terms_of_service_published": False,
        "terms_legal_review_completed": False,
        "privacy_notice_draft_available": True,
        "privacy_notice_published": False,
        "privacy_legal_review_completed": False,
        "dpa_review_packet_available": True,
        "data_processing_agreement_draft_available": True,
        "data_processing_agreement_available": False,
        "customer_data_processing_ready": False,
        "customer_contract_template_available": False,
        "legal_approval_completed": False,
        "production_legal_ready": False,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "customer_contacted": False,
        "product_launched": settings.product_launched,
        "public_sdk_released": settings.public_sdk_released,
        "private_core_exposed": settings.private_core_exposed,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": "complete human legal review for terms, privacy notice, DPA, and customer data processing before production or paid customer use",
    }
