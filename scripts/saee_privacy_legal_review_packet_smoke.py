#!/usr/bin/env python3
"""Smoke check for the SAEE privacy/legal review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "privacy_legal_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "privacy_legal_review_packet.md"
)
GATE_PATH = ROOT / "docs/strategy/SAEE_PRIVACY_LEGAL_REVIEW_PACKET_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRIVACY_LEGAL_REVIEW_PACKET_SMOKE: FAIL: " + message)


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_privacy_legal_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "privacy_legal_review_human_review_packet_only",
        "blocker_target": "privacy_legal_review",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "privacy_legal_review_approval_status": "not_approved",
        "ready_for_human_review": True,
        "privacy_legal_review_evidence_complete": False,
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
        "data_inventory_boundary",
        "personal_data_policy_review",
        "privacy_notice_review",
        "terms_of_service_review",
        "data_retention_policy_review",
        "subprocessor_inventory_review",
        "cross_border_transfer_review",
        "customer_data_processing_terms_review",
        "data_subject_request_process",
        "dpa_handoff",
        "customer_data_exclusion_for_local_mvp",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections <= set(packet.get("required_privacy_legal_review_sections", [])),
        "missing required privacy/legal review sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_privacy_legal_review_packet",
        "packet_status: draft_ready_for_human_review",
        "privacy_legal_review_approval_status: not_approved",
        "privacy_legal_review_evidence_complete: false",
        "production_privacy_security_legal_ready: false",
        "production_legal_ready: false",
        "customer_data_processing_ready: false",
        "legal_approval_completed: false",
        "privacy_legal_review_completed: false",
        "legal_counsel_contacted: false",
        "privacy_notice_published: false",
        "terms_published: false",
        "data_processing_agreement_available: false",
        "dpa_sent_to_customer: false",
        "customer_data_processed: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_privacy_legal_review_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    for token in [
        "privacy_legal_review_evidence_complete: true",
        '"privacy_legal_review_evidence_complete": true',
        "privacy_legal_review_completed: true",
        '"privacy_legal_review_completed": true',
        "legal_counsel_contacted: true",
        '"legal_counsel_contacted": true',
        "privacy_notice_published: true",
        '"privacy_notice_published": true',
        "terms_published: true",
        '"terms_published": true',
        "data_processing_agreement_available: true",
        '"data_processing_agreement_available": true',
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
        "/phase_b_product/commercial_readiness/PRIVACY_LEGAL_REVIEW_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_review_packet.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_review_packet.local.json",
        "/docs/strategy/SAEE_PRIVACY_LEGAL_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_privacy_legal_review_packet.py",
        "/scripts/saee_privacy_legal_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("privacy_legal_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_privacy_legal_review_packet",
        "blocker_target": "privacy_legal_review",
        "human_review_required": True,
        "ready_for_human_review": True,
        "privacy_legal_review_approval_status": "not_approved",
        "privacy_legal_review_evidence_complete": False,
        "production_privacy_security_legal_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "legal_approval_completed": False,
        "privacy_legal_review_completed": False,
        "legal_counsel_contacted": False,
        "privacy_notice_published": False,
        "terms_published": False,
        "data_processing_agreement_available": False,
        "dpa_sent_to_customer": False,
        "customer_data_processed": False,
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
        "Privacy/legal review packet v0.1 is implemented",
        "privacy_legal_review_evidence_complete=false",
        "production_privacy_security_legal_ready=false",
        "blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_PRIVACY_LEGAL_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true privacy_legal_review_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
