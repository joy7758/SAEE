#!/usr/bin/env python3
"""Validate human-filled production restore policy approval input.

This validator checks whether the local restore-policy approval input is
complete and boundary-safe before a human runs the existing evidence builder.
It does not approve policy, collect evidence, run restore, close blockers,
touch live data paths, contact customers/vendors, or claim production readiness.
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

from scripts.saee_production_restore_policy_evidence_builder import (
    DEFAULT_INPUT_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    boundary_violations,
    completed_policy_slots,
    ensure_default_template,
    input_metadata_complete,
    policy_review_flags,
    source_notes,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "production_restore_policy_approval_input_validation.local.json"
DEFAULT_HUMAN_FILLED_INPUT_PATH = (
    OUTPUT_DIR / "production_restore_policy_approval_input.human_filled.local.json"
)
REPORT_PATH = OUTPUT_DIR / "production_restore_policy_approval_input_validation.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "data_operations_owner",
    "security_owner",
    "privacy_legal_owner",
    "incident_response_owner",
    "decision_summary",
]


def read_json(path: Path) -> dict[str, Any]:
    ensure_default_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_VALIDATOR: FAIL "
            f"invalid input {path}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_VALIDATOR: FAIL input must be object"
        )
    return data


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def missing_metadata_fields(data: dict[str, Any]) -> list[str]:
    return [field for field in METADATA_FIELDS if not str(data.get(field, "")).strip()]


def missing_policy_review_keys(data: dict[str, Any]) -> list[str]:
    flags = policy_review_flags(data)
    return [key for key in RESTORE_POLICY_KEYS if flags.get(key) is not True]


def missing_source_note_keys(data: dict[str, Any]) -> list[str]:
    notes = source_notes(data)
    return [key for key in RESTORE_POLICY_KEYS if not notes.get(key)]


def missing_policy_slot_keys(data: dict[str, Any]) -> list[str]:
    slots = completed_policy_slots(data)
    return [key for key in RESTORE_POLICY_KEYS if key not in slots]


def validation_status(*, violations: list[str], input_complete: bool) -> str:
    if violations:
        return "stop"
    if input_complete:
        return "pass"
    return "hold"


def build_validation(input_path: Path) -> dict[str, Any]:
    data = read_json(input_path)
    violations = boundary_violations(data)
    missing_metadata = missing_metadata_fields(data)
    missing_review = missing_policy_review_keys(data)
    missing_notes = missing_source_note_keys(data)
    missing_slots = missing_policy_slot_keys(data)
    metadata_complete = input_metadata_complete(data)
    policy_review_complete = not missing_review
    source_notes_complete = not missing_notes
    policy_slots_complete = not missing_slots
    input_complete = (
        data.get("template_type") == "saee_production_restore_policy_approval_input"
        and metadata_complete
        and policy_review_complete
        and source_notes_complete
        and policy_slots_complete
        and not violations
    )
    status = validation_status(violations=violations, input_complete=input_complete)
    return {
        "validator_type": "saee_production_restore_policy_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_restore_policy_input_pre_builder_check",
        "target_blocker_id": "production_restore_policy",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_production_restore_policy_approval_input_validator.py",
        "input_path": rel(input_path),
        "validation_status": status,
        "input_complete": input_complete,
        "builder_ready": status == "pass",
        "metadata_complete": metadata_complete,
        "policy_evidence_review_complete": policy_review_complete,
        "source_notes_complete": source_notes_complete,
        "policy_slots_complete": policy_slots_complete,
        "missing_metadata_fields": missing_metadata,
        "missing_policy_evidence_review": missing_review,
        "missing_source_notes": missing_notes,
        "missing_policy_slots": missing_slots,
        "required_policy_evidence_item_count": len(RESTORE_POLICY_KEYS),
        "completed_policy_slot_count": len(completed_policy_slots(data)),
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "boundary_review_key_count": len(INPUT_FORBIDDEN_TRUE_KEYS),
        "next_action": (
            "If validation_status is pass, a human may run the restore policy evidence "
            "builder in a separate approved evidence request; otherwise complete the "
            "missing input fields or resolve boundary violations first."
        ),
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_validator": 0,
        "policy_approved_by_validator": False,
        "restore_policy_published_by_validator": False,
        "live_restore_authorized_by_validator": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_report(validation: dict[str, Any]) -> str:
    missing_metadata = "\n".join(f"- {item}" for item in validation["missing_metadata_fields"]) or "- none"
    missing_review = (
        "\n".join(f"- {item}" for item in validation["missing_policy_evidence_review"])
        or "- none"
    )
    missing_notes = "\n".join(f"- {item}" for item in validation["missing_source_notes"]) or "- none"
    missing_slots = "\n".join(f"- {item}" for item in validation["missing_policy_slots"]) or "- none"
    violations = "\n".join(f"- {item}" for item in validation["boundary_violations"]) or "- none"
    return f"""# SAEE Production Restore Policy Approval Input Validation

