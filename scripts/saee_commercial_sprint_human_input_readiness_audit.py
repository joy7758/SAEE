#!/usr/bin/env python3
"""Audit human quick-fill readiness without filling values.

This audit checks whether each current commercial sprint quick-fill row has
enough local context for a human to fill it: source prompt, guidance, worksheet
row, target workbook mapping, and target JSON pointer. It does not fill values,
import values, transfer templates, run validators on real input, collect
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
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

QUICK_FILL_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.local.json"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
GUIDANCE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.local.json"
WORKSHEET_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_human_worksheet.local.json"
ACTIVE_BOARD_JSON = SPRINT_DIR / "commercial_sprint_active_human_input_board.local.json"
NEXT_ACTION_JSON = COMMERCIAL_DIR / "commercial_next_action_summary/commercial_next_action_summary.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT_RECOMMENDATION_GATE.md"


EXPECTED_ROW_COUNT = 64
REQUIRED_QUICK_FILL_FIELDS = [
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
    "target_workbook_csv",
    "target_workbook_column",
    "target_json_pointer",
]


FALSE_FLAGS = {
    "human_values_filled_by_codex": False,
    "quick_fill_values_entered_by_codex": False,
    "workbook_import_authorized": False,
    "workbook_import_performed": False,
    "workbook_written": False,
    "validators_run_on_real_input": False,
    "values_transferred": False,
    "human_filled_templates_written": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "evidence_builder_executed": False,
    "blocker_closure_authorized": False,
    "blockers_closed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "vendor_contacted": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "development_permission_granted": False,
    "task_candidates_executed": False,
    "payment_collected": False,
    "revenue_validated": False,
    "production_ready_claim": False,
    "customer_validation_claim": False,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT: FAIL {path} must be an object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_map(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row.get(key)): row for row in rows}


def build_payload() -> dict[str, Any]:
    quick_fill = read_json(QUICK_FILL_JSON)
    guidance = read_json(GUIDANCE_JSON)
    worksheet = read_json(WORKSHEET_JSON)
    active_board = read_json(ACTIVE_BOARD_JSON)
    next_action = read_json(NEXT_ACTION_JSON)
    rows = read_csv(QUICK_FILL_CSV)

    guidance_by_id = row_map(guidance.get("guidance_rows", []), "quick_fill_row_id")
    worksheet_by_id = row_map(worksheet.get("worksheet_rows", []), "quick_fill_row_id")
    blocker_counts: Counter[str] = Counter()
    readiness_rows: list[dict[str, Any]] = []

    for row in rows:
        row_id = row.get("quick_fill_row_id", "")
        blocker_counts[row.get("blocker_id", "")] += 1
        prompt_path = ROOT / row.get("human_fill_prompt", "")
        required_fields_present = all(row.get(field, "") != "" for field in REQUIRED_QUICK_FILL_FIELDS if field != "human_value_to_enter")
        human_value_blank = row.get("human_value_to_enter", "") == ""
        guidance_present = row_id in guidance_by_id
        worksheet_present = row_id in worksheet_by_id
        target_mapping_present = (
            row.get("target_workbook_csv", "") != ""
            and row.get("target_workbook_column", "") != ""
            and row.get("target_json_pointer", "") != ""
        )
        prompt_exists = prompt_path.exists()
        row_ready = (
            required_fields_present
            and human_value_blank
            and guidance_present
            and worksheet_present
            and target_mapping_present
            and prompt_exists
        )
        readiness_rows.append(
            {
                "quick_fill_row_id": row_id,
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "input_kind": row.get("input_kind", ""),
                "required_fields_present": required_fields_present,
                "human_value_blank": human_value_blank,
                "prompt_path": row.get("human_fill_prompt", ""),
                "prompt_path_exists": prompt_exists,
                "guidance_row_present": guidance_present,
                "worksheet_row_present": worksheet_present,
                "target_mapping_present": target_mapping_present,
                "ready_for_human_input": row_ready,
            }
        )

    ready_count = sum(1 for row in readiness_rows if row["ready_for_human_input"])
    missing_context_count = len(readiness_rows) - ready_count
    value_prefilled_count = sum(1 for row in readiness_rows if not row["human_value_blank"])
    source_statuses = {
        "quick_fill_packet": quick_fill.get("status"),
        "guidance": guidance.get("status"),
        "worksheet": worksheet.get("status"),
        "active_board": active_board.get("status"),
        "next_action_summary": next_action.get("status"),
    }
    status = (
        "pass_human_input_surfaces_ready_hold_values_missing"
        if ready_count == EXPECTED_ROW_COUNT and value_prefilled_count == 0
        else "hold_human_input_surface_gaps"
    )
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_readiness_audit_v0_1": True,
        "audit_type": "local_human_input_surface_readiness_audit",
        "audit_scope": "quick_fill_context_completeness_only_no_values_no_import",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_readiness_audit.py",
        "source_files": {
            "quick_fill_json": rel(QUICK_FILL_JSON),
            "quick_fill_csv": rel(QUICK_FILL_CSV),
            "guidance_json": rel(GUIDANCE_JSON),
            "worksheet_json": rel(WORKSHEET_JSON),
            "active_board_json": rel(ACTIVE_BOARD_JSON),
            "next_action_json": rel(NEXT_ACTION_JSON),
        },
        "source_statuses": source_statuses,
        "quick_fill_row_count": len(rows),
        "expected_quick_fill_row_count": EXPECTED_ROW_COUNT,
        "ready_for_human_input_row_count": ready_count,
        "missing_context_row_count": missing_context_count,
        "value_prefilled_count": value_prefilled_count,
        "blank_value_row_count": sum(1 for row in readiness_rows if row["human_value_blank"]),
        "selected_blocker_count": len(blocker_counts),
        "selected_blocker_ids": sorted(blocker_counts),
        "blocker_row_counts": dict(sorted(blocker_counts.items())),
        "human_input_required": True,
        "human_review_required": True,
        "ready_for_human_fill": ready_count == EXPECTED_ROW_COUNT,
        "ready_for_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "blockers_closed_by_audit": 0,
        "rows": readiness_rows,
        "next_human_action": (
            "Fill human_value_to_enter in the quick-fill CSV using the guidance and worksheet, "
            "then rerun safety preflight and the quick-fill validator. This audit does not "
            "authorize workbook import, validator execution on real input, evidence collection, "
            "or blocker closure."
        ),
        **FALSE_FLAGS,
    }
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "quick_fill_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "required_fields_present",
        "human_value_blank",
        "prompt_path_exists",
        "guidance_row_present",
        "worksheet_row_present",
        "target_mapping_present",
        "ready_for_human_input",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({field: row[field] for field in fields})


def lower_bool(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def write_markdown(payload: dict[str, Any]) -> None:
    status_lines = [
        "commercial_sprint_human_input_readiness_audit_v0_1: true",
        f"audit_scope: {payload['audit_scope']}",
        f"status: {payload['status']}",
        "commercial_status: hold",
        "production_launch_status: hold",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"ready_for_human_input_row_count: {payload['ready_for_human_input_row_count']}",
        f"missing_context_row_count: {payload['missing_context_row_count']}",
        f"value_prefilled_count: {payload['value_prefilled_count']}",
        f"blank_value_row_count: {payload['blank_value_row_count']}",
        f"blockers_closed_by_audit: {payload['blockers_closed_by_audit']}",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    source_lines = "\n".join(
        f"- {name}: `{status}`" for name, status in sorted(payload["source_statuses"].items())
    )
    blocker_lines = "\n".join(
        f"- `{blocker}`: {count} rows" for blocker, count in payload["blocker_row_counts"].items()
    )
    OUT_MD.write_text(
        "\n".join(
            [
                "# Commercial Sprint Human Input Readiness Audit",
                "",
                *status_lines,
                "",
                "## Purpose",
                "",
                "This audit checks whether the current 64-row quick-fill surface is ready for a human to fill. It verifies prompt paths, guidance rows, worksheet rows, target mappings, and blank human-value fields.",
                "",
                "## Source Statuses",
                "",
                source_lines,
                "",
                "## Blocker Row Counts",
                "",
                blocker_lines,
                "",
                "## Boundary",
                "",
                "This audit does not fill values, import values, transfer templates, run validators on real input, collect evidence, execute builders, contact anyone, close blockers, launch product, claim external validation, claim customer validation, or claim production readiness.",
                "",
                "## Next Human Action",
                "",
                payload["next_human_action"],
                "",
            ]
        ),
        encoding="utf-8",
    )

    OUT_BOUNDARY.write_text(
        """# Commercial Sprint Human Input Readiness Audit Boundary

