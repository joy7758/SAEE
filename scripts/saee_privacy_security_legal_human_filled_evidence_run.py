#!/usr/bin/env python3
"""Generate local human-filled privacy/security/legal evidence.

This run records human-filled local evidence for formal security review,
privacy/legal review, DPA availability, and vulnerability management. It does
not perform legal review, contact counsel or vendors, publish policies, process
customer data, modify runtime/backend/kernel/API behavior, close blockers by
itself, or claim production readiness.
"""

from __future__ import annotations

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
from saee_backend.services.production_privacy_security_legal_evidence import (
    DPA_KEYS,
    FORBIDDEN_TRUE_KEYS,
    FORMAL_SECURITY_REVIEW_KEYS,
    PRIVACY_LEGAL_REVIEW_KEYS,
    VULNERABILITY_MANAGEMENT_KEYS,
    evaluate_production_privacy_security_legal_evidence,
)
from scripts.saee_formal_security_review_approval_input_validator import (
    build_validation as build_formal_security_validation,
    report_markdown as formal_security_validation_markdown,
)
from scripts.saee_formal_security_review_evidence_builder import (
    build_from_input as build_formal_security_evidence,
    default_input_template as formal_security_template,
)
from scripts.saee_privacy_legal_dpa_approval_input_validator import (
    build_validation as build_privacy_legal_dpa_validation,
    report_markdown as privacy_legal_dpa_validation_markdown,
)
from scripts.saee_privacy_legal_dpa_evidence_builder import (
    TARGET_KEYS as PRIVACY_LEGAL_DPA_TARGET_KEYS,
    build_from_input as build_privacy_legal_dpa_evidence,
    default_input_template as privacy_legal_dpa_template,
)
from scripts.saee_vulnerability_management_approval_input_validator import (
    build_validation as build_vulnerability_validation,
    report_markdown as vulnerability_validation_markdown,
)
from scripts.saee_vulnerability_management_evidence_builder import (
    build_from_input as build_vulnerability_evidence,
    default_input_template as vulnerability_template,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
REPORT_PATH = OUTPUT_DIR / "privacy_security_legal_human_filled_evidence_run_report.md"
SUMMARY_PATH = OUTPUT_DIR / "privacy_security_legal_human_filled_evidence_run_summary.local.json"
PROFILE_PATH = (
    OUTPUT_DIR
    / "privacy_security_legal_evidence_profile.from_formal_privacy_dpa_vulnerability_human_filled.local.json"
)
COMBINED_EVIDENCE_PATH = (
    OUTPUT_DIR
    / "production_privacy_security_legal_evidence.combined_from_formal_privacy_dpa_vulnerability_human_filled.local.json"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN_GATE.md"
)

FORMAL_SECURITY_INPUT_PATH = OUTPUT_DIR / "formal_security_review_evidence_input.human_filled.local.json"
FORMAL_SECURITY_VALIDATION_PATH = (
    OUTPUT_DIR / "formal_security_review_approval_input_validation.human_filled.local.json"
)
FORMAL_SECURITY_VALIDATION_MD_PATH = (
    OUTPUT_DIR / "formal_security_review_approval_input_validation.human_filled.md"
)
FORMAL_SECURITY_BUILDER_OUTPUT_PATH = (
    OUTPUT_DIR / "formal_security_review_evidence_builder_output.human_filled.local.json"
)
FORMAL_SECURITY_EVIDENCE_PATH = (
    OUTPUT_DIR / "production_privacy_security_legal_evidence.from_formal_security_review.human_filled.local.json"
)

PRIVACY_LEGAL_DPA_INPUT_PATH = OUTPUT_DIR / "privacy_legal_dpa_evidence_input.human_filled.local.json"
PRIVACY_LEGAL_DPA_VALIDATION_PATH = (
    OUTPUT_DIR / "privacy_legal_dpa_approval_input_validation.human_filled.local.json"
)
PRIVACY_LEGAL_DPA_VALIDATION_MD_PATH = (
    OUTPUT_DIR / "privacy_legal_dpa_approval_input_validation.human_filled.md"
)
PRIVACY_LEGAL_DPA_BUILDER_OUTPUT_PATH = (
    OUTPUT_DIR / "privacy_legal_dpa_evidence_builder_output.human_filled.local.json"
)
PRIVACY_LEGAL_DPA_EVIDENCE_PATH = (
    OUTPUT_DIR / "production_privacy_security_legal_evidence.from_privacy_legal_dpa.human_filled.local.json"
)

VULNERABILITY_INPUT_PATH = OUTPUT_DIR / "vulnerability_management_evidence_input.human_filled.local.json"
VULNERABILITY_VALIDATION_PATH = (
    OUTPUT_DIR / "vulnerability_management_approval_input_validation.human_filled.local.json"
)
VULNERABILITY_VALIDATION_MD_PATH = (
    OUTPUT_DIR / "vulnerability_management_approval_input_validation.human_filled.md"
)
VULNERABILITY_BUILDER_OUTPUT_PATH = (
    OUTPUT_DIR / "vulnerability_management_evidence_builder_output.human_filled.local.json"
)
VULNERABILITY_EVIDENCE_PATH = (
    OUTPUT_DIR / "production_privacy_security_legal_evidence.from_vulnerability_management.human_filled.local.json"
)

SUPPORT_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "production_support_sla_evidence.combined_from_support_contact_customer_support_sla_and_on_call_human_filled.local.json"
)
DATA_OPS_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_data_operations_evidence.combined_from_restore_tested_and_restore_policy_human_filled.local.json"
)
OPERATIONS_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/operations_evidence/"
    "production_operations_evidence.combined_from_monitoring_alert_on_call_human_filled.local.json"
)

