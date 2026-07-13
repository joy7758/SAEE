#!/usr/bin/env python3
"""Generate the SAEE production restore policy human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not approve restore policy, run restore, modify live data paths, contact
customers, or change production readiness status.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
PACKET_JSON = OUTPUT_DIR / "production_restore_policy_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "production_restore_policy_review_packet.md"

REQUIRED_POLICY_SECTIONS = [
    "restore_authority_and_approval",
    "backup_retention_and_encryption",
    "tenant_data_scope_and_isolation",
    "customer_data_handling_boundary",
    "credential_and_secret_exclusion",
    "private_core_exclusion",
    "incident_response_handoff",
    "customer_notification_boundary",
    "restore_evidence_retention",
    "post_restore_review",
]

APPROVAL_FLAGS: dict[str, bool] = {
    "production_restore_policy_approved": False,
    "backup_retention_policy_approved": False,
    "tenant_restore_boundary_approved": False,
    "credential_secret_exclusion_reviewed": False,
    "customer_notification_boundary_approved": False,
    "incident_response_handoff_approved": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "production_restore_policy_available": False,
    "production_data_operations_ready": False,
    "restore_to_live_path_enabled": False,
    "live_restore_performed": False,
    "production_data_path_modified": False,
    "credentials_restored": False,
    "private_core_restored": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "external_calls_made": False,
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "production_ready": False,
}


def build_packet() -> dict[str, Any]:
    """Build a machine-readable human review packet."""

    review_checklist = {
        "required_sections_present": True,
        "approval_signoff_required": True,
        "restore_to_live_requires_separate_approval": True,
        "customer_data_restore_requires_privacy_review": True,
        "tenant_restore_requires_security_review": True,
        "incident_handoff_requires_operations_owner": True,
        "customer_notification_requires_legal_review": True,
        "private_core_restore_forbidden": True,
        "credential_restore_forbidden_without_separate_secret_review": True,
    }

    return {
        "packet_type": "saee_production_restore_policy_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_production_restore_policy_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "production_restore_policy_human_review_packet_only",
        "blocker_target": "production_restore_policy",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "policy_approval_status": "not_approved",
        "required_policy_sections": REQUIRED_POLICY_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human data-operations, security, legal/privacy, and operations "
            "owners must review and approve the production restore policy "
            "before the production_restore_policy blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(f"- {item}" for item in packet["required_policy_sections"])
    approval_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["approval_flags"].items()
    )
    boundary_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["boundary_flags"].items()
    )
    checklist_lines = "\n".join(
        f"- {key}: {str(value).lower()}"
        for key, value in packet["review_checklist"].items()
    )
    return f"""# SAEE Production Restore Policy Review Packet v0.1

Status: draft ready for human review; not approved.

This packet converts the `production_restore_policy` blocker into a concrete
human review surface. It does not approve a production restore policy, run a
restore, touch live data paths, contact customers, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
policy_approval_status: {packet['policy_approval_status']}
ready_for_human_review: true
```

## Required Policy Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Data operations owner
- Security owner
- Privacy / legal owner
- Operations incident-response owner

## Non-Approval Statement

This packet is not production evidence by itself. It is a structured draft for
review. The `production_restore_policy` blocker remains open until the approval
flags are backed by human-approved production evidence.
"""


def write_outputs(packet: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PACKET_MD.write_text(render_markdown(packet), encoding="utf-8")


def main() -> None:
    packet = build_packet()
    write_outputs(packet)
    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "production_restore_policy_available=false production_ready=false"
    )


if __name__ == "__main__":
    main()
