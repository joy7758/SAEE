#!/usr/bin/env python3
"""Build a local owner-assignment readiness board without assigning owners.

The board reads the human-fillable owner-assignment input JSON and reports
which selected blocker rows, if any, are complete enough to import into the
existing owner-assignment input validator. It does not contact owners, collect
evidence, execute work, close blockers, launch product, or claim production
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
DEFAULT_INPUT_JSON = SPRINT_DIR / "owner_assignment_input.template.json"
OUTPUT_JSON = SPRINT_DIR / "owner_assignment_readiness_board.local.json"
OUTPUT_MD = SPRINT_DIR / "owner_assignment_readiness_board.md"
OUTPUT_CSV = SPRINT_DIR / "owner_assignment_readiness_board.csv"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD_RECOMMENDATION_GATE.md"
)

SELECTED_BLOCKER_IDS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]

REQUIRED_ROW_FIELDS = [
    "assigned_human_owner",
    "target_review_date",
    "human_approval_reference",
]

FORBIDDEN_TRUE_KEYS = [
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
    "blockers_closed_by_validator",
    "blockers_closed_by_board",
]

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


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD: "
            "FAIL input must be a JSON object"
        )
    return value


def truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "y"}
    return False


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    boundary_review = data.get("boundary_review", {})
    if not isinstance(boundary_review, dict):
        violations.append("boundary_review_missing_or_invalid")
        boundary_review = {}
    for key in FORBIDDEN_TRUE_KEYS:
        if truthy(data.get(key)) or truthy(boundary_review.get(key)):
            violations.append(key)
    return sorted(set(violations))


def rows_by_blocker(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = data.get("assignment_inputs", [])
    if not isinstance(rows, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str):
            result[row["blocker_id"]] = row
    return result


def missing_fields_for_row(row: dict[str, Any] | None) -> list[str]:
    if row is None:
        return ["assignment_input_row"]
    missing = [
        field
        for field in REQUIRED_ROW_FIELDS
        if not str(row.get(field, "")).strip()
    ]
    if row.get("owner_acknowledged_scope") is not True:
        missing.append("owner_acknowledged_scope")
    return missing


def has_any_owner_input(row: dict[str, Any] | None) -> bool:
    if row is None:
        return False
    for field in [
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "human_approval_reference",
        "evidence_collection_request_reference",
        "notes",
    ]:
        if str(row.get(field, "")).strip():
            return True
    return row.get("owner_acknowledged_scope") is True


def classify_row(
    blocker_id: str,
    row: dict[str, Any] | None,
    boundary_risk: bool,
) -> dict[str, Any]:
    missing = missing_fields_for_row(row)
    if boundary_risk:
        status = "boundary_risk"
        ready = False
        action = "fix_boundary_flags"
    elif not missing:
        status = "complete"
        ready = True
        action = "run_input_validator"
    elif has_any_owner_input(row):
        status = "partial"
        ready = False
        action = "fill_owner_fields"
    else:
        status = "missing"
        ready = False
        action = "fill_owner_fields"

    row = row or {}
    return {
        "blocker_id": blocker_id,
        "phase_id": row.get("phase_id", ""),
        "category": row.get("category", ""),
        "owner_review_lane": row.get("owner_review_lane", ""),
        "assigned_human_owner": row.get("assigned_human_owner", ""),
        "target_review_date": row.get("target_review_date", ""),
        "owner_acknowledged_scope": row.get("owner_acknowledged_scope") is True,
        "human_approval_reference": row.get("human_approval_reference", ""),
        "owner_assignment_status": status,
        "missing_fields": missing,
        "ready_for_validator_import": ready,
        "boundary_safe": not boundary_risk,
        "recommended_human_action": action,
        "notes": (
            "owner assignment row can be checked by the validator"
            if ready
            else "owner assignment row is not ready for validator import"
        ),
    }


def build_board(input_json: Path) -> dict[str, Any]:
    data = read_json(input_json)
    violations = boundary_violations(data)
    boundary_risk = bool(violations)
    rows = rows_by_blocker(data)
    review = [
        classify_row(blocker_id, rows.get(blocker_id), boundary_risk)
        for blocker_id in SELECTED_BLOCKER_IDS
    ]
    complete = [item for item in review if item["owner_assignment_status"] == "complete"]
    partial = [item for item in review if item["owner_assignment_status"] == "partial"]
    missing = [item for item in review if item["owner_assignment_status"] == "missing"]
    risk = [item for item in review if item["owner_assignment_status"] == "boundary_risk"]
    import_ready = [item for item in review if item["ready_for_validator_import"]]

    if violations:
        status = "stop_boundary_violation"
    elif import_ready:
        status = "ready_for_validator_import"
    else:
        status = "hold_no_complete_owner_assignment"

    return {
        "commercial_evidence_sprint_owner_assignment_readiness_board_v0_1": True,
        "board_type": "saee_commercial_evidence_sprint_owner_assignment_readiness_board",
        "board_version": "v0.1",
        "status": status,
        "board_scope": "local_owner_assignment_input_readiness_diagnostic",
        "source_input_json": rel(input_json),
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board.py",
        "selected_blocker_count": len(SELECTED_BLOCKER_IDS),
        "complete_owner_assignment_count": len(complete),
        "partial_owner_assignment_count": len(partial),
        "missing_owner_assignment_count": len(missing),
        "boundary_risk_assignment_count": len(risk),
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "import_ready_assignment_count": len(import_ready),
        "ready_for_validator_import": bool(import_ready) and not violations,
        "ready_blocker_ids": [item["blocker_id"] for item in import_ready],
        "human_review_required": True,
        "separate_validator_required": True,
        "ready_for_separate_evidence_collection_request": False,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "blockers_closed_by_board": 0,
        "next_action": (
            "If one or more rows are import-ready, run the existing owner "
            "assignment input validator on the corresponding human-filled JSON. "
            "Otherwise complete owner fields or keep the sprint on hold."
        ),
        "owner_assignment_readiness_review": review,
        **BOUNDARY_FALSE_FLAGS,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_board_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "phase_id",
        "category",
        "owner_review_lane",
        "assigned_human_owner",
        "target_review_date",
        "owner_acknowledged_scope",
        "human_approval_reference",
        "owner_assignment_status",
        "ready_for_validator_import",
        "boundary_safe",
        "recommended_human_action",
        "missing_fields",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in payload["owner_assignment_readiness_review"]:
            row = dict(item)
            row["missing_fields"] = ";".join(item["missing_fields"])
            writer.writerow({field: row.get(field, "") for field in fields})


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["owner_assignment_readiness_review"]
    table = "\n".join(
        "| {blocker_id} | {owner} | {status} | {ready} | {action} | {missing} |".format(
            blocker_id=item["blocker_id"],
            owner=item["assigned_human_owner"] or "none",
            status=item["owner_assignment_status"],
            ready=bool_text(item["ready_for_validator_import"]),
            action=item["recommended_human_action"],
            missing=", ".join(item["missing_fields"]) or "none",
        )
        for item in rows
    )
    body = f"""# SAEE Commercial Evidence Sprint Owner Assignment Readiness Board

