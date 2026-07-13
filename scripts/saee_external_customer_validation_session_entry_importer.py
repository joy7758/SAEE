#!/usr/bin/env python3
"""Prepare and optionally import one human-filled customer validation session.

Default behavior is safe and non-mutating for validation evidence: it writes a
blank human-entry template plus a hold report. With `--apply`, it converts an
explicitly human-filled entry into the existing
`customer_validation_evidence_input.human_filled.local.json` shape consumed by
the existing customer-validation approval validator.

The importer does not contact customers, run sessions, infer feedback, execute
evidence builders, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
SESSION_KIT = EVIDENCE_DIR / "external_customer_validation_session_kit.local.json"
CUSTOMER_TEMPLATE = EVIDENCE_DIR / "customer_validation_evidence_input.template.json"
ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
ENTRY_HUMAN_FILLED = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
TARGET_HUMAN_FILLED = EVIDENCE_DIR / "customer_validation_evidence_input.human_filled.local.json"
IMPORT_SUMMARY = EVIDENCE_DIR / "external_customer_validation_session_entry_import_summary.local.json"
IMPORT_REPORT = EVIDENCE_DIR / "external_customer_validation_session_entry_import_report.md"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_session_entry_import_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORT_GATE.md"


SESSION_TEXT_FIELDS = [
    "session_id",
    "session_date",
    "participant_role",
    "team_type",
    "current_evaluation_method",
]
SESSION_SCORE_FIELDS = [
    "understanding_score",
    "trust_score",
    "decision_influence_score",
    "repeat_usage_intent_score",
]
SESSION_BOUNDARY_FALSE_KEYS = [
    "secrets_collected",
    "production_data_collected",
    "customer_data_uploaded",
    "private_core_disclosed",
    "production_ready_claim_made",
]
TOP_LEVEL_FALSE_FLAGS = {
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "production_ready": False,
    "private_core_exposed": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
}
BOUNDARY_FALSE_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted_by_codex": False,
    "automated_customer_contact": False,
    "customer_data_collected_by_codex": False,
    "customer_secrets_collected": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_builder_executed": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_importer": 0,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORTER: "
            f"FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORTER: "
            f"FAIL JSON root must be object: {rel(path)}"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def review_keys() -> list[str]:
    template = read_json(CUSTOMER_TEMPLATE)
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORTER: "
            "FAIL customer validation template evidence_review missing"
        )
    return list(review)


def blank_session() -> dict[str, Any]:
    return {
        "session_id": "",
        "session_date": "",
        "participant_role": "",
        "team_type": "",
        "current_evaluation_method": "",
        "candidate_count": 0,
        "saee_demo_surface_used": "local_or_online_demo",
        "understanding_score": None,
        "trust_score": None,
        "decision_influence_score": None,
        "repeat_usage_intent_score": None,
        "time_to_value_minutes": None,
        "top_objection": "",
        "evidence_missing": "",
        "willing_to_test_own_candidates": None,
        "boundary_flags": {key: False for key in SESSION_BOUNDARY_FALSE_KEYS},
        "notes": "",
    }


def blank_entry_template() -> dict[str, Any]:
    return {
        "external_customer_validation_session_entry_template_v0_1": True,
        "human_entry_confirmed": False,
        "human_reviewer_name": "",
        "review_date": "",
        "source_session_kit": rel(SESSION_KIT),
        "target_customer_validation_input": rel(TARGET_HUMAN_FILLED),
        "session": blank_session(),
        "evidence_review": {key: False for key in review_keys()},
        "human_source_context": "",
        "boundary_confirmation": {
            "no_secrets_collected": False,
            "no_production_data_collected": False,
            "no_customer_data_uploaded": False,
            "no_private_core_disclosed": False,
            "no_production_ready_claim_made": False,
        },
        **TOP_LEVEL_FALSE_FLAGS,
    }


def is_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and 1 <= value <= 5


def validate_entry(entry: dict[str, Any]) -> dict[str, Any]:
    session = entry.get("session", {})
    if not isinstance(session, dict):
        session = {}
    evidence_review = entry.get("evidence_review", {})
    if not isinstance(evidence_review, dict):
        evidence_review = {}
    boundary_confirmation = entry.get("boundary_confirmation", {})
    if not isinstance(boundary_confirmation, dict):
        boundary_confirmation = {}

    missing_text = [
        field for field in SESSION_TEXT_FIELDS if not str(session.get(field, "")).strip()
    ]
    missing_scores = [
        field for field in SESSION_SCORE_FIELDS if not is_score(session.get(field))
    ]
    missing_required = []
    if not isinstance(session.get("candidate_count"), int) or session.get("candidate_count", 0) <= 0:
        missing_required.append("candidate_count")
    if session.get("willing_to_test_own_candidates") not in {True, False}:
        missing_required.append("willing_to_test_own_candidates")
    if entry.get("human_entry_confirmed") is not True:
        missing_required.append("human_entry_confirmed")
    if not str(entry.get("human_reviewer_name", "")).strip():
        missing_required.append("human_reviewer_name")
    if not str(entry.get("review_date", "")).strip():
        missing_required.append("review_date")
    if not str(entry.get("human_source_context", "")).strip():
        missing_required.append("human_source_context")

    session_boundary = session.get("boundary_flags", {})
    if not isinstance(session_boundary, dict):
        session_boundary = {}
    boundary_violations = [
        key for key in SESSION_BOUNDARY_FALSE_KEYS if session_boundary.get(key) is not False
    ]
    for key, expected in TOP_LEVEL_FALSE_FLAGS.items():
        if entry.get(key) is not expected:
            boundary_violations.append(key)

    confirmation_required = [
        "no_secrets_collected",
        "no_production_data_collected",
        "no_customer_data_uploaded",
        "no_private_core_disclosed",
        "no_production_ready_claim_made",
    ]
    missing_confirmations = [
        key for key in confirmation_required if boundary_confirmation.get(key) is not True
    ]
    missing_review = [key for key in review_keys() if evidence_review.get(key) is not True]
    session_complete = (
        not missing_text
        and not missing_scores
        and not missing_required
        and not boundary_violations
        and not missing_confirmations
    )
    evidence_review_complete = not missing_review
    validation_status = (
        "stop_boundary_violation"
        if boundary_violations
        else (
            "ready_for_customer_validation_validator"
            if session_complete and evidence_review_complete
            else "hold_human_session_entry_required"
        )
    )
    return {
        "validation_status": validation_status,
        "session_complete": session_complete,
        "evidence_review_complete": evidence_review_complete,
        "missing_text_fields": missing_text,
        "missing_score_fields": missing_scores,
        "missing_required_fields": missing_required,
        "missing_boundary_confirmations": missing_confirmations,
        "missing_evidence_review": missing_review,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
    }


def aggregate_metrics(session: dict[str, Any]) -> dict[str, Any]:
    if not session:
        return {
            "session_count": 0,
            "understanding_rate": None,
            "trust_rate": None,
            "decision_influence_rate": None,
            "repeat_usage_intent": None,
            "go_hold_pivot": "not_evaluated",
        }
    return {
        "session_count": 1,
        "understanding_rate": session.get("understanding_score"),
        "trust_rate": session.get("trust_score"),
        "decision_influence_rate": session.get("decision_influence_score"),
        "repeat_usage_intent": session.get("repeat_usage_intent_score"),
        "go_hold_pivot": "ready_for_validator_review",
    }


def build_customer_validation_input(entry: dict[str, Any]) -> dict[str, Any]:
    template = read_json(CUSTOMER_TEMPLATE)
    session = entry.get("session", {})
    evidence_review = entry.get("evidence_review", {})
    payload = dict(template)
    payload.update(TOP_LEVEL_FALSE_FLAGS)
    payload["customer_validation_evidence_input_v0_1"] = True
    payload["input_status"] = "external_customer_validation_session_entry_imported"
    payload["human_reviewer_name"] = entry.get("human_reviewer_name", "")
    payload["review_date"] = entry.get("review_date", "")
    payload["boundary_note"] = (
        "Human-filled external customer or target-user session imported from "
        "external_customer_validation_session_entry.human_filled.local.json. "
        "This is not a public customer-validation claim."
    )
    payload["sessions"] = [session]
    payload["evidence_review"] = {
        key: evidence_review.get(key) is True for key in review_keys()
    }
    payload["aggregate_metrics"] = aggregate_metrics(session)
    return payload


def build_summary(input_path: Path, apply: bool) -> dict[str, Any]:
    write_json(ENTRY_TEMPLATE, blank_entry_template())
    input_exists = input_path.exists()
    entry = read_json(input_path) if input_exists else blank_entry_template()
    validation = validate_entry(entry)
    output_written = False
    if apply and validation["validation_status"] == "ready_for_customer_validation_validator":
        write_json(TARGET_HUMAN_FILLED, build_customer_validation_input(entry))
        output_written = True
    return {
        "external_customer_validation_session_entry_importer_v0_1": True,
        "status": validation["validation_status"],
        "importer_type": "manual_external_customer_validation_session_entry_importer",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_external_customer_validation_session_entry_importer.py",
        "source_session_kit": rel(SESSION_KIT),
        "entry_template": rel(ENTRY_TEMPLATE),
        "entry_input_path": rel(input_path),
        "entry_input_exists": input_exists,
        "target_customer_validation_input": rel(TARGET_HUMAN_FILLED),
        "apply_requested": apply,
        "human_filled_output_written": output_written,
        "ready_for_existing_customer_validation_validator": output_written,
        "human_entry_template_ready": True,
        "human_action_required": not output_written,
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "session_complete": validation["session_complete"],
        "evidence_review_complete": validation["evidence_review_complete"],
        "missing_text_fields": validation["missing_text_fields"],
        "missing_score_fields": validation["missing_score_fields"],
        "missing_required_fields": validation["missing_required_fields"],
        "missing_boundary_confirmations": validation["missing_boundary_confirmations"],
        "missing_evidence_review_count": len(validation["missing_evidence_review"]),
        "missing_evidence_review": validation["missing_evidence_review"],
        "boundary_violation_count": validation["boundary_violation_count"],
        "boundary_violations": validation["boundary_violations"],
        "validator_command_after_import": (
            "python3 scripts/saee_customer_validation_approval_input_validator.py "
            f"--input {rel(TARGET_HUMAN_FILLED)}"
        ),
        "next_human_action": (
            "Copy the entry template, fill it from a real external customer or "
            "target-user session, then run this importer with --apply."
        ),
        **BOUNDARY_FALSE_FLAGS,
    }


def render_report(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Entry Import Report

Status: {summary['status']}.

This importer prepares or converts one human-filled external customer validation
session entry into the existing customer-validation evidence input shape. It
does not contact customers, run sessions, infer feedback, execute the evidence
builder, close blockers, launch product, or claim production readiness.

## Summary

```yaml
external_customer_validation_session_entry_importer_v0_1: true
status: {summary['status']}
entry_template: {summary['entry_template']}
entry_input_exists: {str(summary['entry_input_exists']).lower()}
apply_requested: {str(summary['apply_requested']).lower()}
human_filled_output_written: {str(summary['human_filled_output_written']).lower()}
ready_for_existing_customer_validation_validator: {str(summary['ready_for_existing_customer_validation_validator']).lower()}
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_importer: 0
```

## Human Use

1. Copy `{summary['entry_template']}` to `{rel(ENTRY_HUMAN_FILLED)}`.
2. Fill it only from a real external customer or target-user session.
3. Run:

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --input {rel(ENTRY_HUMAN_FILLED)} --apply
```

4. If import succeeds, run:

```bash
{summary['validator_command_after_import']}
```

The validator result still does not close `customer_validated` or authorize a
production-readiness claim.
"""


