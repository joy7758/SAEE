#!/usr/bin/env python3
"""End-to-end dry run for the 10-row quick-fill review-batch input template.

This script connects the review-batch input-template importer and the selected
batch validator without overwriting the official source quick-fill CSV. It
checks whether a human-filled 10-row template would be ready to become a local
quick-fill output and, when ready, validates a temporary preview quick-fill CSV.

It records only status, counts, and boundary results. It does not persist raw
human values, overwrite source quick-fill data, write workbooks, transfer
templates, run validators on official real input, collect evidence, contact
anyone, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"

DEFAULT_INPUT_TEMPLATE_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
DEFAULT_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json"
)
OUT_MD = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.md"
)
OUT_CSV = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.csv"
)
OUT_BOUNDARY = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_boundary_audit.md"
)
TOP_DOC = (
    COMMERCIAL_DIR
    / "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN_RECOMMENDATION_GATE.md"
)

EXPECTED_TEMPLATE_ROW_COUNT = 10
EXPECTED_SOURCE_ROW_COUNT = 64
SUPERSEDED_REVIEW_BATCH_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"

FALSE_FLAGS = [
    "source_quick_fill_packet_modified",
    "local_quick_fill_output_written",
    "batch_values_applied_to_source",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_official_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "ready_for_workbook_import",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "blockers_closed",
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
    "production_ready_claim",
    "customer_validation_claim",
]


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


IMPORTER = load_module(
    SCRIPTS_DIR / "saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py",
    "review_batch_input_template_importer",
)
VALIDATOR = load_module(
    SCRIPTS_DIR / "saee_commercial_sprint_human_input_quick_fill_review_batch_validator.py",
    "review_batch_validator",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-template-csv", default=str(DEFAULT_INPUT_TEMPLATE_CSV))
    parser.add_argument("--quick-fill-csv", default=str(DEFAULT_QUICK_FILL_CSV))
    return parser.parse_args()


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_preview_quick_fill(
    input_template_csv: Path, quick_fill_csv: Path, output_csv: Path
) -> None:
    source_fields, source_rows = load_csv(quick_fill_csv)
    _, template_rows = load_csv(input_template_csv)
    template_by_id = {row["quick_fill_row_id"]: row for row in template_rows}
    preview_rows = [dict(row) for row in source_rows]
    for row in preview_rows:
        template_row = template_by_id.get(row.get("quick_fill_row_id", ""))
        if not template_row:
            continue
        row["human_value_to_enter"] = template_row.get("human_value_to_enter", "").strip()
        row["notes_for_human"] = template_row.get("notes_for_human", "").strip()
        if row["human_value_to_enter"]:
            row["quick_fill_status"] = "human_filled_from_review_batch_template_pending_validator"
    write_csv(output_csv, source_fields, preview_rows)


def build_payload(input_template_csv: Path, quick_fill_csv: Path) -> dict[str, Any]:
    importer_args = SimpleNamespace(
        input_template_csv=str(input_template_csv),
        quick_fill_csv=str(quick_fill_csv),
        output_quick_fill_csv=str(SPRINT_DIR / "__not_written_review_batch_template_e2e_preview.csv"),
        apply=False,
        confirm_human_approved_template_import=False,
    )
    importer_payload, _, _ = IMPORTER.build_payload(importer_args)

    boundary_violations = list(importer_payload.get("boundary_violations", []))
    importer_row_stop_count = sum(
        1
        for row in importer_payload.get("import_rows", [])
        if str(row.get("row_status", "")).startswith("stop_")
    )
    if str(importer_payload.get("status", "")).startswith("stop_"):
        boundary_violations.append("importer_stop_status")
    if importer_row_stop_count:
        boundary_violations.append("importer_row_stop_status")
    validator_status = "not_run_template_values_missing"
    validator_passed = False
    validator_completed_batch_value_row_count = 0
    validator_missing_batch_value_row_count = EXPECTED_TEMPLATE_ROW_COUNT
    validator_batch_quality_issue_count = 0
    validator_boundary_violation_count = 0
    validator_status_counts: dict[str, int] = {}
    preview_validator_executed = False
    review_batch_template_superseded = (
        importer_payload.get("status") == SUPERSEDED_REVIEW_BATCH_STATUS
    )
    if review_batch_template_superseded:
        validator_status = "not_run_template_route_superseded"
        validator_missing_batch_value_row_count = 0

    if importer_payload.get("status") == "ready_for_local_quick_fill_output_pending_explicit_human_command":
        with tempfile.TemporaryDirectory() as tmp:
            preview_csv = Path(tmp) / "review_batch_template_preview_quick_fill.csv"
            build_preview_quick_fill(input_template_csv, quick_fill_csv, preview_csv)
            validator_payload = VALIDATOR.build_payload(preview_csv)
        preview_validator_executed = True
        validator_status = validator_payload["status"]
        validator_passed = bool(validator_payload["batch_validator_passed"])
        validator_completed_batch_value_row_count = int(
            validator_payload["completed_batch_value_row_count"]
        )
        validator_missing_batch_value_row_count = int(
            validator_payload["missing_batch_value_row_count"]
        )
        validator_batch_quality_issue_count = int(validator_payload["batch_quality_issue_count"])
        validator_boundary_violation_count = int(validator_payload["boundary_violation_count"])
        validator_status_counts = validator_payload.get("batch_validation_status_counts", {})
        boundary_violations.extend(
            f"preview_validator:{issue}" for issue in validator_payload.get("boundary_violations", [])
        )

    if review_batch_template_superseded:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    elif boundary_violations:
        status = "stop_template_e2e_boundary_or_validator_issue"
    elif importer_payload.get("missing_template_value_row_count", 0):
        status = "hold_template_human_values_required"
    elif validator_passed:
        status = "pass_template_values_ready_for_local_output_and_batch_validation"
    elif preview_validator_executed:
        status = "hold_template_values_need_batch_quality_review"
    else:
        status = "hold_template_e2e_not_ready"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1": True,
        "dry_run_type": "review_batch_template_to_preview_quick_fill_to_batch_validator",
        "dry_run_scope": "local_preview_only_no_source_overwrite_no_persistent_output_no_workbook_import",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "source_input_template_csv": rel(input_template_csv),
        "source_quick_fill_csv": rel(quick_fill_csv),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
        "template_row_count": importer_payload["template_row_count"],
        "source_quick_fill_row_count": importer_payload["source_quick_fill_row_count"],
        "template_value_present_row_count": importer_payload["template_value_present_row_count"],
        "missing_template_value_row_count": importer_payload["missing_template_value_row_count"],
        "review_batch_template_superseded": review_batch_template_superseded,
        "ready_for_workbook_import_approval_review": review_batch_template_superseded,
        "would_import_row_count": importer_payload["would_import_row_count"],
        "importer_status": importer_payload["status"],
        "importer_row_stop_count": importer_row_stop_count,
        "importer_apply_performed": False,
        "preview_validator_executed": preview_validator_executed,
        "preview_validator_status": validator_status,
        "preview_validator_passed": validator_passed,
        "preview_validator_completed_batch_value_row_count": validator_completed_batch_value_row_count,
        "preview_validator_missing_batch_value_row_count": validator_missing_batch_value_row_count,
        "preview_validator_batch_quality_issue_count": validator_batch_quality_issue_count,
        "preview_validator_boundary_violation_count": validator_boundary_violation_count,
        "preview_validator_status_counts": validator_status_counts,
        "source_quick_fill_packet_modified": False,
        "persistent_preview_quick_fill_written": False,
        "local_quick_fill_output_written": False,
        "batch_values_applied_to_source": False,
        "quick_fill_imported_to_workbook": False,
        "workbook_import_performed": False,
        "validators_run_on_official_real_input": False,
        "raw_values_recorded_in_status_artifacts": False,
        "human_values_generated_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "blockers_closed_by_dry_run": 0,
        "boundary_violation_count": len(sorted(set(boundary_violations))),
        "boundary_violations": sorted(set(boundary_violations)),
        "row_summaries": [
            {
                "quick_fill_row_id": row["quick_fill_row_id"],
                "mapping_resolved": row["mapping_resolved"],
                "human_template_value_present": row["human_template_value_present"],
                "local_output_ready": row["local_output_ready"],
                "row_status": row["row_status"],
                "template_value_issue_count": row["template_value_issue_count"],
            }
            for row in importer_payload.get("import_rows", [])
        ],
        "next_human_action": (
            "Review the workbook import approval request packet. The old 10-row template E2E dry-run route is superseded; do not write local output, run validators on real input, collect evidence, or close blockers without separate approval."
            if review_batch_template_superseded
            else "Fill the 10-row template, rerun this dry-run, and only after it "
            "passes request a separate explicit local-output apply/import action."
        ),
    }
    for flag in FALSE_FLAGS:
        if flag not in payload:
            payload[flag] = False
    return payload


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"commercial_status: {payload['commercial_status']}",
        f"production_launch_status: {payload['production_launch_status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"template_row_count: {payload['template_row_count']}",
        f"source_quick_fill_row_count: {payload['source_quick_fill_row_count']}",
        f"template_value_present_row_count: {payload['template_value_present_row_count']}",
        f"missing_template_value_row_count: {payload['missing_template_value_row_count']}",
        f"review_batch_template_superseded: {str(payload['review_batch_template_superseded']).lower()}",
        "ready_for_workbook_import_approval_review: "
        f"{str(payload['ready_for_workbook_import_approval_review']).lower()}",
        f"would_import_row_count: {payload['would_import_row_count']}",
        f"importer_status: {payload['importer_status']}",
        f"importer_apply_performed: {str(payload['importer_apply_performed']).lower()}",
        f"preview_validator_executed: {str(payload['preview_validator_executed']).lower()}",
        f"preview_validator_status: {payload['preview_validator_status']}",
        f"preview_validator_passed: {str(payload['preview_validator_passed']).lower()}",
        "preview_validator_completed_batch_value_row_count: "
        f"{payload['preview_validator_completed_batch_value_row_count']}",
        "preview_validator_missing_batch_value_row_count: "
        f"{payload['preview_validator_missing_batch_value_row_count']}",
        f"source_quick_fill_packet_modified: {str(payload['source_quick_fill_packet_modified']).lower()}",
        f"persistent_preview_quick_fill_written: {str(payload['persistent_preview_quick_fill_written']).lower()}",
        f"local_quick_fill_output_written: {str(payload['local_quick_fill_output_written']).lower()}",
        f"batch_values_applied_to_source: {str(payload['batch_values_applied_to_source']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        "validators_run_on_official_real_input: "
        f"{str(payload['validators_run_on_official_real_input']).lower()}",
        "raw_values_recorded_in_status_artifacts: "
        f"{str(payload['raw_values_recorded_in_status_artifacts']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"blockers_closed_by_dry_run: {payload['blockers_closed_by_dry_run']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fields = [
        "quick_fill_row_id",
        "mapping_resolved",
        "human_template_value_present",
        "local_output_ready",
        "row_status",
        "template_value_issue_count",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["row_summaries"]:
            writer.writerow({field: row.get(field, "") for field in fields})

    status_block = "\n".join(status_lines(payload))
    OUT_MD.write_text(
        "# Commercial Sprint Human Input Quick-Fill Review Batch Template E2E Dry Run\n\n"
        f"{status_block}\n\n"
        "## Purpose\n\n"
        "This local dry run checks the 10-row input template through the importer "
        "and, when values are complete, through a temporary preview quick-fill CSV "
        "using the existing selected-batch validator.\n\n"
        "## Boundary\n\n"
        "No official source quick-fill CSV is overwritten, no persistent preview "
        "CSV is written, no workbook import is performed, no validator is run on "
        "official real input, no evidence is collected, no blocker is closed, and "
        "no production-readiness or customer-validation claim is made.\n\n"
        "## Next Human Action\n\n"
        f"{payload['next_human_action']}\n",
        encoding="utf-8",
    )

    OUT_BOUNDARY.write_text(
        "# Commercial Sprint Human Input Quick-Fill Review Batch Template E2E Dry Run Boundary Audit\n\n"
        f"{status_block}\n\n"
        "- Dry run only.\n"
        "- No source quick-fill overwrite.\n"
        "- No persistent preview quick-fill output.\n"
        "- No workbook import.\n"
        "- No template transfer.\n"
        "- No official real-input validator execution.\n"
        "- No raw values recorded in status artifacts.\n"
        "- No evidence collection.\n"
        "- No blocker closure.\n"
        "- No runtime, backend, kernel, API schema, or private core modification.\n",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Review Batch Template E2E Dry Run v0.1\n\n"
        f"{status_block}\n\n"
        "This is a local-only dry-run readiness surface for human-filled 10-row "
        "review-batch templates. It is not a workbook import, real evidence "
        "collection, blocker closure, product launch, or production-readiness claim.\n",
        encoding="utf-8",
    )

    GATE.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Review Batch Template E2E Dry Run Recommendation Gate\n\n"
        "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_v0_1: true\n"
        "answer: conditional\n"
        "recommend_for_template_e2e_dry_run: true\n"
        "recommend_for_source_quick_fill_overwrite: false\n"
        "recommend_for_workbook_import: false\n"
        "recommend_for_template_transfer: false\n"
        "recommend_for_real_evidence: false\n"
        "recommend_for_evidence_collection: false\n"
        "recommend_for_automatic_execution: false\n"
        "recommend_for_blocker_closure: false\n"
        "recommend_for_product_launch: false\n"
        "recommend_for_production_readiness_claim: false\n\n"
        "## Reason\n\n"
        "The dry run is conditionally recommendable as a local readiness check after "
        "a human fills the 10-row template. It is not recommended for execution or "
        "commercial blocker closure without separate human approval and downstream checks.\n\n"
        "## Status\n\n"
        f"{status_block}\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    payload = build_payload(Path(args.input_template_csv), Path(args.quick_fill_csv))
    write_artifacts(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_TEMPLATE_E2E_DRY_RUN: PASS "
        f"status={payload['status']} "
        f"template_value_present_row_count={payload['template_value_present_row_count']} "
        f"preview_validator_executed={str(payload['preview_validator_executed']).lower()} "
        f"preview_validator_passed={str(payload['preview_validator_passed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0 if not payload["boundary_violations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
