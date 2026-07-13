#!/usr/bin/env python3
"""Smoke check for the Phase 1 identity/tenant evidence profile."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_phase1_identity_tenant_evidence_builder import (
    ALL_EVIDENCE_KEYS,
    INPUT_FORBIDDEN_TRUE_KEYS,
    build_from_input,
)
from scripts.saee_phase1_identity_tenant_evidence_profile import (
    DEFAULT_PROFILE_JSON,
    DOC_PATH,
    GATE_PATH,
    OUTPUT_DIR,
    README_PATH,
    TARGET_BLOCKERS,
    build_profile,
)


PROFILE_SCRIPT = ROOT / "scripts/saee_phase1_identity_tenant_evidence_profile.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_PROFILE_SMOKE: FAIL: " + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    evidence_review = {key: True for key in ALL_EVIDENCE_KEYS}
    source_notes = {
        key: f"Human-reviewed production evidence note for {key}."
        for key in ALL_EVIDENCE_KEYS
    }
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "phase_1_identity_tenant_evidence_input_v0_1": True,
        "input_status": "human_filled_fixture_for_profile_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-04",
        "evidence_source_notes": "Fixture-only complete input for deterministic smoke validation.",
        "evidence_review": evidence_review,
        "source_notes_by_key": source_notes,
        "boundary_review": boundary_review,
        "codex_inferred_missing_evidence": False,
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "codex_ran_storage_migration": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "storage_migration_executed": False,
        "customer_data_processed": False,
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
    }


def require_boundary_false(payload: dict[str, object]) -> None:
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
        "landing_page_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "customer_contacted",
        "identity_provider_contacted_by_codex",
        "jwks_fetched_by_codex",
        "production_tokens_validated_by_codex",
        "storage_migration_executed",
        "customer_data_processed",
        "codex_inferred_missing_evidence",
    ]:
        require(payload.get(key) is False, f"{key} must be false")


def main() -> None:
    require(PROFILE_SCRIPT.exists(), "profile script missing")
    default_run = subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_profile = json.loads(default_run.stdout)
    require(DEFAULT_PROFILE_JSON.exists(), "default profile JSON missing")
    require(
        default_profile["profile_type"] == "saee_phase_1_identity_tenant_evidence_profile",
        "wrong profile_type",
    )
    require(
        default_profile["profile_scope"]
        == "local_phase_1_builder_outputs_to_go_no_go_profile",
        "wrong profile_scope",
    )
    require(default_profile["builder_status"] == "hold", "default builder status hold")
    require(default_profile["profile_status"] == "hold", "default profile status hold")
    require(default_profile["auth_readiness_status"] == "hold", "default auth hold")
    require(
        default_profile["tenant_storage_readiness_status"] == "hold",
        "default tenant storage hold",
    )
    require(default_profile["commercial_status"] == "hold", "default commercial hold")
    require(
        default_profile["production_launch_status"] == "hold",
        "default production launch hold",
    )
    require(
        default_profile["phase_1_target_blockers_satisfied_count"] == 0,
        "default satisfies no Phase 1 blockers",
    )
    require(
        default_profile["phase_1_blockers_closed_by_profile"] == 0,
        "default closes no Phase 1 blockers",
    )
    require(default_profile["blockers_closed_by_profile"] == 0, "closes no blockers")
    require(
        default_profile["would_satisfy_phase_1_if_complete"] is False,
        "default not Phase 1 complete",
    )
    require(default_profile["target_blocker_ids"] == TARGET_BLOCKERS, "target blockers")
    require(
        default_profile["development_permission_granted_for_local_scope"] is True,
        "local development authorized",
    )
    require(
        default_profile["sanitized_local_evidence_collection_authorized"] is True,
        "sanitized evidence authorized",
    )
    require(default_profile["production_deployment_authorized"] is False, "production deploy denied")
    require(default_profile["production_data_migration_authorized"] is False, "migration denied")
    require(
        default_profile["rbac_role_permission_consistency_enforced"] is True,
        "RBAC consistency enforced",
    )
    require(
        default_profile["rbac_consistency_negative_cases_passed"]
        == default_profile["rbac_consistency_negative_cases_total"]
        == 5,
        "RBAC negative cases",
    )
    require(
        default_profile["tenant_required_storage_guard_available"] is True,
        "tenant-required storage guard available",
    )
    require(
        default_profile["memory_store_unscoped_operations_denied"] is True
        and default_profile["sqlite_store_unscoped_operations_denied"] is True,
        "tenant-required stores deny unscoped operations",
    )
    require(
        default_profile["default_local_unscoped_mode_preserved"] is True,
        "default local mode preserved",
    )
    require(
        default_profile["storage_tenant_membership_enforcement_available"] is True
        and default_profile["unlisted_tenant_operations_denied"] is True,
        "storage tenant membership enforcement",
    )
    require(
        default_profile["unlisted_tenant_operation_cases_passed"]
        == default_profile["unlisted_tenant_operation_cases_total"]
        == 7,
        "storage tenant membership negative cases",
    )
    require(
        default_profile["membership_scope"]
        == "configured_preview_allowlist_not_identity_authentication",
        "storage tenant membership scope",
    )
    require(default_profile["tenant_secret_boundary_available"] is True, "tenant secret boundary")
    require(
        default_profile["tenant_secret_boundary_negative_cases_passed"]
        == default_profile["tenant_secret_boundary_negative_cases_total"]
        == 24,
        "tenant secret boundary negative cases",
    )
    require(default_profile["tenant_secret_boundary_secret_echo_count"] == 0, "tenant secret echo")
    require(default_profile["tenant_secret_boundary_profile_reviewed"] is False, "tenant secret raw profile review")
    require(default_profile["tenant_secret_boundary_reviewed"] is True, "tenant secret agent review")
    require(default_profile["production_secrets_management_available"] is False, "production secret manager")
    require(default_profile["encryption_at_rest_proven"] is False, "encryption at rest")
    require(default_profile["kms_hsm_available"] is False, "KMS HSM")
    require(default_profile["bound_tenant_authorization_available"] is True, "bound tenant auth")
    require(
        default_profile["bound_tenant_authorization_negative_cases_passed"]
        == default_profile["bound_tenant_authorization_negative_cases_total"]
        == 14,
        "bound tenant auth cases",
    )
    require(default_profile["context_capability_hmac_verified"] is True, "auth capability")
    require(default_profile["storage_operation_permission_bound"] is True, "auth permission")
    require(default_profile["tenant_authorization_profile_policy_reviewed"] is False, "tenant auth raw profile review")
    require(default_profile["tenant_authorization_policy_reviewed"] is True, "tenant auth agent review")
    require(default_profile["security_review_completed"] is True, "tenant security agent review")
    require(default_profile["agent_privacy_boundary_review_completed"] is True, "tenant privacy boundary review")
    require(default_profile["privacy_legal_review_completed"] is False, "privacy legal boundary")
    require(default_profile["human_validation_used"] is False, "human validation boundary")
    require(default_profile["agent_validation_primary"] is True, "agent validation primary")
    require(default_profile["tenant_authorization_enabled"] is False, "tenant auth production")
    require_boundary_false(default_profile)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_input_path = tmp / "complete_input.json"
        complete_builder_path = tmp / "complete_builder_output.json"
        complete_auth_path = tmp / "complete_auth.json"
        complete_tenant_path = tmp / "complete_tenant.json"
        unsafe_input_path = tmp / "unsafe_input.json"
        unsafe_builder_path = tmp / "unsafe_builder_output.json"
        unsafe_auth_path = tmp / "unsafe_auth.json"
        unsafe_tenant_path = tmp / "unsafe_tenant.json"

        write_json(complete_input_path, complete_input())
        write_json(unsafe_input_path, complete_input(unsafe=True))
        build_from_input(
            complete_input_path,
            complete_builder_path,
            complete_auth_path,
            complete_tenant_path,
        )
        build_from_input(
            unsafe_input_path,
            unsafe_builder_path,
            unsafe_auth_path,
            unsafe_tenant_path,
        )
        complete_profile = build_profile(complete_builder_path)
        unsafe_profile = build_profile(unsafe_builder_path)

    require(complete_profile["builder_status"] == "pass", "complete builder pass")
    require(complete_profile["profile_status"] == "pass", "complete profile pass")
    require(complete_profile["auth_readiness_status"] == "pass", "complete auth pass")
    require(
        complete_profile["tenant_storage_readiness_status"] == "pass",
        "complete tenant pass",
    )
    require(
        complete_profile["phase_1_target_blockers_satisfied_count"] == 4,
        "complete profile satisfies 4 Phase 1 blockers",
    )
    require(
        complete_profile["phase_1_target_blockers_satisfied"] == TARGET_BLOCKERS,
        "complete profile target blocker IDs",
    )
    require(
        complete_profile["would_satisfy_phase_1_if_complete"] is True,
        "complete profile would satisfy Phase 1",
    )
    require(
        complete_profile["production_launch_status"] == "hold",
        "complete Phase 1 still not production launch",
    )
    require(
        complete_profile["production_blocker_count"] >= 20,
        "other production blockers must remain",
    )
    require(complete_profile["phase_1_blockers_closed_by_profile"] == 0, "no closure")
    require_boundary_false(complete_profile)

    require(unsafe_profile["builder_status"] == "stop", "unsafe builder stop")
    require(unsafe_profile["profile_status"] == "stop", "unsafe profile stop")
    require(
        unsafe_profile["would_satisfy_phase_1_if_complete"] is False,
        "unsafe cannot satisfy Phase 1",
    )
    require_boundary_false(unsafe_profile)

    for path in [
        OUTPUT_DIR / "README.md",
        OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.local.json",
        OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.md",
        OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.env.example",
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.exists(), f"{path.relative_to(ROOT)} missing")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            OUTPUT_DIR / "README.md",
            OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.md",
            DOC_PATH,
            GATE_PATH,
        ]
    )
    for token in [
        "phase_1_identity_tenant_evidence_profile_v0_1: true",
        "profile_scope: local_phase_1_builder_outputs_to_go_no_go_profile",
        "default_profile_status: hold",
        "phase_1_blockers_closed_by_profile: 0",
        "blockers_closed_by_profile: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_phase_1_go_no_go_precheck: true",
        "recommend_for_blocker_closure: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
        "phase_1_blockers_closed_by_profile: 1",
        '"phase_1_blockers_closed_by_profile": 1',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_PROFILE_V0_1.md",
        "/docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/README.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.env.example",
        "/scripts/saee_phase1_identity_tenant_evidence_profile.py",
        "/scripts/saee_phase1_identity_tenant_evidence_profile_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("phase_1_identity_tenant_evidence_profile_v0_1", {})
    expected_entry = {
        "status": "local_phase_1_go_no_go_profile_default_hold",
        "phase_1_identity_tenant_evidence_profile_v0_1": True,
        "profile_scope": "local_phase_1_builder_outputs_to_go_no_go_profile",
        "default_profile_status": "hold",
        "phase_1_target_blockers_satisfied_count": 0,
        "phase_1_blockers_closed_by_profile": 0,
        "blockers_closed_by_profile": 0,
        "production_launch_status": "hold",
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "storage_migration_executed": False,
        "customer_data_processed": False,
    }
    for key, expected_value in expected_entry.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_PROFILE_SMOKE: PASS "
        "default_hold=true complete_fixture_phase1_pass=true unsafe_fixture_stop=true "
        "phase_1_blockers_closed_by_profile=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
