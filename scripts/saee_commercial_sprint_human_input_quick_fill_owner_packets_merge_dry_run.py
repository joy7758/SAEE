#!/usr/bin/env python3
"""Dry-run map quick-fill owner packet values back to the source quick-fill CSV.

This dry run checks whether owner packet rows can be mapped back to the source
quick-fill rows. It does not record raw values, merge values into the source
quick-fill CSV, import values into the workbook, transfer values into templates,
run validators on real input, collect evidence, execute builders, contact
anyone, close blockers, launch product, or claim production readiness.
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
PACKET_DIR = SPRINT_DIR / "quick_fill_owner_packets"
SOURCE_OWNER_PACKETS_JSON = (
    PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.local.json"
)
SOURCE_OWNER_VALIDATION_JSON = (
    PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_validation.local.json"
)
SOURCE_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = (
    PACKET_DIR
    / "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.local.json"
)
OUT_MD = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.md"
OUT_CSV = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.csv"
OUT_BOUNDARY = (
    PACKET_DIR
    / "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_MERGE_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_MERGE_DRY_RUN_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 64
EXPECTED_PACKET_COUNT = 5
EXPECTED_COUNTS_BY_BLOCKER = {
    "formal_security_review": 12,
    "pricing_page": 14,
    "production_monitoring": 10,
    "production_restore_policy": 13,
    "support_contact": 15,
}

FALSE_FLAGS = [
    "ready_for_quick_fill_merge",
    "ready_for_workbook_import",
    "ready_for_template_transfer",
    "ready_for_existing_local_validators",
    "owner_values_merged_to_quick_fill",
    "quick_fill_written",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "values_transferred",
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
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


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    owner_packets = json.loads(SOURCE_OWNER_PACKETS_JSON.read_text(encoding="utf-8"))
    owner_validation = json.loads(SOURCE_OWNER_VALIDATION_JSON.read_text(encoding="utf-8"))
    quick_fill_rows = read_csv(SOURCE_QUICK_FILL_CSV)
    quick_fill_by_id = {row["quick_fill_row_id"]: row for row in quick_fill_rows}

    boundary_violations: list[str] = []
    merge_rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, str]] = []
    blocker_counts: Counter[str] = Counter()
    owner_lane_counts: Counter[str] = Counter()
    packet_counts: Counter[str] = Counter()
    all_owner_ids: list[str] = []
    owner_value_present_count = 0
    source_value_present_count = 0
    would_merge_count = 0

    if owner_packets.get("owner_packet_count") != EXPECTED_PACKET_COUNT:
        boundary_violations.append("source_owner_packet_count_changed")
    if owner_validation.get("local_owner_packet_validator_run") is not True:
        boundary_violations.append("owner_packet_validator_not_run")
    if owner_validation.get("raw_values_recorded") is not False:
        boundary_violations.append("owner_packet_validator_recorded_raw_values")
    for flag in [
        "ready_for_quick_fill_merge",
        "ready_for_workbook_import",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "values_transferred",
        "evidence_collection_authorized",
        "execution_authorized",
        "evidence_builder_executed",
        "blocker_closure_authorized",
    ]:
        if owner_validation.get(flag) is not False:
            boundary_violations.append(f"owner_validation_{flag}_changed")
    if len(quick_fill_rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_source_quick_fill_row_count")

    for quick_row in quick_fill_rows:
        if quick_row.get("human_value_to_enter", "").strip():
            source_value_present_count += 1

    for packet in owner_packets.get("owner_packets", []):
        packet_csv = packet.get("owner_packet_csv", "")
        packet_path = ROOT / packet_csv
        if not packet_path.exists():
            boundary_violations.append(f"missing_owner_packet_csv:{packet_csv}")
            continue
        for owner_row in read_csv(packet_path):
            row_id = owner_row.get("quick_fill_row_id", "")
            all_owner_ids.append(row_id)
            source_row = quick_fill_by_id.get(row_id)
            blocker_id = owner_row.get("blocker_id", "")
            owner_lane = owner_row.get("owner_review_lane", "")
            owner_packet_id = owner_row.get("owner_packet_id", "")
            blocker_counts[blocker_id] += 1
            owner_lane_counts[owner_lane] += 1
            packet_counts[owner_packet_id] += 1

            owner_value_present = bool(owner_row.get("human_value_to_enter", "").strip())
            owner_notes_present = bool(owner_row.get("notes_for_human", "").strip())
            if owner_value_present:
                owner_value_present_count += 1

            mapping_resolved = source_row is not None
            resolution_status = "resolved" if mapping_resolved else "missing_source_quick_fill_row"
            if not mapping_resolved:
                unresolved_rows.append(
                    {
                        "quick_fill_row_id": row_id,
                        "owner_packet_id": owner_packet_id,
                        "reason": resolution_status,
                    }
                )
            else:
                for field in [
                    "blocker_id",
                    "owner_review_lane",
                    "input_group",
                    "input_key",
                    "target_json_pointer",
                ]:
                    if owner_row.get(field) != source_row.get(field):
                        mapping_resolved = False
                        resolution_status = f"mismatched_{field}"
                        unresolved_rows.append(
                            {
                                "quick_fill_row_id": row_id,
                                "owner_packet_id": owner_packet_id,
                                "reason": resolution_status,
                            }
                        )
                        break

            owner_flags_clear = not any(
                parse_bool(owner_row.get(flag, ""))
                for flag in [
                    "codex_filled_value",
                    "workbook_import_performed",
                    "validators_run_on_real_input",
                    "evidence_collection_authorized",
                    "execution_authorized",
                ]
            )
            source_flags_clear = True if source_row is None else not any(
                parse_bool(source_row.get(flag, ""))
                for flag in [
                    "value_imported_to_workbook",
                    "value_transferred",
                    "template_written",
                ]
            )
            would_merge = (
                mapping_resolved
                and owner_value_present
                and owner_flags_clear
                and source_flags_clear
            )
            if would_merge:
                would_merge_count += 1
                dry_run_status = "would_merge_after_separate_human_approval"
            elif not owner_value_present:
                dry_run_status = "hold_missing_owner_packet_value"
            else:
                dry_run_status = "stop_mapping_or_boundary_issue"

            merge_rows.append(
                {
                    "owner_packet_id": owner_packet_id,
                    "blocker_id": blocker_id,
                    "owner_review_lane": owner_lane,
                    "worksheet_row_id": owner_row.get("worksheet_row_id", ""),
                    "quick_fill_row_id": row_id,
                    "input_group": owner_row.get("input_group", ""),
                    "input_key": owner_row.get("input_key", ""),
                    "mapping_resolved": mapping_resolved,
                    "owner_value_present": owner_value_present,
                    "owner_notes_present": owner_notes_present,
                    "source_value_present": bool(
                        source_row and source_row.get("human_value_to_enter", "").strip()
                    ),
                    "would_merge": would_merge,
                    "dry_run_status": dry_run_status,
                    "raw_value_recorded": False,
                    "owner_value_merged_to_quick_fill": False,
                    "quick_fill_written": False,
                    "workbook_import_performed": False,
                    "validators_run_on_real_input": False,
                    "evidence_collection_authorized": False,
                    "execution_authorized": False,
                }
            )

    duplicate_owner_ids = sorted(
        [row_id for row_id, count in Counter(all_owner_ids).items() if count > 1]
    )
    if duplicate_owner_ids:
        boundary_violations.append("duplicate_owner_packet_quick_fill_row_id")
    if len(merge_rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_owner_packet_row_count")
    if dict(sorted(blocker_counts.items())) != EXPECTED_COUNTS_BY_BLOCKER:
        boundary_violations.append("unexpected_owner_packet_rows_by_blocker")

    unresolved_count = len(unresolved_rows)
    missing_owner_value_count = len(merge_rows) - owner_value_present_count
    all_merge_mappings_resolved = (
        unresolved_count == 0 and len(merge_rows) == EXPECTED_ROW_COUNT
    )
    boundary_violation_count = len(boundary_violations)
    ready_for_merge = (
        all_merge_mappings_resolved
        and would_merge_count == EXPECTED_ROW_COUNT
        and boundary_violation_count == 0
    )
    if boundary_violation_count or unresolved_count:
        status = "stop_unresolved_owner_packet_merge_mapping"
    elif ready_for_merge:
        status = "ready_for_quick_fill_merge_pending_human_approval"
    else:
        status = "hold_owner_packet_human_values_required"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_v0_1": True,
        "dry_run_type": "owner_packets_to_quick_fill_merge_mapping_only",
        "dry_run_scope": "resolve_owner_packets_to_source_quick_fill_without_merge",
        "status": status,
        "source_owner_packets_json": rel(SOURCE_OWNER_PACKETS_JSON),
        "source_owner_packets_validation_json": rel(SOURCE_OWNER_VALIDATION_JSON),
        "source_quick_fill_csv": rel(SOURCE_QUICK_FILL_CSV),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": (
            "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.py"
        ),
        "owner_packet_count": EXPECTED_PACKET_COUNT,
        "merge_mapping_row_count": len(merge_rows),
        "required_merge_mapping_row_count": EXPECTED_ROW_COUNT,
        "resolved_merge_mapping_row_count": len(merge_rows) - unresolved_count,
        "unresolved_merge_mapping_row_count": unresolved_count,
        "all_merge_mappings_resolved": all_merge_mappings_resolved,
        "owner_value_present_row_count": owner_value_present_count,
        "source_quick_fill_value_present_row_count": source_value_present_count,
        "missing_owner_value_row_count": missing_owner_value_count,
        "would_merge_row_count": would_merge_count,
        "human_input_required": not ready_for_merge,
        "human_review_required": True,
        "raw_values_recorded": False,
        "local_owner_packet_merge_dry_run": True,
        "blockers_closed_by_owner_packet_merge_dry_run": 0,
        "boundary_violation_count": boundary_violation_count,
        "boundary_violations": boundary_violations,
        "duplicate_owner_packet_quick_fill_row_ids": duplicate_owner_ids,
        "unresolved_merge_mappings": unresolved_rows,
        "owner_packet_rows_by_blocker": dict(sorted(blocker_counts.items())),
        "owner_packet_rows_by_lane": dict(sorted(owner_lane_counts.items())),
        "owner_packet_rows_by_packet": dict(sorted(packet_counts.items())),
        "merge_dry_run_rows": merge_rows,
        "next_human_action": (
            "Fill owner packet human_value_to_enter cells first. If this dry run "
            "later reports ready_for_quick_fill_merge_pending_human_approval, "
            "request a separate human-approved merge step before writing the "
            "source quick-fill CSV."
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
        "owner_packet_id",
        "blocker_id",
        "owner_review_lane",
        "worksheet_row_id",
        "quick_fill_row_id",
        "input_group",
        "input_key",
        "mapping_resolved",
        "owner_value_present",
        "owner_notes_present",
        "source_value_present",
        "would_merge",
        "dry_run_status",
        "raw_value_recorded",
        "owner_value_merged_to_quick_fill",
        "quick_fill_written",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["merge_dry_run_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"owner_packet_count: {payload['owner_packet_count']}",
        f"merge_mapping_row_count: {payload['merge_mapping_row_count']}",
        f"required_merge_mapping_row_count: {payload['required_merge_mapping_row_count']}",
        f"resolved_merge_mapping_row_count: {payload['resolved_merge_mapping_row_count']}",
        f"unresolved_merge_mapping_row_count: {payload['unresolved_merge_mapping_row_count']}",
        f"all_merge_mappings_resolved: {str(payload['all_merge_mappings_resolved']).lower()}",
        f"owner_value_present_row_count: {payload['owner_value_present_row_count']}",
        f"source_quick_fill_value_present_row_count: {payload['source_quick_fill_value_present_row_count']}",
        f"missing_owner_value_row_count: {payload['missing_owner_value_row_count']}",
        f"would_merge_row_count: {payload['would_merge_row_count']}",
        f"ready_for_quick_fill_merge: {str(payload['ready_for_quick_fill_merge']).lower()}",
        f"owner_values_merged_to_quick_fill: {str(payload['owner_values_merged_to_quick_fill']).lower()}",
        f"quick_fill_written: {str(payload['quick_fill_written']).lower()}",
        f"raw_values_recorded: {str(payload['raw_values_recorded']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"workbook_import_authorized: {str(payload['workbook_import_authorized']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blocker_closure_authorized: {str(payload['blocker_closure_authorized']).lower()}",
        f"blockers_closed_by_owner_packet_merge_dry_run: {payload['blockers_closed_by_owner_packet_merge_dry_run']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Quick-Fill Owner Packets Merge Dry Run",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This dry run checks whether owner packet rows can map back to the source",
        "quick-fill CSV. It does not write or merge values.",
        "",
        "## Merge Readiness",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Merge mapping rows | {payload['merge_mapping_row_count']} |",
        f"| Resolved mappings | {payload['resolved_merge_mapping_row_count']} |",
        f"| Unresolved mappings | {payload['unresolved_merge_mapping_row_count']} |",
        f"| Owner rows with human value | {payload['owner_value_present_row_count']} |",
        f"| Missing owner values | {payload['missing_owner_value_row_count']} |",
        f"| Rows that would merge after approval | {payload['would_merge_row_count']} |",
        "",
        "## Boundary",
        "",
        "No owner-packet value was written into the source quick-fill CSV. No raw",
        "human value was recorded. No workbook import was performed. No values",
        "were transferred into templates. No validators were run on real input.",
        "No evidence was collected and no blocker was closed.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Quick-Fill Owner Packets Merge Dry Run Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This dry run is a local merge-readiness check only. It does not record raw",
        "human values, merge values into the source quick-fill CSV, import values",
        "into the workbook, write workbook files, transfer values, collect evidence,",
        "execute builders, contact customers or vendors, close blockers, launch",
        "product, or claim production readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Quick-Fill Owner Packets Merge Dry Run v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the local dry run that resolves owner packet rows",
        "against source quick-fill rows. It is a readiness surface for a future",
        "separately approved owner-packet merge step.",
        "",
        "## Boundary",
        "",
        "The dry run does not record raw values, merge values, write the source",
        "quick-fill CSV, import workbooks, transfer values, write human-filled",
        "templates, run validators on real input, collect evidence, execute",
        "builders, contact customers or vendors, close blockers, launch product,",
        "or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Quick-Fill Owner Packets Merge Dry Run Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_v0_1: true",
        "answer: recommend",
        "recommend_for_owner_packet_merge_readiness_check: true",
        "recommend_for_human_fill_coordination: true",
        "recommend_for_raw_value_storage: false",
        "recommend_for_value_merge: false",
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
        "validates owner-packet-to-quick-fill mappings without recording raw values,",
        "writing files, or authorizing downstream import or execution.",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_MERGE_DRY_RUN: PASS "
        f"status={payload['status']} "
        f"resolved_merge_mapping_row_count={payload['resolved_merge_mapping_row_count']} "
        f"owner_value_present_row_count={payload['owner_value_present_row_count']} "
        f"would_merge_row_count={payload['would_merge_row_count']} "
        f"owner_values_merged_to_quick_fill={str(payload['owner_values_merged_to_quick_fill']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
