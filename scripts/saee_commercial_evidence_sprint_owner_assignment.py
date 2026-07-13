#!/usr/bin/env python3
"""Build a local owner-assignment packet for the current evidence sprint.

This packet turns the selected ready-for-human-review blockers into an owner
assignment template. It does not collect evidence, execute tasks, contact
customers or vendors, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SPRINT_PATH = SPRINT_DIR / "commercial_next_evidence_sprint.local.json"
OUTPUT_JSON = SPRINT_DIR / "owner_assignment_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "owner_assignment_packet.md"
OUTPUT_CSV = SPRINT_DIR / "owner_assignment_packet.csv"
BOUNDARY_PATH = SPRINT_DIR / "owner_assignment_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_RECOMMENDATION_GATE.md"


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
    return json.loads(path.read_text(encoding="utf-8"))


def assignment_rows(sprint: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sprint.get("selected_blockers", []):
        rows.append(
            {
                "blocker_id": item["blocker_id"],
                "phase_id": item["phase_id"],
                "category": item["category"],
                "owner_review_lane": item["owner_review_lane"],
                "dependency_state": item["dependency_state"],
                "required_evidence": item["required_evidence"],
                "first_evidence_record_ids": [
                    evidence["collection_record_id"]
                    for evidence in item.get("first_evidence_items", [])
                ],
                "first_evidence_keys": [
                    evidence["evidence_key"] for evidence in item.get("first_evidence_items", [])
                ],
                "assigned_human_owner": "",
                "owner_contact_reference": "",
                "target_review_date": "",
                "assignment_status": "unassigned",
                "default_decision": "hold",
                "requires_human_owner": True,
                "requires_human_approval": True,
                "requires_separate_execution_request": True,
                "evidence_collection_authorized": False,
                "execution_authorized": False,
                "closure_authorized": False,
                "owner_contacted_by_codex": False,
                "must_not_touch": [
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
                "recommended_next_human_action": (
                    "Assign a human owner and create a separate approved evidence "
                    "collection request before any collection or execution occurs."
                ),
            }
        )
    return rows


def build_packet() -> dict[str, Any]:
    sprint = read_json(SPRINT_PATH)
    rows = assignment_rows(sprint)
    assigned_count = sum(1 for row in rows if row["assigned_human_owner"].strip())
    packet: dict[str, Any] = {
        "packet_type": "saee_commercial_evidence_sprint_owner_assignment",
        "packet_version": "0.1",
        "status": "hold_owner_assignment_required",
        "assignment_scope": "local_owner_assignment_template_for_selected_evidence_sprint",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_owner_assignment.py",
        "source_sprint": rel(SPRINT_PATH),
        "source_sprint_status": sprint.get("sprint_status"),
        "production_blocker_count": sprint.get("production_blocker_count", 24),
        "open_blocker_count": sprint.get("open_blocker_count", 24),
        "selected_blocker_count": len(rows),
        "selected_blocker_ids": [row["blocker_id"] for row in rows],
        "assignment_rows": rows,
        "assignment_row_count": len(rows),
        "assigned_owner_count": assigned_count,
        "unassigned_owner_count": len(rows) - assigned_count,
        "all_owners_assigned": assigned_count == len(rows) and bool(rows),
        "human_owner_assignment_required": True,
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "blockers_closed_by_assignment": 0,
        "blockers_ready_to_close": [],
        "next_allowed_action": (
            "A human may fill assigned_human_owner and target_review_date, then "
            "create a separate explicit evidence-collection or implementation request."
        ),
    }
    for flag in FALSE_FLAGS:
        packet[flag] = False
    return packet


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(packet: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "phase_id",
        "category",
        "owner_review_lane",
        "dependency_state",
        "assigned_human_owner",
        "target_review_date",
        "assignment_status",
        "requires_human_approval",
        "evidence_collection_authorized",
        "execution_authorized",
        "closure_authorized",
        "recommended_next_human_action",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in packet["assignment_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def markdown_table(packet: dict[str, Any]) -> str:
    lines = [
        "| Blocker | Lane | Owner | Target Date | Assignment Status | Evidence Collection | Execution |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in packet["assignment_rows"]:
        lines.append(
            "| {blocker} | {lane} | {owner} | {date} | {status} | {collection} | {execution} |".format(
                blocker=row["blocker_id"],
                lane=row["owner_review_lane"],
                owner=row["assigned_human_owner"] or "unassigned",
                date=row["target_review_date"] or "unset",
                status=row["assignment_status"],
                collection=str(row["evidence_collection_authorized"]).lower(),
                execution=str(row["execution_authorized"]).lower(),
            )
        )
    return "\n".join(lines)


def write_markdown(packet: dict[str, Any]) -> None:
    OUTPUT_MD.write_text(
        f"""# SAEE Commercial Evidence Sprint Owner Assignment Packet

