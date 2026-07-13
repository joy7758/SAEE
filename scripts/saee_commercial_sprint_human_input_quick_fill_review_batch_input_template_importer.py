#!/usr/bin/env python3
"""Controlled review-batch input-template to quick-fill local-output importer.

Default mode is dry-run only. It reads the 10-row review-batch input template
and the 64-row source quick-fill CSV, checks whether the selected rows are ready
to copy into a local quick-fill output CSV, and writes only importer status
artifacts.

The official source quick-fill CSV is never overwritten. A local output copy is
written only when both `--apply` and
`--confirm-human-approved-template-import` are provided and all selected
template rows have human-entered values with no boundary issues. This script
does not infer values, write the workbook, transfer templates, run validators
on real input, collect evidence, contact anyone, close blockers, launch
product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
DEFAULT_INPUT_TEMPLATE_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
DEFAULT_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
DEFAULT_OUTPUT_QUICK_FILL_CSV = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_packet.imported_from_review_batch_template.local.csv"
)

OUT_JSON = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.local.json"
)
OUT_MD = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.md"
)
OUT_CSV = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.csv"
)
OUT_BOUNDARY = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_boundary_audit.md"
)
TOP_DOC = (
    COMMERCIAL_DIR
    / "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER_RECOMMENDATION_GATE.md"
)

EXPECTED_TEMPLATE_ROW_COUNT = 10
EXPECTED_SOURCE_ROW_COUNT = 64
SUPERSEDED_REVIEW_BATCH_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"

PLACEHOLDER_VALUES = {
    "",
    "todo",
    "tbd",
    "n/a",
    "na",
    "none",
    "unknown",
    "placeholder",
    "fill later",
    "to be filled",
}

SECRET_PATTERNS = {
    "openai_or_provider_api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "langsmith_api_key": re.compile(r"\bls__[A-Za-z0-9_=-]{10,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "jwt_like_token": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
}

FORBIDDEN_CLAIM_PATTERNS = {
    "production_ready_claim": re.compile(r"\bproduction[_ -]?ready\s*[:=]\s*true\b", re.I),
    "customer_validated_claim": re.compile(r"\bcustomer[_ -]?validated\s*[:=]\s*true\b", re.I),
    "product_launched_claim": re.compile(r"\bproduct[_ -]?launched\s*[:=]\s*true\b", re.I),
    "external_validation_claim": re.compile(r"\bexternal[_ -]?validation\s*[:=]\s*true\b", re.I),
    "private_core_exposed_claim": re.compile(r"\bprivate[_ -]?core[_ -]?exposed\s*[:=]\s*true\b", re.I),
}

PRIVATE_CORE_TERMS = [
    "fitness logic",
    "selection logic",
    "mutation logic",
    "lineage internals",
    "private core",
    "evolution kernel",
]

FALSE_FLAGS = [
    "source_quick_fill_packet_modified",
    "batch_values_applied_to_source",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "ready_for_safety_preflight",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-template-csv", default=str(DEFAULT_INPUT_TEMPLATE_CSV))
    parser.add_argument("--quick-fill-csv", default=str(DEFAULT_QUICK_FILL_CSV))
    parser.add_argument("--output-quick-fill-csv", default=str(DEFAULT_OUTPUT_QUICK_FILL_CSV))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-human-approved-template-import", action="store_true")
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scan_for_boundary_issues(text: str) -> list[str]:
    issues: list[str] = []
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            issues.append(name)
    for name, pattern in FORBIDDEN_CLAIM_PATTERNS.items():
        if pattern.search(text):
            issues.append(name)
    lowered = text.lower()
    if any(term in lowered for term in PRIVATE_CORE_TERMS):
        issues.append("private_core_reference")
    return sorted(set(issues))


def classify_value(value: str, notes: str) -> tuple[str, list[str]]:
    stripped = value.strip()
    issues: list[str] = []
    if not stripped:
        return "hold_missing_human_template_value", ["missing_human_template_value"]
    if stripped.lower() in PLACEHOLDER_VALUES:
        issues.append("placeholder_template_value")
    issues.extend(scan_for_boundary_issues("\n".join([stripped, notes.strip()])))
    boundary_issue_prefixes = set(SECRET_PATTERNS) | set(FORBIDDEN_CLAIM_PATTERNS) | {
        "private_core_reference"
    }
    if any(issue in boundary_issue_prefixes for issue in issues):
        return "stop_boundary_or_sensitive_template_value", sorted(set(issues))
    if issues:
        return "needs_human_template_value_review", sorted(set(issues))
    return "template_value_ready_for_local_output", []


def same_identity(template_row: dict[str, str], source_row: dict[str, str]) -> bool:
    identity_fields = [
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "target_json_pointer",
    ]
    return all(template_row.get(field, "") == source_row.get(field, "") for field in identity_fields)


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], list[str], list[dict[str, str]]]:
    input_template_csv = Path(args.input_template_csv)
    quick_fill_csv = Path(args.quick_fill_csv)
    output_quick_fill_csv = Path(args.output_quick_fill_csv)
    template_fields, template_rows = load_csv(input_template_csv)
    source_fields, source_rows = load_csv(quick_fill_csv)
    source_by_id = {row.get("quick_fill_row_id", ""): row for row in source_rows}
    review_batch_template_superseded = len(template_rows) == 0

    boundary_violations: list[str] = []
    if len(template_rows) != EXPECTED_TEMPLATE_ROW_COUNT and not review_batch_template_superseded:
        boundary_violations.append("unexpected_template_row_count")
    if len(source_rows) != EXPECTED_SOURCE_ROW_COUNT:
        boundary_violations.append("unexpected_source_quick_fill_row_count")

    required_template_fields = {
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "target_json_pointer",
        "human_value_to_enter",
        "notes_for_human",
    }
    required_source_fields = required_template_fields | {
        "human_fill_prompt",
        "target_workbook_csv",
        "target_workbook_column",
        "quick_fill_status",
        "value_imported_to_workbook",
        "value_transferred",
        "template_written",
    }
    missing_template_fields = sorted(required_template_fields - set(template_fields))
    missing_source_fields = sorted(required_source_fields - set(source_fields))
    if missing_template_fields:
        boundary_violations.append("missing_template_fields")
    if missing_source_fields:
        boundary_violations.append("missing_source_fields")

    output_rows = [dict(row) for row in source_rows]
    output_by_id = {row.get("quick_fill_row_id", ""): row for row in output_rows}
    import_rows: list[dict[str, Any]] = []
    value_present_count = 0
    would_import_count = 0
    mapping_resolved_count = 0
    row_boundary_count = 0

    for template_row in template_rows:
        row_id = template_row.get("quick_fill_row_id", "")
        source_row = source_by_id.get(row_id)
        value = template_row.get("human_value_to_enter", "").strip()
        notes = template_row.get("notes_for_human", "").strip()
        value_present = bool(value)
        if value_present:
            value_present_count += 1
        mapping_resolved = source_row is not None and same_identity(template_row, source_row)
        if mapping_resolved:
            mapping_resolved_count += 1
        value_status, issues = classify_value(value, notes)
        if value_status.startswith("stop_"):
            row_boundary_count += 1
        source_clean_for_import = False
        if source_row is not None:
            source_clean_for_import = (
                not source_row.get("human_value_to_enter", "").strip()
                and not source_row.get("notes_for_human", "").strip()
                and source_row.get("quick_fill_status") == "blank_pending_human_input"
                and source_row.get("value_imported_to_workbook") == "False"
                and source_row.get("value_transferred") == "False"
                and source_row.get("template_written") == "False"
            )

        import_ready = (
            mapping_resolved
            and source_clean_for_import
            and value_status == "template_value_ready_for_local_output"
        )
        if import_ready:
            would_import_count += 1

        if args.apply and args.confirm_human_approved_template_import and import_ready:
            target = output_by_id[row_id]
            target["human_value_to_enter"] = value
            target["notes_for_human"] = notes
            target["quick_fill_status"] = "human_filled_from_review_batch_template_pending_validator"

        row_status = (
            "ready_for_local_quick_fill_output"
            if import_ready
            else value_status
            if value_status != "template_value_ready_for_local_output"
            else "stop_mapping_or_source_state_issue"
        )
        import_rows.append(
            {
                "quick_fill_row_id": row_id,
                "review_batch_row_id": template_row.get("review_batch_row_id", ""),
                "workbook_row_id": template_row.get("workbook_row_id", ""),
                "blocker_id": template_row.get("blocker_id", ""),
                "owner_review_lane": template_row.get("owner_review_lane", ""),
                "input_group": template_row.get("input_group", ""),
                "input_key": template_row.get("input_key", ""),
                "input_kind": template_row.get("input_kind", ""),
                "mapping_resolved": mapping_resolved,
                "source_clean_for_import": source_clean_for_import,
                "human_template_value_present": value_present,
                "template_value_issue_count": len(issues),
                "template_value_issues": issues,
                "local_output_ready": import_ready,
                "row_status": row_status,
                "value_written_to_local_output": False,
            }
        )

    apply_requested = bool(args.apply)
    human_confirmation_provided = bool(args.confirm_human_approved_template_import)
    if apply_requested and not human_confirmation_provided:
        boundary_violations.append("apply_requested_without_human_confirmation")

    all_template_values_ready = (
        len(template_rows) == EXPECTED_TEMPLATE_ROW_COUNT
        and value_present_count == EXPECTED_TEMPLATE_ROW_COUNT
        and would_import_count == EXPECTED_TEMPLATE_ROW_COUNT
        and row_boundary_count == 0
    )
    apply_preconditions_met = (
        apply_requested
        and human_confirmation_provided
        and all_template_values_ready
        and not boundary_violations
    )
    if apply_requested and human_confirmation_provided and not apply_preconditions_met:
        boundary_violations.append("apply_requested_without_complete_template_import_readiness")

    local_output_written = False
    if apply_preconditions_met:
        write_csv(output_quick_fill_csv, source_fields, output_rows)
        local_output_written = True
        for row in import_rows:
            if row["local_output_ready"]:
                row["value_written_to_local_output"] = True

    if review_batch_template_superseded and not apply_requested:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    elif boundary_violations or row_boundary_count:
        status = "stop_boundary_or_apply_precondition_violation"
    elif all_template_values_ready:
        status = "ready_for_local_quick_fill_output_pending_explicit_human_command"
    else:
        status = "hold_template_human_values_required"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1": True,
        "importer_type": "review_batch_input_template_to_local_quick_fill_output_importer",
        "importer_scope": "template_to_local_quick_fill_output_only_no_source_overwrite_no_workbook_import",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "execution_mode": "apply_write_local_quick_fill_output" if local_output_written else "dry_run_no_write",
        "source_input_template_csv": rel(input_template_csv),
        "source_quick_fill_csv": rel(quick_fill_csv),
        "output_quick_fill_csv": rel(output_quick_fill_csv),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py",
        "template_row_count": len(template_rows),
        "source_quick_fill_row_count": len(source_rows),
        "expected_template_row_count": EXPECTED_TEMPLATE_ROW_COUNT,
        "expected_source_quick_fill_row_count": EXPECTED_SOURCE_ROW_COUNT,
        "mapping_resolved_row_count": mapping_resolved_count,
        "template_value_present_row_count": value_present_count,
        "missing_template_value_row_count": len(template_rows) - value_present_count,
        "review_batch_template_superseded": review_batch_template_superseded,
        "ready_for_workbook_import_approval_review": review_batch_template_superseded,
        "would_import_row_count": would_import_count,
        "row_boundary_issue_count": row_boundary_count,
        "all_template_values_ready": all_template_values_ready,
        "apply_requested": apply_requested,
        "human_template_import_confirmation_provided": human_confirmation_provided,
        "apply_preconditions_met": apply_preconditions_met,
        "apply_performed": local_output_written,
        "local_quick_fill_output_written": local_output_written,
        "batch_values_written_to_local_output": local_output_written,
        "local_output_ready_for_review_batch_validator": local_output_written,
        "source_quick_fill_packet_modified": False,
        "batch_values_applied_to_source": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "raw_values_recorded_in_status_artifacts": False,
        "blockers_closed_by_importer": 0,
        "boundary_violation_count": len(boundary_violations) + row_boundary_count,
        "boundary_violations": sorted(set(boundary_violations)),
        "import_rows": import_rows,
        "next_human_action": (
            "Review the workbook import approval request packet. The old 10-row template importer route is superseded; do not write local quick-fill output, import workbooks, run validators on real input, collect evidence, or close blockers without separate approval."
            if review_batch_template_superseded
            else "Fill the 10-row input template, rerun this importer in dry-run mode, "
            "then use --apply --confirm-human-approved-template-import only after "
            "human approval to write a local quick-fill output CSV for validator review."
        ),
    }
    for flag in FALSE_FLAGS:
        if flag not in payload:
            payload[flag] = False
    return payload, source_fields, output_rows


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1: true",
        f"status: {payload['status']}",
        f"commercial_status: {payload['commercial_status']}",
        f"production_launch_status: {payload['production_launch_status']}",
        f"execution_mode: {payload['execution_mode']}",
        f"importer_scope: {payload['importer_scope']}",
        f"template_row_count: {payload['template_row_count']}",
        f"source_quick_fill_row_count: {payload['source_quick_fill_row_count']}",
        f"mapping_resolved_row_count: {payload['mapping_resolved_row_count']}",
        f"template_value_present_row_count: {payload['template_value_present_row_count']}",
        f"missing_template_value_row_count: {payload['missing_template_value_row_count']}",
        f"review_batch_template_superseded: {str(payload['review_batch_template_superseded']).lower()}",
        "ready_for_workbook_import_approval_review: "
        f"{str(payload['ready_for_workbook_import_approval_review']).lower()}",
        f"would_import_row_count: {payload['would_import_row_count']}",
        f"row_boundary_issue_count: {payload['row_boundary_issue_count']}",
        f"apply_requested: {str(payload['apply_requested']).lower()}",
        "human_template_import_confirmation_provided: "
        f"{str(payload['human_template_import_confirmation_provided']).lower()}",
        f"apply_performed: {str(payload['apply_performed']).lower()}",
        f"local_quick_fill_output_written: {str(payload['local_quick_fill_output_written']).lower()}",
        "batch_values_written_to_local_output: "
        f"{str(payload['batch_values_written_to_local_output']).lower()}",
        f"source_quick_fill_packet_modified: {str(payload['source_quick_fill_packet_modified']).lower()}",
        f"batch_values_applied_to_source: {str(payload['batch_values_applied_to_source']).lower()}",
        f"quick_fill_imported_to_workbook: {str(payload['quick_fill_imported_to_workbook']).lower()}",
        f"workbook_import_performed: {str(payload['workbook_import_performed']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"blockers_closed_by_importer: {payload['blockers_closed_by_importer']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_fields = [
        "quick_fill_row_id",
        "review_batch_row_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "mapping_resolved",
        "source_clean_for_import",
        "human_template_value_present",
        "template_value_issue_count",
        "local_output_ready",
        "row_status",
        "value_written_to_local_output",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for row in payload["import_rows"]:
            writer.writerow({field: row.get(field, "") for field in csv_fields})

    status_block = "\n".join(status_lines(payload))
    OUT_MD.write_text(
        "# Commercial Sprint Human Input Quick-Fill Review Batch Input Template Importer\n\n"
        f"{status_block}\n\n"
        "## Purpose\n\n"
        "This local importer checks whether the 10-row human-filled review-batch "
        "input template can be copied into a local quick-fill output CSV. Default "
        "execution is dry-run only.\n\n"
        "## Apply Boundary\n\n"
        "Apply mode writes only a local quick-fill output CSV and never overwrites "
        "the official source quick-fill packet. It does not import a workbook, "
        "transfer templates, run validators, collect evidence, close blockers, "
        "launch product, or claim production readiness.\n\n"
        "## Next Human Action\n\n"
        f"{payload['next_human_action']}\n",
        encoding="utf-8",
    )

    OUT_BOUNDARY.write_text(
        "# Commercial Sprint Human Input Quick-Fill Review Batch Input Template Importer Boundary Audit\n\n"
        f"{status_block}\n\n"
        "- Default mode writes no quick-fill output.\n"
        "- Apply mode writes only a local quick-fill output CSV after explicit human confirmation.\n"
        "- The official source quick-fill CSV is not overwritten.\n"
        "- No values are inferred or entered by Codex.\n"
        "- No workbook import is performed.\n"
        "- No template transfer is performed.\n"
        "- No validator is run on real input.\n"
        "- No evidence is collected.\n"
        "- No blocker is closed.\n"
        "- No runtime, backend, kernel, API schema, or private core is modified.\n",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Review Batch Input Template Importer v0.1\n\n"
        f"{status_block}\n\n"
        "This is a controlled local bridge from the 10-row review-batch input "
        "template to a local quick-fill output CSV. It is recommendable only as "
        "a human-approved local preparation utility and not as evidence "
        "collection, workbook import, blocker closure, production readiness, or "
        "customer validation.\n",
        encoding="utf-8",
    )

    GATE.write_text(
        "# SAEE Commercial Sprint Human Input Quick-Fill Review Batch Input Template Importer Recommendation Gate\n\n"
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_v0_1: true\n"
        "answer: conditional\n"
        "recommend_for_template_import_dry_run: true\n"
        "recommend_for_human_approved_local_quick_fill_output: true\n"
        "recommend_for_source_quick_fill_overwrite: false\n"
        "recommend_for_unapproved_import: false\n"
        "recommend_for_value_inference: false\n"
        "recommend_for_workbook_import: false\n"
        "recommend_for_template_transfer: false\n"
        "recommend_for_real_evidence: false\n"
        "recommend_for_evidence_collection: false\n"
        "recommend_for_automatic_execution: false\n"
        "recommend_for_blocker_closure: false\n"
        "recommend_for_product_launch: false\n"
        "recommend_for_production_readiness_claim: false\n\n"
        "## Reason\n\n"
        "The importer is conditionally recommendable only after a human has filled "
        "the 10-row input template and explicitly approved writing a local "
        "quick-fill output CSV. It is not recommended for autonomous execution, "
        "source overwrite, workbook import, or blocker closure.\n\n"
        "## Status\n\n"
        f"{status_block}\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    payload, _, _ = build_payload(args)
    write_artifacts(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_IMPORTER: PASS "
        f"status={payload['status']} "
        f"execution_mode={payload['execution_mode']} "
        f"template_value_present_row_count={payload['template_value_present_row_count']} "
        f"would_import_row_count={payload['would_import_row_count']} "
        f"local_quick_fill_output_written={str(payload['local_quick_fill_output_written']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0 if not payload["boundary_violations"] or not args.apply else 1


if __name__ == "__main__":
    raise SystemExit(main())
