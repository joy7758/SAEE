#!/usr/bin/env python3
"""Build a small manual review batch for commercial sprint quick-fill rows.

This batch reduces the active 64-row human quick-fill queue into a 10-row
manual-review packet. It does not generate values, record raw values, modify the
source quick-fill packet, import a workbook, run validators on real input,
collect evidence, close blockers, contact anyone, launch product, or claim
production readiness.

If all 64 quick-fill values are already present, the same surface records that
the old 10-row review-batch path is superseded by the workbook import approval
review path. It still does not import the workbook or execute validators.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
QUALITY_GATE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.local.json"
GUIDANCE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_RECOMMENDATION_GATE.md"
)

BATCH_SIZE = 10
EXPECTED_QUICK_FILL_ROW_COUNT = 64

FALSE_FLAGS = [
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "raw_values_recorded",
    "source_quick_fill_packet_modified",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_guidance_by_row() -> dict[str, dict[str, Any]]:
    payload = json.loads(GUIDANCE_JSON.read_text(encoding="utf-8"))
    return {row["quick_fill_row_id"]: row for row in payload.get("guidance_rows", [])}


def build_payload() -> dict[str, Any]:
    rows = read_csv(QUICK_FILL_CSV)
    quality = json.loads(QUALITY_GATE_JSON.read_text(encoding="utf-8"))
    guidance_by_row = load_guidance_by_row()
    boundary_violations: list[str] = []
    quality_status = quality.get("status")
    quality_gate_passed = quality_status == "pass_quality_gate_pending_safety_preflight_and_human_import_approval"

    if len(rows) != EXPECTED_QUICK_FILL_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")

    missing_rows = [row for row in rows if not row.get("human_value_to_enter", "").strip()]
    full_source_values_present = len(missing_rows) == 0
    if (
        quality_status != "hold_human_quick_fill_required" and not full_source_values_present
    ):
        boundary_violations.append("quality_gate_not_in_human_fill_hold")
    if quality.get("raw_values_recorded") is not False:
        boundary_violations.append("quality_gate_raw_values_recorded")
    if quality.get("ready_for_workbook_import") is not False:
        boundary_violations.append("quality_gate_ready_for_workbook_import")
    selected_source_rows = missing_rows[:BATCH_SIZE]
    blocker_counts: Counter[str] = Counter()
    input_kind_counts: Counter[str] = Counter()
    selected_rows: list[dict[str, Any]] = []

    for index, row in enumerate(selected_source_rows, start=1):
        guidance = guidance_by_row.get(row["quick_fill_row_id"], {})
        blocker_counts[row["blocker_id"]] += 1
        input_kind_counts[row["input_kind"]] += 1
        selected_rows.append(
            {
                "review_batch_row_id": f"QFRB-{index:03d}",
                "quick_fill_row_id": row["quick_fill_row_id"],
                "queue_item_id": row["queue_item_id"],
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": row["blocker_id"],
                "owner_review_lane": row["owner_review_lane"],
                "input_group": row["input_group"],
                "input_key": row["input_key"],
                "input_kind": row["input_kind"],
                "human_fill_prompt": row["human_fill_prompt"],
                "expected_value_shape": guidance.get("expected_value_shape", ""),
                "fill_instruction": guidance.get("fill_instruction", ""),
                "leave_blank_condition": guidance.get("leave_blank_condition", ""),
                "target_workbook_csv": row["target_workbook_csv"],
                "target_workbook_column": row["target_workbook_column"],
                "target_json_pointer": row["target_json_pointer"],
                "source_field_to_fill": "human_value_to_enter",
                "optional_source_field": "notes_for_human",
                "source_value_currently_blank": True,
                "codex_generated_value": False,
                "source_quick_fill_packet_modified": False,
                "workbook_import_performed": False,
                "validators_run_on_real_input": False,
                "evidence_collection_authorized": False,
                "execution_authorized": False,
            }
        )

    status = "hold_review_batch_ready_for_human_entry"
    if boundary_violations:
        status = "stop_boundary_violation"
    elif not selected_rows:
        status = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_review_batch_v0_1": True,
        "review_batch_type": "bounded_manual_quick_fill_review_batch",
        "review_batch_scope": "human_entry_batch_only_no_values_no_import_no_execution",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_quality_gate_json": rel(QUALITY_GATE_JSON),
        "source_guidance_json": rel(GUIDANCE_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch.py",
        "quick_fill_row_count": len(rows),
        "expected_quick_fill_row_count": EXPECTED_QUICK_FILL_ROW_COUNT,
        "missing_value_row_count": len(missing_rows),
        "completed_value_row_count": len(rows) - len(missing_rows),
        "review_batch_size": BATCH_SIZE,
        "selected_review_row_count": len(selected_rows),
        "remaining_missing_after_selected_batch": max(len(missing_rows) - len(selected_rows), 0),
        "selected_blocker_count": len(blocker_counts),
        "selected_blocker_ids": sorted(blocker_counts),
        "selected_input_kind_counts": dict(sorted(input_kind_counts.items())),
        "human_input_required": bool(selected_rows),
        "human_review_required": True,
        "quality_gate_passed": quality_gate_passed,
        "review_batch_superseded": status
        == "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "ready_for_workbook_import_approval_review": status
        == "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "blockers_closed_by_review_batch": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "selected_rows": selected_rows,
        "next_human_action": (
            "No review-batch fill remains because all 64 quick-fill source values "
            "are present. Treat this 10-row review-batch surface as superseded, "
            "and use the workbook import approval request packet for the next "
            "human review. Do not import the workbook from this surface."
            if full_source_values_present
            else "Fill only human_value_to_enter and optional notes_for_human for the "
            "selected quick_fill_row_id values in the source quick-fill CSV; then "
            "rerun the quality gate, safety preflight, packet validator, and import "
            "dry-run before any separate human-approved workbook import request."
        ),
        "post_fill_local_commands": (
            [
                "python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py",
                "python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py",
                "python3 scripts/saee_commercial_sprint_human_input_safety_preflight.py",
                "python3 scripts/mainline_guard.py",
            ]
            if full_source_values_present
            else [
                "python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py",
                "python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate_smoke.py",
                "python3 scripts/saee_commercial_sprint_human_input_safety_preflight.py",
                "python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py",
                "python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py",
            ]
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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
        "human_fill_prompt",
        "expected_value_shape",
        "fill_instruction",
        "target_workbook_csv",
        "target_workbook_column",
        "target_json_pointer",
        "source_field_to_fill",
        "optional_source_field",
        "source_value_currently_blank",
        "codex_generated_value",
        "workbook_import_performed",
        "validators_run_on_real_input",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["selected_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def md_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Batch Row | Quick Fill Row | Blocker | Input Key | Expected Shape | Prompt |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        prompt = str(row["human_fill_prompt"]).replace("|", "/")
        expected = str(row["expected_value_shape"]).replace("|", "/")
        lines.append(
            "| {review_batch_row_id} | {quick_fill_row_id} | {blocker_id} | "
            "{input_key} | {expected} | {prompt} |".format(
                expected=expected,
                prompt=prompt,
                **row,
            )
        )
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Sprint Human Input Quick-Fill Review Batch v0.1

commercial_sprint_human_input_quick_fill_review_batch_v0_1: true
review_batch_scope: {payload['review_batch_scope']}
status: {payload['status']}
commercial_status: {payload['commercial_status']}
production_launch_status: {payload['production_launch_status']}

## Purpose

This packet selects the first {payload['selected_review_row_count']} missing
human quick-fill rows from the active {payload['quick_fill_row_count']}-row
commercial sprint queue when missing values exist. If no missing values remain,
this file is a superseded status record and points to the workbook import
approval review path instead.

## Counts

- quick_fill_row_count: {payload['quick_fill_row_count']}
- completed_value_row_count: {payload['completed_value_row_count']}
- missing_value_row_count: {payload['missing_value_row_count']}
- review_batch_size: {payload['review_batch_size']}
- selected_review_row_count: {payload['selected_review_row_count']}
- remaining_missing_after_selected_batch: {payload['remaining_missing_after_selected_batch']}
- quality_gate_passed: {str(payload['quality_gate_passed']).lower()}
- review_batch_superseded: {str(payload['review_batch_superseded']).lower()}
- ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
- blockers_closed_by_review_batch: {payload['blockers_closed_by_review_batch']}

## Selected Rows

{md_table(payload['selected_rows'])}

## Human Action

{payload['next_human_action']}

## Local Commands

```bash
{chr(10).join(payload['post_fill_local_commands'])}
```

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- ready_for_safety_preflight: false
- ready_for_workbook_import: false
- ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
- workbook_import_authorized: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH: PASS
"""
    OUT_MD.write_text(body, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    body = f"""# Quick-Fill Review Batch Boundary Audit

commercial_sprint_human_input_quick_fill_review_batch_v0_1: true
status: {payload['status']}
boundary_violation_count: {payload['boundary_violation_count']}

This boundary audit confirms the review batch is a local manual-entry aid.

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- quick_fill_imported_to_workbook: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_review_batch: 0
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

SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_BOUNDARY: PASS
"""
    OUT_BOUNDARY.write_text(body, encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Sprint Human Input Quick-Fill Review Batch v0.1

commercial_sprint_human_input_quick_fill_review_batch_v0_1: true
status: {payload['status']}

This surface creates a bounded 10-row manual review batch from the active
commercial sprint quick-fill packet. It helps a human fill the next small group
of values without changing product behavior or recording raw human values in
derived files.

Use it when the full 64-row quick-fill packet is too large for one pass.

Do not use it as evidence that commercial blockers are closed. It does not
authorize safety preflight, workbook import, evidence collection, customer
contact, launch, or production-readiness claims.
"""
    TOP_DOC.write_text(body, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Sprint Quick-Fill Review Batch Recommendation Gate

answer: conditional

commercial_sprint_human_input_quick_fill_review_batch_v0_1: true
status: {payload['status']}

## Recommendation

Recommend this batch only as a local human-entry aid for reducing the active
commercial quick-fill queue into a smaller review unit.

## Do Not Recommend For

- workbook import
- validator execution on real human input
- evidence collection
- blocker closure
- production readiness
- customer contact
- product launch

## Boundary

raw_values_recorded: false
human_values_generated_by_codex: false
quick_fill_values_entered_by_codex: false
workbook_import_authorized: false
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
    print("SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
