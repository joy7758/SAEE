#!/usr/bin/env python3
"""Smoke check for SAEE Production Tenant Storage Isolation Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_V0_1.json"
)
MD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(
        data["production_tenant_storage_isolation_requirements_v0_1"] is True,
        "requirements flag true",
    )
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")

    false_flags = [
        "production_tenant_storage_isolation_implemented",
        "tenant_storage_isolated",
        "production_tenant_storage_isolated",
        "tenant_authorization_policy_available",
        "tenant_billing_isolated",
        "multi_tenant_production_ready",
        "customer_data_processing_ready",
        "production_database_ready",
        "tenant_backup_restore_available",
        "tenant_deletion_retention_available",
        "cross_tenant_access_tests_passed",
        "production_tenant_storage_isolation_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "storage_behavior_modified",
    ]
    for flag in false_flags:
        require(data[flag] is False, f"{flag} false")

    blockers = set(data["tenant_blockers_covered_as_requirements"])
    require(blockers == {"tenant_storage_isolation"}, "tenant blockers mismatch")

    required_controls = {
        "production_tenant_data_model_defined",
        "tenant_scoped_primary_keys_or_partitions",
        "tenant_scoped_query_enforcement",
        "cross_tenant_access_denial_tests",
        "tenant_scoped_audit_metadata",
        "tenant_backup_restore_boundary",
        "tenant_deletion_retention_boundary",
        "tenant_storage_migration_plan",
        "tenant_storage_observability_plan",
    }
    require(
        required_controls <= set(data["required_tenant_storage_controls"]),
        "missing tenant storage controls",
    )

    required_evidence = {
        "same_experiment_id_cross_tenant_partition_tests",
        "cross_tenant_read_denial_tests",
        "cross_tenant_write_denial_tests",
        "tenant_scoped_listing_tests",
        "tenant_scoped_report_endpoint_tests",
        "tenant_audit_ownership_tests",
        "tenant_backup_restore_scope_tests",
        "security_review_completed",
        "privacy_legal_review_completed",
    }
    require(
        required_evidence <= set(data["required_tenant_isolation_evidence"]),
        "missing tenant isolation evidence",
    )

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_tenant_storage_isolation_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_tenant_storage_isolation_implemented: false",
        "tenant_storage_isolated: false",
        "production_tenant_storage_isolated: false",
        "tenant_authorization_policy_available: false",
        "tenant_billing_isolated: false",
        "multi_tenant_production_ready: false",
        "customer_data_processing_ready: false",
        "production_database_ready: false",
        "tenant_backup_restore_available: false",
        "tenant_deletion_retention_available: false",
        "cross_tenant_access_tests_passed: false",
        "production_tenant_storage_isolation_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "storage_behavior_modified: false",
        "answer: conditional",
        "recommend_for_requirements_definition: true",
        "recommend_for_storage_implementation: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_tenant_storage_isolation_requirements.py",
        "/scripts/saee_production_tenant_storage_isolation_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_tenant_storage_isolation_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_tenant_storage_isolation_requirements_v0_1": True,
        "production_tenant_storage_isolation_implemented": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "tenant_authorization_policy_available": False,
        "tenant_billing_isolated": False,
        "multi_tenant_production_ready": False,
        "customer_data_processing_ready": False,
        "production_database_ready": False,
        "tenant_backup_restore_available": False,
        "tenant_deletion_retention_available": False,
        "cross_tenant_access_tests_passed": False,
        "production_tenant_storage_isolation_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
        "storage_behavior_modified": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true tenant_storage_isolated=false "
        "multi_tenant_production_ready=false storage_behavior_modified=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
