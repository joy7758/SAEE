#!/usr/bin/env python3
"""Prepare and optionally import ERD approval completion input.

This helper creates a CSV sheet that a human can fill to approve at most one
commercial evidence request draft for a later separate evidence-collection or
execution request. It can convert the human-filled CSV into local JSON for the
existing approval input validator. It can also generate a single-request local
approval input JSON from explicit human-provided CLI fields, which is useful
when a human wants to approve one ERD without hand-editing the full CSV. It
does not collect evidence, execute work, contact owners/customers/vendors, close
blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
DEFAULT_INPUT_PATH = SPRINT_DIR / "evidence_request_approval_input.template.json"
COMPLETION_CSV_PATH = SPRINT_DIR / "evidence_request_approval_input_completion.csv"
STATUS_JSON_PATH = SPRINT_DIR / "evidence_request_approval_completion_status.local.json"
STATUS_MD_PATH = SPRINT_DIR / "evidence_request_approval_completion_status.md"
GUIDE_PATH = SPRINT_DIR / "evidence_request_approval_completion_guide.md"
TOP_DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
)

CSV_FIELDS = [
    "request_id",
    "blocker_id",
    "title",
    "owner_review_lane",
    "assigned_human_owner",
    "human_approval_reference",
    "approval_scope",
    "approval_decision",
    "evidence_collection_request_reference",
    "execution_request_reference",
    "owner_acknowledged_scope",
    "boundary_acknowledged",
    "notes",
]

ALLOWED_DECISIONS = {
    "hold",
    "approved_for_separate_evidence_collection_request",
    "approved_for_separate_execution_request",
}

APPROVAL_SCOPES = {
    "approved_for_separate_evidence_collection_request": "evidence_collection_only",
    "approved_for_separate_execution_request": (
        "implementation_and_evidence_collection_review"
    ),
}

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
    "vendor_contacted",
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
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            "FAIL approval input must be a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_from_csv(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "y"}


def approval_rows(template: dict[str, Any]) -> list[dict[str, Any]]:
    rows = template.get("approval_inputs", [])
    if not isinstance(rows, list):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            "FAIL approval_inputs must be a list"
        )
    result: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL approval input row must be an object"
            )
        result.append(row)
    return result


def write_completion_csv(template: dict[str, Any]) -> None:
    COMPLETION_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COMPLETION_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in approval_rows(template):
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def build_status(template: dict[str, Any]) -> dict[str, Any]:
    rows = approval_rows(template)
    approved_count = sum(
        1
        for row in rows
        if str(row.get("approval_decision", "")).strip()
        in {
            "approved_for_separate_evidence_collection_request",
            "approved_for_separate_execution_request",
        }
    )
    status: dict[str, Any] = {
        "helper_type": "saee_commercial_evidence_request_approval_completion_helper",
        "helper_version": "v0.1",
        "status": "hold_human_approval_input_required",
        "completion_sheet_ready": True,
        "completion_sheet_path": rel(COMPLETION_CSV_PATH),
        "source_input_template": rel(DEFAULT_INPUT_PATH),
        "generated_by": "scripts/saee_commercial_evidence_request_approval_completion_helper.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selected_blocker_count": len(template.get("selected_blocker_ids", [])),
        "approval_row_count": len(rows),
        "human_approval_input_required": True,
        "approved_request_count": approved_count,
        "approval_input_complete": False,
        "ready_for_validator": False,
        "ready_for_separate_evidence_collection_request": False,
        "ready_for_separate_execution_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "blockers_closed_by_helper": 0,
        "blockers_ready_to_close": [],
        "next_action": (
            "A human should fill evidence_request_approval_input_completion.csv, "
            "convert it with --import-csv into a local input JSON, then run the "
            "existing approval input validator. Do not collect evidence or execute "
            "work from this helper."
        ),
    }
    for key in BOOLEAN_FALSE_BOUNDARIES:
        status[key] = False
    return status


def write_status_markdown(status: dict[str, Any]) -> None:
    STATUS_MD_PATH.write_text(
        f"""# SAEE Commercial Evidence Request Approval Completion Status

Status: {status['status']}.

This status records that the local completion sheet for ERD approval input is
ready for human input. It does not approve requests by itself, collect evidence,
execute work, contact owners, contact customers, contact vendors, close
blockers, launch product, or claim production readiness.

## Summary

