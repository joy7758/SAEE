#!/usr/bin/env python3
"""Validate first-owner input for the first commercial evidence sprint blocker.

This is a narrow pre-evidence validator for SEQ-001 in the human sequence
packet. It checks only the `support_contact` owner fields, so a human can move
the first commercial blocker through a bounded review step without pretending
that all sprint blockers have owners. It does not contact owners, collect
evidence, execute tasks, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SOURCE_SEQUENCE_PATH = SPRINT_DIR / "human_sequence_packet.local.json"
SOURCE_ACTION_PACKET_PATH = SPRINT_DIR / "first_owner_action_packet.local.json"
DEFAULT_INPUT_PATH = SPRINT_DIR / "first_owner_input.template.json"
OUTPUT_PATH = SPRINT_DIR / "first_owner_input_validation.local.json"
REPORT_PATH = SPRINT_DIR / "first_owner_input_validation.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

FIRST_BLOCKER_ID = "support_contact"
VALID_TEMPLATE_TYPE = "saee_commercial_evidence_sprint_first_owner_input"
REQUIRED_FIELDS = [
    "assigned_human_owner",
    "owner_contact_reference",
    "target_review_date",
    "owner_acknowledged_scope",
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
    "owner_assigned_by_codex",
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
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR: "
            "FAIL input must be a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def action_first_blocker(action_packet: dict[str, Any]) -> dict[str, Any]:
    first_blocker = action_packet.get("first_blocker", {})
    if not isinstance(first_blocker, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR: "
            "FAIL first_owner_action_packet first_blocker must be an object"
        )
    if first_blocker.get("blocker_id") != FIRST_BLOCKER_ID:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR: "
            f"FAIL expected first blocker {FIRST_BLOCKER_ID}"
        )
    return first_blocker


def build_template() -> dict[str, Any]:
    action_packet = read_json(SOURCE_ACTION_PACKET_PATH)
    first_blocker = action_first_blocker(action_packet)
    return {
        "template_type": VALID_TEMPLATE_TYPE,
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "source_human_sequence_packet": rel(SOURCE_SEQUENCE_PATH),
        "source_first_owner_action_packet": rel(SOURCE_ACTION_PACKET_PATH),
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": FIRST_BLOCKER_ID,
        "selected_blocker_count": 1,
        "required_human_fields": REQUIRED_FIELDS,
        "first_owner_input": {
            "blocker_id": FIRST_BLOCKER_ID,
            "phase_id": first_blocker.get("phase_id", ""),
            "category": first_blocker.get("category", ""),
            "owner_review_lane": first_blocker.get("owner_review_lane", ""),
            "required_evidence": first_blocker.get("required_evidence", ""),
            "assigned_human_owner": "",
            "owner_contact_reference": "",
            "target_review_date": "",
            "owner_acknowledged_scope": False,
            "human_approval_reference": "",
            "notes": "",
        },
        "boundary_review": {key: False for key in FORBIDDEN_TRUE_KEYS},
        "human_reviewer_name": "",
        "review_date": "",
        "review_notes": "",
    }


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    boundary_review = data.get("boundary_review", {})
    if not isinstance(boundary_review, dict):
        violations.append("boundary_review_missing_or_invalid")
        boundary_review = {}
    for key in FORBIDDEN_TRUE_KEYS:
        if data.get(key) is True or boundary_review.get(key) is True:
            violations.append(key)
    if data.get("blockers_closed_by_validator") not in (None, False, 0, ""):
        violations.append("blockers_closed_by_validator")
    return sorted(set(violations))


def first_owner_row(data: dict[str, Any]) -> dict[str, Any]:
    row = data.get("first_owner_input", {})
    if not isinstance(row, dict):
        return {}
    return row


def missing_fields(data: dict[str, Any]) -> list[str]:
    row = first_owner_row(data)
    if row.get("blocker_id") != FIRST_BLOCKER_ID:
        return ["first_owner_input.blocker_id"]
    missing: list[str] = []
    for field in ["assigned_human_owner", "owner_contact_reference", "target_review_date", "human_approval_reference"]:
        if not str(row.get(field, "")).strip():
            missing.append(field)
    if row.get("owner_acknowledged_scope") is not True:
        missing.append("owner_acknowledged_scope")
    return missing


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    violations = boundary_violations(data)
    missing = missing_fields(data)
    template_type_valid = data.get("template_type") == VALID_TEMPLATE_TYPE
    sequence_step_valid = data.get("sequence_step_id") == "SEQ-001"
    first_blocker_valid = data.get("first_blocker_id") == FIRST_BLOCKER_ID
    first_owner_assignment_complete = (
        template_type_valid
        and sequence_step_valid
        and first_blocker_valid
        and not missing
        and not violations
    )
    validation_status = (
        "stop" if violations else ("pass" if first_owner_assignment_complete else "hold")
    )
    status = (
        "stop_boundary_violation"
        if violations
        else (
            "pass_first_owner_input_complete"
            if first_owner_assignment_complete
            else "hold_first_owner_input_required"
        )
    )
    assigned_owner_count = 1 if first_owner_assignment_complete else 0
    input_path_value = rel(input_path) if input_path.is_relative_to(ROOT) else str(input_path)
    validation: dict[str, Any] = {
        "validator_type": "saee_commercial_evidence_sprint_first_owner_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_first_owner_input_pre_evidence_collection_check",
        "source_human_sequence_packet": rel(SOURCE_SEQUENCE_PATH),
        "source_first_owner_action_packet": rel(SOURCE_ACTION_PACKET_PATH),
        "input_path": input_path_value,
        "generated_by": "scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "validation_status": validation_status,
        "template_type_valid": template_type_valid,
        "sequence_step_id": "SEQ-001",
        "sequence_step_valid": sequence_step_valid,
        "first_blocker_id": FIRST_BLOCKER_ID,
        "first_blocker_valid": first_blocker_valid,
        "selected_blocker_count": 1,
        "assigned_owner_count": assigned_owner_count,
        "unassigned_owner_count": 1 - assigned_owner_count,
        "first_owner_assignment_complete": first_owner_assignment_complete,
        "ready_for_human_sequence_step_002": first_owner_assignment_complete,
        "ready_for_full_owner_assignment_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "missing_assignment_fields": missing,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_validator": 0,
        "blockers_ready_to_close": [],
        "next_action": (
            "If validation_status is pass, move to a separate human-reviewed "
            "SEQ-002 import/validation step. Do not collect evidence or close "
            "blockers from this validator."
        ),
    }
    for key in FORBIDDEN_TRUE_KEYS:
        validation[key] = False
    return validation


def list_items(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Evidence Sprint First Owner Input Validation

Status: {validation['status']}.

This report validates only the first owner input for `support_contact` before
any evidence collection request is opened. It does not assign owners by itself,
contact owners, collect evidence, execute work, close blockers, launch product,
or claim production readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- sequence_step_id: {validation['sequence_step_id']}
- first_blocker_id: {validation['first_blocker_id']}
- selected_blocker_count: {validation['selected_blocker_count']}
- assigned_owner_count: {validation['assigned_owner_count']}
- unassigned_owner_count: {validation['unassigned_owner_count']}
- first_owner_assignment_complete: {str(validation['first_owner_assignment_complete']).lower()}
- ready_for_human_sequence_step_002: {str(validation['ready_for_human_sequence_step_002']).lower()}
- ready_for_full_owner_assignment_validator: false
- ready_for_evidence_collection: false
- ready_for_separate_evidence_collection_request: false
- human_review_required: true
- separate_validator_required: true
- separate_evidence_collection_request_required: true
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_validator: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Missing Assignment Fields

{list_items(validation['missing_assignment_fields'])}

## Boundary Violations

{list_items(validation['boundary_violations'])}

## Boundary

This validator is a local first-owner input check only. Passing validation only
means the `support_contact` owner fields are complete enough for the next
human-reviewed sequence step. It does not authorize evidence collection,
execution, owner contact, customer contact, blocker closure, launch, or
production-readiness claims.
"""


