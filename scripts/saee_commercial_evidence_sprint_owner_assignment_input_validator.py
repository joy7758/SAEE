#!/usr/bin/env python3
"""Validate human-filled owner assignments before evidence collection.

This validator checks whether the selected commercial evidence sprint blockers
have named human owners and review dates. It does not contact owners, collect
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
SOURCE_PACKET_PATH = SPRINT_DIR / "owner_assignment_packet.local.json"
DEFAULT_INPUT_PATH = SPRINT_DIR / "owner_assignment_input.template.json"
OUTPUT_PATH = SPRINT_DIR / "owner_assignment_input_validation.local.json"
REPORT_PATH = SPRINT_DIR / "owner_assignment_input_validation.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

SELECTED_BLOCKER_IDS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
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
]

REQUIRED_ROW_FIELDS = [
    "assigned_human_owner",
    "target_review_date",
    "human_approval_reference",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR: "
            "FAIL input must be a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_template(packet: dict[str, Any]) -> dict[str, Any]:
    assignment_inputs: list[dict[str, Any]] = []
    for row in packet.get("assignment_rows", []):
        assignment_inputs.append(
            {
                "blocker_id": row["blocker_id"],
                "phase_id": row["phase_id"],
                "category": row["category"],
                "owner_review_lane": row["owner_review_lane"],
                "required_evidence": row["required_evidence"],
                "assigned_human_owner": "",
                "owner_contact_reference": "",
                "target_review_date": "",
                "owner_acknowledged_scope": False,
                "human_approval_reference": "",
                "evidence_collection_request_reference": "",
                "notes": "",
            }
        )
    return {
        "template_type": "saee_commercial_evidence_sprint_owner_assignment_input",
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "source_packet": rel(SOURCE_PACKET_PATH),
        "selected_blocker_ids": SELECTED_BLOCKER_IDS,
        "assignment_inputs": assignment_inputs,
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


def rows_by_blocker(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = data.get("assignment_inputs", [])
    if not isinstance(rows, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("blocker_id"), str):
            result[row["blocker_id"]] = row
    return result


def missing_row_fields(data: dict[str, Any]) -> dict[str, list[str]]:
    rows = rows_by_blocker(data)
    missing: dict[str, list[str]] = {}
    for blocker_id in SELECTED_BLOCKER_IDS:
        row = rows.get(blocker_id)
        if row is None:
            missing[blocker_id] = ["assignment_input_row"]
            continue
        row_missing = [
            field for field in REQUIRED_ROW_FIELDS if not str(row.get(field, "")).strip()
        ]
        if row.get("owner_acknowledged_scope") is not True:
            row_missing.append("owner_acknowledged_scope")
        if row_missing:
            missing[blocker_id] = row_missing
    return missing


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    violations = boundary_violations(data)
    missing_fields = missing_row_fields(data)
    selected_ids_match = data.get("selected_blocker_ids") == SELECTED_BLOCKER_IDS
    template_type_valid = (
        data.get("template_type")
        == "saee_commercial_evidence_sprint_owner_assignment_input"
    )
    owner_assignment_complete = (
        template_type_valid and selected_ids_match and not missing_fields and not violations
    )
    validation_status = "stop" if violations else ("pass" if owner_assignment_complete else "hold")
    input_path_value = rel(input_path) if input_path.is_relative_to(ROOT) else str(input_path)
    assigned_owner_count = len(SELECTED_BLOCKER_IDS) - len(missing_fields)
    validation: dict[str, Any] = {
        "validator_type": "saee_commercial_evidence_sprint_owner_assignment_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_owner_assignment_pre_evidence_collection_check",
        "source_packet": rel(SOURCE_PACKET_PATH),
        "input_path": input_path_value,
        "generated_by": "scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation_status": validation_status,
        "template_type_valid": template_type_valid,
        "selected_blocker_ids_match": selected_ids_match,
        "selected_blocker_count": len(SELECTED_BLOCKER_IDS),
        "assigned_owner_count": assigned_owner_count,
        "unassigned_owner_count": len(missing_fields),
        "owner_assignment_complete": owner_assignment_complete,
        "ready_for_separate_evidence_collection_request": owner_assignment_complete,
        "missing_assignment_fields": missing_fields,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_validator": 0,
        "blockers_ready_to_close": [],
        "next_action": (
            "If validation_status is pass, create a separate human-approved "
            "evidence collection request. Do not collect evidence or close blockers "
            "from this validator."
        ),
    }
    for key in FORBIDDEN_TRUE_KEYS:
        validation[key] = False
    return validation


def list_missing(missing: dict[str, list[str]]) -> str:
    if not missing:
        return "- none"
    return "\n".join(
        f"- {blocker_id}: {', '.join(fields)}" for blocker_id, fields in missing.items()
    )


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Evidence Sprint Owner Assignment Input Validation

Status: {validation['validation_status']}.

This report validates human-filled owner assignment input before any evidence
collection request is opened. It does not assign owners by itself, contact
owners, collect evidence, execute work, close blockers, launch product, or
claim production readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- selected_blocker_count: {validation['selected_blocker_count']}
- assigned_owner_count: {validation['assigned_owner_count']}
- unassigned_owner_count: {validation['unassigned_owner_count']}
- owner_assignment_complete: {str(validation['owner_assignment_complete']).lower()}
- ready_for_separate_evidence_collection_request: {str(validation['ready_for_separate_evidence_collection_request']).lower()}
- human_review_required: true
- separate_evidence_collection_request_required: true
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_validator: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Missing Assignment Fields

{list_missing(validation['missing_assignment_fields'])}

## Boundary Violations

{list_missing({'violations': validation['boundary_violations']} if validation['boundary_violations'] else {})}

## Boundary

This validator is a local pre-evidence check only. Passing validation only means
that the owner-assignment input is complete enough for a separate
human-approved evidence collection request. It does not authorize collection,
execution, owner contact, customer contact, blocker closure, launch, or
production-readiness claims.
"""


