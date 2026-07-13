#!/usr/bin/env python3
"""Build the Phase 2 data/operations priority evidence collection packet.

This runner extracts Phase 2 data recovery and production-operations rows from
the cross-phase commercial production evidence collection packet and creates a
human-fillable priority template. It does not deploy monitoring, contact
vendors, send external alerts, activate on-call, run restore tests, touch live
data paths, collect evidence, close blockers, or claim production readiness.
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
    / "phase_b_product/commercial_readiness/phase_2_data_operations_priority_evidence_collection"
)
OUTPUT_JSON = OUTPUT_DIR / "phase_2_data_operations_priority_evidence_collection.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_2_data_operations_priority_evidence_collection.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_2_data_operations_priority_evidence_collection.csv"
OUTPUT_CHECKLIST = OUTPUT_DIR / "phase_2_data_operations_priority_collection_checklist.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "phase_2_data_operations_evidence_input.priority.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "phase_2_data_operations_priority_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_2_DATA_OPERATIONS_PRIORITY_EVIDENCE_COLLECTION_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_2_DATA_OPERATIONS_PRIORITY_EVIDENCE_COLLECTION_RECOMMENDATION_GATE.md"
)


PHASE_ID = "phase_2_data_and_operations_resilience"
TARGET_BLOCKERS = [
    "production_monitoring",
    "external_alert_delivery",
    "on_call_rotation",
    "restore_tested",
    "production_restore_policy",
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
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "execution_authorized",
    "evidence_collection_authorized",
    "monitoring_vendor_contacted_by_codex",
    "alert_provider_contacted_by_codex",
    "external_alert_sent_by_codex",
    "monitoring_deployment_authorized",
    "external_alert_delivery_authorized",
    "on_call_activation_authorized",
    "on_call_rotation_activated",
    "restore_test_authorized",
    "restore_test_executed",
    "live_restore_performed",
    "production_data_path_modified",
    "customer_data_processed",
    "codex_inferred_missing_evidence",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def phase2_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
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
                "phase_2_record_id": f"P2-ECP-{index:03d}",
                "source_collection_record_id": row.get("collection_record_id", ""),
                "priority_rank": index,
                "priority_tier": "missing_production_evidence" if missing else "local_public_shell_requires_human_approval",
                "blocker_id": row.get("blocker_id", ""),
                "blocker_priority": BLOCKER_PRIORITY.get(str(row.get("blocker_id")), 99),
                "evidence_file_type": row.get("evidence_file_type", ""),
                "evidence_key": row.get("evidence_key", ""),
                "gap_status": row.get("gap_status", ""),
                "local_public_shell_value": row.get("local_public_shell_value") is True,
                "production_evidence_missing": missing,
                "owner_review_lane": row.get("owner_review_lane", "operations_engineering"),
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
                    "production_data_path",
                    "monitoring_vendor_without_approval",
                    "alert_delivery_without_approval",
                    "on_call_activation_without_approval",
                    "restore_execution_without_approval",
                ],
                "required_human_action": (
                    "Provide source-backed production evidence and a reviewer note; do not mark accepted for closure without a separate human approval."
                ),
            }
        )
    return priority_rows


def build_priority_template(priority_rows: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_keys = [row["evidence_key"] for row in priority_rows]
    return {
        "phase_2_data_operations_priority_evidence_collection_v0_1": True,
        "input_status": "priority_template_not_filled",
        "human_reviewer_name": "",
        "review_date": "",
        "evidence_source_notes": "",
        "source_collection_packet": rel(SOURCE_PACKET_PATH),
        "priority_collection_source": rel(OUTPUT_JSON),
        "template_note": (
            "Human owners fill evidence_review and source_notes_by_key. Codex must not infer missing evidence, contact vendors, send alerts, activate on-call, run restore tests, or touch live data paths."
        ),
        "evidence_review": {key: False for key in evidence_keys},
        "source_notes_by_key": {key: "" for key in evidence_keys},
        "priority_evidence_key_order": evidence_keys,
        "priority_collection_map_by_key": {
            row["evidence_key"]: {
                "phase_2_record_id": row["phase_2_record_id"],
                "source_collection_record_id": row["source_collection_record_id"],
                "blocker_id": row["blocker_id"],
                "priority_tier": row["priority_tier"],
                "evidence_file_type": row["evidence_file_type"],
            }
            for row in priority_rows
        },
        "boundary_review": {
            "monitoring_vendor_contacted": False,
            "alert_provider_contacted": False,
            "external_alert_sent": False,
            "on_call_rotation_activated": False,
            "restore_test_executed": False,
            "live_restore_performed": False,
            "production_data_path_modified": False,
            "customer_data_processed": False,
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
                    "Human owner must provide source-backed production evidence in the priority template."
                ),
            }
        )
    return summary


def build_packet() -> dict[str, Any]:
    source_packet = read_json(SOURCE_PACKET_PATH)
    rows = phase2_rows(source_packet)
    priority_rows = build_priority_rows(rows)
    local_present = sum(1 for row in priority_rows if row["local_public_shell_value"])
    missing = sum(1 for row in priority_rows if row["production_evidence_missing"])
    packet: dict[str, Any] = {
        "packet_type": "saee_phase_2_data_operations_priority_evidence_collection",
        "packet_version": "0.1",
        "status": "ready_for_human_review_not_execution",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_phase2_data_operations_priority_evidence_collection.py",
        "scope": "phase_2_data_operations_priority_human_evidence_collection",
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
            "Human operations/data owner fills the priority template with source-backed evidence, then opens a separate execution or blocker-closure request if justified."
        ),
        "post_fill_commands": [
            "python3 scripts/saee_data_operations_evidence_runner.py",
            "python3 scripts/saee_operations_evidence_runner.py",
            "python3 scripts/saee_phase2_data_operations_gap_audit.py",
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
        "phase_2_record_id",
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
    return f"""# SAEE Phase 2 Data/Operations Priority Evidence Collection

