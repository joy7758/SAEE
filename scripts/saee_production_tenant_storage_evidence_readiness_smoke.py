#!/usr/bin/env python3
"""Smoke check for SAEE Production Tenant Storage Evidence Readiness v0.1."""

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
from saee_backend.services.production_tenant_storage_evidence import (
    evaluate_production_tenant_storage_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_SMOKE: FAIL: " + message
        )


def write_tenant_storage_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "tenant_storage_evidence_type": "production_tenant_storage_evidence",
        "production_tenant_data_model_approved": True,
        "tenant_scoped_primary_keys_or_partitions_reviewed": True,
        "tenant_query_enforcement_design_reviewed": True,
        "tenant_storage_migration_plan_reviewed": True,
        "same_experiment_id_cross_tenant_partition_tests_passed": True,
        "cross_tenant_read_denial_tests_passed": True,
        "cross_tenant_write_denial_tests_passed": True,
        "tenant_scoped_listing_tests_passed": True,
        "tenant_scoped_report_endpoint_tests_passed": True,
        "tenant_scoped_audit_metadata_reviewed": True,
        "tenant_backup_restore_boundary_approved": True,
        "tenant_deletion_retention_boundary_approved": True,
        "tenant_storage_observability_plan_reviewed": True,
        "tenant_authorization_policy_reviewed": True,
        "tenant_secret_boundary_reviewed": True,
        "security_review_completed": True,
        "privacy_legal_review_completed": True,
        "customer_data_processing_non_claim_reviewed": True,
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
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "production_database_modified": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "live_customer_data_migrated": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
        "tenant_authorization_enabled": False,
        "production_tenant_storage_enabled": False,
        "cross_tenant_access_tests_claimed_as_external_validation": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_tenant_storage_evidence(load_settings({}))
    require(
        local["production_tenant_storage_evidence_type"]
        == "production_tenant_storage_evidence_readiness",
        "wrong evidence type",
    )
    require(
        local["production_tenant_storage_evidence_readiness_v0_1"] is True,
        "readiness flag",
    )
    require(local["status"] == "hold", "default evidence status must hold")
    require(
        local["tenant_storage_evidence_path_configured"] is False,
        "default path false",
    )
    for field in [
        "tenant_storage_model_evidence_complete",
        "tenant_isolation_test_evidence_complete",
        "tenant_operations_evidence_complete",
        "tenant_security_privacy_evidence_complete",
        "tenant_storage_isolation_evidence_complete",
        "production_tenant_storage_evidence_complete",
    ]:
        require(local[field] is False, f"default {field} false")
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
        "customer_data_processing_started",
        "production_database_modified",
        "storage_behavior_modified",
        "migration_executed",
        "live_customer_data_migrated",
        "tenant_storage_isolated",
        "production_tenant_storage_isolated",
        "multi_tenant_production_ready",
        "tenant_authorization_enabled",
        "production_tenant_storage_enabled",
    ]:
        require(local[flag] is False, f"default {flag} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "TENANT_STORAGE_EVIDENCE.json"
        write_tenant_storage_evidence(evidence_path)
        settings = load_settings(
            {"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(evidence_path)}
        )
        configured = evaluate_production_tenant_storage_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_TENANT_STORAGE_EVIDENCE.json"
        write_tenant_storage_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_tenant_storage_evidence(
            load_settings(
                {"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(unsafe_path)}
            )
        )

    require(configured["status"] == "pass", "complete evidence should pass")
    for field in [
        "tenant_storage_model_evidence_complete",
        "tenant_isolation_test_evidence_complete",
        "tenant_operations_evidence_complete",
        "tenant_security_privacy_evidence_complete",
        "tenant_storage_isolation_evidence_complete",
        "production_tenant_storage_evidence_complete",
    ]:
        require(configured[field] is True, f"configured {field} true")
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
        "customer_data_processing_started",
        "production_database_modified",
        "storage_behavior_modified",
        "migration_executed",
        "live_customer_data_migrated",
        "tenant_storage_isolated",
        "production_tenant_storage_isolated",
        "multi_tenant_production_ready",
        "tenant_authorization_enabled",
        "production_tenant_storage_enabled",
    ]:
        require(configured[flag] is False, f"configured {flag} false")

    blocked = blocker_ids(go_no_go)
    require(
        "tenant_storage_isolation" not in blocked,
        "tenant storage evidence should close tenant_storage_isolation blocker",
    )
    require(
        go_no_go["tenant_storage_evidence_isolation_complete"] is True,
        "go/no-go must expose tenant storage evidence complete",
    )
    require(
        go_no_go["production_tenant_storage_evidence_status"] == "pass",
        "go/no-go must expose tenant storage evidence pass",
    )
    require(go_no_go["production_launch_status"] == "hold", "launch still hold")
    require(go_no_go["production_ready"] is False, "go/no-go must keep production false")
    require(go_no_go["customer_validated"] is False, "go/no-go must keep customer false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go private core false")

    require(unsafe["status"] == "stop", "unsafe evidence should stop")
    require(
        "production_ready" in unsafe["boundary_violations"],
        "unsafe production_ready violation recorded",
    )

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join([doc, gate])
    required_tokens = [
        "production_tenant_storage_evidence_readiness_v0_1: true",
        "default_status: hold",
        "tenant_storage_evidence_path_configured_default: false",
        "tenant_storage_isolation_evidence_complete_default: false",
        "production_tenant_storage_evidence_complete_default: false",
        "tenant_storage_isolated: false",
        "production_tenant_storage_isolated: false",
        "multi_tenant_production_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "storage_behavior_modified: false",
        "customer_data_processed: false",
        "answer: conditional",
        "recommend_for_tenant_storage_evidence_review: true",
        "recommend_for_storage_implementation: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_tenant_storage_evidence.py",
        "/scripts/saee_production_tenant_storage_evidence_readiness.py",
        "/scripts/saee_production_tenant_storage_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    print(
        "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "tenant_storage_blocker_satisfied_by_evidence=true "
        "production_launch_status=hold production_ready=false "
        "customer_validated=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
