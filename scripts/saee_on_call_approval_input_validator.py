#!/usr/bin/env python3
"""Validate on-call approval input before the evidence builder.

This validator checks completeness and boundary safety only. It does not start
an on-call rotation, publish an escalation schedule, assign an incident
commander, contact customers or vendors, start support operations, close
blockers, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_support_evidence import ON_CALL_KEYS
from scripts.saee_on_call_evidence_builder import (
    DEFAULT_INPUT_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    boundary_violations,
    completed_on_call_slots,
    evidence_review_flags,
    input_metadata_complete,
    source_notes,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "on_call_approval_input_validation.local.json"
REPORT_PATH = OUTPUT_DIR / "on_call_approval_input_validation.md"
DOC_PATH = (
    ROOT / "phase_b_product/commercial_readiness/ON_CALL_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_ON_CALL_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)


METADATA_FIELDS = (
    "human_reviewer_name",
    "review_date",
    "on_call_owner",
    "incident_operations_owner",
    "decision_summary",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_ON_CALL_APPROVAL_INPUT_VALIDATOR: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_ON_CALL_APPROVAL_INPUT_VALIDATOR: FAIL invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input must be object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def missing_metadata_fields(data: dict[str, Any]) -> list[str]:
    return [field for field in METADATA_FIELDS if not str(data.get(field, "")).strip()]


def missing_evidence_review(data: dict[str, Any]) -> list[str]:
    flags = evidence_review_flags(data)
    return [key for key in ON_CALL_KEYS if not flags[key]]


def missing_source_notes(data: dict[str, Any]) -> list[str]:
    notes = source_notes(data)
    return [key for key in ON_CALL_KEYS if not notes.get(key)]


def missing_on_call_slots(data: dict[str, Any]) -> list[str]:
    complete_slots = completed_on_call_slots(data)
    return [key for key in ON_CALL_KEYS if key not in complete_slots]


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    violations = boundary_violations(data)
    metadata_missing = missing_metadata_fields(data)
    evidence_missing = missing_evidence_review(data)
    notes_missing = missing_source_notes(data)
    slots_missing = missing_on_call_slots(data)
    metadata_complete = input_metadata_complete(data)
    evidence_review_complete = not evidence_missing
    source_notes_complete = not notes_missing
    on_call_slots_complete = not slots_missing
    input_complete = (
        data.get("template_type") == "saee_on_call_evidence_input"
        and metadata_complete
        and evidence_review_complete
        and source_notes_complete
        and on_call_slots_complete
        and not violations
    )
    validation_status = "stop" if violations else ("pass" if input_complete else "hold")
    builder_ready = validation_status == "pass"
    input_path_value = (
        str(input_path.relative_to(ROOT)) if input_path.is_relative_to(ROOT) else str(input_path)
    )

    return {
        "validator_type": "saee_on_call_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_on_call_input_pre_builder_check",
        "target_blocker_id": "on_call_rotation",
        "generated_by": "scripts/saee_on_call_approval_input_validator.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": input_path_value,
        "validation_status": validation_status,
        "input_complete": input_complete,
        "builder_ready": builder_ready,
        "metadata_complete": metadata_complete,
        "evidence_review_complete": evidence_review_complete,
        "source_notes_complete": source_notes_complete,
        "on_call_slots_complete": on_call_slots_complete,
        "required_on_call_evidence_item_count": len(ON_CALL_KEYS),
        "completed_on_call_slot_count": len(completed_on_call_slots(data)),
        "missing_metadata_fields": metadata_missing,
        "missing_evidence_review": evidence_missing,
        "missing_source_notes": notes_missing,
        "missing_on_call_slots": slots_missing,
        "boundary_review_key_count": len(INPUT_FORBIDDEN_TRUE_KEYS),
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_validator": 0,
        "on_call_rotation_approved_by_validator": False,
        "on_call_rotation_available_by_validator": False,
        "on_call_rotation_started_by_validator": False,
        "escalation_schedule_published_by_validator": False,
        "incident_commander_assigned_by_validator": False,
        "production_support_available_by_validator": False,
        "support_contact_available_by_validator": False,
        "customer_support_available_by_validator": False,
        "sla_available_by_validator": False,
        "production_on_call_claim_published": False,
        "production_support_claim_published": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "on_call_rotation_available": False,
        "on_call_rotation_started": False,
        "escalation_schedule_published": False,
        "incident_commander_assigned": False,
        "support_operations_started": False,
        "support_contact_available": False,
        "customer_support_available": False,
        "sla_available": False,
        "production_support_available": False,
        "support_case_created": False,
        "customer_communication_sent": False,
        "staffed_support_started": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
        "next_action": (
            "If validation_status is pass, a human may run the on-call evidence "
            "builder in a separate approved evidence request; otherwise complete "
            "missing input fields or resolve boundary violations first."
        ),
    }


def list_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE On-call Approval Input Validation

Status: {validation['validation_status']}.

This report validates the human-filled on-call evidence input before it is
passed into the existing on-call evidence builder. It does not start an
on-call rotation, publish an escalation schedule, assign an incident
commander, contact customers or vendors, start support operations, close
blockers, or claim production readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- target_blocker_id: {validation['target_blocker_id']}
- input_complete: {str(validation['input_complete']).lower()}
- builder_ready: {str(validation['builder_ready']).lower()}
- blockers_closed_by_validator: {validation['blockers_closed_by_validator']}
- on_call_rotation_approved_by_validator: false
- on_call_rotation_available_by_validator: false
- on_call_rotation_started_by_validator: false
- escalation_schedule_published_by_validator: false
- incident_commander_assigned_by_validator: false
- production_support_available_by_validator: false
- support_contact_available_by_validator: false
- customer_support_available_by_validator: false
- sla_available_by_validator: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Missing Metadata Fields

{list_lines(validation['missing_metadata_fields'])}

## Missing Evidence Review Keys

{list_lines(validation['missing_evidence_review'])}

## Missing Source Notes

{list_lines(validation['missing_source_notes'])}

## Missing On-call Slots

{list_lines(validation['missing_on_call_slots'])}

## Boundary Violations

{list_lines(validation['boundary_violations'])}

## Next Action

If validation_status is pass, a human may run the on-call evidence builder in a
separate approved evidence request. This validator itself closes no blockers
and authorizes no on-call start, escalation schedule publication, incident
commander assignment, support operations, customer contact, vendor contact, or
production claim.
"""


