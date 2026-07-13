#!/usr/bin/env python3
"""Generate the SAEE pricing page copy draft.

This creates a local, documentation-only pricing page copy draft for human
review. It does not publish pricing, create a sales offer, configure payment,
enable checkout, contact customers, collect payment, or mark SAEE
production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_COPY_DRAFT_V0_1.md"
DRAFT_JSON = OUTPUT_DIR / "pricing_page_copy_draft.local.json"
DRAFT_MD = OUTPUT_DIR / "pricing_page_copy_draft.md"
BOUNDARY_AUDIT = OUTPUT_DIR / "pricing_page_copy_draft_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_COPY_DRAFT_RECOMMENDATION_GATE.md"


COPY_SECTIONS = [
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
]

PLAN_CANDIDATES = [
    {
        "plan_id": "controlled_preview",
        "plan_name": "Controlled Preview",
        "intended_use": "Local evaluation demos, academic exploration, and design-partner review.",
        "price_display": "internal_review_placeholder_only",
        "price_source": "MVP_PRICING_AND_PACKAGING.md free tier concept",
        "customer_facing_offer": False,
    },
    {
        "plan_id": "pro_team_review",
        "plan_name": "Pro Team Review",
        "intended_use": "Team-level multi-agent evaluation, saved reports, exports, and scenario packs.",
        "price_display": "99-499 USD/month internal_review_placeholder_not_public_offer",
        "price_source": "MVP_PRICING_AND_PACKAGING.md target price band",
        "customer_facing_offer": False,
    },
    {
        "plan_id": "enterprise_private_review",
        "plan_name": "Enterprise Private Review",
        "intended_use": "Private deployment review, custom scenarios, onboarding, and support review.",
        "price_display": "20k-200k USD/year internal_review_placeholder_not_public_offer",
        "price_source": "MVP_PRICING_AND_PACKAGING.md target price band",
        "customer_facing_offer": False,
    },
]

BOUNDARY_FLAGS = {
    "draft_copy_available": True,
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
    "paid_pilot_completed": False,
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
}


def build_draft() -> dict[str, Any]:
    return {
        "draft_type": "saee_pricing_page_copy_draft",
        "draft_version": "v0.1",
        "draft_status": "draft_not_approved",
        "review_scope": "pricing_page_copy_draft_for_human_review_only",
        "blocker_target": "pricing_page",
        "generated_by": "scripts/saee_pricing_page_copy_draft.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_inputs": [
            "phase_b_product/mvp/MVP_PRICING_AND_PACKAGING.md",
            "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.md",
        ],
        "copy_sections": COPY_SECTIONS,
        "plan_candidates": PLAN_CANDIDATES,
        "positioning": {
            "primary_wedge": "AI agent evaluation and policy stress testing",
            "primary_message": "We test which AI agents survive long-term competition.",
            "recommended_for": [
                "long_term_stability_evaluation",
                "multi_agent_comparison",
                "failure_mode_analysis",
                "survival_curve_evaluation",
                "deployment_recommendation",
            ],
            "not_recommended_for": [
                "generic_tracing_only",
                "prompt_only_evaluation",
                "production_monitoring_replacement",
                "full_quant_trading_platform",
                "public_open_source_evolution_kernel",
            ],
        },
        "human_review_required": True,
        "separate_publication_approval_required": True,
        "separate_payment_enablement_approval_required": True,
        "blocker_closure_allowed_by_draft": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        **BOUNDARY_FLAGS,
    }


def render_plan_cards(draft: dict[str, Any]) -> str:
    blocks: list[str] = []
    for plan in draft["plan_candidates"]:
        blocks.append(
            "\n".join(
                [
                    f"### {plan['plan_name']}",
                    "",
                    f"- plan_id: {plan['plan_id']}",
                    f"- intended_use: {plan['intended_use']}",
                    f"- price_display: {plan['price_display']}",
                    f"- price_source: {plan['price_source']}",
                    "- customer_facing_offer: false",
                ]
            )
        )
    return "\n\n".join(blocks)


def render_copy_draft(draft: dict[str, Any]) -> str:
    sections = "\n".join(f"- {section}" for section in draft["copy_sections"])
    recommended = "\n".join(
        f"- {item}" for item in draft["positioning"]["recommended_for"]
    )
    not_recommended = "\n".join(
        f"- {item}" for item in draft["positioning"]["not_recommended_for"]
    )
    boundary = "\n".join(
        f"- {key}: {str(value).lower()}" for key, value in BOUNDARY_FLAGS.items()
    )
    plan_cards = render_plan_cards(draft)

    return f"""# SAEE Pricing Page Copy Draft v0.1

Status: draft not approved.

This is a documentation-only pricing page copy draft for human review. It is
not a public pricing page, not a sales offer, not payment configuration, and
not production billing evidence.

## Scope

```yaml
draft_type: {draft['draft_type']}
draft_status: {draft['draft_status']}
review_scope: {draft['review_scope']}
blocker_target: {draft['blocker_target']}
human_review_required: true
separate_publication_approval_required: true
separate_payment_enablement_approval_required: true
blocker_closure_allowed_by_draft: false
pricing_page_evidence_complete: false
pricing_page_published: false
production_billing_revenue_ready: false
production_ready: false
```

