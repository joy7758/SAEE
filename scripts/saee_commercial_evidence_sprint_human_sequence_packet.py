#!/usr/bin/env python3
"""Build the human-only execution sequence for the commercial evidence sprint.

The sequence packet prevents accidental jumps from owner assignment directly
to evidence collection or blocker closure. It reads existing local readiness
surfaces and emits the ordered human gates needed for one commercial blocker,
starting with the current first-owner action. It does not assign owners,
approve requests, contact anyone, collect evidence, execute work, close
blockers, launch product, or claim production readiness.
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
CLOSURE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board"
)
FIRST_OWNER_PACKET = SPRINT_DIR / "first_owner_action_packet.local.json"
FIRST_OWNER_INPUT_REQUEST_PACKET = SPRINT_DIR / "first_owner_input_request_packet.local.json"
FIRST_OWNER_INPUT_REQUEST_PACKET_MD = SPRINT_DIR / "first_owner_input_request_packet.md"
OWNER_READINESS_BOARD = SPRINT_DIR / "owner_assignment_readiness_board.local.json"
APPROVAL_READINESS_BOARD = SPRINT_DIR / "evidence_request_approval_readiness_board.local.json"
CLOSURE_READINESS_BOARD = CLOSURE_DIR / "closure_readiness_board.local.json"
OUTPUT_JSON = SPRINT_DIR / "human_sequence_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "human_sequence_packet.md"
OUTPUT_CSV = SPRINT_DIR / "human_sequence_packet.csv"
BOUNDARY_AUDIT = SPRINT_DIR / "human_sequence_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET_RECOMMENDATION_GATE.md"
)

FALSE_FLAGS = {
    "owner_assigned_by_codex": False,
    "owner_contacted_by_codex": False,
    "request_approved_by_codex": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "blocker_closure_authorized": False,
    "ready_for_validator_import": False,
    "ready_for_separate_evidence_collection_request": False,
    "task_candidates_executed": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "vendor_contacted": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "customer_data_collected": False,
    "customer_data_processed": False,
    "payment_collected": False,
    "revenue_validated": False,
}

FORBIDDEN_TRUE_KEYS = [
    *FALSE_FLAGS.keys(),
    "blockers_closed_by_packet",
    "blockers_closed_by_board",
    "blockers_closed_by_validator",
    "closure_candidate_count",
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
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET: "
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


def current_status(
    first_owner: dict[str, Any],
    owner_board: dict[str, Any],
    approval_board: dict[str, Any],
    closure_board: dict[str, Any],
    violations: list[str],
) -> tuple[str, str, str]:
    if violations:
        return (
            "stop_boundary_violation",
            "SEQ-000",
            "Resolve boundary violation before any commercial evidence sprint action.",
        )
    if closure_board.get("closure_candidate_count", 0):
        return (
            "hold_final_closure_review_required",
            "SEQ-007",
            "A human final closure review is required before any blocker can close.",
        )
    if approval_board.get("import_ready_request_count", 0):
        return (
            "hold_approval_validator_required",
            "SEQ-004",
            "Run the ERD approval input validator on the human-filled approval input.",
        )
    if owner_board.get("import_ready_assignment_count", 0):
        return (
            "hold_owner_validator_required",
            "SEQ-002",
            "Run the owner-assignment input validator on the human-filled owner input.",
        )
    return (
        "hold_first_owner_input_required",
        "SEQ-001",
        "Fill the first owner-assignment fields for support_contact; do not collect evidence yet.",
    )


def build_steps(first_blocker_id: str, request_packet_markdown_path: Path) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "SEQ-001",
            "title": "Fill first owner-assignment input",
            "target_blocker_id": first_blocker_id,
            "human_action": (
                "Open the first owner input request packet and fill owner fields "
                "for the first blocker using its command template."
            ),
            "entrypoint": rel(request_packet_markdown_path),
            "required_before_next_step": [
                "assigned_human_owner",
                "owner_contact_reference",
                "target_review_date",
                "owner_acknowledged_scope",
                "human_approval_reference",
            ],
            "must_not_do": [
                "contact customer",
                "collect evidence",
                "execute work",
                "close blocker",
            ],
            "automated_by_codex": False,
            "current_step_by_default": True,
        },
        {
            "step_id": "SEQ-002",
            "title": "Run owner-assignment validator",
            "target_blocker_id": first_blocker_id,
            "human_action": "Run the owner-assignment readiness board and validator on human-filled local input.",
            "entrypoint": rel(OWNER_READINESS_BOARD),
            "required_before_next_step": [
                "owner_assignment_complete",
                "validator_pass",
            ],
            "must_not_do": [
                "collect evidence without separate request",
                "execute work",
                "close blocker",
            ],
            "automated_by_codex": False,
            "current_step_by_default": False,
        },
        {
            "step_id": "SEQ-003",
            "title": "Fill ERD approval input",
            "target_blocker_id": first_blocker_id,
            "human_action": "If owner validation passes, fill one ERD approval row for a separate evidence collection request.",
            "entrypoint": rel(SPRINT_DIR / "evidence_request_approval_input_completion.csv"),
            "required_before_next_step": [
                "approval_decision",
                "approval_scope",
                "human_approval_reference",
                "boundary_acknowledged",
                "evidence_collection_request_reference",
            ],
            "must_not_do": [
                "approve more than one ERD row by default",
                "execute implementation work",
                "close blocker",
            ],
            "automated_by_codex": False,
            "current_step_by_default": False,
        },
        {
            "step_id": "SEQ-004",
            "title": "Run ERD approval validator",
            "target_blocker_id": first_blocker_id,
            "human_action": "Run approval readiness board and approval input validator.",
            "entrypoint": rel(APPROVAL_READINESS_BOARD),
            "required_before_next_step": [
                "approved_request_count=1",
                "ready_for_separate_evidence_collection_request=true",
            ],
            "must_not_do": [
                "treat approval input as evidence itself",
                "close blocker",
            ],
            "automated_by_codex": False,
            "current_step_by_default": False,
        },
        {
            "step_id": "SEQ-005",
            "title": "Open separate evidence collection request",
            "target_blocker_id": first_blocker_id,
            "human_action": "Create a separate human-approved evidence collection request using the approved ERD reference.",
            "entrypoint": rel(SPRINT_DIR / "evidence_request_draft_packet.md"),
            "required_before_next_step": [
                "separate_evidence_collection_request",
                "scope",
                "owner",
                "allowed evidence files",
            ],
            "must_not_do": [
                "modify runtime",
                "modify backend",
                "modify API schema",
                "expose private core",
            ],
            "automated_by_codex": False,
            "current_step_by_default": False,
        },
        {
            "step_id": "SEQ-006",
            "title": "Collect evidence in separate request",
            "target_blocker_id": first_blocker_id,
            "human_action": "Only after separate approval, collect or build the scoped evidence artifact.",
            "entrypoint": "separate_human_approved_evidence_collection_request_required",
            "required_before_next_step": [
                "real evidence artifact",
                "source reference",
                "boundary audit",
            ],
            "must_not_do": [
                "infer missing evidence",
                "use fixture as production evidence",
                "close blocker directly",
            ],
            "automated_by_codex": False,
            "current_step_by_default": False,
        },
        {
            "step_id": "SEQ-007",
            "title": "Run go/no-go and closure review",
            "target_blocker_id": first_blocker_id,
            "human_action": "Run commercial go/no-go and closure readiness checks before any human final closure decision.",
            "entrypoint": rel(CLOSURE_READINESS_BOARD),
            "required_before_next_step": [
                "commercial_go_no_go_pass",
                "closure_candidate",
                "human_final_closure_approval",
            ],
            "must_not_do": [
                "auto-close blocker",
                "claim production readiness",
                "launch product",
            ],
            "automated_by_codex": False,
            "current_step_by_default": False,
        },
    ]


def build_packet(
    first_owner_path: Path,
    first_owner_input_request_path: Path,
    owner_board_path: Path,
    approval_board_path: Path,
    closure_board_path: Path,
) -> dict[str, Any]:
    first_owner = read_json(first_owner_path)
    first_owner_input_request = read_json(first_owner_input_request_path)
    owner_board = read_json(owner_board_path)
    approval_board = read_json(approval_board_path)
    closure_board = read_json(closure_board_path)
    violations = boundary_violations(
        first_owner,
        first_owner_input_request,
        owner_board,
        approval_board,
        closure_board,
    )
    first_blocker_id = str(first_owner.get("first_blocker_id") or "support_contact")
    status, current_step_id, next_human_action = current_status(
        first_owner, owner_board, approval_board, closure_board, violations
    )
    steps = build_steps(first_blocker_id, FIRST_OWNER_INPUT_REQUEST_PACKET_MD)
    for step in steps:
        step["current_step"] = step["step_id"] == current_step_id
    current_step = next((step for step in steps if step["current_step"] is True), steps[0])
    command_template = str(
        first_owner_input_request.get("next_generation_command_template", "")
    ).strip()

    return {
        "commercial_evidence_sprint_human_sequence_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_sprint_human_sequence_packet",
        "packet_version": "v0.1",
        "status": status,
        "packet_scope": "local_human_only_commercial_evidence_sprint_sequence",
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_human_sequence_packet.py",
        "source_files": {
            "first_owner_action_packet": rel(first_owner_path),
            "first_owner_input_request_packet": rel(first_owner_input_request_path),
            "first_owner_input_request_packet_markdown": rel(
                FIRST_OWNER_INPUT_REQUEST_PACKET_MD
            ),
            "owner_assignment_readiness_board": rel(owner_board_path),
            "evidence_request_approval_readiness_board": rel(approval_board_path),
            "closure_readiness_board": rel(closure_board_path),
        },
        "first_blocker_id": first_blocker_id,
        "current_step_id": current_step_id,
        "current_step_entrypoint": current_step.get("entrypoint", ""),
        "current_step_command_template": command_template if current_step_id == "SEQ-001" else "",
        "current_step_command_template_available": bool(
            command_template and current_step_id == "SEQ-001"
        ),
        "next_human_action": next_human_action,
        "sequence_step_count": len(steps),
        "sequence_steps": steps,
        "owner_assignment_status": owner_board.get("status", ""),
        "owner_import_ready_count": owner_board.get("import_ready_assignment_count", 0),
        "approval_readiness_status": approval_board.get("status", ""),
        "approval_import_ready_count": approval_board.get("import_ready_request_count", 0),
        "closure_readiness_status": closure_board.get("status", ""),
        "closure_candidate_count": closure_board.get("closure_candidate_count", 0),
        "human_review_required": True,
        "separate_owner_input_required": True,
        "separate_validator_required": True,
        "separate_approval_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_final_closure_approval_required": True,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "blockers_closed_by_packet": 0,
        **FALSE_FLAGS,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "step_id",
        "current_step",
        "target_blocker_id",
        "title",
        "entrypoint",
        "human_action",
        "required_before_next_step",
        "must_not_do",
        "automated_by_codex",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for step in payload["sequence_steps"]:
            writer.writerow(
                {
                    "step_id": step["step_id"],
                    "current_step": bool_text(step["current_step"]),
                    "target_blocker_id": step["target_blocker_id"],
                    "title": step["title"],
                    "entrypoint": step.get("entrypoint", ""),
                    "human_action": step["human_action"],
                    "required_before_next_step": ";".join(step["required_before_next_step"]),
                    "must_not_do": ";".join(step["must_not_do"]),
                    "automated_by_codex": bool_text(step["automated_by_codex"]),
                }
            )


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {step_id} | {current} | {title} | {action} | {must_not} |".format(
            step_id=step["step_id"],
            current=bool_text(step["current_step"]),
            title=step["title"],
            action=step["human_action"],
            must_not=", ".join(step["must_not_do"]),
        )
        for step in payload["sequence_steps"]
    )
    body = f"""# SAEE Commercial Evidence Sprint Human Sequence Packet

