#!/usr/bin/env python3
"""Smoke check for the SAEE operations monitoring / alert review packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/operations_evidence/"
    "operations_monitoring_alert_review_packet.local.json"
)
PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/operations_evidence/"
    "operations_monitoring_alert_review_packet.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_SMOKE: FAIL: "
            + message
        )


def main() -> None:
    require(PACKET_JSON.exists(), "packet JSON missing")
    require(PACKET_MD.exists(), "packet Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    expected = {
        "packet_type": "saee_operations_monitoring_alert_review_packet",
        "packet_status": "draft_ready_for_human_review",
        "review_scope": "operations_monitoring_alert_human_review_packet_only",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "operations_monitoring_alert_approval_status": "not_approved",
        "ready_for_human_review": True,
        "operations_monitoring_alert_evidence_complete": False,
        "production_operations_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(packet.get(key) == expected_value, f"{key} must be {expected_value}")

    required_blockers = {
        "production_monitoring",
        "external_alert_delivery",
        "on_call_rotation",
    }
    require(required_blockers <= set(packet.get("blocker_targets", [])), "missing blockers")

    required_sections = {
        "production_monitoring_plan_boundary",
        "metrics_coverage_boundary",
        "slo_dashboard_boundary",
        "log_retention_boundary",
        "monitoring_dry_run_boundary",
        "external_alert_channel_boundary",
        "alert_routing_policy_boundary",
        "alert_delivery_test_plan",
        "alert_failure_handling_boundary",
        "incident_escalation_path_boundary",
        "alert_acknowledgement_process_boundary",
        "on_call_rotation_boundary",
        "escalation_schedule_boundary",
        "incident_commander_boundary",
        "vendor_contact_boundary",
        "private_core_exclusion",
        "approval_record",
    }
    require(
        required_sections <= set(packet.get("required_operations_sections", [])),
        "missing required operations sections",
    )

    for key, value in packet.get("approval_flags", {}).items():
        require(value is False, f"approval flag {key} must remain false")
    for key, value in packet.get("boundary_flags", {}).items():
        require(value is False, f"boundary flag {key} must remain false")

    combined = PACKET_MD.read_text(encoding="utf-8") + "\n" + GATE_PATH.read_text(
        encoding="utf-8"
    )
    for token in [
        "packet_type: saee_operations_monitoring_alert_review_packet",
        "packet_status: draft_ready_for_human_review",
        "operations_monitoring_alert_approval_status: not_approved",
        "operations_monitoring_alert_evidence_complete: false",
        "production_operations_ready: false",
        "production_monitoring_available: false",
        "external_alert_delivery_available: false",
        "on_call_rotation_available: false",
        "alert_provider_contacted: false",
        "monitoring_vendor_contacted: false",
        "customer_contacted: false",
        "private_core_exposed: false",
        "production_ready: false",
        "answer: conditional",
        "recommend_for_human_review: true",
        "recommend_for_monitoring_claim: false",
        "recommend_for_alert_delivery_claim: false",
        "recommend_for_on_call_claim: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/operations_evidence/operations_monitoring_alert_review_packet.md",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_monitoring_alert_review_packet.local.json",
        "/docs/strategy/SAEE_OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_RECOMMENDATION_GATE.md",
        "/scripts/saee_operations_monitoring_alert_review_packet.py",
        "/scripts/saee_operations_monitoring_alert_review_packet_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("operations_monitoring_alert_review_packet_v0_1", {})
    expected_entry = {
        "status": "draft_ready_for_human_review",
        "packet_type": "saee_operations_monitoring_alert_review_packet",
        "human_review_required": True,
        "ready_for_human_review": True,
        "operations_monitoring_alert_approval_status": "not_approved",
        "operations_monitoring_alert_evidence_complete": False,
        "production_monitoring_available": False,
        "external_alert_delivery_available": False,
        "on_call_rotation_available": False,
        "production_operations_ready": False,
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
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
        "SAEE_OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_SMOKE: PASS "
        "ready_for_human_review=true "
        "operations_monitoring_alert_evidence_complete=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