- helper_type: {status['helper_type']}
- completion_sheet_ready: true
- selected_blocker_count: {status['selected_blocker_count']}
- approval_row_count: {status['approval_row_count']}
- approved_request_count: {status['approved_request_count']}
- approval_input_complete: false
- ready_for_validator: false
- ready_for_separate_evidence_collection_request: false
- ready_for_separate_execution_request: false
- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- blockers_closed_by_helper: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Next Human Action

Fill `evidence_request_approval_input_completion.csv` for at most one ERD row
with a human owner, approval reference, scope, separate request reference, and
boundary acknowledgement. Then run the helper in import mode and validate the
generated JSON with the approval input validator.

## Boundary

This helper is a local completion aid only. It does not authorize evidence
collection, execution, owner contact, customer contact, vendor contact, blocker
closure, launch, or production-readiness claims.
""",
        encoding="utf-8",
    )


def write_guide() -> None:
    GUIDE_PATH.write_text(
        """# SAEE Evidence Request Approval Completion Guide

Status: local human input guide, hold.

Use this guide to fill the ERD approval completion sheet for the five selected
commercial evidence request drafts.

## Files

- CSV sheet: `evidence_request_approval_input_completion.csv`
- Source JSON template: `evidence_request_approval_input.template.json`
- Status JSON: `evidence_request_approval_completion_status.local.json`
- Existing validator output: `evidence_request_approval_input_validation.local.json`

## Required Human Fields For One Approved ERD

Choose at most one ERD row. For that row, fill:

- `assigned_human_owner`
- `human_approval_reference`
- `approval_decision`
- `approval_scope`
- `evidence_collection_request_reference` or `execution_request_reference`
- `owner_acknowledged_scope` as `true`
- `boundary_acknowledged` as `true`

Allowed decisions:

- `hold`
- `approved_for_separate_evidence_collection_request`
- `approved_for_separate_execution_request`

Allowed scopes:

- `evidence_collection_only`
- `implementation_and_evidence_collection_review`

## Convert CSV to Validator Input

After a human fills the CSV, run:

```bash
python3 scripts/saee_commercial_evidence_request_approval_completion_helper.py \\
  --import-csv phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_completion.csv \\
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json
```

Then validate:

```bash
python3 scripts/saee_commercial_evidence_request_approval_input_validator.py \\
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json
```

## Generate One Human-Approved ERD Input Without Editing CSV

If a human has already chosen one ERD and can provide all required approval
fields, the helper can generate the validator input directly:

```bash
python3 scripts/saee_commercial_evidence_request_approval_completion_helper.py \\
  --single-request-id ERD-001 \\
  --assigned-human-owner "Human Owner Name" \\
  --human-approval-reference "approval-record-id" \\
  --approval-decision approved_for_separate_evidence_collection_request \\
  --approval-scope evidence_collection_only \\
  --evidence-collection-request-reference "separate-evidence-request-id" \\
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.human_filled.local.json
```

This mode still does not approve anything by itself. It only records explicit
human-provided approval fields in a validator input file.

## Boundary

This completion helper does not approve requests by itself, collect evidence,
execute tasks, contact owners, contact customers, contact vendors, close
blockers, launch product, expose private core, or claim production readiness. A
passing validator result only means a separate human-approved evidence
collection or execution request can be created.
""",
        encoding="utf-8",
    )


def write_static_docs() -> None:
    TOP_DOC_PATH.write_text(
        """# SAEE Commercial Evidence Request Approval Completion Helper v0.1

commercial_evidence_request_approval_completion_helper_v0_1: true
status: hold_human_approval_input_required
helper_scope: local_evidence_request_approval_completion_sheet_and_import_helper
completion_sheet_ready: true
selected_blocker_count: 5
approval_row_count: 5
approved_request_count: 0
approval_input_complete: false
ready_for_validator: false
ready_for_separate_evidence_collection_request: false
ready_for_separate_execution_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
blockers_closed_by_helper: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This helper prepares a CSV completion sheet for ERD approval input, can convert
a human-filled CSV into local JSON for the existing approval input validator,
and can generate one validator input from explicit human-provided single-request
approval fields.

## Entrypoints

- completion sheet: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_completion.csv`
- completion guide: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_guide.md`
- completion status: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_status.local.json`
- completion status report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_status.md`
- script: `scripts/saee_commercial_evidence_request_approval_completion_helper.py`
- smoke: `scripts/saee_commercial_evidence_request_approval_completion_helper_smoke.py`

## Single-Request Mode

The script supports `--single-request-id` with explicit human owner, approval
reference, approval decision, scope, and separate request reference fields. This
is a local input-generation convenience only; it does not authorize evidence
collection, execution, owner contact, customer contact, vendor contact, blocker
closure, launch, or production-readiness claims.

