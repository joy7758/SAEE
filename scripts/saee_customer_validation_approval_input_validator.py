#!/usr/bin/env python3
"""Validate human-filled customer-validation input before evidence building.

This validator checks completeness and boundary safety only. It does not
contact customers, run pilot sessions, infer missing results, approve customer
validation, publish validation claims, close blockers, or claim production
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_customer_validation_evidence_builder import (
    INPUT_TEMPLATE_PATH,
    NUMERIC_SCORE_FIELDS,
    REVIEW_KEY_GROUPS,
    SESSION_BOUNDARY_FALSE_KEYS,
    SESSION_REQUIRED_TEXT_FIELDS,
    boundary_violations,
    completed_sessions,
    session_has_required_fields,
    write_template,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
DEFAULT_INPUT_PATH = INPUT_TEMPLATE_PATH
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "customer_validation_approval_input_validation.local.json"
REPORT_PATH = OUTPUT_DIR / "customer_validation_approval_input_validation.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

MISSING_SESSION_FINDING = "no_completed_human_pilot_session"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR: FAIL " + message
        )


def ensure_input_template(path: Path) -> None:
    if path == INPUT_TEMPLATE_PATH and not path.exists():
        write_template()


def read_json(path: Path) -> dict[str, Any]:
    ensure_input_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR: FAIL "
            f"invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input must be object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: review.get(key) is True for key in REVIEW_KEY_GROUPS}


def missing_evidence_review(data: dict[str, Any]) -> list[str]:
    flags = evidence_review_flags(data)
    return [key for key in REVIEW_KEY_GROUPS if not flags[key]]


def raw_sessions(data: dict[str, Any]) -> list[Any]:
    sessions = data.get("sessions", [])
    return sessions if isinstance(sessions, list) else []


def incomplete_session_indices(data: dict[str, Any]) -> list[int]:
    return [
        index
        for index, session in enumerate(raw_sessions(data))
        if not isinstance(session, dict) or not session_has_required_fields(session)
    ]


def blocking_boundary_violations(data: dict[str, Any], completed: list[dict[str, Any]]) -> list[str]:
    findings = boundary_violations(data, completed)
    return [finding for finding in findings if finding != MISSING_SESSION_FINDING]


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    completed = completed_sessions(data)
    blocking_violations = blocking_boundary_violations(data, completed)
    missing_review = missing_evidence_review(data)
    raw = raw_sessions(data)
    raw_sessions_valid = isinstance(data.get("sessions", []), list)
    incomplete_indices = incomplete_session_indices(data)
    missing_completed_session = not completed
    template_flag_valid = data.get("customer_validation_evidence_input_v0_1") is True
    evidence_review_complete = not missing_review
    session_input_complete = (
        raw_sessions_valid
        and bool(raw)
        and bool(completed)
        and len(completed) == len(raw)
        and not incomplete_indices
    )
    input_complete = (
        template_flag_valid
        and evidence_review_complete
        and session_input_complete
        and not missing_completed_session
        and not blocking_violations
    )
    validation_status = "stop" if blocking_violations else ("pass" if input_complete else "hold")
    builder_ready = validation_status == "pass"

    return {
        "validator_type": "saee_customer_validation_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_customer_validation_input_pre_builder_check",
        "target_blocker_ids": ["pilot_results", "customer_validated"],
        "generated_by": "scripts/saee_customer_validation_approval_input_validator.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path),
        "validation_status": validation_status,
        "input_complete": input_complete,
        "builder_ready": builder_ready,
        "template_flag_valid": template_flag_valid,
        "evidence_review_complete": evidence_review_complete,
        "session_input_complete": session_input_complete,
        "required_review_key_count": len(REVIEW_KEY_GROUPS),
        "completed_review_key_count": len(REVIEW_KEY_GROUPS) - len(missing_review),
        "missing_evidence_review": missing_review,
        "raw_session_count": len(raw),
        "completed_session_count": len(completed),
        "missing_completed_session": missing_completed_session,
        "incomplete_session_indices": incomplete_indices,
        "required_session_text_fields": list(SESSION_REQUIRED_TEXT_FIELDS),
        "required_session_score_fields": list(NUMERIC_SCORE_FIELDS),
        "required_session_boundary_false_keys": list(SESSION_BOUNDARY_FALSE_KEYS),
        "boundary_violation_count": len(blocking_violations),
        "boundary_violations": blocking_violations,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_validator": 0,
        "pilot_results_recorded_by_validator": False,
        "customer_validation_approved_by_validator": False,
        "customer_validation_claim_published_by_validator": False,
        "customer_validation_evidence_built_by_validator": False,
        "production_customer_validation_ready_by_validator": False,
        "codex_contacted_customer": False,
        "codex_executed_pilot": False,
        "codex_inferred_missing_results": False,
        "codex_collected_customer_data": False,
        "codex_published_validation_claim": False,
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
        "automated_customer_contact": False,
        "customer_data_collected": False,
        "customer_secrets_collected": False,
        "user_upload_enabled": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "paid_pilot_completed": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
        "next_action": (
            "If validation_status is pass, a human may run the customer "
            "validation evidence builder in a separate approved evidence "
            "request; otherwise complete missing input fields or resolve "
            "boundary violations first."
        ),
    }


def list_lines(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE Customer Validation Approval Input Validation

Status: {validation['validation_status']}.

This report validates the human-filled customer-validation input before it is
passed into the existing customer validation evidence builder. It does not run
pilot sessions, contact customers, infer missing results, approve customer
validation, publish validation claims, close blockers, or claim production
readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- target_blocker_ids: {', '.join(validation['target_blocker_ids'])}
- input_complete: {str(validation['input_complete']).lower()}
- builder_ready: {str(validation['builder_ready']).lower()}
- template_flag_valid: {str(validation['template_flag_valid']).lower()}
- evidence_review_complete: {str(validation['evidence_review_complete']).lower()}
- session_input_complete: {str(validation['session_input_complete']).lower()}
- completed_session_count: {validation['completed_session_count']}
- blockers_closed_by_validator: {validation['blockers_closed_by_validator']}
- pilot_results_recorded_by_validator: false
- customer_validation_approved_by_validator: false
- customer_validation_claim_published_by_validator: false
- production_customer_validation_ready_by_validator: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Missing Evidence Review Keys

{list_lines(validation['missing_evidence_review'])}

## Incomplete Session Indices

{list_lines(validation['incomplete_session_indices'])}

## Boundary Violations

{list_lines(validation['boundary_violations'])}

## Next Action

If validation_status is pass, a human may run the customer validation evidence
builder in a separate approved evidence request. This validator itself closes
no blockers and authorizes no customer validation claim.
"""


