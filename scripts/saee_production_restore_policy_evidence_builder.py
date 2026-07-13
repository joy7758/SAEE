#!/usr/bin/env python3
"""Build production-restore-policy evidence from human-filled approval input.

This builder converts local, human-filled restore-policy approval evidence into
the production data-operations evidence shape consumed by commercial readiness
checks. It does not approve policy, run restore, touch live data paths, contact
customers, infer missing evidence, close blockers by itself, modify product
behavior, or claim production readiness.
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
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
    evaluate_production_data_operations_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
DEFAULT_INPUT_PATH = OUTPUT_DIR / "production_restore_policy_approval_input.template.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "production_restore_policy_evidence_builder_output.local.json"
DEFAULT_DATA_OPS_OUTPUT_PATH = (
    OUTPUT_DIR / "production_data_operations_evidence.from_restore_policy.local.json"
)
REPORT_PATH = OUTPUT_DIR / "production_restore_policy_evidence_builder_report.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)

INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(FORBIDDEN_TRUE_KEYS)
        | {
            "external_model_api_called",
            "external_ai_assistant_tested",
            "policy_approved_by_codex",
            "restore_policy_published_by_codex",
            "live_restore_authorized_by_codex",
            "customer_notification_sent_by_codex",
            "codex_contacted_customer",
            "codex_contacted_vendor",
            "codex_inferred_missing_evidence",
            "execution_authorized",
            "blockers_closed_by_builder",
            "production_restore_policy_claim_published",
            "production_restore_policy_effective_for_customers",
        }
    )
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER: FAIL: " + message
        )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_production_restore_policy_approval_input",
        "template_version": "v0.1",
        "input_status": "template_pending_human_input",
        "human_reviewer_name": "",
        "review_date": "",
        "data_operations_owner": "",
        "security_owner": "",
        "privacy_legal_owner": "",
        "incident_response_owner": "",
        "decision_summary": "",
        "policy_evidence_review": {key: False for key in RESTORE_POLICY_KEYS},
        "source_notes_by_key": {key: "" for key in RESTORE_POLICY_KEYS},
        "policy_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": "",
                "owner_named": False,
                "reviewed_by_human": False,
                "human_source_note": "",
            }
            for key in RESTORE_POLICY_KEYS
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
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "policy_approved_by_codex": False,
        "restore_policy_published_by_codex": False,
        "live_restore_authorized_by_codex": False,
        "customer_notification_sent_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_restore_policy_claim_published": False,
        "production_restore_policy_effective_for_customers": False,
    }


def ensure_default_template(path: Path) -> None:
    if not path.exists():
        write_json(path, default_input_template())
        return
    if path.resolve() != DEFAULT_INPUT_PATH.resolve():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        write_json(path, default_input_template())
        return
    if not isinstance(data, dict) or data.get("input_status") != "template_pending_human_input":
        write_json(path, default_input_template())


def read_json(path: Path) -> dict[str, Any]:
    ensure_default_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def policy_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("policy_evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in RESTORE_POLICY_KEYS}


def source_notes(data: dict[str, Any]) -> dict[str, str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return {}
    return {key: str(notes.get(key, "")).strip() for key in RESTORE_POLICY_KEYS}


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
        "data_operations_owner",
        "security_owner",
        "privacy_legal_owner",
        "incident_response_owner",
        "decision_summary",
    )
    return all(str(data.get(field, "")).strip() for field in fields)


def completed_policy_slots(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots = data.get("policy_evidence_slots", [])
    if not isinstance(slots, list):
        return {}
    complete_slots: dict[str, dict[str, Any]] = {}
    for slot in slots:
        if not isinstance(slot, dict):
            continue
        key = str(slot.get("evidence_key", "")).strip()
        if key not in RESTORE_POLICY_KEYS:
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
    flags = policy_review_flags(data)
    notes = source_notes(data)
    complete_slots = completed_policy_slots(data)
    return (
        data.get("template_type") == "saee_production_restore_policy_approval_input"
        and input_metadata_complete(data)
        and all(flags.values())
        and all(bool(notes.get(key)) for key in RESTORE_POLICY_KEYS)
        and all(key in complete_slots for key in RESTORE_POLICY_KEYS)
        and not boundary_violations(data)
    )


def build_data_operations_evidence(
    data: dict[str, Any],
    input_path: Path,
    *,
    complete: bool,
    violations: list[str],
) -> dict[str, Any]:
    flags = policy_review_flags(data)
    complete_slots = completed_policy_slots(data)
    evidence: dict[str, Any] = {
        "data_operations_evidence_type": "production_data_operations_evidence",
        "evidence_scope": (
            "human_filled_production_restore_policy_to_production_data_operations_evidence"
        ),
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_production_restore_policy_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "source_boundary_violation_count": len(violations),
        "source_boundary_violations": violations,
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "data_operations_owner_recorded": bool(str(data.get("data_operations_owner", "")).strip()),
        "security_owner_recorded": bool(str(data.get("security_owner", "")).strip()),
        "privacy_legal_owner_recorded": bool(str(data.get("privacy_legal_owner", "")).strip()),
        "incident_response_owner_recorded": bool(str(data.get("incident_response_owner", "")).strip()),
        "completed_policy_slot_count": len(complete_slots),
        "policy_approved_by_codex": False,
        "restore_policy_published_by_codex": False,
        "live_restore_authorized_by_codex": False,
        "customer_notification_sent_by_codex": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in RESTORE_TEST_KEYS:
        evidence[key] = False
    for key in RESTORE_POLICY_KEYS:
        evidence[key] = flags[key] and complete
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["external_model_api_called"] = False
    evidence["external_ai_assistant_tested"] = False
    evidence["production_restore_policy_claim_published"] = False
    evidence["production_restore_policy_effective_for_customers"] = False
    return evidence


def data_ops_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def commercial_status_with_evidence(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def build_from_input(
    input_path: Path,
    output_path: Path,
    data_ops_output_path: Path,
    *,
    write_documentation: bool = True,
) -> dict[str, Any]:
    data = read_json(input_path)
    complete = complete_input(data)
    violations = boundary_violations(data)
    flags = policy_review_flags(data)
    missing = [key for key in RESTORE_POLICY_KEYS if not flags[key]]
    missing_slots = [
        key for key in RESTORE_POLICY_KEYS if key not in completed_policy_slots(data)
    ]
    status = "stop" if violations else ("pass" if complete else "hold")

    data_ops_evidence = build_data_operations_evidence(
        data,
        input_path,
        complete=complete,
        violations=violations,
    )
    write_json(data_ops_output_path, data_ops_evidence)

    readiness = data_ops_readiness(data_ops_output_path)
    go_no_go = commercial_status_with_evidence(data_ops_output_path)
    unsatisfied_ids = [
        str(item.get("blocker_id"))
        for item in go_no_go.get("unsatisfied_blockers", [])
        if isinstance(item, dict)
    ]
    summary: dict[str, Any] = {
        "production_restore_policy_evidence_builder_v0_1": True,
        "builder_scope": (
            "human_filled_production_restore_policy_to_production_data_operations_evidence"
        ),
        "generated_by": "scripts/saee_production_restore_policy_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "data_operations_evidence_output": str(data_ops_output_path),
        "status": status,
        "input_complete": complete,
        "metadata_complete": input_metadata_complete(data),
        "completed_policy_slot_count": len(completed_policy_slots(data)),
        "required_evidence_item_count": len(RESTORE_POLICY_KEYS),
        "provided_evidence_item_count": sum(1 for value in flags.values() if value),
        "missing_required_evidence_count": len(missing),
        "missing_required_evidence": missing,
        "missing_policy_slot_count": len(missing_slots),
        "missing_policy_slots": missing_slots,
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "data_operations_readiness_status": readiness["status"],
        "production_restore_policy_available_for_review": readiness[
            "production_restore_policy_available"
        ],
        "production_restore_policy_available": readiness["production_restore_policy_available"],
        "restore_tested": readiness["restore_tested"],
        "production_data_operations_ready": readiness["production_data_operations_ready"],
        "commercial_status_with_policy_evidence": go_no_go["commercial_status"],
        "production_launch_status_with_policy_evidence": go_no_go[
            "production_launch_status"
        ],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "target_blocker_ids": ["production_restore_policy"],
        "target_blocker_satisfied_by_policy_evidence": (
            "production_restore_policy" not in unsatisfied_ids
        ),
        "restore_tested_satisfied_by_policy_evidence": "restore_tested"
        not in unsatisfied_ids,
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
        "production_data_path_modified": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "policy_approved_by_codex": False,
        "restore_policy_published_by_codex": False,
        "live_restore_authorized_by_codex": False,
        "customer_notification_sent_by_codex": False,
        "production_restore_policy_claim_published": False,
        "production_restore_policy_effective_for_customers": False,
        "next_action": (
            "Human owners must fill and approve the restore-policy input before "
            "this builder can produce policy evidence. Restore-tested evidence "
            "remains a separate input unless combined in an explicit go/no-go profile."
        ),
    }
    write_json(output_path, summary)
    if write_documentation:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Production Restore Policy Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- builder_scope: human_filled_production_restore_policy_to_production_data_operations_evidence
- required_evidence_item_count: {summary['required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- data_operations_readiness_status: {summary['data_operations_readiness_status']}
- production_restore_policy_available_for_review: {str(summary['production_restore_policy_available_for_review']).lower()}
- restore_tested: {str(summary['restore_tested']).lower()}
- production_data_operations_ready: {str(summary['production_data_operations_ready']).lower()}
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete way to convert a filled
production restore policy approval input into the existing production
data-operations evidence shape. It only targets the `production_restore_policy`
evidence group.

## What It Does Not Do

It does not approve a production restore policy, run restore, enable live
restore, modify production data paths, restore credentials, restore private
core, contact customers, publish customer-facing policy claims, close blockers,
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
- live_restore_performed: false
- production_data_path_modified: false

## Next Action

Human owners must fill `production_restore_policy_approval_input.template.json`
with real approval evidence. The generated data-operations evidence is only one
input to later go/no-go review and does not close the production restore policy
blocker by itself.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Production Restore Policy Evidence Builder v0.1

Status: local builder available; default output is hold.

production_restore_policy_evidence_builder_v0_1: true
builder_scope: human_filled_production_restore_policy_to_production_data_operations_evidence
required_evidence_item_count: {summary['required_evidence_item_count']}
default_output_status: {summary['status']}
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0
production_restore_policy_available: false
production_data_operations_ready: false

## Purpose

This builder converts a human-filled production restore policy approval input
into local production data-operations evidence fields for the
`production_restore_policy` group. It is a commercial-readiness evidence intake
surface, not policy approval and not restore execution.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_live_restore: false

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves rollback governance by making production restore policy evidence
   machine-checkable after human approval.
3. It preserves safety, license, supply-chain, permission, customer-data, and
   private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   readiness evidence intake layer around rollback safety.

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
live_restore_performed: false
production_data_path_modified: false
restore_to_live_path_enabled: false
credentials_restored: false
private_core_restored: false
policy_approved_by_codex: false
restore_policy_published_by_codex: false
production_restore_policy_claim_published: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json`
- builder output: `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_output.local.json`
- data-operations evidence output: `phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_policy.local.json`
- report: `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_report.md`
- script: `scripts/saee_production_restore_policy_evidence_builder.py`
- smoke: `scripts/saee_production_restore_policy_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Production Restore Policy Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_live_restore: false
recommend_for_external_execution: false

## Reason

The builder is useful because it converts human-approved production restore
policy evidence into a machine-checkable data-operations evidence shape. It is
not sufficient for blocker closure by itself: default input is incomplete, and
restore-tested evidence remains a separate input unless explicitly combined in
a go/no-go profile.

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
live_restore_performed: false
production_data_path_modified: false
restore_to_live_path_enabled: false
credentials_restored: false
private_core_restored: false
policy_approved_by_codex: false
restore_policy_published_by_codex: false
production_restore_policy_claim_published: false
blockers_closed_by_builder: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--data-ops-output", default=str(DEFAULT_DATA_OPS_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_from_input(
        Path(args.input),
        Path(args.output),
        Path(args.data_ops_output),
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PRODUCTION_RESTORE_POLICY_EVIDENCE_BUILDER: PASS "
            f"path={args.output} status={summary['status']} "
            f"production_restore_policy_available_for_review="
            f"{str(summary['production_restore_policy_available_for_review']).lower()} "
            "production_data_operations_ready=false blockers_closed_by_builder=0"
        )


if __name__ == "__main__":
    main()
