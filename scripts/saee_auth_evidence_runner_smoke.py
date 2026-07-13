#!/usr/bin/env python3
"""Smoke check for the local auth evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_auth_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_auth_evidence,
)
from scripts.saee_auth_evidence_runner import OUTPUT_PATH, main as run_runner


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_AUTH_EVIDENCE_RUNNER_SMOKE: FAIL: " + message)


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    require(
        evidence.get("auth_evidence_type") == "production_auth_evidence",
        "wrong auth evidence type",
    )
    require(
        evidence.get("evidence_scope") == "local_public_shell_auth_review_packet",
        "wrong evidence scope",
    )
    for flag in [
        "role_matrix_reviewed",
        "tenant_role_boundary_reviewed",
    ]:
        require(evidence.get(flag) is True, f"{flag} must be recorded")
    for flag in [
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
    ]:
        require(evidence.get(flag) is False, f"{flag} must remain false")

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    local_results = evidence.get("local_public_shell_results", {})
    for flag in [
        "preview_api_key_auth_available",
        "oidc_configuration_present",
        "rbac_policy_template_available",
        "rbac_policy_parseable",
        "required_rbac_roles_present",
        "required_rbac_permissions_present",
        "required_rbac_route_scopes_present",
        "rbac_route_scope_matrix_parseable",
        "local_fixture_token_validation_test_recorded",
        "local_fixture_claims_mapping_reviewed",
        "local_fixture_negative_auth_cases_rejected",
        "local_fixture_rbac_route_matrix_tested",
        "local_fixture_rbac_route_matrix_passed",
    ]:
        require(local_results.get(flag) is True, f"local result {flag} must be true")
    require(
        local_results.get("auth_oidc_rbac_fixture_dry_run_status") == "pass",
        "fixture dry-run status must be pass",
    )
    require(
        local_results.get("local_fixture_claim_cases_passed") == 5,
        "fixture claim cases passed must be 5",
    )
    require(
        local_results.get("local_fixture_rbac_cases_passed") == 6,
        "fixture RBAC cases passed must be 6",
    )
    require(
        local_results.get("blockers_closed_by_fixture_dry_run") == 0,
        "fixture dry-run must close zero blockers",
    )
    for flag in [
        "production_identity_provider_available",
        "oauth_oidc_available",
        "rbac_available",
        "production_auth_ready",
        "external_calls_made",
        "identity_provider_contacted",
        "jwks_fetched",
        "tokens_validated_in_production",
        "production_auth_enabled",
        "rbac_enforced_in_production",
    ]:
        require(local_results.get(flag) is False, f"local result {flag} must be false")

    readiness = evaluate_production_auth_evidence(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    for flag in [
        "production_identity_provider_available",
        "oauth_oidc_available",
        "rbac_available",
        "production_auth_ready",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")
    for flag in [
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
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT / "phase_b_product/commercial_readiness/AUTH_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_AUTH_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "auth_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_auth_review_packet",
        "preview_api_key_auth_available: true",
        "rbac_policy_template_available: true",
        "role_matrix_reviewed: true",
        "tenant_role_boundary_reviewed: true",
        "production_identity_provider_available: false",
        "oauth_oidc_available: false",
        "rbac_available: false",
        "production_auth_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/AUTH_EVIDENCE_RUNNER_V0_1.md",
        "/docs/strategy/SAEE_AUTH_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/auth_evidence/README.md",
        "/phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json",
        "/scripts/saee_auth_evidence_runner.py",
        "/scripts/saee_auth_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("auth_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "auth_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_auth_review_packet",
        "preview_api_key_auth_available": True,
        "rbac_policy_template_available": True,
        "role_matrix_reviewed": True,
        "tenant_role_boundary_reviewed": True,
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
        "blockers_closed_by_default": 0,
    }
    for flag, expected_value in expected.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index {flag} must be {expected_value}",
        )

    print(
        "SAEE_AUTH_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "production_auth_ready=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
