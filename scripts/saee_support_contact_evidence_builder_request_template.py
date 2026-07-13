#!/usr/bin/env python3
"""Generate the support-contact evidence-builder request template.

This creates a local, human-fillable request template for the separate approval
needed before running the support-contact evidence builder. It does not publish
a support contact, send support messages, contact customers or vendors, run the
builder, close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"

OUTPUT_TEMPLATE = SUPPORT_DIR / "support_contact_evidence_builder_request.template.json"
OUTPUT_JSON = SUPPORT_DIR / "support_contact_evidence_builder_request.local.json"
OUTPUT_MD = SUPPORT_DIR / "support_contact_evidence_builder_request.md"
OUTPUT_CSV = SUPPORT_DIR / "support_contact_evidence_builder_request.csv"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "SUPPORT_CONTACT_EVIDENCE_BUILDER_REQUEST_TEMPLATE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_REQUEST_TEMPLATE_RECOMMENDATION_GATE.md"
)

APPROVAL_VALIDATION_PATH = (
    "phase_b_product/commercial_readiness/support_evidence/"
    "support_contact_approval_input_validation.local.json"
)
BUILDER_INPUT_PATH = (
    "phase_b_product/commercial_readiness/support_evidence/"
    "support_contact_decision_input.template.json"
)
TARGET_BUILDER = "scripts/saee_support_contact_evidence_builder.py"

CSV_FIELDS = [
    "item_id",
    "field_path",
    "item_type",
    "required_value",
    "current_value",
    "complete",
    "human_instruction",
]

ACKNOWLEDGEMENT_FIELDS = [
    "approval_input_validator_passed",
    "support_contact_readiness_board_reviewed",
    "human_filled_input_available",
    "validated_input_path_confirmed",
    "builder_input_path_confirmed",
    "target_builder_confirmed",
    "no_support_contact_publication_by_codex",
    "no_support_message_sent_by_codex",
    "no_customer_contact_by_codex",
    "no_vendor_contact_by_codex",
    "no_blocker_closure_by_request",
]

FALSE_FLAGS: dict[str, bool] = {
    "request_approved": False,
    "approval_input_validator_passed": False,
    "human_filled_input_available": False,
    "evidence_builder_execution_authorized": False,
    "evidence_builder_executed": False,
    "support_evidence_output_created_by_request": False,
    "support_contact_published_by_codex": False,
    "support_contact_test_sent_by_codex": False,
    "customer_contacted": False,
    "customer_contacted_by_codex": False,
    "support_vendor_contacted": False,
    "support_vendor_contacted_by_codex": False,
    "support_contact_published": False,
    "support_contact_test_performed": False,
    "customer_facing_support_contact_configured": False,
    "support_contact_available": False,
    "support_contact_configured": False,
    "customer_support_available": False,
    "production_support_available": False,
    "support_process_available": False,
    "sla_available": False,
    "on_call_rotation_available": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "development_permission_granted": False,
    "production_ready": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made_by_codex": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def request_template() -> dict[str, Any]:
    return {
        "template_type": "saee_support_contact_evidence_builder_request",
        "template_version": "v0.1",
        "request_status": "template_not_filled",
        "request_scope": "separate_human_approval_for_support_contact_evidence_builder",
        "target_blocker_id": "support_contact",
        "human_requester_name": "",
        "request_date": "",
        "approval_reference": "",
        "validated_input_path": "",
        "support_contact_review_reference": "",
        "approval_input_validation_path": APPROVAL_VALIDATION_PATH,
        "builder_input_path": BUILDER_INPUT_PATH,
        "target_builder": TARGET_BUILDER,
        "human_acknowledgements": {field: False for field in ACKNOWLEDGEMENT_FIELDS},
        "boundary_review": {
            "runtime_modified": False,
            "backend_modified": False,
            "kernel_modified": False,
            "api_schema_modified": False,
            "private_core_exposed": False,
            "product_launched": False,
            "customer_contacted": False,
            "production_ready": False,
            "support_contact_published_by_codex": False,
            "support_contact_test_sent_by_codex": False,
            "support_vendor_contacted_by_codex": False,
            "evidence_builder_executed": False,
            "blockers_closed_by_request": False,
        },
        "request_note": (
            "Fill this template only after the support-contact approval input "
            "validator passes. Filling this template still does not run the "
            "evidence builder; execution requires a separate human-approved "
            "command."
        ),
    }


def completion_rows(template: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    text_fields = [
        ("SC-EBR-001", "human_requester_name", "Name of the human owner requesting builder approval."),
        ("SC-EBR-002", "request_date", "Request date in YYYY-MM-DD format."),
        ("SC-EBR-003", "approval_reference", "Reference to the passing support-contact approval-input validation record."),
        ("SC-EBR-004", "validated_input_path", "Path to the human-filled support-contact input that passed validation."),
        ("SC-EBR-005", "support_contact_review_reference", "Reference to the reviewed support contact decision or readiness-board record."),
    ]
    for item_id, field, instruction in text_fields:
        value = str(template.get(field, ""))
        rows.append(
            {
                "item_id": item_id,
                "field_path": field,
                "item_type": "text",
                "required_value": "nonempty",
                "current_value": value,
                "complete": str(bool(value.strip())).lower(),
                "human_instruction": instruction,
            }
        )
    acknowledgements = template["human_acknowledgements"]
    for offset, field in enumerate(ACKNOWLEDGEMENT_FIELDS, start=6):
        current = acknowledgements.get(field) is True
        rows.append(
            {
                "item_id": f"SC-EBR-{offset:03d}",
                "field_path": f"human_acknowledgements.{field}",
                "item_type": "boolean",
                "required_value": "true",
                "current_value": str(current).lower(),
                "complete": str(current).lower(),
                "human_instruction": (
                    "Human must set this acknowledgement to true before support-contact "
                    "builder execution can be separately requested."
                ),
            }
        )
    return rows


def build_payload(template: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    required_item_count = len(rows)
    completed_item_count = sum(1 for row in rows if row["complete"] == "true")
    payload: dict[str, Any] = {
        "support_contact_evidence_builder_request_template_v0_1": True,
        "request_template_type": "saee_support_contact_evidence_builder_request_template",
        "request_template_version": "v0.1",
        "request_scope": "separate_human_approval_for_support_contact_evidence_builder",
        "status": "hold_human_support_contact_evidence_builder_request_required",
        "target_blocker_id": "support_contact",
        "target_builder": TARGET_BUILDER,
        "request_template_ready": True,
        "required_item_count": required_item_count,
        "completed_item_count": completed_item_count,
        "missing_item_count": required_item_count - completed_item_count,
        "blockers_closed_by_request_template": 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_support_contact_evidence_builder_request_template.py",
        "request_template": rel(OUTPUT_TEMPLATE),
        "request_status_json": rel(OUTPUT_JSON),
        "request_report": rel(OUTPUT_MD),
        "request_completion_csv": rel(OUTPUT_CSV),
        "approval_input_validation_path": APPROVAL_VALIDATION_PATH,
        "builder_input_path": BUILDER_INPUT_PATH,
        "next_action": (
            "A human owner should fill the request template only after the "
            "support-contact approval input validator passes, then make a "
            "separate explicit execution request if builder execution is desired."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def markdown_report(payload: dict[str, Any], rows: list[dict[str, str]]) -> str:
    lines = [
        "# SAEE Support Contact Evidence Builder Request Template",
        "",
        f"Status: {payload['status']}.",
        "",
        "This local template records the separate human approval request needed before running the support-contact evidence builder. It does not publish a support contact, send support messages, contact customers or vendors, run the builder, close blockers, launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- request_template_type: {payload['request_template_type']}",
        f"- request_scope: {payload['request_scope']}",
        f"- target_blocker_id: {payload['target_blocker_id']}",
        f"- target_builder: `{payload['target_builder']}`",
        "- request_template_ready: true",
        "- request_approved: false",
        "- approval_input_validator_passed: false",
        "- human_filled_input_available: false",
        "- evidence_builder_execution_authorized: false",
        "- evidence_builder_executed: false",
        "- support_evidence_output_created_by_request: false",
        "- blockers_closed_by_request_template: 0",
        "- production_ready: false",
        "",
        "## Completion Items",
        "",
        "| Item | Field | Type | Required | Current | Complete | Human Instruction |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {item_id} | `{field_path}` | {item_type} | {required_value} | {current_value} | {complete} | {human_instruction} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- external_calls_made_by_codex: false",
            "- external_model_api_called: false",
            "- support_contact_published_by_codex: false",
            "- support_contact_test_sent_by_codex: false",
            "- customer_contacted_by_codex: false",
            "- support_vendor_contacted_by_codex: false",
            "- evidence_collection_authorized: false",
            "- execution_authorized: false",
            "- development_permission_granted: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
        ]
    )
    return "\n".join(lines) + "\n"


def top_doc(payload: dict[str, Any]) -> str:
    return f"""# SAEE Support Contact Evidence Builder Request Template v0.1

