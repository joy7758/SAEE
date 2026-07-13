#!/usr/bin/env python3
"""Validate human-filled privacy/legal + DPA input before the builder.

This validator checks completeness and boundary safety only. It does not
perform legal review, create or approve a DPA, contact legal counsel, process
customer data, publish terms or privacy notices, close blockers, or claim
production readiness.
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

from scripts.saee_privacy_legal_dpa_evidence_builder import (
    DEFAULT_INPUT_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    TARGET_KEYS,
    boundary_violations,
    completed_artifacts,
    ensure_default_template,
    evidence_review_flags,
    input_metadata_complete,
    source_notes,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "privacy_legal_dpa_approval_input_validation.local.json"
REPORT_PATH = OUTPUT_DIR / "privacy_legal_dpa_approval_input_validation.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)


METADATA_FIELDS = (
    "human_reviewer_name",
    "review_date",
    "legal_owner",
    "privacy_owner",
    "dpa_owner",
    "review_record_reference",
    "decision_summary",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR: FAIL " + message
        )


def read_json(path: Path) -> dict[str, Any]:
    ensure_default_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR: FAIL "
            f"invalid input {path}: {exc}"
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
    return [key for key in TARGET_KEYS if not flags[key]]


def missing_source_notes(data: dict[str, Any]) -> list[str]:
    notes = source_notes(data)
    return [key for key in TARGET_KEYS if not notes.get(key)]


def missing_review_artifacts(data: dict[str, Any]) -> list[str]:
    artifacts = completed_artifacts(data)
    return [key for key in TARGET_KEYS if key not in artifacts]


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    violations = boundary_violations(data)
    metadata_missing = missing_metadata_fields(data)
    evidence_missing = missing_evidence_review(data)
    notes_missing = missing_source_notes(data)
    artifacts_missing = missing_review_artifacts(data)
    metadata_complete = input_metadata_complete(data)
    evidence_review_complete = not evidence_missing
    source_notes_complete = not notes_missing
    review_artifacts_complete = not artifacts_missing
    input_complete = (
        data.get("template_type") == "saee_privacy_legal_dpa_evidence_input"
        and metadata_complete
        and evidence_review_complete
        and source_notes_complete
        and review_artifacts_complete
        and not violations
    )
    validation_status = "stop" if violations else ("pass" if input_complete else "hold")
    builder_ready = validation_status == "pass"

    return {
        "validator_type": "saee_privacy_legal_dpa_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_privacy_legal_dpa_input_pre_builder_check",
        "target_blocker_ids": [
            "privacy_legal_review",
            "data_processing_agreement",
        ],
        "category": "privacy_security_legal",
        "generated_by": "scripts/saee_privacy_legal_dpa_approval_input_validator.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(
            input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path
        ),
        "validation_status": validation_status,
        "input_complete": input_complete,
        "builder_ready": builder_ready,
        "metadata_complete": metadata_complete,
        "evidence_review_complete": evidence_review_complete,
        "source_notes_complete": source_notes_complete,
        "review_artifacts_complete": review_artifacts_complete,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "required_privacy_legal_dpa_evidence_item_count": len(TARGET_KEYS),
        "completed_review_artifact_count": len(completed_artifacts(data)),
        "missing_metadata_fields": metadata_missing,
        "missing_evidence_review": evidence_missing,
        "missing_source_notes": notes_missing,
        "missing_review_artifacts": artifacts_missing,
        "boundary_review_key_count": len(INPUT_FORBIDDEN_TRUE_KEYS),
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_validator": 0,
        "privacy_legal_review_approved_by_validator": False,
        "privacy_legal_review_completed_by_validator": False,
        "data_processing_agreement_approved_by_validator": False,
        "data_processing_agreement_completed_by_validator": False,
        "legal_review_performed_by_validator": False,
        "dpa_created_by_validator": False,
        "dpa_approved_by_validator": False,
        "legal_counsel_contacted_by_validator": False,
        "customer_data_processed_by_validator": False,
        "terms_published_by_validator": False,
        "privacy_notice_published_by_validator": False,
        "dpa_sent_to_customer_by_validator": False,
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
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
        "production_security_enabled": False,
        "vulnerability_management_operational": False,
        "codex_performed_legal_review": False,
        "codex_contacted_legal_counsel": False,
        "codex_created_dpa": False,
        "codex_approved_dpa": False,
        "codex_processed_customer_data": False,
        "codex_inferred_missing_evidence": False,
        "privacy_legal_review_completed_by_codex": False,
        "data_processing_agreement_completed_by_codex": False,
        "legal_review_execution_authorized": False,
        "legal_review_claim_published": False,
        "dpa_availability_claim_published": False,
        "customer_data_processing_claim_published": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
        "next_action": (
            "If validation_status is pass, a human may run the privacy/legal + "
            "DPA evidence builder in a separate approved evidence request; "
            "otherwise complete missing input fields or resolve boundary violations first."
        ),
    }


def list_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE Privacy/Legal + DPA Approval Input Validation

Status: {validation['validation_status']}.

This report validates the human-filled privacy/legal + DPA input before it is
passed into the existing privacy/legal + DPA evidence builder. It does not
perform legal review, create or approve a DPA, contact legal counsel, process
customer data, publish terms or privacy notices, close blockers, or claim
production readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- target_blocker_ids: privacy_legal_review,data_processing_agreement
- input_complete: {str(validation['input_complete']).lower()}
- builder_ready: {str(validation['builder_ready']).lower()}
- blockers_closed_by_validator: {validation['blockers_closed_by_validator']}
- privacy_legal_review_approved_by_validator: false
- privacy_legal_review_completed_by_validator: false
- data_processing_agreement_approved_by_validator: false
- data_processing_agreement_completed_by_validator: false
- legal_review_performed_by_validator: false
- dpa_created_by_validator: false
- dpa_approved_by_validator: false
- legal_counsel_contacted_by_validator: false
- customer_data_processed_by_validator: false
- terms_published_by_validator: false
- privacy_notice_published_by_validator: false
- dpa_sent_to_customer_by_validator: false
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

## Missing Review Artifacts

{list_lines(validation['missing_review_artifacts'])}

## Boundary Violations

{list_lines(validation['boundary_violations'])}

## Boundary Statement

The validator is pre-builder input validation only. It does not perform legal
review, create or approve a DPA, contact legal counsel, process customer data,
publish terms or privacy notices, send a DPA to customers, close blockers, or
make SAEE production-ready.

## Next Action

If validation_status is pass, a human may run the privacy/legal + DPA evidence
builder in a separate approved evidence request. This validator itself closes
no blockers and authorizes no legal, privacy, DPA, production, or customer-data
claim.
"""


