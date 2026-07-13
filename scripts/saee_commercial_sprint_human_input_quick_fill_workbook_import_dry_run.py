#!/usr/bin/env python3
"""Dry-run resolve quick-fill rows against the commercial sprint workbook.

This dry run checks whether quick-fill rows can be mapped into workbook rows.
It does not import values into the workbook, transfer values into templates,
write human-filled templates, run validators on real input, collect evidence,
execute builders, contact anyone, close blockers, launch product, or claim
production readiness.
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
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"

OUT_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.local.json"
)
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.csv"
OUT_BOUNDARY = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN_RECOMMENDATION_GATE.md"
)

EXPECTED_IMPORT_ROW_COUNT = 64
EXPECTED_WORKBOOK_ROW_COUNT = 65
EXPECTED_TARGET_COLUMN = "human_value_placeholder"

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


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    validation = json.loads(QUICK_FILL_VALIDATION_JSON.read_text(encoding="utf-8"))
    quick_rows = load_csv(QUICK_FILL_CSV)
    workbook_rows = load_csv(WORKBOOK_CSV)
    workbook_by_id = {row["workbook_row_id"]: row for row in workbook_rows}

    boundary_violations: list[str] = []
    unresolved: list[dict[str, str]] = []
    dry_run_rows: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    resolved_count = 0
    value_present_count = 0
    would_import_count = 0

    if validation.get("quick_fill_imported_to_workbook") is not False:
        boundary_violations.append("source_validation_already_imported_to_workbook")
    if validation.get("values_transferred") is not False:
        boundary_violations.append("source_validation_values_transferred")
    if len(quick_rows) != EXPECTED_IMPORT_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")
    if len(workbook_rows) != EXPECTED_WORKBOOK_ROW_COUNT:
        boundary_violations.append("unexpected_workbook_row_count")

    for quick_row in quick_rows:
        workbook_row_id = quick_row.get("workbook_row_id", "")
        workbook_row = workbook_by_id.get(workbook_row_id)
        blocker_counts[quick_row.get("blocker_id", "")] += 1
        value = quick_row.get("human_value_to_enter", "").strip()
        value_present = bool(value)
        if value_present:
            value_present_count += 1

        mapping_resolved = workbook_row is not None
        resolution_status = "resolved" if mapping_resolved else "missing_workbook_row"
        if not mapping_resolved:
            unresolved.append(
                {
                    "quick_fill_row_id": quick_row.get("quick_fill_row_id", ""),
                    "workbook_row_id": workbook_row_id,
                    "reason": resolution_status,
                }
            )
        else:
            resolved_count += 1
            for field in ["blocker_id", "owner_review_lane", "input_group", "input_key"]:
                if quick_row.get(field) != workbook_row.get(field):
                    mapping_resolved = False
                    resolution_status = f"mismatched_{field}"
                    unresolved.append(
                        {
                            "quick_fill_row_id": quick_row.get("quick_fill_row_id", ""),
                            "workbook_row_id": workbook_row_id,
                            "reason": resolution_status,
                        }
                    )
                    break

        target_column_ok = quick_row.get("target_workbook_column") == EXPECTED_TARGET_COLUMN
        target_csv_ok = quick_row.get("target_workbook_csv") == rel(WORKBOOK_CSV)
        import_flags_clear = not any(
            parse_bool(quick_row.get(flag, ""))
            for flag in ["value_imported_to_workbook", "value_transferred", "template_written"]
        )
        would_import = (
            mapping_resolved
            and target_column_ok
            and target_csv_ok
            and import_flags_clear
            and value_present
        )
        if would_import:
            would_import_count += 1
            dry_run_status = "would_import_after_separate_human_approval"
        elif not value_present:
            dry_run_status = "hold_missing_human_value"
        else:
            dry_run_status = "stop_mapping_or_boundary_issue"

        dry_run_rows.append(
            {
                "quick_fill_row_id": quick_row.get("quick_fill_row_id", ""),
                "queue_item_id": quick_row.get("queue_item_id", ""),
                "workbook_row_id": workbook_row_id,
                "blocker_id": quick_row.get("blocker_id", ""),
                "owner_review_lane": quick_row.get("owner_review_lane", ""),
                "input_group": quick_row.get("input_group", ""),
                "input_key": quick_row.get("input_key", ""),
                "target_workbook_csv": quick_row.get("target_workbook_csv", ""),
                "target_workbook_column": quick_row.get("target_workbook_column", ""),
                "mapping_resolved": mapping_resolved,
                "target_csv_ok": target_csv_ok,
                "target_column_ok": target_column_ok,
                "human_value_present": value_present,
                "would_import": would_import,
                "dry_run_status": dry_run_status,
                "workbook_import_performed": False,
                "value_imported_to_workbook": False,
                "value_transferred": False,
                "template_written": False,
            }
        )

    unresolved_count = len(dry_run_rows) - sum(1 for row in dry_run_rows if row["mapping_resolved"])
    missing_value_count = len(dry_run_rows) - value_present_count
    all_import_mappings_resolved = (
        unresolved_count == 0 and resolved_count == EXPECTED_IMPORT_ROW_COUNT
    )
    boundary_violation_count = len(boundary_violations)

    if boundary_violation_count or unresolved_count:
        status = "stop_unresolved_import_mapping"
    elif would_import_count == EXPECTED_IMPORT_ROW_COUNT:
        status = "ready_for_workbook_import_pending_human_approval"
    else:
        status = "hold_human_quick_fill_required"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_v0_1": True,
        "dry_run_type": "quick_fill_to_workbook_import_mapping_only",
        "dry_run_scope": "resolve_quick_fill_to_workbook_without_import",
        "status": status,
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_quick_fill_validation_json": rel(QUICK_FILL_VALIDATION_JSON),
        "target_workbook_csv": rel(WORKBOOK_CSV),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py",
        "quick_fill_row_count": len(quick_rows),
        "workbook_row_count": len(workbook_rows),
        "import_mapping_row_count": len(dry_run_rows),
        "resolved_import_mapping_row_count": sum(
            1 for row in dry_run_rows if row["mapping_resolved"]
        ),
        "unresolved_import_mapping_row_count": unresolved_count,
        "all_import_mappings_resolved": all_import_mappings_resolved,
        "value_present_row_count": value_present_count,
        "missing_value_row_count": missing_value_count,
        "would_import_row_count": would_import_count,
        "ready_for_workbook_import": would_import_count == EXPECTED_IMPORT_ROW_COUNT
        and all_import_mappings_resolved
        and boundary_violation_count == 0,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_import_dry_run": 0,
        "boundary_violation_count": boundary_violation_count,
        "boundary_violations": boundary_violations,
        "unresolved_import_mappings": unresolved,
        "blocker_import_counts": dict(sorted(blocker_counts.items())),
        "dry_run_rows": dry_run_rows,
        "next_human_action": (
            "Fill human_value_to_enter cells first. If the dry run later reports "
            "ready_for_workbook_import=true, create a separate human-approved "
            "workbook import request before any workbook write."
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
        "target_workbook_csv",
        "target_workbook_column",
        "mapping_resolved",
        "target_csv_ok",
        "target_column_ok",
        "human_value_present",
        "would_import",
        "dry_run_status",
        "workbook_import_performed",
        "value_imported_to_workbook",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["dry_run_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"import_mapping_row_count: {payload['import_mapping_row_count']}",
        f"resolved_import_mapping_row_count: {payload['resolved_import_mapping_row_count']}",
        f"unresolved_import_mapping_row_count: {payload['unresolved_import_mapping_row_count']}",
        f"all_import_mappings_resolved: {str(payload['all_import_mappings_resolved']).lower()}",
        f"value_present_row_count: {payload['value_present_row_count']}",
        f"missing_value_row_count: {payload['missing_value_row_count']}",
        f"would_import_row_count: {payload['would_import_row_count']}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        f"workbook_written: {str(payload['workbook_written']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_import_dry_run: {payload['blockers_closed_by_import_dry_run']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Quick-Fill Workbook Import Dry Run",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This dry run checks whether quick-fill rows can map safely into the",
        "commercial sprint workbook. It does not write the workbook.",
        "",
        "## Import Readiness",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Import mapping rows | {payload['import_mapping_row_count']} |",
        f"| Resolved mappings | {payload['resolved_import_mapping_row_count']} |",
        f"| Unresolved mappings | {payload['unresolved_import_mapping_row_count']} |",
        f"| Rows with human value | {payload['value_present_row_count']} |",
        f"| Missing values | {payload['missing_value_row_count']} |",
        f"| Rows that would import after approval | {payload['would_import_row_count']} |",
        "",
        "## Boundary",
        "",
        "No workbook import was performed. No workbook file was written. No values",
        "were transferred into templates. No human-filled templates were written.",
        "No validators were run on real input. No evidence was collected and no",
        "blocker was closed.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Quick-Fill Workbook Import Dry Run Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This dry run is a local import-readiness check only. It does not import",
        "values into the workbook, write workbook files, transfer values, collect",
        "evidence, execute builders, contact customers or vendors, close blockers,",
        "launch product, or claim production readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Quick-Fill Workbook Import Dry Run v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the local dry run that resolves quick-fill rows",
        "against commercial sprint workbook rows. It is a readiness surface for a",
        "future separately approved import step.",
        "",
        "## Boundary",
        "",
        "The dry run does not import values, write the workbook, transfer values,",
        "write human-filled templates, run validators on real input, collect",
        "evidence, execute builders, contact customers or vendors, close blockers,",
        "launch product, or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Quick-Fill Workbook Import Dry Run Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_workbook_import_dry_run_v0_1: true",
        "answer: recommend",
        "recommend_for_import_readiness_check: true",
        "recommend_for_human_fill_coordination: true",
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
        "This dry run is recommendable as a local readiness check because it",
        "validates quick-fill-to-workbook mappings without writing workbook values",
        "or authorizing downstream execution.",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORT_DRY_RUN: PASS "
        f"status={payload['status']} "
        f"resolved_import_mapping_row_count={payload['resolved_import_mapping_row_count']} "
        f"value_present_row_count={payload['value_present_row_count']} "
        f"would_import_row_count={payload['would_import_row_count']} "
        f"workbook_import_performed={str(payload['workbook_import_performed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
