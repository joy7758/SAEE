#!/usr/bin/env python3
"""Smoke check for the SAEE support/SLA/on-call review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "support_sla_on_call_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "support_sla_on_call_review_packet.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_SLA_ON_CALL_REVIEW_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_SUPPORT_SLA_ON_CALL_REVIEW_PACKET_SMOKE: FAIL: " + message
        )


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_support_sla_on_call_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "support_sla_on_call_human_review_packet_only",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "support_sla_on_call_approval_status": "not_approved",
        "ready_for_human_review": True,
        "support_sla_on_call_evidence_complete": False,
        "production_support_available": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_blockers = {
        "support_contact",
        "customer_support",
        "sla",
        "on_call_rotation",
    }
    require(required_blockers <= set(packet.get("blocker_targets", [])), "missing blockers")

    required_sections = {
        "support_contact_boundary",
        "support_contact_owner_boundary",
        "abuse_handling_path_boundary",
        "customer_notice_route_boundary",
        "support_contact_test_plan",
        "staffed_support_process_boundary",
        "case_triage_workflow_boundary",
        "support_case_audit_trail_boundary",
        "engineering_handoff_boundary",
        "customer_communication_template_boundary",
        "support_process_dry_run_boundary",
        "sla_terms_boundary",
        "severity_definitions_boundary",
        "support_hours_boundary",
        "response_targets_boundary",
        "sla_exclusions_boundary",
        "legal_review_boundary",
        "on_call_rotation_boundary",
        "escalation_schedule_boundary",
        "incident_commander_boundary",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections <= set(packet.get("required_support_sections", [])),
        "missing required support sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_support_sla_on_call_review_packet",
        "packet_status: draft_ready_for_human_review",
        "support_sla_on_call_approval_status: not_approved",
        "support_sla_on_call_evidence_complete: false",
        "production_support_available: false",
        "support_contact_available: false",
        "support_contact_configured: false",
        "customer_facing_support_contact_configured: false",
        "customer_support_available: false",
        "support_process_available: false",
        "sla_available: false",
        "on_call_rotation_available: false",
        "support_vendor_contacted: false",
        "customer_contacted: false",
        "private_core_exposed: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_support_claim: false",
        "recommend_for_sla_claim: false",
        "recommend_for_on_call_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/support_evidence/support_sla_on_call_review_packet.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_sla_on_call_review_packet.local.json",
        "/docs/strategy/SAEE_SUPPORT_SLA_ON_CALL_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_support_sla_on_call_review_packet.py",
        "/scripts/saee_support_sla_on_call_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("support_sla_on_call_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_support_sla_on_call_review_packet",
        "human_review_required": True,
        "ready_for_human_review": True,
        "support_sla_on_call_approval_status": "not_approved",
        "support_sla_on_call_evidence_complete": False,
        "support_contact_available": False,
        "support_contact_configured": False,
        "customer_facing_support_contact_configured": False,
        "customer_support_available": False,
        "production_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "support_vendor_contacted": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected_entry.items():
        require(
            entry.get(key) == expected_value,
            f"agent-index {key} must be {expected_value}",
        )

    print(
        "SAEE_SUPPORT_SLA_ON_CALL_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true "
        "support_sla_on_call_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
