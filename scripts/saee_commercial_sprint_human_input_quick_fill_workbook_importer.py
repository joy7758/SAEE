#!/usr/bin/env python3
"""Controlled quick-fill to workbook importer for the commercial sprint.

Default mode is dry-run only. It reads the quick-fill CSV and workbook CSV,
checks whether rows are importable, and writes only importer status artifacts.

Actual workbook output is written only when both `--apply` and
`--confirm-human-approved-import` are provided and every import row has a
human-entered value. This script does not infer values, transfer values into
templates, run validators on real input, collect evidence, execute builders,
contact anyone, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
DEFAULT_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
DEFAULT_WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
DEFAULT_IMPORTED_WORKBOOK_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_workbook.imported_from_quick_fill.local.csv"
)
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER_RECOMMENDATION_GATE.md"
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
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def required_value_shape(input_kind: str) -> str:
    if input_kind == "metadata_field":
        return "human-reviewed metadata value"
    if input_kind == "evidence_review_key":
        return "human evidence review outcome"
    if input_kind == "support_contact_bridge_field":
        return "human-approved support-contact bridge value"
    return "human-reviewed text value"


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], list[str], list[dict[str, str]]]:
    quick_fill_csv = Path(args.quick_fill_csv)
    workbook_csv = Path(args.workbook_csv)
    output_workbook_csv = Path(args.output_workbook_csv)
    quick_fields, quick_rows = load_csv(quick_fill_csv)
    workbook_fields, workbook_rows = load_csv(workbook_csv)
    workbook_by_id = {row["workbook_row_id"]: row for row in workbook_rows}

    boundary_violations: list[str] = []
    import_rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, str]] = []
    blocker_counts: Counter[str] = Counter()
    value_present_count = 0
    import_ready_count = 0

    if len(quick_rows) != EXPECTED_IMPORT_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")
    if len(workbook_rows) != EXPECTED_WORKBOOK_ROW_COUNT:
        boundary_violations.append("unexpected_workbook_row_count")
    required_quick_fields = {
        "quick_fill_row_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "human_value_to_enter",
        "target_workbook_csv",
        "target_workbook_column",
        "value_imported_to_workbook",
        "value_transferred",
        "template_written",
    }
    missing_quick_fields = sorted(required_quick_fields - set(quick_fields))
    if missing_quick_fields:
        boundary_violations.append("missing_quick_fill_fields")
    if EXPECTED_TARGET_COLUMN not in workbook_fields:
        boundary_violations.append("missing_target_workbook_column")

    imported_workbook_rows = [dict(row) for row in workbook_rows]
    imported_workbook_by_id = {row["workbook_row_id"]: row for row in imported_workbook_rows}

    for quick_row in quick_rows:
        workbook_row_id = quick_row.get("workbook_row_id", "")
        workbook_row = workbook_by_id.get(workbook_row_id)
        blocker_counts[quick_row.get("blocker_id", "")] += 1
        value = quick_row.get("human_value_to_enter", "").strip()
        value_present = bool(value)
        if value_present:
            value_present_count += 1

        mapping_resolved = workbook_row is not None
        reason = "resolved" if mapping_resolved else "missing_workbook_row"
        if mapping_resolved:
            for field in ["blocker_id", "owner_review_lane", "input_group", "input_key", "input_kind"]:
                if quick_row.get(field) != workbook_row.get(field):
                    mapping_resolved = False
                    reason = f"mismatched_{field}"
                    break
        if not mapping_resolved:
            unresolved.append(
                {
                    "quick_fill_row_id": quick_row.get("quick_fill_row_id", ""),
                    "workbook_row_id": workbook_row_id,
                    "reason": reason,
                }
            )

        target_csv_ok = quick_row.get("target_workbook_csv") == rel(workbook_csv)
        target_column_ok = quick_row.get("target_workbook_column") == EXPECTED_TARGET_COLUMN
        import_flags_clear = not any(
            parse_bool(quick_row.get(flag, ""))
            for flag in ["value_imported_to_workbook", "value_transferred", "template_written"]
        )
        import_ready = (
            mapping_resolved
            and target_csv_ok
            and target_column_ok
            and import_flags_clear
            and value_present
        )
        if import_ready:
            import_ready_count += 1
        if args.apply and args.confirm_human_approved_import and import_ready:
            target_row = imported_workbook_by_id[workbook_row_id]
            target_row[EXPECTED_TARGET_COLUMN] = value
            target_row["status"] = "imported_from_quick_fill_pending_validator"
            target_row["notes"] = (
                (target_row.get("notes", "") + " ").strip()
                + " Imported from human-filled quick-fill CSV by explicit human-approved importer."
            ).strip()

        if import_ready:
            row_status = "ready_for_apply"
        elif not value_present:
            row_status = "hold_missing_human_value"
        elif not import_flags_clear:
            row_status = "stop_existing_import_or_transfer_flag"
        else:
            row_status = "stop_mapping_or_target_issue"

        import_rows.append(
            {
                "quick_fill_row_id": quick_row.get("quick_fill_row_id", ""),
                "workbook_row_id": workbook_row_id,
                "blocker_id": quick_row.get("blocker_id", ""),
                "owner_review_lane": quick_row.get("owner_review_lane", ""),
                "input_group": quick_row.get("input_group", ""),
                "input_key": quick_row.get("input_key", ""),
                "input_kind": quick_row.get("input_kind", ""),
                "expected_value_shape": required_value_shape(quick_row.get("input_kind", "")),
                "mapping_resolved": mapping_resolved,
                "target_csv_ok": target_csv_ok,
                "target_column_ok": target_column_ok,
                "human_value_present": value_present,
                "import_ready": import_ready,
                "row_status": row_status,
                "value_imported_to_workbook": False,
                "value_transferred": False,
                "template_written": False,
            }
        )

    missing_value_count = len(import_rows) - value_present_count
    unresolved_count = len(import_rows) - sum(1 for row in import_rows if row["mapping_resolved"])
    all_import_mappings_resolved = unresolved_count == 0 and len(import_rows) == EXPECTED_IMPORT_ROW_COUNT
    apply_authorized = bool(args.apply and args.confirm_human_approved_import)
    apply_preconditions_met = (
        apply_authorized
        and not boundary_violations
        and all_import_mappings_resolved
        and import_ready_count == EXPECTED_IMPORT_ROW_COUNT
    )
    workbook_written = False
    if args.apply and not args.confirm_human_approved_import:
        boundary_violations.append("apply_requested_without_human_confirmation")
    if args.apply and args.confirm_human_approved_import and not apply_preconditions_met:
        boundary_violations.append("apply_requested_without_complete_import_readiness")
    if apply_preconditions_met:
        write_csv(output_workbook_csv, workbook_fields, imported_workbook_rows)
        workbook_written = True

    if boundary_violations:
        status = "stop_boundary_or_apply_precondition_violation"
    elif import_ready_count == EXPECTED_IMPORT_ROW_COUNT:
        status = "ready_for_apply_pending_explicit_human_command"
    else:
        status = "hold_human_quick_fill_required"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_workbook_importer_v0_1": True,
        "importer_type": "controlled_quick_fill_to_workbook_importer",
        "importer_scope": "quick_fill_to_workbook_only_no_template_transfer_no_evidence",
        "status": status,
        "execution_mode": "apply_write_local_workbook_output" if workbook_written else "dry_run_no_write",
        "source_quick_fill_csv": rel(quick_fill_csv),
        "source_workbook_csv": rel(workbook_csv),
        "output_workbook_csv": rel(output_workbook_csv),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py",
        "quick_fill_row_count": len(quick_rows),
        "workbook_row_count": len(workbook_rows),
        "import_candidate_row_count": len(import_rows),
        "resolved_import_mapping_row_count": sum(1 for row in import_rows if row["mapping_resolved"]),
        "unresolved_import_mapping_row_count": unresolved_count,
        "all_import_mappings_resolved": all_import_mappings_resolved,
        "value_present_row_count": value_present_count,
        "missing_value_row_count": missing_value_count,
        "import_ready_row_count": import_ready_count,
        "apply_requested": bool(args.apply),
        "human_import_confirmation_provided": bool(args.confirm_human_approved_import),
        "apply_preconditions_met": apply_preconditions_met,
        "apply_performed": workbook_written,
        "quick_fill_imported_to_workbook": workbook_written,
        "workbook_import_performed": workbook_written,
        "workbook_written": workbook_written,
        "ready_for_workbook_import": import_ready_count == EXPECTED_IMPORT_ROW_COUNT
        and all_import_mappings_resolved
        and not boundary_violations,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": workbook_written,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_importer": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "unresolved_import_mappings": unresolved,
        "blocker_import_counts": dict(sorted(blocker_counts.items())),
        "import_rows": import_rows,
        "next_human_action": (
            "Fill human_value_to_enter in the quick-fill CSV, rerun dry-run, "
            "then use --apply --confirm-human-approved-import only after human approval."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload, workbook_fields, imported_workbook_rows


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = payload["import_rows"]
    csv_fields = [
        "quick_fill_row_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "expected_value_shape",
        "mapping_resolved",
        "target_csv_ok",
        "target_column_ok",
        "human_value_present",
        "import_ready",
        "row_status",
        "value_imported_to_workbook",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in csv_fields})

    status_lines = [
        "commercial_sprint_human_input_quick_fill_workbook_importer_v0_1: true",
        f"status: {payload['status']}",
        f"execution_mode: {payload['execution_mode']}",
        f"importer_scope: {payload['importer_scope']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"import_candidate_row_count: {payload['import_candidate_row_count']}",
        f"resolved_import_mapping_row_count: {payload['resolved_import_mapping_row_count']}",
        f"unresolved_import_mapping_row_count: {payload['unresolved_import_mapping_row_count']}",
        f"value_present_row_count: {payload['value_present_row_count']}",
        f"missing_value_row_count: {payload['missing_value_row_count']}",
        f"import_ready_row_count: {payload['import_ready_row_count']}",
        f"apply_requested: {str(payload['apply_requested']).lower()}",
        f"human_import_confirmation_provided: {str(payload['human_import_confirmation_provided']).lower()}",
        f"apply_performed: {str(payload['apply_performed']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        f"workbook_written: {str(payload['workbook_written']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_importer: {payload['blockers_closed_by_importer']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]
    status_block = "\n".join(status_lines)

    OUT_MD.write_text(
        "# Commercial Sprint Human Input Quick-Fill Workbook Importer\n\n"
        f"{status_block}\n\n"
        "## Purpose\n\n"
        "This local importer checks whether human-filled quick-fill values can be "
        "imported into the commercial sprint workbook. Default execution is dry-run "
        "only and writes no workbook output.\n\n"
        "## Apply Boundary\n\n"
        "Workbook output is written only when `--apply` and "
        "`--confirm-human-approved-import` are both provided and every import row is "
        "complete and mapped. Apply mode still does not transfer values into "
        "templates, run validators, collect evidence, execute builders, close "
        "blockers, contact anyone, launch product, or claim production readiness.\n\n"
        "## Next Human Action\n\n"
        f"{payload['next_human_action']}\n",
        encoding="utf-8",
    )

    OUT_BOUNDARY.write_text(
        "# Commercial Sprint Human Input Quick-Fill Workbook Importer Boundary Audit\n\n"
        f"{status_block}\n\n"
        "- Default mode wrote no workbook output.\n"
        "- No values were inferred or entered by Codex.\n"
        "- No template transfer was performed.\n"
        "- No validator was run on real input.\n"
        "- No evidence was collected.\n"
        "- No blocker was closed.\n"
        "- No runtime, backend, kernel, API schema, or private core was modified.\n",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Workbook Importer v0.1\n\n"
        f"{status_block}\n\n"
        "This is a controlled local importer for human-filled quick-fill values. "
        "It is recommendable only as a human-approved workbook-import utility and "
        "not as evidence collection, blocker closure, production readiness, or "
        "customer validation.\n",
        encoding="utf-8",
    )

    GATE.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Workbook Importer Recommendation Gate\n\n"
        "commercial_sprint_human_input_quick_fill_workbook_importer_v0_1: true\n"
        "answer: conditional\n"
        "recommend_for_import_readiness_check: true\n"
        "recommend_for_human_approved_workbook_import: true\n"
        "recommend_for_unapproved_import: false\n"
        "recommend_for_value_inference: false\n"
        "recommend_for_value_suggestion: false\n"
        "recommend_for_template_transfer: false\n"
        "recommend_for_real_evidence: false\n"
        "recommend_for_evidence_collection: false\n"
        "recommend_for_automatic_execution: false\n"
        "recommend_for_blocker_closure: false\n"
        "recommend_for_product_launch: false\n"
        "recommend_for_production_readiness_claim: false\n\n"
        "## Reason\n\n"
        "The importer is conditionally recommendable only after a human has filled "
        "the quick-fill values and explicitly approved workbook import. It is not "
        "recommended for autonomous execution or blocker closure.\n\n"
        "## Status\n\n"
        f"{status_block}\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick-fill-csv", default=str(DEFAULT_QUICK_FILL_CSV))
    parser.add_argument("--workbook-csv", default=str(DEFAULT_WORKBOOK_CSV))
    parser.add_argument("--output-workbook-csv", default=str(DEFAULT_IMPORTED_WORKBOOK_CSV))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-human-approved-import", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload, _, _ = build_payload(args)
    write_artifacts(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_WORKBOOK_IMPORTER: PASS "
        f"status={payload['status']} "
        f"execution_mode={payload['execution_mode']} "
        f"import_ready_row_count={payload['import_ready_row_count']} "
        f"apply_performed={str(payload['apply_performed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0 if not payload["boundary_violations"] or not args.apply else 1


if __name__ == "__main__":
    raise SystemExit(main())
