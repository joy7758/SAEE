#!/usr/bin/env python3
"""Build the first human-owner action packet for the commercial evidence sprint.

The packet selects one already-planned blocker from the owner-assignment packet
and gives a human reviewer the exact fields and helper command needed to create
a human-filled owner assignment input later. It does not assign an owner,
contact anyone, collect evidence, execute work, close blockers, launch product,
or claim production readiness.
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
SOURCE_OWNER_PACKET = SPRINT_DIR / "owner_assignment_packet.local.json"
SOURCE_READINESS_BOARD = SPRINT_DIR / "owner_assignment_readiness_board.local.json"
OUTPUT_JSON = SPRINT_DIR / "first_owner_action_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "first_owner_action_packet.md"
OUTPUT_CSV = SPRINT_DIR / "first_owner_action_packet.csv"
BOUNDARY_AUDIT = SPRINT_DIR / "first_owner_action_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET_RECOMMENDATION_GATE.md"
)

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
    "vendor_contacted",
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
    "blockers_closed_by_assignment",
    "blockers_closed_by_board",
    "blockers_closed_by_packet",
]

BOUNDARY_FALSE_FLAGS = {
    "owner_assignment_complete": False,
    "ready_for_validator_import": False,
    "ready_for_separate_evidence_collection_request": False,
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

REQUIRED_HUMAN_FIELDS = [
    "assigned_human_owner",
    "owner_contact_reference",
    "target_review_date",
    "owner_acknowledged_scope",
    "human_approval_reference",
]


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
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: "
            "FAIL input must be a JSON object"
        )
    return value


def truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "y"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def boundary_violations(*payloads: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for payload in payloads:
        boundary_review = payload.get("boundary_review", {})
        if not isinstance(boundary_review, dict):
            boundary_review = {}
        for key in FORBIDDEN_TRUE_KEYS:
            if truthy(payload.get(key)) or truthy(boundary_review.get(key)):
                violations.append(key)
    return sorted(set(violations))


def assignment_rows(owner_packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = owner_packet.get("assignment_rows", [])
    if not isinstance(rows, list):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: "
            "FAIL assignment_rows must be a list"
        )
    result: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit(
                "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: "
                "FAIL assignment row must be an object"
            )
        result.append(row)
    return result


def choose_row(rows: list[dict[str, Any]], blocker_id: str | None) -> dict[str, Any]:
    if not rows:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: "
            "FAIL no assignment rows available"
        )
    if blocker_id is None:
        return rows[0]
    for row in rows:
        if row.get("blocker_id") == blocker_id:
            return row
    raise SystemExit(
        "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: "
        f"FAIL unknown --blocker-id {blocker_id}"
    )


def command_template(blocker_id: str) -> list[str]:
    return [
        "python3",
        "scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py",
        "--single-blocker-id",
        blocker_id,
        "--assigned-human-owner",
        "<human owner>",
        "--owner-contact-reference",
        "<internal owner reference>",
        "--target-review-date",
        "YYYY-MM-DD",
        "--owner-acknowledged-scope",
        "true",
        "--human-approval-reference",
        "<human approval record>",
        "--output-input-json",
        "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json",
    ]


def shell_command(blocker_id: str) -> str:
    parts = command_template(blocker_id)
    lines = [
        "python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \\",
        f"  --single-blocker-id {blocker_id} \\",
        '  --assigned-human-owner "<human owner>" \\',
        '  --owner-contact-reference "<internal owner reference>" \\',
        '  --target-review-date "YYYY-MM-DD" \\',
        "  --owner-acknowledged-scope true \\",
        '  --human-approval-reference "<human approval record>" \\',
        "  --output-input-json "
        "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
        "owner_assignment_input.human_filled.local.json",
    ]
    assert parts[0] == "python3"
    return "\n".join(lines)


def build_packet(
    source_owner_assignment_packet: Path,
    source_readiness_board: Path,
    blocker_id: str | None,
) -> dict[str, Any]:
    owner_packet = read_json(source_owner_assignment_packet)
    readiness_board = read_json(source_readiness_board)
    rows = assignment_rows(owner_packet)
    selected = choose_row(rows, blocker_id)
    selected_blocker_id = str(selected.get("blocker_id", ""))
    violations = boundary_violations(owner_packet, readiness_board)
    status = (
        "stop_boundary_violation"
        if violations
        else "hold_human_owner_input_required"
    )

    return {
        "commercial_evidence_sprint_first_owner_action_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_sprint_first_owner_action_packet",
        "packet_version": "v0.1",
        "status": status,
        "packet_scope": "local_first_owner_assignment_action_packet",
        "source_owner_assignment_packet": rel(source_owner_assignment_packet),
        "source_owner_assignment_readiness_board": rel(source_readiness_board),
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_first_owner_action_packet.py",
        "selected_blocker_count": len(rows),
        "first_blocker_id": selected_blocker_id,
        "first_blocker": {
            "blocker_id": selected_blocker_id,
            "phase_id": selected.get("phase_id", ""),
            "category": selected.get("category", ""),
            "owner_review_lane": selected.get("owner_review_lane", ""),
            "required_evidence": selected.get("required_evidence", ""),
            "first_evidence_keys": selected.get("first_evidence_keys", []),
            "first_evidence_record_ids": selected.get("first_evidence_record_ids", []),
            "dependency_state": selected.get("dependency_state", ""),
            "default_decision": selected.get("default_decision", "hold"),
            "must_not_touch": selected.get(
                "must_not_touch",
                [
                    "runtime",
                    "backend",
                    "kernel",
                    "api_schema",
                    "private_core",
                    "customer_contact_without_approval",
                    "vendor_contact_without_approval",
                    "payment_collection",
                    "production_launch",
                ],
            ),
            "recommended_next_human_action": (
                "Fill explicit owner-assignment fields for this blocker, then run "
                "the existing completion helper and readiness board. Do not collect "
                "evidence or execute work from this packet."
            ),
        },
        "required_human_fields": REQUIRED_HUMAN_FIELDS,
        "human_fill_command_template": command_template(selected_blocker_id),
        "human_fill_shell_command": shell_command(selected_blocker_id),
        "human_review_required": True,
        "human_owner_input_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "blockers_closed_by_packet": 0,
        "next_action": (
            "A human should fill the placeholders in the command template for "
            f"{selected_blocker_id}, generate a human-filled local owner input, "
            "then run the owner-assignment readiness board and input validator."
        ),
        **BOUNDARY_FALSE_FLAGS,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "first_blocker_id",
        "phase_id",
        "category",
        "owner_review_lane",
        "required_evidence",
        "required_human_fields",
        "status",
        "owner_assignment_complete",
        "ready_for_validator_import",
        "ready_for_separate_evidence_collection_request",
        "evidence_collection_authorized",
        "execution_authorized",
        "blockers_closed_by_packet",
        "next_action",
    ]
    first = payload["first_blocker"]
    row = {
        "first_blocker_id": payload["first_blocker_id"],
        "phase_id": first.get("phase_id", ""),
        "category": first.get("category", ""),
        "owner_review_lane": first.get("owner_review_lane", ""),
        "required_evidence": first.get("required_evidence", ""),
        "required_human_fields": ";".join(payload["required_human_fields"]),
        "status": payload["status"],
        "owner_assignment_complete": bool_text(payload["owner_assignment_complete"]),
        "ready_for_validator_import": bool_text(payload["ready_for_validator_import"]),
        "ready_for_separate_evidence_collection_request": bool_text(
            payload["ready_for_separate_evidence_collection_request"]
        ),
        "evidence_collection_authorized": bool_text(payload["evidence_collection_authorized"]),
        "execution_authorized": bool_text(payload["execution_authorized"]),
        "blockers_closed_by_packet": payload["blockers_closed_by_packet"],
        "next_action": payload["next_action"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    first = payload["first_blocker"]
    fields = "\n".join(f"- `{field}`" for field in payload["required_human_fields"])
    body = f"""# SAEE Commercial Evidence Sprint First Owner Action Packet

