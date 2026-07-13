#!/usr/bin/env python3
"""Smoke check for the SAEE DPA review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "data_processing_agreement_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "data_processing_agreement_review_packet.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_DATA_PROCESSING_AGREEMENT_REVIEW_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_DATA_PROCESSING_AGREEMENT_REVIEW_PACKET_SMOKE: FAIL: " + message
        )


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_data_processing_agreement_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "data_processing_agreement_human_review_packet_only",
        "blocker_target": "data_processing_agreement",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "dpa_review_approval_status": "not_approved",
        "ready_for_human_review": True,
        "dpa_review_packet_evidence_complete": False,
        "data_processing_agreement_available": False,
        "production_privacy_security_legal_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "legal_approval_completed": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "blockers_closed_by_packet": 0,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "controller_processor_roles",
        "processing_purpose",
        "data_categories",
        "security_measures",
        "subprocessor_terms",
        "audit_rights",
        "breach_notice_window",
        "deletion_or_return_terms",
        "jurisdiction_and_transfer_terms",
        "customer_dpa_template_boundary",
        "privacy_legal_dependency",
        "customer_data_exclusion_for_local_mvp",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections <= set(packet.get("required_dpa_review_sections", [])),
        "missing required DPA review sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_data_processing_agreement_review_packet",
        "packet_status: draft_ready_for_human_review",
        "dpa_review_approval_status: not_approved",
        "dpa_review_packet_evidence_complete: false",
        "data_processing_agreement_available: false",
        "production_privacy_security_legal_ready: false",
        "production_legal_ready: false",
        "customer_data_processing_ready: false",
        "legal_approval_completed: false",
        "data_processing_agreement_approved: false",
        "dpa_sent_to_customer: false",
        "customer_data_processed: false",
        "privacy_legal_review_completed: false",
        "legal_counsel_contacted: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_dpa_availability_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    for token in [
        "dpa_review_packet_evidence_complete: true",
        '"dpa_review_packet_evidence_complete": true',
        "data_processing_agreement_available: true",
        '"data_processing_agreement_available": true',
        "data_processing_agreement_approved: true",
        '"data_processing_agreement_approved": true',
        "dpa_sent_to_customer: true",
        '"dpa_sent_to_customer": true',
        "customer_data_processed: true",
        '"customer_data_processed": true',
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
    ]:
        require(token not in combined, "forbidden true claim present: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/DATA_PROCESSING_AGREEMENT_REVIEW_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/data_processing_agreement_review_packet.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/data_processing_agreement_review_packet.local.json",
        "/docs/strategy/SAEE_DATA_PROCESSING_AGREEMENT_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_data_processing_agreement_review_packet.py",
        "/scripts/saee_data_processing_agreement_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("data_processing_agreement_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_data_processing_agreement_review_packet",
        "blocker_target": "data_processing_agreement",
        "human_review_required": True,
        "ready_for_human_review": True,
        "dpa_review_approval_status": "not_approved",
        "dpa_review_packet_evidence_complete": False,
        "data_processing_agreement_available": False,
        "production_privacy_security_legal_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "legal_approval_completed": False,
        "data_processing_agreement_approved": False,
        "dpa_sent_to_customer": False,
        "customer_data_processed": False,
        "privacy_legal_review_completed": False,
        "legal_counsel_contacted": False,
        "private_core_exposed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "blockers_closed_by_packet": 0,
    }
    for key, expected_value in expected_entry.items():
        require(
            entry.get(key) == expected_value,
            f"agent-index {key} must be {expected_value}",
        )

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Data processing agreement review packet v0.1 is implemented",
        "dpa_review_packet_evidence_complete=false",
        "data_processing_agreement_available=false",
        "blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_DATA_PROCESSING_AGREEMENT_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true dpa_review_packet_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
