#!/usr/bin/env python3
"""Smoke check for SAEE Production Auth Evidence Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_auth_evidence import (
    evaluate_production_auth_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_AUTH_EVIDENCE_SMOKE: FAIL: {message}")


def write_auth_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "auth_evidence_type": "production_auth_evidence",
        "production_identity_provider_selected": True,
        "identity_provider_admin_owner_named": True,
        "oidc_issuer_verified": True,
        "oidc_audience_approved": True,
        "jwks_rotation_policy_reviewed": True,
        "oauth_oidc_flow_approved": True,
        "token_validation_test_recorded": True,
        "claims_mapping_reviewed": True,
        "session_expiry_policy_approved": True,
        "auth_failure_handling_reviewed": True,
        "rbac_policy_approved": True,
        "role_matrix_reviewed": True,
        "tenant_role_boundary_reviewed": True,
        "least_privilege_reviewed": True,
        "admin_recovery_policy_reviewed": True,
        "production_ready": unsafe,
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
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_auth_evidence(load_settings({}))
    require(
        local["production_auth_evidence_type"] == "production_auth_evidence_readiness",
        "wrong evidence type",
    )
    require(local["production_auth_evidence_readiness_v0_1"] is True, "readiness flag")
    require(local["status"] == "hold", "default evidence status must hold")
    require(local["auth_evidence_path_configured"] is False, "default path false")
    require(
        local["production_identity_provider_available"] is False,
        "default identity provider false",
    )
    require(local["oauth_oidc_available"] is False, "default OAuth/OIDC false")
    require(local["rbac_available"] is False, "default RBAC false")
    require(local["production_auth_ready"] is False, "default auth ready false")
    require(local["production_ready"] is False, "default production false")
    require(local["customer_validated"] is False, "default customer validation false")
    require(local["product_launched"] is False, "default launch false")
    require(local["private_core_exposed"] is False, "default private core false")
    require(local["external_calls_made"] is False, "default external calls false")
    require(local["customer_contacted"] is False, "default customer contacted false")
    require(local["identity_provider_contacted"] is False, "default IdP contacted false")
    require(local["jwks_fetched"] is False, "default JWKS fetched false")
    require(
        local["tokens_validated_in_production"] is False,
        "default production tokens false",
    )
    require(local["production_auth_enabled"] is False, "default auth enabled false")
    require(local["rbac_enforced_in_production"] is False, "default RBAC enforced false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "AUTH_EVIDENCE.json"
        write_auth_evidence(evidence_path)
        settings = load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(evidence_path)})
        configured = evaluate_production_auth_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_AUTH_EVIDENCE.json"
        write_auth_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_auth_evidence(
            load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(unsafe_path)})
        )

    require(configured["status"] == "pass", "complete auth evidence should pass")
    require(
        configured["production_identity_provider_available"] is True,
        "identity provider evidence true",
    )
    require(configured["oauth_oidc_available"] is True, "OAuth/OIDC evidence true")
    require(configured["rbac_available"] is True, "RBAC evidence true")
    require(configured["production_auth_ready"] is True, "auth ready evidence true")
    require(configured["production_ready"] is False, "evidence pass must not claim production")
    require(configured["customer_validated"] is False, "evidence pass must not claim customers")
    require(configured["product_launched"] is False, "evidence pass must not claim launch")
    require(configured["external_calls_made"] is False, "evidence pass must not call external")
    require(configured["customer_contacted"] is False, "evidence pass must not contact customers")
    require(
        configured["identity_provider_contacted"] is False,
        "evidence pass must not contact IdP",
    )
    require(configured["jwks_fetched"] is False, "evidence pass must not fetch JWKS")
    require(
        configured["tokens_validated_in_production"] is False,
        "evidence pass must not validate production tokens",
    )
    require(
        configured["production_auth_enabled"] is False,
        "evidence pass must not enable production auth",
    )
    require(
        configured["rbac_enforced_in_production"] is False,
        "evidence pass must not enforce production RBAC",
    )

    blocked = blocker_ids(go_no_go)
    for blocker in ["production_identity_provider", "oauth_oidc", "rbac"]:
        require(blocker not in blocked, f"{blocker} should be satisfied by auth evidence")
    require(
        go_no_go["production_auth_evidence_status"] == "pass",
        "go/no-go should expose auth evidence pass",
    )
    require(
        go_no_go["auth_evidence_production_identity_provider_available"] is True,
        "go/no-go should expose identity provider evidence",
    )
    require(
        go_no_go["auth_evidence_oauth_oidc_available"] is True,
        "go/no-go should expose OAuth/OIDC evidence",
    )
    require(
        go_no_go["auth_evidence_rbac_available"] is True,
        "go/no-go should expose RBAC evidence",
    )
    require(go_no_go["commercial_status"] == "hold", "auth evidence alone must not launch")
    require(go_no_go["production_launch_status"] == "hold", "production launch must still hold")
    require(go_no_go["production_ready"] is False, "go/no-go must keep production false")
    require(go_no_go["customer_validated"] is False, "go/no-go must keep customer false")
    require(go_no_go["product_launched"] is False, "go/no-go must keep launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go must keep private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require("production_ready" in unsafe["boundary_violations"], "unsafe evidence must detect boundary")
    require(unsafe["production_ready"] is False, "unsafe output must preserve production false")

    doc = (
        ROOT / "phase_b_product/commercial_readiness/PRODUCTION_AUTH_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_PRODUCTION_AUTH_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    for token in [
        "production_auth_evidence_readiness_v0_1: true",
        "default_status: hold",
        "auth_evidence_path_configured_default: false",
        "production_identity_provider_available_default: false",
        "oauth_oidc_available_default: false",
        "rbac_available_default: false",
        "production_auth_ready_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "identity_provider_contacted: false",
        "jwks_fetched: false",
        "tokens_validated_in_production: false",
        "production_auth_enabled: false",
        "rbac_enforced_in_production: false",
        "answer: conditional",
        "recommend_for_production_launch: false",
    ]:
        require(token in doc or token in gate, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_AUTH_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_AUTH_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_auth_evidence.py",
        "/scripts/saee_production_auth_evidence_readiness.py",
        "/scripts/saee_production_auth_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_auth_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_auth_evidence_readiness_hold",
        "production_auth_evidence_readiness_v0_1": True,
        "auth_evidence_path_configured_default": False,
        "production_identity_provider_available_default": False,
        "oauth_oidc_available_default": False,
        "rbac_available_default": False,
        "production_auth_ready_default": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
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
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_AUTH_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "auth_blockers_satisfied_by_evidence=true production_launch_status=hold "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
