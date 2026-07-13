#!/usr/bin/env python3
"""Smoke test the SAEE RBAC policy template pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.identity_provider_readiness import (
    REQUIRED_RBAC_PERMISSIONS,
    REQUIRED_RBAC_ROLES,
    REQUIRED_ROUTE_SCOPES,
    evaluate_identity_provider_readiness,
)
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_RBAC_POLICY_TEMPLATE_SMOKE: FAIL {message}")


def main() -> None:
    generate_template()
    require(TEMPLATE_PATH.exists(), "template missing")
    data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    require(
        data.get("policy_type") == "saee_production_rbac_policy_template",
        "policy type mismatch",
    )
    require(data.get("policy_status") == "template_only_not_enforced", "status mismatch")
    require(data.get("rbac_policy_template_v0_1") is True, "template flag missing")
    require(
        set(data.get("required_roles", [])) == REQUIRED_RBAC_ROLES,
        "required roles mismatch",
    )
    require(
        set(data.get("required_permissions", [])) == REQUIRED_RBAC_PERMISSIONS,
        "required permissions mismatch",
    )
    require(
        set(data.get("required_route_scopes", [])) == REQUIRED_ROUTE_SCOPES,
        "required route scopes mismatch",
    )

    readiness = evaluate_identity_provider_readiness(
        load_settings(
            {
                "SAEE_PRODUCTION_OIDC_ISSUER": "https://idp.example.invalid/",
                "SAEE_PRODUCTION_OIDC_AUDIENCE": "saee-preview",
                "SAEE_PRODUCTION_OIDC_JWKS_URL": "https://idp.example.invalid/.well-known/jwks.json",
                "SAEE_PRODUCTION_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
            }
        )
    )
    require(readiness["status"] == "pass", "template should pass config readiness")
    require(readiness["required_rbac_roles_present"] is True, "roles must be present")
    require(
        readiness["required_rbac_permissions_present"] is True,
        "permissions must be present",
    )
    require(
        readiness["required_rbac_route_scopes_present"] is True,
        "route scopes must be present",
    )
    require(
        readiness["rbac_route_scope_matrix_parseable"] is True,
        "route matrix must be parseable",
    )

    for key in [
        "production_identity_provider_available",
        "oauth_oidc_available",
        "rbac_available",
        "rbac_enforced",
        "production_auth_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "runtime_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_identity_provider_contacted",
        "jwks_fetched",
        "tokens_validated",
    ]:
        require(data.get(key) is False, f"template {key} must be false")
        require(readiness.get(key) is False, f"readiness {key} must be false")

    readme = (TEMPLATE_PATH.parent / "README.md").read_text(encoding="utf-8")
    for token in [
        "Status: template only; RBAC is not enforced.",
        "No RBAC enforcement enabled.",
        "No production authentication readiness claimed.",
        "No private core exposed.",
    ]:
        require(token in readme, f"README missing {token}")

    print(
        "SAEE_RBAC_POLICY_TEMPLATE_SMOKE: PASS "
        f"roles={len(REQUIRED_RBAC_ROLES)} "
        f"permissions={len(REQUIRED_RBAC_PERMISSIONS)} "
        f"route_scopes={len(REQUIRED_ROUTE_SCOPES)} "
        "rbac_enforced=false production_auth_ready=false"
    )


if __name__ == "__main__":
    main()
