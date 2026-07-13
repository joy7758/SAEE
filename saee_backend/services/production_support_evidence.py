"""Production support/SLA evidence readiness checks.

This module validates a local evidence JSON file for future production support
review. It does not create a support desk, contact customers, contact support
vendors, send notices, start an on-call rotation, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionSupportEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionSupportEvidenceSeverity = Literal["info", "blocker"]

SUPPORT_CONTACT_KEYS = (
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
)
CUSTOMER_SUPPORT_KEYS = (
    "staffed_support_process_defined",
    "case_triage_workflow_defined",
    "support_case_audit_trail_available",
    "handoff_to_engineering_defined",
    "customer_communication_template_approved",
    "support_process_dry_run_recorded",
)
SLA_KEYS = (
    "human_approved_sla_terms",
    "severity_definitions_approved",
    "support_hours_approved",
    "response_targets_approved",
    "exclusions_approved",
    "legal_review_completed",
)
ON_CALL_KEYS = (
    "on_call_rotation_defined",
    "escalation_schedule_defined",
    "incident_commander_named",
)
FORBIDDEN_TRUE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "customer_contacted",
    "support_vendor_contacted",
)


@dataclass(frozen=True)
class ProductionSupportEvidenceFinding:
    check_id: str
    severity: ProductionSupportEvidenceSeverity
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
    severity: ProductionSupportEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionSupportEvidenceFinding:
    return ProductionSupportEvidenceFinding(
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


def evaluate_production_support_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic support/SLA evidence readiness.

    A `pass` here means the local evidence file is present and internally
    complete enough for production launch review. It is not a launch approval
    and does not contact or create any support channel.
    """

    path_configured = bool(settings.production_support_evidence_path)
    file_exists, file_parseable, data = _read_evidence(settings.production_support_evidence_path)
    correct_type = data.get("support_evidence_type") == "production_support_sla_evidence"
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    support_contact_available = bool(settings.support_contact) and _all_true(
        data, SUPPORT_CONTACT_KEYS
    )
    customer_support_available = _all_true(data, CUSTOMER_SUPPORT_KEYS)
    sla_available = _all_true(data, SLA_KEYS)
    on_call_rotation_available = _all_true(data, ON_CALL_KEYS)
    production_support_available = (
        support_contact_available
        and customer_support_available
        and sla_available
        and on_call_rotation_available
        and not forbidden_true
    )

    findings = [
        _finding(
            "support_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH must point to local support evidence",
        ),
        _finding(
            "support_evidence_file_exists",
            "blocker",
            file_exists,
            "support evidence file must exist locally",
        ),
        _finding(
            "support_evidence_file_parseable",
            "blocker",
            file_parseable,
            "support evidence file must be parseable JSON",
        ),
        _finding(
            "support_evidence_type_valid",
            "blocker",
            correct_type,
            "support_evidence_type must be production_support_sla_evidence",
        ),
        _finding(
            "support_contact_evidence_complete",
            "blocker",
            support_contact_available,
            "support contact evidence must be complete and SAEE_SUPPORT_CONTACT must be configured",
        ),
        _finding(
            "customer_support_evidence_complete",
            "blocker",
            customer_support_available,
            "customer support process evidence must be complete",
        ),
        _finding(
            "sla_evidence_complete",
            "blocker",
            sla_available,
            "SLA approval evidence must be complete",
        ),
        _finding(
            "on_call_rotation_evidence_complete",
            "blocker",
            on_call_rotation_available,
            "on-call rotation and escalation evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "support evidence must not claim production launch, customer validation, external calls, private-core exposure, or code modification",
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
    status: ProductionSupportEvidenceStatus
    if forbidden_true:
        status = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_support_evidence_type": "production_support_sla_evidence_readiness",
        "production_support_evidence_readiness_v0_1": True,
        "status": status,
        "support_evidence_path_configured": path_configured,
        "support_evidence_file_exists": file_exists,
        "support_evidence_file_parseable": file_parseable,
        "support_evidence_type_valid": correct_type,
        "support_contact_available": support_contact_available,
        "customer_support_available": customer_support_available,
        "production_support_available": production_support_available,
        "support_process_available": customer_support_available,
        "sla_available": sla_available,
        "on_call_rotation_available": on_call_rotation_available,
        "support_contact_missing_evidence": _missing_true_keys(data, SUPPORT_CONTACT_KEYS),
        "customer_support_missing_evidence": _missing_true_keys(data, CUSTOMER_SUPPORT_KEYS),
        "sla_missing_evidence": _missing_true_keys(data, SLA_KEYS),
        "on_call_missing_evidence": _missing_true_keys(data, ON_CALL_KEYS),
        "boundary_violation_count": len(forbidden_true),
        "boundary_violations": forbidden_true,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human review may use this evidence for launch gating only after all other production blockers are resolved"
        if status == "pass"
        else "complete support contact, staffed support, SLA, and on-call evidence before launch review",
    }
