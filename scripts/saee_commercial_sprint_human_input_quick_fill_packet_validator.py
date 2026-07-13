#!/usr/bin/env python3
"""Validate completion state of the commercial sprint quick-fill packet.

This validator checks whether a human has filled the quick-fill CSV values. It
does not import values into the workbook, transfer values into templates, write
human-filled templates, run validators on real input, collect evidence, execute
builders, contact anyone, close blockers, launch product, or claim production
readiness.
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
QUICK_FILL_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR_RECOMMENDATION_GATE.md"
)

EXPECTED_QUICK_FILL_ROW_COUNT = 64
ALLOWED_SOURCE_PACKET_STATUSES = {
    "hold_human_quick_fill_required",
    "human_confirmed_values_present_pending_safety_preflight",
}
EXPECTED_SELECTED_BLOCKERS = {
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
}

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

FORBIDDEN_VALUE_TOKENS = [
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


def load_rows() -> list[dict[str, str]]:
    with QUICK_FILL_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_boundary_violations(row: dict[str, str]) -> list[str]:
    violations: list[str] = []
    if row.get("blocker_id") not in EXPECTED_SELECTED_BLOCKERS:
        violations.append("unexpected_blocker_id")
    for flag in ["value_imported_to_workbook", "value_transferred", "template_written"]:
        if parse_bool(row.get(flag, "")):
            violations.append(f"{flag}_is_true")
    searchable_value = " ".join(
        [
            row.get("human_value_to_enter", ""),
            row.get("notes_for_human", ""),
        ]
    ).lower()
    for token in FORBIDDEN_VALUE_TOKENS:
        if token in searchable_value:
            violations.append(f"forbidden_value_token:{token}")
    return violations


def build_payload() -> dict[str, Any]:
    source_packet = json.loads(QUICK_FILL_JSON.read_text(encoding="utf-8"))
    rows = load_rows()

    boundary_violations: list[str] = []
    if source_packet.get("status") not in ALLOWED_SOURCE_PACKET_STATUSES:
        boundary_violations.append("source_packet_status_changed")
    if source_packet.get("quick_fill_imported_to_workbook") is not False:
        boundary_violations.append("source_packet_imported_to_workbook")
    if source_packet.get("values_transferred") is not False:
        boundary_violations.append("source_packet_values_transferred")
    if len(rows) != EXPECTED_QUICK_FILL_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")

    ids = [row.get("quick_fill_row_id", "") for row in rows]
    duplicate_ids = sorted([item for item, count in Counter(ids).items() if count > 1])
    if duplicate_ids:
        boundary_violations.append("duplicate_quick_fill_row_id")

    validation_rows: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    owner_lane_counts: Counter[str] = Counter()
    completed = 0
    missing = 0

    for row in rows:
        blocker_counts[row.get("blocker_id", "")] += 1
        owner_lane_counts[row.get("owner_review_lane", "")] += 1
        value_present = bool(row.get("human_value_to_enter", "").strip())
        row_violations = row_boundary_violations(row)
        if row_violations:
            boundary_violations.extend(
                f"{row.get('quick_fill_row_id', '<missing>')}:{violation}"
                for violation in row_violations
            )

        row_complete = value_present and not row_violations
        if row_complete:
            completed += 1
            row_status = "complete_pending_human_approved_workbook_import"
        else:
            missing += 1
            row_status = "missing_human_value" if not value_present else "boundary_violation"

        validation_rows.append(
            {
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "queue_item_id": row.get("queue_item_id", ""),
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "human_value_present": value_present,
                "row_complete": row_complete,
                "status": row_status,
                "target_workbook_csv": row.get("target_workbook_csv", ""),
                "target_workbook_column": row.get("target_workbook_column", ""),
                "target_json_pointer": row.get("target_json_pointer", ""),
                "value_imported_to_workbook": False,
                "value_transferred": False,
                "template_written": False,
            }
        )

    boundary_violation_count = len(boundary_violations)
    quick_fill_complete = (
        len(rows) == EXPECTED_QUICK_FILL_ROW_COUNT
        and missing == 0
        and boundary_violation_count == 0
    )
    if boundary_violation_count:
        status = "stop_boundary_violation"
    elif quick_fill_complete:
        status = "ready_for_workbook_import_pending_human_approval"
    else:
        status = "hold_human_quick_fill_required"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_packet_validator_v0_1": True,
        "validator_type": "local_quick_fill_completion_validator",
        "validator_scope": "quick_fill_human_value_completion_only_no_import_no_transfer",
        "status": status,
        "source_quick_fill_packet_json": rel(QUICK_FILL_JSON),
        "source_quick_fill_packet_csv": rel(QUICK_FILL_CSV),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py",
        "quick_fill_row_count": len(rows),
        "required_quick_fill_row_count": EXPECTED_QUICK_FILL_ROW_COUNT,
        "completed_quick_fill_row_count": completed,
        "missing_quick_fill_row_count": missing,
        "quick_fill_complete": quick_fill_complete,
        "human_input_required": not quick_fill_complete,
        "human_review_required": True,
        "ready_for_workbook_import": quick_fill_complete,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "quick_fill_values_entered_by_codex": False,
        "quick_fill_imported_to_workbook": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_quick_fill_validator": 0,
        "boundary_violation_count": boundary_violation_count,
        "boundary_violations": boundary_violations,
        "duplicate_quick_fill_row_ids": duplicate_ids,
        "blocker_validation_counts": dict(sorted(blocker_counts.items())),
        "owner_lane_validation_counts": dict(sorted(owner_lane_counts.items())),
        "validation_rows": validation_rows,
        "next_human_action": (
            "Fill missing human_value_to_enter cells in the quick-fill CSV. "
            "Do not import into the workbook until a separate human-approved "
            "workbook import step exists."
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
        "human_value_present",
        "row_complete",
        "status",
        "target_workbook_csv",
        "target_workbook_column",
        "target_json_pointer",
        "value_imported_to_workbook",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["validation_rows"]:
            writer.writerow({field: row[field] for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_packet_validator_v0_1: true",
        f"status: {payload['status']}",
        f"validator_scope: {payload['validator_scope']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"required_quick_fill_row_count: {payload['required_quick_fill_row_count']}",
        f"completed_quick_fill_row_count: {payload['completed_quick_fill_row_count']}",
        f"missing_quick_fill_row_count: {payload['missing_quick_fill_row_count']}",
        f"quick_fill_complete: {str(payload['quick_fill_complete']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"quick_fill_values_entered_by_codex: {str(payload['quick_fill_values_entered_by_codex']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_quick_fill_validator: {payload['blockers_closed_by_quick_fill_validator']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Packet Validation",
        "",
        *status_lines(payload),
        "",
        "## Purpose",
        "",
        "This validator checks whether the quick-fill packet has human-entered",
        "values. It is a local completion check only and does not import values",
        "into the workbook.",
        "",
        "## Completion State",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Quick-fill rows | {payload['quick_fill_row_count']} |",
        f"| Completed rows | {payload['completed_quick_fill_row_count']} |",
        f"| Missing rows | {payload['missing_quick_fill_row_count']} |",
        f"| Boundary violations | {payload['boundary_violation_count']} |",
        "",
        "## Boundary",
        "",
        "No values were entered by Codex. No values were imported into the",
        "workbook. No values were transferred into templates. No human-filled",
        "templates were written. No validators were run on real input. No evidence",
        "was collected and no blocker was closed.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Packet Validation Boundary Audit",
        "",
        *status_lines(payload),
        "",
        "This validator is local and read-only with respect to commercial evidence",
        "execution. It checks quick-fill completion state only. It does not import",
        "values, transfer values, collect evidence, execute builders, contact",
        "customers or vendors, close blockers, launch product, or claim production",
        "readiness.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Quick-Fill Packet Validator v0.1",
        "",
        *status_lines(payload),
        "",
        "## Role",
        "",
        "This document records the local completion validator for the commercial",
        "sprint quick-fill packet. It supports human input coordination without",
        "changing SAEE product behavior.",
        "",
        "## Boundary",
        "",
        "The validator does not fill values, import values, transfer values, write",
        "human-filled templates, run validators on real input, collect evidence,",
        "execute builders, contact customers or vendors, close blockers, launch",
        "product, or claim production readiness.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Quick-Fill Packet Validator Recommendation Gate",
        "",
        "commercial_sprint_human_input_quick_fill_packet_validator_v0_1: true",
        "answer: recommend",
        "recommend_for_completion_validation: true",
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
        "This validator is recommendable as a local coordination check because it",
        "shows whether the human quick-fill sheet is complete while preserving all",
        "execution and evidence boundaries.",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_PACKET_VALIDATOR: PASS "
        f"status={payload['status']} "
        f"completed_quick_fill_row_count={payload['completed_quick_fill_row_count']} "
        f"missing_quick_fill_row_count={payload['missing_quick_fill_row_count']} "
        f"ready_for_workbook_import={str(payload['ready_for_workbook_import']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
