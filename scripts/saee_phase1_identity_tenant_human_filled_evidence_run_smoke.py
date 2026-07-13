#!/usr/bin/env python3
"""Smoke test the Phase 1 identity/tenant human-filled evidence run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile"
BUILDER_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
AUTH_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"

SUMMARY_PATH = PROFILE_DIR / "phase_1_identity_tenant_human_filled_evidence_run_summary.local.json"
PROFILE_PATH = PROFILE_DIR / "phase_1_identity_tenant_evidence_profile.human_filled.local.json"
REPORT_PATH = PROFILE_DIR / "phase_1_identity_tenant_human_filled_evidence_run_report.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN_GATE.md"

REQUIRED_FILES = [
    SUMMARY_PATH,
    PROFILE_PATH,
    REPORT_PATH,
    GATE_PATH,
    AUTH_DIR / "production_identity_provider_decision_input.human_filled.local.json",
    AUTH_DIR / "production_identity_provider_approval_input_validation.human_filled.local.json",
    AUTH_DIR / "production_identity_provider_approval_input_validation.human_filled.md",
    BUILDER_DIR / "phase_1_identity_tenant_evidence_input.human_filled.local.json",
    BUILDER_DIR / "oauth_oidc_approval_input_validation.human_filled.local.json",
    BUILDER_DIR / "oauth_oidc_approval_input_validation.human_filled.md",
    BUILDER_DIR / "rbac_approval_input_validation.human_filled.local.json",
    BUILDER_DIR / "rbac_approval_input_validation.human_filled.md",
    BUILDER_DIR / "tenant_storage_approval_input_validation.human_filled.local.json",
    BUILDER_DIR / "tenant_storage_approval_input_validation.human_filled.md",
    BUILDER_DIR / "phase_1_identity_tenant_evidence_builder_output.human_filled.local.json",
    BUILDER_DIR / "phase_1_identity_tenant_auth_evidence.human_filled.local.json",
    BUILDER_DIR / "phase_1_identity_tenant_storage_evidence.human_filled.local.json",
]

TARGET_BLOCKERS = [
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
]
REMAINING_BLOCKERS = ["pilot_results", "customer_validated"]

EXPECTED_TRUE = {
    "phase_1_identity_tenant_human_filled_evidence_run_v0_1": True,
    "production_auth_ready": True,
    "production_identity_provider_available": True,
    "oauth_oidc_available": True,
    "rbac_available": True,
    "production_tenant_storage_evidence_complete": True,
    "tenant_storage_isolation_evidence_complete": True,
    "human_review_required": True,
    "separate_human_launch_approval_required": True,
}

EXPECTED_STATUS = {
    "run_status": "pass",
    "validation_status": "pass",
    "idp_validation_status": "pass",
    "oauth_oidc_validation_status": "pass",
    "rbac_validation_status": "pass",
    "tenant_storage_validation_status": "pass",
    "builder_status": "pass",
    "phase_1_profile_status": "pass",
    "auth_readiness_status": "pass",
    "tenant_storage_readiness_status": "pass",
    "commercial_status_after_profile": "hold",
    "production_launch_status_after_profile": "hold",
    "run_type": "local_human_filled_phase_1_identity_tenant_evidence",
}

EXPECTED_FALSE = [
    "production_ready",
    "customer_validated",
    "product_launched",
    "customer_contacted",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "identity_provider_contacted",
    "identity_provider_contacted_by_codex",
    "jwks_fetched",
    "jwks_fetched_by_codex",
    "tokens_validated_in_production",
    "production_tokens_validated_by_codex",
    "production_auth_enabled",
    "rbac_enforced_in_production",
    "storage_migration_executed",
    "migration_executed",
    "customer_data_processed",
    "customer_data_processing_started",
    "tenant_storage_isolated",
    "production_tenant_storage_isolated",
    "production_tenant_storage_enabled",
    "production_database_modified",
    "storage_behavior_modified",
    "task_candidates_executed",
    "development_permission_granted",
]


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_PHASE1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL "
        + message
    )


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - smoke diagnostic
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    summary = read_json(SUMMARY_PATH)
    profile = read_json(PROFILE_PATH)

    for key, value in EXPECTED_STATUS.items():
        if summary.get(key) != value:
            fail(f"summary {key} must be {value}")
    for key, value in EXPECTED_TRUE.items():
        if summary.get(key) is not value:
            fail(f"summary {key} must be {value}")
    for key in EXPECTED_FALSE:
        if summary.get(key) is not False:
            fail(f"summary {key} must be false")

    if summary.get("phase_1_satisfied_blockers") != TARGET_BLOCKERS:
        fail("summary phase_1_satisfied_blockers changed")
    if summary.get("phase_1_target_blockers") != TARGET_BLOCKERS:
        fail("summary phase_1_target_blockers changed")
    if summary.get("phase_1_satisfied_blocker_count") != 4:
        fail("summary phase_1_satisfied_blocker_count must be 4")
    if summary.get("all_evidence_remaining_blockers") != REMAINING_BLOCKERS:
        fail("summary remaining blockers must be pilot_results/customer_validated")
    if summary.get("all_evidence_production_blocker_count") != 2:
        fail("summary all_evidence_production_blocker_count must be 2")
    if summary.get("blockers_closed_by_validator") != 0:
        fail("validator must close zero blockers directly")
    if summary.get("blockers_closed_by_builder") != 0:
        fail("builder must close zero blockers directly")
    if summary.get("blockers_closed_by_profile") != 0:
        fail("profile must close zero blockers directly")
    if summary.get("accepted_for_blocker_closure_count") != 0:
        fail("accepted_for_blocker_closure_count must be 0")

    expected_profile = {
        "profile_status": "pass",
        "auth_readiness_status": "pass",
        "tenant_storage_readiness_status": "pass",
        "auth_production_ready_for_review": True,
        "tenant_storage_production_ready_for_review": True,
        "phase_1_target_blockers_satisfied": TARGET_BLOCKERS,
        "phase_1_target_blockers_satisfied_count": 4,
        "phase_1_target_blockers_unsatisfied": [],
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "customer_contacted": False,
    }
    for key, value in expected_profile.items():
        if profile.get(key) != value:
            fail(f"profile {key} must be {value}")

    for path_value in summary.get("output_files", []):
        output_path = Path(str(path_value))
        if not output_path.is_file():
            fail(f"summary output file does not exist: {path_value}")

    print(
        "SAEE_PHASE1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: PASS "
        "phase_1_profile_status=pass production_blockers=2 production_ready=false"
    )


if __name__ == "__main__":
    main()
