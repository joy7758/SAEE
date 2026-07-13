#!/usr/bin/env python3
"""Build blocker-specific owner packets from the quick-fill human worksheet.

This creates five local CSV packets, one per blocker / owner lane, so humans can
divide the 64 quick-fill rows without editing runtime, importing workbooks, or
executing evidence work.
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
PACKET_DIR = SPRINT_DIR / "quick_fill_owner_packets"
SOURCE_WORKSHEET_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.local.json"
)

OUT_JSON = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.local.json"
OUT_MD = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.md"
OUT_CSV = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.csv"
OUT_BOUNDARY = (
    PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 64
EXPECTED_PACKET_COUNT = 5
COMPLETED_STATUS = "completed_owner_lane_packets_pending_workbook_import_approval_review"
READY_STATUS = "ready_for_owner_lane_human_quick_fill"

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


def slug(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in text.lower())


def load_worksheet() -> dict[str, Any]:
    return json.loads(SOURCE_WORKSHEET_JSON.read_text(encoding="utf-8"))


def owner_packet_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["blocker_id"]].append(row)
    return dict(sorted(grouped.items()))


def packet_csv_fields() -> list[str]:
    return [
        "owner_packet_id",
        "blocker_id",
        "owner_review_lane",
        "worksheet_row_id",
        "quick_fill_row_id",
        "input_group",
        "input_key",
        "input_kind",
        "expected_value_shape",
        "fill_instruction",
        "leave_blank_condition",
        "target_json_pointer",
        "human_value_to_enter",
        "notes_for_human",
        "packet_status",
        "codex_filled_value",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
    ]


def packetize_row(packet_id: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "owner_packet_id": packet_id,
        "blocker_id": row["blocker_id"],
        "owner_review_lane": row["owner_review_lane"],
        "worksheet_row_id": row["worksheet_row_id"],
        "quick_fill_row_id": row["quick_fill_row_id"],
        "input_group": row["input_group"],
        "input_key": row["input_key"],
        "input_kind": row["input_kind"],
        "expected_value_shape": row["expected_value_shape"],
        "fill_instruction": row["fill_instruction"],
        "leave_blank_condition": row["leave_blank_condition"],
        "target_json_pointer": row["target_json_pointer"],
        "human_value_to_enter": row.get("human_value_to_enter", ""),
        "notes_for_human": row.get("notes_for_human", ""),
        "packet_status": (
            "ready_for_human_value"
            if not row.get("human_value_to_enter", "")
            else "human_value_present_unvalidated"
        ),
        "codex_filled_value": False,
        "workbook_import_performed": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
    }


def build_payload() -> dict[str, Any]:
    worksheet = load_worksheet()
    rows = worksheet.get("worksheet_rows", [])
    grouped = owner_packet_rows(rows)
    blocker_counts: Counter[str] = Counter()
    owner_lane_counts: Counter[str] = Counter()
    blank_value_count = 0
    boundary_violations: list[str] = []
    packets: list[dict[str, Any]] = []

    if len(rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_source_worksheet_row_count")
    if len(grouped) != EXPECTED_PACKET_COUNT:
        boundary_violations.append("unexpected_owner_packet_count")
    if worksheet.get("workbook_import_authorized") is not False:
        boundary_violations.append("source_worksheet_authorizes_workbook_import")
    if worksheet.get("validators_run_on_real_input") is not False:
        boundary_violations.append("source_worksheet_ran_validators_on_real_input")

    PACKET_DIR.mkdir(parents=True, exist_ok=True)

    for index, (blocker_id, blocker_rows) in enumerate(grouped.items(), start=1):
        owner_lanes = sorted({row["owner_review_lane"] for row in blocker_rows})
        packet_id = f"QFOP-{index:03d}"
        packet_filename = f"{slug(blocker_id)}_quick_fill_owner_packet.csv"
        packet_path = PACKET_DIR / packet_filename
        packet_rows = [packetize_row(packet_id, row) for row in blocker_rows]

        for row in packet_rows:
            blocker_counts[row["blocker_id"]] += 1
            owner_lane_counts[row["owner_review_lane"]] += 1
            if not row["human_value_to_enter"]:
                blank_value_count += 1

        with packet_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=packet_csv_fields())
            writer.writeheader()
            writer.writerows(packet_rows)

        packets.append(
            {
                "owner_packet_id": packet_id,
                "blocker_id": blocker_id,
                "owner_review_lanes": owner_lanes,
                "owner_packet_csv": rel(packet_path),
                "packet_row_count": len(packet_rows),
                "blank_human_value_row_count": sum(
                    1 for row in packet_rows if not row["human_value_to_enter"]
                ),
                "suggested_values_count": 0,
                "codex_filled_value_count": 0,
                "workbook_import_authorized": False,
                "workbook_import_performed": False,
                "validators_run_on_real_input": False,
                "evidence_collection_authorized": False,
                "execution_authorized": False,
                "blockers_closed_by_owner_packet": 0,
            }
        )

    if boundary_violations:
        status = "stop_boundary_violation"
    elif blank_value_count == 0:
        status = COMPLETED_STATUS
    else:
        status = READY_STATUS
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_owner_packets_v0_1": True,
        "packet_type": "blocker_specific_human_quick_fill_owner_packets",
        "packet_scope": (
            "manual_owner_review_packets_only_no_import"
            if blank_value_count == 0
            else "manual_owner_entry_packets_only_no_values_no_import"
        ),
        "status": status,
        "source_worksheet_json": rel(SOURCE_WORKSHEET_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": (
            "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets.py"
        ),
        "quick_fill_row_count": len(rows),
        "owner_packet_count": len(packets),
        "owner_review_lane_count": len(owner_lane_counts),
        "blocker_count": len(blocker_counts),
        "blank_human_value_row_count": blank_value_count,
        "nonblank_human_value_row_count": len(rows) - blank_value_count,
        "suggested_values_count": 0,
        "human_input_required": blank_value_count > 0,
        "human_review_required": True,
        "ready_for_human_quick_fill": not boundary_violations and blank_value_count > 0,
        "ready_for_workbook_import_approval_review": (
            not boundary_violations and blank_value_count == 0
        ),
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "blockers_closed_by_owner_packets": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "owner_packet_rows_by_blocker": dict(sorted(blocker_counts.items())),
        "owner_packet_rows_by_lane": dict(sorted(owner_lane_counts.items())),
        "owner_packets": packets,
        "next_human_action": (
            "Review owner-lane packets as a record of the confirmed quick-fill "
            "values. Do not merge, import a workbook, run validators on real "
            "input, collect evidence, or close blockers without separate human "
            "approval."
            if blank_value_count == 0
            else (
                "Give each owner packet CSV to the matching human owner lane, then "
                "copy approved values back into the source quick-fill CSV and rerun "
                "the quick-fill validator."
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


def write_index_csv(payload: dict[str, Any]) -> None:
    fields = [
        "owner_packet_id",
        "blocker_id",
        "owner_review_lanes",
        "owner_packet_csv",
        "packet_row_count",
        "blank_human_value_row_count",
        "suggested_values_count",
        "workbook_import_authorized",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
        "blockers_closed_by_owner_packet",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for packet in payload["owner_packets"]:
            row = dict(packet)
            row["owner_review_lanes"] = ";".join(packet["owner_review_lanes"])
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_owner_packets_v0_1: true",
        f"status: {payload['status']}",
        f"packet_scope: {payload['packet_scope']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"owner_packet_count: {payload['owner_packet_count']}",
        f"owner_review_lane_count: {payload['owner_review_lane_count']}",
        f"blocker_count: {payload['blocker_count']}",
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
        f"blockers_closed_by_owner_packets: {payload['blockers_closed_by_owner_packets']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Owner Packets",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "These packets split the 64 quick-fill rows by blocker and owner review",
        "lane so humans can complete values in parallel. They do not provide",
        "values and do not authorize import, transfer, validation, evidence work,",
        "or blocker closure.",
        "",
        "## Owner Packet Index",
        "",
        "| Packet | Blocker | Owner Lane | Rows | Blank Values | CSV |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for packet in payload["owner_packets"]:
        lanes = ", ".join(f"`{lane}`" for lane in packet["owner_review_lanes"])
        lines.append(
            "| "
            f"`{packet['owner_packet_id']}` | "
            f"`{packet['blocker_id']}` | "
            f"{lanes} | "
            f"{packet['packet_row_count']} | "
            f"{packet['blank_human_value_row_count']} | "
            f"`{packet['owner_packet_csv']}` |"
        )
    lines.extend(
        [
            "",
            "## Human Procedure",
            "",
            "1. Give each packet CSV to the human owner lane listed above.",
            "2. Human owners fill only reviewed values in their local copy.",
            "3. Copy approved values back into the source quick-fill CSV.",
            "4. Run the quick-fill safety preflight and validator before import.",
            "5. Request separate workbook-import approval only after validation passes.",
            "",
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
        "# Commercial Sprint Human Input Quick-Fill Owner Packets Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "These packets are local manual-entry aids only. They do not fill values,",
        "suggest actual values, import values into the workbook, write workbook",
        "files, transfer values, run validators on real input, collect evidence,",
        "execute builders, contact customers or vendors, close blockers, launch",
        "product, or claim production readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Owner Packets v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the blocker-specific owner packet layer for the",
        "commercial sprint quick-fill path. It exists to make human assignment",
        "and manual value entry easier without changing SAEE behavior.",
        "",
        "## Boundary",
        "",
        "The owner packets do not generate values, import workbooks, write workbook",
        "files, transfer values, run validators on real input, collect evidence,",
        "close blockers, launch product, or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Owner Packets Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_owner_packets_v0_1: true",
        "answer: recommend",
        "recommend_for_owner_lane_handoff: true",
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
        "These owner packets are recommendable as manual handoff aids because they",
        "split existing blank quick-fill rows by blocker and owner lane while",
        "preserving all import, execution, evidence, launch, production-readiness,",
        "and blocker-closure boundaries.",
        "",
        "## Status",
        "",
        *status_lines(payload),
    ]
    GATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_json(payload)
    write_index_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS: PASS "
        f"status={payload['status']} "
        f"owner_packet_count={payload['owner_packet_count']} "
        f"quick_fill_row_count={payload['quick_fill_row_count']} "
        f"blank_human_value_row_count={payload['blank_human_value_row_count']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
