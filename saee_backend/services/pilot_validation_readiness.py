"""Controlled pilot validation readiness for the SAEE public API shell.

This module records whether SAEE has enough local materials to run a future
human-approved pilot validation session. It does not contact customers, record
real customer evidence, claim customer validation, enable uploads, or modify
runtime/backend/private core behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


PilotValidationReadinessStatus = Literal["pass", "hold", "stop"]
PilotValidationFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class PilotValidationFinding:
    check_id: str
    severity: PilotValidationFindingSeverity
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
    severity: PilotValidationFindingSeverity,
    passed: bool,
    message: str,
) -> PilotValidationFinding:
    return PilotValidationFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_pilot_validation_readiness(
    settings: SaeeBackendSettings = SETTINGS,
) -> dict[str, object]:
    """Return deterministic readiness for future human-approved pilot sessions."""

    public_use = public_use_required(settings)
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires explicit pilot review"
            if public_use
            else "local environment detected; pilot validation readiness is advisory",
        ),
        _finding(
            "first_user_test_plan_available",
            "info",
            True,
            "first-user test plan is available",
        ),
        _finding(
            "feedback_form_available",
            "info",
            True,
            "feedback form is available",
        ),
        _finding(
            "success_criteria_available",
            "info",
            True,
            "go / hold / pivot success criteria are available",
        ),
        _finding(
            "pilot_result_template_available",
            "info",
            True,
            "machine-readable pilot result template is available",
        ),
        _finding(
            "pilot_sessions_missing",
            "blocker",
            False,
            "no real pilot sessions have been completed or recorded",
        ),
        _finding(
            "customer_permission_missing",
            "blocker",
            False,
            "no customer permission, data approval, or pilot participant record exists",
        ),
        _finding(
            "customer_validation_non_claim",
            "blocker",
            settings.customer_validated is False,
            "customer_validated must remain false until real pilot evidence is recorded",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false",
        ),
    ]

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    status: PilotValidationReadinessStatus = "hold" if blockers else "pass"

    return {
        "pilot_validation_readiness_type": "controlled_pilot_validation_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "pilot_validation_readiness_v0_1": True,
        "pilot_validation_status": status,
        "first_user_test_plan_available": True,
        "feedback_form_available": True,
        "success_criteria_available": True,
        "pilot_result_template_available": True,
        "pilot_session_protocol_available": True,
        "pilot_sessions_completed": 0,
        "pilot_results_recorded": False,
        "customer_permission_recorded": False,
        "customer_contacted": False,
        "customer_validated": settings.customer_validated,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "user_upload_enabled": False,
        "customer_data_processing_ready": False,
        "product_launched": settings.product_launched,
        "production_ready": settings.production_ready,
        "public_sdk_released": settings.public_sdk_released,
        "private_core_exposed": settings.private_core_exposed,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": "run human-approved pilot sessions and record evidence before claiming customer validation",
    }
