"""Production privacy/security/legal evidence readiness checks.

This module validates a local evidence JSON file for future production privacy,
security, legal, DPA, and vulnerability-management review. It does not perform
legal review, contact legal counsel, contact security vendors, process customer
data, enable vulnerability operations, call external services, change API
schema, modify runtime behavior, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionPrivacySecurityLegalEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionPrivacySecurityLegalEvidenceSeverity = Literal["info", "blocker"]

FORMAL_SECURITY_REVIEW_KEYS = (
    "formal_security_review_report",
    "public_shell_threat_model_reviewed",
    "auth_and_tenant_boundary_reviewed",
    "storage_backup_and_restore_reviewed",
    "dependency_review_completed",
    "private_core_non_exposure_review_completed",
    "review_findings_triaged",
)
PRIVACY_LEGAL_REVIEW_KEYS = (
    "privacy_notice_approved",
    "terms_of_service_approved",
    "data_inventory_reviewed",
    "retention_policy_approved",
    "subprocessor_inventory_reviewed",
    "customer_data_processing_approved",
    "legal_reviewer_recorded",
)
DPA_KEYS = (
    "dpa_terms_approved",
    "controller_processor_roles_defined",
    "subprocessor_terms_approved",
    "breach_notice_terms_approved",
    "deletion_or_return_terms_approved",
    "customer_dpa_template_available",
)
VULNERABILITY_MANAGEMENT_KEYS = (
    "security_contact_configured",
    "coordinated_disclosure_policy_approved",
    "triage_owner_named",
    "severity_model_approved",
    "remediation_targets_approved",
    "vulnerability_case_dry_run_recorded",
    "advisory_publication_policy_approved",
)
FORBIDDEN_TRUE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "customer_contacted",
    "security_vendor_contacted",
    "legal_counsel_contacted",
    "customer_data_processed",
    "customer_data_processing_started",
    "dpa_sent_to_customer",
    "terms_published",
    "privacy_notice_published",
    "production_security_enabled",
    "vulnerability_management_operational",
)


@dataclass(frozen=True)
class ProductionPrivacySecurityLegalEvidenceFinding:
    check_id: str
    severity: ProductionPrivacySecurityLegalEvidenceSeverity
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
    severity: ProductionPrivacySecurityLegalEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionPrivacySecurityLegalEvidenceFinding:
    return ProductionPrivacySecurityLegalEvidenceFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def _all_true(data: dict[str, object], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def _missing_true_keys(data: dict[str, object], keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if data.get(key) is not True]


def _read_evidence(path_value: str) -> tuple[bool, bool, dict[str, object]]:
    if not path_value:
        return False, False, {}
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        return False, False, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, False, {}
    if not isinstance(data, dict):
        return True, False, {}
    return True, True, data


def evaluate_production_privacy_security_legal_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic production privacy/security/legal evidence readiness.

    A `pass` means the local evidence file is internally complete enough for
    human production launch review. It is not legal approval, production
    security certification, customer-data-processing authorization, launch
    approval, customer validation, or production readiness.
    """

    path_configured = bool(settings.production_privacy_security_legal_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_privacy_security_legal_evidence_path
    )
    correct_type = (
        data.get("privacy_security_legal_evidence_type")
        == "production_privacy_security_legal_evidence"
    )
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    formal_security_review_completed = _all_true(data, FORMAL_SECURITY_REVIEW_KEYS)
    privacy_legal_review_completed = _all_true(data, PRIVACY_LEGAL_REVIEW_KEYS)
    data_processing_agreement_available = _all_true(data, DPA_KEYS)
    vulnerability_management_available = _all_true(
        data, VULNERABILITY_MANAGEMENT_KEYS
    )
    production_privacy_security_legal_ready = (
        formal_security_review_completed
        and privacy_legal_review_completed
        and data_processing_agreement_available
        and vulnerability_management_available
        and not forbidden_true
    )

    findings = [
        _finding(
            "privacy_security_legal_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH must point to local privacy/security/legal evidence",
        ),
        _finding(
            "privacy_security_legal_evidence_file_exists",
            "blocker",
            file_exists,
            "privacy/security/legal evidence file must exist locally",
        ),
        _finding(
            "privacy_security_legal_evidence_file_parseable",
            "blocker",
            file_parseable,
            "privacy/security/legal evidence file must be parseable JSON",
        ),
        _finding(
            "privacy_security_legal_evidence_type_valid",
            "blocker",
            correct_type,
            "privacy_security_legal_evidence_type must be production_privacy_security_legal_evidence",
        ),
        _finding(
            "formal_security_review_evidence_complete",
            "blocker",
            formal_security_review_completed,
            "formal security review evidence must be complete",
        ),
        _finding(
            "privacy_legal_review_evidence_complete",
            "blocker",
            privacy_legal_review_completed,
            "privacy legal review evidence must be complete",
        ),
        _finding(
            "data_processing_agreement_evidence_complete",
            "blocker",
            data_processing_agreement_available,
            "DPA evidence must be complete",
        ),
        _finding(
            "vulnerability_management_evidence_complete",
            "blocker",
            vulnerability_management_available,
            "vulnerability management evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "privacy/security/legal evidence must not claim production launch, customer validation, customer contact, customer data processing, legal/vendor contact, production security enablement, private-core exposure, or code modification",
        ),
        _finding(
            "no_external_actions",
            "info",
            True,
            "readiness check only reads a local evidence file and performs no external action",
        ),
    ]

    blocking_failures = [
        finding
        for finding in findings
        if finding.severity == "blocker" and not finding.passed
    ]
    if forbidden_true:
        status: ProductionPrivacySecurityLegalEvidenceStatus = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence_readiness",
        "production_privacy_security_legal_evidence_readiness_v0_1": True,
        "status": status,
        "privacy_security_legal_evidence_path_configured": path_configured,
        "privacy_security_legal_evidence_file_exists": file_exists,
        "privacy_security_legal_evidence_file_parseable": file_parseable,
        "privacy_security_legal_evidence_type_valid": correct_type,
        "formal_security_review_completed": formal_security_review_completed,
        "privacy_legal_review_completed": privacy_legal_review_completed,
        "data_processing_agreement_available": data_processing_agreement_available,
        "vulnerability_management_available": vulnerability_management_available,
        "production_privacy_security_legal_ready": production_privacy_security_legal_ready,
        "formal_security_review_missing_evidence": _missing_true_keys(
            data, FORMAL_SECURITY_REVIEW_KEYS
        ),
        "privacy_legal_review_missing_evidence": _missing_true_keys(
            data, PRIVACY_LEGAL_REVIEW_KEYS
        ),
        "data_processing_agreement_missing_evidence": _missing_true_keys(
            data, DPA_KEYS
        ),
        "vulnerability_management_missing_evidence": _missing_true_keys(
            data, VULNERABILITY_MANAGEMENT_KEYS
        ),
        "boundary_violation_count": len(forbidden_true),
        "boundary_violations": forbidden_true,
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
        "production_security_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "legal_approval_completed": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after all other production blockers are resolved"
        if status == "pass"
        else "complete formal security, privacy legal, DPA, and vulnerability management evidence before launch review",
    }
