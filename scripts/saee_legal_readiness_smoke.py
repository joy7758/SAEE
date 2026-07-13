#!/usr/bin/env python3
"""Smoke check for SAEE Legal / DPA Readiness v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.legal_readiness import evaluate_legal_readiness


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_LEGAL_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_LEGAL_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_legal_readiness(load_settings({}))
    require(local["legal_readiness_type"] == "controlled_preview_legal_dpa_readiness", "type")
    require(local["status"] == "hold", "status hold")
    require(local["legal_readiness_v0_1"] is True, "legal readiness true")
    require(local["terms_of_service_draft_available"] is True, "terms draft true")
    require(local["terms_of_service_published"] is False, "terms published false")
    require(local["terms_legal_review_completed"] is False, "terms legal review false")
    require(local["privacy_notice_draft_available"] is True, "privacy notice draft true")
    require(local["privacy_notice_published"] is False, "privacy notice published false")
    require(local["privacy_legal_review_completed"] is False, "privacy legal review false")
    require(local["dpa_review_packet_available"] is True, "DPA packet true")
    require(local["data_processing_agreement_draft_available"] is True, "DPA draft true")
    require(local["data_processing_agreement_available"] is False, "DPA available false")
    require(local["customer_data_processing_ready"] is False, "customer data processing false")
    require(local["customer_contract_template_available"] is False, "contract template false")
    require(local["legal_approval_completed"] is False, "legal approval false")
    require(local["production_legal_ready"] is False, "production legal false")
    require(local["production_ready"] is False, "production false")
    require(local["customer_validated"] is False, "customer validation false")
    require(local["customer_contacted"] is False, "customer contact false")
    require(local["product_launched"] is False, "product launch false")
    require(local["public_sdk_released"] is False, "public SDK false")
    require(local["private_core_exposed"] is False, "private core false")
    require(local["api_schema_modified"] is False, "API schema false")
    require(local["runtime_modified"] is False, "runtime false")
    require(local["kernel_modified"] is False, "kernel false")
    require(local["external_calls_made"] is False, "external calls false")
    require(local["external_model_api_called"] is False, "external model false")
    require(finding(local, "terms_of_service_draft_available")["passed"] is True, "terms finding")
    require(finding(local, "privacy_notice_draft_available")["passed"] is True, "privacy finding")
    require(finding(local, "dpa_review_packet_available")["passed"] is True, "DPA finding")
    require(finding(local, "legal_review_missing")["passed"] is False, "legal review blocks")
    require(finding(local, "dpa_not_available")["passed"] is False, "DPA blocks")

    payload = load_settings({}).readiness_payload()
    require(payload["legal_readiness_v0_1"] is True, "ready legal flag")
    require(payload["legal_readiness_status"] == "hold", "ready legal hold")
    require(payload["terms_of_service_draft_available"] is True, "ready terms draft")
    require(payload["terms_of_service_published"] is False, "ready terms published false")
    require(payload["privacy_notice_draft_available"] is True, "ready privacy draft")
    require(payload["privacy_notice_published"] is False, "ready privacy published false")
    require(payload["dpa_review_packet_available"] is True, "ready DPA packet")
    require(payload["data_processing_agreement_draft_available"] is True, "ready DPA draft")
    require(payload["data_processing_agreement_available"] is False, "ready DPA false")
    require(payload["privacy_legal_review_completed"] is False, "ready legal review false")
    require(payload["customer_data_processing_ready"] is False, "ready customer data false")
    require(payload["production_legal_ready"] is False, "ready production legal false")

    doc = (
        ROOT / "phase_b_product/commercial_readiness/LEGAL_DPA_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_LEGAL_DPA_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    required_doc_tokens = [
        "legal_readiness_v0_1: true",
        "legal_readiness_status: hold",
        "terms_of_service_draft_available: true",
        "terms_of_service_published: false",
        "privacy_notice_draft_available: true",
        "privacy_notice_published: false",
        "dpa_review_packet_available: true",
        "data_processing_agreement_draft_available: true",
        "data_processing_agreement_available: false",
        "privacy_legal_review_completed: false",
        "customer_data_processing_ready: false",
        "production_legal_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    missing_doc = [token for token in required_doc_tokens if token not in doc]
    require(not missing_doc, "doc missing tokens: " + ", ".join(missing_doc))
    require("answer: conditional" in gate, "gate conditional")
    require("recommend_public_launch_now: false" in gate, "gate no launch")

    print(
        "SAEE_LEGAL_READINESS_SMOKE: PASS "
        "legal_readiness_v0_1=true "
        "terms_draft=true "
        "dpa_available=false "
        "privacy_legal_review_completed=false "
        "production_legal_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
