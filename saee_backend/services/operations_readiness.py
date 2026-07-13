"""Operations readiness checks for the SAEE MVP API shell.

This module evaluates production-operations readiness for the public shell
only. It does not start monitoring, contact external services, configure
alerting providers, modify runtime behavior, or inspect private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


OperationsReadinessStatus = Literal["pass", "hold", "stop"]
OperationsFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class OperationsReadinessFinding:
    check_id: str
    severity: OperationsFindingSeverity
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
    severity: OperationsFindingSeverity,
    passed: bool,
    message: str,
) -> OperationsReadinessFinding:
    return OperationsReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_operations_readiness(settings: SaeeBackendSettings) -> dict[str, object]:
    """Return deterministic operations readiness for local/pre-commercial use."""

    public_use = public_use_required(settings)
    support_contact_configured = bool(settings.support_contact)
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires production operations review"
            if public_use
            else "local environment detected; operations readiness is advisory",
        ),
        _finding(
            "request_metadata_audit_available",
            "info",
            True,
            "optional request metadata audit exists but is not production monitoring",
        ),
        _finding(
            "local_operations_telemetry_available",
            "info",
            True,
            "local request-audit telemetry snapshot is available but is not production monitoring",
        ),
        _finding(
            "incident_response_runbook_available",
            "info",
            True,
            "manual incident response runbook exists but is not on-call, SLA, or production support",
        ),
        _finding(
            "local_alert_policy_available",
            "info",
            True,
            "local alert-candidate policy exists but is not external alert delivery or production alerting",
        ),
        _finding(
            "support_runbook_available",
            "info",
            True,
            "controlled-preview support runbook exists but is not customer support, SLA, or on-call",
        ),
        _finding(
            "privacy_security_review_available",
            "info",
            True,
            "controlled-preview privacy/security review draft exists but is not formal certification",
        ),
        _finding(
            "production_monitoring_missing",
            "blocker",
            False,
            "production monitoring, metrics, dashboards, external alert delivery, and alerting are not configured",
        ),
        _finding(
            "incident_response_operations_missing",
            "blocker",
            False,
            "incident response execution, escalation, and on-call rotation are not configured",
        ),
        _finding(
            "sla_support_missing",
            "blocker",
            False,
            "customer-facing support channel, contractual SLA, and operational commitments are not configured",
        ),
        _finding(
            "private_core_non_exposure",
            "blocker",
            settings.private_core_exposed is False,
            "private_core_exposed must remain false",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false",
        ),
    ]

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    status: OperationsReadinessStatus = "hold" if blockers else "pass"

    return {
        "operations_readiness_type": "public_shell_operations_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "operations_readiness_available": True,
        "operations_readiness_status": status,
        "request_metadata_audit_available": True,
        "local_operations_telemetry_available": True,
        "operations_telemetry_external_export_available": False,
        "local_alert_policy_available": True,
        "external_alert_delivery_available": False,
        "production_monitoring_available": False,
        "alerting_available": False,
        "incident_response_runbook_available": True,
        "privacy_security_review_v0_1": True,
        "privacy_security_review_status": "hold",
        "data_classification_available": True,
        "public_shell_data_map_available": True,
        "pii_policy_draft_available": True,
        "personal_data_allowed": False,
        "secret_handling_guidance_available": True,
        "third_party_processor_inventory_available": True,
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
        "support_readiness_v0_1": True,
        "support_runbook_available": True,
        "support_case_template_available": True,
        "support_sla_draft_available": True,
        "support_response_targets_documented": True,
        "support_contact_configured": support_contact_configured,
        "customer_support_available": False,
        "production_support_available": False,
        "on_call_rotation_available": False,
        "sla_available": False,
        "support_process_available": False,
        "production_operations_ready": False,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "product_launched": settings.product_launched,
        "public_sdk_released": settings.public_sdk_released,
        "private_core_exposed": settings.private_core_exposed,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": "implement production monitoring, alerting, on-call rotation, SLA, and support process before production use",
    }
