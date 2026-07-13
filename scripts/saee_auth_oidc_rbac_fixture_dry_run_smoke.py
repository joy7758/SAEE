#!/usr/bin/env python3
"""Smoke check for the local Auth/OIDC/RBAC fixture dry-run."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_auth_oidc_rbac_fixture_dry_run import (
    FORBIDDEN_TRUE_KEYS,
    RESULTS_PATH,
    main as run_fixture_dry_run,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_SMOKE: FAIL: " + message)


def main() -> None:
    run_fixture_dry_run()
    require(RESULTS_PATH.exists(), "results JSON must exist")
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    expected_true = [
        "auth_oidc_rbac_fixture_dry_run_v0_1",
        "local_fixture_token_validation_test_recorded",
        "local_fixture_claims_mapping_reviewed",
        "local_fixture_negative_auth_cases_rejected",
        "local_fixture_rbac_route_matrix_tested",
        "local_fixture_rbac_route_matrix_passed",
    ]
    for flag in expected_true:
        require(results.get(flag) is True, f"{flag} must be true")

    require(results.get("status") == "pass", "fixture status must pass")
    require(
        results.get("evidence_scope") == "local_fixture_only_no_external_idp",
        "wrong evidence scope",
    )
    require(
        len(results.get("fixture_claim_cases", [])) == 5,
        "must include five claim fixture cases",
    )
    require(
        len(results.get("fixture_rbac_cases", [])) == 6,
        "must include six RBAC fixture cases",
    )
    require(
        all(case.get("passed") is True for case in results["fixture_claim_cases"]),
        "all claim fixture cases must pass",
    )
    require(
        all(case.get("passed") is True for case in results["fixture_rbac_cases"]),
        "all RBAC fixture cases must pass",
    )

    expected_false = [
        "production_identity_provider_selected",
        "identity_provider_admin_owner_named",
        "oidc_issuer_verified",
        "oidc_audience_approved",
        "jwks_rotation_policy_reviewed",
        "oauth_oidc_flow_approved",
        "token_validation_test_recorded",
        "claims_mapping_reviewed",
        "session_expiry_policy_approved",
        "auth_failure_handling_reviewed",
        "rbac_policy_approved",
        "least_privilege_reviewed",
        "admin_recovery_policy_reviewed",
        "production_identity_provider_available",
        "oauth_oidc_available",
        "rbac_available",
        "production_auth_ready",
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
    ]
    for flag in expected_false:
        require(results.get(flag) is False, f"{flag} must remain false")
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if results.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))
    require(
        results.get("blockers_closed_by_fixture_dry_run") == 0,
        "fixture dry-run must close zero blockers",
    )

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    report = (
        ROOT
        / "phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run/auth_oidc_rbac_fixture_dry_run.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate + "\n" + report
    for token in [
        "auth_oidc_rbac_fixture_dry_run_v0_1: true",
        "evidence_scope: local_fixture_only_no_external_idp",
        "local_fixture_token_validation_test_recorded: true",
        "local_fixture_claims_mapping_reviewed: true",
        "local_fixture_rbac_route_matrix_tested: true",
        "production_identity_provider_available: false",
        "oauth_oidc_available: false",
        "rbac_available: false",
        "production_auth_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "identity_provider_contacted: false",
        "jwks_fetched: false",
        "tokens_validated_in_production: false",
        "production_auth_enabled: false",
        "rbac_enforced_in_production: false",
        "blockers_closed_by_fixture_dry_run: 0",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    for forbidden in [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "identity_provider_contacted: true",
        "\"identity_provider_contacted\": true",
        "jwks_fetched: true",
        "\"jwks_fetched\": true",
        "tokens_validated_in_production: true",
        "\"tokens_validated_in_production\": true",
        "production_auth_enabled: true",
        "\"production_auth_enabled\": true",
        "rbac_enforced_in_production: true",
        "\"rbac_enforced_in_production\": true",
        "production_auth_ready: true",
        "\"production_auth_ready\": true",
    ]:
        require(forbidden not in combined, "forbidden true token in docs: " + forbidden)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_V0_1.md",
        "/docs/strategy/SAEE_AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run/README.md",
        "/phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run/auth_oidc_rbac_fixture_dry_run.local.json",
        "/phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run/auth_oidc_rbac_fixture_dry_run.md",
        "/scripts/saee_auth_oidc_rbac_fixture_dry_run.py",
        "/scripts/saee_auth_oidc_rbac_fixture_dry_run_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("auth_oidc_rbac_fixture_dry_run_v0_1", {})
    expected = {
        "status": "local_fixture_dry_run_pass_no_blocker_closure",
        "auth_oidc_rbac_fixture_dry_run_v0_1": True,
        "evidence_scope": "local_fixture_only_no_external_idp",
        "local_fixture_token_validation_test_recorded": True,
        "local_fixture_claims_mapping_reviewed": True,
        "local_fixture_negative_auth_cases_rejected": True,
        "local_fixture_rbac_route_matrix_tested": True,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
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
        "blockers_closed_by_fixture_dry_run": 0,
    }
    for flag, expected_value in expected.items():
        require(entry.get(flag) == expected_value, f"agent-index {flag} mismatch")

    print(
        "SAEE_AUTH_OIDC_RBAC_FIXTURE_DRY_RUN_SMOKE: PASS "
        "local_fixture_only=true production_auth_ready=false "
        "blockers_closed_by_fixture_dry_run=0"
    )


if __name__ == "__main__":
    main()