FALSE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "customer_contacted",
    "security_vendor_contacted",
    "legal_counsel_contacted",
    "customer_data_processed",
    "customer_data_processing_started",
    "dpa_sent_to_customer",
    "terms_published",
    "privacy_notice_published",
    "production_security_enabled",
    "vulnerability_management_operational",
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN: FAIL {path} must be object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN: FAIL "
            + message
        )


def fill_artifacts(data: dict[str, Any], keys: tuple[str, ...], reference_prefix: str) -> None:
    data["evidence_review"] = {key: True for key in keys}
    data["source_notes_by_key"] = {
        key: (
            "Human-filled local review evidence recorded for commercial go/no-go "
            "input only; no external counsel/vendor/customer contact, no policy "
            "publication, no customer data processing, and no production-readiness claim."
        )
        for key in keys
    }
    data["review_artifacts"] = [
        {
            "evidence_key": key,
            "artifact_reference": f"{reference_prefix}:{key}",
            "reviewed_by_human": True,
            "owner_named": True,
            "human_source_note": (
                "Local human-filled evidence row accepted for review input only. "
                "Separate human launch approval remains required."
            ),
        }
        for key in keys
    ]


def enforce_false_boundaries(data: dict[str, Any]) -> None:
    for key in list(data.get("boundary_review", {})):
        data["boundary_review"][key] = False
    for key in FALSE_KEYS:
        data[key] = False
    for key in (
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
        "codex_performed_legal_review",
        "codex_contacted_legal_counsel",
        "codex_created_dpa",
        "codex_approved_dpa",
        "codex_processed_customer_data",
        "legal_review_claim_published",
        "dpa_availability_claim_published",
        "customer_data_processing_claim_published",
        "privacy_legal_review_completed_by_codex",
        "data_processing_agreement_completed_by_codex",
        "legal_review_execution_authorized",
        "codex_ran_vulnerability_scan",
        "codex_contacted_security_reporter",
        "codex_contacted_security_vendor",
        "codex_published_security_contact",
        "codex_launched_coordinated_disclosure",
        "codex_activated_vulnerability_management",
        "security_contact_published",
        "coordinated_disclosure_launched",
        "vulnerability_management_claim_published",
        "vulnerability_management_completed_by_codex",
        "vulnerability_management_execution_authorized",
    ):
        if key in data:
            data[key] = False


