#!/usr/bin/env python3
"""Validate human-filled tenant storage evidence input before builder use.

This validator checks completeness and boundary safety only. It does not
implement production multi-tenancy, modify storage behavior, run migrations,
process customer data, close blockers, or claim production readiness.
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

from saee_backend.services.production_tenant_storage_evidence import (
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
)
from scripts.saee_phase1_identity_tenant_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    INPUT_TEMPLATE_PATH,
    input_template,
    write_json as write_builder_json,
)


OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
DEFAULT_INPUT_PATH = INPUT_TEMPLATE_PATH
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "tenant_storage_approval_input_validation.local.json"
REPORT_PATH = OUTPUT_DIR / "tenant_storage_approval_input_validation.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

TARGET_EVIDENCE_KEYS = (
    TENANT_STORAGE_MODEL_KEYS
    + TENANT_ISOLATION_TEST_KEYS
    + TENANT_OPERATIONS_KEYS
    + TENANT_SECURITY_PRIVACY_KEYS
)
REQUIRED_TEXT_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "evidence_source_notes",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR: FAIL " + message)


def ensure_input_template(path: Path) -> None:
    if path == INPUT_TEMPLATE_PATH and not path.exists():
        write_builder_json(path, input_template())


def read_json(path: Path) -> dict[str, Any]:
    ensure_input_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR: FAIL invalid input {path}: {exc}"
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
    return {key: review.get(key) is True for key in TARGET_EVIDENCE_KEYS}


def missing_evidence_review(data: dict[str, Any]) -> list[str]:
    flags = evidence_review_flags(data)
    return [key for key in TARGET_EVIDENCE_KEYS if not flags[key]]


def missing_source_notes(data: dict[str, Any]) -> list[str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        notes = {}
    return [key for key in TARGET_EVIDENCE_KEYS if not nonempty_text(notes.get(key))]


def boundary_violations(data: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    boundary = data.get("boundary_review", {})
    if not isinstance(boundary, dict):
        findings.append("boundary_review_not_object")
        boundary = {}
    for flag in INPUT_FORBIDDEN_TRUE_KEYS:
        if boundary.get(flag) is not False:
            findings.append(f"boundary_review.{flag}_must_remain_false")
        if data.get(flag) is True:
            findings.append(f"top_level.{flag}_must_not_be_true")
    return findings


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    missing_text = missing_required_text_fields(data)
    missing_review = missing_evidence_review(data)
    missing_notes = missing_source_notes(data)
    violations = boundary_violations(data)
    template_flag_valid = data.get("phase_1_identity_tenant_evidence_input_v0_1") is True
    input_status_filled = data.get("input_status") != "template_not_filled"
    text_complete = not missing_text
    evidence_review_complete = not missing_review
    source_notes_complete = not missing_notes
    input_complete = (
        template_flag_valid
        and input_status_filled
        and text_complete
        and evidence_review_complete
        and source_notes_complete
        and not violations
    )
    validation_status = "stop" if violations else ("pass" if input_complete else "hold")
    builder_ready = validation_status == "pass"

    return {
        "validator_type": "saee_tenant_storage_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_tenant_storage_input_pre_builder_check",
        "target_blocker_ids": ["tenant_storage_isolation"],
        "target_evidence_keys": list(TARGET_EVIDENCE_KEYS),
        "target_evidence_key_groups": {
            "tenant_storage_model": list(TENANT_STORAGE_MODEL_KEYS),
            "tenant_isolation_tests": list(TENANT_ISOLATION_TEST_KEYS),
            "tenant_operations": list(TENANT_OPERATIONS_KEYS),
            "tenant_security_privacy": list(TENANT_SECURITY_PRIVACY_KEYS),
        },
        "generated_by": "scripts/saee_tenant_storage_approval_input_validator.py",
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
        "required_text_fields": list(REQUIRED_TEXT_FIELDS),
        "missing_required_text_fields": missing_text,
        "required_review_key_count": len(TARGET_EVIDENCE_KEYS),
        "completed_review_key_count": len(TARGET_EVIDENCE_KEYS) - len(missing_review),
        "missing_evidence_review": missing_review,
        "missing_source_notes": missing_notes,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_validator": 0,
        "tenant_storage_approved_by_validator": False,
        "tenant_storage_available_by_validator": False,
        "tenant_storage_isolation_evidence_complete_by_validator": False,
        "production_tenant_storage_evidence_built_by_validator": False,
        "tenant_storage_isolated": False,
        "production_tenant_storage_isolated": False,
        "production_tenant_storage_enabled": False,
        "multi_tenant_production_ready": False,
        "tenant_authorization_enabled": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "production_database_modified": False,
        "storage_behavior_modified": False,
        "migration_executed": False,
        "live_customer_data_migrated": False,
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
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
        "next_action": (
            "If validation_status is pass, a human may run the Phase 1 "
            "identity/tenant evidence builder in a separate approved evidence "
            "request; otherwise complete missing tenant storage source notes or "
            "resolve boundary violations first."
        ),
    }


def list_lines(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def report_markdown(validation: dict[str, Any]) -> str:
    return f"""# SAEE Tenant Storage Approval Input Validation

