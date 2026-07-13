#!/usr/bin/env python3
"""Smoke check for the SAEE production-auth evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_auth_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_production_auth_evidence_path.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRODUCTION_AUTH_EVIDENCE_PATH_SMOKE: FAIL: " + message)


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    run = subprocess.run(
        [sys.executable, str(RUNNER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    result = json.loads(run.stdout)
    require(result["production_auth_evidence_path_v0_1"] is True, "path flag true")
    require(
        result["path_type"] == "local_fixture_only_production_auth_evidence_path",
        "path type changed",
    )
    require(result["path_status"] == "pass_fixture_only", "fixture path must pass")
    require(result["fixture_only"] is True, "fixture only true")
    require(
        result["real_identity_provider_selected"] is False,
        "real IdP selection false",
    )
    require(
        result["real_oauth_oidc_flow_approved"] is False,
        "real OAuth/OIDC approval false",
    )
    require(result["real_rbac_policy_approved"] is False, "real RBAC approval false")
    require(
        result["real_production_tokens_validated"] is False,
        "real production token validation false",
    )
    require(result["auth_readiness_status_after_fixture"] == "pass", "auth pass")
    require(
        result["auth_evidence_production_identity_provider_available"] is True,
        "IdP evidence true in fixture",
    )
    require(
        result["auth_evidence_oauth_oidc_available"] is True,
        "OAuth/OIDC evidence true in fixture",
    )
    require(
        result["auth_evidence_rbac_available"] is True,
        "RBAC evidence true in fixture",
    )
    require(
        result["auth_evidence_production_auth_ready"] is True,
        "production auth ready for fixture evidence",
    )
    require(
        result["production_auth_blocker_path_proven"] is True,
        "auth path proven",
    )
    require(
        result["auth_target_blockers_satisfied_count_after_fixture"] == 3,
        "three auth target blockers satisfied by fixture",
    )
    require(result["commercial_status_after_fixture"] == "hold", "commercial hold")
    require(result["production_launch_status_after_fixture"] == "hold", "launch hold")
    require(
        result["production_blocker_count_after_fixture"] == 21,
        "go/no-go leaves 21 blockers",
    )
    require(result["blockers_closed_by_path"] == 0, "path closes no blockers")
    for key in [
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
        "external_model_api_called",
        "external_ai_assistant_tested",
        "customer_contacted",
        "identity_provider_contacted",
        "identity_provider_contacted_by_codex",
        "jwks_fetched",
        "jwks_fetched_by_codex",
        "tokens_validated_in_production",
        "production_tokens_validated_by_codex",
        "production_auth_enabled",
        "rbac_enforced_in_production",
        "production_auth_claim_published",
    ]:
        require(result[key] is False, f"{key} must be false")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    persisted = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    require(persisted == result, "persisted output differs")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "production_auth_evidence_path_v0_1: true",
        "path_type: local_fixture_only_production_auth_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_identity_provider_selected: false",
        "real_oauth_oidc_flow_approved: false",
        "real_rbac_policy_approved: false",
        "real_production_tokens_validated: false",
        "auth_evidence_production_identity_provider_available: true",
        "auth_evidence_oauth_oidc_available: true",
        "auth_evidence_rbac_available: true",
        "auth_evidence_production_auth_ready: true",
        "production_auth_blocker_path_proven: true",
        "auth_target_blockers_satisfied_count_after_fixture: 3",
        "production_blocker_count_after_fixture: 21",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_auth_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_identity_provider_contact: false",
        "recommend_for_jwks_fetch: false",
        "recommend_for_production_token_validation: false",
        "recommend_for_production_auth_enablement: false",
        "recommend_for_production_rbac_enforcement: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)
    for token in [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "real_identity_provider_selected: true",
        "\"real_identity_provider_selected\": true",
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
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_identity_provider_contact: true",
        "recommend_for_jwks_fetch: true",
        "recommend_for_production_token_validation: true",
        "recommend_for_production_auth_enablement: true",
        "recommend_for_production_rbac_enforcement: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_AUTH_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/auth_evidence/production_auth_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/auth_evidence/production_auth_evidence_path_report.md",
        "/docs/strategy/SAEE_PRODUCTION_AUTH_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_auth_evidence_path.py",
        "/scripts/saee_production_auth_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_auth_evidence_path_v0_1", {})
    expected = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_production_auth_evidence_path",
        "fixture_only": True,
        "real_identity_provider_selected": False,
        "real_oauth_oidc_flow_approved": False,
        "real_rbac_policy_approved": False,
        "real_production_tokens_validated": False,
        "production_auth_blocker_path_proven": True,
        "auth_evidence_production_identity_provider_available": True,
        "auth_evidence_oauth_oidc_available": True,
        "auth_evidence_rbac_available": True,
        "auth_evidence_production_auth_ready": True,
        "auth_target_blockers_satisfied_count_after_fixture": 3,
        "production_blocker_count_after_fixture": 21,
        "blockers_closed_by_path": 0,
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
        require(
            entry.get(key) == expected_value,
            f"agent-index production_auth_evidence_path_v0_1 {key} mismatch",
        )

    print(
        "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH_SMOKE: PASS "
        "path_status=pass_fixture_only production_auth_blocker_path_proven=true "
        "production_blocker_count_after_fixture=21 blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
