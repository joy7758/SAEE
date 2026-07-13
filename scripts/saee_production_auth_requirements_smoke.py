#!/usr/bin/env python3
"""Smoke check for SAEE Production Auth Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_AUTH_REQUIREMENTS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_AUTH_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_auth_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")
    require(data["production_auth_implemented"] is False, "auth not implemented")
    require(data["production_identity_provider_available"] is False, "IdP false")
    require(data["oauth_oidc_available"] is False, "OIDC false")
    require(data["rbac_available"] is False, "RBAC false")
    require(data["account_lifecycle_available"] is False, "account lifecycle false")
    require(data["session_management_available"] is False, "session management false")
    require(data["tenant_authorization_available"] is False, "tenant authorization false")
    require(data["admin_recovery_available"] is False, "admin recovery false")
    require(data["production_auth_ready"] is False, "production auth false")
    require(data["production_ready"] is False, "production ready false")
    require(data["customer_validated"] is False, "customer validation false")
    require(data["product_launched"] is False, "product launch false")
    require(data["private_core_exposed"] is False, "private core false")
    require(data["task_candidates_executed"] is False, "tasks not executed")
    require(data["development_permission_granted"] is False, "development permission false")
    require(data["runtime_modified"] is False, "runtime false")
    require(data["backend_modified"] is False, "backend false")
    require(data["kernel_modified"] is False, "kernel false")
    require(data["api_schema_modified"] is False, "API schema false")
    require(data["external_calls_made"] is False, "external calls false")
    require(data["external_identity_provider_contacted"] is False, "external IdP false")

    blockers = set(data["auth_blockers_covered_as_requirements"])
    require(blockers == {"production_identity_provider", "oauth_oidc", "rbac"}, "auth blockers mismatch")
    claims = set(data["required_oidc_claims"])
    for claim in ["iss", "sub", "aud", "exp", "iat", "tenant_id", "roles"]:
        require(claim in claims, f"missing OIDC claim {claim}")
    require(not claims.intersection({"email", "email_verified", "phone", "name", "address"}), "personal claims forbidden")
    require(set(data["optional_oidc_claims"]) == {"nbf", "jti"}, "optional claims mismatch")
    roles = {item["role"] for item in data["role_matrix"]}
    for role in ["owner", "admin", "evaluator_operator", "viewer", "support_operator"]:
        require(role in roles, f"missing role {role}")
    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match auth blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_auth_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_auth_implemented: false",
        "production_identity_provider_available: false",
        "oauth_oidc_available: false",
        "rbac_available: false",
        "production_auth_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "task_candidates_executed: false",
        "development_permission_granted: false",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_production_auth_implementation: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_AUTH_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_auth_requirements.py",
        "/scripts/saee_production_auth_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_auth_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_auth_requirements_v0_1": True,
        "production_auth_implemented": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_AUTH_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true production_auth_ready=false "
        "oauth_oidc_available=false rbac_available=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
