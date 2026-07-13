#!/usr/bin/env python3
"""Smoke check for SAEE Preview Readiness API v0.1."""

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
from saee_backend.services.support_readiness import evaluate_support_readiness
from saee_backend.services.vulnerability_management_readiness import (
    evaluate_vulnerability_management_readiness,
)


ROUTE_PATH = ROOT / "saee_backend/api/readiness.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PREVIEW_READINESS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PREVIEW_READINESS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PREVIEW_READINESS_API_SMOKE: FAIL: {message}")


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
        "evaluate_support_readiness",
        "evaluate_vulnerability_management_readiness",
        '"/support"',
        'require_rbac_route("GET /readiness/support")',
        '"/vulnerability"',
        'require_rbac_route("GET /readiness/vulnerability")',
        "public_shell_preview_readiness_read_only",
        '"support_contact_value_exposed"] = False',
        '"security_contact_value_exposed"] = False',
        '"customer_support_available"] = False',
        '"production_support_available"] = False',
        '"vulnerability_management_available"] = False',
        '"production_vulnerability_management_ready"] = False',
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

    support = evaluate_support_readiness(
        load_settings({"SAEE_ENV": "preview", "SAEE_SUPPORT_CONTACT": "support@example.invalid"})
    )
    require(support["support_contact_configured"] is True, "configured support contact must be true")
    assert_false(
        support,
        [
            "customer_support_available",
            "production_support_available",
            "support_process_available",
            "sla_available",
            "on_call_rotation_available",
            "production_operations_ready",
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "external_calls_made",
            "customer_contacted",
        ],
    )

    vulnerability = evaluate_vulnerability_management_readiness(
        load_settings({"SAEE_ENV": "preview", "SAEE_SECURITY_CONTACT": "security@example.invalid"})
    )
    require(
        vulnerability["security_contact_configured"] is True,
        "configured security contact must be true",
    )
    assert_false(
        vulnerability,
        [
            "vulnerability_management_available",
            "production_vulnerability_management_ready",
            "formal_security_review_completed",
            "production_security_ready",
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "external_calls_made",
            "external_model_api_called",
            "customer_contacted",
        ],
    )

    required_doc_tokens = [
        "preview_readiness_api_v0_1: true",
        "preview_readiness_api_available: true",
        "read_only_preview_readiness_api: true",
        "preview_readiness_routes_available: true",
        "route_scope: public_shell_preview_readiness_read_only",
        "support_route: /readiness/support",
        "vulnerability_route: /readiness/vulnerability",
        "support_contact_value_exposed: false",
        "security_contact_value_exposed: false",
        "request_body_inspected: false",
        "response_body_inspected: false",
        "credentials_inspected: false",
        "private_core_inspected: false",
        "customer_support_available: false",
        "production_support_available: false",
        "sla_available: false",
        "on_call_rotation_available: false",
        "vulnerability_management_available: false",
        "production_vulnerability_management_ready: false",
        "formal_security_review_completed: false",
        "production_security_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "public_sdk_released: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "external_model_api_called: false",
        "customer_contacted: false",
        "answer: conditional",
        "recommend_for_controlled_preview_readiness_review: true",
        "recommend_for_production_support: false",
        "recommend_for_production_security_operations: false",
        "recommend_for_public_launch_now: false",
    ]
    missing_doc = [token for token in required_doc_tokens if token not in combined]
    require(not missing_doc, "doc/gate missing tokens: " + ", ".join(missing_doc))

    forbidden_tokens = [
        "support_contact_value_exposed: true",
        '"support_contact_value_exposed": true',
        "security_contact_value_exposed: true",
        '"security_contact_value_exposed": true',
        "customer_support_available: true",
        '"customer_support_available": true',
        "production_support_available: true",
        '"production_support_available": true',
        "sla_available: true",
        '"sla_available": true',
        "on_call_rotation_available: true",
        '"on_call_rotation_available": true',
        "vulnerability_management_available: true",
        '"vulnerability_management_available": true',
        "production_vulnerability_management_ready: true",
        '"production_vulnerability_management_ready": true',
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    if importlib.util.find_spec("fastapi") and importlib.util.find_spec("starlette"):
        from fastapi.testclient import TestClient
        from saee_backend.main import app

        client = TestClient(app)
        support_response = client.get("/readiness/support")
        require(support_response.status_code == 200, "support route must return 200")
        support_payload = support_response.json()
        require(
            support_payload["route_scope"] == "public_shell_preview_readiness_read_only",
            "support route scope mismatch",
        )
        require(
            support_payload["support_contact_value_exposed"] is False,
            "support route must not expose contact value",
        )
        vulnerability_response = client.get("/readiness/vulnerability")
        require(vulnerability_response.status_code == 200, "vulnerability route must return 200")
        vulnerability_payload = vulnerability_response.json()
        require(
            vulnerability_payload["route_scope"] == "public_shell_preview_readiness_read_only",
            "vulnerability route scope mismatch",
        )
        require(
            vulnerability_payload["security_contact_value_exposed"] is False,
            "vulnerability route must not expose contact value",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/PREVIEW_READINESS_API_V0_1.md",
        "/docs/strategy/SAEE_PREVIEW_READINESS_API_RECOMMENDATION_GATE.md",
        "/saee_backend/api/readiness.py",
        "/scripts/saee_preview_readiness_api_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("preview_readiness_api_v0_1", {})
    expected_index = {
        "status": "local_precommercial_read_only_preview_readiness_api",
        "preview_readiness_api_v0_1": True,
        "preview_readiness_api_available": True,
        "read_only_preview_readiness_api": True,
        "preview_readiness_routes_available": True,
        "support_contact_value_exposed": False,
        "security_contact_value_exposed": False,
        "customer_support_available": False,
        "production_support_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "vulnerability_management_available": False,
        "production_vulnerability_management_ready": False,
        "formal_security_review_completed": False,
        "production_security_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
    }
    for key, expected in expected_index.items():
        require(entry.get(key) == expected, f"agent-index preview_readiness_api_v0_1 {key}")

    print(
        "SAEE_PREVIEW_READINESS_API_SMOKE: PASS "
        "preview_readiness_api_available=true "
        "routes=/readiness/support,/readiness/vulnerability "
        "read_only=true "
        "contact_values_exposed=false "
        "customer_support_available=false "
        "vulnerability_management_available=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
