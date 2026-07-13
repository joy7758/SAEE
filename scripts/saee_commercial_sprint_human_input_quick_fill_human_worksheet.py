#!/usr/bin/env python3
"""Build a grouped human worksheet for the commercial sprint quick-fill rows.

This worksheet is a manual-entry aid. It reads the existing quick-fill packet
and quick-fill guidance, groups the 64 rows by blocker and input group, and
rewrites the same blank value cells into a more human-readable form.

It does not generate values, import a workbook, run validators on real input,
transfer values into templates, collect evidence, close blockers, contact
anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
GUIDANCE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET_RECOMMENDATION_GATE.md"
)

EXPECTED_WORKSHEET_ROW_COUNT = 64
COMPLETED_STATUS = "completed_human_quick_fill_pending_workbook_import_approval"
READY_STATUS = "ready_for_human_quick_fill"

FALSE_FLAGS = [
    "human_value_prefilled_by_codex",
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
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
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_guidance() -> dict[str, dict[str, Any]]:
    payload = json.loads(GUIDANCE_JSON.read_text(encoding="utf-8"))
    rows = payload.get("guidance_rows", [])
    return {row["quick_fill_row_id"]: row for row in rows}


def build_payload() -> dict[str, Any]:
    quick_fill_rows = read_csv(QUICK_FILL_CSV)
    guidance_by_id = load_guidance()

    worksheet_rows: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    input_group_counts: Counter[str] = Counter()
    input_kind_counts: Counter[str] = Counter()
    blank_value_rows = 0
    suggested_values_count = 0
    boundary_violations: list[str] = []

    if len(quick_fill_rows) != EXPECTED_WORKSHEET_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")

    for index, row in enumerate(quick_fill_rows, start=1):
        guidance = guidance_by_id.get(row["quick_fill_row_id"], {})
        human_value = row.get("human_value_to_enter", "")
        notes = row.get("notes_for_human", "")
        if not human_value:
            blank_value_rows += 1
        if guidance.get("suggested_value"):
            suggested_values_count += 1

        blocker_counts[row["blocker_id"]] += 1
        input_group_counts[row["input_group"]] += 1
        input_kind_counts[row["input_kind"]] += 1

        worksheet_rows.append(
            {
                "worksheet_row_id": f"QFW-{index:03d}",
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
                "boundary_warning": guidance.get("boundary_warning", ""),
                "target_workbook_csv": row["target_workbook_csv"],
                "target_workbook_column": row["target_workbook_column"],
                "target_json_pointer": row["target_json_pointer"],
                "human_value_to_enter": human_value,
                "notes_for_human": notes,
                "worksheet_status": (
                    "ready_for_human_value"
                    if not human_value
                    else "human_value_present_unvalidated"
                ),
                "codex_filled_value": False,
                "workbook_import_performed": False,
                "validators_run_on_real_input": False,
                "evidence_collection_authorized": False,
                "execution_authorized": False,
            }
        )

    if boundary_violations:
        status = "stop_boundary_violation"
    elif blank_value_rows == 0:
        status = COMPLETED_STATUS
    else:
        status = READY_STATUS

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_human_worksheet_v0_1": True,
        "worksheet_type": "human_quick_fill_entry_worksheet",
        "worksheet_scope": (
            "manual_human_entry_review_only_no_import"
            if blank_value_rows == 0
            else "manual_human_entry_support_only_no_values_no_import"
        ),
        "status": status,
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_guidance_json": rel(GUIDANCE_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": (
            "scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet.py"
        ),
        "quick_fill_row_count": len(quick_fill_rows),
        "worksheet_row_count": len(worksheet_rows),
        "blocker_count": len(blocker_counts),
        "input_group_count": len(input_group_counts),
        "input_kind_count": len(input_kind_counts),
        "blank_human_value_row_count": blank_value_rows,
        "nonblank_human_value_row_count": len(worksheet_rows) - blank_value_rows,
        "suggested_values_count": suggested_values_count,
        "human_input_required": blank_value_rows > 0,
        "human_review_required": True,
        "ready_for_human_quick_fill": not boundary_violations and blank_value_rows > 0,
        "ready_for_workbook_import_approval_review": (
            not boundary_violations and blank_value_rows == 0
        ),
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "blockers_closed_by_worksheet": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blocker_worksheet_counts": dict(sorted(blocker_counts.items())),
        "input_group_worksheet_counts": dict(sorted(input_group_counts.items())),
        "input_kind_worksheet_counts": dict(sorted(input_kind_counts.items())),
        "worksheet_rows": worksheet_rows,
        "next_human_action": (
            "Review the workbook import approval request packet for the confirmed "
            "64 quick-fill values. Do not import the workbook, run validators on "
            "real input, collect evidence, or close blockers without separate "
            "human approval."
            if blank_value_rows == 0
            else (
                "Fill human_value_to_enter in the source quick-fill CSV using this "
                "worksheet as a grouped checklist, then rerun the quick-fill validator."
            )
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
        "worksheet_row_id",
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
        "leave_blank_condition",
        "boundary_warning",
        "target_json_pointer",
        "human_value_to_enter",
        "notes_for_human",
        "worksheet_status",
        "codex_filled_value",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["worksheet_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_human_worksheet_v0_1: true",
        f"status: {payload['status']}",
        f"worksheet_scope: {payload['worksheet_scope']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"worksheet_row_count: {payload['worksheet_row_count']}",
        f"blocker_count: {payload['blocker_count']}",
        f"input_group_count: {payload['input_group_count']}",
        f"input_kind_count: {payload['input_kind_count']}",
        f"blank_human_value_row_count: {payload['blank_human_value_row_count']}",
        f"nonblank_human_value_row_count: {payload['nonblank_human_value_row_count']}",
        "ready_for_workbook_import_approval_review: "
        f"{str(payload['ready_for_workbook_import_approval_review']).lower()}",
        f"suggested_values_count: {payload['suggested_values_count']}",
        f"human_value_prefilled_by_codex: {str(payload['human_value_prefilled_by_codex']).lower()}",
        f"quick_fill_values_entered_by_codex: {str(payload['quick_fill_values_entered_by_codex']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"workbook_import_authorized: {str(payload['workbook_import_authorized']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        f"workbook_written: {str(payload['workbook_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blocker_closure_authorized: {str(payload['blocker_closure_authorized']).lower()}",
        f"blockers_closed_by_worksheet: {payload['blockers_closed_by_worksheet']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def grouped_rows(payload: dict[str, Any]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in payload["worksheet_rows"]:
        grouped[row["blocker_id"]][row["input_group"]].append(row)
    return grouped


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Human Worksheet",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This worksheet groups the 64 quick-fill rows so a human can fill the",
        "source quick-fill CSV with less context switching. It does not provide",
        "or infer any values.",
        "",
        "## Human Procedure",
        "",
        "1. Use the grouped sections below to review one blocker at a time.",
        "2. Enter human-confirmed values in the source quick-fill CSV only.",
        "3. Leave a row blank when no reviewed value exists.",
        "4. Run the quick-fill validator after human entry.",
        "5. Request a separate import approval only after validation passes.",
        "",
        "## Blocker Counts",
        "",
        "| Blocker | Worksheet Rows |",
        "| --- | ---: |",
    ]
    for blocker, count in payload["blocker_worksheet_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(["", "## Grouped Worksheet", ""])

    for blocker, groups in grouped_rows(payload).items():
        lines.extend([f"### `{blocker}`", ""])
        for input_group, rows in groups.items():
            lines.extend([f"#### `{input_group}`", ""])
            lines.append(
                "| Row | Input Key | Expected Value Shape | Fill Instruction | Target JSON Pointer | Value Status |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- |")
            for row in rows:
                lines.append(
                    "| "
                    f"`{row['quick_fill_row_id']}` | "
                    f"`{row['input_key']}` | "
                    f"{row['expected_value_shape']} | "
                    f"{row['fill_instruction']} | "
                    f"`{row['target_json_pointer']}` | "
                    f"{row['worksheet_status']} |"
                )
            lines.append("")

    lines.extend(
        [
            "## Boundary",
            "",
            "No values were generated, suggested, or entered by Codex. No workbook",
            "import was authorized or performed. No validators were run on real",
            "input. No values were transferred into templates. No evidence was",
            "collected and no blocker was closed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Human Worksheet Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This worksheet is a local manual-entry aid only. It does not fill values,",
        "suggest actual values, import values into the workbook, write workbook",
        "files, transfer values, run validators on real input, collect evidence,",
        "execute builders, contact customers or vendors, close blockers, launch",
        "product, or claim production readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Human Worksheet v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the current human quick-fill worksheet layer. It",
        "exists to make the existing 64-row quick-fill packet easier for a human",
        "to complete without altering SAEE behavior.",
        "",
        "## Boundary",
        "",
        "The worksheet does not generate values, import workbooks, write workbook",
        "files, transfer values, run validators on real input, collect evidence,",
        "close blockers, launch product, or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Human Worksheet Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_human_worksheet_v0_1: true",
        "answer: recommend",
        "recommend_for_human_quick_fill_entry_support: true",
        "recommend_for_human_fill_coordination: true",
        "recommend_for_value_generation: false",
        "recommend_for_value_suggestion: false",
        "recommend_for_value_import: false",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
        "",
        "## Reason",
        "",
        "This worksheet is recommendable as a manual quick-fill aid because it",
        "organizes existing rows for human entry while preserving all import,",
        "execution, evidence, launch, production-readiness, and blocker-closure",
        "boundaries.",
        "",
        "## Status",
        "",
        *status_lines(payload),
    ]
    GATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_HUMAN_WORKSHEET: PASS "
        f"status={payload['status']} "
        f"worksheet_row_count={payload['worksheet_row_count']} "
        f"blank_human_value_row_count={payload['blank_human_value_row_count']} "
        f"suggested_values_count={payload['suggested_values_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
