#!/usr/bin/env python3
"""Generate the SAEE support-contact decision packet.

This packet turns the support_contact commercial blocker into a focused human
decision surface. It does not publish a support contact, send test messages,
contact customers, contact vendors, enable customer support, close blockers,
modify backend behavior, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = OUTPUT_DIR / "support_contact_decision_packet.local.json"
OUTPUT_MD = OUTPUT_DIR / "support_contact_decision_packet.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "support_contact_decision_input.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "support_contact_decision_packet_boundary_audit.md"
DOC_PATH = (
    ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_DECISION_PACKET_V0_1.md"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_DECISION_PACKET_RECOMMENDATION_GATE.md"
)

TARGET_KEYS = [
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
]

FALSE_FLAGS = [
    "support_contact_available",
    "support_contact_configured",
    "customer_facing_support_contact_configured",
    "customer_support_available",
    "production_support_available",
    "support_process_available",
    "sla_available",
    "on_call_rotation_available",
    "support_vendor_contacted",
    "customer_contacted",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "production_ready",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "support_contact_published_by_codex",
    "support_contact_test_performed_by_codex",
    "blockers_closed_by_packet",
    "task_candidates_executed",
    "development_permission_granted",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def packet() -> dict[str, Any]:
    data: dict[str, Any] = {
        "packet_type": "saee_support_contact_decision_packet",
        "packet_version": "v0.1",
        "status": "ready_for_human_review_not_execution",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_support_contact_decision_packet.py",
        "blocker_target": "support_contact",
        "owner_lane": "commercial_support",
        "decision_scope": "human_review_of_customer_facing_support_contact",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "target_support_evidence_keys": TARGET_KEYS,
        "required_human_decision_fields": [
            "support_contact_channel",
            "support_contact_owner",
            "abuse_handling_note",
            "customer_notice_route_note",
            "support_contact_test_plan_note",
            "security_privacy_review_note",
            "rollback_or_disable_plan_note",
        ],
        "candidate_contact_slots": [
            {
                "slot_id": "support_contact_candidate_a",
                "contact_channel": "",
                "display_value_redacted": "",
                "owner_named": None,
                "abuse_handling_reviewed": None,
                "customer_notice_route_reviewed": None,
                "test_plan_reviewed": None,
                "human_source_note": "",
            },
            {
                "slot_id": "support_contact_candidate_b",
                "contact_channel": "",
                "display_value_redacted": "",
                "owner_named": None,
                "abuse_handling_reviewed": None,
                "customer_notice_route_reviewed": None,
                "test_plan_reviewed": None,
                "human_source_note": "",
            },
        ],
        "selection_criteria": [
            "A human owner can be named without exposing private credentials.",
            "The support contact route can be reviewed before customer-facing publication.",
            "Abuse handling and customer notice routing can be documented.",
            "A support contact test can be planned without Codex sending messages.",
            "Approved evidence can be copied into the production support/SLA evidence template only after human approval.",
        ],
        "evidence_mapping": {
            key: {
                "target_blocker": "support_contact",
                "target_template_path": key,
                "target_source_note_path": f"source_notes_by_key.{key}",
                "prefill_allowed": False,
                "requires_human_source_note": True,
            }
            for key in TARGET_KEYS
        },
        "next_human_action": (
            "Human commercial/support owner reviews candidate support contact "
            "evidence, decides whether publication is appropriate, and only then "
            "fills production_support_sla_evidence.template.json-derived evidence."
        ),
    }
    for flag in FALSE_FLAGS:
        data[flag] = False
    return data


def input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_support_contact_decision_input",
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "human_reviewer_name": "",
        "review_date": "",
        "selected_support_contact_channel": "",
        "decision_summary": "",
        "evidence_review": {key: False for key in TARGET_KEYS},
        "source_notes_by_key": {key: "" for key in TARGET_KEYS},
        "boundary_review": {flag: False for flag in FALSE_FLAGS},
        "candidate_contact_slots": packet()["candidate_contact_slots"],
        "template_note": (
            "This input does not configure or publish a SAEE support contact. "
            "It is a human review aid for support_contact evidence only."
        ),
    }


def md_body() -> str:
    rows = "\n".join(
        f"| `{key}` | `support_contact` | `{key}` | human source note required |"
        for key in TARGET_KEYS
    )
    return f"""# SAEE Support Contact Decision Packet v0.1

