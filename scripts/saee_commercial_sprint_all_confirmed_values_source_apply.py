#!/usr/bin/env python3
"""Apply all human-confirmed quick-fill values to the official source CSV.

This is a source-input step only. It copies values from the complete
human-confirmed preview into the official quick-fill packet after explicit
human confirmation. It does not import the workbook, transfer template values,
run validators on real input, collect evidence, execute builders, close
blockers, contact anyone, launch product, or claim production readiness.
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
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
SOURCE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
SOURCE_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.md"
SOURCE_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_boundary_audit.md"
SOURCE_TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_V0_1.md"
)
SOURCE_GATE = (
    ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_RECOMMENDATION_GATE.md"
)
PREVIEW_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_quick_fill_preview.local.csv"

OUT_JSON = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_all_confirmed_values_source_apply_boundary_audit.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY_V0_1.md"
)
GATE = (
    ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 64
FALSE_FLAGS = [
    "quick_fill_imported_to_workbook",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
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


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_all_confirmed_values_source_apply_v0_1: true",
        f"status: {payload['status']}",
        f"apply_scope: {payload['apply_scope']}",
        f"source_quick_fill_row_count: {payload['source_quick_fill_row_count']}",
        f"preview_value_row_count: {payload['preview_value_row_count']}",
        f"applied_value_row_count: {payload['applied_value_row_count']}",
        f"missing_preview_value_row_count: {payload['missing_preview_value_row_count']}",
        f"source_quick_fill_packet_modified: {str(payload['source_quick_fill_packet_modified']).lower()}",
        f"ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        f"blockers_closed_by_source_apply: {payload['blockers_closed_by_source_apply']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]


def source_packet_payload(applied_rows: list[dict[str, str]], blocker_counts: Counter[str]) -> dict[str, Any]:
    json_rows: list[dict[str, Any]] = []
    for row in applied_rows:
        json_row: dict[str, Any] = dict(row)
        json_row["value_imported_to_workbook"] = False
        json_row["value_transferred"] = False
        json_row["template_written"] = False
        json_rows.append(json_row)
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_packet_v0_1": True,
        "packet_type": "local_human_quick_fill_packet",
        "packet_scope": "human_confirmed_quick_fill_source_only_no_import_no_transfer",
        "status": "human_confirmed_values_present_pending_safety_preflight",
        "source_completion_queue_json": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.local.json",
        "source_completion_queue_csv": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.csv",
        "source_confirmed_preview_csv": rel(PREVIEW_CSV),
        "target_workbook_csv": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_workbook.csv",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_all_confirmed_values_source_apply.py",
        "selected_blocker_count": len(blocker_counts),
        "selected_blocker_ids": sorted(blocker_counts),
        "source_queue_item_count": len(applied_rows),
        "quick_fill_row_count": len(applied_rows),
        "blank_value_row_count": 0,
        "confirmed_value_row_count": len(applied_rows),
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_safety_preflight": True,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_quick_fill_packet": 0,
        "boundary_violation_count": 0,
        "boundary_violations": [],
        "blocker_fill_counts": dict(sorted(blocker_counts.items())),
        "quick_fill_rows": json_rows,
        "next_human_action": (
            "Run the quick-fill safety preflight, validator, import dry run, and "
            "workbook import approval request before any separate workbook import."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_source_docs(source_payload: dict[str, Any]) -> None:
    lines = [
        "commercial_sprint_human_input_quick_fill_packet_v0_1: true",
        f"status: {source_payload['status']}",
        f"packet_scope: {source_payload['packet_scope']}",
        f"source_queue_item_count: {source_payload['source_queue_item_count']}",
        f"quick_fill_row_count: {source_payload['quick_fill_row_count']}",
        f"blank_value_row_count: {source_payload['blank_value_row_count']}",
        f"confirmed_value_row_count: {source_payload['confirmed_value_row_count']}",
        "quick_fill_values_entered_by_codex: false",
        "quick_fill_imported_to_workbook: false",
        "human_input_filled_by_codex: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "ready_for_safety_preflight: true",
        "ready_for_workbook_import: false",
        "ready_for_template_transfer: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_quick_fill_packet: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    body = "\n".join(lines)
    SOURCE_JSON.write_text(json.dumps(source_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SOURCE_MD.write_text(
        "# Commercial Sprint Human Input Quick-Fill Packet\n\n"
        f"{body}\n\n"
        "## Purpose\n\n"
        "This packet now contains human-confirmed quick-fill source values copied "
        "from the complete local confirmed-value preview. It remains an input "
        "source only.\n\n"
        "## Boundary\n\n"
        "No workbook import was performed. No values were transferred into "
        "templates. No validators were run on real input. No evidence was "
        "collected and no blocker was closed.\n",
        encoding="utf-8",
    )
    SOURCE_BOUNDARY.write_text(
        "# Commercial Sprint Human Input Quick-Fill Packet Boundary Audit\n\n"
        f"{body}\n\n"
        "The source quick-fill packet contains human-confirmed values only. It "
        "does not authorize workbook import, value transfer, evidence collection, "
        "execution, blocker closure, customer/vendor contact, launch, "
        "customer-validation claims, or production-readiness claims.\n",
        encoding="utf-8",
    )
    SOURCE_TOP_DOC.write_text(
        "# Commercial Sprint Human Input Quick-Fill Packet v0.1\n\n"
        f"{body}\n\n"
        "## Role\n\n"
        "This document records the compact quick-fill source layer for the current "
        "commercial sprint human inputs after human-confirmed values were copied "
        "from the complete local preview.\n\n"
        "## Boundary\n\n"
        "The packet does not import values, transfer values, write human-filled "
        "templates, run validators on real input, collect evidence, execute "
        "builders, contact customers or vendors, close blockers, launch product, "
        "or claim production readiness.\n",
        encoding="utf-8",
    )
    SOURCE_GATE.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Packet Recommendation Gate\n\n"
        "commercial_sprint_human_input_quick_fill_packet_v0_1: true\n"
        "answer: recommend\n"
        "recommend_for_human_fill_coordination: true\n"
        "recommend_for_value_import: false\n"
        "recommend_for_value_transfer: false\n"
        "recommend_for_real_evidence: false\n"
        "recommend_for_evidence_collection: false\n"
        "recommend_for_automatic_execution: false\n"
        "recommend_for_blocker_closure: false\n"
        "recommend_for_product_launch: false\n"
        "recommend_for_production_readiness_claim: false\n\n"
        "## Reason\n\n"
        "The packet is recommendable as a coordination surface because it records "
        "human-confirmed values while preserving all execution and evidence "
        "boundaries.\n\n"
        "## Status\n\n"
        f"{body}\n",
        encoding="utf-8",
    )


def build_and_apply() -> dict[str, Any]:
    source_fields, source_rows = read_csv(SOURCE_CSV)
    _, preview_rows = read_csv(PREVIEW_CSV)
    boundary_violations: list[str] = []
    if len(source_rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_source_row_count")
    if len(preview_rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_preview_row_count")
    source_by_id = {row["quick_fill_row_id"]: row for row in source_rows}
    preview_by_id = {row["quick_fill_row_id"]: row for row in preview_rows}
    if set(source_by_id) != set(preview_by_id):
        boundary_violations.append("source_preview_id_mismatch")

    applied_rows: list[dict[str, str]] = []
    report_rows: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    missing_preview_value = 0
    for row in source_rows:
        row_id = row["quick_fill_row_id"]
        preview = preview_by_id.get(row_id, {})
        value = preview.get("human_value_to_enter", "").strip()
        if not value:
            missing_preview_value += 1
            boundary_violations.append(f"{row_id}:missing_preview_value")
        applied = dict(row)
        applied["human_value_to_enter"] = value
        applied["notes_for_human"] = (
            "human-confirmed value copied from complete local preview; "
            "pending safety preflight and separate workbook import approval"
        )
        applied["quick_fill_status"] = "human_confirmed_value_present_pending_safety_preflight"
        applied["value_imported_to_workbook"] = "False"
        applied["value_transferred"] = "False"
        applied["template_written"] = "False"
        blocker_counts[applied.get("blocker_id", "")] += 1
        applied_rows.append(applied)
        report_rows.append(
            {
                "quick_fill_row_id": row_id,
                "blocker_id": applied.get("blocker_id", ""),
                "value_applied": bool(value),
                "source_status": applied["quick_fill_status"],
                "value_imported_to_workbook": False,
                "value_transferred": False,
                "template_written": False,
            }
        )

    if boundary_violations:
        status = "stop_source_apply_boundary_violation"
        source_modified = False
    else:
        write_csv(SOURCE_CSV, source_fields, applied_rows)
        source_modified = True
        status = "source_values_applied_pending_safety_preflight"
        write_source_docs(source_packet_payload(applied_rows, blocker_counts))

    payload: dict[str, Any] = {
        "commercial_sprint_all_confirmed_values_source_apply_v0_1": True,
        "status": status,
        "apply_scope": "copy_human_confirmed_preview_values_to_official_quick_fill_source_only",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_all_confirmed_values_source_apply.py",
        "source_quick_fill_csv": rel(SOURCE_CSV),
        "preview_quick_fill_csv": rel(PREVIEW_CSV),
        "source_quick_fill_row_count": len(source_rows),
        "preview_value_row_count": sum(bool(row.get("human_value_to_enter", "").strip()) for row in preview_rows),
        "applied_value_row_count": len(applied_rows) if not boundary_violations else 0,
        "missing_preview_value_row_count": missing_preview_value,
        "source_quick_fill_packet_modified": source_modified,
        "ready_for_safety_preflight": source_modified,
        "ready_for_workbook_import": False,
        "blockers_closed_by_source_apply": 0,
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "apply_rows": report_rows,
        "next_human_action": (
            "Run local safety preflight, quick-fill validation, import dry run, "
            "and workbook import approval packet. Do not run workbook import "
            "without a separate explicit execution request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(
        OUT_CSV,
        [
            "quick_fill_row_id",
            "blocker_id",
            "value_applied",
            "source_status",
            "value_imported_to_workbook",
            "value_transferred",
            "template_written",
        ],
        payload["apply_rows"],
    )
    body = "\n".join(status_lines(payload))
    for path, title in [
        (OUT_MD, "Commercial Sprint All Confirmed Values Source Apply"),
        (OUT_BOUNDARY, "Commercial Sprint All Confirmed Values Source Apply Boundary Audit"),
        (TOP_DOC, "Commercial Sprint All Confirmed Values Source Apply v0.1"),
    ]:
        path.write_text(
            f"# {title}\n\n"
            f"{body}\n\n"
            "This local step copies only human-confirmed quick-fill values into "
            "the official quick-fill source. It performs no workbook import, no "
            "template transfer, no validator execution on real input, no evidence "
            "collection, and no blocker closure.\n",
            encoding="utf-8",
        )
    GATE.write_text(
        "# SAEE Commercial Sprint All Confirmed Values Source Apply Recommendation Gate\n\n"
        "commercial_sprint_all_confirmed_values_source_apply_v0_1: true\n"
        "answer: conditional\n"
        "recommend_for_human_confirmed_source_apply: true\n"
        "recommend_for_workbook_import: false\n"
        "recommend_for_template_transfer: false\n"
        "recommend_for_validator_execution: false\n"
        "recommend_for_evidence_collection: false\n"
        "recommend_for_blocker_closure: false\n"
        "recommend_for_product_launch: false\n"
        "recommend_for_production_readiness_claim: false\n\n"
        "## Status\n\n"
        f"{body}\n",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_and_apply()
    write_artifacts(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SOURCE_APPLY: PASS "
        f"status={payload['status']} "
        f"applied_value_row_count={payload['applied_value_row_count']} "
        f"source_quick_fill_packet_modified={str(payload['source_quick_fill_packet_modified']).lower()} "
        "workbook_import_performed=false production_ready=false"
    )
    return 0 if not payload["boundary_violations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
