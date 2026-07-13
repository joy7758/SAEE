#!/usr/bin/env python3
"""Prepare and optionally export combined human input for support_contact.

The helper creates one combined template covering the first-owner input and the
support-contact decision input. If a human-filled combined input is supplied, it
can export the two existing validator inputs. It does not validate those exports
as passing, run validators, configure or publish support, collect evidence, or
close blockers.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
)
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"

BRIDGE_JSON = BRIDGE_DIR / "support_contact_human_input_bridge.local.json"
COMBINED_TEMPLATE = BRIDGE_DIR / "support_contact_human_input_bridge_input.template.json"
COMPLETION_STATUS_JSON = BRIDGE_DIR / "support_contact_human_input_bridge_completion_status.local.json"
COMPLETION_STATUS_MD = BRIDGE_DIR / "support_contact_human_input_bridge_completion_status.md"
COMPLETION_GUIDE = BRIDGE_DIR / "support_contact_human_input_bridge_completion_guide.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
)

FIRST_OWNER_TEMPLATE = SPRINT_DIR / "first_owner_input.template.json"
DEFAULT_FIRST_OWNER_OUTPUT = SPRINT_DIR / "first_owner_input.from_bridge.human_filled.local.json"
SUPPORT_DECISION_TEMPLATE = SUPPORT_DIR / "support_contact_decision_input.template.json"
DEFAULT_SUPPORT_OUTPUT = SUPPORT_DIR / "support_contact_decision_input.from_bridge.human_filled.local.json"

SUPPORT_KEYS = [
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
]

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
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "support_contact_configured_by_codex",
    "support_contact_published_by_codex",
    "support_contact_tested_by_codex",
    "support_contact_available",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "support_vendor_contacted",
    "customer_facing_support_contact_configured",
    "customer_support_available",
    "production_support_available",
    "production_support_claim_published",
    "blocker_closure_authorized",
    "blockers_closed_by_helper",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER: "
            "FAIL input must be a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def false_boundary() -> dict[str, bool]:
    return {key: False for key in FALSE_FLAGS}


def build_combined_template() -> dict[str, Any]:
    first_owner = read_json(FIRST_OWNER_TEMPLATE)
    support_decision = read_json(SUPPORT_DECISION_TEMPLATE)
    bridge = read_json(BRIDGE_JSON)
    return {
        "template_type": "saee_support_contact_human_input_bridge_combined_input",
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "target_blocker_id": "support_contact",
        "source_bridge": rel(BRIDGE_JSON),
        "source_first_owner_template": rel(FIRST_OWNER_TEMPLATE),
        "source_support_contact_decision_template": rel(SUPPORT_DECISION_TEMPLATE),
        "combined_input_row_count": bridge.get("combined_input_row_count", 16),
        "human_reviewer_name": "",
        "review_date": "",
        "review_notes": "",
        "first_owner_input": first_owner.get("first_owner_input", {}),
        "support_contact_decision_input": support_decision,
        "boundary_review": false_boundary(),
        "template_note": (
            "Human-filled bridge input only. This does not configure or publish "
            "a support contact, send tests, collect evidence, close blockers, or "
            "claim production readiness."
        ),
    }


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    boundary = data.get("boundary_review", {})
    if not isinstance(boundary, dict):
        violations.append("boundary_review_missing_or_invalid")
        boundary = {}
    for key in FALSE_FLAGS:
        if data.get(key) is True or boundary.get(key) is True:
            violations.append(key)
    return sorted(set(violations))


def first_owner_missing(data: dict[str, Any]) -> list[str]:
    row = data.get("first_owner_input", {})
    if not isinstance(row, dict):
        return ["first_owner_input"]
    missing: list[str] = []
    if row.get("blocker_id") != "support_contact":
        missing.append("first_owner_input.blocker_id")
    for field in [
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "human_approval_reference",
    ]:
        if not str(row.get(field, "")).strip():
            missing.append(f"first_owner_input.{field}")
    if row.get("owner_acknowledged_scope") is not True:
        missing.append("first_owner_input.owner_acknowledged_scope")
    return missing


def support_decision_missing(data: dict[str, Any]) -> list[str]:
    support = data.get("support_contact_decision_input", {})
    if not isinstance(support, dict):
        return ["support_contact_decision_input"]
    missing: list[str] = []
    for field in [
        "human_reviewer_name",
        "review_date",
        "selected_support_contact_channel",
        "decision_summary",
    ]:
        if not str(support.get(field, "")).strip():
            missing.append(f"support_contact_decision_input.{field}")
    review = support.get("evidence_review", {})
    notes = support.get("source_notes_by_key", {})
    if not isinstance(review, dict):
        review = {}
        missing.append("support_contact_decision_input.evidence_review")
    if not isinstance(notes, dict):
        notes = {}
        missing.append("support_contact_decision_input.source_notes_by_key")
    for key in SUPPORT_KEYS:
        if review.get(key) is not True:
            missing.append(f"support_contact_decision_input.evidence_review.{key}")
        if not str(notes.get(key, "")).strip():
            missing.append(f"support_contact_decision_input.source_notes_by_key.{key}")
    slots = support.get("candidate_contact_slots", [])
    complete_slots = 0
    if isinstance(slots, list):
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
                complete_slots += 1
    if complete_slots < 1:
        missing.append("support_contact_decision_input.candidate_contact_slots")
    return missing


def export_first_owner(data: dict[str, Any], output: Path) -> None:
    template = read_json(FIRST_OWNER_TEMPLATE)
    exported = dict(template)
    exported["input_status"] = "human_filled_first_owner_local_input_from_bridge"
    exported["first_owner_input"] = data["first_owner_input"]
    exported["review_notes"] = (
        "Generated from a human-filled support-contact bridge input. This does "
        "not assign owners by Codex, collect evidence, authorize execution, or "
        "close blockers."
    )
    write_json(output, exported)


def export_support_decision(data: dict[str, Any], output: Path) -> None:
    support = dict(data["support_contact_decision_input"])
    support["input_status"] = "human_filled_support_contact_decision_input_from_bridge"
    support["template_note"] = (
        "Generated from a human-filled support-contact bridge input. This does "
        "not configure or publish support, send tests, collect evidence, or "
        "close blockers."
    )
    write_json(output, support)


def status_payload(
    *,
    input_path: Path | None,
    export_performed: bool,
    first_owner_output: Path,
    support_output: Path,
    missing_first_owner: list[str],
    missing_support: list[str],
    violations: list[str],
) -> dict[str, Any]:
    missing_total = len(missing_first_owner) + len(missing_support)
    status = (
        "stop_boundary_violation"
        if violations
        else ("ready_for_separate_validators" if export_performed else "hold_combined_human_input_required")
    )
    payload: dict[str, Any] = {
        "support_contact_human_input_bridge_completion_helper_v0_1": True,
        "helper_type": "saee_support_contact_human_input_bridge_completion_helper",
        "helper_scope": "local_combined_human_input_template_and_export_helper",
        "status": status,
        "target_blocker_id": "support_contact",
        "combined_template_path": rel(COMBINED_TEMPLATE),
        "combined_input_path": rel(input_path) if input_path else "",
        "first_owner_export_path": rel(first_owner_output),
        "support_contact_decision_export_path": rel(support_output),
        "combined_input_export_performed": export_performed,
        "ready_for_first_owner_validator": export_performed,
        "ready_for_support_contact_approval_input_validator": export_performed,
        "ready_for_evidence_collection": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_helper": 0,
        "first_owner_missing_field_count": len(missing_first_owner),
        "support_contact_missing_field_count": len(missing_support),
        "combined_missing_field_count": missing_total,
        "missing_first_owner_fields": missing_first_owner,
        "missing_support_contact_fields": missing_support,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_input_required": not export_performed,
        "human_review_required": True,
        "requires_separate_validators": True,
        "requires_separate_evidence_collection_request": True,
        "requires_separate_blocker_closure_approval": True,
        "generated_by": "scripts/saee_support_contact_human_input_bridge_completion_helper.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "next_action": (
            "Fill the combined bridge input, export validator inputs, then run "
            "the two separate validators. Do not collect evidence or close "
            "blockers without a separate approved request."
        ),
    }
    payload.update(false_boundary())
    payload["blockers_closed_by_helper"] = 0
    return payload


def write_status_docs(payload: dict[str, Any]) -> None:
    shared = f"""support_contact_human_input_bridge_completion_helper_v0_1: true
