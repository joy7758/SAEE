#!/usr/bin/env python3
"""Prepare and optionally import owner-assignment completion input.

This helper creates a CSV sheet that a human can fill for the selected
commercial evidence sprint blockers. It can also convert a human-filled CSV
into a local owner-assignment input JSON for the existing validator. It does
not assign owners by itself, contact owners, collect evidence, execute work,
close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
DEFAULT_INPUT_PATH = SPRINT_DIR / "owner_assignment_input.template.json"
COMPLETION_CSV_PATH = SPRINT_DIR / "owner_assignment_input_completion.csv"
STATUS_JSON_PATH = SPRINT_DIR / "owner_assignment_completion_status.local.json"
STATUS_MD_PATH = SPRINT_DIR / "owner_assignment_completion_status.md"
GUIDE_PATH = SPRINT_DIR / "owner_assignment_completion_guide.md"
TOP_DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
)

CSV_FIELDS = [
    "blocker_id",
    "phase_id",
    "category",
    "owner_review_lane",
    "required_evidence",
    "assigned_human_owner",
    "owner_contact_reference",
    "target_review_date",
    "owner_acknowledged_scope",
    "human_approval_reference",
    "evidence_collection_request_reference",
    "notes",
]

BOOLEAN_FALSE_BOUNDARIES = [
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
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "owner_contacted_by_codex",
    "customer_data_collected",
    "customer_data_processed",
    "payment_collected",
    "revenue_validated",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
            "FAIL owner assignment input must be a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_from_csv(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "y"}


def assignment_rows(template: dict[str, Any]) -> list[dict[str, Any]]:
    rows = template.get("assignment_inputs", [])
    if not isinstance(rows, list):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
            "FAIL assignment_inputs must be a list"
        )
    result: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
                "FAIL assignment input row must be an object"
            )
        result.append(row)
    return result


def required_single_blocker_fields(args: argparse.Namespace) -> None:
    missing: list[str] = []
    if not args.assigned_human_owner:
        missing.append("--assigned-human-owner")
    if not args.target_review_date:
        missing.append("--target-review-date")
    if not args.human_approval_reference:
        missing.append("--human-approval-reference")
    if args.owner_acknowledged_scope != "true":
        missing.append("--owner-acknowledged-scope true")
    if missing:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
            "FAIL single-blocker mode requires "
            + ", ".join(missing)
        )


def fill_single_blocker_input(
    base_input_json: Path,
    output_input_json: Path,
    *,
    blocker_id: str,
    assigned_human_owner: str,
    owner_contact_reference: str,
    target_review_date: str,
    owner_acknowledged_scope: bool,
    human_approval_reference: str,
    evidence_collection_request_reference: str,
    notes: str,
) -> dict[str, Any]:
    template = read_json(base_input_json)
    rows = assignment_rows(template)
    matched = False
    for row in rows:
        if row.get("blocker_id") != blocker_id:
            continue
        matched = True
        row["assigned_human_owner"] = assigned_human_owner
        row["owner_contact_reference"] = owner_contact_reference
        row["target_review_date"] = target_review_date
        row["owner_acknowledged_scope"] = owner_acknowledged_scope
        row["human_approval_reference"] = human_approval_reference
        row["evidence_collection_request_reference"] = evidence_collection_request_reference
        row["notes"] = notes
        break
    if not matched:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
            f"FAIL unknown --single-blocker-id {blocker_id}"
        )
    imported = dict(template)
    imported["input_status"] = "human_filled_single_blocker_local_input"
    imported["assignment_inputs"] = rows
    imported["review_notes"] = (
        "Generated from explicit human-provided single-blocker owner assignment "
        "fields by the local completion helper. This does not contact owners, "
        "authorize evidence collection, authorize execution, or close blockers."
    )
    output_input_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_input_json, imported)
    return imported


def write_completion_csv(template: dict[str, Any]) -> None:
    COMPLETION_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COMPLETION_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in assignment_rows(template):
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def build_status(template: dict[str, Any]) -> dict[str, Any]:
    rows = assignment_rows(template)
    assigned_count = sum(1 for row in rows if str(row.get("assigned_human_owner", "")).strip())
    unassigned_count = len(rows) - assigned_count
    status: dict[str, Any] = {
        "helper_type": "saee_commercial_evidence_sprint_owner_assignment_completion_helper",
        "helper_version": "v0.1",
        "status": "hold_human_owner_input_required",
        "completion_sheet_ready": True,
        "completion_sheet_path": rel(COMPLETION_CSV_PATH),
        "source_input_template": rel(DEFAULT_INPUT_PATH),
        "generated_by": "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selected_blocker_count": len(template.get("selected_blocker_ids", [])),
        "assignment_row_count": len(rows),
        "human_owner_input_required": True,
        "assigned_owner_count": assigned_count,
        "unassigned_owner_count": unassigned_count,
        "owner_assignment_complete": assigned_count == len(rows) and len(rows) > 0,
        "ready_for_validator": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_helper": 0,
        "blockers_ready_to_close": [],
        "next_action": (
            "A human should fill owner_assignment_input_completion.csv, convert it "
            "with --import-csv into a local input JSON, then run the existing "
            "owner assignment input validator. Do not collect evidence from this helper."
        ),
    }
    for key in BOOLEAN_FALSE_BOUNDARIES:
        status[key] = False
    return status


def write_status_markdown(status: dict[str, Any]) -> None:
    STATUS_MD_PATH.write_text(
        f"""# SAEE Commercial Evidence Sprint Owner Assignment Completion Status

