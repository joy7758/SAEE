"""Production identity provider configuration readiness checks.

This module evaluates configuration inputs for a future production identity
provider integration. It does not implement OAuth/OIDC, fetch JWKS, validate
tokens, enforce RBAC, contact identity providers, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings
from saee_backend.services.rbac_policy import RbacPolicyError, validate_rbac_policy_document


IdentityProviderConfigStatus = Literal["pass", "hold", "stop"]
IdentityProviderFindingSeverity = Literal["info", "blocker"]

REQUIRED_RBAC_ROLES = {
    "owner",
    "admin",
    "evaluator_operator",
    "viewer",
    "support_operator",
}

REQUIRED_RBAC_PERMISSIONS = {
    "admin:manage",
    "audit:read",
    "experiment:create",
    "experiment:read",
    "experiment:run",
    "operations:read",
    "readiness:read",
    "support:read",
    "support:triage",
}

REQUIRED_ROUTE_SCOPES = {
    "GET /health",
    "GET /ready",
    "GET /commercial/status",
    "GET /experiment",
    "POST /experiment/create",
    "POST /experiment/run",
    "GET /experiment/{experiment_id}/stability",
    "GET /experiment/{experiment_id}/failures",
    "GET /experiment/{experiment_id}/ranking",
    "GET /experiment/{experiment_id}/survival",
    "GET /operations/telemetry",
    "GET /operations/alerts",
    "GET /readiness/billing-pricing",
    "GET /readiness/data-operations",
    "GET /readiness/legal",
    "GET /readiness/operations",
    "GET /readiness/privacy-security",
    "GET /readiness/support",
    "GET /readiness/vulnerability",
}

FORBIDDEN_TRUE_KEYS = {
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
    "external_identity_provider_contacted",
    "jwks_fetched",
    "tokens_validated",
    "rbac_enforced",
    "production_auth_ready",
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
}


@dataclass(frozen=True)
class IdentityProviderReadinessFinding:
    check_id: str
    severity: IdentityProviderFindingSeverity
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
    severity: IdentityProviderFindingSeverity,
    passed: bool,
    message: str,
) -> IdentityProviderReadinessFinding:
    return IdentityProviderReadinessFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def _load_rbac_policy(
    path_value: str,
) -> tuple[bool, bool, set[str], set[str], set[str], bool]:
    if not path_value:
        return False, False, set(), set(), set(), False
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        return False, False, set(), set(), set(), False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, False, set(), set(), set(), False
    roles = data.get("roles", [])
    if not isinstance(roles, list):
        return True, False, set(), set(), set(), False
    role_names = {
        role.get("role")
        for role in roles
        if isinstance(role, dict) and isinstance(role.get("role"), str)
    }
    permissions: set[str] = set()
    for role in roles:
        if not isinstance(role, dict):
            continue
        role_permissions = role.get("permissions", [])
        if not isinstance(role_permissions, list):
            continue
        permissions.update(
            permission
            for permission in role_permissions
            if isinstance(permission, str)
        )
    route_scopes = data.get("route_scopes", [])
    if not isinstance(route_scopes, list):
        return True, False, role_names, permissions, set(), False
    route_names = {
        route.get("route")
        for route in route_scopes
        if isinstance(route, dict) and isinstance(route.get("route"), str)
    }
    route_scope_matrix_parseable = all(
        isinstance(route, dict)
        and isinstance(route.get("route"), str)
        and isinstance(route.get("required_permission"), str)
        and isinstance(route.get("allowed_roles"), list)
        and all(isinstance(role, str) for role in route.get("allowed_roles", []))
        for route in route_scopes
    )
    boundary_safe = not any(data.get(key) is True for key in FORBIDDEN_TRUE_KEYS)
    try:
        validate_rbac_policy_document(data)
    except RbacPolicyError:
        route_scope_matrix_parseable = False
    return (
        True,
        True,
        role_names,
        permissions,
        route_names,
        route_scope_matrix_parseable and boundary_safe,
    )


def evaluate_identity_provider_readiness(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic production IdP configuration readiness.

    A `pass` status here means only that required local configuration inputs
    are present and parseable for future implementation review. It is not a
    production-authentication pass.
    """

    oidc_issuer_configured = bool(settings.production_oidc_issuer)
    oidc_audience_configured = bool(settings.production_oidc_audience)
    oidc_jwks_url_configured = bool(settings.production_oidc_jwks_url)
    oidc_configuration_present = (
        oidc_issuer_configured
        and oidc_audience_configured
        and oidc_jwks_url_configured
    )
    rbac_policy_path_configured = bool(settings.production_rbac_policy_path)
    (
        rbac_file_exists,
        rbac_policy_parseable,
        configured_roles,
        configured_permissions,
        configured_route_scopes,
        rbac_route_scope_matrix_parseable,
    ) = _load_rbac_policy(settings.production_rbac_policy_path)
    missing_roles = sorted(REQUIRED_RBAC_ROLES - configured_roles)
    required_roles_present = rbac_policy_parseable and not missing_roles
    missing_permissions = sorted(REQUIRED_RBAC_PERMISSIONS - configured_permissions)
    required_permissions_present = rbac_policy_parseable and not missing_permissions
    missing_route_scopes = sorted(REQUIRED_ROUTE_SCOPES - configured_route_scopes)
    required_route_scopes_present = rbac_policy_parseable and not missing_route_scopes

    findings = [
        _finding(
            "oidc_issuer_configured",
            "blocker",
            oidc_issuer_configured,
            "SAEE_PRODUCTION_OIDC_ISSUER must identify the expected issuer",
        ),
        _finding(
            "oidc_audience_configured",
            "blocker",
            oidc_audience_configured,
            "SAEE_PRODUCTION_OIDC_AUDIENCE must identify the expected audience",
        ),
        _finding(
            "oidc_jwks_url_configured",
            "blocker",
            oidc_jwks_url_configured,
            "SAEE_PRODUCTION_OIDC_JWKS_URL must identify the JWKS URL for later implementation",
        ),
        _finding(
            "rbac_policy_path_configured",
            "blocker",
            rbac_policy_path_configured,
            "SAEE_PRODUCTION_RBAC_POLICY_PATH must point to a local RBAC policy file",
        ),
        _finding(
            "rbac_policy_file_exists",
            "blocker",
            rbac_file_exists,
            "Configured RBAC policy path must exist locally",
        ),
        _finding(
            "rbac_policy_parseable",
            "blocker",
            rbac_policy_parseable,
            "Configured RBAC policy must be parseable JSON",
        ),
        _finding(
            "required_roles_present",
            "blocker",
            required_roles_present,
            "Configured RBAC policy must include owner, admin, evaluator_operator, viewer, and support_operator roles",
        ),
        _finding(
            "required_permissions_present",
            "blocker",
            required_permissions_present,
            "Configured RBAC policy must include the required permission vocabulary",
        ),
        _finding(
            "required_route_scopes_present",
            "blocker",
            required_route_scopes_present,
            "Configured RBAC policy must map every public-shell route to a permission",
        ),
        _finding(
            "rbac_route_scope_matrix_parseable",
            "blocker",
            rbac_route_scope_matrix_parseable,
            "Configured RBAC route-scope matrix must be parseable and boundary-safe",
        ),
        _finding(
            "external_identity_provider_non_contact",
            "info",
            True,
            "readiness check does not contact the identity provider or fetch JWKS",
        ),
        _finding(
            "production_auth_non_claim",
            "info",
            True,
            "production_identity_provider_available, oauth_oidc_available, rbac_available, and production_auth_ready remain false",
        ),
    ]

    blockers = [
        finding
        for finding in findings
        if finding.severity == "blocker" and not finding.passed
    ]
    status: IdentityProviderConfigStatus = "hold" if blockers else "pass"
    next_action = (
        "human review may decide whether to authorize production auth implementation"
        if status == "pass"
        else "configure OIDC inputs and a local RBAC policy before implementation review"
    )

    return {
        "identity_provider_config_readiness_type": "production_identity_provider_config_readiness",
        "identity_provider_config_readiness_v0_1": True,
        "status": status,
        "oidc_configuration_present": oidc_configuration_present,
        "oidc_issuer_configured": oidc_issuer_configured,
        "oidc_audience_configured": oidc_audience_configured,
        "oidc_jwks_url_configured": oidc_jwks_url_configured,
        "rbac_policy_path_configured": rbac_policy_path_configured,
        "rbac_policy_file_exists": rbac_file_exists,
        "rbac_policy_parseable": rbac_policy_parseable,
        "required_rbac_roles_present": required_roles_present,
        "missing_rbac_roles": missing_roles,
        "required_rbac_permissions_present": required_permissions_present,
        "missing_rbac_permissions": missing_permissions,
        "required_rbac_route_scopes_present": required_route_scopes_present,
        "missing_rbac_route_scopes": missing_route_scopes,
        "rbac_route_scope_matrix_parseable": rbac_route_scope_matrix_parseable,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
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
        "external_identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated": False,
        "rbac_enforced": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blockers),
        "next_action": next_action,
    }
