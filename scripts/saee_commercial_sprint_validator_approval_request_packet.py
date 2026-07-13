#!/usr/bin/env python3
"""Build a human approval request packet for post-transfer validators.

This packet sits after the post-transfer validator sequencer. It records which
local validators would require explicit human approval before execution. It
does not run validators, approve validator execution, collect evidence, execute
builders, contact anyone, close blockers, launch product, or claim production
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
SEQUENCER_JSON = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

FALSE_FLAGS = [
    "validator_execution_authorized",
    "validators_run",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
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
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def approval_status(sequence_status: str, step_ready: bool) -> str:
    if sequence_status == "hold_template_transfer_required" or not step_ready:
        return "hold_template_transfer_required"
    return "hold_human_validator_approval_required"


def build_payload() -> dict[str, Any]:
    sequence = read_json(SEQUENCER_JSON)
    template_transfer_complete = sequence.get("template_transfer_complete") is True
    approval_rows: list[dict[str, Any]] = []
    for step in sequence.get("validator_steps", []):
        step_ready = step.get("ready_for_validator") is True
        approval_rows.append(
            {
                "sequence_id": step["sequence_id"],
                "blocker_id": step["blocker_id"],
                "validator_key": step["validator_key"],
                "runner": step["runner"],
                "smoke": step["smoke"],
                "human_filled_input_target": step["human_filled_input_target"],
                "validation_output": step["validation_output"],
                "ready_for_validator": step_ready,
                "human_validator_approval_required": True,
                "human_validator_approval_recorded": False,
                "human_validator_approval_reference": "",
                "approval_status": approval_status(sequence.get("status", ""), step_ready),
                "validator_execution_authorized": False,
                "validator_run": False,
                "validation_status": "not_run",
                "builder_ready": False,
                "blockers_closed_by_validator": 0,
            }
        )

    ready_validator_count = sum(1 for row in approval_rows if row["ready_for_validator"])
    status = (
        "hold_validator_approval_required"
        if template_transfer_complete and ready_validator_count == len(approval_rows)
        else "hold_template_transfer_required"
    )
    payload: dict[str, Any] = {
        "commercial_sprint_validator_approval_request_packet_v0_1": True,
        "packet_type": "controlled_validator_execution_approval_request_packet",
        "packet_scope": "post_transfer_validator_approval_request_only_no_validator_execution_no_evidence",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_validator_approval_request_packet.py",
        "source_post_transfer_validator_sequence_json": rel(SEQUENCER_JSON),
        "planned_validator_count": len(approval_rows),
        "approval_request_count": len(approval_rows),
        "ready_validator_count": ready_validator_count,
        "approved_validator_count": 0,
        "validator_execution_authorized_count": 0,
        "validators_run_count": 0,
        "builder_ready_count": 0,
        "blockers_closed_by_packet": 0,
        "template_transfer_complete": template_transfer_complete,
        "ready_for_validator_approval": template_transfer_complete
        and ready_validator_count == len(approval_rows),
        "ready_for_validator_execution": False,
        "human_validator_approval_required": True,
        "separate_validator_execution_request_required": True,
        "separate_evidence_builder_request_required": True,
        "next_human_action": (
            "Complete template transfer first. Then record explicit human approval "
            "for each validator before running validators in a separate command."
        ),
        "approval_requests": approval_rows,
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "sequence_id",
        "blocker_id",
        "validator_key",
        "runner",
        "ready_for_validator",
        "human_validator_approval_required",
        "human_validator_approval_recorded",
        "approval_status",
        "validator_execution_authorized",
        "validator_run",
        "validation_status",
        "builder_ready",
        "blockers_closed_by_validator",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["approval_requests"]:
            writer.writerow({field: row.get(field) for field in fields})


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {sequence_id} | {blocker_id} | {validator_key} | {ready_for_validator} | {human_validator_approval_recorded} | {validator_execution_authorized} |".format(
            **row
        )
        for row in payload["approval_requests"]
    )
    path.write_text(
        f"""# Commercial Sprint Validator Approval Request Packet v0.1

