#!/usr/bin/env python3
"""Validate the local Alibaba Cloud Marketplace entry-readiness package."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "agent-interface/ecosystem/saee-alibaba-cloud-marketplace-entry-readiness.v1.json"
PACKAGE = ROOT / "cloud-entry-package/alibaba-cloud-marketplace-v0.1"
LISTING = PACKAGE / "listing-draft.json"
PROPOSAL = PACKAGE / "cooperation-product-proposal.json"
SOP = PACKAGE / "delivery-sop.md"
STORE_PROFILE = PACKAGE / "store-profile-draft.json"
SUBMISSION_OBSERVATION = PACKAGE / "submission-observation.v0.1.json"
STORE_LOGO = PACKAGE / "assets/store-logo-180x120.png"
STORE_BANNER = PACKAGE / "assets/store-banner-920x518.png"
SEO_COPY = PACKAGE / "seo-listing-copy.v0.1.json"
PRODUCT_DETAIL = PACKAGE / "product-detail-draft.md"
PRODUCT_MAIN_IMAGE = PACKAGE / "assets/product-main-1280x720.png"
PRODUCT_LOGO = PACKAGE / "assets/product-logo-310x310.png"
PRODUCT_USAGE_GUIDE = ROOT / "output/pdf/SAEE_Alibaba_Cloud_Marketplace_Agent_Readiness_Service_User_Guide_v0.1.pdf"
PRODUCT_ARCHITECTURE_SVG = PACKAGE / "assets/product-architecture-1600x900.svg"
PRODUCT_ARCHITECTURE_PNG = PACKAGE / "assets/product-architecture-1600x900.png"
GATE = ROOT / "docs/strategy/SAEE_ALIBABA_CLOUD_MARKETPLACE_ENTRY_READINESS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_ALIBABA_CLOUD_MARKETPLACE_ENTRY_READINESS_SMOKE: FAIL " + message)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), path.as_posix())
    return value


def main() -> None:
    for path in (
        READINESS,
        PACKAGE / "README.md",
        LISTING,
        PROPOSAL,
        SOP,
        STORE_PROFILE,
        SUBMISSION_OBSERVATION,
        STORE_LOGO,
        STORE_BANNER,
        SEO_COPY,
        PRODUCT_DETAIL,
        PRODUCT_MAIN_IMAGE,
        PRODUCT_LOGO,
        PRODUCT_USAGE_GUIDE,
        PRODUCT_ARCHITECTURE_SVG,
        PRODUCT_ARCHITECTURE_PNG,
        GATE,
    ):
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    readiness = load(READINESS)
    listing = load(LISTING)
    proposal = load(PROPOSAL)
    store_profile = load(STORE_PROFILE)
    submission_observation = load(SUBMISSION_OBSERVATION)
    truth = readiness["truth_boundary"]

    require(readiness["partner_workbench_observations"]["product_ecosystem_partner_membership_active"] is True, "partner membership")
    require(readiness["marketplace_console_observations"]["marketplace_category_qualification_completed"] is True, "category qualification")
    require(readiness["marketplace_console_observations"]["service_provider_profile_required_fields_completed"] is True, "service-provider profile completion")
    require(readiness["marketplace_console_observations"]["settlement_information_saved_to_provider_profile"] is True, "settlement profile information")
    require(readiness["marketplace_console_observations"]["enterprise_settlement_account_activation_completed"] is True, "settlement account")
    require(readiness["marketplace_console_observations"]["enterprise_settlement_account_activation_owner_confirmed"] is True, "settlement owner confirmation")
    require(readiness["marketplace_console_observations"]["enterprise_settlement_account_activation_platform_status_observed_in_this_update"] is True, "settlement platform observation")
    require(readiness["marketplace_console_observations"]["custody_account_provider_options"] == ["enterprise_alipay", "mybank"], "custody account provider options")
    require(readiness["marketplace_console_observations"]["enterprise_alipay_binding_requires_enterprise_alipay_qr_scan"] is True, "enterprise Alipay QR requirement")
    require(readiness["marketplace_console_observations"]["personal_alipay_explicitly_disallowed"] is True, "personal Alipay boundary")
    require(readiness["marketplace_console_observations"]["alipay_binding_confirmation_dialog_observed"] is True, "Alipay handoff dialog")
    require(readiness["marketplace_console_observations"]["alipay_binding_or_qr_scan_performed"] is True, "Alipay binding observation")
    require(readiness["marketplace_console_observations"]["enterprise_alipay_custody_account_application_submitted"] is True, "Alipay custody application")
    require(readiness["marketplace_console_observations"]["enterprise_alipay_custody_account_application_status"] == "active_owner_confirmed", "Alipay custody active state")
    require(readiness["marketplace_console_observations"]["mybank_application_form_observed"] is True, "MYbank application handoff")
    require(readiness["marketplace_console_observations"]["custody_account_provider_owner_selected"] == "enterprise_alipay", "provider owner decision")
    require(readiness["marketplace_console_observations"]["current_handoff_surface"] == "marketplace_product_management_review_in_progress", "marketplace handoff")
    require(readiness["privacy"]["legal_representative_identity_number_stored"] is False, "identity data boundary")
    require(readiness["marketplace_console_observations"]["withholding_authorization_performed"] is True, "withholding authorization")
    require(readiness["marketplace_console_observations"]["withholding_authorization_platform_status_observed"] is True, "withholding platform observation")
    require(readiness["marketplace_console_observations"]["publish_product_action_blocked_by_startup_guide"] is False, "publish action gate")
    require(readiness["marketplace_console_observations"]["publish_product_block_reason"] is None, "publish block reason")
    require(readiness["marketplace_console_observations"]["publish_product_block_state_currently_verified"] is False, "publish block observation")
    require(readiness["marketplace_console_observations"]["publish_product_unblocked_state_currently_verified"] is True, "publish unblocked observation")
    require(readiness["marketplace_console_observations"]["marketplace_overview_todo_items"] == [], "startup todo")
    require(readiness["marketplace_console_observations"]["store_profile_required_text_fields_prepared"] is True, "store text preparation")
    require(readiness["marketplace_console_observations"]["store_profile_description_editor_state_synchronized"] is True, "store description editor state")
    require(readiness["marketplace_console_observations"]["store_profile_description_required_error_visible_after_correction"] is False, "store description error cleared")
    require(readiness["marketplace_console_observations"]["store_profile_required_public_assets_uploaded"] is True, "store asset upload")
    require(readiness["marketplace_console_observations"]["store_profile_required_private_contact_fields_prepared"] is True, "store contact preparation")
    require(readiness["marketplace_console_observations"]["store_profile_submission"] is True, "store profile submission")
    require(readiness["marketplace_console_observations"]["store_profile_submission_actor"] == "owner", "store profile submission actor")
    require(readiness["marketplace_console_observations"]["store_profile_submission_platform_followup_observed"] is True, "store profile followup")
    require(readiness["marketplace_console_observations"]["product_type_selection_page_opened"] is True, "product type page")
    require(readiness["marketplace_console_observations"]["product_type_owner_selected"] is True, "product type owner decision")
    require(readiness["marketplace_console_observations"]["product_type_current_ui_selection_observed"] == "服务类", "current product type observation")
    require(readiness["marketplace_console_observations"]["product_type_current_ui_selection_accepted_by_owner"] is True, "product type confirmation")
    require(readiness["marketplace_console_observations"]["spi_notification_current_ui_selection_observed"] is False, "SPI observation")
    require(readiness["marketplace_console_observations"]["service_flow_template_modal_opened"] is True, "service flow modal")
    require(readiness["marketplace_console_observations"]["service_flow_template_selected"] is True, "service flow selection")
    require(readiness["marketplace_console_observations"]["service_flow_template_name"] == "最简服务流", "service flow name")
    require(readiness["marketplace_console_observations"]["product_access_form_fields_modified_by_codex"] is True, "product access form execution")
    require(readiness["marketplace_console_observations"]["marketplace_product_draft_record_created"] is True, "product draft record")
    require(readiness["marketplace_console_observations"]["marketplace_product_draft_commodity_id"] == "68657", "commodity ID")
    require(readiness["marketplace_console_observations"]["marketplace_product_code"] == "cmfw00074657", "product code")
    require(readiness["marketplace_console_observations"]["marketplace_product_basic_info_architecture_image_uploaded"] is True, "architecture upload")
    require(readiness["marketplace_console_observations"]["marketplace_product_basic_info_saved"] is True, "basic info saved")
    require(readiness["marketplace_console_observations"]["marketplace_product_business_info_fields_modified_by_codex"] is True, "business info write")
    require(readiness["marketplace_console_observations"]["marketplace_product_category_selected"] == "AI应用及服务市场 / AI应用", "product category")
    require(readiness["marketplace_console_observations"]["marketplace_product_application_object_selected"] == "企业", "application object")
    require(readiness["marketplace_console_observations"]["marketplace_product_application_scenario_selected"] == "应用开发", "application scenario")
    require(readiness["marketplace_console_observations"]["marketplace_product_custom_tags_selected"] == ["数据智能", "数据分析"], "custom tags")
    require(readiness["marketplace_console_observations"]["marketplace_product_delivery_time_entered"] is False, "delivery time boundary")
    require(readiness["marketplace_console_observations"]["marketplace_product_warranty_time_entered"] is False, "warranty time boundary")
    require(readiness["marketplace_console_observations"]["marketplace_product_business_info_saved"] is True, "business info saved")
    require(readiness["marketplace_console_observations"]["marketplace_product_sales_information_opened"] is True, "sales information opened")
    require(readiness["marketplace_console_observations"]["marketplace_product_sales_mode_observed"] == "按次售卖", "sales mode")
    require(readiness["marketplace_console_observations"]["marketplace_product_enterprise_only_observed"] is False, "enterprise-only boundary")
    require(readiness["marketplace_console_observations"]["marketplace_product_sku_name_entered"] == "单工作流单场景首发评估", "SKU name")
    require(readiness["marketplace_console_observations"]["marketplace_product_price_cny_entered"] == 999, "price entered")
    require(readiness["marketplace_console_observations"]["marketplace_product_validity_current_ui_selection"] == "1年", "current validity observation")
    require(readiness["marketplace_console_observations"]["marketplace_product_validity_owner_approved"] is True, "validity approval")
    require(readiness["marketplace_console_observations"]["marketplace_product_sales_information_form_fields_entered"] is True, "sales fields entered")
    require(readiness["marketplace_console_observations"]["marketplace_product_sales_information_saved"] is True, "sales information saved")
    require(readiness["marketplace_console_observations"]["marketplace_product_protocol_information_saved"] is True, "protocol information saved")
    require(readiness["marketplace_console_observations"]["marketplace_product_review_status"] == "审核中", "review status")
    require(readiness["marketplace_console_observations"]["marketplace_product_listing_status"] == "未上架", "listing status")
    require(readiness["deposit_evidence"]["guarantee_deposit_owner_confirmed_paid"] is True, "owner deposit confirmation")
    require(readiness["deposit_evidence"]["guarantee_deposit_platform_receipt_observed_in_this_inspection"] is False, "deposit evidence boundary")
    require(readiness["partner_workbench_observations"]["cooperation_product_record_count"] == 0, "cooperation product count")
    require(readiness["partner_workbench_observations"]["integration_certification_application_count"] == 0, "certification application count")
    require(readiness["local_package"]["listing_draft_ready"] is True, "listing package")
    require(readiness["local_package"]["store_profile_draft_ready"] is True, "store profile package")
    require(readiness["local_package"]["store_profile_public_assets_ready"] is True, "store profile assets")
    for key in (
        "seo_listing_copy_ready",
        "product_detail_draft_ready",
        "product_main_image_ready",
        "product_logo_ready",
        "product_usage_guide_pdf_ready",
        "product_architecture_svg_ready",
        "product_architecture_png_ready",
    ):
        require(readiness["local_package"][key] is True, key)

    for key in (
        "settlement_financial_authorization_performed_by_codex",
        "cooperation_product_submission",
        "integration_certification_application_submission",
        "bailian_tested",
        "bailian_integrated",
        "marketplace_product_listed",
        "commercial_delivery_completed",
        "customer_validated",
        "revenue_confirmed",
        "production_ready",
    ):
        require(truth[key] is False, key)
    require(truth["marketplace_product_access_form_fill_authorized"] is True, "access form authorization")
    require(truth["marketplace_product_basic_info_form_fill_authorized"] is True, "basic info form authorization")
    require(truth["marketplace_product_basic_info_form_modified_by_codex"] is True, "basic info form write")
    require(truth["marketplace_product_basic_info_saved"] is True, "basic info save")
    require(truth["marketplace_product_business_info_form_fill_authorized"] is True, "business info authorization")
    require(truth["marketplace_product_business_info_form_modified_by_codex"] is True, "business info write truth")
    require(truth["marketplace_product_business_info_saved"] is True, "business info saved truth")
    require(truth["marketplace_product_sales_information_opened"] is True, "sales information opened truth")
    require(truth["marketplace_product_sales_information_form_fields_entered"] is True, "sales fields entered truth")
    require(truth["marketplace_product_sales_information_saved"] is True, "sales information saved truth")
    require(truth["marketplace_product_protocol_information_saved"] is True, "protocol information saved truth")
    require(truth["marketplace_product_submission"] is True, "marketplace submission truth")
    require(truth["marketplace_product_review_in_progress"] is True, "marketplace review truth")
    require(truth["marketplace_product_review_approved"] is False, "marketplace approval boundary")
    require(truth["public_price_points_approved"] is True, "price approval truth")
    require(truth["customer_input_adapter_ready"] is True, "customer input adapter truth")
    require(truth["marketplace_product_access_form_modified_by_codex"] is True, "access form write")
    require(truth["marketplace_product_draft_created"] is True, "product draft truth")
    require(truth["store_profile_submission"] is True, "store profile truth")

    require(listing["product"]["preferred_access_type"] == "SERVICE_HUMAN_DELIVERED", "product type")
    require(listing["product"]["marketplace_product_name_proposed"], "proposed marketplace product name")
    require(listing["product"]["platform_current_ui_selection_observed"] == "服务类", "listing product type observation")
    require(listing["product"]["platform_current_ui_selection_adopted_as_owner_decision"] is True, "listing owner confirmation")
    require(listing["marketplace_commodity_id"] == "68657", "listing commodity ID")
    require(listing["product"]["marketplace_basic_info_saved"] is True, "listing basic info saved")
    require(listing["product"]["marketplace_business_info_page_opened"] is True, "listing business info page")
    require(listing["marketplace_business_info"]["category"] == "AI应用及服务市场 / AI应用", "listing category")
    require(listing["marketplace_business_info"]["saved"] is True, "listing business saved")
    require(listing["initial_sku"]["workflow_count"] == 1, "workflow scope")
    require(listing["initial_sku"]["scenario_count"] == 1, "scenario scope")
    require(listing["initial_sku"]["public_price_cny"] == 999, "owner price decision")
    require(listing["initial_sku"]["marketplace_form_entered"] is True, "marketplace form entered")
    require(listing["initial_sku"]["validity_current_ui_selection"] == "1年", "current validity")
    require(listing["initial_sku"]["validity_owner_approved"] is True, "validity approval")
    for key in ("tax_rate", "delivery_business_days", "refund_terms", "support_terms", "acceptance_terms"):
        require(listing["initial_sku"][key] is None, f"owner decision {key}")
    require(set(listing["canonical_contracts"]["public_operations"]) == {"saee.evaluate_agent_run", "saee.evaluate_evidence"}, "public operations")
    require(listing["truth_boundary"]["marketplace_product_submission"] is True, "listing submission")
    require(listing["truth_boundary"]["marketplace_product_listed"] is False, "listing publication boundary")
    require(proposal["proposed_integration"]["external_world_execution"] is False, "execution boundary")
    require(proposal["proposed_integration"]["deployment_authority"] is False, "authority boundary")
    require(proposal["truth_boundary"]["official_support"] is False, "official support boundary")
    require(store_profile["submission_state"] == "submitted_owner_confirmed_platform_followup_observed", "store profile submission state")
    require(store_profile["store_description_editor_state"] == "synchronized_required_error_cleared", "store description editor state")
    require(store_profile["private_contact_fields"]["values_stored_here"] is False, "store profile privacy boundary")
    require(store_profile["truth_boundary"]["marketplace_product_submission"] is True, "store profile product submission")
    require(submission_observation["marketplace_product_code"] == "cmfw00074657", "submission observation product code")
    require(submission_observation["platform_observation"]["review_status"] == "审核中", "submission observation review")
    require(submission_observation["platform_observation"]["listing_status"] == "未上架", "submission observation listing")
    require(submission_observation["truth_boundary"]["marketplace_product_submission"] is True, "submission observation submission")
    require(submission_observation["truth_boundary"]["marketplace_product_listed"] is False, "submission observation listing boundary")

    gate_text = GATE.read_text(encoding="utf-8")
    require("answer: recommend" in gate_text, "recommendation gate")
    require(
        "marketplace product submission" in gate_text.lower()
        or "marketplace submission" in gate_text.lower(),
        "submission gate",
    )
    sop_text = SOP.read_text(encoding="utf-8")
    require("not certification" in sop_text, "certification boundary")
    require("unknown executable" in sop_text, "supply-chain boundary")

    serialized = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (READINESS, LISTING, PROPOSAL, SOP, STORE_PROFILE, SUBMISSION_OBSERVATION, GATE, PACKAGE / "README.md")
    )
    require(re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", serialized) is None, "phone number stored")
    require(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", serialized) is None, "email address stored")
    require(re.search(r"(?<!\d)\d{17}[0-9Xx](?!\d)", serialized) is None, "identity number stored")

    print(
        "SAEE_ALIBABA_CLOUD_MARKETPLACE_ENTRY_READINESS_SMOKE: PASS "
        "partner_membership=true category_qualification=true deposit_owner_confirmed=true "
        "deposit_platform_receipt_observed=false settlement_account_owner_confirmed=true settlement_platform_observed=true cooperation_products=0 "
        "settlement_provider_options=enterprise_alipay_or_mybank alipay_binding=true custody_application=active_owner_confirmed withholding_authorization=true "
        "publish_action_blocked=false publish_entry_unblocked=true store_profile_prepared=true store_profile_submission=true product_type_owner_selected=true "
        "seo_listing_copy_ready=true product_assets_ready=true service_flow_template_selected=true product_draft_created=true commodity_id=68657 "
        "basic_info_form_fill_authorized=true basic_info_saved=true business_info_form_fill_authorized=true "
        "business_info_saved=true sales_information_opened=true sales_information_form_fields_entered=true sales_information_saved=true protocol_information_saved=true public_price_points_approved=true validity_owner_approved=true customer_input_adapter_ready=true architecture_uploaded=true certification_applications=0 local_listing_package=true marketplace_submission=true marketplace_review=审核中 "
        "marketplace_listed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