Status: {validation['validation_status']}.

This report validates the human-filled restore-policy approval input before it
is passed into the existing production restore policy evidence builder. It does
not approve policy, run restore, collect evidence, close blockers, touch live
data paths, contact customers/vendors, or claim production readiness.

## Summary

- validator_type: {validation['validator_type']}
- validation_scope: {validation['validation_scope']}
- target_blocker_id: {validation['target_blocker_id']}
- input_complete: {str(validation['input_complete']).lower()}
- builder_ready: {str(validation['builder_ready']).lower()}
- blockers_closed_by_validator: {validation['blockers_closed_by_validator']}
- policy_approved_by_validator: false
- restore_policy_published_by_validator: false
- live_restore_authorized_by_validator: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Missing Metadata Fields

{missing_metadata}

## Missing Policy Review Keys

{missing_review}

## Missing Source Notes

{missing_notes}

## Missing Policy Slots

{missing_slots}

## Boundary Violations

{violations}

## Next Action

{validation['next_action']}
"""


def write_documentation(validation: dict[str, Any]) -> None:
    REPORT_PATH.write_text(render_report(validation), encoding="utf-8")
    DOC_PATH.write_text(
        "\n".join(
            [
                "# SAEE Production Restore Policy Approval Input Validator v0.1",
                "",
                "production_restore_policy_approval_input_validator_v0_1: true",
                "validator_scope: local_human_filled_restore_policy_input_pre_builder_check",
                f"default_validation_status: {validation['validation_status']}",
                f"default_input_complete: {str(validation['input_complete']).lower()}",
                f"default_builder_ready: {str(validation['builder_ready']).lower()}",
                "target_blocker_id: production_restore_policy",
                "blockers_closed_by_validator: 0",
                "policy_approved_by_validator: false",
                "restore_policy_published_by_validator: false",
                "live_restore_authorized_by_validator: false",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "",
                "## Purpose",
                "",
                "This validator checks whether the human-filled restore-policy approval",
                "input is complete and boundary-safe before it is passed to the existing",
                "production restore policy evidence builder.",
                "",
                "## Boundary",
                "",
                "The validator is pre-builder input validation only. It does not approve",
                "policy, run restore, collect evidence, close blockers, touch live data",
                "paths, contact customers or vendors, modify runtime/backend/kernel/API",
                "schema/private core, launch product, or claim production readiness.",
                "",
                "## Entrypoints",
                "",
                "- input template: `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json`",
                "- validation output: `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_validation.local.json`",
                "- validation report: `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_validation.md`",
                "- script: `scripts/saee_production_restore_policy_approval_input_validator.py`",
                "- smoke: `scripts/saee_production_restore_policy_approval_input_validator_smoke.py`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        "\n".join(
            [
                "# SAEE Production Restore Policy Approval Input Validator Recommendation Gate",
                "",
                "answer: conditional",
                "",
                "recommend_for_human_input_validation: true",
                "recommend_for_policy_approval: false",
                "recommend_for_evidence_collection_authorization: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_live_restore: false",
                "recommend_for_production_launch: false",
                "recommend_for_production_readiness_claim: false",
                "",
                "## Reason",
                "",
                "The validator is useful because it catches missing human input and",
                "boundary violations before the restore-policy evidence builder is run.",
                "It is not policy approval and does not close the production restore",
                "policy blocker by itself.",
                "",
                "## Boundary",
                "",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "runtime_modified: false",
                "backend_modified: false",
                "kernel_modified: false",
                "api_schema_modified: false",
                "external_calls_made: false",
                "customer_contacted: false",
                "live_restore_performed: false",
                "production_data_path_modified: false",
                "restore_to_live_path_enabled: false",
                "blockers_closed_by_validator: 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=(
            DEFAULT_HUMAN_FILLED_INPUT_PATH
            if DEFAULT_HUMAN_FILLED_INPUT_PATH.exists()
            else DEFAULT_INPUT_PATH
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Do not write Markdown documentation outputs",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation = build_validation(args.input)
    write_json(args.output, validation)
    if not args.no_docs:
        write_documentation(validation)
    if args.json:
        print(json.dumps(validation, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_VALIDATOR: PASS "
            f"status={validation['validation_status']} "
            f"builder_ready={str(validation['builder_ready']).lower()} "
            f"blockers_closed_by_validator={validation['blockers_closed_by_validator']} "
            f"production_ready={str(validation['production_ready']).lower()}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