Status: ready for human review, not execution.

This directory extracts the Phase 2 production monitoring, alert delivery,
on-call, restore-test, and restore-policy evidence items from the cross-phase
commercial production evidence collection packet and provides a human-fillable
priority template.

Counts:

- required_evidence_item_count: {packet['required_evidence_item_count']}
- local_public_shell_present_count: {packet['local_public_shell_present_count']}
- missing_production_evidence_count: {packet['missing_production_evidence_count']}
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

Boundary:

- no monitoring vendor contacted by Codex
- no alert provider contacted by Codex
- no external alert sent by Codex
- no on-call activation by Codex
- no restore test run by Codex
- no production data path modification
- no customer data processing
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
        "| {phase_2_record_id} | {priority_tier} | {blocker_id} | {evidence_key} | {human_fill_status} |".format(
            **row
        )
        for row in packet["priority_rows"]
    )
    return f"""# SAEE Phase 2 Data/Operations Priority Evidence Collection v0.1

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

1. Fill `phase_2_data_operations_evidence_input.priority.template.json` with
   source-backed production evidence.
2. Keep every boundary flag false unless a separate approved execution request
   exists.
3. Re-run the existing operations and data-operations evidence runners only
   after local evidence paths are configured by a human.
4. Re-run the Phase 2 gap audit and mainline guard.

## What This Does Not Do

It does not collect evidence, deploy monitoring, contact vendors, send alerts,
activate on-call, run restore tests, modify production data paths, process
customer data, close blockers, or claim production readiness.
"""


def render_checklist(packet: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 2 Data/Operations Priority Collection Checklist",
        "",
        "Use this only after a human owner decides to collect Phase 2 evidence.",
        "",
    ]
    for row in packet["priority_rows"]:
        lines.append(
            f"- [ ] {row['phase_2_record_id']} `{row['blocker_id']}` / `{row['evidence_key']}` "
            "-> fill `evidence_review` and `source_notes_by_key` in the priority template"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Do not deploy monitoring from this packet.",
            "- Do not contact monitoring or alert vendors from this packet.",
            "- Do not send external alerts from this packet.",
            "- Do not activate on-call from this packet.",
            "- Do not run restore tests from this packet.",
            "- Do not modify production data paths from this packet.",
            "- Do not close blockers from this packet.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_boundary(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 2 Priority Collection Boundary Audit

- monitoring_vendor_contacted_by_codex: false
- alert_provider_contacted_by_codex: false
- external_alert_sent_by_codex: false
- monitoring_deployment_authorized: false
- external_alert_delivery_authorized: false
- on_call_activation_authorized: false
- on_call_rotation_activated: false
- restore_test_authorized: false
- restore_test_executed: false
- live_restore_performed: false
- production_data_path_modified: false
- customer_data_processed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_collection: {packet['blockers_closed_by_collection']}

This packet is a human-review collection planner only.
"""


def render_doc(packet: dict[str, Any]) -> str:
    return f"""# Phase 2 Data/Operations Priority Evidence Collection v0.1

phase_2_data_operations_priority_evidence_collection_v0_1: true
status: ready_for_human_review_not_execution
scope: phase_2_data_operations_priority_human_evidence_collection
required_evidence_item_count: {packet['required_evidence_item_count']}
local_public_shell_present_count: {packet['local_public_shell_present_count']}
missing_production_evidence_count: {packet['missing_production_evidence_count']}
accepted_for_blocker_closure_count: {packet['accepted_for_blocker_closure_count']}
blockers_closed_by_collection: {packet['blockers_closed_by_collection']}
execution_authorized: false
evidence_collection_authorized: false
monitoring_vendor_contacted_by_codex: false
alert_provider_contacted_by_codex: false
external_alert_sent_by_codex: false
on_call_rotation_activated: false
restore_test_executed: false
production_data_path_modified: false
production_ready: false
customer_validated: false
private_core_exposed: false

This packet extracts the 26 Phase 2 evidence items from the cross-phase queue
and provides a human-fillable priority evidence template. It is not production
evidence and does not close blockers.
"""


def render_gate(packet: dict[str, Any]) -> str:
    return f"""# SAEE Phase 2 Data/Operations Priority Evidence Collection Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_human_evidence_input: true
recommend_for_evidence_collection_authorization: false
recommend_for_execution_authorization: false
recommend_for_blocker_closure: false
recommend_for_monitoring_deployment: false
recommend_for_alert_delivery: false
recommend_for_on_call_activation: false
recommend_for_restore_test_execution: false
recommend_for_production_launch: false

reason: This packet improves Phase 2 commercial readiness by creating a
human-fillable priority input surface for 26 data-recovery and
production-operations evidence items. It does not supply evidence or authorize
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
        "SAEE_PHASE2_DATA_OPERATIONS_PRIORITY_EVIDENCE_COLLECTION: PASS "
        f"required_items={packet['required_evidence_item_count']} "
        f"local_public_shell={packet['local_public_shell_present_count']} "
        f"missing_production={packet['missing_production_evidence_count']} "
        f"blockers_closed_by_collection={packet['blockers_closed_by_collection']}"
    )


if __name__ == "__main__":
    main()
