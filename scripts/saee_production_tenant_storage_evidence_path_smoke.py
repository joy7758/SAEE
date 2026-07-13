#!/usr/bin/env python3
"""Smoke check for the SAEE production tenant-storage evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_tenant_storage_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_production_tenant_storage_evidence_path.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_SMOKE: FAIL: " + message
        )


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
    require(
        result["production_tenant_storage_evidence_path_v0_1"] is True,
        "path flag true",
    )
    require(
        result["path_type"]
        == "local_fixture_only_production_tenant_storage_evidence_path",
        "path type changed",
    )
    require(result["path_status"] == "pass_fixture_only", "fixture path must pass")
    require(result["fixture_only"] is True, "fixture only true")
    require(
        result["real_tenant_storage_design_approved"] is False,
        "real tenant storage design approval false",
    )
    require(
        result["real_cross_tenant_tests_run_in_production"] is False,
        "real production cross-tenant tests false",
    )
    require(
        result["real_tenant_operations_approved"] is False,
        "real tenant operations approval false",
    )
    require(
        result["real_security_privacy_reviews_completed"] is False,
        "real security/privacy reviews false",
    )
    require(
        result["real_customer_data_processing_approved"] is False,
        "real customer data processing approval false",
    )
    require(
        result["tenant_storage_readiness_status_after_fixture"] == "pass",
        "tenant storage readiness pass",
    )
    require(
        result["tenant_storage_evidence_model_complete_after_fixture"] is True,
        "model evidence true in fixture",
    )
    require(
        result["tenant_storage_evidence_isolation_complete_after_fixture"] is True,
        "isolation evidence true in fixture",
    )
    require(
        result["tenant_storage_evidence_operations_complete_after_fixture"] is True,
        "operations evidence true in fixture",
    )
    require(
        result["tenant_storage_evidence_security_privacy_complete_after_fixture"]
        is True,
        "security/privacy evidence true in fixture",
    )
    require(
        result["tenant_storage_evidence_complete_after_fixture"] is True,
        "tenant storage evidence complete in fixture",
    )
    require(
        result["tenant_storage_blocker_path_proven"] is True,
        "tenant storage path proven",
    )
    require(
        result["tenant_storage_target_blockers_satisfied_count_after_fixture"] == 1,
        "one tenant storage target blocker satisfied by fixture",
    )
    require(result["commercial_status_after_fixture"] == "hold", "commercial hold")
    require(result["production_launch_status_after_fixture"] == "hold", "launch hold")
    require(
        result["production_blocker_count_after_fixture"] == 23,
        "go/no-go leaves 23 blockers",
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
        "production_tenant_storage_evidence_path_v0_1: true",
        "path_type: local_fixture_only_production_tenant_storage_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_tenant_storage_design_approved: false",
        "real_cross_tenant_tests_run_in_production: false",
        "real_tenant_operations_approved: false",
        "real_security_privacy_reviews_completed: false",
        "real_customer_data_processing_approved: false",
        "tenant_storage_readiness_status_after_fixture: pass",
        "tenant_storage_evidence_model_complete_after_fixture: true",
        "tenant_storage_evidence_isolation_complete_after_fixture: true",
        "tenant_storage_evidence_operations_complete_after_fixture: true",
        "tenant_storage_evidence_security_privacy_complete_after_fixture: true",
        "tenant_storage_evidence_complete_after_fixture: true",
        "tenant_storage_blocker_path_proven: true",
        "tenant_storage_target_blockers_satisfied_count_after_fixture: 1",
        "production_blocker_count_after_fixture: 23",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_tenant_storage_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_storage_behavior_change: false",
        "recommend_for_migration_execution: false",
        "recommend_for_customer_data_processing: false",
        "recommend_for_production_tenant_storage_enablement: false",
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
        "real_tenant_storage_design_approved: true",
        "\"real_tenant_storage_design_approved\": true",
        "real_cross_tenant_tests_run_in_production: true",
        "\"real_cross_tenant_tests_run_in_production\": true",
        "real_customer_data_processing_approved: true",
        "\"real_customer_data_processing_approved\": true",
        "storage_behavior_modified: true",
        "\"storage_behavior_modified\": true",
        "migration_executed: true",
        "\"migration_executed\": true",
        "production_database_modified: true",
        "\"production_database_modified\": true",
        "customer_data_processed: true",
        "\"customer_data_processed\": true",
        "tenant_storage_isolated: true",
        "\"tenant_storage_isolated\": true",
        "production_tenant_storage_isolated: true",
        "\"production_tenant_storage_isolated\": true",
        "multi_tenant_production_ready: true",
        "\"multi_tenant_production_ready\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_storage_behavior_change: true",
        "recommend_for_migration_execution: true",
        "recommend_for_customer_data_processing: true",
        "recommend_for_production_tenant_storage_enablement: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/production_tenant_storage_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/production_tenant_storage_evidence_path_report.md",
        "/docs/strategy/SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_tenant_storage_evidence_path.py",
        "/scripts/saee_production_tenant_storage_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_tenant_storage_evidence_path_v0_1", {})
    expected = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_production_tenant_storage_evidence_path",
        "fixture_only": True,
        "real_tenant_storage_design_approved": False,
        "real_cross_tenant_tests_run_in_production": False,
        "real_tenant_operations_approved": False,
        "real_security_privacy_reviews_completed": False,
        "real_customer_data_processing_approved": False,
        "tenant_storage_blocker_path_proven": True,
        "tenant_storage_evidence_model_complete_after_fixture": True,
        "tenant_storage_evidence_isolation_complete_after_fixture": True,
        "tenant_storage_evidence_operations_complete_after_fixture": True,
        "tenant_storage_evidence_security_privacy_complete_after_fixture": True,
        "tenant_storage_evidence_complete_after_fixture": True,
        "tenant_storage_target_blockers_satisfied_count_after_fixture": 1,
        "production_blocker_count_after_fixture": 23,
        "blockers_closed_by_path": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "customer_data_processed": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
    }
    for flag, expected_value in expected.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index production_tenant_storage_evidence_path_v0_1 {flag} must be {expected_value}",
        )

    print("SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH_SMOKE: PASS")


if __name__ == "__main__":
    main()
