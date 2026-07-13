#!/usr/bin/env python3
"""Build the Phase 5 customer validation/launch priority evidence packet.

This runner extracts Phase 5 pilot-results and customer-validation rows from
the cross-phase commercial production evidence collection packet and creates a
human-fillable priority template. It does not contact customers, execute
pilots, infer feedback, collect customer data, publish validation claims,
approve launch, close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKET_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet/commercial_production_evidence_collection_packet.local.json"
)
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_priority_evidence_collection"
)
OUTPUT_JSON = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_evidence_collection.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_evidence_collection.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_evidence_collection.csv"
OUTPUT_CHECKLIST = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_collection_checklist.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "phase_5_customer_validation_launch_evidence_input.priority.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "phase_5_customer_validation_launch_priority_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION_RECOMMENDATION_GATE.md"
)


PHASE_ID = "phase_5_customer_validation_and_launch_review"
TARGET_BLOCKERS = [
    "pilot_results",
    "customer_validated",
]
BLOCKER_PRIORITY = {blocker: index + 1 for index, blocker in enumerate(TARGET_BLOCKERS)}


BOUNDARY_FALSE_FLAGS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "customer_contacted_by_codex",
    "automated_customer_contact",
    "unsolicited_customer_contact",
    "customer_data_collected",
    "customer_data_processing_started",
    "customer_data_processed",
    "customer_secrets_collected",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "execution_authorized",
    "evidence_collection_authorized",
    "codex_executed_pilot",
    "pilot_session_started",
    "pilot_session_completed",
    "pilot_results_recorded",
    "feedback_form_completed",
    "permission_to_use_feedback_recorded",
    "public_validation_claim_published",
    "case_study_published",
    "testimonial_published",
    "product_market_fit_claimed",
    "production_readiness_claimed",
    "launch_approved",
    "public_launch_claim_added",
    "revenue_validated",
    "user_upload_enabled",
    "codex_inferred_missing_evidence",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def phase5_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in packet.get("evidence_collection_queue", [])
        if row.get("phase_id") == PHASE_ID
    ]
    rows.sort(
        key=lambda row: (
            BLOCKER_PRIORITY.get(str(row.get("blocker_id")), 99),
            0 if row.get("production_evidence_missing") is True else 1,
            str(row.get("evidence_key", "")),
        )
    )
    return rows


def build_priority_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        missing = row.get("production_evidence_missing") is True
        priority_rows.append(
            {
                "phase_5_record_id": f"P5-ECP-{index:03d}",
                "source_collection_record_id": row.get("collection_record_id", ""),
                "priority_rank": index,
                "priority_tier": (
                    "missing_production_evidence"
                    if missing
                    else "local_public_shell_requires_human_approval"
                ),
                "blocker_id": row.get("blocker_id", ""),
                "blocker_priority": BLOCKER_PRIORITY.get(str(row.get("blocker_id")), 99),
                "evidence_file_type": row.get("evidence_file_type", ""),
                "evidence_key": row.get("evidence_key", ""),
                "gap_status": row.get("gap_status", ""),
                "local_public_shell_value": row.get("local_public_shell_value") is True,
                "production_evidence_missing": missing,
                "owner_review_lane": row.get("owner_review_lane", "customer_validation"),
                "human_fill_status": "not_started",
                "human_evidence_value": None,
                "human_source_note": "",
                "accepted_for_blocker_closure": False,
                "human_review_required": True,
                "manual_collection_required": True,
                "execution_authorized": False,
                "evidence_collection_authorized": False,
                "requires_separate_execution_request": True,
                "must_not_touch": [
                    "runtime",
                    "backend",
                    "kernel",
                    "api_schema",
                    "private_core",
                    "production_customer_data",
                    "customer_contact_without_approval",
                    "pilot_execution_without_approval",
                    "feedback_inference_without_approval",
                    "customer_data_collection_without_approval",
                    "validation_claim_without_approval",
                    "case_study_without_approval",
                    "testimonial_without_approval",
                    "launch_approval_without_approval",
                ],
                "required_human_action": (
                    "Provide source-backed pilot/customer-validation evidence, permission records, and claim-scope approval; do not mark accepted for closure without a separate human approval."
                ),
            }
        )
    return priority_rows


def build_priority_template(priority_rows: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_keys = [row["evidence_key"] for row in priority_rows]
    return {
        "phase_5_customer_validation_launch_priority_evidence_collection_v0_1": True,
        "input_status": "priority_template_not_filled",
        "human_reviewer_name": "",
        "review_date": "",
        "evidence_source_notes": "",
        "source_collection_packet": rel(SOURCE_PACKET_PATH),
        "priority_collection_source": rel(OUTPUT_JSON),
        "template_note": (
            "Human owners fill evidence_review and source_notes_by_key. Codex must not infer customer evidence, contact customers, execute pilots, collect customer data, publish validation claims, publish testimonials, approve launch, or claim production readiness."
        ),
        "evidence_review": {key: False for key in evidence_keys},
        "source_notes_by_key": {key: "" for key in evidence_keys},
        "priority_evidence_key_order": evidence_keys,
        "priority_collection_map_by_key": {
            row["evidence_key"]: {
                "phase_5_record_id": row["phase_5_record_id"],
                "source_collection_record_id": row["source_collection_record_id"],
                "blocker_id": row["blocker_id"],
                "priority_tier": row["priority_tier"],
                "evidence_file_type": row["evidence_file_type"],
            }
            for row in priority_rows
        },
        "boundary_review": {
            "customer_contacted": False,
            "pilot_executed": False,
            "pilot_results_recorded": False,
            "feedback_form_completed": False,
            "customer_data_collected": False,
            "permission_to_use_feedback_recorded": False,
            "validation_claim_published": False,
            "case_study_published": False,
            "testimonial_published": False,
            "product_market_fit_claimed": False,
            "launch_approved": False,
            "product_launched": False,
            "customer_validated": False,
            "production_ready_claim": False,
        },
    }


def summarize_by_blocker(priority_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for blocker_id in TARGET_BLOCKERS:
        subset = [row for row in priority_rows if row["blocker_id"] == blocker_id]
        local_present = sum(1 for row in subset if row["local_public_shell_value"])
        missing = sum(1 for row in subset if row["production_evidence_missing"])
        summary.append(
            {
                "blocker_id": blocker_id,
                "required_items": len(subset),
                "local_public_shell_present": local_present,
                "missing_production_evidence": missing,
                "ready_to_close": False,
                "human_review_required": True,
                "execution_authorized": False,
                "evidence_collection_authorized": False,
                "next_action": (
                    "Human owner must provide source-backed pilot/customer-validation evidence in the priority template."
                ),
            }
        )
    return summary


def build_packet() -> dict[str, Any]:
    source_packet = read_json(SOURCE_PACKET_PATH)
    rows = phase5_rows(source_packet)
    priority_rows = build_priority_rows(rows)
    local_present = sum(1 for row in priority_rows if row["local_public_shell_value"])
    missing = sum(1 for row in priority_rows if row["production_evidence_missing"])
    packet: dict[str, Any] = {
        "packet_type": "saee_phase_5_customer_validation_launch_priority_evidence_collection",
        "packet_version": "0.1",
        "status": "ready_for_human_review_not_execution",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_phase5_customer_validation_launch_priority_evidence_collection.py",
        "scope": "phase_5_customer_validation_launch_priority_human_evidence_collection",
        "source_collection_packet": rel(SOURCE_PACKET_PATH),
        "human_fillable_template": rel(OUTPUT_TEMPLATE),
        "phase_id": PHASE_ID,
        "target_blocker_count": len(TARGET_BLOCKERS),
        "target_blockers": TARGET_BLOCKERS,
        "required_evidence_item_count": len(priority_rows),
        "local_public_shell_present_count": local_present,
        "missing_production_evidence_count": missing,
        "accepted_for_blocker_closure_count": 0,
        "blockers_closed_by_collection": 0,
        "blockers_ready_to_close": [],
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "recommended_next_action": (
            "Human validation owner fills the priority template with source-backed pilot/customer evidence, then opens a separate execution or blocker-closure request if justified."
        ),
        "post_fill_commands": [
            "python3 scripts/saee_customer_validation_evidence_runner.py",
            "python3 scripts/saee_phase5_customer_validation_launch_gap_audit.py",
            "python3 scripts/mainline_guard.py",
        ],
        "blocker_summary": summarize_by_blocker(priority_rows),
        "priority_rows": priority_rows,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        packet[flag] = False
    return packet


def csv_text(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = [
        "phase_5_record_id",
        "source_collection_record_id",
        "priority_rank",
        "priority_tier",
        "blocker_id",
        "evidence_file_type",
        "evidence_key",
        "gap_status",
        "local_public_shell_value",
        "production_evidence_missing",
        "owner_review_lane",
        "human_fill_status",
        "human_evidence_value",
        "human_source_note",
        "accepted_for_blocker_closure",
        "execution_authorized",
        "evidence_collection_authorized",
        "required_human_action",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return output.getvalue()


def render_readme(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 5 Customer Validation/Launch Priority Evidence Collection

Status: ready for human review, not execution.

This directory extracts the Phase 5 pilot-results and customer-validation
evidence items from the cross-phase commercial production evidence collection
packet and provides a human-fillable priority template.

Counts:

- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

Boundary:

- no customer contacted by Codex
- no automated customer contact
- no pilot executed by Codex
- no feedback inferred by Codex
- no customer data collected or processed
- no customer secrets collected
- no customer-validation claim published
- no case study or testimonial published
- no product-market-fit claim
- no launch approval
- no product launch
- no runtime, backend, kernel, API schema, or private-core modification
- no blocker closure
- No blocker closure
- no production-ready claim
"""


