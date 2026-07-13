#!/usr/bin/env python3
"""Generate the SAEE tenant security/privacy human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not complete a security review, approve privacy/legal processing,
enable tenant authorization, process customer data, or mark SAEE
production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence"
PACKET_JSON = OUTPUT_DIR / "tenant_security_privacy_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "tenant_security_privacy_review_packet.md"

REQUIRED_REVIEW_SECTIONS = [
    "tenant_authorization_policy",
    "tenant_role_and_operator_access_boundary",
    "tenant_secret_boundary",
    "customer_data_processing_non_claim",
    "cross_tenant_access_review",
    "security_review_handoff",
    "privacy_legal_review_handoff",
    "private_core_exclusion",
    "production_enablement_exclusion",
    "separate_execution_approval",
]

APPROVAL_FLAGS: dict[str, bool] = {
    "tenant_authorization_policy_reviewed": False,
    "tenant_secret_boundary_reviewed": False,
    "security_review_completed": False,
    "privacy_legal_review_completed": False,
    "tenant_security_privacy_review_approved": False,
    "customer_data_processing_approved": False,
    "cross_tenant_access_review_approved": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "tenant_authorization_enabled": False,
    "customer_data_processed": False,
    "customer_data_processing_started": False,
    "production_tenant_storage_enabled": False,
    "tenant_storage_isolated": False,
    "production_tenant_storage_isolated": False,
    "multi_tenant_production_ready": False,
    "production_database_modified": False,
    "storage_behavior_modified": False,
    "migration_executed": False,
    "live_customer_data_migrated": False,
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
        "human_review_required": True,
        "tenant_authorization_requires_separate_approval": True,
        "customer_data_processing_requires_privacy_legal_approval": True,
        "security_review_requires_named_owner": True,
        "privacy_legal_review_requires_named_owner": True,
        "cross_tenant_access_review_requires_evidence": True,
        "private_core_review_out_of_scope": True,
        "production_enablement_forbidden_by_this_packet": True,
    }

    return {
        "packet_type": "saee_tenant_security_privacy_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_tenant_security_privacy_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "tenant_security_privacy_human_review_packet_only",
        "blocker_target": "tenant_storage_isolation",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "policy_approval_status": "not_approved",
        "required_review_sections": REQUIRED_REVIEW_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "tenant_security_privacy_evidence_complete": False,
        "production_tenant_storage_evidence_complete": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "next_action": (
            "Human security, privacy/legal, and tenant-authorization owners "
            "must review this packet before tenant security/privacy evidence "
            "can be considered complete for production launch review."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(f"- {item}" for item in packet["required_review_sections"])
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
    return f"""# SAEE Tenant Security / Privacy Review Packet v0.1

Status: draft ready for human review; not approved.

This packet converts the remaining tenant storage security/privacy gap into a
concrete human review surface. It does not complete a security review, approve
privacy/legal handling, enable tenant authorization, process customer data,
modify tenant storage behavior, or make SAEE production-ready.

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
tenant_security_privacy_evidence_complete: false
production_tenant_storage_evidence_complete: false
```

## Required Review Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human approval and production evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Security owner
- Privacy / legal owner
- Tenant authorization owner
- Data operations owner

## Non-Approval Statement

This packet is not production evidence by itself. It is a structured draft for
review. The `tenant_storage_isolation` blocker remains open until the approval
flags are backed by human-approved production evidence and the configured
tenant storage evidence file satisfies the production evidence checker.
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
        "SAEE_TENANT_SECURITY_PRIVACY_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "tenant_security_privacy_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