Status: {validation['validation_status']}.

This report validates the human-filled tenant storage evidence fields in the
Phase 1 identity/tenant evidence input before downstream evidence-builder use.
It does not implement production multi-tenancy, modify storage behavior, run
migrations, process customer data, close blockers, or claim production
readiness.

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
- completed_review_key_count: {validation['completed_review_key_count']}
- blockers_closed_by_validator: {validation['blockers_closed_by_validator']}
- tenant_storage_approved_by_validator: false
- tenant_storage_available_by_validator: false
- tenant_storage_isolation_evidence_complete_by_validator: false
- tenant_storage_isolated: false
- production_tenant_storage_isolated: false
- production_tenant_storage_enabled: false
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

## Boundary Violations

{list_lines(validation['boundary_violations'])}

## Next Action

If validation_status is pass, a human may run the Phase 1 identity/tenant
evidence builder in a separate approved evidence request. This validator itself
closes no blockers, modifies no storage behavior, runs no migrations, processes
no customer data, and authorizes no production tenant storage action.
"""


def write_docs(validation: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# SAEE Tenant Storage Approval Input Validator v0.1

tenant_storage_approval_input_validator_v0_1: true
validator_scope: local_human_filled_tenant_storage_input_pre_builder_check
default_validation_status: {validation['validation_status']}
default_input_complete: {str(validation['input_complete']).lower()}
default_builder_ready: {str(validation['builder_ready']).lower()}
target_blocker_ids: tenant_storage_isolation
required_review_key_count: {validation['required_review_key_count']}
completed_review_key_count: {validation['completed_review_key_count']}
blockers_closed_by_validator: 0
tenant_storage_approved_by_validator: false
tenant_storage_available_by_validator: false
tenant_storage_isolation_evidence_complete_by_validator: false
production_tenant_storage_evidence_built_by_validator: false
tenant_storage_isolated: false
production_tenant_storage_isolated: false
production_tenant_storage_enabled: false
multi_tenant_production_ready: false
tenant_authorization_enabled: false
customer_data_processed: false
storage_behavior_modified: false
migration_executed: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether human-filled tenant storage evidence input is
complete and boundary-safe before it is copied into the existing Phase 1
identity/tenant evidence builder.

## Target Evidence Groups

Tenant storage model:

- production_tenant_data_model_approved
- tenant_scoped_primary_keys_or_partitions_reviewed
- tenant_query_enforcement_design_reviewed
- tenant_storage_migration_plan_reviewed

Tenant isolation tests:

- same_experiment_id_cross_tenant_partition_tests_passed
- cross_tenant_read_denial_tests_passed
- cross_tenant_write_denial_tests_passed
- tenant_scoped_listing_tests_passed
- tenant_scoped_report_endpoint_tests_passed

Tenant operations:

- tenant_scoped_audit_metadata_reviewed
- tenant_backup_restore_boundary_approved
- tenant_deletion_retention_boundary_approved
- tenant_storage_observability_plan_reviewed

Tenant security/privacy:

- tenant_authorization_policy_reviewed
- tenant_secret_boundary_reviewed
- security_review_completed
- privacy_legal_review_completed
- customer_data_processing_non_claim_reviewed

## Boundary

The validator is pre-builder input validation only. It does not implement
production multi-tenancy, modify storage behavior, run migrations, process
customer data, enable production tenant storage, close blockers, modify
runtime/backend/kernel/API schema/private core, launch product, or claim
production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json`
- validation output: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_validation.md`
- script: `scripts/saee_tenant_storage_approval_input_validator.py`
- smoke: `scripts/saee_tenant_storage_approval_input_validator_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Tenant Storage Approval Input Validator Recommendation Gate

answer: conditional

recommend_for_human_input_validation: true
recommend_for_evidence_builder_execution: false
recommend_for_storage_behavior_change: false
recommend_for_storage_migration: false
recommend_for_customer_data_processing: false
recommend_for_tenant_storage_enablement: false
recommend_for_tenant_storage_isolation_claim: false
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful because it catches missing tenant storage approval
input, missing source notes, and boundary violations before downstream Phase 1
tenant storage evidence builders are run. It is not production multi-tenancy,
not storage migration, not customer-data processing approval, and does not
close the `tenant_storage_isolation` blocker by itself.

## Boundary

tenant_storage_available_by_validator: false
tenant_storage_isolation_evidence_complete_by_validator: false
tenant_storage_isolated: false
production_tenant_storage_isolated: false
production_tenant_storage_enabled: false
multi_tenant_production_ready: false
tenant_authorization_enabled: false
customer_data_processed: false
storage_behavior_modified: false
migration_executed: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
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
            "SAEE_TENANT_STORAGE_APPROVAL_INPUT_VALIDATOR: PASS "
            f"status={validation['validation_status']} "
            f"builder_ready={str(validation['builder_ready']).lower()} "
            "blockers_closed_by_validator=0 production_ready=false"
        )


if __name__ == "__main__":
    main()
