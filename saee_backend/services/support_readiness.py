"""Controlled-preview support readiness for the SAEE public API shell.

This module records whether support documentation is ready for a controlled
preview. It does not create a customer support desk, configure a ticketing
system, start an on-call rotation, create an SLA, contact customers, call
external services, or inspect private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


SupportReadinessStatus = Literal["pass", "hold", "stop"]
SupportFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class SupportReadinessFinding:
    check_id: str
    severity: SupportFindingSeverity
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
    severity: SupportFindingSeverity,
    passed: bool,
    message: str,
) -> SupportReadinessFinding:
    return SupportReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_support_readiness(settings: SaeeBackendSettings = SETTINGS) -> dict[str, object]:
    """Return deterministic support readiness for local/controlled-preview use."""

    public_use = public_use_required(settings)
    support_contact_configured = bool(settings.support_contact)
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires explicit support review"
            if public_use
            else "local environment detected; support readiness is advisory",
        ),
        _finding(
            "support_runbook_available",
            "info",
            True,
            "controlled-preview support runbook is documented for human operators",
        ),
        _finding(
            "support_case_template_available",
            "info",
            True,
            "support case fields are documented for manual issue intake",
        ),
        _finding(
            "support_sla_draft_available",
            "info",
            True,
            "non-contractual response targets are documented as a draft only",
        ),
        _finding(
            "support_contact_missing",
            "blocker",
            support_contact_configured,
            "controlled-preview support contact is configured"
            if support_contact_configured
            else "no controlled-preview support mailbox, ticketing queue, or staffed channel is configured",
        ),
        _finding(
            "production_sla_missing",
            "blocker",
            False,
            "no contractual SLA, on-call rotation, escalation schedule, or customer support commitment exists",
        ),
        _finding(
            "customer_validation_non_claim",
            "blocker",
            settings.customer_validated is False,
            "customer_validated must remain false until real customer validation is recorded",
        ),
        _finding(
            "production_non_claim",
            "blocker",
            settings.production_ready is False,
            "production_ready must remain false",
        ),
    ]

    blockers = [finding for finding in findings if finding.severity == "blocker" and not finding.passed]
    status: SupportReadinessStatus = "hold" if blockers else "pass"

    return {
        "support_readiness_type": "controlled_preview_support_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "support_readiness_v0_1": True,
        "support_runbook_available": True,
        "support_case_template_available": True,
        "support_sla_draft_available": True,
        "support_response_targets_documented": True,
        "support_contact_configured": support_contact_configured,
        "customer_support_available": False,
        "production_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "production_operations_ready": False,
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
        "next_action": "configure a staffed support channel, escalation ownership, on-call rotation, and contractual SLA before production use",
    }