status: {payload['status']}
helper_scope: local_combined_human_input_template_and_export_helper
target_blocker_id: support_contact
combined_input_export_performed: {str(payload['combined_input_export_performed']).lower()}
ready_for_first_owner_validator: {str(payload['ready_for_first_owner_validator']).lower()}
ready_for_support_contact_approval_input_validator: {str(payload['ready_for_support_contact_approval_input_validator']).lower()}
ready_for_evidence_collection: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_helper: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false"""
    COMPLETION_STATUS_MD.write_text(
        f"""# Support Contact Human Input Bridge Completion Status

{shared}

## Missing First Owner Fields

{chr(10).join('- ' + item for item in payload['missing_first_owner_fields']) or '- none'}

## Missing Support Contact Fields

{chr(10).join('- ' + item for item in payload['missing_support_contact_fields']) or '- none'}

## Boundary Violations

{chr(10).join('- ' + item for item in payload['boundary_violations']) or '- none'}

## Boundary

This helper only prepares a combined human-input template and, when a
human-filled input is supplied, exports two local validator inputs. It does not
run validators, configure or publish support, send tests, contact customers or
vendors, collect evidence, close blockers, launch product, or claim production
readiness.
""",
        encoding="utf-8",
    )
    COMPLETION_GUIDE.write_text(
        """# Support Contact Human Input Bridge Completion Guide

