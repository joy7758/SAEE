#!/usr/bin/env python3
"""Prepare first-owner input completion materials for SEQ-001.

This helper creates a one-row first-owner input sheet for `support_contact` and
can turn explicit human-provided fields into a local input JSON for the first
owner input validator. It does not assign owners by itself, contact owners,
collect evidence, execute work, close blockers, launch product, or claim
production readiness.
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_sprint_first_owner_input_validator import (
    DEFAULT_INPUT_PATH,
    FIRST_BLOCKER_ID,
    FORBIDDEN_TRUE_KEYS,
    build_template,
)


SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMPLETION_CSV_PATH = SPRINT_DIR / "first_owner_input_completion.csv"
STATUS_JSON_PATH = SPRINT_DIR / "first_owner_input_completion_status.local.json"
STATUS_MD_PATH = SPRINT_DIR / "first_owner_input_completion_status.md"
GUIDE_PATH = SPRINT_DIR / "first_owner_input_completion_guide.md"
DEFAULT_OUTPUT_INPUT_PATH = SPRINT_DIR / "first_owner_input.human_filled.local.json"
TOP_DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
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
    "notes",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER: "
            "FAIL input must be a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_template() -> dict[str, Any]:
    if DEFAULT_INPUT_PATH.exists():
        return read_json(DEFAULT_INPUT_PATH)
    template = build_template()
    write_json(DEFAULT_INPUT_PATH, template)
    return template


def first_owner_row(template: dict[str, Any]) -> dict[str, Any]:
    row = template.get("first_owner_input", {})
    if not isinstance(row, dict) or row.get("blocker_id") != FIRST_BLOCKER_ID:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER: "
            f"FAIL expected first_owner_input.blocker_id={FIRST_BLOCKER_ID}"
        )
    return row


def write_completion_csv(template: dict[str, Any]) -> None:
    row = first_owner_row(template)
    csv_row = {field: row.get(field, "") for field in CSV_FIELDS}
    for field in [
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "owner_acknowledged_scope",
        "human_approval_reference",
    ]:
        csv_row[field] = ""
    COMPLETION_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COMPLETION_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerow(csv_row)


def bool_from_arg(value: str) -> bool:
    return value.strip().lower() == "true"


def args_complete(args: argparse.Namespace) -> bool:
    return all(
        [
            bool(args.assigned_human_owner),
            bool(args.owner_contact_reference),
            bool(args.target_review_date),
            args.owner_acknowledged_scope == "true",
            bool(args.human_approval_reference),
        ]
    )


def fill_first_owner_input(
    template: dict[str, Any],
    args: argparse.Namespace,
    output_input_json: Path,
) -> dict[str, Any]:
    if not args_complete(args):
        missing = []
        if not args.assigned_human_owner:
            missing.append("--assigned-human-owner")
        if not args.owner_contact_reference:
            missing.append("--owner-contact-reference")
        if not args.target_review_date:
            missing.append("--target-review-date")
        if args.owner_acknowledged_scope != "true":
            missing.append("--owner-acknowledged-scope true")
        if not args.human_approval_reference:
            missing.append("--human-approval-reference")
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER: "
            "FAIL first-owner input generation requires " + ", ".join(missing)
        )
    data = dict(template)
    row = dict(first_owner_row(template))
    row["assigned_human_owner"] = args.assigned_human_owner
    row["owner_contact_reference"] = args.owner_contact_reference
    row["target_review_date"] = args.target_review_date
    row["owner_acknowledged_scope"] = bool_from_arg(args.owner_acknowledged_scope)
    row["human_approval_reference"] = args.human_approval_reference
    row["notes"] = args.notes or ""
    data["input_status"] = "human_filled_first_owner_local_input"
    data["first_owner_input"] = row
    data["review_notes"] = (
        "Generated from explicit human-provided first-owner fields by the local "
        "completion helper. This does not contact owners, authorize evidence "
        "collection, authorize execution, or close blockers."
    )
    output_input_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_input_json, data)
    return data


def boundary_defaults() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUE_KEYS}


def build_status(*, wrote_filled_input: bool, output_input_json: Path | None) -> dict[str, Any]:
    assigned_owner_count = 1 if wrote_filled_input else 0
    status = (
        "ready_for_first_owner_input_validator"
        if wrote_filled_input
        else "hold_human_first_owner_input_required"
    )
    payload: dict[str, Any] = {
        "helper_type": "saee_commercial_evidence_sprint_first_owner_input_completion_helper",
        "helper_version": "v0.1",
        "helper_scope": "local_first_owner_input_completion_sheet_and_generation_helper",
        "status": status,
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": FIRST_BLOCKER_ID,
        "completion_sheet_ready": True,
        "selected_blocker_count": 1,
        "human_first_owner_input_required": not wrote_filled_input,
        "assigned_owner_count": assigned_owner_count,
        "unassigned_owner_count": 1 - assigned_owner_count,
        "first_owner_assignment_complete": wrote_filled_input,
        "ready_for_first_owner_input_validator": wrote_filled_input,
        "ready_for_full_owner_assignment_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_helper": 0,
        "blockers_ready_to_close": [],
        "completion_csv": rel(COMPLETION_CSV_PATH),
        "template_input": rel(DEFAULT_INPUT_PATH),
        "generated_input": rel(output_input_json) if output_input_json else "",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py",
        "next_action": (
            "Fill the first-owner fields, generate first_owner_input.human_filled.local.json, "
            "then run the first-owner input validator. Do not collect evidence or close blockers."
        ),
    }
    payload.update(boundary_defaults())
    return payload


def write_status_report(payload: dict[str, Any]) -> None:
    STATUS_MD_PATH.write_text(
        f"""# SAEE Commercial Evidence Sprint First Owner Input Completion Helper

