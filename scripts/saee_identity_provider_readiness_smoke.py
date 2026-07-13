#!/usr/bin/env python3
"""Smoke check for SAEE Identity Provider Configuration Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.identity_provider_readiness import (
    evaluate_identity_provider_readiness,
)
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_IDENTITY_PROVIDER_READINESS_SMOKE: FAIL: {message}")


def main() -> None:
    local = evaluate_identity_provider_readiness(load_settings({}))
    require(
        local["identity_provider_config_readiness_type"]
        == "production_identity_provider_config_readiness",
        "wrong readiness type",
    )
    require(local["identity_provider_config_readiness_v0_1"] is True, "readiness flag true")
    require(local["status"] == "hold", "default config readiness must hold")
    require(local["oidc_configuration_present"] is False, "default OIDC config false")
    require(local["rbac_policy_path_configured"] is False, "default RBAC path false")
    require(
        local["required_rbac_permissions_present"] is False,
        "default RBAC permissions false",
    )
    require(
        local["required_rbac_route_scopes_present"] is False,
        "default RBAC route scopes false",
    )
    require(
        local["rbac_route_scope_matrix_parseable"] is False,
        "default RBAC route matrix false",
    )
    require(local["production_identity_provider_available"] is False, "production IdP false")
    require(local["oauth_oidc_available"] is False, "OAuth/OIDC false")
    require(local["rbac_available"] is False, "RBAC false")
    require(local["production_auth_ready"] is False, "production auth false")
    require(local["production_ready"] is False, "production ready false")
    require(local["customer_validated"] is False, "customer validation false")
    require(local["product_launched"] is False, "product launch false")
    require(local["private_core_exposed"] is False, "private core false")
    require(local["external_calls_made"] is False, "external calls false")
    require(
        local["external_identity_provider_contacted"] is False,
        "external IdP contact false",
    )
    require(local["jwks_fetched"] is False, "JWKS fetched false")
    require(local["tokens_validated"] is False, "tokens validated false")
    require(local["rbac_enforced"] is False, "RBAC enforced false")

    generate_template()
    configured = evaluate_identity_provider_readiness(
        load_settings(
            {
                "SAEE_PRODUCTION_OIDC_ISSUER": "https://idp.example.invalid/",
                "SAEE_PRODUCTION_OIDC_AUDIENCE": "saee-preview",
                "SAEE_PRODUCTION_OIDC_JWKS_URL": "https://idp.example.invalid/.well-known/jwks.json",
                "SAEE_PRODUCTION_RBAC_POLICY_PATH": str(TEMPLATE_PATH),
            }
        )
    )

    require(configured["status"] == "pass", "complete local config should pass config readiness")
    require(configured["oidc_configuration_present"] is True, "OIDC config present")
    require(configured["rbac_policy_file_exists"] is True, "RBAC file exists")
    require(configured["rbac_policy_parseable"] is True, "RBAC file parseable")
    require(configured["required_rbac_roles_present"] is True, "required roles present")
    require(
        configured["required_rbac_permissions_present"] is True,
        "required permissions present",
    )
    require(
        configured["required_rbac_route_scopes_present"] is True,
        "required route scopes present",
    )
    require(
        configured["rbac_route_scope_matrix_parseable"] is True,
        "route-scope matrix parseable",
    )
    require(
        configured["production_identity_provider_available"] is False,
        "config pass must not claim production IdP",
    )
    require(configured["oauth_oidc_available"] is False, "config pass must not claim OIDC")
    require(configured["rbac_available"] is False, "config pass must not claim RBAC")
    require(
        configured["production_auth_ready"] is False,
        "config pass must not claim production auth",
    )
    require(configured["production_ready"] is False, "config pass must not claim production")
    require(configured["external_calls_made"] is False, "config pass must not call external services")
    require(configured["external_identity_provider_contacted"] is False, "config pass must not contact IdP")
    require(configured["jwks_fetched"] is False, "config pass must not fetch JWKS")
    require(configured["tokens_validated"] is False, "config pass must not validate tokens")
    require(configured["rbac_enforced"] is False, "config pass must not enforce RBAC")

    inconsistent_policy = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    inconsistent_operator = next(
        item for item in inconsistent_policy["roles"] if item["role"] == "evaluator_operator"
    )
    inconsistent_operator["permissions"].remove("experiment:run")
    with tempfile.TemporaryDirectory(prefix="saee-idp-readiness-") as directory:
        inconsistent_path = Path(directory) / "inconsistent-rbac.json"
        inconsistent_path.write_text(json.dumps(inconsistent_policy), encoding="utf-8")
        inconsistent = evaluate_identity_provider_readiness(
            load_settings(
                {
                    "SAEE_PRODUCTION_OIDC_ISSUER": "https://idp.example.invalid/",
                    "SAEE_PRODUCTION_OIDC_AUDIENCE": "saee-preview",
                    "SAEE_PRODUCTION_OIDC_JWKS_URL": "https://idp.example.invalid/.well-known/jwks.json",
                    "SAEE_PRODUCTION_RBAC_POLICY_PATH": str(inconsistent_path),
                }
            )
        )
    require(inconsistent["status"] == "hold", "role-permission mismatch must hold")
    require(inconsistent["rbac_policy_parseable"] is True, "mismatched policy remains JSON parseable")
    require(
        inconsistent["rbac_route_scope_matrix_parseable"] is False,
        "role-permission mismatch must fail matrix consistency",
    )
    require(inconsistent["production_auth_ready"] is False, "mismatch keeps production auth false")

    readiness_payload = load_settings(
        {
            "SAEE_PRODUCTION_OIDC_ISSUER": "https://idp.example.invalid/",
            "SAEE_PRODUCTION_OIDC_AUDIENCE": "saee-preview",
            "SAEE_PRODUCTION_OIDC_JWKS_URL": "https://idp.example.invalid/.well-known/jwks.json",
            "SAEE_PRODUCTION_RBAC_POLICY_PATH": "/tmp/saee-rbac-policy.json",
        }
    ).readiness_payload()
    require(
        readiness_payload["identity_provider_config_readiness_v0_1"] is True,
        "ready payload must expose identity config readiness",
    )
    require(
        readiness_payload["production_oidc_configuration_present"] is True,
        "ready payload must expose OIDC config presence",
    )
    require(
        readiness_payload["production_rbac_policy_path_configured"] is True,
        "ready payload must expose RBAC path presence",
    )
    require(
        readiness_payload["production_identity_provider_available"] is False,
        "ready payload must keep IdP false",
    )
    require(
        readiness_payload["oauth_oidc_available"] is False,
        "ready payload must keep OIDC false",
    )
    require(readiness_payload["rbac_available"] is False, "ready payload must keep RBAC false")
    require(
        readiness_payload["production_auth_ready"] is False,
        "ready payload must keep production auth false",
    )

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/IDENTITY_PROVIDER_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_IDENTITY_PROVIDER_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    for token in [
        "identity_provider_config_readiness_v0_1: true",
        "production_identity_provider_available: false",
        "oauth_oidc_available: false",
        "rbac_available: false",
        "production_auth_ready: false",
        "external_identity_provider_contacted: false",
        "jwks_fetched: false",
        "tokens_validated: false",
        "rbac_enforced: false",
        "answer: conditional",
        "recommend_for_production_auth_implementation: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in doc or token in gate, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/IDENTITY_PROVIDER_READINESS_V0_1.md",
        "/docs/strategy/SAEE_IDENTITY_PROVIDER_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/identity_provider_readiness.py",
        "/scripts/saee_identity_provider_readiness.py",
        "/scripts/saee_identity_provider_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("identity_provider_readiness_v0_1", {})
    expected = {
        "status": "production_identity_provider_config_readiness_hold",
        "identity_provider_config_readiness_v0_1": True,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_identity_provider_contacted": False,
        "jwks_fetched": False,
        "tokens_validated": False,
        "rbac_enforced": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_IDENTITY_PROVIDER_READINESS_SMOKE: PASS "
        "config_readiness_present=true production_auth_ready=false "
        "oauth_oidc_available=false rbac_available=false "
        "role_permission_mismatch_rejected=true external_calls_made=false"
    )


if __name__ == "__main__":
    main()