Use `support_contact_human_input_bridge_input.template.json` as the single
human-filled source for `support_contact`.

## Export Validator Inputs

```bash
python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py \\
  --combined-input phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json
```

Then run the existing validators separately:

```bash
python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py \\
  --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.from_bridge.human_filled.local.json

python3 scripts/saee_support_contact_approval_input_validator.py \\
  --input phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.from_bridge.human_filled.local.json
```

This guide does not authorize evidence collection, support-contact publication,
support-contact tests, blocker closure, customer contact, or production claims.
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Support Contact Human Input Bridge Completion Helper v0.1

{shared}

## Agent Recommendation Gate

recommendation_gate:
  feature_or_direction: support_contact_human_input_bridge_completion_helper
  target_customer_need: reduce manual handoff error before support_contact validators
  answer: recommend
  reasons_to_recommend:
    - It gives humans one combined input template for the current `support_contact` path.
    - It exports only local validator inputs and keeps evidence collection and execution false.
  reasons_not_to_recommend:
    - It does not make support contact production-ready.
    - Separate validators and separate evidence collection approval remain required.
  final_decision: recommend_for_combined_input_export_only

## Boundary

This helper is local input preparation only. It does not run validators, collect
evidence, close blockers, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Support Contact Human Input Bridge Completion Helper Recommendation Gate

answer: recommend
recommend_for_combined_input_template: true
recommend_for_local_validator_input_export: true
recommend_for_running_validators: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

reason: The helper reduces manual handoff error by exporting local validator
inputs from a human-filled combined bridge input while keeping execution,
evidence collection, support publication, blocker closure, and production
claims false.

{shared}
""",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    template = build_combined_template()
    write_json(COMBINED_TEMPLATE, template)

    combined_input_path = Path(args.combined_input) if args.combined_input else None
    if combined_input_path and not combined_input_path.is_absolute():
        combined_input_path = ROOT / combined_input_path
    first_owner_output = Path(args.first_owner_output)
    if not first_owner_output.is_absolute():
        first_owner_output = ROOT / first_owner_output
    support_output = Path(args.support_contact_output)
    if not support_output.is_absolute():
        support_output = ROOT / support_output

    missing_first_owner: list[str] = []
    missing_support: list[str] = []
    violations: list[str] = []
    export_performed = False
    if combined_input_path:
        data = read_json(combined_input_path)
        if data.get("template_type") != "saee_support_contact_human_input_bridge_combined_input":
            missing_first_owner.append("template_type")
        violations = boundary_violations(data)
        missing_first_owner.extend(first_owner_missing(data))
        missing_support.extend(support_decision_missing(data))
        if not missing_first_owner and not missing_support and not violations:
            export_first_owner(data, first_owner_output)
            export_support_decision(data, support_output)
            export_performed = True

    payload = status_payload(
        input_path=combined_input_path,
        export_performed=export_performed,
        first_owner_output=first_owner_output,
        support_output=support_output,
        missing_first_owner=missing_first_owner,
        missing_support=missing_support,
        violations=violations,
    )
    write_json(COMPLETION_STATUS_JSON, payload)
    write_status_docs(payload)
    print(
        "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER: PASS "
        f"status={payload['status']} "
        f"combined_input_export_performed={str(export_performed).lower()} "
        "blockers_closed_by_helper=0 production_ready=false"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--combined-input", default="")
    parser.add_argument("--first-owner-output", default=str(DEFAULT_FIRST_OWNER_OUTPUT))
    parser.add_argument("--support-contact-output", default=str(DEFAULT_SUPPORT_OUTPUT))
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