commercial_evidence_sprint_owner_assignment_readiness_board_v0_1: true
status: {payload["status"]}
board_scope: {payload["board_scope"]}
selected_blocker_count: {payload["selected_blocker_count"]}
complete_owner_assignment_count: {payload["complete_owner_assignment_count"]}
partial_owner_assignment_count: {payload["partial_owner_assignment_count"]}
missing_owner_assignment_count: {payload["missing_owner_assignment_count"]}
import_ready_assignment_count: {payload["import_ready_assignment_count"]}
ready_for_validator_import: {bool_text(payload["ready_for_validator_import"])}
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
blockers_closed_by_board: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This board summarizes whether the owner-assignment input JSON currently has
rows complete enough to import into the existing owner-assignment input
validator. It is a local diagnostic board only.

## Owner Assignment Readiness

| Blocker | Owner | Status | Validator import ready | Recommended human action | Missing fields |
| --- | --- | --- | --- | --- | --- |
{table}

## Boundary

This board does not assign owners, contact owners, import data, collect
evidence, execute work, contact customers, contact vendors, close blockers,
launch product, expose private core, or claim production readiness.

## Next Action

{payload["next_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Commercial Evidence Sprint Owner Assignment Readiness Board v0.1

commercial_evidence_sprint_owner_assignment_readiness_board_v0_1: true
status: hold_no_complete_owner_assignment
board_scope: local_owner_assignment_input_readiness_diagnostic
selected_blocker_count: 5
complete_owner_assignment_count: 0
partial_owner_assignment_count: 0
missing_owner_assignment_count: 5
import_ready_assignment_count: 0
ready_for_validator_import: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
blockers_closed_by_board: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This board checks the owner-assignment input JSON and reports which selected
commercial blocker rows are complete enough for validator import.

It helps a human reviewer answer:

```text
Which owner-assignment rows, if any, are complete enough for validator import?
```

## Boundary

This is a local diagnostic board only. It does not assign owners, contact
owners/customers/vendors, import data, collect evidence, execute work, close
blockers, launch product, modify runtime/backend/kernel/API schema, expose
private core, or claim production readiness.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Commercial Evidence Sprint Owner Assignment Readiness Board Recommendation Gate

answer: conditional

recommend_for_owner_assignment_readiness_diagnostic: true
recommend_for_validator_import: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The board is useful because it makes owner-assignment completeness explicit
before a human runs the owner-assignment input validator. It is not an owner
assignment, evidence collection, execution, or blocker-closure mechanism.

## Boundary

- ready_for_separate_evidence_collection_request: false
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
    parser.add_argument("--input-json", default=str(DEFAULT_INPUT_JSON))
    parser.add_argument("--output-json", default=str(OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(OUTPUT_MD))
    parser.add_argument("--output-csv", default=str(OUTPUT_CSV))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_board(Path(args.input_json))
    write_json(Path(args.output_json), payload)
    write_report(Path(args.output_md), payload)
    write_board_csv(Path(args.output_csv), payload)
    write_top_doc(TOP_DOC)
    write_gate(GATE)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_READINESS_BOARD: PASS "
            f"status={payload['status']} "
            f"import_ready_assignment_count={payload['import_ready_assignment_count']} "
            "evidence_collection_authorized=false "
            "execution_authorized=false "
            "production_ready=false"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
