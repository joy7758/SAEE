"""Production authentication evidence readiness checks.

This module validates a local evidence JSON file for future production
authentication review. It does not validate real tokens, contact identity
providers, fetch JWKS, enable RBAC, deploy production authentication, change API
schema, modify runtime behavior, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionAuthEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionAuthEvidenceSeverity = Literal["info", "blocker"]

AUTH_IDP_KEYS = (
    "production_identity_provider_selected",
    "identity_provider_admin_owner_named",
    "oidc_issuer_verified",
    "oidc_audience_approved",
    "jwks_rotation_policy_reviewed",
)
OAUTH_OIDC_KEYS = (
    "oauth_oidc_flow_approved",
    "token_validation_test_recorded",
    "claims_mapping_reviewed",
    "session_expiry_policy_approved",
    "auth_failure_handling_reviewed",
)
RBAC_KEYS = (
    "rbac_policy_approved",
    "role_matrix_reviewed",
    "tenant_role_boundary_reviewed",
    "least_privilege_reviewed",
    "admin_recovery_policy_reviewed",
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
    "identity_provider_contacted",
    "jwks_fetched",
    "tokens_validated_in_production",
    "production_auth_enabled",
    "rbac_enforced_in_production",
)


@dataclass(frozen=True)
class ProductionAuthEvidenceFinding:
    check_id: str
    severity: ProductionAuthEvidenceSeverity
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
    severity: ProductionAuthEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionAuthEvidenceFinding:
    return ProductionAuthEvidenceFinding(
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


def evaluate_production_auth_evidence(settings: SaeeBackendSettings) -> dict[str, object]:
    """Return deterministic production-auth evidence readiness.

    A `pass` means the local evidence file is internally complete enough for
    human production launch review. It is not production authentication, token
    validation, IdP integration, RBAC enforcement, launch approval, or a
    production-readiness claim.
    """

    path_configured = bool(settings.production_auth_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_auth_evidence_path
    )
    correct_type = data.get("auth_evidence_type") == "production_auth_evidence"
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    production_identity_provider_available = _all_true(data, AUTH_IDP_KEYS)
    oauth_oidc_available = _all_true(data, OAUTH_OIDC_KEYS)
    rbac_available = _all_true(data, RBAC_KEYS)
    production_auth_ready = (
        production_identity_provider_available
        and oauth_oidc_available
        and rbac_available
        and not forbidden_true
    )

    findings = [
        _finding(
            "auth_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH must point to local auth evidence",
        ),
        _finding(
            "auth_evidence_file_exists",
            "blocker",
            file_exists,
            "auth evidence file must exist locally",
        ),
        _finding(
            "auth_evidence_file_parseable",
            "blocker",
            file_parseable,
            "auth evidence file must be parseable JSON",
        ),
        _finding(
            "auth_evidence_type_valid",
            "blocker",
            correct_type,
            "auth_evidence_type must be production_auth_evidence",
        ),
        _finding(
            "production_identity_provider_evidence_complete",
            "blocker",
            production_identity_provider_available,
            "production identity provider evidence must be complete",
        ),
        _finding(
            "oauth_oidc_evidence_complete",
            "blocker",
            oauth_oidc_available,
            "OAuth/OIDC evidence must be complete",
        ),
        _finding(
            "rbac_evidence_complete",
            "blocker",
            rbac_available,
            "RBAC evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "auth evidence must not claim production launch, customer validation, IdP contact, JWKS fetch, production token validation, RBAC enforcement, private-core exposure, or code modification",
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
        status: ProductionAuthEvidenceStatus = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_auth_evidence_type": "production_auth_evidence_readiness",
        "production_auth_evidence_readiness_v0_1": True,
        "status": status,
        "auth_evidence_path_configured": path_configured,
        "auth_evidence_file_exists": file_exists,
        "auth_evidence_file_parseable": file_parseable,
        "auth_evidence_type_valid": correct_type,
        "production_identity_provider_available": production_identity_provider_available,
        "oauth_oidc_available": oauth_oidc_available,
        "rbac_available": rbac_available,
        "production_auth_ready": production_auth_ready,
        "production_identity_provider_missing_evidence": _missing_true_keys(
            data, AUTH_IDP_KEYS
        ),
        "oauth_oidc_missing_evidence": _missing_true_keys(data, OAUTH_OIDC_KEYS),
        "rbac_missing_evidence": _missing_true_keys(data, RBAC_KEYS),
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
        "identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated_in_production": False,
        "production_auth_enabled": False,
        "rbac_enforced_in_production": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after all other production blockers are resolved"
        if status == "pass"
        else "complete production IdP, OAuth/OIDC, and RBAC evidence before launch review",
    }
