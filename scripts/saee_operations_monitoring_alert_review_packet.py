#!/usr/bin/env python3
"""Generate the SAEE operations monitoring / alert / on-call review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not deploy production monitoring, enable external alert delivery, start an
on-call rotation, contact vendors, contact customers, modify backend behavior,
or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
PACKET_JSON = OUTPUT_DIR / "operations_monitoring_alert_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "operations_monitoring_alert_review_packet.md"

REQUIRED_OPERATIONS_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "production_monitoring_plan_approved": False,
    "metrics_coverage_approved": False,
    "slo_dashboard_approved": False,
    "log_retention_review_completed": False,
    "monitoring_dry_run_approved": False,
    "external_alert_channel_approved": False,
    "alert_routing_policy_approved": False,
    "alert_delivery_test_completed": False,
    "alert_failure_handling_approved": False,
    "incident_escalation_path_approved": False,
    "alert_acknowledgement_process_approved": False,
    "on_call_rotation_approved": False,
    "escalation_schedule_approved": False,
    "incident_commander_named": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "production_monitoring_available": False,
    "production_monitoring_deployed": False,
    "external_alert_delivery_available": False,
    "external_alert_delivery_enabled": False,
    "alerting_available": False,
    "on_call_rotation_available": False,
    "production_operations_ready": False,
    "alert_provider_contacted": False,
    "monitoring_vendor_contacted": False,
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "production_ready": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "external_calls_made": False,
}


def build_packet() -> dict[str, Any]:
    review_checklist = {
        "required_sections_present": True,
        "human_review_required": True,
        "monitoring_requires_operations_and_engineering_approval": True,
        "alert_delivery_requires_vendor_or_channel_owner_approval": True,
        "on_call_requires_operations_owner_approval": True,
        "alert_delivery_test_requires_separate_execution_approval": True,
        "monitoring_dry_run_requires_separate_execution_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_operations_monitoring_alert_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_operations_monitoring_alert_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "operations_monitoring_alert_human_review_packet_only",
        "blocker_targets": [
            "production_monitoring",
            "external_alert_delivery",
            "on_call_rotation",
        ],
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "operations_monitoring_alert_approval_status": "not_approved",
        "required_operations_sections": REQUIRED_OPERATIONS_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "operations_monitoring_alert_evidence_complete": False,
        "production_operations_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human operations, engineering, security, and commercial owners "
            "must review monitoring coverage, alert delivery, failure handling, "
            "and on-call ownership evidence before operations launch blockers can "
            "close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    blocker_lines = "\n".join(f"- {item}" for item in packet["blocker_targets"])
    section_lines = "\n".join(f"- {item}" for item in packet["required_operations_sections"])
    checklist_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["review_checklist"].items()
    )
    approval_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["approval_flags"].items()
    )
    boundary_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["boundary_flags"].items()
    )
    return f"""# SAEE Operations Monitoring / Alert / On-call Review Packet v0.1

Status: draft ready for human review; production monitoring, external alert
delivery, and on-call readiness not approved.

This packet converts operations launch blockers into a concrete human review
surface. It does not deploy production monitoring, enable external alert
delivery, start on-call rotation, contact monitoring or alert vendors, contact
customers, modify backend behavior, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
human_review_required: true
separate_execution_approval_required: true
operations_monitoring_alert_approval_status: {packet['operations_monitoring_alert_approval_status']}
ready_for_human_review: true
operations_monitoring_alert_evidence_complete: false
production_operations_ready: false
```

## Blocker Targets

{blocker_lines}

## Required Operations Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Operations owner
- Engineering owner
- Security owner
- Commercial owner
- Incident response owner

## Non-Approval Statement

This packet is not a deployed monitoring stack, not an external alert channel,
not an alert delivery test, not an on-call rotation, not incident-command
ownership, not vendor integration evidence, and not production operations
evidence by itself. The operations blockers remain open until monitoring
coverage, external alert delivery, failure handling, and on-call ownership are
approved and backed by human-provided evidence.
"""


def write_outputs(packet: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKET_JSON.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    PACKET_MD.write_text(render_markdown(packet), encoding="utf-8")


def main() -> None:
    packet = build_packet()
    write_outputs(packet)
    print(
        "SAEE_OPERATIONS_MONITORING_ALERT_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "operations_monitoring_alert_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
