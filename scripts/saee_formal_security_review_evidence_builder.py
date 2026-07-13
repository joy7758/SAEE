#!/usr/bin/env python3
"""Build formal-security-review evidence from a human-filled review input.

This builder converts a local, human-filled formal security review input into
the production privacy/security/legal evidence shape consumed by commercial
readiness checks. It does not perform a security review, contact reviewers or
vendors, run penetration tests, inspect private core, close blockers, modify
product behavior, or claim production readiness.
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
from saee_backend.services.production_privacy_security_legal_evidence import (
    DPA_KEYS,
    FORBIDDEN_TRUE_KEYS,
    FORMAL_SECURITY_REVIEW_KEYS,
    PRIVACY_LEGAL_REVIEW_KEYS,
    VULNERABILITY_MANAGEMENT_KEYS,
    evaluate_production_privacy_security_legal_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
DEFAULT_INPUT_PATH = OUTPUT_DIR / "formal_security_review_evidence_input.template.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "formal_security_review_evidence_builder_output.local.json"
DEFAULT_PRIVACY_SECURITY_LEGAL_OUTPUT_PATH = (
    OUTPUT_DIR
    / "production_privacy_security_legal_evidence.from_formal_security_review.local.json"
)
REPORT_PATH = OUTPUT_DIR / "formal_security_review_evidence_builder_report.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)

INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(FORBIDDEN_TRUE_KEYS)
        | {
            "codex_performed_security_review",
            "codex_contacted_security_reviewer",
            "codex_contacted_vendor",
            "codex_ran_penetration_test",
            "codex_inspected_private_core",
            "codex_inferred_missing_evidence",
            "security_review_claim_published",
            "security_review_execution_authorized",
            "blockers_closed_by_builder",
            "formal_security_review_completed_by_codex",
            "production_security_claim_published",
        }
    )
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER: FAIL: " + message
        )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_formal_security_review_evidence_input",
        "template_version": "v0.1",
        "input_status": "template_pending_human_input",
        "human_reviewer_name": "",
        "review_date": "",
        "security_review_owner": "",
        "report_reference": "",
        "decision_summary": "",
        "evidence_review": {key: False for key in FORMAL_SECURITY_REVIEW_KEYS},
        "source_notes_by_key": {key: "" for key in FORMAL_SECURITY_REVIEW_KEYS},
        "review_artifacts": [
            {
                "evidence_key": key,
                "artifact_reference": "",
                "reviewed_by_human": False,
                "owner_named": False,
                "human_source_note": "",
            }
            for key in FORMAL_SECURITY_REVIEW_KEYS
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
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "codex_inferred_missing_evidence": False,
        "security_review_claim_published": False,
        "security_review_execution_authorized": False,
        "blockers_closed_by_builder": False,
        "formal_security_review_completed_by_codex": False,
        "production_security_claim_published": False,
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
            f"SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in FORMAL_SECURITY_REVIEW_KEYS}


def source_notes(data: dict[str, Any]) -> dict[str, str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return {}
    return {key: str(notes.get(key, "")).strip() for key in FORMAL_SECURITY_REVIEW_KEYS}


def completed_artifacts(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = data.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        return {}
    completed: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        key = str(artifact.get("evidence_key", "")).strip()
        if key not in FORMAL_SECURITY_REVIEW_KEYS:
            continue
        if (
            str(artifact.get("artifact_reference", "")).strip()
            and artifact.get("reviewed_by_human") is True
            and artifact.get("owner_named") is True
            and str(artifact.get("human_source_note", "")).strip()
        ):
            completed[key] = artifact
    return completed


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
        "security_review_owner",
        "report_reference",
        "decision_summary",
    )
    return all(str(data.get(field, "")).strip() for field in fields)


def complete_input(data: dict[str, Any]) -> bool:
    flags = evidence_review_flags(data)
    notes = source_notes(data)
    artifacts = completed_artifacts(data)
    return (
        data.get("template_type") == "saee_formal_security_review_evidence_input"
        and input_metadata_complete(data)
        and all(flags.values())
        and all(bool(notes.get(key)) for key in FORMAL_SECURITY_REVIEW_KEYS)
        and all(key in artifacts for key in FORMAL_SECURITY_REVIEW_KEYS)
        and not boundary_violations(data)
    )


def build_privacy_security_legal_evidence(
    data: dict[str, Any],
    input_path: Path,
    *,
    complete: bool,
) -> dict[str, Any]:
    flags = evidence_review_flags(data)
    artifacts = completed_artifacts(data)
    evidence: dict[str, Any] = {
        "privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence",
        "evidence_scope": "human_filled_formal_security_review_to_production_privacy_security_legal_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_formal_security_review_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "security_review_owner_recorded": bool(str(data.get("security_review_owner", "")).strip()),
        "report_reference_recorded": bool(str(data.get("report_reference", "")).strip()),
        "completed_review_artifact_count": len(artifacts),
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in FORMAL_SECURITY_REVIEW_KEYS:
        evidence[key] = flags[key] and complete
    for key in PRIVACY_LEGAL_REVIEW_KEYS + DPA_KEYS + VULNERABILITY_MANAGEMENT_KEYS:
        evidence[key] = False
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["formal_security_review_completed_by_codex"] = False
    evidence["security_review_claim_published"] = False
    evidence["production_security_claim_published"] = False
    return evidence


def readiness(path: Path) -> dict[str, object]:
    return evaluate_production_privacy_security_legal_evidence(
        load_settings({"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(path)})
    )


def build_from_input(
    input_path: Path,
    output_path: Path,
    privacy_security_legal_output_path: Path,
    *,
    write_documentation: bool = True,
) -> dict[str, Any]:
    data = read_json(input_path)
    complete = complete_input(data)
    violations = boundary_violations(data)
    flags = evidence_review_flags(data)
    missing = [key for key in FORMAL_SECURITY_REVIEW_KEYS if not flags[key]]
    missing_artifacts = [
        key for key in FORMAL_SECURITY_REVIEW_KEYS if key not in completed_artifacts(data)
    ]
    status = "stop" if violations else ("pass" if complete else "hold")

    evidence = build_privacy_security_legal_evidence(data, input_path, complete=complete)
    write_json(privacy_security_legal_output_path, evidence)

    readiness_result = readiness(privacy_security_legal_output_path)
    summary: dict[str, Any] = {
        "formal_security_review_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_formal_security_review_to_production_privacy_security_legal_evidence",
        "generated_by": "scripts/saee_formal_security_review_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "privacy_security_legal_evidence_output": str(privacy_security_legal_output_path),
        "status": status,
        "input_complete": complete,
        "metadata_complete": input_metadata_complete(data),
        "completed_review_artifact_count": len(completed_artifacts(data)),
        "required_evidence_item_count": len(FORMAL_SECURITY_REVIEW_KEYS),
        "provided_evidence_item_count": sum(1 for value in flags.values() if value),
        "missing_required_evidence_count": len(missing),
        "missing_required_evidence": missing,
        "missing_review_artifact_count": len(missing_artifacts),
        "missing_review_artifacts": missing_artifacts,
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "privacy_security_legal_readiness_status": readiness_result["status"],
        "formal_security_review_completed_for_review": readiness_result[
            "formal_security_review_completed"
        ],
        "production_privacy_security_legal_ready": readiness_result[
            "production_privacy_security_legal_ready"
        ],
        "target_blocker_ids": ["formal_security_review"],
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
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "codex_inferred_missing_evidence": False,
        "security_review_claim_published": False,
        "security_review_execution_authorized": False,
        "formal_security_review_completed_by_codex": False,
        "production_security_claim_published": False,
        "next_action": (
            "A human security owner may fill the formal security review input "
            "with source-backed report references and findings triage evidence. "
            "The generated evidence remains one input to a later go/no-go profile."
        ),
    }
    write_json(output_path, summary)
    if write_documentation:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Formal Security Review Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- builder_scope: human_filled_formal_security_review_to_production_privacy_security_legal_evidence
- required_evidence_item_count: {summary['required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- privacy_security_legal_readiness_status: {summary['privacy_security_legal_readiness_status']}
- formal_security_review_completed_for_review: {str(summary['formal_security_review_completed_for_review']).lower()}
- production_privacy_security_legal_ready: false
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete way to convert a completed
formal security review report and triage record into the existing production
privacy/security/legal evidence shape. It only targets the
`formal_security_review` evidence group.

## What It Does Not Do

It does not perform a security review, contact reviewers or vendors, run
penetration tests, inspect private core, publish a security claim, close
blockers, or mark SAEE as production ready.

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
- security_vendor_contacted: false
- codex_performed_security_review: false
- codex_ran_penetration_test: false

## Next Action

Human security owners must fill
`formal_security_review_evidence_input.template.json` with real source notes
and report references. The generated evidence is only one input to later
go/no-go review and does not close the `formal_security_review` blocker by
itself.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Formal Security Review Evidence Builder v0.1

Status: local builder available; default output is hold.

formal_security_review_evidence_builder_v0_1: true
builder_scope: human_filled_formal_security_review_to_production_privacy_security_legal_evidence
required_evidence_item_count: {summary['required_evidence_item_count']}
default_output_status: {summary['status']}
formal_security_review_completed_for_review: {str(summary['formal_security_review_completed_for_review']).lower()}
production_privacy_security_legal_ready: false
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0

## Purpose

This builder converts a human-filled formal security review input into local
production privacy/security/legal evidence fields for the
`formal_security_review` group. It is a commercial-readiness evidence intake
surface, not security review execution.

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
security_vendor_contacted: false
legal_counsel_contacted: false
codex_performed_security_review: false
codex_contacted_security_reviewer: false
codex_contacted_vendor: false
codex_ran_penetration_test: false
codex_inspected_private_core: false
security_review_claim_published: false
production_security_claim_published: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json`
- builder output: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_output.local.json`
- privacy/security/legal evidence output: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/production_privacy_security_legal_evidence.from_formal_security_review.local.json`
- report: `phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_report.md`
- script: `scripts/saee_formal_security_review_evidence_builder.py`
- smoke: `scripts/saee_formal_security_review_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Formal Security Review Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_security_review_claim: false
recommend_for_production_security_claim: false
recommend_for_external_execution: false

## Reason

The builder is useful because it converts human-filled formal security review
evidence into a machine-checkable production privacy/security/legal evidence
shape. It is not sufficient for blocker closure by itself: default input is
incomplete, and even complete formal-security evidence leaves privacy/legal,
DPA, and vulnerability-management evidence unresolved.

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
security_vendor_contacted: false
legal_counsel_contacted: false
codex_performed_security_review: false
codex_contacted_security_reviewer: false
codex_contacted_vendor: false
codex_ran_penetration_test: false
codex_inspected_private_core: false
security_review_claim_published: false
production_security_claim_published: false
blockers_closed_by_builder: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument(
        "--privacy-security-legal-output",
        default=str(DEFAULT_PRIVACY_SECURITY_LEGAL_OUTPUT_PATH),
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_from_input(
        Path(args.input),
        Path(args.output),
        Path(args.privacy_security_legal_output),
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER: PASS "
            f"status={summary['status']} "
            f"input_complete={str(summary['input_complete']).lower()} "
            "blockers_closed_by_builder=0 production_ready=false"
        )


if __name__ == "__main__":
    main()