commercial_sprint_human_input_readiness_audit_v0_1: true
audit_scope: quick_fill_context_completeness_only_no_values_no_import
status: boundary_safe
human_values_filled_by_codex: false
workbook_import_authorized: false
workbook_import_performed: false
validators_run_on_real_input: false
values_transferred: false
human_filled_templates_written: false
evidence_collection_authorized: false
execution_authorized: false
blocker_closure_authorized: false
blockers_closed_by_audit: 0
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
customer_contacted: false
external_calls_made: false
external_model_api_called: false

This is a local readiness audit only. It reads quick-fill context surfaces and
writes status artifacts. It does not collect or infer real human evidence.
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# Commercial Sprint Human Input Readiness Audit v0.1

commercial_sprint_human_input_readiness_audit_v0_1: true
audit_type: local_human_input_surface_readiness_audit
audit_scope: quick_fill_context_completeness_only_no_values_no_import
status: pass_human_input_surfaces_ready_hold_values_missing
commercial_status: hold
production_launch_status: hold
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Recommendation Gate Answer

recommend_for_human_quick_fill_readiness: true
recommend_for_workbook_import: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Boundary

Use this audit to confirm that the human quick-fill surface is complete enough
for a human reviewer to fill. Do not treat it as evidence collection, workbook
import approval, validator execution approval, blocker closure, customer
validation, launch, or production readiness.
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Commercial Sprint Human Input Readiness Audit Recommendation Gate

answer: recommend_for_human_quick_fill_readiness_only

recommend_for_human_quick_fill_readiness: true
recommend_for_workbook_import: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The audit is useful when the next commercial step is manual quick-fill input. It
checks that every row has enough local context for a human reviewer to fill
without Codex inventing values.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
blockers_closed_by_audit: 0

This gate does not authorize workbook import, validator execution on real input,
evidence collection, blocker closure, launch, customer-validation claims, or
production-readiness claims.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(payload)
    write_markdown(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_READINESS_AUDIT: PASS "
        f"status={payload['status']} ready_rows={payload['ready_for_human_input_row_count']} "
        "values_filled_by_codex=false production_ready=false"
    )


if __name__ == "__main__":
    main()
