#!/usr/bin/env python3
"""Smoke check for SAEE Data Operations Readiness API v0.1."""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_data_operations_evidence import (
    evaluate_production_data_operations_evidence,
)


ROUTE_PATH = ROOT / "saee_backend/api/readiness.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/DATA_OPERATIONS_READINESS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_DATA_OPERATIONS_READINESS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_DATA_OPERATIONS_READINESS_API_SMOKE: FAIL: {message}")


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
        "evaluate_production_data_operations_evidence",
        '"/data-operations"',
        'require_rbac_route("GET /readiness/data-operations")',
        "public_shell_data_operations_readiness_read_only",
        '"data_operations_readiness_api_v0_1"] = True',
        '"read_only_data_operations_readiness_api"] = True',
        '"task_candidates_executed"] = False',
        '"blockers_closed_by_route"] = 0',
        '"restore_executed_by_route"] = False',
        '"live_data_path_inspected"] = False',
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

    report = evaluate_production_data_operations_evidence(load_settings({}))
    require(report["status"] == "hold", "default data operations status must be hold")
    require(report["restore_tested"] is False, "default restore_tested must be false")
    require(
        report["production_restore_policy_available"] is False,
        "default production_restore_policy_available must be false",
    )
    require(
        report["production_data_operations_ready"] is False,
        "default production_data_operations_ready must be false",
    )
    assert_false(
        report,
        [
            "production_ready",
            "customer_validated",
            "product_launched",
            "public_sdk_released",
            "private_core_exposed",
            "api_schema_modified",
            "runtime_modified",
            "kernel_modified",
            "external_calls_made",
            "production_data_path_modified",
            "restore_to_live_path_enabled",
            "live_restore_performed",
            "credentials_restored",
            "private_core_restored",
        ],
    )

    required_doc_tokens = [
        "data_operations_readiness_api_v0_1: true",
        "data_operations_readiness_api_available: true",
        "read_only_data_operations_readiness_api: true",
        "data_operations_readiness_route: GET /readiness/data-operations",
        "route_scope: public_shell_data_operations_readiness_read_only",
        "production_data_operations_evidence_status_default: hold",
        "restore_tested_default: false",
        "production_restore_tested_default: false",
        "production_restore_policy_available_default: false",
        "production_data_operations_ready_default: false",
        "blockers_closed_by_route: 0",
        "task_candidates_executed: false",
        "restore_executed_by_route: false",
        "live_data_path_inspected: false",
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
        "recommend_for_controlled_preview_data_operations_readiness_review: true",
        "recommend_for_restore_execution: false",
        "recommend_for_production_restore_policy_approval: false",
        "recommend_for_production_data_operations_readiness: false",
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
        "restore_executed_by_route: true",
        '"restore_executed_by_route": true',
        "live_data_path_inspected: true",
        '"live_data_path_inspected": true',
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
        response = client.get("/readiness/data-operations")
        require(response.status_code == 200, "data-operations route must return 200")
        payload = response.json()
        require(
            payload["route_scope"] == "public_shell_data_operations_readiness_read_only",
            "data-operations route scope mismatch",
        )
        require(payload["status"] == "hold", "route status must remain hold")
        require(payload["restore_tested"] is False, "route default restore_tested false")
        require(
            payload["production_restore_policy_available"] is False,
            "route default production_restore_policy_available false",
        )
        require(
            payload["production_data_operations_ready"] is False,
            "route default production_data_operations_ready false",
        )
        require(payload["blockers_closed_by_route"] == 0, "route must close zero blockers")
        require(payload["task_candidates_executed"] is False, "route must execute no tasks")
        assert_false(
            payload,
            [
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
                "live_data_path_inspected",
                "restore_executed_by_route",
            ],
        )

    print(
        "SAEE_DATA_OPERATIONS_READINESS_API_SMOKE: PASS "
        "route=/readiness/data-operations read_only=true status=hold "
        "blockers_closed_by_route=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