commercial_evidence_sprint_human_sequence_packet_v0_1: true
status: {payload["status"]}
packet_scope: {payload["packet_scope"]}
first_blocker_id: {payload["first_blocker_id"]}
current_step_id: {payload["current_step_id"]}
current_step_entrypoint: {payload["current_step_entrypoint"]}
current_step_command_template_available: {bool_text(payload["current_step_command_template_available"])}
sequence_step_count: {payload["sequence_step_count"]}
owner_import_ready_count: {payload["owner_import_ready_count"]}
approval_import_ready_count: {payload["approval_import_ready_count"]}
closure_candidate_count: {payload["closure_candidate_count"]}
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

This packet gives the human-only sequence for moving one commercial evidence
sprint blocker from owner assignment toward evidence collection review without
skipping gates. It is a sequencing surface, not an execution mechanism.

## Sequence

| Step | Current | Title | Human action | Must not do |
| --- | --- | --- | --- | --- |
{rows}

## Current Next Human Action

{payload["next_human_action"]}

## Current Step Command Template

```bash
{payload["current_step_command_template"]}
```

## Boundary

This packet does not assign owners, approve requests, contact anyone, import
data, collect evidence, execute work, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, or claim production
readiness.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_boundary_audit(path: Path, payload: dict[str, Any]) -> None:
    violations = ", ".join(payload["boundary_violations"]) or "none"
    body = f"""# SAEE Commercial Evidence Sprint Human Sequence Boundary Audit

commercial_evidence_sprint_human_sequence_packet_v0_1: true
status: {payload["status"]}
boundary_violation_count: {payload["boundary_violation_count"]}
boundary_violations: {violations}

## Confirmed Boundaries

- No owner assigned by Codex
- No owner contacted by Codex
- No request approved by Codex
- No evidence collection authorized
- No execution authorized
- No blocker closure authorized
- No blocker closed
- No customer contacted
- No vendor contacted
- No runtime modified
- No backend modified
- No kernel modified
- No API schema modified
- No private core exposed
- No product launched
- No production-ready claim added

## Decision

This is a local human-only sequence packet. It may guide human review order but
cannot substitute for owner assignment, validator import, evidence request
approval, evidence collection, execution approval, go/no-go, or closure review.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Commercial Evidence Sprint Human Sequence Packet v0.1

commercial_evidence_sprint_human_sequence_packet_v0_1: true
status: hold_first_owner_input_required
packet_scope: local_human_only_commercial_evidence_sprint_sequence
first_blocker_id: support_contact
current_step_id: SEQ-001
current_step_entrypoint: phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.md
current_step_command_template_available: true
sequence_step_count: 7
ready_for_validator_import: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
owner_contacted_by_codex: false
request_approved_by_codex: false
blockers_closed_by_packet: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This packet locks the human-only sequence for the first commercial evidence
sprint blocker so owner assignment, validator import, ERD approval, separate
evidence request, evidence collection, and closure review cannot be conflated.

## Boundary

This is a local sequencing surface only. It does not assign owners, approve
requests, contact anyone, collect evidence, execute work, close blockers,
launch product, modify runtime/backend/kernel/API schema, expose private core,
or claim production readiness.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Commercial Evidence Sprint Human Sequence Packet Recommendation Gate

answer: conditional

recommend_for_human_sequence_control: true
recommend_for_owner_assignment: false
recommend_for_request_approval: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_customer_contact: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The packet is useful because it makes the required human gate order explicit
for the first commercial evidence sprint blocker. It is not itself owner
assignment, request approval, evidence collection, execution, or blocker
closure.

## Boundary

- ready_for_validator_import: false
- ready_for_separate_evidence_collection_request: false
- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- request_approved_by_codex: false
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
    parser.add_argument("--first-owner-packet", default=str(FIRST_OWNER_PACKET))
    parser.add_argument(
        "--first-owner-input-request-packet",
        default=str(FIRST_OWNER_INPUT_REQUEST_PACKET),
    )
    parser.add_argument("--owner-readiness-board", default=str(OWNER_READINESS_BOARD))
    parser.add_argument("--approval-readiness-board", default=str(APPROVAL_READINESS_BOARD))
    parser.add_argument("--closure-readiness-board", default=str(CLOSURE_READINESS_BOARD))
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
        Path(args.first_owner_packet),
        Path(args.first_owner_input_request_packet),
        Path(args.owner_readiness_board),
        Path(args.approval_readiness_board),
        Path(args.closure_readiness_board),
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
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_HUMAN_SEQUENCE_PACKET: PASS "
            f"status={payload['status']} "
            f"current_step_id={payload['current_step_id']} "
            f"first_blocker_id={payload['first_blocker_id']} "
            "blockers_closed_by_packet=0 production_ready=false"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