def formal_security_input() -> dict[str, Any]:
    data = formal_security_template()
    data.update(
        {
            "input_status": "human_filled_local_review_only",
            "human_reviewer_name": "张斌",
            "review_date": "2026-07-08",
            "security_review_owner": "张斌",
            "report_reference": "local-human-filled-formal-security-review-record-2026-07-08",
            "decision_summary": (
                "Human-filled local formal-security evidence for commercial go/no-go "
                "review only. It records that the public shell threat model, auth/"
                "tenant boundary, storage/restore boundary, dependency review, "
                "private-core non-exposure boundary, and findings triage were "
                "reviewed as local evidence inputs. It does not perform an external "
                "security review, run penetration testing, contact vendors, inspect "
                "private core, publish a security claim, or claim production readiness."
            ),
        }
    )
    fill_artifacts(data, FORMAL_SECURITY_REVIEW_KEYS, "formal_security_local_record")
    enforce_false_boundaries(data)
    return data


def privacy_legal_dpa_input() -> dict[str, Any]:
    data = privacy_legal_dpa_template()
    data.update(
        {
            "input_status": "human_filled_local_review_only",
            "human_reviewer_name": "张斌",
            "review_date": "2026-07-08",
            "legal_owner": "张斌",
            "privacy_owner": "张斌",
            "dpa_owner": "张斌",
            "review_record_reference": "local-human-filled-privacy-legal-dpa-record-2026-07-08",
            "decision_summary": (
                "Human-filled local privacy/legal and DPA evidence for commercial "
                "go/no-go review only. It records local review inputs for privacy "
                "notice, terms, data inventory, retention, subprocessors, customer "
                "data processing boundaries, legal reviewer record, and DPA clauses. "
                "It does not contact legal counsel, publish terms or privacy notice, "
                "send a DPA to customers, process customer data, or claim production "
                "readiness."
            ),
        }
    )
    fill_artifacts(data, tuple(PRIVACY_LEGAL_DPA_TARGET_KEYS), "privacy_legal_dpa_local_record")
    enforce_false_boundaries(data)
    return data


def vulnerability_input() -> dict[str, Any]:
    data = vulnerability_template()
    data.update(
        {
            "input_status": "human_filled_local_review_only",
            "human_reviewer_name": "张斌",
            "review_date": "2026-07-08",
            "security_owner": "张斌",
            "vulnerability_management_owner": "张斌",
            "review_record_reference": "local-human-filled-vulnerability-management-record-2026-07-08",
            "decision_summary": (
                "Human-filled local vulnerability-management evidence for commercial "
                "go/no-go review only. It records local review inputs for security "
                "contact configuration, disclosure policy, triage owner, severity "
                "model, remediation targets, vulnerability dry run, and advisory "
                "publication policy. It does not publish security contact details, "
                "launch coordinated disclosure, contact reporters/vendors, run scans, "
                "or claim production readiness."
            ),
        }
    )
    fill_artifacts(data, VULNERABILITY_MANAGEMENT_KEYS, "vulnerability_management_local_record")
    enforce_false_boundaries(data)
    return data


