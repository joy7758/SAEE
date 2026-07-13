#!/usr/bin/env python3
"""Generate the SAEE support/SLA/on-call human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not configure a support contact, create a staffed support desk, approve
SLA terms, start an on-call rotation, contact customers, contact vendors, or
mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
PACKET_JSON = OUTPUT_DIR / "support_sla_on_call_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "support_sla_on_call_review_packet.md"

REQUIRED_SUPPORT_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "customer_facing_support_contact_approved": False,
    "support_contact_owner_named": False,
    "abuse_handling_path_approved": False,
    "customer_notice_route_approved": False,
    "support_contact_test_completed": False,
    "staffed_support_process_approved": False,
    "case_triage_workflow_approved": False,
    "support_case_audit_trail_approved": False,
    "engineering_handoff_approved": False,
    "customer_communication_template_approved": False,
    "support_process_dry_run_approved": False,
    "human_approved_sla_terms": False,
    "severity_definitions_approved": False,
    "support_hours_approved": False,
    "response_targets_approved": False,
    "exclusions_approved": False,
    "legal_review_completed": False,
    "on_call_rotation_approved": False,
    "escalation_schedule_approved": False,
    "incident_commander_named": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
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
        "support_contact_requires_owner_approval": True,
        "customer_support_requires_staffing_approval": True,
        "sla_requires_legal_and_commercial_approval": True,
        "on_call_requires_operations_owner_approval": True,
        "support_contact_test_requires_separate_execution_approval": True,
        "support_process_dry_run_requires_separate_execution_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_support_sla_on_call_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_support_sla_on_call_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "support_sla_on_call_human_review_packet_only",
        "blocker_targets": [
            "support_contact",
            "customer_support",
            "sla",
            "on_call_rotation",
        ],
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "support_sla_on_call_approval_status": "not_approved",
        "required_support_sections": REQUIRED_SUPPORT_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "support_sla_on_call_evidence_complete": False,
        "production_support_available": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human commercial, support, operations, legal, and security owners "
            "must review support contact, staffed support process, SLA terms, "
            "and on-call escalation evidence before support launch blockers can "
            "close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    blocker_lines = "\n".join(f"- {item}" for item in packet["blocker_targets"])
    section_lines = "\n".join(f"- {item}" for item in packet["required_support_sections"])
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
    return f"""# SAEE Support / SLA / On-call Review Packet v0.1

Status: draft ready for human review; support, SLA, and on-call readiness not
approved.

This packet converts the support launch blockers into a concrete human review
surface. It does not configure a support contact, create a staffed support
desk, approve SLA terms, start an on-call rotation, contact customers, contact
support vendors, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
human_review_required: true
separate_execution_approval_required: true
support_sla_on_call_approval_status: {packet['support_sla_on_call_approval_status']}
ready_for_human_review: true
support_sla_on_call_evidence_complete: false
production_support_available: false
```

## Blocker Targets

{blocker_lines}

## Required Support Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Commercial owner
- Support owner
- Operations owner
- Legal owner
- Security owner
- Engineering escalation owner

## Non-Approval Statement

This packet is not a configured customer-facing support contact, not a staffed
support desk, not an approved support process, not approved SLA terms, not an
on-call rotation, not customer support evidence, and not production support
evidence by itself. The support blockers remain open until support contact,
staffed support process, SLA terms, and on-call escalation ownership are
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
        "SAEE_SUPPORT_SLA_ON_CALL_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "support_sla_on_call_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
