#!/usr/bin/env python3
"""Audit Phase 5 customer validation and launch-review evidence gaps.

This runner compares Phase 5 pilot-results and customer-validation production
evidence requirements against existing local public-shell customer-validation
evidence. It is a planning and review aid only: it does not contact customers,
run pilots, infer missing feedback, collect customer data, publish validation
claims, authorize launch, close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from scripts.saee_commercial_review_semantics import local_public_shell_go_no_go_summary


CUSTOMER_VALIDATION_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json"
)
DEPENDENCY_PLAN_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
)
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit"
)
OUTPUT_JSON = OUTPUT_DIR / "phase_5_customer_validation_launch_gap_audit.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_5_customer_validation_launch_gap_audit.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_5_customer_validation_launch_gap_audit.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT_RECOMMENDATION_GATE.md"
)


LOCAL_PROFILE_ENV = {
    "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": "phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json",
    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": "phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json",
    "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json",
    "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json",
    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json",
    "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json",
    "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
    "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(
        CUSTOMER_VALIDATION_EVIDENCE_PATH.relative_to(ROOT)
    ),
}


PHASE_ID = "phase_5_customer_validation_and_launch_review"
TARGET_BLOCKERS = [
    "pilot_results",
    "customer_validated",
]


REQUIRED_EVIDENCE_ITEMS: list[dict[str, str]] = [
    {
        "blocker_id": "pilot_results",
        "evidence_key": "at_least_one_human_approved_pilot_session_completed",
    },
    {
        "blocker_id": "pilot_results",
        "evidence_key": "pilot_result_template_completed",
    },
    {
        "blocker_id": "pilot_results",
        "evidence_key": "feedback_form_completed",
    },
    {
        "blocker_id": "pilot_results",
        "evidence_key": "success_criteria_applied",
    },
    {
        "blocker_id": "pilot_results",
        "evidence_key": "boundary_flags_reviewed",
    },
    {
        "blocker_id": "pilot_results",
        "evidence_key": "pilot_result_reviewed_by_human",
    },
    {
        "blocker_id": "customer_validated",
        "evidence_key": "real_customer_or_target_user_feedback_recorded",
    },
    {
        "blocker_id": "customer_validated",
        "evidence_key": "permission_to_use_feedback_recorded",
    },
    {
        "blocker_id": "customer_validated",
        "evidence_key": "customer_problem_fit_reviewed",
    },
    {
        "blocker_id": "customer_validated",
        "evidence_key": "decision_usefulness_observed",
    },
    {
        "blocker_id": "customer_validated",
        "evidence_key": "claim_scope_approved",
    },
    {
        "blocker_id": "customer_validated",
        "evidence_key": "customer_validation_record_approved_by_human",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def phase_blockers(plan: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = [
        blocker
        for blocker in plan.get("blockers", [])
        if blocker.get("phase_id") == PHASE_ID
    ]
    blocker_ids = [blocker["blocker_id"] for blocker in blockers]
    if blocker_ids != TARGET_BLOCKERS:
        raise SystemExit(
            "SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT: FAIL "
            f"unexpected phase blockers {blocker_ids}"
        )
    return blockers


def blocker_map(blockers: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {blocker["blocker_id"]: blocker for blocker in blockers}


def classify_item(local_value: bool) -> str:
    if local_value:
        return "local_public_shell_evidence_present_requires_human_production_approval"
    return "missing_external_or_human_production_evidence"


def build_gap_rows(
    customer_validation: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_blocker = blocker_map(blockers)
    rows: list[dict[str, Any]] = []
    for item in REQUIRED_EVIDENCE_ITEMS:
        local_value = customer_validation.get(item["evidence_key"]) is True
        blocker = by_blocker[item["blocker_id"]]
        rows.append(
            {
                "blocker_id": item["blocker_id"],
                "evidence_file_type": "production_customer_validation_evidence",
                "evidence_key": item["evidence_key"],
                "local_public_shell_value": local_value,
                "accepted_for_blocker_closure": False,
                "gap_status": classify_item(local_value),
                "external_dependency_required": blocker.get(
                    "external_dependency_required"
                )
                is True,
                "engineering_implementation_required": blocker.get(
                    "engineering_implementation_required"
                )
                is True,
                "human_review_required": True,
                "notes": (
                    "Local evidence is review input only; it does not close the production blocker."
                    if local_value
                    else "Real customer or target-user evidence and human approval are still missing."
                ),
            }
        )
    return rows


def summarize_by_blocker(
    rows: list[dict[str, Any]], blockers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_blocker = blocker_map(blockers)
    summary: list[dict[str, Any]] = []
    for blocker_id in TARGET_BLOCKERS:
        subset = [row for row in rows if row["blocker_id"] == blocker_id]
        local_present = sum(1 for row in subset if row["local_public_shell_value"])
        missing = len(subset) - local_present
        blocker = by_blocker[blocker_id]
        summary.append(
            {
                "blocker_id": blocker_id,
                "required_items": len(subset),
                "local_public_shell_present": local_present,
                "missing_production_evidence": missing,
                "ready_to_close": False,
                "external_dependency_required": blocker.get(
                    "external_dependency_required"
                )
                is True,
                "engineering_implementation_required": blocker.get(
                    "engineering_implementation_required"
                )
                is True,
                "next_action": (
                    "Human owners must provide real pilot and customer-validation "
                    "evidence, permission records, and approved claim scope before "
                    "this blocker can close."
                ),
            }
        )
    return summary


def csv_text(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = [
        "blocker_id",
        "evidence_file_type",
        "evidence_key",
        "local_public_shell_value",
        "accepted_for_blocker_closure",
        "gap_status",
        "external_dependency_required",
        "engineering_implementation_required",
        "human_review_required",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build_audit() -> dict[str, Any]:
    customer_validation = read_json(CUSTOMER_VALIDATION_EVIDENCE_PATH)
    plan = read_json(DEPENDENCY_PLAN_PATH)
    blockers = phase_blockers(plan)
    default_go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    local_profile_go_no_go = evaluate_commercial_go_no_go(load_settings(LOCAL_PROFILE_ENV))
    rows = build_gap_rows(customer_validation, blockers)
    blocker_summary = summarize_by_blocker(rows, blockers)
    local_present = sum(1 for row in rows if row["local_public_shell_value"])
    missing = len(rows) - local_present

    return {
        "audit_type": "saee_phase_5_customer_validation_launch_gap_audit",
        "audit_version": "v0.1",
        "audit_scope": "local_public_shell_to_production_customer_validation_launch_gap_review",
        "phase_id": PHASE_ID,
        "generated_by": "scripts/saee_phase5_customer_validation_launch_gap_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_dependency_plan": str(DEPENDENCY_PLAN_PATH.relative_to(ROOT)),
        "source_customer_validation_evidence": str(
            CUSTOMER_VALIDATION_EVIDENCE_PATH.relative_to(ROOT)
        ),
        "target_blockers": [blocker["blocker_id"] for blocker in blockers],
        "target_blocker_count": len(blockers),
        "required_evidence_item_count": len(rows),
        "local_public_shell_present_count": local_present,
        "missing_production_evidence_count": missing,
        "accepted_for_blocker_closure_count": 0,
        "blockers_ready_to_close": [],
        "blockers_closed_by_audit": 0,
        "default_go_no_go": {
            "commercial_status": default_go_no_go["commercial_status"],
            "production_launch_status": default_go_no_go["production_launch_status"],
            "satisfied_production_checks": default_go_no_go[
                "satisfied_production_checks"
            ],
            "production_blocker_count": default_go_no_go["production_blocker_count"],
            "total_production_checks": default_go_no_go["total_production_checks"],
        },
        "local_profile_go_no_go": local_public_shell_go_no_go_summary(local_profile_go_no_go),
        "blocker_summary": blocker_summary,
        "gap_rows": rows,
        "human_review_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "unsolicited_customer_contact": False,
        "codex_executed_pilot": False,
        "pilot_session_started": False,
        "pilot_session_completed": False,
        "pilot_results_recorded": False,
        "feedback_form_completed": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "permission_to_use_feedback_recorded": False,
        "public_validation_claim_published": False,
        "case_study_published": False,
        "testimonial_published": False,
        "product_market_fit_claimed": False,
        "production_readiness_claimed": False,
        "customer_validated": False,
        "product_launched": False,
        "launch_approved": False,
        "public_launch_claim_added": False,
        "production_ready": False,
        "revenue_validated": False,
        "user_upload_enabled": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "next_action": (
            "Human owners must provide approved real pilot and customer-validation "
            "evidence before any Phase 5 blocker, customer-validation claim, or "
            "launch decision can close."
        ),
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Phase 5 Customer Validation/Launch Gap Audit

Status: local gap audit only; no blocker closure.

This directory compares Phase 5 pilot-results and customer-validation evidence
requirements against existing local public-shell customer-validation evidence.
It is a commercial-readiness review surface, not a customer test, pilot, or
launch task.

Boundary:

- no customer contacted by Codex
- no pilot executed
- no feedback inferred
- no customer data collected
- no customer secrets collected
- no validation claim published
- no case study or testimonial published
- no product-market-fit claim
- no production-readiness claim
- no product launch approval
- no blocker closure
- no backend, runtime, kernel, API schema, or private core modification
""",
        encoding="utf-8",
    )


def markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 5 Customer Validation/Launch Gap Audit v0.1",
        "",
        "Status: local public-shell gap audit only; no blocker closure.",
        "",
        "This audit compares Phase 5 production evidence requirements against",
        "existing local customer-validation evidence. Local evidence may support",
        "human review, but it is not accepted as pilot completion, customer",
        "validation, or launch approval by this audit.",
        "",
        "## Summary",
        "",
        f"- required_evidence_item_count: {audit['required_evidence_item_count']}",
        f"- local_public_shell_present_count: {audit['local_public_shell_present_count']}",
        f"- missing_production_evidence_count: {audit['missing_production_evidence_count']}",
        f"- accepted_for_blocker_closure_count: {audit['accepted_for_blocker_closure_count']}",
        f"- blockers_closed_by_audit: {audit['blockers_closed_by_audit']}",
        f"- default_go_no_go: {audit['default_go_no_go']['satisfied_production_checks']}/{audit['default_go_no_go']['total_production_checks']} satisfied",
        f"- local_profile_go_no_go: {audit['local_profile_go_no_go']['satisfied_production_checks']}/{audit['local_profile_go_no_go']['total_production_checks']} satisfied",
        f"- local_public_shell_review_candidate_count: {audit['local_profile_go_no_go']['local_public_shell_review_candidate_count']}",
        f"- customer_validated: {str(audit['customer_validated']).lower()}",
        f"- product_launched: {str(audit['product_launched']).lower()}",
        f"- production_ready: {str(audit['production_ready']).lower()}",
        f"- private_core_exposed: {str(audit['private_core_exposed']).lower()}",
        "",
        "## Blocker Summary",
        "",
        "| Blocker | Required items | Local public-shell present | Missing production evidence | Ready to close | External dependency |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in audit["blocker_summary"]:
        lines.append(
            "| {blocker_id} | {required_items} | {local_public_shell_present} | {missing_production_evidence} | {ready} | {external} |".format(
                blocker_id=row["blocker_id"],
                required_items=row["required_items"],
                local_public_shell_present=row["local_public_shell_present"],
                missing_production_evidence=row["missing_production_evidence"],
                ready=str(row["ready_to_close"]).lower(),
                external=str(row["external_dependency_required"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this audit.",
            "- No customer is contacted by Codex.",
            "- No pilot is executed.",
            "- No feedback is inferred.",
            "- No customer data or secrets are collected.",
            "- No customer-validation claim is published.",
            "- No case study or testimonial is published.",
            "- No product-market-fit claim is made.",
            "- No production-readiness claim is made.",
            "- No product launch is authorized.",
            "- No private core is exposed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_doc() -> None:
    DOC_PATH.write_text(
        """# SAEE Phase 5 Customer Validation/Launch Gap Audit v0.1

phase_5_customer_validation_launch_gap_audit_v0_1: true
audit_scope: local_public_shell_to_production_customer_validation_launch_gap_review
required_evidence_item_count: 12
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
customer_contacted_by_codex: false
automated_customer_contact: false
codex_executed_pilot: false
pilot_session_completed: false
pilot_results_recorded: false
feedback_form_completed: false
customer_data_collected: false
customer_secrets_collected: false
permission_to_use_feedback_recorded: false
public_validation_claim_published: false
case_study_published: false
testimonial_published: false
product_market_fit_claimed: false
production_readiness_claimed: false
customer_validated: false
product_launched: false
launch_approved: false
production_ready: false
revenue_validated: false
private_core_exposed: false

## Purpose

This audit compares Phase 5 pilot-results and customer-validation production
evidence requirements against existing local public-shell customer-validation
evidence. It records which evidence keys are locally present and which still
need real customer or target-user evidence and human approval.

It is an audit only. It does not authorize execution, close blockers, contact
customers, run pilots, infer missing feedback, collect customer data, publish
validation claims, publish testimonials or case studies, approve launch, or
claim production readiness.

## Target Blockers

- pilot_results
- customer_validated
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE_PATH.write_text(
        """# SAEE Phase 5 Customer Validation/Launch Gap Audit Recommendation Gate

answer: conditional
recommend_for_human_review: true
recommend_for_blocker_closure: false
recommend_for_execution_authorization: false
recommend_for_customer_contact: false
recommend_for_pilot_execution: false
recommend_for_customer_validation_claim: false
recommend_for_case_study_publication: false
recommend_for_testimonial_publication: false
recommend_for_product_market_fit_claim: false
recommend_for_launch_approval: false
recommend_for_production_launch: false

## Reason

This audit is useful because it separates local public-shell
customer-validation packets from real pilot and customer-validation evidence.
It does not close any blocker, contact customers, execute pilots, authorize
launch, or create validation claims.

## Boundary

```yaml
audit_scope: local_public_shell_to_production_customer_validation_launch_gap_review
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
customer_contacted_by_codex: false
automated_customer_contact: false
codex_executed_pilot: false
pilot_session_completed: false
pilot_results_recorded: false
customer_data_collected: false
customer_secrets_collected: false
public_validation_claim_published: false
case_study_published: false
testimonial_published: false
product_market_fit_claimed: false
customer_validated: false
product_launched: false
launch_approved: false
production_ready: false
private_core_exposed: false
```

## Next Action

Human reviewers may use the gap table to decide whether to authorize a
separate real pilot/customer-validation evidence collection task. Until then,
all Phase 5 blockers remain open.
""",
        encoding="utf-8",
    )


def write_outputs(audit: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(markdown_report(audit), encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(audit["gap_rows"]), encoding="utf-8")
    write_readme()
    write_doc()
    write_gate()


def main() -> None:
    audit = build_audit()
    write_outputs(audit)
    print(
        "SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