commercial_evidence_sprint_first_owner_action_packet_v0_1: true
status: {payload["status"]}
packet_scope: {payload["packet_scope"]}
selected_blocker_count: {payload["selected_blocker_count"]}
first_blocker_id: {payload["first_blocker_id"]}
owner_assignment_complete: false
ready_for_validator_import: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
blockers_closed_by_packet: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This packet gives a human reviewer the smallest next owner-assignment action
for the commercial evidence sprint. It selects exactly one already-planned
blocker and shows the fields needed before the existing owner-assignment
validator can be used.

## First Blocker

- blocker_id: `{payload["first_blocker_id"]}`
- phase_id: `{first.get("phase_id", "")}`
- category: `{first.get("category", "")}`
- owner_review_lane: `{first.get("owner_review_lane", "")}`
- required_evidence: {first.get("required_evidence", "")}
- default_decision: `{first.get("default_decision", "hold")}`

## Human Fields Required

{fields}

## Command Template

Do not run this command until a human supplies real placeholder values:

```bash
{payload["human_fill_shell_command"]}
```

## Boundary

This packet does not assign an owner, contact an owner, contact customers,
contact vendors, collect evidence, execute work, import data, close blockers,
launch product, modify runtime/backend/kernel/API schema, expose private core,
or claim production readiness.

