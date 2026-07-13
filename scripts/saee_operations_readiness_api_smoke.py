#!/usr/bin/env python3
"""Smoke check for SAEE Operations Readiness API v0.1."""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.operations_readiness import evaluate_operations_readiness


ROUTE_PATH = ROOT / "saee_backend/api/readiness.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/OPERATIONS_READINESS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_OPERATIONS_READINESS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_OPERATIONS_READINESS_API_SMOKE: FAIL: {message}")


def assert_false(payload: dict[str, object], keys: list[str]) -> None:
    for key in keys:
        require(payload.get(key) is False, f"{key} must be false")


def main() -> None:
    for path in [ROUTE_PATH, MAIN_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")
    py_compile.compile(str(ROUTE_PATH), doraise=True)
    py_compile.compile(str(MAIN_PATH), doraise=True)

    route = ROUTE_PATH.read_text(encoding="utf-8")
    main = MAIN_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")
    gate = GATE_PATH.read_text(encoding="utf-8")
    combined = "\n".join([route, main, doc, gate])

    route_tokens = [
        "APIRouter",
        "Depends(require_api_key)",
        "require_tenant_boundary",
        "require_rbac_route",
        "evaluate_operations_readiness",
        '"/operations"',
        'require_rbac_route("GET /readiness/operations")',
        "public_shell_operations_readiness_read_only",
        '"operations_readiness_api_v0_1"] = True',
        '"operations_readiness_api_available"] = True',
        '"read_only_operations_readiness_api"] = True',
        '"task_candidates_executed"] = False',
        '"blockers_closed_by_route"] = 0',
        '"monitoring_configured_by_route"] = False',
        '"external_alert_delivery_configured_by_route"] = False',
        '"on_call_rotation_started_by_route"] = False',
        '"sla_started_by_route"] = False',
        '"support_process_started_by_route"] = False',
        '"production_ready"] = False',
        '"customer_validated"] = False',
        '"product_launched"] = False',
        '"body_inspected"] = False',
        '"credentials_inspected"] = False',
        '"private_core_inspected"] = False',
    ]
    missing_route = [token for token in route_tokens if token not in route]
    require(not missing_route, "route missing tokens: " + ", ".join(missing_route))

    main_tokens = [
        "readiness_router",
        'prefix="/readiness"',
        'tags=["readiness"]',
    ]
    missing_main = [token for token in main_tokens if token not in main]
    require(not missing_main, "main.py missing tokens: " + ", ".join(missing_main))

    report = evaluate_operations_readiness(load_settings({}))
    require(report["operations_readiness_status"] == "hold", "default operations status must be hold")
    require(report["request_metadata_audit_available"] is True, "request metadata audit must be available")
    require(report["local_operations_telemetry_available"] is True, "local telemetry must be available")
    require(
        report["operations_telemetry_external_export_available"] is False,
        "external telemetry export must be false",
    )
    require(report["local_alert_policy_available"] is True, "local alert policy must be available")
    require(report["incident_response_runbook_available"] is True, "incident runbook must be available")
    assert_false(
        report,
        [
            "external_alert_delivery_available",
            "production_monitoring_available",
            "alerting_available",
            "customer_support_available",
            "production_support_available",
            "on_call_rotation_available",
            "sla_available",
            "support_process_available",
            "production_operations_ready",
            "production_ready",
            "customer_validated",
            "product_launched",
            "public_sdk_released",
            "private_core_exposed",
            "runtime_modified",
            "kernel_modified",
            "api_schema_modified",
            "external_calls_made",
        ],
    )

    required_doc_tokens = [
        "operations_readiness_api_v0_1: true",
        "operations_readiness_api_available: true",
        "read_only_operations_readiness_api: true",
        "operations_readiness_route: GET /readiness/operations",
        "route_scope: public_shell_operations_readiness_read_only",
        "operations_readiness_status_default: hold",
        "request_metadata_audit_available_default: true",
        "local_operations_telemetry_available_default: true",
        "operations_telemetry_external_export_available_default: false",
        "local_alert_policy_available_default: true",
        "external_alert_delivery_available_default: false",
        "production_monitoring_available_default: false",
        "alerting_available_default: false",
        "incident_response_runbook_available_default: true",
        "production_operations_ready_default: false",
        "customer_support_available_default: false",
        "production_support_available_default: false",
        "on_call_rotation_available_default: false",
        "sla_available_default: false",
        "support_process_available_default: false",
        "blockers_closed_by_route: 0",
        "task_candidates_executed: false",
        "monitoring_configured_by_route: false",
        "external_alert_delivery_configured_by_route: false",
        "on_call_rotation_started_by_route: false",
        "sla_started_by_route: false",
        "support_process_started_by_route: false",
        "body_inspected: false",
        "credentials_inspected: false",
        "private_core_inspected: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "public_sdk_released: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_controlled_preview_operations_readiness_review: true",
        "recommend_for_production_monitoring_configuration: false",
        "recommend_for_external_alert_delivery_configuration: false",
        "recommend_for_on_call_rotation_start: false",
        "recommend_for_sla_start: false",
        "recommend_for_support_process_start: false",
        "recommend_for_production_operations_ready_claim: false",
        "recommend_for_public_launch_now: false",
    ]
    missing_doc = [token for token in required_doc_tokens if token not in combined]
    require(not missing_doc, "doc/gate missing tokens: " + ", ".join(missing_doc))

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "public_sdk_released: true",
        '"public_sdk_released": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "task_candidates_executed: true",
        '"task_candidates_executed": true',
        "monitoring_configured_by_route: true",
        '"monitoring_configured_by_route": true',
        "external_alert_delivery_configured_by_route: true",
        '"external_alert_delivery_configured_by_route": true',
        "on_call_rotation_started_by_route: true",
        '"on_call_rotation_started_by_route": true',
        "sla_started_by_route: true",
        '"sla_started_by_route": true',
        "support_process_started_by_route: true",
        '"support_process_started_by_route": true',
        "production_operations_ready: true",
        '"production_operations_ready": true',
        "api_schema_modified: true",
        '"api_schema_modified": true',
        "runtime_modified: true",
        '"runtime_modified": true',
        "kernel_modified: true",
        '"kernel_modified": true',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    if importlib.util.find_spec("fastapi") and importlib.util.find_spec("starlette"):
        from fastapi.testclient import TestClient

        from saee_backend.main import app

        client = TestClient(app)
        response = client.get("/readiness/operations")
        require(response.status_code == 200, "operations route must return 200")
        payload = response.json()
        require(
            payload["route_scope"] == "public_shell_operations_readiness_read_only",
            "operations route scope mismatch",
        )
        require(payload["operations_readiness_status"] == "hold", "route status must remain hold")
        require(payload["request_metadata_audit_available"] is True, "route request audit true")
        require(payload["local_operations_telemetry_available"] is True, "route telemetry true")
        require(payload["local_alert_policy_available"] is True, "route alert policy true")
        require(payload["incident_response_runbook_available"] is True, "route runbook true")
        require(payload["blockers_closed_by_route"] == 0, "route must close zero blockers")
        require(payload["task_candidates_executed"] is False, "route must execute no tasks")
        assert_false(
            payload,
            [
                "operations_telemetry_external_export_available",
                "external_alert_delivery_available",
                "production_monitoring_available",
                "alerting_available",
                "customer_support_available",
                "production_support_available",
                "on_call_rotation_available",
                "sla_available",
                "support_process_available",
                "production_operations_ready",
                "production_ready",
                "customer_validated",
                "product_launched",
                "public_sdk_released",
                "private_core_exposed",
                "api_schema_modified",
                "runtime_modified",
                "kernel_modified",
                "external_calls_made",
                "body_inspected",
                "credentials_inspected",
                "private_core_inspected",
                "monitoring_configured_by_route",
                "external_alert_delivery_configured_by_route",
                "on_call_rotation_started_by_route",
                "sla_started_by_route",
                "support_process_started_by_route",
            ],
        )

    print(
        "SAEE_OPERATIONS_READINESS_API_SMOKE: PASS "
        "route=/readiness/operations read_only=true status=hold "
        "blockers_closed_by_route=0 production_monitoring_available=false "
        "external_alert_delivery_available=false on_call_rotation_available=false "
        "production_operations_ready=false"
    )


if __name__ == "__main__":
    main()