def write_static_docs() -> None:
    TOP_DOC.parent.mkdir(parents=True, exist_ok=True)
    TOP_DOC.write_text(
        """# SAEE Commercial Evidence Sprint First Owner Input Validator v0.1

commercial_evidence_sprint_first_owner_input_validator_v0_1: true
status: hold_first_owner_input_required
validator_scope: local_first_owner_input_pre_evidence_collection_check
sequence_step_id: SEQ-001
first_blocker_id: support_contact
selected_blocker_count: 1
assigned_owner_count: 0
unassigned_owner_count: 1
first_owner_assignment_complete: false
ready_for_human_sequence_step_002: false
ready_for_full_owner_assignment_validator: false
ready_for_evidence_collection: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_validator: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks only the first commercial evidence sprint owner input for
`support_contact`. It exists because the human sequence packet starts with one
bounded owner-assignment action rather than requiring all five selected
commercial blockers to be filled at once.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json`
- validation output: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_validation.md`
- script: `scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py`
- smoke: `scripts/saee_commercial_evidence_sprint_first_owner_input_validator_smoke.py`

## Boundary

This is local first-owner input validation only. It does not contact owners,
collect evidence, execute tasks, close blockers, launch product, modify
runtime, backend, kernel, API schema, or private core, or claim production
readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Sprint First Owner Input Validator Recommendation Gate

answer: conditional

recommend_for_first_owner_input_validation: true
recommend_for_full_owner_assignment_validation: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful for checking whether the `support_contact` owner input
for SEQ-001 is complete before a later human-reviewed import or evidence
request step. It is not an evidence collection runner and does not authorize
execution.

## Boundary

- first_blocker_id: support_contact
- ready_for_evidence_collection: false
- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- blockers_closed_by_validator: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def run(input_path: Path, *, json_only: bool = False) -> dict[str, Any]:
    template = build_template()
    write_json(DEFAULT_INPUT_PATH, template)
    validation = build_validation(input_path)
    write_json(OUTPUT_PATH, validation)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    write_static_docs()
    if json_only:
        print(json.dumps(validation, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_VALIDATOR: "
            f"PASS status={validation['status']} "
            "first_blocker_id=support_contact "
            f"first_owner_assignment_complete="
            f"{str(validation['first_owner_assignment_complete']).lower()} "
            "ready_for_evidence_collection=false "
            "evidence_collection_authorized=false execution_authorized=false "
            "blockers_closed_by_validator=0 production_ready=false"
        )
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if input_path == DEFAULT_INPUT_PATH and not input_path.exists():
        write_json(DEFAULT_INPUT_PATH, build_template())
    run(input_path, json_only=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