def write_static_docs() -> None:
    TOP_DOC.write_text(
        """# SAEE Commercial Evidence Sprint Owner Assignment Input Validator v0.1

commercial_evidence_sprint_owner_assignment_input_validator_v0_1: true
status: hold
validator_scope: local_human_filled_owner_assignment_pre_evidence_collection_check
selected_blocker_count: 5
assigned_owner_count: 0
unassigned_owner_count: 5
owner_assignment_complete: false
ready_for_separate_evidence_collection_request: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_validator: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether a human-filled owner assignment input is complete
before a separate evidence collection request is created.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.template.json`
- validation output: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_validation.md`
- script: `scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py`
- smoke: `scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator_smoke.py`

## Boundary

This is local input validation only. It does not contact owners, collect
evidence, execute tasks, close blockers, launch product, modify runtime,
backend, kernel, API schema, or private core, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Sprint Owner Assignment Input Validator Recommendation Gate

answer: conditional

recommend_for_owner_assignment_input_validation: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful for checking whether human-filled owner assignment input
is complete before a separate evidence collection request. It is not an
evidence collection runner and does not authorize execution.

## Boundary

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
    packet = read_json(SOURCE_PACKET_PATH)
    template = build_template(packet)
    write_json(DEFAULT_INPUT_PATH, template)
    validation = build_validation(input_path)
    write_json(OUTPUT_PATH, validation)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    write_static_docs()
    if json_only:
        print(json.dumps(validation, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_OWNER_ASSIGNMENT_INPUT_VALIDATOR: "
            f"PASS status={validation['validation_status']} "
            f"owner_assignment_complete={str(validation['owner_assignment_complete']).lower()} "
            f"ready_for_separate_evidence_collection_request="
            f"{str(validation['ready_for_separate_evidence_collection_request']).lower()} "
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
        packet = read_json(SOURCE_PACKET_PATH)
        write_json(DEFAULT_INPUT_PATH, build_template(packet))
    run(input_path, json_only=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
