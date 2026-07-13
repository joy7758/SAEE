#!/usr/bin/env python3
"""Build a compact human quick-fill packet for commercial sprint inputs.

The packet is a smaller human-facing fill sheet derived from the missing-input
queue. It keeps only the fields a human needs to provide values. It does not
fill values, import values back into the workbook, transfer values into
blocker-specific templates, write human-filled templates, run validators on real
input, collect evidence, execute builders, contact anyone, close blockers,
launch product, or claim production readiness.
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
QUEUE_JSON = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.local.json"
QUEUE_CSV = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.csv"
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
CONFIRMED_PREVIEW_CSV = (
    SPRINT_DIR / "commercial_sprint_all_confirmed_values_quick_fill_preview.local.csv"
)

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_QUEUE_ITEM_COUNT = 64
EXPECTED_SELECTED_BLOCKERS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]

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
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "human_input_filled_by_codex",
    "quick_fill_values_entered_by_codex",
    "quick_fill_imported_to_workbook",
    "validators_run_on_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_queue() -> dict[str, Any]:
    return json.loads(QUEUE_JSON.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def bool_from_cell(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def build_payload() -> dict[str, Any]:
    queue = load_queue()
    items = queue.get("queue_items", [])
    if queue.get("status") != "hold_human_input_required":
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET: "
            "FAIL source queue must be hold_human_input_required"
        )
    if len(items) != EXPECTED_QUEUE_ITEM_COUNT:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET: "
            f"FAIL expected {EXPECTED_QUEUE_ITEM_COUNT} queue items, found {len(items)}"
        )
    if queue.get("values_transferred") is not False:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET: "
            "FAIL source queue must not transfer values"
        )

    confirmed_rows_available = False
    fill_rows: list[dict[str, Any]] = []
    if CONFIRMED_PREVIEW_CSV.exists():
        preview_rows = read_csv_rows(CONFIRMED_PREVIEW_CSV)
        confirmed_rows_available = (
            len(preview_rows) == EXPECTED_QUEUE_ITEM_COUNT
            and all(row.get("human_value_to_enter", "").strip() for row in preview_rows)
        )
        if confirmed_rows_available:
            for row in preview_rows:
                fill_rows.append(
                    {
                        "quick_fill_row_id": row["quick_fill_row_id"],
                        "queue_item_id": row["queue_item_id"],
                        "workbook_row_id": row["workbook_row_id"],
                        "blocker_id": row["blocker_id"],
                        "owner_review_lane": row["owner_review_lane"],
                        "input_group": row["input_group"],
                        "input_key": row["input_key"],
                        "input_kind": row["input_kind"],
                        "human_fill_prompt": row["human_fill_prompt"],
                        "human_value_to_enter": row["human_value_to_enter"],
                        "notes_for_human": row.get("notes_for_human", ""),
                        "target_workbook_csv": row.get("target_workbook_csv") or rel(WORKBOOK_CSV),
                        "target_workbook_column": row.get("target_workbook_column")
                        or "human_value_placeholder",
                        "target_json_pointer": row["target_json_pointer"],
                        "human_filled_input_target": "",
                        "quick_fill_status": "human_confirmed_pending_safety_preflight",
                        "value_imported_to_workbook": bool_from_cell(
                            row.get("value_imported_to_workbook")
                        ),
                        "value_transferred": bool_from_cell(row.get("value_transferred")),
                        "template_written": bool_from_cell(row.get("template_written")),
                    }
                )

    if not confirmed_rows_available:
        for item in items:
            fill_rows.append(
                {
                    "quick_fill_row_id": item["queue_item_id"].replace("HIQ", "QF"),
                    "queue_item_id": item["queue_item_id"],
                    "workbook_row_id": item["workbook_row_id"],
                    "blocker_id": item["blocker_id"],
                    "owner_review_lane": item["owner_review_lane"],
                    "input_group": item["input_group"],
                    "input_key": item["input_key"],
                    "input_kind": item["input_kind"],
                    "human_fill_prompt": item["source_prompt"],
                    "human_value_to_enter": "",
                    "notes_for_human": "",
                    "target_workbook_csv": rel(WORKBOOK_CSV),
                    "target_workbook_column": "human_value_placeholder",
                    "target_json_pointer": item["target_json_pointer"],
                    "human_filled_input_target": item["human_filled_input_target"],
                    "quick_fill_status": "blank_pending_human_input",
                    "value_imported_to_workbook": False,
                    "value_transferred": False,
                    "template_written": False,
                }
            )

    blocker_counts: Counter[str] = Counter(row["blocker_id"] for row in fill_rows)
    lane_counts: Counter[str] = Counter(row["owner_review_lane"] for row in fill_rows)
    blank_value_count = sum(
        1 for row in fill_rows if not str(row.get("human_value_to_enter", "")).strip()
    )
    confirmed_value_count = len(fill_rows) - blank_value_count

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_packet_v0_1": True,
        "packet_type": "local_human_quick_fill_packet",
        "packet_scope": (
            "human_confirmed_quick_fill_source_only_no_import_no_transfer"
            if confirmed_rows_available
            else "blank_quick_fill_sheet_only_no_import_no_transfer"
        ),
        "status": (
            "human_confirmed_values_present_pending_safety_preflight"
            if confirmed_rows_available
            else "hold_human_quick_fill_required"
        ),
        "source_completion_queue_json": rel(QUEUE_JSON),
        "source_completion_queue_csv": rel(QUEUE_CSV),
        "source_confirmed_preview_csv": rel(CONFIRMED_PREVIEW_CSV)
        if CONFIRMED_PREVIEW_CSV.exists()
        else "",
        "target_workbook_csv": rel(WORKBOOK_CSV),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_packet.py",
        "selected_blocker_count": len(EXPECTED_SELECTED_BLOCKERS),
        "selected_blocker_ids": EXPECTED_SELECTED_BLOCKERS,
        "source_queue_item_count": len(items),
        "quick_fill_row_count": len(fill_rows),
        "blank_value_row_count": blank_value_count,
        "confirmed_value_row_count": confirmed_value_count,
        "human_input_required": blank_value_count > 0,
        "human_review_required": True,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "ready_for_safety_preflight": confirmed_rows_available,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_quick_fill_packet": 0,
        "boundary_violation_count": 0,
        "boundary_violations": [],
        "blocker_fill_counts": dict(sorted(blocker_counts.items())),
        "owner_lane_fill_counts": dict(sorted(lane_counts.items())),
        "quick_fill_rows": fill_rows,
        "next_human_action": (
            "Run the local safety preflight and workbook-import dry run, then ask "
            "for separate human approval before any real workbook import."
            if confirmed_rows_available
            else "Fill human_value_to_enter in the quick-fill CSV, then copy reviewed "
            "values into the workbook CSV human_value_placeholder column in a "
            "separate human-approved step."
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
        "human_fill_prompt",
        "human_value_to_enter",
        "notes_for_human",
        "target_workbook_csv",
        "target_workbook_column",
        "target_json_pointer",
        "quick_fill_status",
        "value_imported_to_workbook",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["quick_fill_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_packet_v0_1: true",
        f"status: {payload['status']}",
        f"packet_scope: {payload['packet_scope']}",
        f"source_queue_item_count: {payload['source_queue_item_count']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"blank_value_row_count: {payload['blank_value_row_count']}",
        f"confirmed_value_row_count: {payload['confirmed_value_row_count']}",
        f"quick_fill_values_entered_by_codex: {str(payload['quick_fill_values_entered_by_codex']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_quick_fill_packet: {payload['blockers_closed_by_quick_fill_packet']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Packet",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This packet is a compact human-facing sheet derived from the completion",
        "queue. It is easier to fill than the full workbook because it contains",
        "only the 64 missing required rows.",
        "",
        "## Fill Counts",
        "",
        "| Blocker | Rows to fill |",
        "| --- | ---: |",
    ]
    for blocker, count in payload["blocker_fill_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Human Procedure",
            "",
            "1. Open the quick-fill CSV.",
            "2. Fill only `human_value_to_enter` and optional `notes_for_human`.",
            "3. Review the values manually.",
            "4. Copy reviewed values into the workbook CSV in a separate human-approved step.",
            "5. Rerun the workbook validator.",
            "",
            "## Boundary",
            "",
            "No values were entered by Codex. No values were imported into the",
            "workbook. No values were transferred into templates. No human-filled",
            "templates were written. No validators were run on real input.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Packet Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This quick-fill packet is a local blank sheet only. It does not authorize",
        "value import, value transfer, evidence collection, execution, blocker",
        "closure, customer/vendor contact, launch, customer-validation claims, or",
        "production-readiness claims.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Packet v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the compact quick-fill layer for the current",
        "commercial sprint human inputs. It improves the human operator workflow",
        "without changing SAEE product behavior.",
        "",
        "## Boundary",
        "",
        "The packet does not fill values, import values, transfer values, write",
        "human-filled templates, run validators on real input, collect evidence,",
        "execute builders, contact customers or vendors, close blockers, launch",
        "product, or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Packet Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_packet_v0_1: true",
        "answer: recommend",
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
        "This packet is recommendable as a coordination surface because it reduces",
        "human input friction while preserving all execution and evidence",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET: PASS "
        f"status={payload['status']} "
        f"quick_fill_row_count={payload['quick_fill_row_count']} "
        f"quick_fill_imported_to_workbook={str(payload['quick_fill_imported_to_workbook']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
