#!/usr/bin/env python3
"""Smoke check for the SAEE production-monitoring evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_monitoring_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_production_monitoring_evidence_path.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRODUCTION_MONITORING_EVIDENCE_PATH_SMOKE: FAIL: " + message)


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
        result["production_monitoring_evidence_path_v0_1"] is True,
        "path flag true",
    )
    require(
        result["path_type"] == "local_fixture_only_production_monitoring_evidence_path",
        "path type changed",
    )
    require(result["path_status"] == "pass_fixture_only", "fixture path must pass")
    require(result["fixture_only"] is True, "fixture only true")
    require(
        result["real_production_monitoring_deployed"] is False,
        "real monitoring deployment false",
    )
    require(result["real_dashboard_configured"] is False, "real dashboard false")
    require(
        result["real_metrics_export_enabled"] is False,
        "real metrics export false",
    )
    require(result["real_log_retention_changed"] is False, "real log retention false")
    require(result["builder_status"] == "pass", "builder pass")
    require(result["builder_input_complete"] is True, "fixture input complete")
    require(
        result["production_monitoring_available_for_review"] is True,
        "production monitoring available in fixture",
    )
    require(
        result["production_monitoring_blocker_path_proven"] is True,
        "production monitoring path proven",
    )
    require(
        result["operations_readiness_status_after_fixture"] == "hold",
        "partial operations readiness should hold",
    )
    require(
        result["operations_readiness_production_monitoring_available"] is True,
        "monitoring readiness true",
    )
    require(
        result["operations_readiness_external_alert_delivery_available"] is False,
        "external alert delivery remains false",
    )
    require(
        result["operations_readiness_on_call_rotation_available"] is False,
        "on-call remains false",
    )
    require(
        result["operations_readiness_production_operations_ready"] is False,
        "production operations remains false",
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
        "alert_provider_contacted",
        "monitoring_vendor_contacted",
        "production_monitoring_deployed",
        "external_alert_delivery_enabled",
        "monitoring_deployed_by_codex",
        "dashboard_configured_by_codex",
        "metrics_export_enabled_by_codex",
        "log_retention_changed_by_codex",
        "monitoring_vendor_contacted_by_codex",
        "alert_provider_contacted_by_codex",
        "support_operations_started",
        "production_monitoring_claim_published",
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
        "production_monitoring_evidence_path_v0_1: true",
        "path_type: local_fixture_only_production_monitoring_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_production_monitoring_deployed: false",
        "production_monitoring_blocker_path_proven: true",
        "operations_readiness_production_monitoring_available: true",
        "operations_readiness_external_alert_delivery_available: false",
        "operations_readiness_on_call_rotation_available: false",
        "operations_readiness_production_operations_ready: false",
        "production_blocker_count_after_fixture: 23",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_monitoring_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_vendor_contact: false",
        "recommend_for_monitoring_deployment: false",
        "recommend_for_support_operations: false",
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
        "real_production_monitoring_deployed: true",
        "\"real_production_monitoring_deployed\": true",
        "production_monitoring_deployed: true",
        "\"production_monitoring_deployed\": true",
        "external_alert_delivery_enabled: true",
        "\"external_alert_delivery_enabled\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "alert_provider_contacted: true",
        "\"alert_provider_contacted\": true",
        "monitoring_vendor_contacted: true",
        "\"monitoring_vendor_contacted\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_vendor_contact: true",
        "recommend_for_monitoring_deployment: true",
        "recommend_for_support_operations: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_MONITORING_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_path_report.md",
        "/docs/strategy/SAEE_PRODUCTION_MONITORING_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_monitoring_evidence_path.py",
        "/scripts/saee_production_monitoring_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_monitoring_evidence_path_v0_1", {})
    expected = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_production_monitoring_evidence_path",
        "fixture_only": True,
        "real_production_monitoring_deployed": False,
        "real_dashboard_configured": False,
        "real_metrics_export_enabled": False,
        "real_log_retention_changed": False,
        "production_monitoring_blocker_path_proven": True,
        "operations_readiness_production_monitoring_available": True,
        "operations_readiness_external_alert_delivery_available": False,
        "operations_readiness_on_call_rotation_available": False,
        "operations_readiness_production_operations_ready": False,
        "production_blocker_count_after_fixture": 23,
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
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "production_monitoring_deployed": False,
        "external_alert_delivery_enabled": False,
        "support_operations_started": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_PRODUCTION_MONITORING_EVIDENCE_PATH_SMOKE: PASS "
        "fixture_only=true production_monitoring_path_proven=true "
        "production_blockers_after_fixture=23 blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