Status: {status['status']}.

This status records that the local completion sheet for the selected commercial
evidence sprint owner assignments is ready for human input. It does not assign
owners, contact owners, collect evidence, execute tasks, close blockers, launch
product, or claim production readiness.

## Summary

- helper_type: {status['helper_type']}
- completion_sheet_ready: true
- selected_blocker_count: {status['selected_blocker_count']}
- assignment_row_count: {status['assignment_row_count']}
- assigned_owner_count: {status['assigned_owner_count']}
- unassigned_owner_count: {status['unassigned_owner_count']}
- owner_assignment_complete: {str(status['owner_assignment_complete']).lower()}
- ready_for_validator: false
- ready_for_separate_evidence_collection_request: false
- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- blockers_closed_by_helper: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Next Human Action

Fill `owner_assignment_input_completion.csv` with human owner names, target
review dates, scope acknowledgements, and approval references. Then run the
helper in import mode and validate the generated JSON with the existing input
validator.

## Boundary

This helper is a local completion aid only. It does not authorize evidence
collection, execution, owner contact, customer contact, blocker closure, launch,
or production-readiness claims.
""",
        encoding="utf-8",
    )


def write_guide() -> None:
    GUIDE_PATH.write_text(
        """# SAEE Owner Assignment Completion Guide

Status: local human input guide, hold.

Use this guide to fill the owner assignment completion sheet for the five
selected commercial evidence sprint blockers.

## Files

- CSV sheet: `owner_assignment_input_completion.csv`
- Source JSON template: `owner_assignment_input.template.json`
- Status JSON: `owner_assignment_completion_status.local.json`
- Existing validator output: `owner_assignment_input_validation.local.json`

## Required Human Fields

For each blocker row, fill:

- `assigned_human_owner`
- `target_review_date`
- `owner_acknowledged_scope` as `true`
- `human_approval_reference`

Optional fields:

- `owner_contact_reference`
- `evidence_collection_request_reference`
- `notes`

## Convert CSV to Validator Input

After a human fills the CSV, run:

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \\
  --import-csv phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_completion.csv \\
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

Then validate:

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py \\
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

## Generate One Human-Assigned Blocker Input Without Editing CSV

For a single selected blocker, a human can provide owner-assignment fields
directly:

```bash
python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \\
  --single-blocker-id support_contact \\
  --assigned-human-owner "Human Owner Name" \\
  --target-review-date "2026-07-12" \\
  --owner-acknowledged-scope true \\
  --human-approval-reference "approval-record-id" \\
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json
```

To fill multiple blockers incrementally, pass the previous output back with
`--base-input-json` and a new `--single-blocker-id`.

This mode records only human-provided owner-assignment input. It does not
contact owners, collect evidence, authorize execution, or close blockers.

## Boundary

