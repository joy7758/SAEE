#!/usr/bin/env python3
"""Smoke check for the local operations evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_operations_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_operations_evidence,
)
from scripts.saee_operations_evidence_runner import OUTPUT_PATH, main as run_runner


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_OPERATIONS_EVIDENCE_RUNNER_SMOKE: FAIL: " + message)


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    require(
        evidence.get("operations_evidence_type") == "production_operations_evidence",
        "wrong operations evidence type",
    )
    require(
        evidence.get("evidence_scope")
        == "local_public_shell_telemetry_alert_candidate_dry_run",
        "wrong evidence scope",
    )
    require(evidence.get("monitoring_dry_run_recorded") is True, "dry run must be recorded")
    require(
        evidence.get("production_monitoring_plan_approved") is False,
        "must not claim monitoring plan approval",
    )
    require(
        evidence.get("metrics_coverage_approved") is False,
        "must not claim metrics coverage approval",
    )
    require(
        evidence.get("external_alert_channel_configured") is False,
        "must not claim external alert channel",
    )
    require(
        evidence.get("alert_delivery_test_recorded") is False,
        "must not claim alert delivery test",
    )
    require(
        evidence.get("on_call_rotation_defined") is False,
        "must not claim on-call rotation",
    )
    require(
        evidence["local_public_shell_results"]["event_count"] == 3,
        "must record local sample events",
    )
    require(
        evidence["local_public_shell_results"]["alert_candidates_generated"] is True,
        "must record alert-candidate generation",
    )

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    readiness = evaluate_production_operations_evidence(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    require(
        readiness["production_monitoring_available"] is False,
        "production monitoring must remain incomplete",
    )
    require(
        readiness["external_alert_delivery_available"] is False,
        "external alert delivery must remain incomplete",
    )
    require(
        readiness["on_call_rotation_available"] is False,
        "on-call rotation must remain incomplete",
    )
    require(
        readiness["production_operations_ready"] is False,
        "production operations must remain incomplete",
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
        "alert_provider_contacted",
        "monitoring_vendor_contacted",
        "production_monitoring_deployed",
        "external_alert_delivery_enabled",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT / "phase_b_product/commercial_readiness/OPERATIONS_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_OPERATIONS_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "operations_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_telemetry_alert_candidate_dry_run",
        "production_operations_ready: false",
        "production_monitoring_available: false",
        "external_alert_delivery_available: false",
        "on_call_rotation_available: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/OPERATIONS_EVIDENCE_RUNNER_V0_1.md",
        "/docs/strategy/SAEE_OPERATIONS_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/operations_evidence/README.md",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json",
        "/scripts/saee_operations_evidence_runner.py",
        "/scripts/saee_operations_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("operations_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "operations_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_telemetry_alert_candidate_dry_run",
        "monitoring_dry_run_recorded": True,
        "alert_candidates_generated": True,
        "production_monitoring_plan_approved": False,
        "metrics_coverage_approved": False,
        "external_alert_channel_configured": False,
        "alert_delivery_test_recorded": False,
        "on_call_rotation_defined": False,
        "production_monitoring_available": False,
        "external_alert_delivery_available": False,
        "on_call_rotation_available": False,
        "production_operations_ready": False,
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
    for flag, expected_value in expected.items():
        require(entry.get(flag) == expected_value, f"agent-index {flag} must be {expected_value}")

    print(
        "SAEE_OPERATIONS_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "production_operations_ready=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