def write_docs(validation: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# SAEE Customer Validation Approval Input Validator v0.1

customer_validation_approval_input_validator_v0_1: true
validator_scope: local_human_filled_customer_validation_input_pre_builder_check
default_validation_status: {validation['validation_status']}
default_input_complete: {str(validation['input_complete']).lower()}
default_builder_ready: {str(validation['builder_ready']).lower()}
target_blocker_ids: pilot_results, customer_validated
required_review_key_count: {validation['required_review_key_count']}
completed_session_count: {validation['completed_session_count']}
blockers_closed_by_validator: 0
pilot_results_recorded_by_validator: false
customer_validation_approved_by_validator: false
customer_validation_claim_published_by_validator: false
customer_validation_evidence_built_by_validator: false
production_customer_validation_ready_by_validator: false
codex_contacted_customer: false
codex_executed_pilot: false
codex_inferred_missing_results: false
codex_collected_customer_data: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether human-filled customer-validation input is complete
and boundary-safe before it is passed to the existing customer validation
evidence builder.

## Boundary

The validator is pre-builder input validation only. It does not contact
customers, run pilot sessions, infer missing results, approve customer
validation, publish validation claims, collect customer data, create
testimonials, close blockers, modify runtime/backend/kernel/API schema/private
core, launch product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.md`
- script: `scripts/saee_customer_validation_approval_input_validator.py`
- smoke: `scripts/saee_customer_validation_approval_input_validator_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Customer Validation Approval Input Validator Recommendation Gate

answer: conditional

recommend_for_human_input_validation: true
recommend_for_evidence_builder_execution: false
recommend_for_customer_contact: false
recommend_for_pilot_execution: false
recommend_for_customer_validation_claim: false
recommend_for_customer_validation_approval: false
recommend_for_blocker_closure: false
recommend_for_product_market_fit_claim: false
recommend_for_testimonial_publication: false
recommend_for_case_study_publication: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful because it catches missing human input and boundary
violations before the customer validation evidence builder is run. It is not a
pilot execution tool, not customer validation approval, and does not close the
pilot-results or customer-validation blockers by itself.

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
automated_customer_contact: false
customer_data_collected: false
customer_secrets_collected: false
public_validation_claim_published: false
testimonial_published: false
case_study_published: false
paid_pilot_completed: false
pilot_results_recorded_by_validator: false
customer_validation_approved_by_validator: false
customer_validation_claim_published_by_validator: false
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
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR: PASS "
            f"status={validation['validation_status']} "
            f"builder_ready={str(validation['builder_ready']).lower()} "
            "blockers_closed_by_validator=0 customer_validated=false"
        )


if __name__ == "__main__":
    main()
