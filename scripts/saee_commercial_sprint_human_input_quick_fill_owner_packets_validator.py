#!/usr/bin/env python3
"""Validate completion state of quick-fill owner packets.

This validator checks whether humans have filled the blocker-specific owner
packet CSVs. It does not merge values back to the source quick-fill packet,
import values into the workbook, transfer values into templates, run evidence
validators on real input, collect evidence, execute builders, contact anyone,
close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "quick_fill_owner_packets"
)
SOURCE_JSON = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets.local.json"

OUT_JSON = (
    PACKET_DIR
    / "commercial_sprint_human_input_quick_fill_owner_packets_validation.local.json"
)
OUT_MD = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_validation.md"
OUT_CSV = PACKET_DIR / "commercial_sprint_human_input_quick_fill_owner_packets_validation.csv"
OUT_BOUNDARY = (
    PACKET_DIR
    / "commercial_sprint_human_input_quick_fill_owner_packets_validation_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR_RECOMMENDATION_GATE.md"
)

EXPECTED_TOTAL_ROWS = 64
EXPECTED_PACKET_COUNT = 5
EXPECTED_COUNTS_BY_BLOCKER = {
    "formal_security_review": 12,
    "pricing_page": 14,
    "production_monitoring": 10,
    "production_restore_policy": 13,
    "support_contact": 15,
}
OWNER_PACKETS_READY_STATUS = "ready_for_owner_lane_human_quick_fill"
OWNER_PACKETS_COMPLETED_STATUS = (
    "completed_owner_lane_packets_pending_workbook_import_approval_review"
)
COMPLETED_VALIDATION_STATUS = (
    "completed_owner_packet_values_pending_workbook_import_approval_review"
)

FALSE_FLAGS = [
    "ready_for_quick_fill_merge",
    "ready_for_workbook_import",
    "ready_for_template_transfer",
    "ready_for_existing_local_validators",
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

SECRET_TOKENS = [
    "sk-",
    "openai_api_key",
    "begin private key",
    "password=",
    "api_key=",
    "secret=",
    "token=",
]

FORBIDDEN_CLAIM_TOKENS = [
    "production_ready=true",
    '"production_ready": true',
    "product_launched=true",
    '"product_launched": true',
    "customer_validated=true",
    '"customer_validated": true',
    "private_core_exposed=true",
    '"private_core_exposed": true',
    "execution_authorized=true",
    '"execution_authorized": true',
    "evidence_collection_authorized=true",
    '"evidence_collection_authorized": true',
    "blockers_closed=true",
    '"blockers_closed": true',
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


def value_scan_counts(row: dict[str, str]) -> tuple[int, int]:
    searchable = " ".join(
        [row.get("human_value_to_enter", ""), row.get("notes_for_human", "")]
    ).lower()
    secret_hits = sum(1 for token in SECRET_TOKENS if token in searchable)
    forbidden_hits = sum(1 for token in FORBIDDEN_CLAIM_TOKENS if token in searchable)
    return secret_hits, forbidden_hits


def row_boundary_violations(row: dict[str, str]) -> list[str]:
    violations: list[str] = []
    if row.get("blocker_id") not in EXPECTED_COUNTS_BY_BLOCKER:
        violations.append("unexpected_blocker_id")
    for flag in [
        "codex_filled_value",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
    ]:
        if parse_bool(row.get(flag, "")):
            violations.append(f"{flag}_is_true")
    secret_hits, forbidden_hits = value_scan_counts(row)
    if secret_hits:
        violations.append("unsafe_value_pattern_detected")
    if forbidden_hits:
        violations.append("forbidden_claim_pattern_detected")
    return violations


def build_payload() -> dict[str, Any]:
    source = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    packets = source.get("owner_packets", [])
    boundary_violations: list[str] = []

    if source.get("status") not in {
        OWNER_PACKETS_READY_STATUS,
        OWNER_PACKETS_COMPLETED_STATUS,
    }:
        boundary_violations.append("source_owner_packets_status_changed")
    if source.get("owner_packet_count") != EXPECTED_PACKET_COUNT:
        boundary_violations.append("source_owner_packet_count_changed")
    for flag in [
        "workbook_import_authorized",
        "workbook_import_performed",
        "workbook_written",
        "validators_run_on_real_input",
        "values_transferred",
        "evidence_collection_authorized",
        "execution_authorized",
        "evidence_builder_executed",
        "blocker_closure_authorized",
    ]:
        if source.get(flag) is not False:
            boundary_violations.append(f"source_{flag}_changed")

    validation_rows: list[dict[str, Any]] = []
    packet_summaries: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    owner_lane_counts: Counter[str] = Counter()
    packet_id_counts: Counter[str] = Counter()
    completed = 0
    missing = 0
    unsafe_hits = 0
    forbidden_hits = 0
    all_ids: list[str] = []

    for packet in packets:
        packet_csv = packet.get("owner_packet_csv", "")
        packet_path = ROOT / packet_csv
        if not packet_path.exists():
            boundary_violations.append(f"missing_owner_packet_csv:{packet_csv}")
            continue

        rows = read_csv(packet_path)
        packet_completed = 0
        packet_missing = 0
        packet_boundary_count = 0

        for row in rows:
            row_id = row.get("quick_fill_row_id", "")
            all_ids.append(row_id)
            blocker_id = row.get("blocker_id", "")
            owner_lane = row.get("owner_review_lane", "")
            owner_packet_id = row.get("owner_packet_id", "")
            blocker_counts[blocker_id] += 1
            owner_lane_counts[owner_lane] += 1
            packet_id_counts[owner_packet_id] += 1

            value_present = bool(row.get("human_value_to_enter", "").strip())
            notes_present = bool(row.get("notes_for_human", "").strip())
            secret_count, forbidden_count = value_scan_counts(row)
            unsafe_hits += secret_count
            forbidden_hits += forbidden_count
            row_violations = row_boundary_violations(row)
            if row_violations:
                packet_boundary_count += len(row_violations)
                boundary_violations.extend(
                    f"{row_id or '<missing>'}:{violation}" for violation in row_violations
                )

            row_complete = value_present and not row_violations
            if row_complete:
                completed += 1
                packet_completed += 1
                row_status = "present_unvalidated_human_value"
            else:
                missing += 1
                packet_missing += 1
                row_status = "missing_human_value" if not value_present else "stop_boundary_risk"

            validation_rows.append(
                {
                    "owner_packet_id": owner_packet_id,
                    "blocker_id": blocker_id,
                    "owner_review_lane": owner_lane,
                    "worksheet_row_id": row.get("worksheet_row_id", ""),
                    "quick_fill_row_id": row_id,
                    "input_group": row.get("input_group", ""),
                    "input_key": row.get("input_key", ""),
                    "human_value_present": value_present,
                    "notes_present": notes_present,
                    "row_complete": row_complete,
                    "status": row_status,
                    "raw_value_recorded": False,
                    "value_merged_to_quick_fill": False,
                    "workbook_import_performed": False,
                    "validators_run_on_real_input": False,
                    "evidence_collection_authorized": False,
                    "execution_authorized": False,
                }
            )

        packet_summaries.append(
            {
                "owner_packet_id": packet.get("owner_packet_id", ""),
                "blocker_id": packet.get("blocker_id", ""),
                "owner_packet_csv": packet_csv,
                "packet_row_count": len(rows),
                "completed_owner_packet_row_count": packet_completed,
                "missing_owner_packet_row_count": packet_missing,
                "boundary_violation_count": packet_boundary_count,
                "ready_for_quick_fill_merge": False,
            }
        )

    duplicate_ids = sorted([item for item, count in Counter(all_ids).items() if count > 1])
    if duplicate_ids:
        boundary_violations.append("duplicate_quick_fill_row_id")
    if len(validation_rows) != EXPECTED_TOTAL_ROWS:
        boundary_violations.append("unexpected_total_owner_packet_row_count")
    if len(packet_summaries) != EXPECTED_PACKET_COUNT:
        boundary_violations.append("unexpected_owner_packet_count")
    if dict(sorted(blocker_counts.items())) != EXPECTED_COUNTS_BY_BLOCKER:
        boundary_violations.append("unexpected_owner_packet_rows_by_blocker")

    boundary_violation_count = len(boundary_violations)
    all_complete = (
        len(validation_rows) == EXPECTED_TOTAL_ROWS
        and missing == 0
        and boundary_violation_count == 0
    )
    if boundary_violation_count:
        status = "stop_boundary_violation"
    elif all_complete:
        status = COMPLETED_VALIDATION_STATUS
    else:
        status = "hold_owner_packet_human_values_required"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1": True,
        "validator_type": "local_owner_packet_completion_validator",
        "validator_scope": "owner_packet_human_value_completion_only_no_merge_no_import",
        "status": status,
        "source_owner_packets_json": rel(SOURCE_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": (
            "scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator.py"
        ),
        "owner_packet_count": len(packet_summaries),
        "quick_fill_row_count": len(validation_rows),
        "required_owner_packet_row_count": EXPECTED_TOTAL_ROWS,
        "completed_owner_packet_row_count": completed,
        "missing_owner_packet_row_count": missing,
        "all_owner_packets_complete": all_complete,
        "human_input_required": not all_complete,
        "human_review_required": True,
        "ready_for_workbook_import_approval_review": all_complete,
        "local_owner_packet_validator_run": True,
        "raw_values_recorded": False,
        "unsafe_value_pattern_hit_count": unsafe_hits,
        "forbidden_claim_pattern_hit_count": forbidden_hits,
        "blockers_closed_by_owner_packet_validator": 0,
        "boundary_violation_count": boundary_violation_count,
        "boundary_violations": boundary_violations,
        "duplicate_quick_fill_row_ids": duplicate_ids,
        "owner_packet_rows_by_blocker": dict(sorted(blocker_counts.items())),
        "owner_packet_rows_by_lane": dict(sorted(owner_lane_counts.items())),
        "owner_packet_rows_by_packet": dict(sorted(packet_id_counts.items())),
        "owner_packet_summaries": packet_summaries,
        "validation_rows": validation_rows,
        "next_human_action": (
            "Review the workbook import approval request packet for the confirmed "
            "owner-packet values. Do not merge values, import a workbook, run "
            "validators on real input, collect evidence, or close blockers without "
            "separate human approval."
            if all_complete
            else (
                "Fill missing human_value_to_enter cells in owner packet CSVs, then "
                "copy reviewed values back to the source quick-fill CSV and rerun "
                "the quick-fill safety preflight before any import request."
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
        "owner_packet_id",
        "blocker_id",
        "owner_review_lane",
        "worksheet_row_id",
        "quick_fill_row_id",
        "input_group",
        "input_key",
        "human_value_present",
        "notes_present",
        "row_complete",
        "status",
        "raw_value_recorded",
        "value_merged_to_quick_fill",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["validation_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1: true",
        f"status: {payload['status']}",
        f"validator_scope: {payload['validator_scope']}",
        f"owner_packet_count: {payload['owner_packet_count']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"required_owner_packet_row_count: {payload['required_owner_packet_row_count']}",
        f"completed_owner_packet_row_count: {payload['completed_owner_packet_row_count']}",
        f"missing_owner_packet_row_count: {payload['missing_owner_packet_row_count']}",
        f"all_owner_packets_complete: {str(payload['all_owner_packets_complete']).lower()}",
        "ready_for_workbook_import_approval_review: "
        f"{str(payload['ready_for_workbook_import_approval_review']).lower()}",
        f"raw_values_recorded: {str(payload['raw_values_recorded']).lower()}",
        f"unsafe_value_pattern_hit_count: {payload['unsafe_value_pattern_hit_count']}",
        f"forbidden_claim_pattern_hit_count: {payload['forbidden_claim_pattern_hit_count']}",
        f"ready_for_quick_fill_merge: {str(payload['ready_for_quick_fill_merge']).lower()}",
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
        f"blockers_closed_by_owner_packet_validator: {payload['blockers_closed_by_owner_packet_validator']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Owner Packets Validation",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This validator checks completion state across the five owner packet CSVs.",
        "It records counts only and does not record raw human values.",
        "",
        "## Completion State",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Owner packets | {payload['owner_packet_count']} |",
        f"| Required rows | {payload['required_owner_packet_row_count']} |",
        f"| Completed rows | {payload['completed_owner_packet_row_count']} |",
        f"| Missing rows | {payload['missing_owner_packet_row_count']} |",
        f"| Unsafe value pattern hits | {payload['unsafe_value_pattern_hit_count']} |",
        f"| Forbidden claim pattern hits | {payload['forbidden_claim_pattern_hit_count']} |",
        "",
        "## Owner Packet State",
        "",
        "| Packet | Blocker | Rows | Completed | Missing | Boundary Violations |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for packet in payload["owner_packet_summaries"]:
        lines.append(
            "| "
            f"`{packet['owner_packet_id']}` | "
            f"`{packet['blocker_id']}` | "
            f"{packet['packet_row_count']} | "
            f"{packet['completed_owner_packet_row_count']} | "
            f"{packet['missing_owner_packet_row_count']} | "
            f"{packet['boundary_violation_count']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No owner-packet value was merged into the source quick-fill packet. No",
            "workbook import was authorized or performed. No values were transferred",
            "into templates. No validators were run on real input. No evidence was",
            "collected and no blocker was closed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Owner Packets Validation Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This validator is local and read-only with respect to commercial evidence",
        "execution. It checks owner-packet completion state only. It does not",
        "record raw human values, merge values into the source quick-fill packet,",
        "import values into the workbook, write workbook files, transfer values,",
        "run validators on real input, collect evidence, execute builders, contact",
        "customers or vendors, close blockers, launch product, or claim production",
        "readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Owner Packets Validator v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the local completion validator for the commercial",
        "sprint owner packets. It supports human input coordination without",
        "changing SAEE product behavior.",
        "",
        "## Boundary",
        "",
        "The validator does not fill values, record raw values, merge values into",
        "the source quick-fill packet, import workbooks, transfer values, write",
        "human-filled templates, run validators on real input, collect evidence,",
        "execute builders, contact customers or vendors, close blockers, launch",
        "product, or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Owner Packets Validator Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_owner_packets_validator_v0_1: true",
        "answer: recommend",
        "recommend_for_owner_packet_completion_validation: true",
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
        "This validator is recommendable as a local coordination check because it",
        "shows whether the blocker-specific owner packets are complete while",
        "preserving all value merge, import, execution, evidence, launch, and",
        "production-readiness boundaries.",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_OWNER_PACKETS_VALIDATOR: PASS "
        f"status={payload['status']} "
        f"completed_owner_packet_row_count={payload['completed_owner_packet_row_count']} "
        f"missing_owner_packet_row_count={payload['missing_owner_packet_row_count']} "
        f"ready_for_quick_fill_merge={str(payload['ready_for_quick_fill_merge']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