support_contact_evidence_builder_request_template_v0_1: true
status: {payload['status']}
target_blocker_id: support_contact
target_builder: {TARGET_BUILDER}
request_template_ready: true
request_approved: false
evidence_builder_execution_authorized: false
evidence_builder_executed: false
blockers_closed_by_request_template: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This artifact provides the separate human approval request template required
after the support-contact approval input validator passes and before the
support-contact evidence builder is run.

It is a request template only. It does not run the builder, publish a support
contact, send support messages, contact customers or vendors, collect
production evidence, close blockers, launch product, or claim production
readiness.

## Files

- template: `phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_request.template.json`
- status: `phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_request.local.json`
- report: `phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_request.md`
- completion CSV: `phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_request.csv`
- script: `scripts/saee_support_contact_evidence_builder_request_template.py`
- smoke: `scripts/saee_support_contact_evidence_builder_request_template_smoke.py`

## Boundary

- request_approved: false
- evidence_builder_execution_authorized: false
- evidence_builder_executed: false
- support_contact_published_by_codex: false
- support_contact_test_sent_by_codex: false
- customer_contacted_by_codex: false
- support_vendor_contacted_by_codex: false
- production_ready: false
- blockers_closed_by_request_template: 0
"""


def gate_doc() -> str:
    return """# SAEE Support Contact Evidence Builder Request Template Recommendation Gate

answer: recommend
recommend_for_separate_human_evidence_builder_request: true
recommend_for_builder_execution: false
recommend_for_production: false

## Reason

The template fills a commercial-readiness gap between a passing support-contact
approval input validator and any later support-contact evidence builder
execution. It makes the separate human approval requirement explicit without
executing the builder or changing product behavior.

## Boundary

- evidence_builder_execution_authorized: false
- evidence_builder_executed: false
- support_contact_published_by_codex: false
- support_contact_test_sent_by_codex: false
- customer_contacted_by_codex: false
- support_vendor_contacted_by_codex: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Next Action

Human owner fills the request template only after the support-contact approval
input validator passes. Builder execution still requires a separate explicit
human-approved execution request.
"""


def main() -> None:
    template = request_template()
    rows = completion_rows(template)
    payload = build_payload(template, rows)
    write_json(OUTPUT_TEMPLATE, template)
    write_json(OUTPUT_JSON, payload)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown_report(payload, rows), encoding="utf-8")
    TOP_DOC.write_text(top_doc(payload), encoding="utf-8")
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(gate_doc(), encoding="utf-8")
    print("SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_REQUEST_TEMPLATE: PASS")


if __name__ == "__main__":
    main()
