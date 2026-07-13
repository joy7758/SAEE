#!/usr/bin/env python3
"""Validate human-filled production identity-provider input before evidence use.

This validator checks completeness and boundary safety only. It does not select
or contact an identity provider, fetch JWKS, validate production tokens, enable
production authentication, enforce production RBAC, close blockers, or claim
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

from scripts.saee_production_identity_provider_decision_packet import (
    FALSE_FLAGS,
    OUTPUT_TEMPLATE,
    TARGET_KEYS,
    input_template,
    write_json as write_decision_json,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
DEFAULT_INPUT_PATH = OUTPUT_TEMPLATE
DEFAULT_OUTPUT_PATH = (
    OUTPUT_DIR / "production_identity_provider_approval_input_validation.local.json"
)
REPORT_PATH = OUTPUT_DIR / "production_identity_provider_approval_input_validation.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

REQUIRED_TEXT_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "selected_provider_name",
    "decision_summary",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR: FAIL "
            + message
        )


def ensure_input_template(path: Path) -> None:
    if path == OUTPUT_TEMPLATE and not path.exists():
        write_decision_json(path, input_template())


def read_json(path: Path) -> dict[str, Any]:
    ensure_input_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR: FAIL "
            f"invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input must be object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def missing_required_text_fields(data: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_TEXT_FIELDS if not nonempty_text(data.get(field))]


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: review.get(key) is True for key in TARGET_KEYS}


def missing_evidence_review(data: dict[str, Any]) -> list[str]:
    flags = evidence_review_flags(data)
    return [key for key in TARGET_KEYS if not flags[key]]


def missing_source_notes(data: dict[str, Any]) -> list[str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        notes = {}
    return [key for key in TARGET_KEYS if not nonempty_text(notes.get(key))]


def boundary_violations(data: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    boundary = data.get("boundary_review", {})
    if not isinstance(boundary, dict):
        findings.append("boundary_review_not_object")
        boundary = {}
    for flag in FALSE_FLAGS:
        if boundary.get(flag) is not False:
            findings.append(f"boundary_review.{flag}_must_remain_false")
        if data.get(flag) is True:
            findings.append(f"top_level.{flag}_must_not_be_true")
    return findings


def candidate_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("candidate_provider_slots", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def selected_slot(data: dict[str, Any]) -> dict[str, Any] | None:
    selected = str(data.get("selected_provider_name", "")).strip()
    if not selected:
        return None
    for slot in candidate_slots(data):
        if str(slot.get("provider_name", "")).strip() == selected:
            return slot
    return None


def selected_slot_missing_fields(data: dict[str, Any]) -> list[str]:
    slot = selected_slot(data)
    if slot is None:
        return ["selected_provider_slot"]
    missing: list[str] = []
    for field in [
        "provider_name",
        "human_source_note",
    ]:
        if not nonempty_text(slot.get(field)):
            missing.append(field)
    for field in [
        "oidc_supported",
        "admin_owner_named",
        "issuer_reviewed",
        "audience_reviewed",
        "jwks_rotation_reviewed",
    ]:
        if slot.get(field) is not True:
            missing.append(field)
    return missing


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    missing_text = missing_required_text_fields(data)
    missing_review = missing_evidence_review(data)
    missing_notes = missing_source_notes(data)
    missing_slot = selected_slot_missing_fields(data)
    violations = boundary_violations(data)
    template_flag_valid = (
        data.get("template_type") == "saee_production_identity_provider_decision_input"
        and data.get("template_version") == "v0.1"
    )
    input_status_filled = data.get("input_status") != "template_not_filled"
    text_complete = not missing_text
    evidence_review_complete = not missing_review
    source_notes_complete = not missing_notes
    selected_candidate_complete = not missing_slot
    input_complete = (
        template_flag_valid
        and input_status_filled
        and text_complete
        and evidence_review_complete
        and source_notes_complete
        and selected_candidate_complete
        and not violations
    )
    validation_status = "stop" if violations else ("pass" if input_complete else "hold")
    builder_ready = validation_status == "pass"

    return {
        "validator_type": "saee_production_identity_provider_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": (
            "local_human_filled_production_identity_provider_input_pre_builder_check"
        ),
        "target_blocker_ids": ["production_identity_provider"],
        "generated_by": (
            "scripts/saee_production_identity_provider_approval_input_validator.py"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": rel_path(input_path),
        "validation_status": validation_status,
        "input_complete": input_complete,
        "builder_ready": builder_ready,
        "template_flag_valid": template_flag_valid,
        "input_status_filled": input_status_filled,
        "text_complete": text_complete,
        "evidence_review_complete": evidence_review_complete,
        "source_notes_complete": source_notes_complete,
        "selected_candidate_complete": selected_candidate_complete,
        "required_text_fields": list(REQUIRED_TEXT_FIELDS),
        "missing_required_text_fields": missing_text,
        "required_review_key_count": len(TARGET_KEYS),
        "completed_review_key_count": len(TARGET_KEYS) - len(missing_review),
        "missing_evidence_review": missing_review,
        "missing_source_notes": missing_notes,
        "selected_candidate_missing_fields": missing_slot,
        "candidate_provider_slot_count": len(candidate_slots(data)),
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_validator": 0,
        "production_identity_provider_selected_by_validator": False,
        "production_identity_provider_approved_by_validator": False,
        "production_identity_provider_available_by_validator": False,
        "production_auth_evidence_built_by_validator": False,
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "production_auth_ready": False,
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
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "production_auth_enabled": False,
        "rbac_enforced_in_production": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
        "next_action": (
            "If validation_status is pass, a human may run the Phase 1 "
            "identity/tenant evidence builder in a separate approved evidence "
            "request; otherwise complete missing input fields or resolve "
            "boundary violations first."
        ),
    }


def list_lines(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE Production Identity Provider Approval Input Validation

Status: {validation['validation_status']}.

This report validates the human-filled production identity-provider decision
input before it is copied into downstream production-auth evidence builders. It
does not select or contact an identity provider, fetch JWKS, validate
production tokens, enable production authentication, close blockers, or claim
production readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- target_blocker_ids: {', '.join(validation['target_blocker_ids'])}
- input_complete: {str(validation['input_complete']).lower()}
- builder_ready: {str(validation['builder_ready']).lower()}
- template_flag_valid: {str(validation['template_flag_valid']).lower()}
- input_status_filled: {str(validation['input_status_filled']).lower()}
- text_complete: {str(validation['text_complete']).lower()}
- evidence_review_complete: {str(validation['evidence_review_complete']).lower()}
- source_notes_complete: {str(validation['source_notes_complete']).lower()}
- selected_candidate_complete: {str(validation['selected_candidate_complete']).lower()}
- completed_review_key_count: {validation['completed_review_key_count']}
- blockers_closed_by_validator: {validation['blockers_closed_by_validator']}
- production_identity_provider_selected_by_validator: false
- production_identity_provider_approved_by_validator: false
- production_identity_provider_available_by_validator: false
- codex_contacted_identity_provider: false
- codex_fetched_jwks: false
- codex_validated_production_tokens: false
- production_auth_ready: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Missing Required Text Fields

{list_lines(validation['missing_required_text_fields'])}

## Missing Evidence Review Keys

{list_lines(validation['missing_evidence_review'])}

## Missing Source Notes

{list_lines(validation['missing_source_notes'])}

## Selected Candidate Missing Fields

{list_lines(validation['selected_candidate_missing_fields'])}

## Boundary Violations

{list_lines(validation['boundary_violations'])}

## Next Action

If validation_status is pass, a human may run the Phase 1 identity/tenant
evidence builder in a separate approved evidence request. This validator itself
closes no blockers, enables no authentication, and authorizes no external
identity-provider action.
"""