This completion helper does not assign owners by itself, contact owners, collect
evidence, execute tasks, close blockers, launch product, contact customers,
expose private core, or claim production readiness. A passing validator result
only means a separate human-approved evidence collection request can be created.
""",
        encoding="utf-8",
    )


def write_static_docs() -> None:
    TOP_DOC_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Owner Assignment Completion Helper v0.1

commercial_evidence_sprint_owner_assignment_completion_helper_v0_1: true
status: hold_human_owner_input_required
helper_scope: local_owner_assignment_completion_sheet_and_import_helper
completion_sheet_ready: true
selected_blocker_count: 5
assignment_row_count: 5
assigned_owner_count: 0
unassigned_owner_count: 5
owner_assignment_complete: false
ready_for_validator: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
blockers_closed_by_helper: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This helper prepares a CSV completion sheet for the selected commercial evidence
sprint owner assignments, can convert a human-filled CSV into local JSON for
the existing owner assignment input validator, and can generate one validator
input from explicit human-provided single-blocker owner assignment fields.

## Entrypoints

- completion sheet: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_completion.csv`
- completion guide: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_completion_guide.md`
- completion status: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_completion_status.local.json`
- completion status report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_completion_status.md`
- script: `scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py`
- single-blocker mode: `scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py --single-blocker-id support_contact`
- smoke: `scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper_smoke.py`

## Boundary

This is local completion support only. It does not assign owners by itself,
contact owners, collect evidence, execute tasks, close blockers, launch
product, modify runtime, backend, kernel, API schema, or private core, or claim
production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Owner Assignment Completion Helper Recommendation Gate

answer: conditional

recommend_for_owner_assignment_completion_support: true
recommend_for_owner_assignment_import: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The helper is useful because it gives a human a structured CSV completion sheet
and deterministic CSV-to-input-JSON plus single-blocker input generation paths
before validator use. It is not an evidence collection runner and does not
authorize execution.

## Boundary

- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- blockers_closed_by_helper: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def import_csv_to_input(import_csv_path: Path, output_input_json: Path) -> dict[str, Any]:
    template = read_json(DEFAULT_INPUT_PATH)
    rows = assignment_rows(template)
    rows_by_id = {row["blocker_id"]: row for row in rows}
    with import_csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CSV_FIELDS:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
                "FAIL CSV header does not match expected owner assignment fields"
            )
        for csv_row in reader:
            blocker_id = csv_row.get("blocker_id", "")
            if blocker_id not in rows_by_id:
                raise SystemExit(
                    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
                    f"FAIL unknown blocker_id in CSV: {blocker_id}"
                )
            target = rows_by_id[blocker_id]
            for field in CSV_FIELDS:
                if field in {"blocker_id", "phase_id", "category", "owner_review_lane", "required_evidence"}:
                    continue
                if field == "owner_acknowledged_scope":
                    target[field] = bool_from_csv(csv_row.get(field, ""))
                else:
                    target[field] = csv_row.get(field, "")
    imported = dict(template)
    imported["input_status"] = "human_filled_local_import"
    imported["assignment_inputs"] = rows
    imported["review_notes"] = (
        "Converted from owner_assignment_input_completion.csv by the local "
        "completion helper. This does not authorize evidence collection or execution."
    )
    output_input_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_input_json, imported)
    return imported


def run(
    import_csv_path: Path | None,
    output_input_json: Path | None,
    *,
    json_only: bool = False,
    single_blocker_id: str = "",
    base_input_json: Path | None = None,
    assigned_human_owner: str = "",
    owner_contact_reference: str = "",
    target_review_date: str = "",
    owner_acknowledged_scope: bool = False,
    human_approval_reference: str = "",
    evidence_collection_request_reference: str = "",
    single_blocker_notes: str = "",
) -> dict[str, Any]:
    template = read_json(DEFAULT_INPUT_PATH)
    write_completion_csv(template)
    status = build_status(template)
    if import_csv_path is not None:
        if output_input_json is None:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
                "FAIL --output-input-json is required with --import-csv"
            )
        import_csv_to_input(import_csv_path, output_input_json)
        status["imported_input_json_path"] = (
            rel(output_input_json) if output_input_json.is_relative_to(ROOT) else str(output_input_json)
        )
        status["ready_for_validator"] = True
        status["owner_assignment_complete"] = False
        status["next_action"] = (
            "Run scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py "
            "against the imported JSON. Validator pass still requires a separate "
            "human-approved evidence collection request."
        )
    if single_blocker_id:
        if output_input_json is None:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
                "FAIL --output-input-json is required with --single-blocker-id"
            )
        base_path = base_input_json or DEFAULT_INPUT_PATH
        imported = fill_single_blocker_input(
            base_path,
            output_input_json,
            blocker_id=single_blocker_id,
            assigned_human_owner=assigned_human_owner,
            owner_contact_reference=owner_contact_reference,
            target_review_date=target_review_date,
            owner_acknowledged_scope=owner_acknowledged_scope,
            human_approval_reference=human_approval_reference,
            evidence_collection_request_reference=evidence_collection_request_reference,
            notes=single_blocker_notes,
        )
        imported_rows = assignment_rows(imported)
        assigned_count = sum(
            1 for row in imported_rows if str(row.get("assigned_human_owner", "")).strip()
        )
        status["imported_input_json_path"] = (
            rel(output_input_json)
            if output_input_json.is_relative_to(ROOT)
            else str(output_input_json)
        )
        status["single_blocker_input_generated"] = True
        status["single_blocker_id"] = single_blocker_id
        status["single_blocker_input_status"] = "human_filled_single_blocker_local_input"
        status["ready_for_validator"] = True
        status["assigned_owner_count"] = assigned_count
        status["unassigned_owner_count"] = max(0, len(imported_rows) - assigned_count)
        status["owner_assignment_complete"] = False
        status["ready_for_separate_evidence_collection_request"] = False
        status["next_action"] = (
            "Run scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py "
            "against the generated JSON. If more blockers need owners, rerun single-blocker "
            "mode with --base-input-json set to the previous output."
        )
    write_json(STATUS_JSON_PATH, status)
    write_status_markdown(status)
    write_guide()
    write_static_docs()
    if json_only:
        print(json.dumps(status, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_COMPLETION_HELPER: "
            f"PASS status={status['status']} "
            f"completion_sheet_ready={str(status['completion_sheet_ready']).lower()} "
            f"assigned_owner_count={status['assigned_owner_count']} "
            "blockers_closed_by_helper=0 production_ready=false"
        )
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-csv", default="")
    parser.add_argument("--base-input-json", default="")
    parser.add_argument("--output-input-json", default="")
    parser.add_argument("--single-blocker-id", default="")
    parser.add_argument("--assigned-human-owner", default="")
    parser.add_argument("--owner-contact-reference", default="")
    parser.add_argument("--target-review-date", default="")
    parser.add_argument("--owner-acknowledged-scope", choices=["true", "false"], default="false")
    parser.add_argument("--human-approval-reference", default="")
    parser.add_argument("--evidence-collection-request-reference", default="")
    parser.add_argument("--single-blocker-notes", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.single_blocker_id:
        required_single_blocker_fields(args)
    import_csv_path = Path(args.import_csv) if args.import_csv else None
    base_input_json = Path(args.base_input_json) if args.base_input_json else None
    output_input_json = Path(args.output_input_json) if args.output_input_json else None
    if import_csv_path is not None and not import_csv_path.is_absolute():
        import_csv_path = ROOT / import_csv_path
    if base_input_json is not None and not base_input_json.is_absolute():
        base_input_json = ROOT / base_input_json
    if output_input_json is not None and not output_input_json.is_absolute():
        output_input_json = ROOT / output_input_json
    run(
        import_csv_path,
        output_input_json,
        json_only=args.json,
        single_blocker_id=args.single_blocker_id,
        base_input_json=base_input_json,
        assigned_human_owner=args.assigned_human_owner,
        owner_contact_reference=args.owner_contact_reference,
        target_review_date=args.target_review_date,
        owner_acknowledged_scope=args.owner_acknowledged_scope == "true",
        human_approval_reference=args.human_approval_reference,
        evidence_collection_request_reference=args.evidence_collection_request_reference,
        single_blocker_notes=args.single_blocker_notes,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