def write_docs(validation: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# SAEE On-call Approval Input Validator v0.1

on_call_approval_input_validator_v0_1: true
validator_scope: local_human_filled_on_call_input_pre_builder_check
default_validation_status: {validation['validation_status']}
default_input_complete: {str(validation['input_complete']).lower()}
default_builder_ready: {str(validation['builder_ready']).lower()}
target_blocker_id: on_call_rotation
required_on_call_evidence_item_count: {validation['required_on_call_evidence_item_count']}
blockers_closed_by_validator: 0
on_call_rotation_approved_by_validator: false
on_call_rotation_available_by_validator: false
on_call_rotation_started_by_validator: false
escalation_schedule_published_by_validator: false
incident_commander_assigned_by_validator: false
production_support_available_by_validator: false
support_contact_available_by_validator: false
customer_support_available_by_validator: false
sla_available_by_validator: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether the human-filled on-call evidence input is
complete and boundary-safe before it is passed to the existing on-call evidence
builder.

## Boundary

The validator is pre-builder input validation only. It does not start an
on-call rotation, publish an escalation schedule, assign an incident commander,
contact customers or vendors, start support operations, collect evidence, close
blockers, modify runtime/backend/kernel/API schema/private core, launch
product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/support_evidence/on_call_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_validation.md`
- script: `scripts/saee_on_call_approval_input_validator.py`
- smoke: `scripts/saee_on_call_approval_input_validator_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE On-call Approval Input Validator Recommendation Gate

answer: conditional

recommend_for_human_input_validation: true
recommend_for_on_call_approval: false
recommend_for_on_call_start: false
recommend_for_escalation_schedule_publication: false
recommend_for_incident_commander_assignment: false
recommend_for_evidence_collection_authorization: false
recommend_for_blocker_closure: false
recommend_for_customer_support_claim: false
recommend_for_sla_claim: false
recommend_for_support_contact_claim: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful because it catches missing human input and boundary
violations before the on-call evidence builder is run. It is not on-call
approval, does not start on-call rotation, and does not close the
on_call_rotation blocker by itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
on_call_rotation_available: false
on_call_rotation_started: false
escalation_schedule_published: false
incident_commander_assigned: false
support_operations_started: false
support_contact_available: false
customer_support_available: false
sla_available: false
production_support_available: false
on_call_rotation_approved_by_validator: false
on_call_rotation_available_by_validator: false
on_call_rotation_started_by_validator: false
escalation_schedule_published_by_validator: false
incident_commander_assigned_by_validator: false
blockers_closed_by_validator: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-docs", action="store_true")
    args = parser.parse_args()

    validation = build_validation(Path(args.input))
    write_json(Path(args.output), validation)
    if not args.no_docs:
        write_docs(validation)
    if args.json:
        print(json.dumps(validation, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_ON_CALL_APPROVAL_INPUT_VALIDATOR: PASS "
            f"status={validation['validation_status']} "
            f"builder_ready={str(validation['builder_ready']).lower()} "
            "blockers_closed_by_validator=0 production_ready=false"
        )


if __name__ == "__main__":
    main()