Status: {payload['status']}.

This helper creates a one-row human-fillable first-owner input sheet for
`support_contact` and can generate a local validator input only from explicit
human-provided fields.

## Summary

- helper_type: {payload['helper_type']}
- helper_scope: {payload['helper_scope']}
- sequence_step_id: {payload['sequence_step_id']}
- first_blocker_id: {payload['first_blocker_id']}
- completion_sheet_ready: {str(payload['completion_sheet_ready']).lower()}
- selected_blocker_count: {payload['selected_blocker_count']}
- assigned_owner_count: {payload['assigned_owner_count']}
- unassigned_owner_count: {payload['unassigned_owner_count']}
- first_owner_assignment_complete: {str(payload['first_owner_assignment_complete']).lower()}
- ready_for_first_owner_input_validator: {str(payload['ready_for_first_owner_input_validator']).lower()}
- ready_for_full_owner_assignment_validator: false
- ready_for_evidence_collection: false
- ready_for_separate_evidence_collection_request: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_helper: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Boundary

This helper does not assign owners by itself, contact owners, collect evidence,
execute tasks, close blockers, launch product, contact customers, expose
private core, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_guide() -> None:
    GUIDE_PATH.write_text(
        """# SAEE First Owner Input Completion Guide

Status: local human input guide, hold.

Use this guide for `SEQ-001`: fill the `support_contact` owner input before
running the first-owner input validator.

## Files

- CSV sheet: `first_owner_input_completion.csv`
- Source JSON template: `first_owner_input.template.json`
- Status JSON: `first_owner_input_completion_status.local.json`
- Validator output: `first_owner_input_validation.local.json`

## Required Human Fields

- `assigned_human_owner`
- `owner_contact_reference`
- `target_review_date`
- `owner_acknowledged_scope` as `true`
- `human_approval_reference`

## Generate Human-Filled First Owner Input

```bash
python3 scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py \\
  --assigned-human-owner "Human Owner Name" \\
  --owner-contact-reference "internal-owner-reference" \\
  --target-review-date "2026-07-12" \\
  --owner-acknowledged-scope true \\
  --human-approval-reference "approval-record-id" \\
  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json
```

Then validate:

```bash
python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py \\
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.human_filled.local.json
```

## Boundary

This helper records only human-provided first-owner input. It does not contact
owners, collect evidence, authorize execution, close blockers, launch product,
or claim production readiness.
""",
        encoding="utf-8",
    )


def write_static_docs() -> None:
    TOP_DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOP_DOC_PATH.write_text(
        """# SAEE Commercial Evidence Sprint First Owner Input Completion Helper v0.1

commercial_evidence_sprint_first_owner_input_completion_helper_v0_1: true
status: hold_human_first_owner_input_required
helper_scope: local_first_owner_input_completion_sheet_and_generation_helper
sequence_step_id: SEQ-001
first_blocker_id: support_contact
completion_sheet_ready: true
selected_blocker_count: 1
assigned_owner_count: 0
unassigned_owner_count: 1
first_owner_assignment_complete: false
ready_for_first_owner_input_validator: false
ready_for_full_owner_assignment_validator: false
ready_for_evidence_collection: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_helper: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This helper prepares the human-fillable first-owner input for `support_contact`
and can generate a local validator input from explicit human-provided fields.

## Entrypoints

- completion sheet: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion.csv`
- completion guide: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_guide.md`
- status JSON: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.local.json`
- status report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.md`
- script: `scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py`
- smoke: `scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper_smoke.py`

## Boundary

This is local input preparation only. It does not contact owners, collect
evidence, execute tasks, close blockers, launch product, modify runtime,
backend, kernel, API schema, or private core, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Sprint First Owner Input Completion Helper Recommendation Gate

answer: conditional

recommend_for_first_owner_input_completion_support: true
recommend_for_first_owner_input_generation: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The helper is useful for preparing a human-filled `support_contact` owner input
for the first-owner validator. It does not approve evidence collection,
execute work, or close blockers.

## Boundary

- first_blocker_id: support_contact
- ready_for_evidence_collection: false
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


def run(args: argparse.Namespace, *, json_only: bool = False) -> dict[str, Any]:
    template = ensure_template()
    write_completion_csv(template)
    output_input_json: Path | None = None
    wrote_filled_input = False
    if args_complete(args):
        output_input_json = Path(args.output_input_json)
        if not output_input_json.is_absolute():
            output_input_json = ROOT / output_input_json
        fill_first_owner_input(template, args, output_input_json)
        wrote_filled_input = True
    status = build_status(
        wrote_filled_input=wrote_filled_input,
        output_input_json=output_input_json,
    )
    write_json(STATUS_JSON_PATH, status)
    write_status_report(status)
    write_guide()
    write_static_docs()
    if json_only:
        print(json.dumps(status, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_COMPLETION_HELPER: "
            f"PASS status={status['status']} "
            "completion_sheet_ready=true "
            f"assigned_owner_count={status['assigned_owner_count']} "
            "ready_for_evidence_collection=false "
            "evidence_collection_authorized=false execution_authorized=false "
            "blockers_closed_by_helper=0 production_ready=false"
        )
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assigned-human-owner", default="")
    parser.add_argument("--owner-contact-reference", default="")
    parser.add_argument("--target-review-date", default="")
    parser.add_argument(
        "--owner-acknowledged-scope",
        choices=["true", "false"],
        default="false",
    )
    parser.add_argument("--human-approval-reference", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--output-input-json", default=str(DEFAULT_OUTPUT_INPUT_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    run(args, json_only=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