Status: ready_for_human_review_not_execution.

This packet narrows the `support_contact` commercial blocker into a human
decision surface. It helps a human owner decide whether SAEE has a
customer-facing support contact path that can later be recorded as production
support evidence.

It does not publish a support contact, send test messages, contact customers,
contact vendors, create a staffed support desk, approve SLA terms, start an
on-call rotation, modify backend behavior, close blockers, launch product, or
claim production readiness.

## Target Blocker

```text
blocker_target: support_contact
owner_lane: commercial_support
status: ready_for_human_review_not_execution
support_contact_available: false
support_contact_configured: false
customer_facing_support_contact_configured: false
blockers_closed_by_packet: false
```

## Evidence Mapping

| Evidence key | Blocker | Production support evidence field | Requirement |
| --- | --- | --- | --- |
{rows}

## Human Review Steps

1. List one or two candidate support contact routes in the template.
2. Record the human owner for the support contact.
3. Review abuse handling, customer notice routing, and privacy/security limits.
4. Record a support contact test plan without sending messages from Codex.
5. Only after separate approval, copy source-backed values into production
   support/SLA evidence.

## Existing Evidence Template

Use the existing template after human evidence exists:

```text
phase_b_product/commercial_readiness/production_evidence_templates/production_support_sla_evidence.template.json
```

## Non-Claims

- support_contact_available: false
- support_contact_configured: false
- customer_facing_support_contact_configured: false
- customer_support_available: false
- production_support_available: false
- support_process_available: false
- sla_available: false
- on_call_rotation_available: false
- customer_contacted: false
- support_vendor_contacted: false
- product_launched: false
- production_ready: false
- private_core_exposed: false
- support_contact_published_by_codex: false
- support_contact_test_performed_by_codex: false
- blockers_closed_by_packet: false
"""


def boundary_body() -> str:
    return """# SAEE Support Contact Decision Packet Boundary Audit

- No support contact published by Codex
- No support contact configured
- No support contact test performed by Codex
- No customer contacted
- No support vendor contacted
- No staffed support desk created
- No SLA terms approved
- No on-call rotation started
- No backend modified
- No runtime modified
- No kernel modified
- No API schema modified
- No private core exposed
- No product launched
- No production-ready claim
- No blocker closure
"""


def gate_body() -> str:
    return """# SAEE Support Contact Decision Packet Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_support_contact_publication: false
recommend_for_support_contact_configuration: false
recommend_for_support_contact_test: false
recommend_for_customer_support_claim: false
recommend_for_blocker_closure: false
recommend_for_production_launch: false

reason: The packet improves commercial readiness by turning the
`support_contact` blocker into a focused human decision surface. It does not
publish or configure contact information, send messages, or authorize
execution.

boundary:
- support_contact_available: false
- support_contact_configured: false
- customer_facing_support_contact_configured: false
- customer_support_available: false
- production_support_available: false
- support_process_available: false
- sla_available: false
- on_call_rotation_available: false
- customer_contacted: false
- support_vendor_contacted: false
- product_launched: false
- production_ready: false
- private_core_exposed: false
- support_contact_published_by_codex: false
- support_contact_test_performed_by_codex: false
- blockers_closed_by_packet: false
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = packet()
    write_json(OUTPUT_JSON, data)
    write_json(OUTPUT_TEMPLATE, input_template())
    body = md_body()
    write_text(OUTPUT_MD, body)
    write_text(DOC_PATH, body)
    write_text(OUTPUT_BOUNDARY, boundary_body())
    write_text(GATE_PATH, gate_body())
    print(
        "SAEE_SUPPORT_CONTACT_DECISION_PACKET: PASS "
        f"path={OUTPUT_JSON} status={data['status']} "
        "support_contact_available=false blockers_closed_by_packet=false"
    )


if __name__ == "__main__":
    main()