Status: {packet['status']}.

This packet assigns human ownership slots for the selected commercial evidence
sprint blockers. It does not contact owners, collect evidence, execute tasks,
close blockers, launch product, or claim production readiness.

## Summary

- packet_type: {packet['packet_type']}
- assignment_scope: {packet['assignment_scope']}
- source_sprint_status: {packet['source_sprint_status']}
- production_blocker_count: {packet['production_blocker_count']}
- open_blocker_count: {packet['open_blocker_count']}
- selected_blocker_count: {packet['selected_blocker_count']}
- assigned_owner_count: {packet['assigned_owner_count']}
- unassigned_owner_count: {packet['unassigned_owner_count']}
- all_owners_assigned: {str(packet['all_owners_assigned']).lower()}
- human_owner_assignment_required: true
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_assignment: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Assignment Table

{markdown_table(packet)}

## Boundary

Owner assignment is a planning and accountability surface only. Any evidence
collection, owner contact, implementation, product change, customer contact,
vendor contact, payment setup, production launch, or blocker closure requires a
separate explicit human-approved request.
""",
        encoding="utf-8",
    )
    BOUNDARY_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Owner Assignment Boundary Audit

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- public_sdk_released: false
- external_calls_made: false
- external_model_api_called: false
- external_ai_assistant_tested: false
- owner_contacted_by_codex: false
- evidence_collection_authorized: false
- execution_authorized: false
- task_candidates_executed: false
- blockers_closed_by_assignment: 0

Final boundary decision: local owner assignment planning only.
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Commercial Evidence Sprint Owner Assignment v0.1

commercial_evidence_sprint_owner_assignment_v0_1: true
status: {packet['status']}
assignment_scope: local_owner_assignment_template_for_selected_evidence_sprint
selected_blocker_count: {packet['selected_blocker_count']}
assigned_owner_count: {packet['assigned_owner_count']}
unassigned_owner_count: {packet['unassigned_owner_count']}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_assignment: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This artifact gives the current commercial next evidence sprint a
machine-readable human-owner assignment surface. It helps the team move from a
selected blocker list to accountable human review without executing any work.

## Entrypoints

- source sprint: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.local.json`
- assignment JSON: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.local.json`
- assignment report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.md`
- assignment CSV: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.csv`
- boundary audit: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_boundary_audit.md`
- script: `scripts/saee_commercial_evidence_sprint_owner_assignment.py`
- smoke: `scripts/saee_commercial_evidence_sprint_owner_assignment_smoke.py`

## Boundary

This is owner-assignment planning only. It does not contact owners, collect
evidence, execute tasks, modify product behavior, change backend/runtime/kernel
or API schema, expose private core, contact customers or vendors, launch
product, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Owner Assignment Recommendation Gate

answer: conditional

recommend_for_owner_assignment_planning: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The owner-assignment packet is useful for formal commercial readiness because
it turns selected sprint blockers into explicit human ownership slots. It does
not authorize collection, execution, customer contact, vendor contact, blocker
closure, product launch, or production readiness.

## Boundary

evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
task_candidates_executed: false
blockers_closed_by_assignment: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
""",
        encoding="utf-8",
    )


def main() -> None:
    packet = build_packet()
    write_json(OUTPUT_JSON, packet)
    write_csv(packet)
    write_markdown(packet)
    print(
        "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT: PASS "
        f"status={packet['status']} selected_blockers={packet['selected_blocker_count']} "
        "evidence_collection_authorized=false execution_authorized=false "
        "blockers_closed_by_assignment=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
