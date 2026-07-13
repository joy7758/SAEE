#!/usr/bin/env python3
"""Smoke check for SAEE Commercial Status API v0.1."""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


ROUTE_PATH = ROOT / "saee_backend/api/commercial.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_STATUS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_STATUS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_COMMERCIAL_STATUS_API_SMOKE: FAIL: {message}")


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
        "evaluate_commercial_go_no_go",
        '"/status"',
        'require_rbac_route("GET /commercial/status")',
        "public_shell_commercial_read_only",
        '"commercial_status_api_v0_1"] = True',
        '"read_only_commercial_status_api"] = True',
        '"task_candidates_executed"] = False',
        '"blockers_closed_by_route"] = 0',
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
        "commercial_router",
        'prefix="/commercial"',
        'tags=["commercial"]',
    ]
    missing_main = [token for token in main_tokens if token not in main]
    require(not missing_main, "main.py missing tokens: " + ", ".join(missing_main))

    report = evaluate_commercial_go_no_go(load_settings({}))
    require(report["commercial_status"] == "hold", "default commercial status must be hold")
    require(
        report["production_launch_status"] == "hold",
        "default production launch status must be hold",
    )
    require(
        report["production_blocker_count"] > 0,
        "default report must retain production blockers",
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
        ],
    )

    required_doc_tokens = [
        "commercial_status_api_v0_1: true",
        "commercial_status_api_available: true",
        "read_only_commercial_status_api: true",
        "commercial_status_route: GET /commercial/status",
        "route_scope: public_shell_commercial_read_only",
        "commercial_status: hold",
        "production_launch_status: hold",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "public_sdk_released: false",
        "private_core_exposed: false",
        "task_candidates_executed: false",
        "blockers_closed_by_route: 0",
        "body_inspected: false",
        "credentials_inspected: false",
        "private_core_inspected: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_controlled_preview_commercial_status_review: true",
        "recommend_for_production_launch: false",
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
        response = client.get("/commercial/status")
        require(response.status_code == 200, "commercial status route must return 200")
        payload = response.json()
        require(
            payload["route_scope"] == "public_shell_commercial_read_only",
            "commercial route scope mismatch",
        )
        require(payload["commercial_status"] == "hold", "route status must remain hold")
        require(payload["production_launch_status"] == "hold", "route launch status hold")
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
            ],
        )

    print(
        "SAEE_COMMERCIAL_STATUS_API_SMOKE: PASS "
        "route=/commercial/status read_only=true commercial_status=hold "
        "blockers_closed_by_route=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
