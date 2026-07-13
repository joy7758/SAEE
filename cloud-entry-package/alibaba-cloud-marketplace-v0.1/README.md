# SAEE Alibaba Cloud Marketplace Entry Package v0.1

## Live platform state

- Marketplace draft commodity ID: `68657`.
- Product access information completed: `服务类`, SPI notification `否`,
  public `最简服务流`, and the provider company as the delivery provider.
- Product basic information is saved, including the main image, logo,
  introduction, four highlights, product detail, PDF guide, after-sales copy,
  and the 16:9 architecture diagram.
- Current handoff: business information is saved. On the sales-information
  page, PAY_PER_USE, enterprise-only=false, SKU `单工作流单场景首发评估`, and
  RMB 999 are entered. The required validity control remains at its pre-existing
  `1年` selection and is not owner-approved, so the page is not saved. Final
  product submission remains a separate gate.
- `marketplace_product_submission=false`, `marketplace_product_listed=false`,
  and `production_ready=false`.

This is a local, agent-readable preparation package for the first bounded SAEE
Alibaba Cloud Marketplace product. It does not submit a cooperation product,
apply for certification, create a Marketplace listing, or authorize production
delivery.

## Proposed first product

```text
Name: SAEE Agent Readiness Assessment
Chinese name: SAEE 智能体上线可靠性评估服务
Preferred access type: service / human-delivered
Scope: one Agent workflow + one scenario + approved, sanitized execution evidence
Outputs: JSON and human-readable assessment report
Allowed recommendations: CONTINUE, REPLAN, HUMAN_REVIEW_REQUIRED, STOP
```

The product evaluates execution-evidence sufficiency. It does not certify
compliance, guarantee safety, authorize deployment, execute an external system,
or rank Agents universally.

## Files

- `listing-draft.json`: machine-readable Marketplace copy and open owner inputs.
- `cooperation-product-proposal.json`: draft for the product-ecosystem
  cooperation-product route that precedes certification and Marketplace
  association.
- `delivery-sop.md`: bounded order-to-delivery and rollback workflow.
- `store-profile-draft.json`: machine-readable store copy, customer-service
  hours, public asset paths, and private-contact boundaries.
- `seo-listing-copy.v0.1.json`: official-rule-backed product title, summary,
  highlights, tags, SEO keywords, search description, agent recommendation,
  and claim boundaries.
- `product-detail-draft.md`: plain-language product detail copy for customers
  and retrieval agents.
- `service-user-guide.md`: source for the required Marketplace PDF guide.
- `sales-pricing.v0.1.json`: owner-authorized RMB 999 per-use initial SKU;
  not yet saved or published on the Marketplace.
- Marketplace delivery bridge:
  `docs/commercial/SAEE_ALIBABA_MARKETPLACE_DELIVERY_BRIDGE_V0_1.md`.
- Marketplace intake, bundle, and receipt schemas:
  `agent-interface/commercial/saee-marketplace-*.schema.v0.1.json`.
- Delivery bridge validation:
  `python3 scripts/saee_marketplace_assessment_delivery_smoke.py`.
- `assets/store-logo-180x120.png`: 3:2 public store logo.
- `assets/store-banner-920x518.png`: public store banner derived from the local
  SAEE landing-page capture.
- `assets/product-main-1280x720.png`: 16:9 product-related main image.
- `assets/product-logo-310x310.png`: square product logo.
- `assets/product-architecture-1600x900.svg`: agent-readable architecture
  source with explicit role, title, and description metadata.
- `assets/product-architecture-1600x900.png`: 16:9 Marketplace architecture
  image uploaded to draft `68657`.
- Readiness truth:
  `agent-interface/ecosystem/saee-alibaba-cloud-marketplace-entry-readiness.v1.json`.
- Recommendation gate:
  `docs/strategy/SAEE_ALIBABA_CLOUD_MARKETPLACE_ENTRY_READINESS_RECOMMENDATION_GATE.md`.
- Validation:
  `python3 scripts/saee_alibaba_cloud_marketplace_entry_readiness_smoke.py`.
- SEO listing validation:
  `python3 scripts/saee_alibaba_cloud_marketplace_seo_listing_smoke.py`.
- PDF guide generation:
  `python3 scripts/saee_alibaba_marketplace_service_user_guide_pdf.py`.

## Current gate

```text
local_listing_package_ready=true
marketplace_category_qualification_completed=true
enterprise_settlement_account_activation_completed=true
alibaba_cloud_withholding_authorization_completed=true
publish_product_action_blocked_by_startup_guide=false
publish_product_entry_unblocked=true
store_profile_submission=true
product_type_selection_page_opened=true
product_type_owner_selected=true
cooperation_product_submission=false
integration_certification_application_submission=false
bailian_tested=false
marketplace_product_draft_created=true
marketplace_product_basic_info_saved=true
marketplace_product_business_info_form_fill_authorized=true
marketplace_product_business_info_saved=true
marketplace_product_sales_information_opened=true
marketplace_product_submission=false
marketplace_product_listed=false
public_price_points_approved=true
marketplace_sales_information_form_fields_entered=true
marketplace_sales_information_saved=false
customer_validated=false
production_ready=false
```

The saved business information uses no service-region
restriction, category `AI应用及服务市场 / AI应用`, delivery method `人工服务`,
application object `企业`, application scenario `应用开发`, and tags `数据智能`
and `数据分析`. Delivery time and warranty time remain empty because no
owner-approved commitment exists. The sales-information page is open. The
RMB 999 per-use launch price and SKU are entered but are not yet saved or
public. The next gate is owner confirmation of the required validity; `1年` is
only the current UI default, not an approved commitment. Agreements,
cooperation-product submission,
certification, Marketplace submission, and listing remain separate gates.