def render_report(packet: dict[str, Any]) -> str:
    blocker_lines = "\n".join(
        "- `{blocker_id}`: required={required_items}, local_public_shell={local_public_shell_present}, missing_production={missing_production_evidence}, ready_to_close=false".format(
            **row
        )
        for row in packet["blocker_summary"]
    )
    row_lines = "\n".join(
        "| {phase_5_record_id} | {priority_tier} | {blocker_id} | {evidence_key} | {human_fill_status} |".format(
            **row
        )
        for row in packet["priority_rows"]
    )
    return f"""# SAEE Phase 5 Customer Validation/Launch Priority Evidence Collection v0.1

## Summary

- status: {packet['status']}
- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

## Blocker Summary

{blocker_lines}

## Priority Rows

| Record | Priority tier | Blocker | Evidence key | Human fill status |
| --- | --- | --- | --- | --- |
{row_lines}

## How Human Owners Use This

1. Fill `phase_5_customer_validation_launch_evidence_input.priority.template.json`
   with source-backed pilot/customer-validation evidence.
2. Keep every boundary flag false unless a separate approved execution request
   exists.
3. Re-run the existing customer-validation evidence runner only after local
   evidence paths are configured by a human.
4. Re-run the Phase 5 gap audit and mainline guard.

## What This Does Not Do

It does not collect evidence, contact customers, execute pilots, infer
feedback, collect customer data, publish validation claims, publish case
studies or testimonials, claim product-market fit, approve launch, launch
product, close blockers, validate revenue, or claim production readiness.
"""


