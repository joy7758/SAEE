#!/usr/bin/env python3
"""Generate the SAEE DPA review human review packet.

The packet is a local, documentation-only commercial-readiness surface. It
does not create or approve a DPA, contact legal counsel, send terms to
customers, process customer data, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
PACKET_JSON = OUTPUT_DIR / "data_processing_agreement_review_packet.local.json"
PACKET_MD = OUTPUT_DIR / "data_processing_agreement_review_packet.md"

REQUIRED_DPA_REVIEW_SECTIONS = [
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
]

APPROVAL_FLAGS: dict[str, bool] = {
    "dpa_terms_approved": False,
    "controller_processor_roles_defined": False,
    "processing_purpose_approved": False,
    "data_categories_approved": False,
    "security_measures_approved": False,
    "subprocessor_terms_approved": False,
    "audit_rights_approved": False,
    "breach_notice_terms_approved": False,
    "deletion_or_return_terms_approved": False,
    "jurisdiction_and_transfer_terms_approved": False,
    "customer_dpa_template_available": False,
    "legal_reviewer_recorded": False,
}

BOUNDARY_FLAGS: dict[str, bool] = {
    "data_processing_agreement_available": False,
    "data_processing_agreement_approved": False,
    "dpa_sent_to_customer": False,
    "customer_contract_template_available": False,
    "customer_data_processing_approved": False,
    "customer_data_processed": False,
    "customer_data_processing_started": False,
    "privacy_legal_review_completed": False,
    "legal_counsel_contacted": False,
    "privacy_notice_published": False,
    "terms_published": False,
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
        "privacy_review_dependency_explicit": True,
        "customer_data_processing_requires_separate_approval": True,
        "customer_dpa_distribution_requires_separate_approval": True,
        "production_readiness_claim_forbidden": True,
        "private_core_detail_forbidden": True,
    }

    return {
        "packet_type": "saee_data_processing_agreement_review_packet",
        "packet_version": "v0.1",
        "packet_status": "draft_ready_for_human_review",
        "generated_by": "scripts/saee_data_processing_agreement_review_packet.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "review_scope": "data_processing_agreement_human_review_packet_only",
        "blocker_target": "data_processing_agreement",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "dpa_review_approval_status": "not_approved",
        "required_dpa_review_sections": REQUIRED_DPA_REVIEW_SECTIONS,
        "review_checklist": review_checklist,
        "approval_flags": APPROVAL_FLAGS,
        "boundary_flags": BOUNDARY_FLAGS,
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
        "next_action": (
            "Human legal, privacy, security, data-operations, and commercial "
            "owners must review controller/processor roles, processing purpose, "
            "data categories, security measures, subprocessors, audit rights, "
            "breach notice, deletion/return, jurisdiction/transfer terms, and "
            "customer DPA template boundaries before the data_processing_agreement "
            "blocker can close."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    section_lines = "\n".join(f"- {item}" for item in packet["required_dpa_review_sections"])
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
    return f"""# SAEE Data Processing Agreement Review Packet v0.1

Status: draft ready for human review; DPA not approved or available.

This packet converts the `data_processing_agreement` commercial blocker into a
concrete human review surface. It does not create a DPA, approve a DPA, publish
terms, send a DPA to customers, approve customer data processing, contact
customers, or make SAEE production-ready.

## Scope

```yaml
packet_type: {packet['packet_type']}
packet_status: {packet['packet_status']}
review_scope: {packet['review_scope']}
blocker_target: {packet['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
dpa_review_approval_status: {packet['dpa_review_approval_status']}
ready_for_human_review: true
dpa_review_packet_evidence_complete: false
data_processing_agreement_available: false
production_privacy_security_legal_ready: false
production_legal_ready: false
customer_data_processing_ready: false
legal_approval_completed: false
blockers_closed_by_packet: 0
```

## Required DPA Review Sections

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

This packet is not a DPA, not legal approval, not privacy legal review
completion, not customer data processing approval, not customer contract
evidence, and not production legal readiness by itself. The
`data_processing_agreement` blocker remains open until the required DPA terms
are approved and backed by human-provided evidence.
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
        "SAEE_DATA_PROCESSING_AGREEMENT_REVIEW_PACKET: PASS "
        f"path={PACKET_JSON} status={packet['packet_status']} "
        "dpa_review_packet_evidence_complete=false production_ready=false"
    )


if __name__ == "__main__":
    main()
