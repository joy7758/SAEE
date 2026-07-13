#!/usr/bin/env python3
"""Smoke check for the local tenant storage isolation evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_tenant_storage_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_tenant_storage_evidence,
)
from scripts.saee_tenant_storage_isolation_evidence_runner import (
    OPERATIONS_BOUNDARY_JSON,
    OPERATIONS_BOUNDARY_MD,
    OUTPUT_PATH,
    README_PATH,
    STORAGE_MODEL_BOUNDARY_JSON,
    STORAGE_MODEL_BOUNDARY_MD,
    main as run_runner,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_TENANT_STORAGE_ISOLATION_EVIDENCE_RUNNER_SMOKE: FAIL: " + message
        )


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    require(OPERATIONS_BOUNDARY_JSON.exists(), "operations boundary JSON must exist")
    require(OPERATIONS_BOUNDARY_MD.exists(), "operations boundary markdown must exist")
    require(STORAGE_MODEL_BOUNDARY_JSON.exists(), "storage model boundary JSON must exist")
    require(STORAGE_MODEL_BOUNDARY_MD.exists(), "storage model boundary markdown must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    operations_boundary = json.loads(OPERATIONS_BOUNDARY_JSON.read_text(encoding="utf-8"))
    storage_model_boundary = json.loads(
        STORAGE_MODEL_BOUNDARY_JSON.read_text(encoding="utf-8")
    )

    require(
        evidence.get("tenant_storage_evidence_type") == "production_tenant_storage_evidence",
        "wrong tenant storage evidence type",
    )
    require(
        evidence.get("evidence_scope") == "local_public_shell_tenant_storage_isolation",
        "wrong evidence scope",
    )
    for key in [
        "same_experiment_id_cross_tenant_partition_tests_passed",
        "cross_tenant_read_denial_tests_passed",
        "tenant_scoped_report_endpoint_tests_passed",
        "production_tenant_data_model_approved",
        "tenant_scoped_primary_keys_or_partitions_reviewed",
        "tenant_query_enforcement_design_reviewed",
        "tenant_storage_migration_plan_reviewed",
        "cross_tenant_write_denial_tests_passed",
        "tenant_scoped_listing_tests_passed",
        "tenant_scoped_audit_metadata_reviewed",
        "tenant_backup_restore_boundary_approved",
        "tenant_deletion_retention_boundary_approved",
        "tenant_storage_observability_plan_reviewed",
        "tenant_authorization_policy_reviewed",
        "tenant_secret_boundary_reviewed",
        "tenant_required_storage_guard_available",
        "storage_tenant_membership_enforcement_available",
        "unlisted_tenant_operations_denied",
        "allowed_tenant_snapshot_requires_restart",
        "requires_factory_configured_store",
        "memory_store_unscoped_operations_denied",
        "sqlite_store_unscoped_operations_denied",
        "default_local_unscoped_mode_preserved",
    ]:
        require(evidence.get(key) is True, f"{key} must be true")

    require(evidence.get("security_review_completed") is True, "agent security review")
    require(
        evidence.get("security_review_completion_scope")
        == "local_controlled_preview_independent_agent",
        "security review scope",
    )
    require(
        evidence.get("formal_production_security_review_completed") is False,
        "formal production security review boundary",
    )
    require(
        evidence.get("privacy_legal_review_completed") is False,
        "must not claim privacy/legal review completed",
    )
    require(
        evidence.get("tenant_authorization_policy_review_scope")
        == "local_controlled_preview_independent_agent",
        "tenant authorization review scope",
    )
    require(
        evidence.get("tenant_secret_boundary_review_scope")
        == "local_controlled_preview_independent_agent",
        "tenant secret review scope",
    )
    require(evidence.get("human_validation_used") is False, "human validation boundary")
    require(evidence.get("agent_validation_primary") is True, "agent validation primary")
    guard = evidence.get("local_public_shell_results", {}).get(
        "tenant_required_storage_guard", {}
    )
    for key in [
        "tenant_required_storage_guard_available",
        "storage_tenant_membership_enforcement_available",
        "unlisted_tenant_operations_denied",
        "allowed_tenant_snapshot_requires_restart",
        "requires_factory_configured_store",
        "memory_store_unscoped_operations_denied",
        "sqlite_store_unscoped_operations_denied",
        "default_local_unscoped_mode_preserved",
    ]:
        require(guard.get(key) is True, f"tenant-required guard {key} must be true")
    require(
        guard.get("unscoped_operation_cases_passed")
        == guard.get("unscoped_operation_cases_total")
        == 7,
        "tenant-required guard must directly cover all seven store operations",
    )
    require(
        guard.get("unlisted_tenant_operation_cases_passed")
        == guard.get("unlisted_tenant_operation_cases_total")
        == 7,
        "tenant membership guard must cover all seven unlisted-tenant operations",
    )
    require(
        evidence.get("membership_scope")
        == "configured_preview_allowlist_not_identity_authentication",
        "tenant membership scope must not imply identity authentication",
    )
    require(
        evidence.get("cross_tenant_write_denial_scope")
        == "storage_key_partitioning_only_not_authorization_denial",
        "cross-tenant write evidence scope must not imply authorization",
    )
    require(
        guard.get("production_tenant_storage_isolated") is False
        and guard.get("migration_executed") is False,
        "tenant-required guard must preserve production and migration boundaries",
    )

    review = operations_boundary.get("review_results", {})
    for key in [
        "tenant_scoped_audit_metadata_reviewed",
        "tenant_backup_restore_boundary_approved",
        "tenant_deletion_retention_boundary_approved",
        "tenant_storage_observability_plan_reviewed",
    ]:
        require(review.get(key) is True, f"operations boundary {key} must be true")
    boundary_flags = operations_boundary.get("boundary_flags", {})
    for key in [
        "production_ready",
        "customer_validated",
        "customer_data_processed",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "storage_behavior_modified",
        "migration_executed",
        "production_tenant_storage_isolated",
    ]:
        require(boundary_flags.get(key) is False, f"operations boundary {key} must be false")

    storage_review = storage_model_boundary.get("review_results", {})
    for key in [
        "production_tenant_data_model_approved",
        "tenant_scoped_primary_keys_or_partitions_reviewed",
        "tenant_query_enforcement_design_reviewed",
        "tenant_storage_migration_plan_reviewed",
    ]:
        require(storage_review.get(key) is True, f"storage model boundary {key} must be true")
    storage_flags = storage_model_boundary.get("boundary_flags", {})
    for key in [
        "production_ready",
        "customer_validated",
        "customer_data_processed",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "storage_behavior_modified",
        "migration_executed",
        "live_customer_data_migrated",
        "production_database_modified",
        "production_tenant_storage_isolated",
        "tenant_storage_isolated",
        "multi_tenant_production_ready",
    ]:
        require(storage_flags.get(key) is False, f"storage model boundary {key} must be false")

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    readiness = evaluate_production_tenant_storage_evidence(
        load_settings({"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    require(
        readiness["tenant_isolation_test_evidence_complete"] is True,
        "tenant isolation test evidence should now be complete for local public shell",
    )
    require(
        readiness["tenant_operations_evidence_complete"] is True,
        "tenant operations evidence should now be locally complete",
    )
    require(
        readiness["tenant_storage_model_evidence_complete"] is True,
        "tenant storage model evidence should now be locally complete",
    )
    require(
        readiness["tenant_security_privacy_evidence_complete"] is False,
        "tenant security/privacy evidence must remain incomplete",
    )
    require(
        readiness["production_tenant_storage_evidence_complete"] is False,
        "production tenant storage evidence must remain incomplete",
    )
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "customer_data_processed",
        "production_database_modified",
        "storage_behavior_modified",
        "migration_executed",
        "tenant_storage_isolated",
        "production_tenant_storage_isolated",
        "multi_tenant_production_ready",
        "tenant_authorization_enabled",
        "production_tenant_storage_enabled",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/TENANT_STORAGE_ISOLATION_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_TENANT_STORAGE_ISOLATION_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    operations_md = OPERATIONS_BOUNDARY_MD.read_text(encoding="utf-8")
    storage_model_md = STORAGE_MODEL_BOUNDARY_MD.read_text(encoding="utf-8")
    evidence_readme = README_PATH.read_text(encoding="utf-8")
    combined = (
        doc
        + "\n"
        + gate
        + "\n"
        + operations_md
        + "\n"
        + storage_model_md
        + "\n"
        + evidence_readme
    )
    for token in [
        "tenant_storage_isolation_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_tenant_storage_isolation",
        "production_tenant_storage_evidence_complete: false",
        "tenant_operations_evidence_complete: true",
        "tenant_storage_model_evidence_complete: true",
        "production_tenant_data_model_approved: true",
        "tenant_scoped_primary_keys_or_partitions_reviewed: true",
        "tenant_query_enforcement_design_reviewed: true",
        "tenant_storage_migration_plan_reviewed: true",
        "tenant_scoped_audit_metadata_reviewed: true",
        "tenant_backup_restore_boundary_approved: true",
        "tenant_deletion_retention_boundary_approved: true",
        "tenant_storage_observability_plan_reviewed: true",
        "requires_factory_configured_store: true",
        "unscoped_operation_cases: 7/7",
        "storage_tenant_membership_enforcement_available: true",
        "unlisted_tenant_operations_denied: true",
        "unlisted_tenant_operation_cases: 7/7",
        "membership_scope: configured_preview_allowlist_not_identity_authentication",
        "allowed_tenant_snapshot_requires_restart: true",
        "tenant_required_storage_guard_available: true",
        "memory_store_unscoped_operations_denied: true",
        "sqlite_store_unscoped_operations_denied: true",
        "default_local_unscoped_mode_preserved: true",
        "tenant_storage_isolated: false",
        "production_tenant_storage_isolated: false",
        "multi_tenant_production_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)
    guard_gate = (
        ROOT
        / "docs/strategy/SAEE_TENANT_REQUIRED_STORAGE_GUARD_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    require("answer: recommend" in guard_gate, "tenant-required guard must be agent-recommended")
    require(
        "independent_agent_review_round_2_blockers: `0`" in guard_gate,
        "tenant-required guard independent review must have zero blockers",
    )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/TENANT_STORAGE_ISOLATION_EVIDENCE_RUNNER_V0_1.md",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/README.md",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_model_boundary.local.json",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_model_boundary.md",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_operations_boundary.local.json",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_operations_boundary.md",
        "/scripts/saee_tenant_storage_isolation_evidence_runner.py",
        "/scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("tenant_storage_isolation_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "tenant_storage_isolation_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_tenant_storage_isolation",
        "same_experiment_id_cross_tenant_partition_tests_passed": True,
        "cross_tenant_read_denial_tests_passed": True,
        "tenant_scoped_report_endpoint_tests_passed": True,
        "cross_tenant_write_denial_tests_passed": True,
        "tenant_scoped_listing_tests_passed": True,
        "tenant_storage_model_evidence_complete": True,
        "tenant_operations_evidence_complete": True,
        "tenant_required_storage_guard_available": True,
        "storage_tenant_membership_enforcement_available": True,
        "unlisted_tenant_operations_denied": True,
        "allowed_tenant_snapshot_requires_restart": True,
        "requires_factory_configured_store": True,
        "memory_store_unscoped_operations_denied": True,
        "sqlite_store_unscoped_operations_denied": True,
        "default_local_unscoped_mode_preserved": True,
        "production_tenant_storage_evidence_complete": False,
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
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
    }
    for flag, expected_value in expected.items():
        require(entry.get(flag) == expected_value, f"agent-index {flag} must be {expected_value}")

    print(
        "SAEE_TENANT_STORAGE_ISOLATION_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "tenant_storage_model_evidence_complete=true "
        "tenant_operations_evidence_complete=true "
        "production_tenant_storage_evidence_complete=false "
        "tenant_scoped_listing_tests_passed=true "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