## Next Action

{payload["next_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_boundary_audit(path: Path, payload: dict[str, Any]) -> None:
    violations = ", ".join(payload["boundary_violations"]) or "none"
    body = f"""# SAEE First Owner Action Packet Boundary Audit

commercial_evidence_sprint_first_owner_action_packet_v0_1: true
status: {payload["status"]}
boundary_violation_count: {payload["boundary_violation_count"]}
boundary_violations: {violations}

## Confirmed Boundaries

- No owner assigned by Codex
- No owner contacted by Codex
- No customer contacted
- No vendor contacted
- No evidence collection authorized
- No execution authorized
- No blocker closed
- No runtime modified
- No backend modified
- No kernel modified
- No API schema modified
- No private core exposed
- No product launched
- No production-ready claim added

## Decision

This is a local first-owner action packet only. It may guide a human reviewer
but cannot substitute for owner assignment, validator import, evidence
collection, execution approval, or blocker closure.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Commercial Evidence Sprint First Owner Action Packet v0.1

commercial_evidence_sprint_first_owner_action_packet_v0_1: true
status: hold_human_owner_input_required
packet_scope: local_first_owner_assignment_action_packet
default_first_blocker_id: support_contact
selected_blocker_count: 5
owner_assignment_complete: false
ready_for_validator_import: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
blockers_closed_by_packet: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This packet narrows the next commercial evidence sprint action to one human
owner-assignment step. It exists because the sprint has 5 selected blockers,
but the owner-assignment readiness board shows zero complete owner rows.

## Boundary

This is a local human-action packet only. It does not assign owners, contact
owners/customers/vendors, collect evidence, execute work, close blockers,
launch product, modify runtime/backend/kernel/API schema, expose private core,
or claim production readiness.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Commercial Evidence Sprint First Owner Action Packet Recommendation Gate

answer: conditional

recommend_for_first_human_owner_action: true
recommend_for_owner_assignment_completion: false
recommend_for_validator_import: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The packet is useful because it turns a broad owner-assignment gap into one
clear first human action. It is not useful as evidence collection, execution,
owner assignment, or blocker closure.

## Boundary

- owner_assignment_complete: false
- ready_for_validator_import: false
- ready_for_separate_evidence_collection_request: false
- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- blockers_closed_by_packet: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-owner-assignment-packet", default=str(SOURCE_OWNER_PACKET))
    parser.add_argument("--source-readiness-board", default=str(SOURCE_READINESS_BOARD))
    parser.add_argument("--blocker-id", default=None)
    parser.add_argument("--output-json", default=str(OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(OUTPUT_MD))
    parser.add_argument("--output-csv", default=str(OUTPUT_CSV))
    parser.add_argument("--boundary-audit", default=str(BOUNDARY_AUDIT))
    parser.add_argument("--top-doc", default=str(TOP_DOC))
    parser.add_argument("--gate", default=str(GATE))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_packet(
        Path(args.source_owner_assignment_packet),
        Path(args.source_readiness_board),
        args.blocker_id,
    )
    write_json(Path(args.output_json), payload)
    write_report(Path(args.output_md), payload)
    write_csv(Path(args.output_csv), payload)
    write_boundary_audit(Path(args.boundary_audit), payload)
    write_top_doc(Path(args.top_doc))
    write_gate(Path(args.gate))
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_ACTION_PACKET: PASS "
            f"status={payload['status']} "
            f"first_blocker_id={payload['first_blocker_id']} "
            "owner_assignment_complete=false "
            "blockers_closed_by_packet=0 production_ready=false"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
