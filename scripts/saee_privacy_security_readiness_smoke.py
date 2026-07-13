#!/usr/bin/env python3
"""Smoke check for SAEE Privacy/Security Review Readiness v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.privacy_security_readiness import (
    evaluate_privacy_security_readiness,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRIVACY_SECURITY_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_PRIVACY_SECURITY_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_privacy_security_readiness(load_settings({}))
    require(
        local["privacy_security_readiness_type"]
        == "controlled_preview_privacy_security_readiness",
        "wrong readiness type",
    )
    require(local["status"] == "hold", "privacy/security readiness must hold")
    require(local["privacy_security_review_v0_1"] is True, "review readiness must be true")
    require(local["data_classification_available"] is True, "data classification must be available")
    require(local["public_shell_data_map_available"] is True, "data map must be available")
    require(local["pii_policy_draft_available"] is True, "PII policy draft must be available")
    require(local["personal_data_allowed"] is False, "personal data must remain disallowed")
    require(local["secret_handling_guidance_available"] is True, "secret guidance must be available")
    require(
        local["third_party_processor_inventory_available"] is True,
        "third-party inventory must be available",
    )
    require(local["legal_readiness_v0_1"] is True, "legal readiness true")
    require(local["legal_readiness_status"] == "hold", "legal readiness hold")
    require(local["terms_of_service_draft_available"] is True, "terms draft true")
    require(local["terms_of_service_published"] is False, "terms published false")
    require(local["privacy_notice_draft_available"] is True, "privacy notice draft true")
    require(local["privacy_notice_published"] is False, "privacy notice published false")
    require(local["dpa_review_packet_available"] is True, "DPA packet true")
    require(local["data_processing_agreement_draft_available"] is True, "DPA draft true")
    require(local["production_legal_ready"] is False, "production legal false")
    require(local["vulnerability_management_readiness_v0_1"] is True, "vuln readiness true")
    require(local["security_contact_configured"] is False, "security contact false")
    require(
        local["vulnerability_disclosure_policy_draft_available"] is True,
        "vulnerability disclosure draft true",
    )
    require(local["vulnerability_triage_runbook_available"] is True, "triage runbook true")
    require(local["vulnerability_remediation_sla_available"] is False, "remediation SLA false")
    require(local["coordinated_disclosure_available"] is False, "coordinated disclosure false")
    require(local["external_model_api_called"] is False, "external model API must be false")
    require(local["external_ai_assistant_tested"] is False, "external assistant test must be false")
    require(
        local["formal_security_review_completed"] is False,
        "formal security review must remain false",
    )
    require(local["privacy_legal_review_completed"] is False, "privacy legal review false")
    require(
        local["data_processing_agreement_available"] is False,
        "DPA must remain false",
    )
    require(local["security_certification_available"] is False, "certification false")
    require(local["soc2_available"] is False, "SOC2 false")
    require(local["iso27001_available"] is False, "ISO27001 false")
    require(local["penetration_test_completed"] is False, "penetration test false")
    require(
        local["vulnerability_management_available"] is False,
        "vulnerability management false",
    )
    require(
        local["production_vulnerability_management_ready"] is False,
        "production vulnerability management false",
    )
    require(local["compliance_logging_available"] is False, "compliance logging false")
    require(local["production_security_ready"] is False, "production security false")
    require(local["customer_data_processing_ready"] is False, "customer data processing false")
    require(local["production_ready"] is False, "production ready must remain false")
    require(local["customer_validated"] is False, "customer validation must remain false")
    require(local["product_launched"] is False, "product launch must remain false")
    require(local["private_core_exposed"] is False, "private core exposed must remain false")
    require(local["api_schema_modified"] is False, "API schema must not be modified")
    require(local["runtime_modified"] is False, "runtime must not be modified")
    require(local["kernel_modified"] is False, "kernel must not be modified")
    require(local["external_calls_made"] is False, "external calls must be false")
    require(local["customer_contacted"] is False, "customer contact must be false")
    require(finding(local, "data_classification_available")["passed"] is True, "classification pass")
    require(
        finding(local, "vulnerability_disclosure_policy_draft_available")["passed"] is True,
        "vulnerability disclosure draft pass",
    )
    require(finding(local, "formal_security_review_missing")["passed"] is False, "security review blocks")
    require(finding(local, "privacy_legal_review_missing")["passed"] is False, "privacy review blocks")

    payload = load_settings({}).readiness_payload()
    require(payload["privacy_security_review_v0_1"] is True, "ready payload review true")
    require(payload["privacy_security_review_status"] == "hold", "ready payload hold")
    require(payload["data_classification_available"] is True, "ready payload classification")
    require(payload["personal_data_allowed"] is False, "ready payload personal data false")
    require(payload["legal_readiness_v0_1"] is True, "ready payload legal true")
    require(payload["terms_of_service_draft_available"] is True, "ready payload terms draft")
    require(payload["terms_of_service_published"] is False, "ready payload terms published false")
    require(payload["privacy_notice_draft_available"] is True, "ready payload privacy draft")
    require(payload["privacy_notice_published"] is False, "ready payload privacy published false")
    require(payload["dpa_review_packet_available"] is True, "ready payload DPA packet")
    require(payload["data_processing_agreement_draft_available"] is True, "ready payload DPA draft")
    require(payload["production_legal_ready"] is False, "ready payload production legal false")
    require(payload["vulnerability_management_readiness_v0_1"] is True, "ready payload vuln true")
    require(payload["security_contact_configured"] is False, "ready payload security contact false")
    require(
        payload["production_vulnerability_management_ready"] is False,
        "ready payload production vulnerability false",
    )
    require(payload["formal_security_review_completed"] is False, "ready payload formal review false")
    require(payload["privacy_legal_review_completed"] is False, "ready payload privacy review false")
    require(payload["security_certification_available"] is False, "ready payload certification false")
    require(payload["production_security_ready"] is False, "ready payload production security false")

    doc = (ROOT / "phase_b_product/commercial_readiness/PRIVACY_SECURITY_REVIEW_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_PRIVACY_SECURITY_REVIEW_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("privacy_security_review_v0_1: true" in doc, "doc missing state")
    require("personal_data_allowed: false" in doc, "doc missing personal data false")
    require("legal_readiness_v0_1: true" in doc, "doc missing legal readiness")
    require("terms_of_service_draft_available: true" in doc, "doc missing terms draft")
    require("terms_of_service_published: false" in doc, "doc missing terms published false")
    require("privacy_notice_draft_available: true" in doc, "doc missing privacy draft")
    require("privacy_notice_published: false" in doc, "doc missing privacy published false")
    require("dpa_review_packet_available: true" in doc, "doc missing DPA packet")
    require("data_processing_agreement_draft_available: true" in doc, "doc missing DPA draft")
    require("production_legal_ready: false" in doc, "doc missing production legal false")
    require("vulnerability_management_readiness_v0_1: true" in doc, "doc missing vuln readiness")
    require("security_contact_configured: false" in doc, "doc missing security contact false")
    require(
        "production_vulnerability_management_ready: false" in doc,
        "doc missing production vulnerability false",
    )
    require("formal_security_review_completed: false" in doc, "doc missing security review false")
    require("privacy_legal_review_completed: false" in doc, "doc missing privacy review false")
    require("security_certification_available: false" in doc, "doc missing cert false")
    require("production_security_ready: false" in doc, "doc missing production security false")
    require("answer: conditional" in gate, "gate conditional")
    require("recommend_public_launch_now: false" in gate, "gate no launch")

    print(
        "SAEE_PRIVACY_SECURITY_READINESS_SMOKE: PASS "
        "privacy_security_review_v0_1=true "
        "personal_data_allowed=false "
        "formal_security_review_completed=false "
        "privacy_legal_review_completed=false "
        "security_certification_available=false "
        "production_security_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
