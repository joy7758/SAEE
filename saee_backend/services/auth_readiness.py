"""Authentication readiness checks for the SAEE MVP API shell.

This module evaluates the public-shell authentication boundary only. It does
not implement OAuth/OIDC/SSO/RBAC, contact identity providers, call external
services, or inspect private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SaeeBackendSettings
from saee_backend.services.commercial_preflight import public_use_required


AuthReadinessStatus = Literal["pass", "hold", "stop"]
AuthFindingSeverity = Literal["info", "blocker"]


@dataclass(frozen=True)
class AuthReadinessFinding:
    check_id: str
    severity: AuthFindingSeverity
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
    severity: AuthFindingSeverity,
    passed: bool,
    message: str,
) -> AuthReadinessFinding:
    return AuthReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def evaluate_auth_readiness(settings: SaeeBackendSettings) -> dict[str, object]:
    """Return deterministic auth readiness for local and controlled-preview use."""

    public_use = public_use_required(settings)
    preview_auth_available = settings.require_api_key and settings.api_key_configured
    findings = [
        _finding(
            "environment_scope",
            "info",
            True,
            "non-local environment requires controlled-preview auth"
            if public_use
            else "local environment detected; auth is advisory",
        ),
        _finding(
            "preview_api_key_auth",
            "blocker",
            preview_auth_available if public_use else True,
            "non-local controlled preview must require and configure X-SAEE-API-Key",
        ),
        _finding(
            "production_identity_provider_non_claim",
            "info",
            True,
            "production identity provider is not configured and production_auth_ready remains false",
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
    if blockers:
        status: AuthReadinessStatus = "hold"
    else:
        status = "pass" if public_use and preview_auth_available else "hold"

    if blockers:
        next_action = "configure preview auth before controlled preview"
    elif status == "pass":
        next_action = "controlled preview auth is available; production identity provider remains missing"
    else:
        next_action = "keep local demo mode; configure preview auth before non-local use"

    return {
        "auth_readiness_type": "public_shell_auth_readiness",
        "environment": settings.environment,
        "public_use_required": public_use,
        "status": status,
        "auth_mode": settings.auth_mode,
        "auth_boundary_available": True,
        "preview_auth_available": preview_auth_available,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "sso_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
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
        "next_action": next_action,
    }
