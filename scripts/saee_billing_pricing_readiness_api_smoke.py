#!/usr/bin/env python3
"""Smoke check for SAEE Billing / Pricing Readiness API v0.1."""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.billing_pricing_readiness import (
    evaluate_billing_pricing_readiness,
)


ROUTE_PATH = ROOT / "saee_backend/api/readiness.py"
MAIN_PATH = ROOT / "saee_backend/main.py"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/BILLING_PRICING_READINESS_API_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_BILLING_PRICING_READINESS_API_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_BILLING_PRICING_READINESS_API_SMOKE: FAIL: {message}")


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
        "evaluate_billing_pricing_readiness",
        '"/billing-pricing"',
        'require_rbac_route("GET /readiness/billing-pricing")',
        "public_shell_billing_pricing_readiness_read_only",
        '"billing_pricing_readiness_api_v0_1"] = True',
        '"read_only_billing_pricing_readiness_api"] = True',
        '"task_candidates_executed"] = False',
        '"blockers_closed_by_route"] = 0',
        '"payment_provider_contacted_by_route"] = False',
        '"checkout_created_by_route"] = False',
        '"invoice_created_by_route"] = False',
        '"payment_credentials_inspected"] = False',
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

    report = evaluate_billing_pricing_readiness(load_settings({}))
    require(report["billing_pricing_status"] == "hold", "default billing status must be hold")
    require(report["pricing_page_published"] is False, "default pricing page false")
    require(
        report["payment_provider_configured"] is False,
        "default payment provider false",
    )
    require(report["checkout_enabled"] is False, "default checkout false")
    require(report["invoice_process_ready"] is False, "default invoice false")
    require(report["tax_review_completed"] is False, "default tax review false")
    require(report["refund_policy_available"] is False, "default refund false")
    require(report["tenant_billing_isolated"] is False, "default tenant billing false")
    require(report["revenue_validated"] is False, "default revenue false")
    assert_false(
        report,
        [
            "pricing_page_published",
            "sales_offer_sent",
            "paid_product_launched",
            "enterprise_contract_signed",
            "payment_provider_configured",
            "checkout_enabled",
            "invoice_process_ready",
            "tax_review_completed",
            "refund_policy_available",
            "billing_operations_ready",
            "tenant_billing_isolated",
            "customer_payment_collected",
            "paid_pilot_completed",
            "revenue_validated",
            "product_market_fit_claimed",
            "production_readiness_claimed",
            "production_ready",
            "customer_validated",
            "customer_contacted",
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
        "billing_pricing_readiness_api_v0_1: true",
        "billing_pricing_readiness_api_available: true",
        "read_only_billing_pricing_readiness_api: true",
        "billing_pricing_readiness_route: GET /readiness/billing-pricing",
        "route_scope: public_shell_billing_pricing_readiness_read_only",
        "billing_pricing_status_default: hold",
        "pricing_page_published_default: false",
        "payment_provider_configured_default: false",
        "checkout_enabled_default: false",
        "invoice_process_ready_default: false",
        "tax_review_completed_default: false",
        "refund_policy_available_default: false",
        "tenant_billing_isolated_default: false",
        "customer_payment_collected_default: false",
        "revenue_validated_default: false",
        "blockers_closed_by_route: 0",
        "task_candidates_executed: false",
        "payment_provider_contacted_by_route: false",
        "checkout_created_by_route: false",
        "invoice_created_by_route: false",
        "payment_credentials_inspected: false",
        "body_inspected: false",
        "credentials_inspected: false",
        "private_core_inspected: false",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "product_launched: false",
        "public_sdk_released: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_controlled_preview_billing_pricing_readiness_review: true",
        "recommend_for_payment_provider_configuration: false",
        "recommend_for_checkout_creation: false",
        "recommend_for_invoice_creation: false",
        "recommend_for_pricing_publication: false",
        "recommend_for_revenue_validation_claim: false",
        "recommend_for_public_launch_now: false",
    ]
    missing_doc = [token for token in required_doc_tokens if token not in combined]
    require(not missing_doc, "doc/gate missing tokens: " + ", ".join(missing_doc))

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "customer_contacted: true",
        '"customer_contacted": true',
        "product_launched: true",
        '"product_launched": true',
        "public_sdk_released: true",
        '"public_sdk_released": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "task_candidates_executed: true",
        '"task_candidates_executed": true',
        "payment_provider_contacted_by_route: true",
        '"payment_provider_contacted_by_route": true',
        "checkout_created_by_route: true",
        '"checkout_created_by_route": true',
        "invoice_created_by_route: true",
        '"invoice_created_by_route": true',
        "payment_credentials_inspected: true",
        '"payment_credentials_inspected": true',
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
        response = client.get("/readiness/billing-pricing")
        require(response.status_code == 200, "billing-pricing route must return 200")
        payload = response.json()
        require(
            payload["route_scope"] == "public_shell_billing_pricing_readiness_read_only",
            "billing-pricing route scope mismatch",
        )
        require(payload["billing_pricing_status"] == "hold", "route status must remain hold")
        require(payload["pricing_page_published"] is False, "route pricing page false")
        require(
            payload["payment_provider_configured"] is False,
            "route payment provider false",
        )
        require(payload["revenue_validated"] is False, "route revenue false")
        require(payload["blockers_closed_by_route"] == 0, "route must close zero blockers")
        require(payload["task_candidates_executed"] is False, "route must execute no tasks")
        assert_false(
            payload,
            [
                "production_ready",
                "customer_validated",
                "customer_contacted",
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
                "payment_credentials_inspected",
                "payment_provider_contacted_by_route",
                "checkout_created_by_route",
                "invoice_created_by_route",
            ],
        )

    print(
        "SAEE_BILLING_PRICING_READINESS_API_SMOKE: PASS "
        "route=/readiness/billing-pricing read_only=true status=hold "
        "blockers_closed_by_route=0 production_ready=false revenue_validated=false"
    )


if __name__ == "__main__":
    main()
