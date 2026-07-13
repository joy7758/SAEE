#!/usr/bin/env python3
"""Build row-level guidance for commercial sprint quick-fill inputs.

This guidance helps a human fill `human_value_to_enter` consistently. It does
not enter values, import values into the workbook, transfer values into
templates, write human-filled templates, run validators on real input, collect
evidence, execute builders, contact anyone, close blockers, launch product, or
claim production readiness.
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
QUICK_FILL_VALIDATION_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"
)

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE_RECOMMENDATION_GATE.md"
)

EXPECTED_GUIDANCE_ROW_COUNT = 64

FALSE_FLAGS = [
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
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "task_candidates_executed",
    "human_input_filled_by_codex",
    "quick_fill_values_entered_by_codex",
    "quick_fill_imported_to_workbook",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def guidance_for(row: dict[str, str]) -> tuple[str, str, str, str]:
    input_kind = row["input_kind"]
    input_group = row["input_group"]
    input_key = row["input_key"]

    boundary_warning = (
        "Do not use this field to claim production readiness, customer "
        "validation, launch, private-core exposure, or blocker closure."
    )

    if input_kind == "metadata_field":
        if input_key.endswith("_date") or input_key in {"review_date", "target_review_date"}:
            return (
                "ISO date or review date reference",
                "Use a human-confirmed date such as YYYY-MM-DD, not an inferred date.",
                "If no date exists yet, leave blank and keep the row pending.",
                boundary_warning,
            )
        if "owner" in input_key or "reviewer" in input_key:
            return (
                "human owner or reviewer identifier",
                "Use the accountable human role, team, or reviewer reference.",
                "Do not let Codex assign, contact, or infer the owner.",
                boundary_warning,
            )
        return (
            "human-reviewed metadata value",
            "Use the exact value approved by the human reviewer.",
            "Leave blank if the value is not approved.",
            boundary_warning,
        )

    if input_kind == "evidence_review_key":
        return (
            "human evidence review outcome",
            "Use a concise human-reviewed outcome such as true, false, hold, or a short evidence reference.",
            "Only mark true when the referenced evidence exists and has been reviewed by a human.",
            boundary_warning,
        )

    if input_kind == "support_contact_bridge_field":
        if input_group == "first_owner_input":
            return (
                "first-owner coordination field",
                "Use human-approved owner, contact-reference, target-date, scope-acknowledgement, or approval-reference text.",
                "Do not assign an owner or contact anyone from this guidance layer.",
                boundary_warning,
            )
        if input_group == "support_contact_decision_metadata":
            return (
                "support-contact decision metadata",
                "Use human-reviewed support-contact decision metadata.",
                "Do not publish support contact details from this guidance layer.",
                boundary_warning,
            )
        if input_group == "support_contact_candidate_slot":
            return (
                "support-contact candidate slot",
                "Use a human-approved support-contact candidate reference.",
                "Do not publish or test the candidate contact from this guidance layer.",
                boundary_warning,
            )
        return (
            "support-contact bridge value",
            "Use human-reviewed support-contact bridge input.",
            "Leave blank if the support owner has not approved it.",
            boundary_warning,
        )

    return (
        "human-reviewed text value",
        "Use an explicitly reviewed human value.",
        "Leave blank if there is no reviewed value.",
        boundary_warning,
    )


def build_payload() -> dict[str, Any]:
    validation = json.loads(QUICK_FILL_VALIDATION_JSON.read_text(encoding="utf-8"))
    rows = load_csv(QUICK_FILL_CSV)
    guidance_rows: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    input_kind_counts: Counter[str] = Counter()
    input_group_counts: Counter[str] = Counter()
    boundary_violations: list[str] = []

    if validation.get("quick_fill_imported_to_workbook") is not False:
        boundary_violations.append("source_validation_already_imported_to_workbook")
    if validation.get("values_transferred") is not False:
        boundary_violations.append("source_validation_values_transferred")
    if len(rows) != EXPECTED_GUIDANCE_ROW_COUNT:
        boundary_violations.append("unexpected_guidance_row_count")

    for row in rows:
        blocker_counts[row["blocker_id"]] += 1
        input_kind_counts[row["input_kind"]] += 1
        input_group_counts[row["input_group"]] += 1
        value_shape, fill_instruction, leave_blank_condition, boundary_warning = guidance_for(row)
        guidance_rows.append(
            {
                "quick_fill_row_id": row["quick_fill_row_id"],
                "queue_item_id": row["queue_item_id"],
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": row["blocker_id"],
                "owner_review_lane": row["owner_review_lane"],
                "input_group": row["input_group"],
                "input_key": row["input_key"],
                "input_kind": row["input_kind"],
                "expected_value_shape": value_shape,
                "fill_instruction": fill_instruction,
                "leave_blank_condition": leave_blank_condition,
                "boundary_warning": boundary_warning,
                "actual_value_provided": False,
                "suggested_value": "",
                "codex_filled_value": False,
                "workbook_import_performed": False,
                "value_transferred": False,
                "template_written": False,
            }
        )

    status = (
        "stop_boundary_violation"
        if boundary_violations
        else "ready_for_human_quick_fill"
    )
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_guidance_v0_1": True,
        "guidance_type": "row_level_human_quick_fill_guidance",
        "guidance_scope": "human_fill_guidance_only_no_values_no_import",
        "status": status,
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_quick_fill_validation_json": rel(QUICK_FILL_VALIDATION_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_guidance.py",
        "guidance_row_count": len(guidance_rows),
        "quick_fill_row_count": len(rows),
        "unique_blocker_count": len(blocker_counts),
        "unique_input_group_count": len(input_group_counts),
        "unique_input_kind_count": len(input_kind_counts),
        "suggested_values_count": 0,
        "actual_values_provided_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "ready_for_human_fill": not boundary_violations,
        "ready_for_workbook_import": False,
        "quick_fill_values_entered_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_guidance": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blocker_guidance_counts": dict(sorted(blocker_counts.items())),
        "input_group_guidance_counts": dict(sorted(input_group_counts.items())),
        "input_kind_guidance_counts": dict(sorted(input_kind_counts.items())),
        "guidance_rows": guidance_rows,
        "next_human_action": (
            "Use this guidance while filling human_value_to_enter in the "
            "quick-fill CSV. Then rerun the quick-fill validator."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
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
        "boundary_warning",
        "actual_value_provided",
        "suggested_value",
        "codex_filled_value",
        "workbook_import_performed",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["guidance_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_guidance_v0_1: true",
        f"status: {payload['status']}",
        f"guidance_scope: {payload['guidance_scope']}",
        f"guidance_row_count: {payload['guidance_row_count']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"unique_blocker_count: {payload['unique_blocker_count']}",
        f"unique_input_group_count: {payload['unique_input_group_count']}",
        f"unique_input_kind_count: {payload['unique_input_kind_count']}",
        f"suggested_values_count: {payload['suggested_values_count']}",
        f"actual_values_provided_count: {payload['actual_values_provided_count']}",
        f"ready_for_human_fill: {str(payload['ready_for_human_fill']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"quick_fill_values_entered_by_codex: {str(payload['quick_fill_values_entered_by_codex']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        f"workbook_written: {str(payload['workbook_written']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_guidance: {payload['blockers_closed_by_guidance']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Guidance",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This file gives row-level guidance for filling `human_value_to_enter` in",
        "the quick-fill CSV. It does not provide actual values.",
        "",
        "## Guidance Counts",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in payload["blocker_guidance_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Human Procedure",
            "",
            "1. Open the quick-fill CSV.",
            "2. Use this guidance to understand the expected value shape.",
            "3. Fill only `human_value_to_enter` and optional `notes_for_human`.",
            "4. Leave rows blank when no human-reviewed value exists.",
            "5. Rerun the quick-fill validator before any import request.",
            "",
            "## Boundary",
            "",
            "No values were suggested or entered by Codex. No workbook import was",
            "performed. No workbook file was written. No values were transferred into",
            "templates. No validators were run on real input. No evidence was collected",
            "and no blocker was closed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Guidance Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This guidance is a local human-fill aid only. It does not provide actual",
        "values, import values into the workbook, write workbook files, transfer",
        "values, collect evidence, execute builders, contact customers or vendors,",
        "close blockers, launch product, or claim production readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Guidance v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the local row-level guidance layer for the current",
        "commercial sprint quick-fill packet. It makes human input easier to fill",
        "without changing SAEE product behavior.",
        "",
        "## Boundary",
        "",
        "The guidance does not fill values, suggest actual values, import values,",
        "write the workbook, transfer values, write human-filled templates, run",
        "validators on real input, collect evidence, execute builders, contact",
        "customers or vendors, close blockers, launch product, or claim production",
        "readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Guidance Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_guidance_v0_1: true",
        "answer: recommend",
        "recommend_for_human_fill_guidance: true",
        "recommend_for_human_fill_coordination: true",
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
        "This guidance is recommendable as a human-fill aid because it clarifies",
        "expected value shapes without entering values or authorizing import,",
        "execution, evidence collection, or blocker closure.",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_GUIDANCE: PASS "
        f"status={payload['status']} "
        f"guidance_row_count={payload['guidance_row_count']} "
        f"suggested_values_count={payload['suggested_values_count']} "
        f"ready_for_human_fill={str(payload['ready_for_human_fill']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
