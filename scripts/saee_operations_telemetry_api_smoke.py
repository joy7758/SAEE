#!/usr/bin/env python3
"""Smoke check for SAEE Operations Telemetry API v0.1."""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.api.audit import build_request_audit_event
from saee_backend.config import load_settings
from saee_backend.services.operations_alert_policy import evaluate_operations_alert_policy
from saee_backend.services.operations_telemetry import build_operations_telemetry_snapshot


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_OPERATIONS_TELEMETRY_API_SMOKE: FAIL: {message}")


def main() -> None:
    operations_route = ROOT / "saee_backend/api/operations.py"
    main_py = ROOT / "saee_backend/main.py"
    doc_path = ROOT / "phase_b_product/commercial_readiness/OPERATIONS_TELEMETRY_API_V0_1.md"
    gate_path = ROOT / "docs/strategy/SAEE_OPERATIONS_TELEMETRY_API_RECOMMENDATION_GATE.md"

    py_compile.compile(str(operations_route), doraise=True)

    route_text = operations_route.read_text(encoding="utf-8")
    main_text = main_py.read_text(encoding="utf-8")
    doc = doc_path.read_text(encoding="utf-8")
    gate = gate_path.read_text(encoding="utf-8")

    required_route_tokens = [
        "APIRouter",
        "require_api_key",
        "require_tenant_boundary",
        "require_rbac_route",
        "build_operations_telemetry_snapshot",
        "evaluate_operations_alert_policy",
        "build_operations_telemetry_snapshot(tenant_id=tenant_id)",
        "evaluate_operations_alert_policy(tenant_id=tenant_id)",
        "\"/telemetry\"",
        "require_rbac_route(\"GET /operations/telemetry\")",
        "\"/alerts\"",
        "require_rbac_route(\"GET /operations/alerts\")",
        "public_shell_operations_read_only",
        "\"production_monitoring_available\"] = False",
        "\"operations_telemetry_external_export_available\"] = False",
        "\"external_alert_delivery_available\"] = False",
        "\"body_inspected\"] = False",
        "\"credentials_inspected\"] = False",
        "\"private_core_inspected\"] = False",
        "\"tenant_scope_filter_applied\"] = tenant_id is not None",
        "\"tenant_id_raw_filter_recorded\"] = False",
    ]
    missing_route_tokens = [token for token in required_route_tokens if token not in route_text]
    require(not missing_route_tokens, "route missing tokens: " + ", ".join(missing_route_tokens))
    require("operations_router" in main_text, "main.py must include operations router")
    require("prefix=\"/operations\"" in main_text, "main.py must mount /operations")

    with tempfile.TemporaryDirectory() as tmpdir:
        audit_path = Path(tmpdir) / "request_audit.jsonl"
        events = [
            build_request_audit_event(
                request_id="req-api-ok",
                method="GET",
                path="/ready",
                status_code=200,
                duration_ms=8.0,
            ),
            build_request_audit_event(
                request_id="req-api-error",
                method="GET",
                path="/operations/telemetry",
                status_code=500,
                duration_ms=120.0,
                error_type="unhandled_exception",
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
        telemetry = build_operations_telemetry_snapshot(settings)
        alerts = evaluate_operations_alert_policy(settings)

    require(telemetry["event_count"] == 2, "telemetry must read local events")
    require(telemetry["error_count"] == 1, "telemetry must count errors")
    require(telemetry["production_monitoring_available"] is False, "monitoring must remain false")
    require(telemetry["tenant_scope_filter_applied"] is False, "default tenant filter false")
    require(telemetry["tenant_id_raw_filter_recorded"] is False, "default raw tenant filter false")
    require(
        telemetry["operations_telemetry_external_export_available"] is False,
        "external export must remain false",
    )
    require(telemetry["body_inspected"] is False, "body inspection must remain false")
    require(telemetry["credentials_inspected"] is False, "credential inspection must remain false")
    require(telemetry["private_core_inspected"] is False, "private core inspection must remain false")
    require(alerts["alert_count"] >= 1, "alert candidate should be generated for local error")
    require(alerts["tenant_scope_filter_applied"] is False, "alert default tenant filter false")
    require(alerts["tenant_id_raw_filter_recorded"] is False, "alert default raw tenant filter false")
    require(alerts["external_alert_delivery_available"] is False, "external delivery false")
    require(alerts["alerting_available"] is False, "production alerting false")

    if importlib.util.find_spec("fastapi") is not None:
        from fastapi.testclient import TestClient

        from saee_backend.main import app

        client = TestClient(app)
        response = client.get("/operations/telemetry")
        require(response.status_code == 200, "FastAPI telemetry route must return 200")
        body = response.json()
        require(
            body["route_scope"] == "public_shell_operations_read_only",
            "FastAPI telemetry route scope wrong",
        )

    required_doc_tokens = [
        "operations_telemetry_api_v0_1: true",
        "operations_telemetry_api_available: true",
        "read_only_operations_api: true",
        "GET /operations/telemetry",
        "GET /operations/alerts",
        "production_monitoring_available: false",
        "external_alert_delivery_available: false",
        "operations_telemetry_external_export_available: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "tenant_scope_filter_available: true",
        "tenant_id_raw_filter_recorded: false",
    ]
    missing_doc_tokens = [token for token in required_doc_tokens if token not in doc]
    require(not missing_doc_tokens, "doc missing tokens: " + ", ".join(missing_doc_tokens))

    required_gate_tokens = [
        "answer: conditional",
        "recommend_for_controlled_preview_operations_review: true",
        "recommend_for_production_monitoring: false",
        "recommend_for_external_alert_delivery: false",
        "recommend_for_public_launch_now: false",
        "operations_telemetry_api_v0_1: true",
        "production_monitoring_available: false",
        "external_calls_made: false",
        "tenant_scope_filter_available: true",
    ]
    missing_gate_tokens = [token for token in required_gate_tokens if token not in gate]
    require(not missing_gate_tokens, "gate missing tokens: " + ", ".join(missing_gate_tokens))

    forbidden = [
        "production_monitoring_available: true",
        "\"production_monitoring_available\": true",
        "external_alert_delivery_available: true",
        "\"external_alert_delivery_available\": true",
        "operations_telemetry_external_export_available: true",
        "\"operations_telemetry_external_export_available\": true",
        "production_operations_ready: true",
        "\"production_operations_ready\": true",
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "external_calls_made: true",
        "\"external_calls_made\": true",
    ]
    combined = "\n".join([route_text, main_text, doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    print(
        "SAEE_OPERATIONS_TELEMETRY_API_SMOKE: PASS "
        "operations_telemetry_api_available=true "
        "routes=/operations/telemetry,/operations/alerts "
        "read_only=true "
        "production_monitoring_available=false "
        "external_alert_delivery_available=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
