"""Production data-operations evidence readiness checks.

This module validates a local evidence JSON file for future production restore
review. It does not run restore, change live data paths, contact customers,
call external services, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionDataOperationsEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionDataOperationsEvidenceSeverity = Literal["info", "blocker"]

RESTORE_TEST_KEYS = (
    "production_like_restore_test_plan_approved",
    "isolated_restore_environment_used",
    "restore_integrity_checks_passed",
    "rto_rpo_observed_and_recorded",
    "tenant_scope_validated_if_customer_data_exists",
    "restore_test_report_reviewed",
)
RESTORE_POLICY_KEYS = (
    "production_restore_policy_approved",
    "backup_retention_policy_approved",
    "tenant_restore_boundary_approved",
    "credential_secret_exclusion_reviewed",
    "customer_notification_boundary_approved",
    "incident_response_handoff_approved",
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
    "production_data_path_modified",
    "restore_to_live_path_enabled",
    "live_restore_performed",
    "credentials_restored",
    "private_core_restored",
)


@dataclass(frozen=True)
class ProductionDataOperationsEvidenceFinding:
    check_id: str
    severity: ProductionDataOperationsEvidenceSeverity
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
    severity: ProductionDataOperationsEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionDataOperationsEvidenceFinding:
    return ProductionDataOperationsEvidenceFinding(
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


def evaluate_production_data_operations_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic restore-policy evidence readiness.

    A `pass` means the local evidence file is internally complete enough for
    human production launch review. It is not a production restore execution,
    launch approval, or customer-data processing approval.
    """

    path_configured = bool(settings.production_data_operations_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_data_operations_evidence_path
    )
    correct_type = data.get("data_operations_evidence_type") == (
        "production_data_operations_evidence"
    )
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    restore_tested = _all_true(data, RESTORE_TEST_KEYS)
    production_restore_policy_available = _all_true(data, RESTORE_POLICY_KEYS)
    production_restore_tested = restore_tested
    production_restore_policy_approved = production_restore_policy_available
    production_data_operations_ready = (
        restore_tested
        and production_restore_policy_available
        and not forbidden_true
    )

    findings = [
        _finding(
            "data_operations_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH must point to local data-operations evidence",
        ),
        _finding(
            "data_operations_evidence_file_exists",
            "blocker",
            file_exists,
            "data-operations evidence file must exist locally",
        ),
        _finding(
            "data_operations_evidence_file_parseable",
            "blocker",
            file_parseable,
            "data-operations evidence file must be parseable JSON",
        ),
        _finding(
            "data_operations_evidence_type_valid",
            "blocker",
            correct_type,
            "data_operations_evidence_type must be production_data_operations_evidence",
        ),
        _finding(
            "restore_test_evidence_complete",
            "blocker",
            restore_tested,
            "production-like restore test evidence must be complete",
        ),
        _finding(
            "production_restore_policy_evidence_complete",
            "blocker",
            production_restore_policy_available,
            "production restore policy evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "data-operations evidence must not claim production launch, customer validation, live restore, private-core exposure, or code modification",
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
    status: ProductionDataOperationsEvidenceStatus
    if forbidden_true:
        status = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_data_operations_evidence_type": "production_data_operations_evidence_readiness",
        "production_data_operations_evidence_readiness_v0_1": True,
        "status": status,
        "data_operations_evidence_path_configured": path_configured,
        "data_operations_evidence_file_exists": file_exists,
        "data_operations_evidence_file_parseable": file_parseable,
        "data_operations_evidence_type_valid": correct_type,
        "restore_tested": restore_tested,
        "production_restore_tested": production_restore_tested,
        "restore_test_evidence_complete": restore_tested,
        "production_restore_policy_available": production_restore_policy_available,
        "production_restore_policy_approved": production_restore_policy_approved,
        "production_restore_policy_evidence_complete": production_restore_policy_available,
        "production_data_operations_ready": production_data_operations_ready,
        "restore_test_missing_evidence": _missing_true_keys(data, RESTORE_TEST_KEYS),
        "restore_policy_missing_evidence": _missing_true_keys(data, RESTORE_POLICY_KEYS),
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
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after all other production blockers are resolved"
        if status == "pass"
        else "complete production-like restore test and production restore policy evidence before launch review",
    }
