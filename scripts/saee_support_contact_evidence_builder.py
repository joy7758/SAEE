#!/usr/bin/env python3
"""Build support-contact evidence from a human-filled decision input.

This builder converts the local support-contact decision input into the
production support/SLA evidence shape consumed by commercial readiness checks.
It does not publish a support contact, send messages, contact customers or
vendors, create a support desk, approve SLA/on-call evidence, close blockers,
modify product behavior, or claim production readiness.
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
from saee_backend.services.production_support_evidence import (
    CUSTOMER_SUPPORT_KEYS,
    FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS,
    SLA_KEYS,
    SUPPORT_CONTACT_KEYS,
    evaluate_production_support_evidence,
)
from scripts.saee_support_contact_decision_packet import (
    FALSE_FLAGS as DECISION_FALSE_FLAGS,
    OUTPUT_TEMPLATE as DEFAULT_INPUT_PATH,
    TARGET_KEYS,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "support_contact_evidence_builder_output.local.json"
DEFAULT_SUPPORT_OUTPUT_PATH = (
    OUTPUT_DIR / "production_support_sla_evidence.from_support_contact.local.json"
)
REPORT_PATH = OUTPUT_DIR / "support_contact_evidence_builder_report.md"
DOC_PATH = (
    ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_EVIDENCE_BUILDER_V0_1.md"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)

INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(DECISION_FALSE_FLAGS)
        | set(FORBIDDEN_TRUE_KEYS)
        | {
            "codex_published_support_contact",
            "codex_sent_support_contact_test",
            "codex_contacted_customer",
            "codex_contacted_vendor",
            "codex_inferred_missing_evidence",
            "execution_authorized",
            "blockers_closed_by_builder",
        }
    )
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER: FAIL: " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in SUPPORT_CONTACT_KEYS}


def source_notes(data: dict[str, Any]) -> dict[str, str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return {}
    return {key: str(notes.get(key, "")).strip() for key in SUPPORT_CONTACT_KEYS}


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
        "selected_support_contact_channel",
        "decision_summary",
    )
    return all(str(data.get(field, "")).strip() for field in fields)


def completed_contact_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    slots = data.get("candidate_contact_slots", [])
    if not isinstance(slots, list):
        return []
    complete_slots = []
    for slot in slots:
        if not isinstance(slot, dict):
            continue
        if (
            str(slot.get("contact_channel", "")).strip()
            and str(slot.get("display_value_redacted", "")).strip()
            and slot.get("owner_named") is True
            and slot.get("abuse_handling_reviewed") is True
            and slot.get("customer_notice_route_reviewed") is True
            and slot.get("test_plan_reviewed") is True
            and str(slot.get("human_source_note", "")).strip()
        ):
            complete_slots.append(slot)
    return complete_slots


def complete_input(data: dict[str, Any]) -> bool:
    flags = evidence_review_flags(data)
    notes = source_notes(data)
    return (
        data.get("template_type") == "saee_support_contact_decision_input"
        and input_metadata_complete(data)
        and all(flags.values())
        and all(bool(notes.get(key)) for key in SUPPORT_CONTACT_KEYS)
        and bool(completed_contact_slots(data))
        and not boundary_violations(data)
    )


def build_support_evidence(
    data: dict[str, Any],
    input_path: Path,
    *,
    complete: bool,
) -> dict[str, Any]:
    flags = evidence_review_flags(data)
    evidence: dict[str, Any] = {
        "support_evidence_type": "production_support_sla_evidence",
        "evidence_scope": "human_filled_support_contact_decision_to_production_support_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_support_contact_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "selected_support_contact_channel_recorded": bool(
            str(data.get("selected_support_contact_channel", "")).strip()
        ),
        "completed_contact_slot_count": len(completed_contact_slots(data)),
        "codex_published_support_contact": False,
        "codex_sent_support_contact_test": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in SUPPORT_CONTACT_KEYS:
        evidence[key] = flags[key] and complete
    for key in CUSTOMER_SUPPORT_KEYS + SLA_KEYS + ON_CALL_KEYS:
        evidence[key] = False
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def support_readiness(path: Path, support_contact: str) -> dict[str, object]:
    return evaluate_production_support_evidence(
        load_settings(
            {
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(path),
                "SAEE_SUPPORT_CONTACT": support_contact,
            }
        )
    )


def build_from_input(
    input_path: Path,
    output_path: Path,
    support_output_path: Path,
    *,
    write_documentation: bool = True,
) -> dict[str, Any]:
    data = read_json(input_path)
    complete = complete_input(data)
    violations = boundary_violations(data)
    flags = evidence_review_flags(data)
    missing = [key for key in SUPPORT_CONTACT_KEYS if not flags[key]]
    status = "stop" if violations else ("pass" if complete else "hold")

    support_evidence = build_support_evidence(data, input_path, complete=complete)
    write_json(support_output_path, support_evidence)

    selected_contact = str(data.get("selected_support_contact_channel", "")).strip()
    readiness = support_readiness(support_output_path, selected_contact if complete else "")
    summary: dict[str, Any] = {
        "support_contact_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_support_contact_decision_to_production_support_evidence",
        "generated_by": "scripts/saee_support_contact_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "support_evidence_output": str(support_output_path),
        "status": status,
        "input_complete": complete,
        "metadata_complete": input_metadata_complete(data),
        "completed_contact_slot_count": len(completed_contact_slots(data)),
        "required_evidence_item_count": len(SUPPORT_CONTACT_KEYS),
        "provided_evidence_item_count": sum(1 for value in flags.values() if value),
        "missing_required_evidence_count": len(missing),
        "missing_required_evidence": missing,
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "support_readiness_status": readiness["status"],
        "support_contact_available_for_review": readiness["support_contact_available"],
        "production_support_available": readiness["production_support_available"],
        "customer_support_available": readiness["customer_support_available"],
        "sla_available": readiness["sla_available"],
        "on_call_rotation_available": readiness["on_call_rotation_available"],
        "target_blocker_ids": ["support_contact"],
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
        "support_vendor_contacted": False,
        "support_contact_published_by_codex": False,
        "support_contact_test_performed_by_codex": False,
        "codex_inferred_missing_evidence": False,
        "next_action": (
            "If a human fills the support-contact decision input with source notes, "
            "the generated support evidence can be used as one input to support "
            "readiness review. Customer support, SLA, and on-call evidence remain separate."
        ),
    }
    write_json(output_path, summary)
    if write_documentation:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Support Contact Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- builder_scope: human_filled_support_contact_decision_to_production_support_evidence
- required_evidence_item_count: {summary['required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- support_readiness_status: {summary['support_readiness_status']}
- support_contact_available_for_review: {str(summary['support_contact_available_for_review']).lower()}
- production_support_available: {str(summary['production_support_available']).lower()}
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete way to convert a filled
support-contact decision input into the existing production support/SLA
evidence shape. It only targets the `support_contact` evidence group.

## What It Does Not Do

It does not publish a support contact, send support-contact tests, contact
customers, contact support vendors, create customer support operations, approve
SLA terms, start on-call rotation, close blockers, or mark SAEE as production
ready.

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
- support_vendor_contacted: false

## Next Action

Human owners must fill `support_contact_decision_input.template.json` with real
source notes. The generated support evidence is only one input to later
go/no-go review and does not close support blockers by itself.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Support Contact Evidence Builder v0.1

Status: local builder available; default output is hold.

support_contact_evidence_builder_v0_1: true
builder_scope: human_filled_support_contact_decision_to_production_support_evidence
required_evidence_item_count: {summary['required_evidence_item_count']}
default_output_status: {summary['status']}
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0
production_support_available: false

## Purpose

This builder converts a human-filled support-contact decision input into local
production support/SLA evidence fields for the `support_contact` group. It is a
commercial-readiness evidence intake surface, not support execution.

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
support_vendor_contacted: false
support_contact_published_by_codex: false
support_contact_test_performed_by_codex: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json`
- builder output: `phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_output.local.json`
- support evidence output: `phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_support_contact.local.json`
- report: `phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_report.md`
- script: `scripts/saee_support_contact_evidence_builder.py`
- smoke: `scripts/saee_support_contact_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Support Contact Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_customer_support_claim: false
recommend_for_sla_claim: false
recommend_for_on_call_claim: false
recommend_for_external_execution: false

## Reason

The builder is useful because it converts human-filled support-contact evidence
into a machine-checkable production support/SLA evidence shape. It is not
sufficient for blocker closure by itself: default input is incomplete, and even
complete support-contact evidence leaves customer support, SLA, and on-call
evidence unresolved.

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
support_contact_published_by_codex: false
support_contact_test_performed_by_codex: false
blockers_closed_by_builder: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--support-output", default=str(DEFAULT_SUPPORT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_from_input(
        Path(args.input),
        Path(args.output),
        Path(args.support_output),
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_SUPPORT_CONTACT_EVIDENCE_BUILDER: PASS "
            f"path={args.output} status={summary['status']} "
            f"support_contact_available_for_review="
            f"{str(summary['support_contact_available_for_review']).lower()} "
            "production_support_available=false blockers_closed_by_builder=0"
        )


if __name__ == "__main__":
    main()
