#!/usr/bin/env python3
"""Build operations-on-call-rotation evidence from a human-filled input.

This builder converts local, human-filled operations-on-call-rotation review
evidence into the production operations evidence shape consumed by commercial
readiness checks. It does not start on-call rotation, publish escalation
schedules, assign incident commanders, contact vendors, send alerts, modify
product behavior, close blockers, or claim production readiness.
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

from saee_backend.config import load_settings
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    ON_CALL_KEYS,
    FORBIDDEN_TRUE_KEYS,
    PRODUCTION_MONITORING_KEYS,
    evaluate_production_operations_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
DEFAULT_INPUT_PATH = OUTPUT_DIR / "operations_on_call_rotation_evidence_input.template.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "operations_on_call_rotation_evidence_builder_output.local.json"
DEFAULT_OPERATIONS_OUTPUT_PATH = (
    OUTPUT_DIR / "production_operations_evidence.from_operations_on_call_rotation.local.json"
)
REPORT_PATH = OUTPUT_DIR / "operations_on_call_rotation_evidence_builder_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/OPERATIONS_ON_CALL_ROTATION_EVIDENCE_BUILDER_V0_1.md"
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_OPERATIONS_ON_CALL_ROTATION_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)

INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(FORBIDDEN_TRUE_KEYS)
        | {
            "backend_modified",
            "external_model_api_called",
            "external_ai_assistant_tested",
            "on_call_rotation_started_by_codex",
            "escalation_schedule_published_by_codex",
            "incident_commander_assigned_by_codex",
            "monitoring_vendor_contacted_by_codex",
            "alert_provider_contacted_by_codex",
            "on_call_vendor_contacted_by_codex",
            "codex_contacted_customer",
            "codex_contacted_vendor",
            "codex_inferred_missing_evidence",
            "execution_authorized",
            "blockers_closed_by_builder",
            "production_on_call_rotation_claim_published",
        }
    )
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_OPERATIONS_ON_CALL_ROTATION_EVIDENCE_BUILDER: FAIL: " + message)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_operations_on_call_rotation_evidence_input",
        "template_version": "v0.1",
        "input_status": "template_pending_human_input",
        "human_reviewer_name": "",
        "review_date": "",
        "on_call_rotation_owner": "",
        "operations_reviewer_name": "",
        "decision_summary": "",
        "evidence_review": {key: False for key in ON_CALL_KEYS},
        "source_notes_by_key": {key: "" for key in ON_CALL_KEYS},
        "on_call_rotation_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": "",
                "owner_named": False,
                "reviewed_by_human": False,
                "human_source_note": "",
            }
            for key in ON_CALL_KEYS
        ],
        "boundary_review": {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS},
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
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "on_call_rotation_started": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "on_call_vendor_contacted_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_on_call_rotation_claim_published": False,
    }


def ensure_default_template(path: Path) -> None:
    if not path.exists():
        write_json(path, default_input_template())


def read_json(path: Path) -> dict[str, Any]:
    ensure_default_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_OPERATIONS_ON_CALL_ROTATION_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in ON_CALL_KEYS}


def source_notes(data: dict[str, Any]) -> dict[str, str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return {}
    return {key: str(notes.get(key, "")).strip() for key in ON_CALL_KEYS}


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations = [key for key in INPUT_FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    boundary = data.get("boundary_review", {})
    if not isinstance(boundary, dict):
        violations.append("boundary_review_missing")
        return violations
    for key in INPUT_FORBIDDEN_TRUE_KEYS:
        if boundary.get(key) is True:
            violations.append(f"boundary_review.{key}")
    return violations


def input_metadata_complete(data: dict[str, Any]) -> bool:
    fields = (
        "human_reviewer_name",
        "review_date",
        "on_call_rotation_owner",
        "operations_reviewer_name",
        "decision_summary",
    )
    return all(str(data.get(field, "")).strip() for field in fields)


def completed_on_call_rotation_slots(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots = data.get("on_call_rotation_evidence_slots", [])
    if not isinstance(slots, list):
        return {}
    complete_slots: dict[str, dict[str, Any]] = {}
    for slot in slots:
        if not isinstance(slot, dict):
            continue
        key = str(slot.get("evidence_key", "")).strip()
        if key not in ON_CALL_KEYS:
            continue
        if (
            str(slot.get("evidence_reference", "")).strip()
            and slot.get("owner_named") is True
            and slot.get("reviewed_by_human") is True
            and str(slot.get("human_source_note", "")).strip()
        ):
            complete_slots[key] = slot
    return complete_slots


def complete_input(data: dict[str, Any]) -> bool:
    flags = evidence_review_flags(data)
    notes = source_notes(data)
    complete_slots = completed_on_call_rotation_slots(data)
    return (
        data.get("template_type") == "saee_operations_on_call_rotation_evidence_input"
        and input_metadata_complete(data)
        and all(flags.values())
        and all(bool(notes.get(key)) for key in ON_CALL_KEYS)
        and all(key in complete_slots for key in ON_CALL_KEYS)
        and not boundary_violations(data)
    )


def build_operations_evidence(
    data: dict[str, Any],
    input_path: Path,
    *,
    complete: bool,
) -> dict[str, Any]:
    flags = evidence_review_flags(data)
    complete_slots = completed_on_call_rotation_slots(data)
    evidence: dict[str, Any] = {
        "operations_evidence_type": "production_operations_evidence",
        "evidence_scope": "human_filled_operations_on_call_rotation_to_production_operations_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_operations_on_call_rotation_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "on_call_rotation_owner_recorded": bool(str(data.get("on_call_rotation_owner", "")).strip()),
        "operations_reviewer_name_recorded": bool(
            str(data.get("operations_reviewer_name", "")).strip()
        ),
        "completed_on_call_rotation_slot_count": len(complete_slots),
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "alert_provider_contacted_by_codex": False,
        "on_call_vendor_contacted_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in ON_CALL_KEYS:
        evidence[key] = flags[key] and complete
    for key in PRODUCTION_MONITORING_KEYS + EXTERNAL_ALERT_DELIVERY_KEYS:
        evidence[key] = False
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["backend_modified"] = False
    evidence["external_model_api_called"] = False
    evidence["external_ai_assistant_tested"] = False
    return evidence


def operations_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_operations_evidence(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def build_from_input(
    input_path: Path,
    output_path: Path,
    operations_output_path: Path,
    *,
    write_documentation: bool = True,
) -> dict[str, Any]:
    data = read_json(input_path)
    complete = complete_input(data)
    violations = boundary_violations(data)
    flags = evidence_review_flags(data)
    missing = [key for key in ON_CALL_KEYS if not flags[key]]
    missing_slots = [
        key for key in ON_CALL_KEYS if key not in completed_on_call_rotation_slots(data)
    ]
    status = "stop" if violations else ("pass" if complete else "hold")

    operations_evidence = build_operations_evidence(data, input_path, complete=complete)
    write_json(operations_output_path, operations_evidence)

    readiness = operations_readiness(operations_output_path)
    summary: dict[str, Any] = {
        "operations_on_call_rotation_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_operations_on_call_rotation_to_production_operations_evidence",
        "generated_by": "scripts/saee_operations_on_call_rotation_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "operations_evidence_output": str(operations_output_path),
        "status": status,
        "input_complete": complete,
        "metadata_complete": input_metadata_complete(data),
        "completed_on_call_rotation_slot_count": len(completed_on_call_rotation_slots(data)),
        "required_evidence_item_count": len(ON_CALL_KEYS),
        "provided_evidence_item_count": sum(1 for value in flags.values() if value),
        "missing_required_evidence_count": len(missing),
        "missing_required_evidence": missing,
        "missing_on_call_rotation_slot_count": len(missing_slots),
        "missing_on_call_rotation_slots": missing_slots,
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "operations_readiness_status": readiness["status"],
        "production_monitoring_available": readiness["production_monitoring_available"],
        "external_alert_delivery_available": readiness["external_alert_delivery_available"],
        "operations_on_call_rotation_available_for_review": readiness["on_call_rotation_available"],
        "operations_on_call_rotation_available": readiness["on_call_rotation_available"],
        "on_call_rotation_available": readiness["on_call_rotation_available"],
        "production_operations_ready": readiness["production_operations_ready"],
        "target_blocker_ids": ["on_call_rotation"],
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
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
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "on_call_rotation_started": False,
        "on_call_rotation_started_by_codex": False,
        "escalation_schedule_published_by_codex": False,
        "incident_commander_assigned_by_codex": False,
        "on_call_vendor_contacted_by_codex": False,
        "production_on_call_rotation_claim_published": False,
        "codex_inferred_missing_evidence": False,
        "next_action": (
            "If a human fills the operations-on-call-rotation evidence input with "
            "source notes, the generated operations evidence can be used as "
            "one input to operations readiness review. Production monitoring "
            "and external alert delivery evidence remain separate."
        ),
    }
    write_json(output_path, summary)
    if write_documentation:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Operations On-call Rotation Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- builder_scope: human_filled_operations_on_call_rotation_to_production_operations_evidence
- required_evidence_item_count: {summary['required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- operations_readiness_status: {summary['operations_readiness_status']}
- operations_on_call_rotation_available_for_review: {str(summary['operations_on_call_rotation_available_for_review']).lower()}
- production_operations_ready: {str(summary['production_operations_ready']).lower()}
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete way to convert a filled
operations-on-call-rotation input into the existing production operations evidence
shape. It only targets the `on_call_rotation` evidence group.

## What It Does Not Do

It does not start on-call rotation, publish escalation schedules, assign
incident commanders, contact vendors or customers, send alerts, close blockers,
or mark SAEE as production ready.

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- customer_contacted: false
- alert_provider_contacted: false
- monitoring_vendor_contacted: false
- on_call_rotation_started: false

## Next Action

Human owners must fill `operations_on_call_rotation_evidence_input.template.json`
with real source notes. The generated operations evidence is only one input to
later go/no-go review and does not close operations blockers by itself.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Operations On-call Rotation Evidence Builder v0.1

Status: local builder available; default output is hold.

operations_on_call_rotation_evidence_builder_v0_1: true
builder_scope: human_filled_operations_on_call_rotation_to_production_operations_evidence
required_evidence_item_count: {summary['required_evidence_item_count']}
default_output_status: {summary['status']}
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0
production_operations_ready: false

## Purpose

This builder converts a human-filled operations-on-call-rotation input into local
production operations evidence fields for the `on_call_rotation` group.
It is a commercial-readiness evidence intake surface, not on-call activation,
escalation schedule publication, incident commander assignment, vendor contact,
or alert operations.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false

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
alert_provider_contacted: false
monitoring_vendor_contacted: false
on_call_rotation_started: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false
on_call_vendor_contacted_by_codex: false
production_on_call_rotation_claim_published: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_input.template.json`
- builder output: `phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_builder_output.local.json`
- operations evidence output: `phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.from_operations_on_call_rotation.local.json`
- report: `phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_builder_report.md`
- script: `scripts/saee_operations_on_call_rotation_evidence_builder.py`
- smoke: `scripts/saee_operations_on_call_rotation_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Operations On-call Rotation Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_on_call_activation: false
recommend_for_escalation_schedule_publication: false
recommend_for_incident_commander_assignment: false
recommend_for_vendor_contact: false
recommend_for_external_execution: false

## Reason

The builder is useful because it converts human-filled operations-on-call-rotation
evidence into a machine-checkable production operations evidence shape. It is
not sufficient for blocker closure by itself: default input is incomplete, and
even complete operations-on-call-rotation evidence leaves production monitoring
and external alert delivery evidence unresolved.

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
alert_provider_contacted: false
monitoring_vendor_contacted: false
on_call_rotation_started: false
on_call_rotation_started_by_codex: false
escalation_schedule_published_by_codex: false
incident_commander_assigned_by_codex: false
on_call_vendor_contacted_by_codex: false
production_on_call_rotation_claim_published: false
blockers_closed_by_builder: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--operations-output", default=str(DEFAULT_OPERATIONS_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_from_input(
        Path(args.input),
        Path(args.output),
        Path(args.operations_output),
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_OPERATIONS_ON_CALL_ROTATION_EVIDENCE_BUILDER: PASS "
            f"path={args.output} status={summary['status']} "
            "operations_on_call_rotation_available_for_review="
            f"{str(summary['operations_on_call_rotation_available_for_review']).lower()} "
            "production_operations_ready=false blockers_closed_by_builder=0"
        )


if __name__ == "__main__":
    main()
