#!/usr/bin/env python3
"""Smoke check for SAEE Operations Alert Policy v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.api.audit import build_request_audit_event
from saee_backend.config import load_settings
from saee_backend.services.operations_alert_policy import evaluate_operations_alert_policy


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_OPERATIONS_ALERT_POLICY_SMOKE: FAIL: {message}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_path = Path(tmpdir) / "request_audit.jsonl"
        events = [
            build_request_audit_event(
                request_id="req-ok-1",
                method="GET",
                path="/ready",
                status_code=200,
                duration_ms=80.0,
            ),
            build_request_audit_event(
                request_id="req-ok-2",
                method="POST",
                path="/experiment/run",
                status_code=200,
                duration_ms=120.0,
                tenant_audit_metadata={
                    "tenant_boundary_checked": True,
                    "tenant_id_present": True,
                    "tenant_id_hash_recorded": True,
                    "tenant_id_raw_recorded": False,
                    "tenant_id_hash": sha256("tenant-alpha".encode("utf-8")).hexdigest(),
                    "tenant_id_hash_algorithm": "sha256",
                },
            ),
            build_request_audit_event(
                request_id="req-error-1",
                method="POST",
                path="/experiment/run",
                status_code=500,
                duration_ms=2500.0,
                error_type="unhandled_exception",
                tenant_audit_metadata={
                    "tenant_boundary_checked": True,
                    "tenant_id_present": True,
                    "tenant_id_hash_recorded": True,
                    "tenant_id_raw_recorded": False,
                    "tenant_id_hash": sha256("tenant-beta".encode("utf-8")).hexdigest(),
                    "tenant_id_hash_algorithm": "sha256",
                },
            ),
            build_request_audit_event(
                request_id="req-error-2",
                method="POST",
                path="/experiment/run",
                status_code=503,
                duration_ms=3000.0,
                error_type="service_unavailable",
                tenant_audit_metadata={
                    "tenant_boundary_checked": True,
                    "tenant_id_present": True,
                    "tenant_id_hash_recorded": True,
                    "tenant_id_raw_recorded": False,
                    "tenant_id_hash": sha256("tenant-beta".encode("utf-8")).hexdigest(),
                    "tenant_id_hash_algorithm": "sha256",
                },
            ),
        ]
        audit_path.write_text(
            "\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n",
            encoding="utf-8",
        )
        settings = load_settings(
            {
                "SAEE_REQUEST_AUDIT_ENABLED": "true",
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
            }
        )
        report = evaluate_operations_alert_policy(settings)
        tenant_report = evaluate_operations_alert_policy(settings, tenant_id="tenant-alpha")

    require(report["alert_policy_type"] == "local_public_shell_alert_policy", "wrong alert policy type")
    require(report["local_alert_policy_available"] is True, "local alert policy must be available")
    require(report["alert_candidates_generated"] is True, "alert candidates must be generated")
    require(report["alert_count"] >= 1, "test data must produce local alert candidates")
    require(report["event_count"] == 4, "event count wrong")
    require(report["error_count"] == 2, "error count wrong")
    require(report["error_rate"] == 0.5, "error rate wrong")
    require(report["tenant_scope_filter_applied"] is False, "default tenant filter false")
    require(report["tenant_id_raw_filter_recorded"] is False, "default raw tenant filter false")
    require(tenant_report["tenant_scope_filter_applied"] is True, "tenant alert filter true")
    require(tenant_report["tenant_id_raw_filter_recorded"] is False, "tenant alert raw filter false")
    require(tenant_report["event_count"] == 1, "tenant alert event count wrong")
    require(tenant_report["error_count"] == 0, "tenant alert should exclude other tenant errors")
    require(tenant_report["alert_count"] == 0, "tenant alert should not inherit other tenant alerts")
    require(report["external_alert_delivery_available"] is False, "external delivery must remain false")
    require(report["alerting_available"] is False, "production alerting must remain false")
    require(report["production_monitoring_available"] is False, "production monitoring must remain false")
    require(report["operations_telemetry_external_export_available"] is False, "external export must remain false")
    require(report["incident_response_runbook_available"] is True, "incident runbook must be available")
    require(report["support_readiness_v0_1"] is True, "support readiness must be available")
    require(report["support_runbook_available"] is True, "support runbook must be available")
    require(report["support_contact_configured"] is False, "support contact must remain false")
    require(report["customer_support_available"] is False, "customer support must remain false")
    require(report["production_support_available"] is False, "production support must remain false")
    require(report["on_call_rotation_available"] is False, "on-call must remain false")
    require(report["sla_available"] is False, "SLA must remain false")
    require(report["support_process_available"] is False, "support process must remain false")
    require(report["production_operations_ready"] is False, "production operations must remain false")
    require(report["body_inspected"] is False, "body must not be inspected")
    require(report["credentials_inspected"] is False, "credentials must not be inspected")
    require(report["private_core_inspected"] is False, "private core must not be inspected")
    require(report["private_core_exposed"] is False, "private core exposed false")
    require(report["production_ready"] is False, "production ready false")
    require(report["customer_validated"] is False, "customer validation false")
    require(report["product_launched"] is False, "product launch false")
    require(report["external_calls_made"] is False, "external calls false")
    require(all(item["manual_review_required"] is True for item in report["alerts"]), "alerts need review")

    empty_report = evaluate_operations_alert_policy(load_settings({"SAEE_REQUEST_AUDIT_PATH": "/tmp/no-such-saee-audit.jsonl"}))
    require(empty_report["event_count"] == 0, "empty report event count wrong")
    require(empty_report["alerting_available"] is False, "empty report alerting false")
    require(empty_report["external_calls_made"] is False, "empty report external calls false")

    doc = (ROOT / "phase_b_product/commercial_readiness/OPERATIONS_ALERT_POLICY_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_OPERATIONS_ALERT_POLICY_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("operations_alert_policy_v0_1: true" in doc, "alert policy doc missing state")
    require("local_alert_policy_available: true" in doc, "alert policy doc missing local availability")
    require("tenant_scope_filter_available: true" in doc, "alert policy doc tenant filter true")
    require("tenant_id_raw_filter_recorded: false" in doc, "alert policy doc raw tenant filter false")
    require("external_alert_delivery_available: false" in doc, "alert policy doc delivery false")
    require("alerting_available: false" in doc, "alert policy doc alerting false")
    require("production_operations_ready: false" in doc, "alert policy doc production ops false")
    require("body_inspected: false" in doc, "alert policy doc body false")
    require("answer: conditional" in gate, "alert policy gate conditional")
    require("recommend_public_launch_now: false" in gate, "alert policy gate no launch")

    print(
        "SAEE_OPERATIONS_ALERT_POLICY_SMOKE: PASS "
        "local_alert_policy_available=true "
        "external_alert_delivery_available=false "
        "alerting_available=false "
        "production_monitoring_available=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
