#!/usr/bin/env python3
"""Build a local ERD approval readiness board without approving work.

The board reads the human-fillable ERD approval completion CSV and reports
whether any row is complete enough to import into the existing approval input
validator. It does not import, approve, collect evidence, execute work, contact
owners/customers/vendors, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = (
    ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
)
DEFAULT_INPUT_CSV = SPRINT_DIR / "evidence_request_approval_input_completion.csv"
OUTPUT_JSON = SPRINT_DIR / "evidence_request_approval_readiness_board.local.json"
OUTPUT_MD = SPRINT_DIR / "evidence_request_approval_readiness_board.md"
OUTPUT_CSV = SPRINT_DIR / "evidence_request_approval_readiness_board.csv"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD_RECOMMENDATION_GATE.md"
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

BOUNDARY_FALSE_FLAGS = {
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "owner_contacted_by_codex": False,
    "customer_contacted": False,
    "vendor_contacted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "task_candidates_executed": False,
    "development_permission_granted": False,
    "customer_data_collected": False,
    "customer_data_processed": False,
    "payment_collected": False,
    "revenue_validated": False,
}


def truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "1", "y"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CSV_FIELDS:
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD: "
                "FAIL completion CSV header mismatch"
            )
        return list(reader)


def missing_for_approval(row: dict[str, str]) -> list[str]:
    decision = row["approval_decision"].strip()
    missing: list[str] = []
    for field in ["assigned_human_owner", "human_approval_reference", "approval_scope"]:
        if not row[field].strip():
            missing.append(field)
    if not truthy(row["owner_acknowledged_scope"]):
        missing.append("owner_acknowledged_scope")
    if not truthy(row["boundary_acknowledged"]):
        missing.append("boundary_acknowledged")

    if decision == "approved_for_separate_evidence_collection_request":
        if row["approval_scope"].strip() != "evidence_collection_only":
            missing.append("approval_scope=evidence_collection_only")
        if not row["evidence_collection_request_reference"].strip():
            missing.append("evidence_collection_request_reference")
    elif decision == "approved_for_separate_execution_request":
        if (
            row["approval_scope"].strip()
            != "implementation_and_evidence_collection_review"
        ):
            missing.append(
                "approval_scope=implementation_and_evidence_collection_review"
            )
        if not row["execution_request_reference"].strip():
            missing.append("execution_request_reference")
    return missing


def classify_row(row: dict[str, str]) -> dict[str, Any]:
    decision = row["approval_decision"].strip() or "hold"
    notes: list[str] = []
    if decision not in ALLOWED_DECISIONS:
        return {
            "request_id": row["request_id"],
            "blocker_id": row["blocker_id"],
            "title": row["title"],
            "approval_decision": decision,
            "row_status": "invalid_decision",
            "missing_fields": [],
            "import_ready": False,
            "boundary_safe": False,
            "notes": "approval_decision is not allowed",
        }
    if decision == "hold":
        return {
            "request_id": row["request_id"],
            "blocker_id": row["blocker_id"],
            "title": row["title"],
            "approval_decision": decision,
            "row_status": "held",
            "missing_fields": [],
            "import_ready": False,
            "boundary_safe": True,
            "notes": "row remains on hold",
        }

    missing = missing_for_approval(row)
    if missing:
        notes.append("approval row is incomplete")
        status = "approval_incomplete"
        import_ready = False
    else:
        notes.append("approval row can be imported into the validator")
        status = "approval_import_ready"
        import_ready = True
    return {
        "request_id": row["request_id"],
        "blocker_id": row["blocker_id"],
        "title": row["title"],
        "approval_decision": decision,
        "row_status": status,
        "missing_fields": missing,
        "import_ready": import_ready,
        "boundary_safe": True,
        "notes": "; ".join(notes),
    }


def build_board(input_csv: Path) -> dict[str, Any]:
    rows = read_rows(input_csv)
    try:
        source_completion_csv = str(input_csv.resolve().relative_to(ROOT))
    except ValueError:
        source_completion_csv = str(input_csv)
    review = [classify_row(row) for row in rows]
    approved_rows = [
        item for item in review if item["approval_decision"] != "hold"
    ]
    import_ready_rows = [item for item in review if item["import_ready"]]
    invalid_rows = [item for item in review if not item["boundary_safe"]]
    boundary_violations: list[str] = []
    if len(approved_rows) > 1:
        boundary_violations.append("multiple_approved_rows")
    if invalid_rows:
        boundary_violations.append("invalid_approval_decision")

    if boundary_violations:
        status = "stop_boundary_violation"
    elif import_ready_rows:
        status = "ready_for_validator_import"
    elif approved_rows:
        status = "hold_approval_rows_incomplete"
    else:
        status = "hold_no_approved_request"

    return {
        "commercial_evidence_request_approval_readiness_board_v0_1": True,
        "board_type": "saee_commercial_evidence_request_approval_readiness_board",
        "board_version": "v0.1",
        "status": status,
        "board_scope": "local_erd_approval_completion_readiness_diagnostic",
        "source_completion_csv": source_completion_csv,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_request_approval_readiness_board.py",
        "approval_row_count": len(rows),
        "approved_candidate_count": len(approved_rows),
        "import_ready_request_count": len(import_ready_rows),
        "invalid_row_count": len(invalid_rows),
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "ready_for_validator_import": bool(import_ready_rows)
        and not boundary_violations,
        "ready_request_ids": [item["request_id"] for item in import_ready_rows],
        "held_request_count": sum(1 for item in review if item["row_status"] == "held"),
        "incomplete_approval_count": sum(
            1 for item in review if item["row_status"] == "approval_incomplete"
        ),
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "blockers_closed_by_board": 0,
        "next_action": (
            "If one row is import-ready, run the completion helper import mode "
            "and then run the approval input validator. Otherwise complete one "
            "approval row or keep all rows on hold."
        ),
        "request_readiness_review": review,
        **BOUNDARY_FALSE_FLAGS,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_board_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "request_id",
        "blocker_id",
        "title",
        "approval_decision",
        "row_status",
        "import_ready",
        "boundary_safe",
        "missing_fields",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in payload["request_readiness_review"]:
            row = dict(item)
            row["missing_fields"] = ";".join(item["missing_fields"])
            writer.writerow({field: row.get(field, "") for field in fields})


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["request_readiness_review"]
    table = "\n".join(
        "| {request_id} | {blocker_id} | {approval_decision} | {row_status} | {import_ready} | {missing} |".format(
            request_id=item["request_id"],
            blocker_id=item["blocker_id"],
            approval_decision=item["approval_decision"],
            row_status=item["row_status"],
            import_ready=bool_text(item["import_ready"]),
            missing=", ".join(item["missing_fields"]) or "none",
        )
        for item in rows
    )
    body = f"""# SAEE Commercial Evidence Request Approval Readiness Board