## Draft Page Copy

### Headline

SAEE evaluates which AI agents, workflows, and decision policies remain stable
under long-horizon competitive testing.

### Supporting Copy

Use SAEE when the question is not just whether one prompt works once, but
which agent or policy version remains more stable across repeated simulation,
competition, failure-mode review, survival-curve analysis, and deployment
recommendation.

### Primary Wedge

AI agent evaluation and policy stress testing.

### Recommended For

{recommended}

### Not Recommended For

{not_recommended}

## Draft Package Cards

The following package cards are internal review placeholders. They are not
approved public offers and must not be published without separate human,
commercial, legal, tax, and payment review.

{plan_cards}

## Usage Units for Review

- scenario runs
- evaluated episodes
- saved reports
- seats
- retention window

## Current Product Boundary

SAEE is a local MVP and controlled-preview candidate. It is not production
ready, not customer validated, not a public SDK, and not a hosted paid product.

## Private Core Boundary

The pricing page must not expose private core, kernel internals, fitness
logic, selection logic, mutation logic, lineage internals, or runtime
implementation details.

## Required Copy Sections

{sections}

## Boundary Flags

{boundary}

## Non-Approval Statement

This draft can help a human reviewer decide what a future pricing page might
say. It does not close the `pricing_page` blocker and does not authorize
publication, payment collection, customer contact, launch, or production
readiness claims.
"""


def render_top_doc(draft: dict[str, Any]) -> str:
    return f"""# SAEE Pricing Page Copy Draft v0.1

Status: draft not approved; human review required.

This top-level note records that a pricing page copy draft exists for the
`pricing_page` commercial blocker. The draft is documentation-only and does
not publish pricing, create a sales offer, configure payment, enable checkout,
contact customers, collect payment, validate revenue, launch product, or make
SAEE production-ready.

```yaml
pricing_page_copy_draft_v0_1: true
draft_type: {draft['draft_type']}
draft_status: {draft['draft_status']}
review_scope: {draft['review_scope']}
blocker_target: {draft['blocker_target']}
draft_copy_available: true
human_review_required: true
separate_publication_approval_required: true
separate_payment_enablement_approval_required: true
blocker_closure_allowed_by_draft: false
pricing_page_evidence_complete: false
pricing_page_approved: false
human_approved_pricing_page_copy: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_configured: false
checkout_enabled: false
customer_payment_collected: false
revenue_validated: false
production_billing_revenue_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Review Purpose

The draft turns the existing internal packaging plan into a page-shaped copy
surface that product, commercial, legal, tax, and payment owners can review.
It improves reviewability only. It does not create public evidence that a
pricing page is approved or live.

## Source Inputs

- `phase_b_product/mvp/MVP_PRICING_AND_PACKAGING.md`
- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.md`

## Next Human Action

Review the draft copy in
`phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft.md`.
If publication is desired later, create a separate explicit publication and
payment-readiness approval request.
"""


def render_boundary_audit() -> str:
    return """# SAEE Pricing Page Copy Draft Boundary Audit

Final boundary decision: draft for human review only.

- Only documentation / pricing copy draft materials were created.
- No public pricing page was published.
- No sales offer was created.
- No payment provider was configured.
- No checkout was enabled.
- No payment link was created.
- No invoice was sent.
- No tax collection was started.
- No customer payment was collected.
- No revenue was validated.
- No product was launched.
- No customer was contacted.
- No customer validation was claimed.
- No production-ready claim was added.
- No landing page was modified.
- No runtime was modified.
- No backend was modified.
- No kernel was modified.
- No API schema was modified.
- No private core was exposed.

This draft does not close the `pricing_page` blocker. Separate human approval
is required before any public pricing page, sales offer, payment collection,
or production billing evidence can exist.
"""


def render_gate() -> str:
    return """# SAEE Pricing Page Copy Draft Recommendation Gate

answer: conditional

recommend_for_human_copy_review: true
recommend_for_public_pricing_claim: false
recommend_for_pricing_page_publication: false
recommend_for_sales_offer: false
recommend_for_payment_enablement: false
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The draft improves the human-review surface for the `pricing_page` blocker by
turning internal packaging notes into conservative page-shaped copy. It remains
documentation-only and does not authorize publication, payment, customer
contact, blocker closure, launch, or production readiness claims.

## Boundary

```yaml
draft_copy_available: true
pricing_page_evidence_complete: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_configured: false
checkout_enabled: false
customer_payment_collected: false
revenue_validated: false
production_billing_revenue_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Next Action

Human reviewers may review the copy draft. Publishing or payment enablement
requires a separate explicit approval request.
"""


def write_outputs(draft: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_JSON.write_text(
        json.dumps(draft, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    DRAFT_MD.write_text(render_copy_draft(draft), encoding="utf-8")
    TOP_DOC.write_text(render_top_doc(draft), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary_audit(), encoding="utf-8")
    GATE.write_text(render_gate(), encoding="utf-8")


def main() -> None:
    draft = build_draft()
    write_outputs(draft)
    print(
        "SAEE_PRICING_PAGE_COPY_DRAFT: PASS "
        f"path={DRAFT_JSON} status={draft['draft_status']} "
        "pricing_page_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