def render_boundary(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Entry Import Boundary Audit

Final boundary decision: {summary['status']}.

- Runtime modified: {str(summary['runtime_modified']).lower()}
- Backend modified: {str(summary['backend_modified']).lower()}
- Kernel modified: {str(summary['kernel_modified']).lower()}
- API schema modified: {str(summary['api_schema_modified']).lower()}
- Private core exposed: {str(summary['private_core_exposed']).lower()}
- Customer contacted by Codex: {str(summary['customer_contacted_by_codex']).lower()}
- External calls made: {str(summary['external_calls_made']).lower()}
- Evidence builder executed: {str(summary['evidence_builder_executed']).lower()}
- Customer validated: {str(summary['customer_validated']).lower()}
- Production ready: {str(summary['production_ready']).lower()}
- Product launched: {str(summary['product_launched']).lower()}
- Blockers closed by importer: {summary['blockers_closed_by_importer']}
"""


def render_gate(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Entry Import Gate

answer: {summary['status']}

reason: This importer makes the human-filled external customer validation
session entry compatible with the existing local customer-validation validator.
It does not perform the session, contact customers, infer missing answers,
execute evidence builders, close blockers, or claim validation.

status: {summary['status']}
human_entry_template_ready: true
human_filled_output_written: {str(summary['human_filled_output_written']).lower()}
ready_for_existing_customer_validation_validator: {str(summary['ready_for_existing_customer_validation_validator']).lower()}
current_goal_blocker: customer_validated

boundary:
customer_validated: false
production_ready: false
product_launched: false
customer_contacted_by_codex: false
private_core_exposed: false
evidence_builder_executed: false
blockers_closed_by_importer: 0

next_action: Human fills the session entry template from real customer or
target-user feedback, then runs the importer with `--apply`.
"""


def write_outputs(summary: dict[str, Any]) -> None:
    write_json(IMPORT_SUMMARY, summary)
    IMPORT_REPORT.write_text(render_report(summary), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary(summary), encoding="utf-8")
    GATE.write_text(render_gate(summary), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare/import one human-filled external customer validation session entry."
    )
    parser.add_argument("--input", default=str(ENTRY_HUMAN_FILLED))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build_summary(Path(args.input), args.apply)
    write_outputs(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_IMPORTER: PASS "
            f"status={summary['status']} "
            f"human_filled_output_written={str(summary['human_filled_output_written']).lower()} "
            "customer_validated=false production_ready=false"
        )


if __name__ == "__main__":
    main()
