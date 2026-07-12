#!/usr/bin/env python3
"""Fail-closed validation for the Baidu Qianfan partner consultation payload."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPLICATION = ROOT / "agent-interface/ecosystem/saee-baidu-partner-consultation-application.v1.json"
SCHEMA = ROOT / "agent-interface/ecosystem/saee-baidu-partner-consultation-application.schema.v1.json"
RECEIPT = ROOT / "agent-interface/ecosystem/saee-baidu-partner-consultation-submission-receipt.v1.json"
ALLOWED_INDUSTRIES = {"金融", "教育", "制造业", "零售与电商", "政务", "智能硬件", "法律", "企业办公", "资讯服务", "其他"}
MOBILE = re.compile(r"^1[3-9][0-9]{9}$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_PARTNER_APPLICATION_SMOKE: FAIL " + message)


def main() -> None:
    application = json.loads(APPLICATION.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    fields = application["form_fields"]
    receipt = application["submission_receipt"]
    boundary = application["truth_boundary"]

    require(schema["$schema"].endswith("2020-12/schema"), "schema version")
    require(application["application_id"] == "saee.baidu.qianfan-partner-consultation.v1", "application id")
    require(application["route"]["route_id"] == "qianfan_partner_consultation", "route")
    require(application["authorization"]["contact_baidu"] is True, "contact authorization")
    require(application["authorization"]["submit_ecosystem_application"] is True, "submission authorization")
    require(fields["product_shape"] == ["服务"], "product shape")
    require(fields["service_capability"] == ["产品集成"], "service capability")
    require(fields["partner_rights"] == ["应用场景共建", "技术赋能提升"], "partner rights")
    require(set(fields["industry"]).issubset(ALLOWED_INDUSTRIES), "industry enum")

    missing = []
    if not fields["industry"]:
        missing.append("industry")
    for key in ("company_name", "contact_name", "contact_role", "mobile_phone"):
        if not fields[key].strip():
            missing.append(key)
    if fields["contact_consent"] is not True:
        missing.append("contact_consent")
    if fields["mobile_phone"]:
        require(MOBILE.fullmatch(fields["mobile_phone"]) is not None, "mobile format")

    ready = not missing
    require(receipt["submitted"] is boundary["qianfan_partner_consultation_submitted"], "submission receipt drift")
    require(boundary["marketplace_submission"] is False, "partner consultation is not marketplace submission")
    require(boundary["marketplace_listed"] is False, "marketplace listing boundary")
    require(boundary["production_ready"] is False, "production boundary")
    if receipt["submitted"]:
        submission = json.loads(RECEIPT.read_text(encoding="utf-8"))
        require(application["status"] == "submitted_receipt_recorded", "submitted status")
        require(receipt["receipt_ref"] == str(RECEIPT.relative_to(ROOT)), "receipt ref")
        require(submission["status"] == "submitted_redirect_acknowledged", "receipt status")
        require(submission["submitted_selection"]["required_personal_fields_present_at_submission"] is True, "submitted field completeness")
        require(submission["submitted_selection"]["contact_consent"] is True, "submitted consent")
        require(submission["browser_observation"]["submit_action_executed"] is True, "submit action")
        require(submission["browser_observation"]["redirect_observed"] is True, "submit redirect")
        require(submission["privacy"]["personal_values_added_to_parent_public_allowlist_by_submission_workflow"] is False, "submission workflow personal data retention")
        require(boundary["form_fields_complete"] is False, "redacted repository fields")
        require(boundary["form_fields_complete_at_submission"] is True, "submission-time completeness")
        require(boundary["ready_for_submission"] is False, "post-submission ready state")
        require(boundary["personal_data_stored_in_application_record"] is False, "application record PII boundary")
        expected_status = "submitted_receipt_recorded"
    else:
        require(boundary["form_fields_complete"] is ready, "form_fields_complete drift")
        require(boundary["ready_for_submission"] is ready, "ready_for_submission drift")
        expected_status = "ready_for_authorized_submission" if ready else "awaiting_verified_human_inputs"
    require(application["status"] == expected_status, "status drift")

    print(
        "SAEE_BAIDU_PARTNER_APPLICATION_SMOKE: PASS "
        f"contract_valid=true ready_for_submission={str(boundary['ready_for_submission']).lower()} "
        f"repository_personal_data=false submitted={str(receipt['submitted']).lower()} "
        "acknowledgement=redirect_no_backend_id marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
