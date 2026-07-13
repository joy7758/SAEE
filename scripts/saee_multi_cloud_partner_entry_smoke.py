#!/usr/bin/env python3
"""Validate the sanitized multi-cloud partner-entry truth surface."""

from __future__ import annotations

import json
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
    tencent_handoff = json.loads((ROOT / providers["Tencent Cloud"]["contact_handoff_ref"]).read_text(encoding="utf-8"))
    require(tencent_handoff["truth_boundary"]["human_slider_captcha_required"] is True, "Tencent CAPTCHA handoff")
    require(tencent_handoff["truth_boundary"]["business_cooperation_inquiry_submitted"] is False, "Tencent inquiry boundary")
    require(aggregate["submitted_count"] == 2, "submitted count")
    require(aggregate["partner_or_ecosystem_interest_submission_count"] == 2, "interest submission count")
    require(aggregate["provider_contact_inquiry_count"] == 1, "contact inquiry count")
    require(aggregate["acknowledged_external_intake_count"] == 3, "acknowledged intake count")
    require(aggregate["incomplete_form_handoff_count"] == 1, "handoff count")
    require(aggregate["formal_partner_application_count"] == 0, "formal application count")
    require(aggregate["blocked_count"] == 3, "blocked count")
    for key in ("provider_approved_count", "marketplace_submission_count", "marketplace_listed_count"):
        require(aggregate[key] == 0, key)
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
            ROOT / providers["Tencent Cloud"]["contact_handoff_ref"],
        )
    )
    for forbidden in ("18518485118", "139115", "joy7759@gmail.com", "张斌", "山西游骑兵电子商务有限公司"):
        require(forbidden not in serialized, "sensitive value stored")

    print(
        "SAEE_MULTI_CLOUD_PARTNER_ENTRY_SMOKE: PASS "
        "providers=5 interest_submitted=2 contact_inquiry=1 captcha_handoff=1 "
        "formal_partner_application=0 blocked=3 provider_approved=0 "
        "marketplace_submission=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