## Boundary

This is local completion support only. It does not approve requests by itself,
collect evidence, execute work, contact owners/customers/vendors, close
blockers, launch product, modify runtime, backend, kernel, API schema, or
private core, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Request Approval Completion Helper Recommendation Gate

answer: conditional

recommend_for_evidence_request_approval_completion_support: true
recommend_for_evidence_request_approval_import: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The helper is useful because it gives a human a structured CSV completion sheet
and deterministic CSV-to-input-JSON conversion path before approval validator
use. It also supports single-request input generation when a human provides all
approval fields explicitly. It is not an evidence collection runner and does
not authorize execution.

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
    rows = approval_rows(template)
    rows_by_id = {row["request_id"]: row for row in rows}
    with import_csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CSV_FIELDS:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL CSV header does not match expected approval fields"
            )
        for csv_row in reader:
            request_id = csv_row.get("request_id", "")
            if request_id not in rows_by_id:
                raise SystemExit(
                    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                    f"FAIL unknown request_id in CSV: {request_id}"
                )
            target = rows_by_id[request_id]
            for field in CSV_FIELDS:
                if field in {"request_id", "blocker_id", "title", "owner_review_lane"}:
                    continue
                if field in {"owner_acknowledged_scope", "boundary_acknowledged"}:
                    target[field] = bool_from_csv(csv_row.get(field, ""))
                else:
                    target[field] = csv_row.get(field, "")
    imported = dict(template)
    imported["input_status"] = "human_filled_local_import"
    imported["approval_inputs"] = rows
    imported["review_notes"] = (
        "Converted from evidence_request_approval_input_completion.csv by the "
        "local completion helper. This does not authorize evidence collection "
        "or execution."
    )
    output_input_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_input_json, imported)
    return imported


def build_single_request_input(
    *,
    request_id: str,
    assigned_human_owner: str,
    human_approval_reference: str,
    approval_decision: str,
    approval_scope: str,
    evidence_collection_request_reference: str,
    execution_request_reference: str,
    notes: str,
    output_input_json: Path,
) -> dict[str, Any]:
    if approval_decision not in ALLOWED_DECISIONS or approval_decision == "hold":
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            "FAIL --approval-decision must be approved_for_separate_evidence_collection_request "
            "or approved_for_separate_execution_request in single-request mode"
        )
    required_scope = APPROVAL_SCOPES[approval_decision]
    if approval_scope != required_scope:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            f"FAIL --approval-scope must be {required_scope} for {approval_decision}"
        )
    if not assigned_human_owner.strip():
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            "FAIL --assigned-human-owner is required in single-request mode"
        )
    if not human_approval_reference.strip():
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            "FAIL --human-approval-reference is required in single-request mode"
        )
    if approval_decision == "approved_for_separate_evidence_collection_request":
        if not evidence_collection_request_reference.strip():
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL --evidence-collection-request-reference is required for evidence collection approval"
            )
        if execution_request_reference.strip():
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL --execution-request-reference must be blank for evidence collection only approval"
            )
    if approval_decision == "approved_for_separate_execution_request":
        if not execution_request_reference.strip():
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL --execution-request-reference is required for execution approval"
            )

    template = read_json(DEFAULT_INPUT_PATH)
    rows = approval_rows(template)
    target = None
    for row in rows:
        if row.get("request_id") == request_id:
            target = row
            break
    if target is None:
        known = ", ".join(str(row.get("request_id")) for row in rows)
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            f"FAIL unknown --single-request-id {request_id}; expected one of {known}"
        )

    for row in rows:
        row["assigned_human_owner"] = ""
        row["human_approval_reference"] = ""
        row["approval_scope"] = ""
        row["approval_decision"] = "hold"
        row["evidence_collection_request_reference"] = ""
        row["execution_request_reference"] = ""
        row["owner_acknowledged_scope"] = False
        row["boundary_acknowledged"] = False
        row["notes"] = ""

    target["assigned_human_owner"] = assigned_human_owner.strip()
    target["human_approval_reference"] = human_approval_reference.strip()
    target["approval_scope"] = approval_scope
    target["approval_decision"] = approval_decision
    target["evidence_collection_request_reference"] = (
        evidence_collection_request_reference.strip()
    )
    target["execution_request_reference"] = execution_request_reference.strip()
    target["owner_acknowledged_scope"] = True
    target["boundary_acknowledged"] = True
    target["notes"] = notes.strip()

    generated = dict(template)
    generated["input_status"] = "human_filled_single_request_local_input"
    generated["approval_inputs"] = rows
    generated["review_notes"] = (
        "Generated from explicit human-provided single-request CLI fields by the "
        "local completion helper. This does not authorize evidence collection "
        "or execution; it only prepares input for the approval input validator."
    )
    output_input_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_input_json, generated)
    return generated