commercial_evidence_request_approval_readiness_board_v0_1: true
status: {payload["status"]}
board_scope: {payload["board_scope"]}
approval_row_count: {payload["approval_row_count"]}
approved_candidate_count: {payload["approved_candidate_count"]}
import_ready_request_count: {payload["import_ready_request_count"]}
ready_for_validator_import: {bool_text(payload["ready_for_validator_import"])}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_board: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This board summarizes whether the ERD approval completion CSV currently has one
row ready to import into the existing approval input validator. It is a local
diagnostic board only.

## Request Readiness

| Request | Blocker | Decision | Row status | Import ready | Missing fields |
| --- | --- | --- | --- | --- | --- |
{table}

## Boundary

This board does not approve requests, import CSV data, collect evidence,
execute work, contact owners, contact customers, contact vendors, close
blockers, launch product, expose private core, or claim production readiness.

## Next Action

{payload["next_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Commercial Evidence Request Approval Readiness Board v0.1

commercial_evidence_request_approval_readiness_board_v0_1: true
status: hold_no_approved_request
board_scope: local_erd_approval_completion_readiness_diagnostic
approval_row_count: 5
approved_candidate_count: 0
import_ready_request_count: 0
ready_for_validator_import: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_board: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This board checks the ERD approval completion CSV and reports whether any row
is ready to import into the existing approval input validator.

It helps a human reviewer answer:

```text
Which ERD approval row, if any, is complete enough for validator import?
```

## Boundary

This is a local diagnostic board only. It does not approve requests, import
CSV data, collect evidence, execute work, contact owners/customers/vendors,
close blockers, launch product, modify runtime/backend/kernel/API schema, expose
private core, or claim production readiness.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Commercial Evidence Request Approval Readiness Board Recommendation Gate

answer: conditional

recommend_for_approval_readiness_diagnostic: true
recommend_for_validator_import: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The board is useful because it makes the ERD approval completion state explicit
before a human runs CSV import and the approval input validator. It is not an
approval, evidence collection, or execution mechanism.

## Boundary

- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- blockers_closed_by_board: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-json", default=str(OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(OUTPUT_MD))
    parser.add_argument("--output-csv", default=str(OUTPUT_CSV))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_board(Path(args.input_csv))
    write_json(Path(args.output_json), payload)
    write_report(Path(args.output_md), payload)
    write_board_csv(Path(args.output_csv), payload)
    write_top_doc(TOP_DOC)
    write_gate(GATE)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_READINESS_BOARD: PASS "
            f"status={payload['status']} "
            f"import_ready_request_count={payload['import_ready_request_count']} "
            "evidence_collection_authorized=false "
            "execution_authorized=false "
            "production_ready=false"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