def write_docs(validation: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# SAEE Privacy/Legal + DPA Approval Input Validator v0.1

privacy_legal_dpa_approval_input_validator_v0_1: true
validator_scope: local_human_filled_privacy_legal_dpa_input_pre_builder_check
default_validation_status: {validation['validation_status']}
default_input_complete: {str(validation['input_complete']).lower()}
default_builder_ready: {str(validation['builder_ready']).lower()}
target_blocker_ids: privacy_legal_review,data_processing_agreement
required_metadata_field_count: {validation['required_metadata_field_count']}
required_privacy_legal_dpa_evidence_item_count: {validation['required_privacy_legal_dpa_evidence_item_count']}
blockers_closed_by_validator: 0
privacy_legal_review_approved_by_validator: false
privacy_legal_review_completed_by_validator: false
data_processing_agreement_approved_by_validator: false
data_processing_agreement_completed_by_validator: false
legal_review_performed_by_validator: false
dpa_created_by_validator: false
dpa_approved_by_validator: false
legal_counsel_contacted_by_validator: false
customer_data_processed_by_validator: false
terms_published_by_validator: false
privacy_notice_published_by_validator: false
dpa_sent_to_customer_by_validator: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether the human-filled privacy/legal + DPA input is
complete and boundary-safe before it is passed to the existing privacy/legal +
DPA evidence builder.

## Boundary

The validator is pre-builder input validation only. It does not perform legal
review, create or approve a DPA, contact legal counsel, process customer data,
publish terms, publish a privacy notice, send a DPA to customers, collect
evidence, close blockers, modify runtime/backend/kernel/API schema/private
core, launch product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_validation.md`
- script: `scripts/saee_privacy_legal_dpa_approval_input_validator.py`
- smoke: `scripts/saee_privacy_legal_dpa_approval_input_validator_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Privacy/Legal + DPA Approval Input Validator Recommendation Gate

answer: conditional

recommend_for_human_input_validation: true
recommend_for_privacy_legal_review_approval: false
recommend_for_data_processing_agreement_approval: false
recommend_for_legal_review_completion_claim: false
recommend_for_dpa_availability_claim: false
recommend_for_customer_data_processing_claim: false
recommend_for_evidence_collection_authorization: false
recommend_for_blocker_closure: false
recommend_for_legal_counsel_contact: false
recommend_for_customer_contact: false
recommend_for_terms_publication: false
recommend_for_privacy_notice_publication: false
recommend_for_dpa_customer_send: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful because it catches missing human input and boundary
violations before the privacy/legal + DPA evidence builder is run. It is not
legal review execution, does not approve a DPA, and does not close either
privacy/legal or data-processing blocker by itself.

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
legal_counsel_contacted: false
customer_data_processed: false
dpa_sent_to_customer: false
terms_published: false
privacy_notice_published: false
codex_performed_legal_review: false
codex_contacted_legal_counsel: false
codex_created_dpa: false
codex_approved_dpa: false
codex_processed_customer_data: false
privacy_legal_review_completed_by_validator: false
data_processing_agreement_completed_by_validator: false
legal_review_performed_by_validator: false
dpa_created_by_validator: false
dpa_approved_by_validator: false
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
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR: PASS "
            f"status={validation['validation_status']} "
            f"builder_ready={str(validation['builder_ready']).lower()} "
            "blockers_closed_by_validator=0 production_ready=false"
        )


if __name__ == "__main__":
    main()
