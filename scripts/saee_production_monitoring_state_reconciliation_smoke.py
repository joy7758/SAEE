#!/usr/bin/env python3
"""Smoke test for production-monitoring state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_production_monitoring_state_reconciliation.py"
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/operations_evidence/"
    "production_monitoring_state_reconciliation"
)
SUMMARY = OUT_DIR / "production_monitoring_state_reconciliation.local.json"
REPORT = OUT_DIR / "production_monitoring_state_reconciliation.md"
BOUNDARY = OUT_DIR / "production_monitoring_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_MONITORING_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "production_monitoring_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_production_monitoring_state_reconciliation_no_deploy_no_closure",
        "target_blocker_id": "production_monitoring",
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "approval_input_complete": True,
        "approval_builder_ready": True,
        "builder_output_ready": True,
        "monitoring_evidence_ready_for_review": True,
        "combined_operations_profile_ready": True,
        "production_monitoring_satisfied_by_profile": True,
        "external_alert_delivery_satisfied_by_profile": True,
        "operations_on_call_rotation_satisfied_by_profile": True,
        "monitoring_owner_recorded": True,
        "metrics_coverage_approved": True,
        "log_retention_reviewed": True,
        "monitoring_dry_run_recorded": True,
        "production_monitoring_deployed": False,
        "production_monitoring_claim_published": False,
        "dashboard_configured_by_codex": False,
        "metrics_export_enabled_by_codex": False,
        "log_retention_changed_by_codex": False,
        "monitoring_deployed_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "codex_contacted_vendor": False,
        "codex_contacted_customer": False,
        "external_alert_delivery_enabled": False,
        "external_alert_delivery_available": False,
        "on_call_rotation_available": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("status") == "ready_for_human_operations_profile_review_no_closure",
        "status must be review-ready no-closure",
    )
    require(payload.get("resolved_current_path") == "combined_operations_profile", "resolved path mismatch")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Production Monitoring State Reconciliation",
        "production_monitoring_deployed=false",
        "dashboard_configured_by_codex=false",
        "metrics_export_enabled_by_codex=false",
        "monitoring_vendor_contacted_by_codex=false",
        "external_alert_delivery_enabled=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "No production monitoring deployed by Codex",
        "answer: hold_human_operations_review_required_no_monitoring_deploy_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "production_monitoring_deployed=true",
        "dashboard_configured_by_codex=true",
        "metrics_export_enabled_by_codex=true",
        "monitoring_vendor_contacted_by_codex=true",
        "external_alert_delivery_enabled=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/PRODUCTION_MONITORING_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation.md",
        "/docs/strategy/SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_production_monitoring_state_reconciliation.py",
        "/scripts/saee_production_monitoring_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("production_monitoring_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing production_monitoring_state_reconciliation_v0_1")
    for key in [
        "status",
        "target_blocker_id",
        "resolved_current_path",
        "monitoring_evidence_ready_for_review",
        "combined_operations_profile_ready",
        "production_monitoring_satisfied_by_profile",
        "external_alert_delivery_satisfied_by_profile",
        "operations_on_call_rotation_satisfied_by_profile",
        "production_monitoring_deployed",
        "dashboard_configured_by_codex",
        "metrics_export_enabled_by_codex",
        "monitoring_vendor_contacted_by_codex",
        "external_alert_delivery_enabled",
        "blockers_closed_by_reconciliation",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Production Monitoring State Reconciliation v0.1",
        "monitoring_evidence_ready_for_review=true",
        "combined_operations_profile_ready=true",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
