#!/usr/bin/env python3
"""Smoke check for the SAEE pricing page copy draft."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_COPY_DRAFT_V0_1.md"
DRAFT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft.local.json"
)
DRAFT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft.md"
)
BOUNDARY_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft_boundary_audit.md"
)
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_COPY_DRAFT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRICING_PAGE_COPY_DRAFT_SMOKE: FAIL " + message)


def main() -> int:
    for path in [TOP_DOC, DRAFT_JSON, DRAFT_MD, BOUNDARY_AUDIT, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    draft = json.loads(DRAFT_JSON.read_text(encoding="utf-8"))
    expected = {
        "draft_type": "saee_pricing_page_copy_draft",
        "draft_version": "v0.1",
        "draft_status": "draft_not_approved",
        "review_scope": "pricing_page_copy_draft_for_human_review_only",
        "blocker_target": "pricing_page",
        "draft_copy_available": True,
        "human_review_required": True,
        "separate_publication_approval_required": True,
        "separate_payment_enablement_approval_required": True,
        "blocker_closure_allowed_by_draft": False,
        "pricing_page_evidence_complete": False,
        "pricing_page_approved": False,
        "human_approved_pricing_page_copy": False,
        "approved_plan_and_usage_terms": False,
        "pricing_page_publication_approval_recorded": False,
        "pricing_page_published": False,
        "public_price_points_approved": False,
        "sales_offer_sent": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "payment_link_created": False,
        "invoice_sent_to_customer": False,
        "tax_collection_started": False,
        "customer_payment_collected": False,
        "paid_product_launched": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "production_billing_revenue_ready": False,
        "landing_page_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "production_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(draft.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "headline_and_positioning",
        "target_buyer_and_use_case_boundary",
        "package_cards",
        "internal_price_band_placeholders",
        "usage_units_and_limits",
        "controlled_preview_terms",
        "non_production_ready_disclaimer",
        "what_saee_is_not",
        "private_core_exclusion",
        "legal_tax_payment_handoff",
        "publication_approval_record",
    }
    require(required_sections <= set(draft.get("copy_sections", [])), "missing copy sections")
    require(len(draft.get("plan_candidates", [])) == 3, "expected three plan candidates")
    for plan in draft.get("plan_candidates", []):
        require(plan.get("customer_facing_offer") is False, "plan must not be a customer offer")
        require("internal_review_placeholder" in plan.get("price_display", ""), "price display must be placeholder")

    combined = "\n".join(
        [
            TOP_DOC.read_text(encoding="utf-8"),
            DRAFT_MD.read_text(encoding="utf-8"),
            BOUNDARY_AUDIT.read_text(encoding="utf-8"),
            GATE.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "pricing_page_copy_draft_v0_1: true",
        "draft_type: saee_pricing_page_copy_draft",
        "draft_status: draft_not_approved",
        "review_scope: pricing_page_copy_draft_for_human_review_only",
        "blocker_closure_allowed_by_draft: false",
        "pricing_page_evidence_complete: false",
        "pricing_page_published: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_copy_review: true",
        "recommend_for_public_pricing_claim: false",
        "recommend_for_pricing_page_publication: false",
        "recommend_for_payment_enablement: false",
        "recommend_for_blocker_closure: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing tokens: " + ", ".join(missing))

    forbidden_tokens = [
        "pricing_page_evidence_complete: true",
        '"pricing_page_evidence_complete": true',
        "pricing_page_published: true",
        '"pricing_page_published": true',
        "sales_offer_sent: true",
        '"sales_offer_sent": true',
        "payment_provider_configured: true",
        '"payment_provider_configured": true',
        "checkout_enabled: true",
        '"checkout_enabled": true',
        "customer_payment_collected: true",
        '"customer_payment_collected": true',
        "revenue_validated: true",
        '"revenue_validated": true',
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "recommend_for_blocker_closure: true",
        "recommend_for_payment_enablement: true",
        "recommend_for_pricing_page_publication: true",
        "recommend_for_production_readiness_claim: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRICING_PAGE_COPY_DRAFT_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft_boundary_audit.md",
        "/docs/strategy/SAEE_PRICING_PAGE_COPY_DRAFT_RECOMMENDATION_GATE.md",
        "/scripts/saee_pricing_page_copy_draft.py",
        "/scripts/saee_pricing_page_copy_draft_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("pricing_page_copy_draft_v0_1", {})
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRICING_PAGE_COPY_DRAFT_SMOKE: PASS "
        "draft_not_approved=true pricing_page_evidence_complete=false "
        "pricing_page_published=false production_ready=false private_core_exposed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