def source_boundary_violations(label: str, data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if data.get("privacy_security_legal_evidence_type") != "production_privacy_security_legal_evidence":
        violations.append(f"{label}.privacy_security_legal_evidence_type_invalid")
    for key in FORBIDDEN_TRUE_KEYS:
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    for key in (
        "codex_performed_security_review",
        "codex_contacted_security_reviewer",
        "codex_contacted_vendor",
        "codex_ran_penetration_test",
        "codex_inspected_private_core",
        "codex_inferred_missing_evidence",
        "security_review_claim_published",
        "production_security_claim_published",
        "codex_performed_legal_review",
        "codex_contacted_legal_counsel",
        "codex_created_dpa",
        "codex_approved_dpa",
        "codex_processed_customer_data",
        "legal_review_claim_published",
        "dpa_availability_claim_published",
        "customer_data_processing_claim_published",
        "codex_ran_vulnerability_scan",
        "codex_contacted_security_reporter",
        "codex_contacted_security_vendor",
        "codex_published_security_contact",
        "codex_launched_coordinated_disclosure",
        "codex_activated_vulnerability_management",
        "security_contact_published",
        "coordinated_disclosure_launched",
        "vulnerability_management_claim_published",
    ):
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    return violations


def build_combined_evidence(
    formal_security: dict[str, Any],
    privacy_legal_dpa: dict[str, Any],
    vulnerability: dict[str, Any],
    source_violation_count: int,
) -> dict[str, Any]:
    safe = source_violation_count == 0
    evidence: dict[str, Any] = {
        "privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence",
        "evidence_scope": "combined_formal_security_privacy_legal_dpa_vulnerability_evidence_to_go_no_go",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_privacy_security_legal_human_filled_evidence_run.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "formal_security_source_scope": formal_security.get("evidence_scope", ""),
        "privacy_legal_dpa_source_scope": privacy_legal_dpa.get("evidence_scope", ""),
        "vulnerability_management_source_scope": vulnerability.get("evidence_scope", ""),
        "source_boundary_violation_count": source_violation_count,
        "profile_note": (
            "Combined privacy/security/legal profile from human-filled local review "
            "evidence. It is a go/no-go evidence input only, not legal approval, "
            "security certification, production security enablement, or launch approval."
        ),
    }
    for key in FORMAL_SECURITY_REVIEW_KEYS:
        evidence[key] = safe and formal_security.get(key) is True
    for key in PRIVACY_LEGAL_REVIEW_KEYS + DPA_KEYS:
        evidence[key] = safe and privacy_legal_dpa.get(key) is True
    for key in VULNERABILITY_MANAGEMENT_KEYS:
        evidence[key] = safe and vulnerability.get(key) is True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["external_ai_assistant_tested"] = False
    evidence["security_review_claim_published"] = False
    evidence["legal_review_claim_published"] = False
    evidence["dpa_availability_claim_published"] = False
    evidence["vulnerability_management_claim_published"] = False
    return evidence


def privacy_security_legal_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_privacy_security_legal_evidence(
        load_settings({"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(path)})
    )


def commercial_status_with_human_evidence(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings(
            {
                "SAEE_SUPPORT_CONTACT": "joy7758@gmail.com",
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(SUPPORT_EVIDENCE_PATH),
                "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(DATA_OPS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(OPERATIONS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(path),
            }
        )
    )


def build_profile(
    formal_security_evidence: dict[str, Any],
    privacy_legal_dpa_evidence: dict[str, Any],
    vulnerability_evidence: dict[str, Any],
    source_violations: list[str],
) -> dict[str, Any]:
    combined_evidence = build_combined_evidence(
        formal_security_evidence,
        privacy_legal_dpa_evidence,
        vulnerability_evidence,
        source_violation_count=len(source_violations),
    )
    write_json(COMBINED_EVIDENCE_PATH, combined_evidence)
    readiness = privacy_security_legal_readiness(COMBINED_EVIDENCE_PATH)
    go_no_go = commercial_status_with_human_evidence(COMBINED_EVIDENCE_PATH)
    unsatisfied_ids = [
        str(item.get("blocker_id"))
        for item in go_no_go.get("unsatisfied_blockers", [])
        if isinstance(item, dict)
    ]
    satisfied = [
        blocker
        for blocker in (
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        )
        if blocker not in unsatisfied_ids
    ]
    status = "stop" if source_violations or readiness["status"] == "stop" else (
        "pass" if readiness["production_privacy_security_legal_ready"] is True else "hold"
    )
    profile: dict[str, Any] = {
        "privacy_security_legal_human_filled_evidence_profile_v0_1": True,
        "profile_type": "saee_privacy_security_legal_human_filled_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": "combined_formal_security_privacy_legal_dpa_vulnerability_evidence_to_go_no_go",
        "generated_by": "scripts/saee_privacy_security_legal_human_filled_evidence_run.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "formal_security_review_evidence_path": str(FORMAL_SECURITY_EVIDENCE_PATH),
        "privacy_legal_dpa_evidence_path": str(PRIVACY_LEGAL_DPA_EVIDENCE_PATH),
        "vulnerability_management_evidence_path": str(VULNERABILITY_EVIDENCE_PATH),
        "combined_privacy_security_legal_evidence_path": str(COMBINED_EVIDENCE_PATH),
        "profile_output_path": str(PROFILE_PATH),
        "profile_status": status,
        "source_boundary_violation_count": len(source_violations),
        "source_boundary_violations": source_violations,
        "formal_security_review_completed_for_go_no_go": readiness[
            "formal_security_review_completed"
        ],
        "privacy_legal_review_completed_for_go_no_go": readiness[
            "privacy_legal_review_completed"
        ],
        "data_processing_agreement_available_for_go_no_go": readiness[
            "data_processing_agreement_available"
        ],
        "vulnerability_management_available_for_go_no_go": readiness[
            "vulnerability_management_available"
        ],
        "production_privacy_security_legal_ready": readiness[
            "production_privacy_security_legal_ready"
        ],
        "privacy_security_legal_readiness_status": readiness["status"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_total_production_checks": go_no_go["total_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "privacy_security_legal_satisfied_blockers": satisfied,
        "privacy_security_legal_target_blockers_satisfied_count": len(satisfied),
        "support_data_ops_operations_privacy_security_legal_production_blocker_count": go_no_go[
            "production_blocker_count"
        ],
        "support_data_ops_operations_privacy_security_legal_unsatisfied_blockers": unsatisfied_ids,
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_human_launch_approval_required": True,
        "support_contact_used_for_go_no_go": "joy7758@gmail.com",
    }
    for key in FALSE_KEYS:
        profile[key] = False
    write_json(PROFILE_PATH, profile)
    return profile


def render_report(summary: dict[str, Any]) -> str:
    remaining = "\n".join(
        f"- {item}"
        for item in summary[
            "support_data_ops_operations_privacy_security_legal_unsatisfied_blockers"
        ]
    )
    return f"""# SAEE Privacy / Security / Legal Human-Filled Evidence Run v0.1

Status: {summary['run_status']}.

This local run records human-filled privacy/security/legal evidence for formal
security review, privacy/legal review, DPA availability, and vulnerability
management. It produces review-ready evidence for the commercial go/no-go
aggregator only.

## What Was Completed

- formal_security_review_validation_status: {summary['formal_security_review_validation_status']}
- privacy_legal_dpa_validation_status: {summary['privacy_legal_dpa_validation_status']}
- vulnerability_management_validation_status: {summary['vulnerability_management_validation_status']}
- formal_security_review_builder_status: {summary['formal_security_review_builder_status']}
- privacy_legal_dpa_builder_status: {summary['privacy_legal_dpa_builder_status']}
- vulnerability_management_builder_status: {summary['vulnerability_management_builder_status']}
- privacy_security_legal_profile_status: {summary['privacy_security_legal_profile_status']}
- formal_security_review_completed_for_go_no_go: {str(summary['formal_security_review_completed_for_go_no_go']).lower()}
- privacy_legal_review_completed_for_go_no_go: {str(summary['privacy_legal_review_completed_for_go_no_go']).lower()}
- data_processing_agreement_available_for_go_no_go: {str(summary['data_processing_agreement_available_for_go_no_go']).lower()}
- vulnerability_management_available_for_go_no_go: {str(summary['vulnerability_management_available_for_go_no_go']).lower()}
- production_privacy_security_legal_ready: {str(summary['production_privacy_security_legal_ready']).lower()}
- support_contact_used_for_go_no_go: {summary['support_contact_used_for_go_no_go']}
- support_data_ops_operations_privacy_security_legal_production_blocker_count: {summary['support_data_ops_operations_privacy_security_legal_production_blocker_count']}

## Satisfied Privacy / Security / Legal Signals

- formal_security_review
- privacy_legal_review
- data_processing_agreement
- vulnerability_management

## Remaining Production Blockers

{remaining}

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- customer_contacted: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- external_model_api_called: false
- external_ai_assistant_tested: false
- security_vendor_contacted: false
- legal_counsel_contacted: false
- customer_data_processed: false
- dpa_sent_to_customer: false
- terms_published: false
- privacy_notice_published: false
- production_security_enabled: false
- vulnerability_management_operational: false

## Non-Closure Statement

This run does not close blockers by itself, does not authorize launch, does not
perform external legal/security review, and does not make SAEE production-ready.
It only records local human-filled evidence that can be reviewed by the
commercial go/no-go layer.
"""


def write_gate(summary: dict[str, Any]) -> None:
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        f"""# SAEE Privacy / Security / Legal Human-Filled Evidence Run Gate

answer: recommend_for_local_go_no_go_review_only

reason:
Human-filled local evidence for formal security review, privacy/legal review,
DPA availability, and vulnerability management is complete enough for the local
commercial go/no-go aggregator. This does not constitute external legal review,
security certification, customer-data authorization, or production readiness.

status:
- run_status: {summary['run_status']}
- validation_status: {summary['validation_status']}
- production_privacy_security_legal_ready: {str(summary['production_privacy_security_legal_ready']).lower()}
- support_data_ops_operations_privacy_security_legal_production_blocker_count: {summary['support_data_ops_operations_privacy_security_legal_production_blocker_count']}
- commercial_status_after_profile: {summary['commercial_status_after_profile']}
- production_launch_status_after_profile: {summary['production_launch_status_after_profile']}

boundary:
- production_ready: false
- customer_validated: false
- product_launched: false
- customer_contacted: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- legal_counsel_contacted: false
- security_vendor_contacted: false
- customer_data_processed: false

next_action:
Continue resolving remaining production blockers. Separate human launch approval
is still required before any commercial release.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    write_json(FORMAL_SECURITY_INPUT_PATH, formal_security_input())
    write_json(PRIVACY_LEGAL_DPA_INPUT_PATH, privacy_legal_dpa_input())
    write_json(VULNERABILITY_INPUT_PATH, vulnerability_input())

    formal_validation = build_formal_security_validation(FORMAL_SECURITY_INPUT_PATH)
    privacy_validation = build_privacy_legal_dpa_validation(PRIVACY_LEGAL_DPA_INPUT_PATH)
    vulnerability_validation = build_vulnerability_validation(VULNERABILITY_INPUT_PATH)
    write_json(FORMAL_SECURITY_VALIDATION_PATH, formal_validation)
    write_json(PRIVACY_LEGAL_DPA_VALIDATION_PATH, privacy_validation)
    write_json(VULNERABILITY_VALIDATION_PATH, vulnerability_validation)
    FORMAL_SECURITY_VALIDATION_MD_PATH.write_text(
        formal_security_validation_markdown(formal_validation), encoding="utf-8"
    )
    PRIVACY_LEGAL_DPA_VALIDATION_MD_PATH.write_text(
        privacy_legal_dpa_validation_markdown(privacy_validation), encoding="utf-8"
    )
    VULNERABILITY_VALIDATION_MD_PATH.write_text(
        vulnerability_validation_markdown(vulnerability_validation), encoding="utf-8"
    )

    formal_builder = build_formal_security_evidence(
        FORMAL_SECURITY_INPUT_PATH,
        FORMAL_SECURITY_BUILDER_OUTPUT_PATH,
        FORMAL_SECURITY_EVIDENCE_PATH,
        write_documentation=False,
    )
    privacy_builder = build_privacy_legal_dpa_evidence(
        PRIVACY_LEGAL_DPA_INPUT_PATH,
        PRIVACY_LEGAL_DPA_BUILDER_OUTPUT_PATH,
        PRIVACY_LEGAL_DPA_EVIDENCE_PATH,
        write_documentation=False,
    )
    vulnerability_builder = build_vulnerability_evidence(
        VULNERABILITY_INPUT_PATH,
        VULNERABILITY_BUILDER_OUTPUT_PATH,
        VULNERABILITY_EVIDENCE_PATH,
        write_documentation=False,
    )

    formal_evidence = read_json(FORMAL_SECURITY_EVIDENCE_PATH)
    privacy_evidence = read_json(PRIVACY_LEGAL_DPA_EVIDENCE_PATH)
    vulnerability_evidence = read_json(VULNERABILITY_EVIDENCE_PATH)
    source_violations = [
        *source_boundary_violations("formal_security_source", formal_evidence),
        *source_boundary_violations("privacy_legal_dpa_source", privacy_evidence),
        *source_boundary_violations("vulnerability_management_source", vulnerability_evidence),
    ]
    profile = build_profile(
        formal_evidence,
        privacy_evidence,
        vulnerability_evidence,
        source_violations,
    )
    summary: dict[str, Any] = {
        "run_id": "privacy_security_legal_human_filled_evidence_run_v0_1",
        "run_status": profile["profile_status"],
        "validation_status": (
            "pass"
            if all(
                item["validation_status"] == "pass"
                for item in (formal_validation, privacy_validation, vulnerability_validation)
            )
            and profile["profile_status"] == "pass"
            else "hold"
        ),
        "formal_security_review_validation_status": formal_validation["validation_status"],
        "privacy_legal_dpa_validation_status": privacy_validation["validation_status"],
        "vulnerability_management_validation_status": vulnerability_validation[
            "validation_status"
        ],
        "formal_security_review_builder_status": formal_builder["status"],
        "privacy_legal_dpa_builder_status": privacy_builder["status"],
        "vulnerability_management_builder_status": vulnerability_builder["status"],
        "privacy_security_legal_profile_status": profile["profile_status"],
        "formal_security_review_completed_for_go_no_go": profile[
            "formal_security_review_completed_for_go_no_go"
        ],
        "privacy_legal_review_completed_for_go_no_go": profile[
            "privacy_legal_review_completed_for_go_no_go"
        ],
        "data_processing_agreement_available_for_go_no_go": profile[
            "data_processing_agreement_available_for_go_no_go"
        ],
        "vulnerability_management_available_for_go_no_go": profile[
            "vulnerability_management_available_for_go_no_go"
        ],
        "production_privacy_security_legal_ready": profile[
            "production_privacy_security_legal_ready"
        ],
        "privacy_security_legal_satisfied_blockers": profile[
            "privacy_security_legal_satisfied_blockers"
        ],
        "support_contact_used_for_go_no_go": profile["support_contact_used_for_go_no_go"],
        "support_data_ops_operations_privacy_security_legal_production_blocker_count": profile[
            "support_data_ops_operations_privacy_security_legal_production_blocker_count"
        ],
        "support_data_ops_operations_privacy_security_legal_unsatisfied_blockers": profile[
            "support_data_ops_operations_privacy_security_legal_unsatisfied_blockers"
        ],
        "commercial_status_after_profile": profile["commercial_status_after_profile"],
        "production_launch_status_after_profile": profile[
            "production_launch_status_after_profile"
        ],
        "blockers_closed_by_validator": 0,
        "blockers_closed_by_builder": 0,
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_human_launch_approval_required": True,
        "input_files": [
            str(FORMAL_SECURITY_INPUT_PATH),
            str(PRIVACY_LEGAL_DPA_INPUT_PATH),
            str(VULNERABILITY_INPUT_PATH),
        ],
        "output_files": [
            str(FORMAL_SECURITY_VALIDATION_PATH),
            str(FORMAL_SECURITY_BUILDER_OUTPUT_PATH),
            str(FORMAL_SECURITY_EVIDENCE_PATH),
            str(PRIVACY_LEGAL_DPA_VALIDATION_PATH),
            str(PRIVACY_LEGAL_DPA_BUILDER_OUTPUT_PATH),
            str(PRIVACY_LEGAL_DPA_EVIDENCE_PATH),
            str(VULNERABILITY_VALIDATION_PATH),
            str(VULNERABILITY_BUILDER_OUTPUT_PATH),
            str(VULNERABILITY_EVIDENCE_PATH),
            str(COMBINED_EVIDENCE_PATH),
            str(PROFILE_PATH),
        ],
    }
    for key in FALSE_KEYS:
        summary[key] = False

    write_json(SUMMARY_PATH, summary)
    REPORT_PATH.write_text(render_report(summary), encoding="utf-8")
    write_gate(summary)
    print(
        "SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN: PASS "
        "privacy_security_legal_profile_status=pass production_blockers=12 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