def render_checklist(packet: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 5 Customer Validation/Launch Priority Collection Checklist",
        "",
        "Use this only after a human owner decides to collect Phase 5 evidence.",
        "",
    ]
    for row in packet["priority_rows"]:
        lines.append(
            f"- [ ] {row['phase_5_record_id']} `{row['blocker_id']}` / `{row['evidence_key']}` "
            "-> fill `evidence_review` and `source_notes_by_key` in the priority template"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Do not contact customers from this packet.",
            "- Do not execute pilots from this packet.",
            "- Do not infer missing customer feedback from this packet.",
            "- Do not collect or process customer data from this packet.",
            "- Do not publish validation claims from this packet.",
            "- Do not publish case studies or testimonials from this packet.",
            "- Do not claim product-market fit from this packet.",
            "- Do not approve launch or launch product from this packet.",
            "- Do not close blockers from this packet.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_boundary(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 5 Priority Collection Boundary Audit

- customer_contacted_by_codex: false
- automated_customer_contact: false
- unsolicited_customer_contact: false
- codex_executed_pilot: false
- pilot_session_started: false
- pilot_session_completed: false
- pilot_results_recorded: false
- feedback_form_completed: false
- customer_data_collected: false
- customer_data_processing_started: false
- customer_data_processed: false
- customer_secrets_collected: false
- permission_to_use_feedback_recorded: false
- public_validation_claim_published: false
- case_study_published: false
- testimonial_published: false
- product_market_fit_claimed: false
- production_readiness_claimed: false
- customer_validated: false
- product_launched: false
- launch_approved: false
- public_launch_claim_added: false
- revenue_validated: false
- user_upload_enabled: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- production_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

This packet is a human-review collection planner only.
"""


def render_doc(packet: dict[str, Any]) -> str:
    return f"""# Phase 5 Customer Validation/Launch Priority Evidence Collection v0.1

phase_5_customer_validation_launch_priority_evidence_collection_v0_1: true
status: ready_for_human_review_not_execution
scope: phase_5_customer_validation_launch_priority_human_evidence_collection
required_evidence_item_count: {packet['required_evidence_item_count']}
local_public_shell_present_count: {packet['local_public_shell_present_count']}
missing_production_evidence_count: {packet['missing_production_evidence_count']}
accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
blockers_closed_by_collection: {packet['blockers_closed_by_collection']}
execution_authorized: false
evidence_collection_authorized: false
customer_contacted_by_codex: false
automated_customer_contact: false
codex_executed_pilot: false
pilot_session_completed: false
pilot_results_recorded: false
feedback_form_completed: false
customer_data_collected: false
customer_data_processing_started: false
permission_to_use_feedback_recorded: false
public_validation_claim_published: false
case_study_published: false
testimonial_published: false
product_market_fit_claimed: false
launch_approved: false
product_launched: false
customer_validated: false
revenue_validated: false
production_ready: false
private_core_exposed: false

This packet extracts the 12 Phase 5 evidence items from the cross-phase queue
and provides a human-fillable priority evidence template. It is not production
evidence and does not close blockers.
"""


def render_gate(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 5 Customer Validation/Launch Priority Evidence Collection Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_human_evidence_input: true
recommend_for_evidence_collection_authorization: false
recommend_for_execution_authorization: false
recommend_for_blocker_closure: false
recommend_for_customer_contact: false
recommend_for_pilot_execution: false
recommend_for_feedback_inference: false
recommend_for_customer_data_collection: false
recommend_for_customer_validation_claim: false
recommend_for_case_study_publication: false
recommend_for_testimonial_publication: false
recommend_for_product_market_fit_claim: false
recommend_for_launch_approval: false
recommend_for_product_launch: false

reason: This packet improves Phase 5 commercial readiness by creating a
human-fillable priority input surface for 12 pilot-results and
customer-validation evidence items. It does not supply evidence or authorize
execution.

counts:
- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

boundary:
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- revenue_validated: false
- execution_authorized: false
- evidence_collection_authorized: false
"""


def write_outputs(packet: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    template = build_priority_template(packet["priority_rows"])
    OUTPUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_TEMPLATE.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(packet["priority_rows"]), encoding="utf-8")
    OUTPUT_MD.write_text(render_report(packet), encoding="utf-8")
    OUTPUT_CHECKLIST.write_text(render_checklist(packet), encoding="utf-8")
    OUTPUT_BOUNDARY.write_text(render_boundary(packet), encoding="utf-8")
    README_PATH.write_text(render_readme(packet), encoding="utf-8")
    DOC_PATH.write_text(render_doc(packet), encoding="utf-8")
    GATE_PATH.write_text(render_gate(packet), encoding="utf-8")


def main() -> None:
    packet = build_packet()
    write_outputs(packet)
    print(
        "SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_PRIORITY_EVIDENCE_COLLECTION: PASS "
        f"required_items={packet['required_evidence_item_count']} "
        f"local_public_shell={packet['local_public_shell_present_count']} "
        f"missing_production={packet['missing_production_evidence_count']} "
        f"blockers_closed_by_collection={packet['blockers_closed_by_collection']}"
    )


if __name__ == "__main__":
    main()