def run(
    import_csv_path: Path | None,
    output_input_json: Path | None,
    *,
    single_request_id: str = "",
    assigned_human_owner: str = "",
    human_approval_reference: str = "",
    approval_decision: str = "",
    approval_scope: str = "",
    evidence_collection_request_reference: str = "",
    execution_request_reference: str = "",
    single_request_notes: str = "",
    json_only: bool = False,
) -> dict[str, Any]:
    template = read_json(DEFAULT_INPUT_PATH)
    write_completion_csv(template)
    status = build_status(template)
    single_request_mode = bool(single_request_id)
    if import_csv_path is not None and single_request_mode:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            "FAIL --import-csv and --single-request-id cannot be used together"
        )
    if import_csv_path is not None:
        if output_input_json is None:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL --output-input-json is required with --import-csv"
            )
        import_csv_to_input(import_csv_path, output_input_json)
        status["imported_input_json_path"] = (
            rel(output_input_json)
            if output_input_json.is_relative_to(ROOT)
            else str(output_input_json)
        )
        status["ready_for_validator"] = True
        status["approval_input_complete"] = False
        status["next_action"] = (
            "Run scripts/saee_commercial_evidence_request_approval_input_validator.py "
            "against the imported JSON. Validator pass still requires a separate "
            "human-approved evidence collection or execution request."
        )
    if single_request_mode:
        if output_input_json is None:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
                "FAIL --output-input-json is required with --single-request-id"
            )
        build_single_request_input(
            request_id=single_request_id,
            assigned_human_owner=assigned_human_owner,
            human_approval_reference=human_approval_reference,
            approval_decision=approval_decision,
            approval_scope=approval_scope,
            evidence_collection_request_reference=evidence_collection_request_reference,
            execution_request_reference=execution_request_reference,
            notes=single_request_notes,
            output_input_json=output_input_json,
        )
        status["generated_single_request_input_json_path"] = (
            rel(output_input_json)
            if output_input_json.is_relative_to(ROOT)
            else str(output_input_json)
        )
        status["single_request_input_generator_used"] = True
        status["single_request_id"] = single_request_id
        status["ready_for_validator"] = True
        status["approval_input_complete"] = False
        status["next_action"] = (
            "Run scripts/saee_commercial_evidence_request_approval_input_validator.py "
            "against the single-request JSON. Validator pass still requires a "
            "separate human-approved evidence collection or execution request."
        )
    write_json(STATUS_JSON_PATH, status)
    write_status_markdown(status)
    write_guide()
    write_static_docs()
    if json_only:
        print(json.dumps(status, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_COMPLETION_HELPER: "
            f"PASS status={status['status']} "
            f"completion_sheet_ready={str(status['completion_sheet_ready']).lower()} "
            f"approved_request_count={status['approved_request_count']} "
            "blockers_closed_by_helper=0 production_ready=false"
        )
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-csv", default="")
    parser.add_argument("--output-input-json", default="")
    parser.add_argument("--single-request-id", default="")
    parser.add_argument("--assigned-human-owner", default="")
    parser.add_argument("--human-approval-reference", default="")
    parser.add_argument("--approval-decision", default="")
    parser.add_argument("--approval-scope", default="")
    parser.add_argument("--evidence-collection-request-reference", default="")
    parser.add_argument("--execution-request-reference", default="")
    parser.add_argument("--single-request-notes", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    import_csv_path = Path(args.import_csv) if args.import_csv else None
    output_input_json = Path(args.output_input_json) if args.output_input_json else None
    if import_csv_path is not None and not import_csv_path.is_absolute():
        import_csv_path = ROOT / import_csv_path
    if output_input_json is not None and not output_input_json.is_absolute():
        output_input_json = ROOT / output_input_json
    run(
        import_csv_path,
        output_input_json,
        single_request_id=args.single_request_id,
        assigned_human_owner=args.assigned_human_owner,
        human_approval_reference=args.human_approval_reference,
        approval_decision=args.approval_decision,
        approval_scope=args.approval_scope,
        evidence_collection_request_reference=args.evidence_collection_request_reference,
        execution_request_reference=args.execution_request_reference,
        single_request_notes=args.single_request_notes,
        json_only=args.json,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