def write_docs(validation: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# SAEE Production Identity Provider Approval Input Validator v0.1

production_identity_provider_approval_input_validator_v0_1: true
validator_scope: local_human_filled_production_identity_provider_input_pre_builder_check
default_validation_status: {validation['validation_status']}
default_input_complete: {str(validation['input_complete']).lower()}
default_builder_ready: {str(validation['builder_ready']).lower()}
target_blocker_ids: production_identity_provider
required_review_key_count: {validation['required_review_key_count']}
completed_review_key_count: {validation['completed_review_key_count']}
blockers_closed_by_validator: 0
production_identity_provider_selected_by_validator: false
production_identity_provider_approved_by_validator: false
production_identity_provider_available_by_validator: false
production_auth_evidence_built_by_validator: false
codex_contacted_identity_provider: false
codex_fetched_jwks: false
codex_validated_production_tokens: false
production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether human-filled production identity-provider input
is complete and boundary-safe before it is copied into existing Phase 1
identity/tenant evidence builders.

## Boundary

The validator is pre-builder input validation only. It does not select or
contact an identity provider, fetch JWKS, validate production tokens, enable
production authentication, enforce production RBAC, close blockers, modify
runtime/backend/kernel/API schema/private core, launch product, or claim
production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json`
- validation output: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.md`
- script: `scripts/saee_production_identity_provider_approval_input_validator.py`
- smoke: `scripts/saee_production_identity_provider_approval_input_validator_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Production Identity Provider Approval Input Validator Recommendation Gate

answer: conditional

recommend_for_human_input_validation: true
recommend_for_evidence_builder_execution: false
recommend_for_identity_provider_selection: false
recommend_for_identity_provider_contact: false
recommend_for_jwks_fetch: false
recommend_for_token_validation: false
recommend_for_auth_enablement: false
recommend_for_rbac_enforcement: false
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful because it catches missing identity-provider decision
input and boundary violations before downstream auth evidence builders are run.
It is not an identity-provider selector, not an OAuth/OIDC implementation, not
production auth approval, and does not close the `production_identity_provider`
blocker by itself.

## Boundary

production_identity_provider_available: false
oauth_oidc_available: false
rbac_available: false
production_auth_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
identity_provider_contacted_by_codex: false
jwks_fetched_by_codex: false
production_tokens_validated_by_codex: false
production_auth_enabled: false
rbac_enforced_in_production: false
production_identity_provider_selected_by_validator: false
production_identity_provider_approved_by_validator: false
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
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_APPROVAL_INPUT_VALIDATOR: PASS "
            f"status={validation['validation_status']} "
            f"builder_ready={str(validation['builder_ready']).lower()} "
            "blockers_closed_by_validator=0 production_auth_ready=false"
        )


if __name__ == "__main__":
    main()
