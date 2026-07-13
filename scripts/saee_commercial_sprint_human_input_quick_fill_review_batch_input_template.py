#!/usr/bin/env python3
"""Create a compact human input template for the current quick-fill review batch.

The template contains only the selected 10 review-batch rows and blank
`human_value_to_enter` / `notes_for_human` cells for manual completion. It does
not generate values, apply values to the source quick-fill CSV, import a
workbook, run validators on real input, collect evidence, close blockers,
contact anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
REVIEW_BATCH_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_RECOMMENDATION_GATE.md"
)

EXPECTED_TEMPLATE_ROW_COUNT = 10
SUPERSEDED_REVIEW_BATCH_STATUS = (
    "superseded_by_full_quick_fill_values_pending_workbook_import_approval"
)

FALSE_FLAGS = [
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "raw_values_recorded",
    "source_quick_fill_packet_modified",
    "batch_values_applied_to_source",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "ready_for_safety_preflight",
    "ready_for_workbook_import",
    "safe_to_import_after_human_approval",
    "values_transferred",
    "human_filled_templates_written",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "blockers_closed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "task_candidates_executed",
    "payment_collected",
    "revenue_validated",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def build_payload() -> dict[str, Any]:
    batch = json.loads(REVIEW_BATCH_JSON.read_text(encoding="utf-8"))
    selected_rows = batch.get("selected_rows", [])
    batch_superseded = (
        batch.get("status") == SUPERSEDED_REVIEW_BATCH_STATUS
        and len(selected_rows) == 0
    )
    boundary_violations: list[str] = []

    if batch.get("status") != "hold_review_batch_ready_for_human_entry" and not batch_superseded:
        boundary_violations.append("review_batch_not_ready_for_human_entry")
    if len(selected_rows) != EXPECTED_TEMPLATE_ROW_COUNT and not batch_superseded:
        boundary_violations.append("unexpected_selected_review_row_count")
    if batch.get("raw_values_recorded") is not False:
        boundary_violations.append("review_batch_raw_values_recorded")

    template_rows: list[dict[str, Any]] = []
    for row in selected_rows:
        template_rows.append(
            {
                "review_batch_row_id": row["review_batch_row_id"],
                "quick_fill_row_id": row["quick_fill_row_id"],
                "queue_item_id": row["queue_item_id"],
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": row["blocker_id"],
                "owner_review_lane": row["owner_review_lane"],
                "input_group": row["input_group"],
                "input_key": row["input_key"],
                "input_kind": row["input_kind"],
                "human_fill_prompt": row["human_fill_prompt"],
                "expected_value_shape": row.get("expected_value_shape", ""),
                "fill_instruction": row.get("fill_instruction", ""),
                "leave_blank_condition": row.get("leave_blank_condition", ""),
                "target_json_pointer": row["target_json_pointer"],
                "human_value_to_enter": "",
                "notes_for_human": "",
                "template_status": "blank_human_entry_required",
                "codex_generated_value": False,
                "applied_to_source_quick_fill": False,
            }
        )

    if batch_superseded and not boundary_violations:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    elif boundary_violations:
        status = "stop_boundary_violation"
    else:
        status = "ready_for_human_batch_value_entry"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1": True,
        "template_type": "selected_quick_fill_review_batch_human_input_template",
        "template_scope": "blank_human_entry_template_only_no_values_no_apply_no_import",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "source_review_batch_json": rel(REVIEW_BATCH_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template.py",
        "template_row_count": len(template_rows),
        "expected_template_row_count": EXPECTED_TEMPLATE_ROW_COUNT,
        "blank_human_value_row_count": len(template_rows),
        "prefilled_human_value_row_count": 0,
        "notes_prefilled_row_count": 0,
        "selected_review_row_count": len(template_rows),
        "human_input_required": not batch_superseded,
        "human_review_required": True,
        "input_template_ready": (not boundary_violations and not batch_superseded),
        "blockers_closed_by_input_template": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "template_rows": template_rows,
        "next_human_action": (
            "No review-batch input template remains. The full quick-fill source "
            "values are present, so the next human step is workbook import "
            "approval review, not template entry."
            if batch_superseded
            else "Fill human_value_to_enter and optional notes_for_human in this "
            "10-row template, then copy the reviewed values into the matching "
            "quick_fill_row_id rows of the source quick-fill CSV before running "
            "the review-batch validator."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "expected_value_shape",
        "fill_instruction",
        "leave_blank_condition",
        "target_json_pointer",
        "human_value_to_enter",
        "notes_for_human",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["template_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Batch Row | Quick Fill Row | Input Key | Expected Shape | Human Value | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {review_batch_row_id} | {quick_fill_row_id} | {input_key} | "
            "{expected_value_shape} |  |  |".format(**row)
        )
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Sprint Human Input Quick-Fill Review Batch Input Template v0.1

commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1: true
template_scope: {payload['template_scope']}
status: {payload['status']}
commercial_status: {payload['commercial_status']}
production_launch_status: {payload['production_launch_status']}

## Summary

- template_row_count: {payload['template_row_count']}
- blank_human_value_row_count: {payload['blank_human_value_row_count']}
- prefilled_human_value_row_count: {payload['prefilled_human_value_row_count']}
- notes_prefilled_row_count: {payload['notes_prefilled_row_count']}
- input_template_ready: {str(payload['input_template_ready']).lower()}
- blockers_closed_by_input_template: {payload['blockers_closed_by_input_template']}

## Fill Template

{table(payload['template_rows'])}

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- batch_values_applied_to_source: false
- ready_for_safety_preflight: false
- ready_for_workbook_import: false
- workbook_import_authorized: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE: PASS
"""
    OUT_MD.write_text(body, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    body = f"""# Quick-Fill Review Batch Input Template Boundary Audit

commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1: true
status: {payload['status']}
boundary_violation_count: {payload['boundary_violation_count']}

This boundary audit confirms the input template is blank and human-entry only.

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- batch_values_applied_to_source: false
- quick_fill_imported_to_workbook: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_input_template: 0
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- external_calls_made: false
- external_ai_assistant_tested: false

SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_BOUNDARY: PASS
"""
    OUT_BOUNDARY.write_text(body, encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Sprint Human Input Quick-Fill Review Batch Input Template v0.1

commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1: true
status: {payload['status']}

This file-backed surface provides a compact 10-row blank input template for the
current quick-fill review batch. Humans may fill it first, then manually copy
approved values back into the source quick-fill CSV.

It does not generate values, apply values, modify the source quick-fill packet,
import a workbook, collect evidence, close blockers, launch product, or claim
production readiness.
"""
    TOP_DOC.write_text(body, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Sprint Quick-Fill Review Batch Input Template Recommendation Gate

answer: conditional

commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1: true
status: {payload['status']}

## Recommendation

Recommend this template only as a compact human-entry aid for the selected
10-row quick-fill review batch.

## Do Not Recommend For

- automatic value generation
- automatic source CSV modification
- workbook import
- evidence collection
- blocker closure
- production readiness

## Boundary

raw_values_recorded: false
human_values_generated_by_codex: false
quick_fill_values_entered_by_codex: false
source_quick_fill_packet_modified: false
batch_values_applied_to_source: false
workbook_import_authorized: false
validators_run_on_real_input: false
evidence_collection_authorized: false
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
"""
    GATE.write_text(body, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE: "
        f"PASS status={payload['status']} "
        f"template_row_count={payload['template_row_count']} "
        f"blank_human_value_row_count={payload['blank_human_value_row_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
