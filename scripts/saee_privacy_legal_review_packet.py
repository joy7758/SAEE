#!/usr/bin/env python3
"""Generate the SAEE privacy/legal review human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not contact legal counsel, approve privacy terms, publish legal wording,
process customer data, send a DPA, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
PACKET_JSON = OUTPUT_DIR / "privacy_legal_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "privacy_legal_review_packet.md"

REQUIRED_PRIVACY_LEGAL_REVIEW_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "privacy_notice_approved": False,
    "terms_of_service_approved": False,
    "data_inventory_reviewed": False,
    "retention_policy_approved": False,
    "subprocessor_inventory_reviewed": False,
    "cross_border_transfer_reviewed": False,
    "customer_data_processing_approved": False,
    "data_subject_request_process_approved": False,
    "legal_reviewer_recorded": False,
    "dpa_handoff_approved": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "privacy_legal_review_completed": False,
    "legal_counsel_contacted": False,
    "privacy_notice_published": False,
    "terms_published": False,
    "data_processing_agreement_available": False,
    "dpa_sent_to_customer": False,
    "customer_contract_template_available": False,
    "customer_data_processing_approved": False,
    "customer_data_processed": False,
    "customer_data_processing_started": False,
    "data_subject_request_process_operational": False,
    "subprocessor_terms_approved": False,
    "cross_border_transfer_approved": False,
    "production_legal_ready": False,
    "customer_data_processing_ready": False,
    "production_privacy_security_legal_ready": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "production_ready": False,
}


def build_packet() -> dict[str, Any]:
    review_checklist = {
        "required_sections_present": True,
        "human_review_required": True,
        "legal_reviewer_required": True,
        "privacy_notice_requires_separate_approval": True,
        "terms_of_service_requires_separate_approval": True,
        "customer_data_processing_requires_separate_approval": True,
        "dpa_work_requires_separate_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_privacy_legal_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_privacy_legal_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "privacy_legal_review_human_review_packet_only",
        "blocker_target": "privacy_legal_review",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "privacy_legal_review_approval_status": "not_approved",
        "required_privacy_legal_review_sections": REQUIRED_PRIVACY_LEGAL_REVIEW_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
        "ready_for_human_review": True,
        "privacy_legal_review_evidence_complete": False,
        "production_privacy_security_legal_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "legal_approval_completed": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "blockers_closed_by_packet": 0,
        "next_action": (
            "Human legal, privacy, security, data-operations, and commercial "
            "owners must review privacy notice, terms, data inventory, "
            "retention, subprocessors, transfer boundaries, customer data "
            "processing, data subject requests, and DPA handoff before the "
            "privacy_legal_review blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(
        f"- {item}" for item in packet["required_privacy_legal_review_sections"]
    )
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
    return f"""# SAEE Privacy Legal Review Packet v0.1

Status: draft ready for human review; privacy legal review not approved.

This packet converts the `privacy_legal_review` commercial blocker into a
concrete human review surface. It does not contact legal counsel, complete
privacy legal review, publish terms, publish a privacy notice, approve customer
data processing, send a DPA, contact customers, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
privacy_legal_review_approval_status: {packet['privacy_legal_review_approval_status']}
ready_for_human_review: true
privacy_legal_review_evidence_complete: false
production_privacy_security_legal_ready: false
production_legal_ready: false
customer_data_processing_ready: false
legal_approval_completed: false
blockers_closed_by_packet: 0
```

## Required Privacy Legal Review Sections

{section_lines}

## Review Checklist

{checklist_lines}

## Approval Flags

These remain false until explicit human legal/privacy approval and production
evidence exist.

{approval_lines}

## Boundary Flags

{boundary_lines}

## Required Human Owners

- Legal owner
- Privacy owner
- Security owner
- Data operations owner
- Commercial owner

## Non-Approval Statement

This packet is not legal approval, not privacy review completion, not customer
data processing approval, not DPA availability, not customer contract evidence,
and not production legal readiness by itself. The `privacy_legal_review`
blocker remains open until the required review sections are approved and backed
by human-provided evidence.
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
        "SAEE_PRIVACY_LEGAL_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "privacy_legal_review_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
