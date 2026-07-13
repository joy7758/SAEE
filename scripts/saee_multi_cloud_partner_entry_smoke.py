#!/usr/bin/env python3
"""Validate the sanitized multi-cloud partner-entry truth surface."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "agent-interface/ecosystem/saee-multi-cloud-partner-entry-matrix.v1.json"
AUTH = ROOT / "agent-interface/ecosystem/saee-multi-cloud-external-action-authorization-gate.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_MULTI_CLOUD_PARTNER_ENTRY_SMOKE: FAIL " + message)


def main() -> None:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    providers = {item["provider"]: item for item in matrix["providers"]}
    aggregate = matrix["aggregate_truth"]

    require(auth["authorization"]["approved"] is True, "authorization")
    require(auth["truth_boundary"]["authorization_is_scope_limited"] is True, "scope")
    require(set(providers) == {"Volcengine", "OpenAI", "Google Cloud", "Alibaba Cloud", "Tencent Cloud"}, "providers")
    require(providers["Volcengine"]["recommendation"] == "recommend", "Volcengine recommendation")
    receipt_ref = providers["Volcengine"]["submission_receipt_ref"]
    receipt = json.loads((ROOT / receipt_ref).read_text(encoding="utf-8"))
    require(receipt["status"] == "submitted_success_text_observed", "Volcengine submission")
    require(receipt["truth_boundary"]["ai_partner_consultation_submitted"] is True, "Volcengine truth")
    openai_receipt = json.loads((ROOT / providers["OpenAI"]["submission_receipt_ref"]).read_text(encoding="utf-8"))
    require(providers["OpenAI"]["recommendation"] == "recommend", "OpenAI route recommendation")
    require(openai_receipt["truth_boundary"]["openai_partner_interest_submitted"] is True, "OpenAI submission")
    require(all(providers[name]["recommendation"] == "conditional" for name in ("Google Cloud", "Alibaba Cloud", "Tencent Cloud")), "conditional routes")
    require(providers["Google Cloud"]["current_state"] == "blocked_personal_email_domain_rejected", "Google email rejection")
    alibaba_receipt = json.loads((ROOT / providers["Alibaba Cloud"]["contact_receipt_ref"]).read_text(encoding="utf-8"))
    require(alibaba_receipt["truth_boundary"]["product_ecosystem_cooperation_inquiry_submitted"] is True, "Alibaba contact inquiry")
    require(alibaba_receipt["truth_boundary"]["formal_product_partner_application_submitted"] is False, "Alibaba formal application boundary")
    alibaba_submission = json.loads((ROOT / providers["Alibaba Cloud"]["application_submission_receipt_ref"]).read_text(encoding="utf-8"))
    require(alibaba_submission["platform_observations"]["submission_success_message_displayed"] is True, "Alibaba submission success")
    require(alibaba_submission["platform_observations"]["application_under_review_displayed"] is True, "Alibaba review state")
    require(alibaba_submission["truth_boundary"]["enterprise_verified"] is True, "Alibaba enterprise verification")
    require(alibaba_submission["truth_boundary"]["formal_product_partner_application_started"] is True, "Alibaba application started")
    require(alibaba_submission["truth_boundary"]["formal_product_partner_application_submitted"] is True, "Alibaba application submitted")
    require(alibaba_submission["truth_boundary"]["application_under_review"] is True, "Alibaba application under review")
    require(alibaba_submission["truth_boundary"]["agreement_signed"] is False, "Alibaba agreement boundary")
    require(alibaba_submission["truth_boundary"]["guarantee_deposit_paid"] is False, "Alibaba deposit boundary")
    alibaba_activation = json.loads((ROOT / providers["Alibaba Cloud"]["partner_activation_receipt_ref"]).read_text(encoding="utf-8"))
    alibaba_ticket = json.loads((ROOT / providers["Alibaba Cloud"]["qoder_technical_consultation_ticket_receipt_ref"]).read_text(encoding="utf-8"))
    require(alibaba_activation["truth_boundary"]["partner_application_review_approved"] is True, "Alibaba application approval")
    require(alibaba_activation["truth_boundary"]["partner_contract_signature_observed"] is True, "Alibaba signed agreement observation")
    require(alibaba_activation["truth_boundary"]["product_ecosystem_partner_membership_active"] is True, "Alibaba partner membership")
    require(alibaba_activation["truth_boundary"]["approved_cloud_marketplace_route_available"] is True, "Alibaba marketplace route")
    require(alibaba_activation["truth_boundary"]["marketplace_product_submission"] is False, "Alibaba marketplace product boundary")
    alibaba_marketplace = json.loads((ROOT / providers["Alibaba Cloud"]["marketplace_entry_readiness_ref"]).read_text(encoding="utf-8"))
    require(alibaba_marketplace["marketplace_console_observations"]["marketplace_category_qualification_completed"] is True, "Alibaba Marketplace category qualification")
    require(alibaba_marketplace["marketplace_console_observations"]["enterprise_settlement_account_activation_completed"] is True, "Alibaba Marketplace settlement account")
    require(alibaba_marketplace["marketplace_console_observations"]["enterprise_settlement_account_activation_owner_confirmed"] is True, "Alibaba Marketplace settlement owner confirmation")
    require(alibaba_marketplace["marketplace_console_observations"]["withholding_authorization_performed"] is True, "Alibaba Marketplace withholding authorization")
    require(alibaba_marketplace["marketplace_console_observations"]["publish_product_action_blocked_by_startup_guide"] is False, "Alibaba Marketplace publish entry")
    require(alibaba_marketplace["marketplace_console_observations"]["publish_product_unblocked_state_currently_verified"] is True, "Alibaba Marketplace publish verification")
    require(alibaba_marketplace["marketplace_console_observations"]["store_profile_required_text_fields_prepared"] is True, "Alibaba Marketplace store-profile preparation")
    require(alibaba_marketplace["marketplace_console_observations"]["store_profile_submission"] is True, "Alibaba Marketplace store-profile submission")
    require(alibaba_marketplace["marketplace_console_observations"]["product_type_owner_selected"] is True, "Alibaba Marketplace product type")
    require(alibaba_marketplace["deposit_evidence"]["guarantee_deposit_owner_confirmed_paid"] is True, "Alibaba deposit owner confirmation")
    require(alibaba_marketplace["deposit_evidence"]["guarantee_deposit_platform_receipt_observed_in_this_inspection"] is False, "Alibaba deposit receipt boundary")
    require(alibaba_marketplace["partner_workbench_observations"]["cooperation_product_record_count"] == 0, "Alibaba cooperation product count")
    require(alibaba_marketplace["partner_workbench_observations"]["integration_certification_application_count"] == 0, "Alibaba certification application count")
    require(alibaba_marketplace["truth_boundary"]["marketplace_product_submission"] is True, "Alibaba Marketplace submission")
    require(alibaba_marketplace["truth_boundary"]["marketplace_product_review_in_progress"] is True, "Alibaba Marketplace review")
    require(alibaba_marketplace["truth_boundary"]["marketplace_product_listed"] is False, "Alibaba Marketplace listing boundary")
    require(alibaba_ticket["truth_boundary"]["technical_conversation_request_submitted"] is True, "Alibaba Qoder ticket")
    require(alibaba_ticket["truth_boundary"]["technical_conversation_completed"] is False, "Alibaba Qoder conversation boundary")
    tencent_handoff = json.loads((ROOT / providers["Tencent Cloud"]["contact_handoff_ref"]).read_text(encoding="utf-8"))
    require(tencent_handoff["truth_boundary"]["human_slider_captcha_required"] is True, "Tencent CAPTCHA handoff")
    require(tencent_handoff["truth_boundary"]["business_cooperation_inquiry_submitted"] is False, "Tencent inquiry boundary")
    require(aggregate["submitted_count"] == 3, "submitted count")
    require(aggregate["submitted_provider_count"] == 3, "submitted provider count")
    require(aggregate["partner_or_ecosystem_interest_submission_count"] == 2, "interest submission count")
    require(aggregate["provider_contact_inquiry_count"] == 1, "contact inquiry count")
    require(aggregate["external_submission_event_count"] == 5, "external submission event count")
    require(aggregate["acknowledged_external_intake_count"] == 4, "acknowledged intake count")
    require(aggregate["incomplete_form_handoff_count"] == 1, "handoff count")
    require(aggregate["enterprise_verified_provider_count"] == 1, "enterprise verified provider count")
    require(aggregate["formal_partner_application_started_count"] == 1, "formal application started count")
    require(aggregate["formal_partner_application_count"] == 1, "formal application count")
    require(aggregate["formal_partner_application_under_review_count"] == 0, "formal application under review count")
    require(aggregate["formal_partner_application_approved_count"] == 1, "formal application approved count")
    require(aggregate["partner_program_membership_active_count"] == 1, "partner membership active count")
    require(aggregate["approved_marketplace_route_available_count"] == 1, "marketplace route count")
    require(aggregate["enterprise_settlement_account_activation_completed_count"] == 1, "settlement account count")
    require(aggregate["withholding_authorization_completed_count"] == 1, "withholding authorization count")
    require(aggregate["marketplace_store_profile_submission_completed_count"] == 1, "store-profile submission count")
    require(aggregate["marketplace_publish_product_entry_unblocked_count"] == 1, "publish-entry count")
    require(aggregate["blocked_count"] == 2, "blocked count")
    require(aggregate["provider_approved_count"] == 1, "provider approved count")
    require(aggregate["marketplace_submission_count"] == 1, "marketplace submission count")
    require(aggregate["marketplace_listed_count"] == 0, "marketplace listed count")
    require(aggregate["customer_validated"] is False, "customer validation")
    require(aggregate["production_ready"] is False, "production readiness")

    serialized = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MATRIX,
            AUTH,
            ROOT / receipt_ref,
            ROOT / providers["OpenAI"]["submission_receipt_ref"],
            ROOT / providers["Alibaba Cloud"]["contact_receipt_ref"],
            ROOT / providers["Alibaba Cloud"]["application_submission_receipt_ref"],
            ROOT / providers["Alibaba Cloud"]["partner_activation_receipt_ref"],
            ROOT / providers["Alibaba Cloud"]["marketplace_entry_readiness_ref"],
            ROOT / providers["Alibaba Cloud"]["qoder_technical_consultation_ticket_receipt_ref"],
            ROOT / providers["Tencent Cloud"]["contact_handoff_ref"],
        )
    )
    require(re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", serialized) is None, "phone number stored")
    require(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", serialized) is None, "email address stored")
    require(re.search(r"(?<!\d)\d{17}[0-9Xx](?!\d)", serialized) is None, "identity number stored")

    print(
        "SAEE_MULTI_CLOUD_PARTNER_ENTRY_SMOKE: PASS "
        "providers=5 interest_submitted=2 contact_inquiry=1 enterprise_verified=1 "
        "formal_application_started=1 formal_partner_application=1 approved=1 membership_active=1 "
        "marketplace_route_available=1 category_qualification=1 settlement_account=1 withholding_authorization=1 store_profile_prepared=1 store_profile_submission=1 publish_entry_unblocked=1 product_type_owner_selected=1 "
        "captcha_handoff=1 blocked=2 provider_approved=1 "
        "marketplace_submission=1 marketplace_review=审核中 marketplace_listed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
