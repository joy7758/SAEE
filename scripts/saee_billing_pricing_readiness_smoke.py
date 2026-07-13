#!/usr/bin/env python3
"""Smoke check for SAEE Billing / Pricing Readiness v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.billing_pricing_readiness import (
    evaluate_billing_pricing_readiness,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_BILLING_PRICING_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_BILLING_PRICING_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_billing_pricing_readiness(load_settings({}))
    require(
        local["billing_pricing_readiness_type"]
        == "controlled_preview_billing_pricing_readiness",
        "wrong readiness type",
    )
    require(local["billing_pricing_readiness_v0_1"] is True, "readiness marker")
    require(local["billing_pricing_status"] == "hold", "billing readiness must hold")
    require(local["pricing_packaging_plan_available"] is True, "pricing plan available")
    require(local["internal_price_bands_available"] is True, "internal price bands available")
    require(local["billing_policy_draft_available"] is True, "billing policy draft")
    require(local["pricing_page_published"] is False, "pricing page false")
    require(local["sales_offer_sent"] is False, "sales offer false")
    require(local["paid_product_launched"] is False, "paid launch false")
    require(local["enterprise_contract_signed"] is False, "contract false")
    require(local["payment_provider_configured"] is False, "payment provider false")
    require(local["checkout_enabled"] is False, "checkout false")
    require(local["invoice_process_ready"] is False, "invoice false")
    require(local["tax_review_completed"] is False, "tax review false")
    require(local["refund_policy_available"] is False, "refund false")
    require(local["billing_operations_ready"] is False, "billing ops false")
    require(local["tenant_billing_isolated"] is False, "tenant billing false")
    require(local["customer_payment_collected"] is False, "payment collected false")
    require(local["paid_pilot_completed"] is False, "paid pilot false")
    require(local["revenue_validated"] is False, "revenue false")
    require(local["product_market_fit_claimed"] is False, "PMF false")
    require(local["production_readiness_claimed"] is False, "production claim false")
    require(local["customer_contacted"] is False, "customer contact false")
    require(local["customer_validated"] is False, "customer validation false")
    require(local["product_launched"] is False, "product launch false")
    require(local["production_ready"] is False, "production ready false")
    require(local["private_core_exposed"] is False, "private core false")
    require(local["api_schema_modified"] is False, "API schema false")
    require(local["runtime_modified"] is False, "runtime false")
    require(local["kernel_modified"] is False, "kernel false")
    require(local["external_calls_made"] is False, "external calls false")
    require(finding(local, "published_price_missing")["passed"] is False, "price missing blocks")
    require(finding(local, "payment_provider_missing")["passed"] is False, "payment missing blocks")
    require(
        finding(local, "revenue_validation_non_claim")["passed"] is False,
        "revenue missing blocks",
    )

    payload = load_settings({}).readiness_payload()
    require(payload["billing_pricing_readiness_v0_1"] is True, "ready payload readiness")
    require(payload["billing_pricing_status"] == "hold", "ready payload hold")
    require(payload["pricing_page_published"] is False, "ready payload pricing false")
    require(payload["payment_provider_configured"] is False, "ready payload provider false")
    require(payload["checkout_enabled"] is False, "ready payload checkout false")
    require(payload["invoice_process_ready"] is False, "ready payload invoice false")
    require(payload["revenue_validated"] is False, "ready payload revenue false")
    require(payload["customer_payment_collected"] is False, "ready payload payment false")
    require(payload["customer_validated"] is False, "ready payload customer false")

    doc = (
        ROOT / "phase_b_product/commercial_readiness/BILLING_PRICING_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_BILLING_PRICING_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    source = (ROOT / "phase_b_product/mvp/MVP_PRICING_AND_PACKAGING.md").read_text(
        encoding="utf-8"
    )
    require("billing_pricing_readiness_v0_1: true" in doc, "doc missing state")
    require("billing_pricing_status: hold" in doc, "doc hold")
    require("pricing_page_published: false" in doc, "doc pricing false")
    require("payment_provider_configured: false" in doc, "doc payment false")
    require("checkout_enabled: false" in doc, "doc checkout false")
    require("invoice_process_ready: false" in doc, "doc invoice false")
    require("tax_review_completed: false" in doc, "doc tax false")
    require("revenue_validated: false" in doc, "doc revenue false")
    require("answer: conditional" in gate, "gate conditional")
    require("recommend_public_launch_now: false" in gate, "gate no launch")
    require("pricing_page_published: false" in source, "source pricing false")
    require("sales_offer_sent: false" in source, "source offer false")

    print(
        "SAEE_BILLING_PRICING_READINESS_SMOKE: PASS "
        "billing_pricing_readiness_v0_1=true "
        "pricing_page_published=false "
        "payment_provider_configured=false "
        "revenue_validated=false "
        "customer_validated=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
