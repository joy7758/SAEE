"""Production tenant storage evidence readiness checks.

This module validates a local evidence JSON file for future production tenant
storage isolation review. It does not implement production multi-tenancy,
change storage behavior, migrate data, contact customers, process customer
data, change API schema, modify runtime behavior, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionTenantStorageEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionTenantStorageEvidenceSeverity = Literal["info", "blocker"]

TENANT_STORAGE_MODEL_KEYS = (
    "production_tenant_data_model_approved",
    "tenant_scoped_primary_keys_or_partitions_reviewed",
    "tenant_query_enforcement_design_reviewed",
    "tenant_storage_migration_plan_reviewed",
)
TENANT_ISOLATION_TEST_KEYS = (
    "same_experiment_id_cross_tenant_partition_tests_passed",
    "cross_tenant_read_denial_tests_passed",
    "cross_tenant_write_denial_tests_passed",
    "tenant_scoped_listing_tests_passed",
    "tenant_scoped_report_endpoint_tests_passed",
)
TENANT_OPERATIONS_KEYS = (
    "tenant_scoped_audit_metadata_reviewed",
    "tenant_backup_restore_boundary_approved",
    "tenant_deletion_retention_boundary_approved",
    "tenant_storage_observability_plan_reviewed",
)
TENANT_SECURITY_PRIVACY_KEYS = (
    "tenant_authorization_policy_reviewed",
    "tenant_secret_boundary_reviewed",
    "security_review_completed",
    "privacy_legal_review_completed",
    "customer_data_processing_non_claim_reviewed",
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
    "customer_data_processed",
    "customer_data_processing_started",
    "production_database_modified",
    "storage_behavior_modified",
    "migration_executed",
    "live_customer_data_migrated",
    "tenant_storage_isolated",
    "production_tenant_storage_isolated",
    "multi_tenant_production_ready",
    "tenant_authorization_enabled",
    "production_tenant_storage_enabled",
    "cross_tenant_access_tests_claimed_as_external_validation",
)


@dataclass(frozen=True)
class ProductionTenantStorageEvidenceFinding:
    check_id: str
    severity: ProductionTenantStorageEvidenceSeverity
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
    severity: ProductionTenantStorageEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionTenantStorageEvidenceFinding:
    return ProductionTenantStorageEvidenceFinding(
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


def evaluate_production_tenant_storage_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic production tenant storage evidence readiness.

    A `pass` means the local evidence file is internally complete enough for
    human production launch review of the `tenant_storage_isolation` blocker.
    It is not production multi-tenancy, storage behavior modification,
    customer-data processing approval, or production-readiness approval.
    """

    path_configured = bool(settings.production_tenant_storage_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_tenant_storage_evidence_path
    )
    correct_type = (
        data.get("tenant_storage_evidence_type")
        == "production_tenant_storage_evidence"
    )
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    tenant_storage_model_evidence_complete = _all_true(
        data, TENANT_STORAGE_MODEL_KEYS
    )
    tenant_isolation_test_evidence_complete = _all_true(
        data, TENANT_ISOLATION_TEST_KEYS
    )
    tenant_operations_evidence_complete = _all_true(data, TENANT_OPERATIONS_KEYS)
    tenant_security_privacy_evidence_complete = _all_true(
        data, TENANT_SECURITY_PRIVACY_KEYS
    )
    production_tenant_storage_evidence_complete = (
        tenant_storage_model_evidence_complete
        and tenant_isolation_test_evidence_complete
        and tenant_operations_evidence_complete
        and tenant_security_privacy_evidence_complete
        and not forbidden_true
    )

    findings = [
        _finding(
            "tenant_storage_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH must point to local tenant storage evidence",
        ),
        _finding(
            "tenant_storage_evidence_file_exists",
            "blocker",
            file_exists,
            "tenant storage evidence file must exist locally",
        ),
        _finding(
            "tenant_storage_evidence_file_parseable",
            "blocker",
            file_parseable,
            "tenant storage evidence file must be parseable JSON",
        ),
        _finding(
            "tenant_storage_evidence_type_valid",
            "blocker",
            correct_type,
            "tenant_storage_evidence_type must be production_tenant_storage_evidence",
        ),
        _finding(
            "tenant_storage_model_evidence_complete",
            "blocker",
            tenant_storage_model_evidence_complete,
            "tenant storage model evidence must be complete",
        ),
        _finding(
            "tenant_isolation_test_evidence_complete",
            "blocker",
            tenant_isolation_test_evidence_complete,
            "tenant isolation denial-test evidence must be complete",
        ),
        _finding(
            "tenant_operations_evidence_complete",
            "blocker",
            tenant_operations_evidence_complete,
            "tenant operations boundary evidence must be complete",
        ),
        _finding(
            "tenant_security_privacy_evidence_complete",
            "blocker",
            tenant_security_privacy_evidence_complete,
            "tenant security/privacy evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "tenant storage evidence must not claim production readiness, customer validation, customer-data processing, production multi-tenancy, storage modification, private-core exposure, or code modification",
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
        status: ProductionTenantStorageEvidenceStatus = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_tenant_storage_evidence_type": "production_tenant_storage_evidence_readiness",
        "production_tenant_storage_evidence_readiness_v0_1": True,
        "status": status,
        "tenant_storage_evidence_path_configured": path_configured,
        "tenant_storage_evidence_file_exists": file_exists,
        "tenant_storage_evidence_file_parseable": file_parseable,
        "tenant_storage_evidence_type_valid": correct_type,
        "tenant_storage_model_evidence_complete": tenant_storage_model_evidence_complete,
        "tenant_isolation_test_evidence_complete": tenant_isolation_test_evidence_complete,
        "tenant_operations_evidence_complete": tenant_operations_evidence_complete,
        "tenant_security_privacy_evidence_complete": tenant_security_privacy_evidence_complete,
        "tenant_storage_isolation_evidence_complete": production_tenant_storage_evidence_complete,
        "production_tenant_storage_evidence_complete": production_tenant_storage_evidence_complete,
        "tenant_storage_model_missing_evidence": _missing_true_keys(
            data, TENANT_STORAGE_MODEL_KEYS
        ),
        "tenant_isolation_test_missing_evidence": _missing_true_keys(
            data, TENANT_ISOLATION_TEST_KEYS
        ),
        "tenant_operations_missing_evidence": _missing_true_keys(
            data, TENANT_OPERATIONS_KEYS
        ),
        "tenant_security_privacy_missing_evidence": _missing_true_keys(
            data, TENANT_SECURITY_PRIVACY_KEYS
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
        "customer_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "production_database_modified": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "live_customer_data_migrated": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
        "tenant_authorization_enabled": False,
        "production_tenant_storage_enabled": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after customer validation and all other production blockers are resolved"
        if status == "pass"
        else "complete production tenant storage model, isolation tests, operations, and security/privacy evidence before launch review",
    }
