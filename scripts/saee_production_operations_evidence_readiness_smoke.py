#!/usr/bin/env python3
"""Smoke check for SAEE Production Operations Evidence Readiness v0.1."""

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
from saee_backend.services.production_operations_evidence import (
    evaluate_production_operations_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_SMOKE: FAIL: {message}")


def write_operations_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "operations_evidence_type": "production_operations_evidence",
        "production_monitoring_plan_approved": True,
        "metrics_coverage_approved": True,
        "slo_dashboard_defined": True,
        "log_retention_reviewed": True,
        "monitoring_dry_run_recorded": True,
        "external_alert_channel_configured": True,
        "alert_routing_policy_approved": True,
        "alert_delivery_test_recorded": True,
        "alert_failure_handling_defined": True,
        "incident_escalation_path_defined": True,
        "alert_acknowledgement_process_defined": True,
        "on_call_rotation_defined": True,
        "escalation_schedule_defined": True,
        "incident_commander_named": True,
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
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "production_monitoring_deployed": False,
        "external_alert_delivery_enabled": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_operations_evidence(load_settings({}))
    require(
        local["production_operations_evidence_type"]
        == "production_operations_evidence_readiness",
        "wrong evidence type",
    )
    require(local["production_operations_evidence_readiness_v0_1"] is True, "readiness flag")
    require(local["status"] == "hold", "default evidence status must hold")
    require(local["operations_evidence_path_configured"] is False, "default path false")
    require(local["production_monitoring_available"] is False, "default monitoring false")
    require(local["external_alert_delivery_available"] is False, "default alert delivery false")
    require(local["on_call_rotation_available"] is False, "default on-call false")
    require(local["production_operations_ready"] is False, "default operations ready false")
    require(local["production_ready"] is False, "default production false")
    require(local["customer_validated"] is False, "default customer validation false")
    require(local["product_launched"] is False, "default launch false")
    require(local["private_core_exposed"] is False, "default private core false")
    require(local["external_calls_made"] is False, "default external calls false")
    require(local["customer_contacted"] is False, "default customer contacted false")
    require(local["alert_provider_contacted"] is False, "default alert provider false")
    require(local["monitoring_vendor_contacted"] is False, "default monitoring vendor false")
    require(local["production_monitoring_deployed"] is False, "default monitoring deployed false")
    require(
        local["external_alert_delivery_enabled"] is False,
        "default alert delivery enabled false",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "OPERATIONS_EVIDENCE.json"
        write_operations_evidence(evidence_path)
        settings = load_settings(
            {
                "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(evidence_path),
            }
        )
        configured = evaluate_production_operations_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_OPERATIONS_EVIDENCE.json"
        write_operations_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_operations_evidence(
            load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(unsafe_path)})
        )

    require(configured["status"] == "pass", "complete operations evidence should pass")
    require(configured["production_monitoring_available"] is True, "monitoring evidence true")
    require(configured["external_alert_delivery_available"] is True, "alert evidence true")
    require(configured["on_call_rotation_available"] is True, "on-call evidence true")
    require(configured["production_operations_ready"] is True, "operations ready true")
    require(configured["production_ready"] is False, "evidence pass must not claim production")
    require(configured["customer_validated"] is False, "evidence pass must not claim customers")
    require(configured["product_launched"] is False, "evidence pass must not claim launch")
    require(configured["external_calls_made"] is False, "evidence pass must not call external")
    require(configured["customer_contacted"] is False, "evidence pass must not contact customers")
    require(
        configured["alert_provider_contacted"] is False,
        "evidence pass must not contact alert providers",
    )
    require(
        configured["monitoring_vendor_contacted"] is False,
        "evidence pass must not contact monitoring vendors",
    )
    require(
        configured["production_monitoring_deployed"] is False,
        "evidence pass must not deploy monitoring",
    )
    require(
        configured["external_alert_delivery_enabled"] is False,
        "evidence pass must not enable alert delivery",
    )

    blocked = blocker_ids(go_no_go)
    for blocker in ["production_monitoring", "external_alert_delivery", "on_call_rotation"]:
        require(blocker not in blocked, f"{blocker} should be satisfied by operations evidence")
    require(
        go_no_go["production_operations_evidence_status"] == "pass",
        "go/no-go should expose operations evidence pass",
    )
    require(
        go_no_go["operations_evidence_production_monitoring_available"] is True,
        "go/no-go should expose monitoring evidence",
    )
    require(
        go_no_go["operations_evidence_external_alert_delivery_available"] is True,
        "go/no-go should expose alert evidence",
    )
    require(
        go_no_go["operations_evidence_on_call_rotation_available"] is True,
        "go/no-go should expose on-call evidence",
    )
    require(go_no_go["commercial_status"] == "hold", "operations evidence alone must not launch")
    require(go_no_go["production_launch_status"] == "hold", "production launch must still hold")
    require(go_no_go["production_ready"] is False, "go/no-go must keep production false")
    require(go_no_go["customer_validated"] is False, "go/no-go must keep customer validation false")
    require(go_no_go["product_launched"] is False, "go/no-go must keep launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go must keep private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require("production_ready" in unsafe["boundary_violations"], "unsafe evidence must detect boundary")
    require(unsafe["production_ready"] is False, "unsafe output must still preserve production false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_OPERATIONS_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    for token in [
        "production_operations_evidence_readiness_v0_1: true",
        "default_status: hold",
        "operations_evidence_path_configured_default: false",
        "production_monitoring_available_default: false",
        "external_alert_delivery_available_default: false",
        "on_call_rotation_available_default: false",
        "production_operations_ready_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "alert_provider_contacted: false",
        "monitoring_vendor_contacted: false",
        "production_monitoring_deployed: false",
        "external_alert_delivery_enabled: false",
        "answer: conditional",
        "recommend_for_production_launch: false",
    ]:
        require(token in doc or token in gate, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_OPERATIONS_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_operations_evidence.py",
        "/scripts/saee_production_operations_evidence_readiness.py",
        "/scripts/saee_production_operations_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_operations_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_operations_evidence_readiness_hold",
        "production_operations_evidence_readiness_v0_1": True,
        "operations_evidence_path_configured_default": False,
        "production_monitoring_available_default": False,
        "external_alert_delivery_available_default": False,
        "on_call_rotation_available_default": False,
        "production_operations_ready_default": False,
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
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "operations_blockers_satisfied_by_evidence=true production_launch_status=hold "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
