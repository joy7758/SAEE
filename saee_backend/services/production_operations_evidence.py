"""Production operations evidence readiness checks.

This module validates a local evidence JSON file for future production
operations review. It does not deploy monitoring, send alerts, contact
vendors, contact customers, call external services, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionOperationsEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionOperationsEvidenceSeverity = Literal["info", "blocker"]

PRODUCTION_MONITORING_KEYS = (
    "production_monitoring_plan_approved",
    "metrics_coverage_approved",
    "slo_dashboard_defined",
    "log_retention_reviewed",
    "monitoring_dry_run_recorded",
)
EXTERNAL_ALERT_DELIVERY_KEYS = (
    "external_alert_channel_configured",
    "alert_routing_policy_approved",
    "alert_delivery_test_recorded",
    "alert_failure_handling_defined",
    "incident_escalation_path_defined",
    "alert_acknowledgement_process_defined",
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
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "customer_contacted",
    "alert_provider_contacted",
    "monitoring_vendor_contacted",
    "production_monitoring_deployed",
    "external_alert_delivery_enabled",
)


@dataclass(frozen=True)
class ProductionOperationsEvidenceFinding:
    check_id: str
    severity: ProductionOperationsEvidenceSeverity
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
    severity: ProductionOperationsEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionOperationsEvidenceFinding:
    return ProductionOperationsEvidenceFinding(
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


def evaluate_production_operations_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic production-operations evidence readiness.

    A `pass` means the local evidence file is internally complete enough for
    human production launch review. It is not a monitoring deployment, alert
    provider integration, on-call activation, launch approval, or production
    readiness claim.
    """

    path_configured = bool(settings.production_operations_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_operations_evidence_path
    )
    correct_type = data.get("operations_evidence_type") == "production_operations_evidence"
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    production_monitoring_available = _all_true(data, PRODUCTION_MONITORING_KEYS)
    external_alert_delivery_available = _all_true(data, EXTERNAL_ALERT_DELIVERY_KEYS)
    on_call_rotation_available = _all_true(data, ON_CALL_KEYS)
    production_operations_ready = (
        production_monitoring_available
        and external_alert_delivery_available
        and on_call_rotation_available
        and not forbidden_true
    )

    findings = [
        _finding(
            "operations_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH must point to local operations evidence",
        ),
        _finding(
            "operations_evidence_file_exists",
            "blocker",
            file_exists,
            "operations evidence file must exist locally",
        ),
        _finding(
            "operations_evidence_file_parseable",
            "blocker",
            file_parseable,
            "operations evidence file must be parseable JSON",
        ),
        _finding(
            "operations_evidence_type_valid",
            "blocker",
            correct_type,
            "operations_evidence_type must be production_operations_evidence",
        ),
        _finding(
            "production_monitoring_evidence_complete",
            "blocker",
            production_monitoring_available,
            "production monitoring evidence must be complete",
        ),
        _finding(
            "external_alert_delivery_evidence_complete",
            "blocker",
            external_alert_delivery_available,
            "external alert delivery evidence must be complete",
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
            "operations evidence must not claim production launch, customer validation, external calls, private-core exposure, vendor contact, or code modification",
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
    status: ProductionOperationsEvidenceStatus
    if forbidden_true:
        status = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_operations_evidence_type": "production_operations_evidence_readiness",
        "production_operations_evidence_readiness_v0_1": True,
        "status": status,
        "operations_evidence_path_configured": path_configured,
        "operations_evidence_file_exists": file_exists,
        "operations_evidence_file_parseable": file_parseable,
        "operations_evidence_type_valid": correct_type,
        "production_monitoring_available": production_monitoring_available,
        "external_alert_delivery_available": external_alert_delivery_available,
        "on_call_rotation_available": on_call_rotation_available,
        "production_operations_ready": production_operations_ready,
        "production_monitoring_missing_evidence": _missing_true_keys(
            data, PRODUCTION_MONITORING_KEYS
        ),
        "external_alert_delivery_missing_evidence": _missing_true_keys(
            data, EXTERNAL_ALERT_DELIVERY_KEYS
        ),
        "on_call_missing_evidence": _missing_true_keys(data, ON_CALL_KEYS),
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
        "customer_contacted": False,
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "production_monitoring_deployed": False,
        "external_alert_delivery_enabled": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after all other production blockers are resolved"
        if status == "pass"
        else "complete production monitoring, external alert delivery, and on-call evidence before launch review",
    }
