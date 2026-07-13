#!/usr/bin/env python3
"""Smoke check for SAEE Operations Telemetry v0.1."""

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
from saee_backend.services.operations_telemetry import build_operations_telemetry_snapshot


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_OPERATIONS_TELEMETRY_SMOKE: FAIL: {message}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_path = Path(tmpdir) / "request_audit.jsonl"
        events = [
            build_request_audit_event(
                request_id="req-ok-1",
                method="GET",
                path="/ready",
                status_code=200,
                duration_ms=10.0,
            ),
            build_request_audit_event(
                request_id="req-ok-2",
                method="POST",
                path="/experiment/run",
                status_code=200,
                duration_ms=30.0,
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
                duration_ms=90.0,
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
        ]
        audit_path.write_text(
            "\n".join(json.dumps(event, sort_keys=True) for event in events) + "\nnot-json\n",
            encoding="utf-8",
        )
        settings = load_settings(
            {
                "SAEE_REQUEST_AUDIT_ENABLED": "true",
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
            }
        )
        snapshot = build_operations_telemetry_snapshot(settings)
        tenant_snapshot = build_operations_telemetry_snapshot(settings, tenant_id="tenant-alpha")

    require(snapshot["telemetry_type"] == "local_public_shell_operations_telemetry", "wrong type")
    require(snapshot["local_operations_telemetry_available"] is True, "telemetry must be available")
    require(snapshot["operations_telemetry_external_export_available"] is False, "external export false")
    require(snapshot["local_alert_policy_available"] is True, "local alert policy must be available")
    require(snapshot["external_alert_delivery_available"] is False, "external alert delivery false")
    require(snapshot["production_monitoring_available"] is False, "production monitoring false")
    require(snapshot["alerting_available"] is False, "alerting false")
    require(snapshot["incident_response_runbook_available"] is True, "incident response runbook true")
    require(snapshot["production_operations_ready"] is False, "production operations false")
    require(snapshot["event_count"] == 3, "must read three events")
    require(snapshot["invalid_line_count"] == 1, "must count invalid line")
    require(snapshot["status_code_counts"] == {"200": 2, "500": 1}, "status counts wrong")
    require(snapshot["method_counts"] == {"GET": 1, "POST": 2}, "method counts wrong")
    require(snapshot["error_count"] == 1, "error count wrong")
    require(snapshot["tenant_audit_metadata_available"] is True, "tenant audit metadata true")
    require(snapshot["tenant_boundary_checked_count"] == 2, "tenant boundary count wrong")
    require(snapshot["tenant_scoped_request_count"] == 2, "tenant scoped count wrong")
    require(snapshot["tenant_id_hash_recorded_count"] == 2, "tenant hash count wrong")
    require(snapshot["tenant_id_raw_recorded_count"] == 0, "raw tenant ID count must be zero")
    require(snapshot["tenant_scope_filter_applied"] is False, "default tenant filter false")
    require(snapshot["tenant_id_raw_filter_recorded"] is False, "default raw tenant filter false")
    require(tenant_snapshot["tenant_scope_filter_applied"] is True, "tenant filter must apply")
    require(tenant_snapshot["tenant_id_raw_filter_recorded"] is False, "raw tenant filter false")
    require(tenant_snapshot["event_count"] == 1, "tenant-scoped snapshot must read one event")
    require(tenant_snapshot["error_count"] == 0, "tenant-scoped snapshot must exclude other tenant errors")
    require(tenant_snapshot["tenant_scoped_request_count"] == 1, "tenant-scoped count wrong")
    require(snapshot["duration_ms_median"] == 30.0, "median wrong")
    require(snapshot["duration_ms_p95"] == 84.0, "p95 wrong")
    require(snapshot["body_inspected"] is False, "body must not be inspected")
    require(snapshot["credentials_inspected"] is False, "credentials must not be inspected")
    require(snapshot["private_core_inspected"] is False, "private core must not be inspected")
    require(snapshot["private_core_exposed"] is False, "private core exposed false")
    require(snapshot["production_ready"] is False, "production ready false")
    require(snapshot["external_calls_made"] is False, "external calls false")

    doc = (ROOT / "phase_b_product/commercial_readiness/OPERATIONS_TELEMETRY_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_OPERATIONS_TELEMETRY_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("operations_telemetry_v0_1: true" in doc, "telemetry doc missing state")
    require("production_monitoring_available: false" in doc, "telemetry doc must keep monitoring false")
    require("operations_telemetry_external_export_available: false" in doc, "telemetry doc export false")
    require("incident_response_runbook_available: true" in doc, "telemetry doc incident runbook true")
    require("tenant_audit_metadata_available: true" in doc, "telemetry doc tenant metadata true")
    require("tenant_scope_filter_available: true" in doc, "telemetry doc tenant filter true")
    require("tenant_id_raw_recorded_count" in doc, "telemetry doc missing tenant raw count")
    require("body_inspected: false" in doc, "telemetry doc body false")
    require("answer: conditional" in gate, "telemetry gate conditional")
    require("recommend_public_launch_now: false" in gate, "telemetry gate no launch")

    print(
        "SAEE_OPERATIONS_TELEMETRY_SMOKE: PASS "
        "local_operations_telemetry_available=true "
        "local_alert_policy_available=true "
        "production_monitoring_available=false "
        "external_alert_delivery_available=false "
        "external_export=false "
        "tenant_audit_metadata_available=true "
        "tenant_id_raw_recorded_count=0 "
        "body_inspected=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