commercial_sprint_validator_approval_request_packet_v0_1: true
packet_type: {payload['packet_type']}
packet_scope: {payload['packet_scope']}
status: {payload['status']}
planned_validator_count: {payload['planned_validator_count']}
approval_request_count: {payload['approval_request_count']}
ready_validator_count: {payload['ready_validator_count']}
approved_validator_count: {payload['approved_validator_count']}
validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
validators_run_count: {payload['validators_run_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_packet: {payload['blockers_closed_by_packet']}
template_transfer_complete: {str(payload['template_transfer_complete']).lower()}
ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
ready_for_validator_execution: false
human_validator_approval_required: true
separate_validator_execution_request_required: true
separate_evidence_builder_request_required: true
validator_execution_authorized: false
validators_run: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
boundary_violation_count: 0
production_ready: false
customer_validated: false
product_launched: false

## Approval Requests

| Sequence | Blocker | Validator | Ready | Approval Recorded | Execution Authorized |
| --- | --- | --- | --- | --- | --- |
{rows}

## Boundary

This packet prepares human approval records for existing local validators only.
It does not approve or run validators, collect evidence, execute evidence
builders, contact customers or vendors, close blockers, launch product, or
claim production readiness.
""",
        encoding="utf-8",
    )


def write_boundary(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# Commercial Sprint Validator Approval Request Packet Boundary Audit

commercial_sprint_validator_approval_request_packet_v0_1: true
status: {payload['status']}
packet_scope: {payload['packet_scope']}
planned_validator_count: {payload['planned_validator_count']}
approval_request_count: {payload['approval_request_count']}
ready_validator_count: {payload['ready_validator_count']}
approved_validator_count: 0
validator_execution_authorized_count: 0
validators_run_count: 0
builder_ready_count: 0
blockers_closed_by_packet: 0
template_transfer_complete: {str(payload['template_transfer_complete']).lower()}
ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
ready_for_validator_execution: false
human_validator_approval_required: true
separate_validator_execution_request_required: true
separate_evidence_builder_request_required: true
validator_execution_authorized: false
validators_run: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
customer_contacted: false
vendor_contacted: false
external_calls_made: false
external_model_api_called: false
external_ai_assistant_tested: false
boundary_violation_count: 0

No validator execution approval was granted by this packet, and no validator
was run.
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Validator Approval Request Packet Recommendation Gate

answer: conditional
recommend_for_validator_approval_request_packet: true
recommend_for_human_validator_approval_collection: true
recommend_for_validator_execution: false
recommend_for_auto_approval: false
recommend_for_real_input_validation_without_human_approval: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

commercial_sprint_validator_approval_request_packet_v0_1: true
status: {payload['status']}
packet_scope: {payload['packet_scope']}
planned_validator_count: {payload['planned_validator_count']}
approval_request_count: {payload['approval_request_count']}
ready_validator_count: {payload['ready_validator_count']}
approved_validator_count: 0
validator_execution_authorized_count: 0
validators_run_count: 0
builder_ready_count: 0
blockers_closed_by_packet: 0
template_transfer_complete: {str(payload['template_transfer_complete']).lower()}
ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
ready_for_validator_execution: false
human_validator_approval_required: true
separate_validator_execution_request_required: true
separate_evidence_builder_request_required: true
validator_execution_authorized: false
validators_run: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
boundary_violation_count: 0
production_ready: false
customer_validated: false
product_launched: false

Reason: this packet is recommendable only as a local approval-record surface.
It is not recommendable as automatic validator execution, evidence collection,
builder execution, blocker closure, launch, or production-readiness proof.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_report(OUT_MD, payload)
    write_boundary(OUT_BOUNDARY, payload)
    write_report(TOP_DOC, payload)
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_APPROVAL_REQUEST_PACKET: PASS "
        f"status={payload['status']} "
        f"approval_request_count={payload['approval_request_count']} "
        f"approved_validator_count={payload['approved_validator_count']} "
        "validators_run=false production_ready=false"
    )


if __name__ == "__main__":
    main()
