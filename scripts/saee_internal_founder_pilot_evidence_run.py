#!/usr/bin/env python3
"""Record an internal founder self-test pilot evidence run.

This run uses explicit human answers from the current thread to create local
pilot-result evidence. It is internal proxy evidence only: it does not contact
customers, claim external customer validation, publish testimonials, launch
product, modify backend/runtime/kernel/API schema, or expose private core.
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
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    PILOT_RESULT_KEYS,
    evaluate_production_customer_validation_evidence,
)
from scripts.saee_customer_validation_approval_input_validator import (
    build_validation as build_customer_validation_input_validation,
    report_markdown as customer_validation_input_validation_markdown,
)
from scripts.saee_customer_validation_evidence_builder import (
    build_from_file,
    input_template,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
INPUT_PATH = OUTPUT_DIR / "customer_validation_evidence_input.internal_founder_pilot.local.json"
VALIDATION_PATH = OUTPUT_DIR / "customer_validation_approval_input_validation.internal_founder_pilot.local.json"
VALIDATION_MD_PATH = OUTPUT_DIR / "customer_validation_approval_input_validation.internal_founder_pilot.md"
EVIDENCE_PATH = OUTPUT_DIR / "customer_validation_evidence.from_internal_founder_pilot.local.json"
SUMMARY_PATH = OUTPUT_DIR / "internal_founder_pilot_evidence_run_summary.local.json"
REPORT_PATH = OUTPUT_DIR / "internal_founder_pilot_evidence_run_report.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_INTERNAL_FOUNDER_PILOT_EVIDENCE_RUN_GATE.md"

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
PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "production_privacy_security_legal_evidence.combined_from_formal_privacy_dpa_vulnerability_human_filled.local.json"
)
BILLING_REVENUE_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "production_billing_revenue_evidence.combined_from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json"
)
AUTH_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/"
    "phase_1_identity_tenant_auth_evidence.human_filled.local.json"
)
TENANT_STORAGE_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/"
    "phase_1_identity_tenant_storage_evidence.human_filled.local.json"
)

RUN_DATE = "2026-07-09"
SESSION_ID = "PILOT-20260709-FOUNDER-SELF-TEST-001"
FALSE_BOUNDARY_KEYS = [
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
    "customer_contacted_by_codex",
    "automated_customer_contact",
    "unsolicited_customer_contact",
    "customer_data_collected",
    "customer_data_processing_started",
    "customer_secrets_collected",
    "user_upload_enabled",
    "product_market_fit_claimed",
    "revenue_validated",
    "production_readiness_claimed",
    "public_validation_claim_published",
    "testimonial_published",
    "case_study_published",
    "paid_pilot_completed",
]


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_INTERNAL_FOUNDER_PILOT_EVIDENCE_RUN: FAIL " + message)


def founder_pilot_input() -> dict[str, Any]:
    data = input_template()
    review = {key: False for key in (PILOT_RESULT_KEYS + CUSTOMER_VALUE_KEYS + CLAIM_PERMISSION_KEYS + BOUNDARY_REVIEW_KEYS)}
    for key in PILOT_RESULT_KEYS:
        review[key] = True
    for key in CUSTOMER_VALUE_KEYS:
        review[key] = True
    for key in BOUNDARY_REVIEW_KEYS:
        review[key] = True

    # Internal use is approved, but no public customer-validation claim is approved.
    for key in [
        "real_customer_or_target_user_feedback_recorded",
        "permission_to_use_feedback_recorded",
        "customer_problem_fit_reviewed",
        "decision_usefulness_observed",
        "customer_validation_record_approved_by_human",
    ]:
        review[key] = True
    review["claim_scope_approved"] = False
    review["reviewer_approved_validation_claim"] = False

    data.update(
        {
            "input_status": "internal_founder_self_test_completed",
            "customer_validation_evidence_input_v0_1": True,
            "human_reviewer_name": "张斌",
            "review_date": RUN_DATE,
            "evidence_review": review,
            "aggregate_metrics": {
                "session_count": 1,
                "understanding_rate": 5,
                "trust_rate": 4,
                "decision_influence_rate": 4,
                "repeat_usage_intent": 4,
                "go_hold_pivot": "hold_external_customer_validation_required",
            },
            "boundary_note": (
                "Internal founder self-test only. It may support pilot-results "
                "evidence, but it is not real external customer validation and "
                "must not be used as a public customer-validation claim."
            ),
            "sessions": [
                {
                    "session_id": SESSION_ID,
                    "session_date": RUN_DATE,
                    "participant_role": "创始人 / AI Agent 产品负责人 / 策略评测需求方",
                    "team_type": "早期创业团队 / AI Agent 产品团队",
                    "current_evaluation_method": "人工对比、少量测试、LangSmith/日志追踪、主观判断组合",
                    "candidate_count": 3,
                    "understanding_score": 5,
                    "trust_score": 4,
                    "decision_influence_score": 4,
                    "repeat_usage_intent_score": 4,
                    "willing_to_test_own_candidates": True,
                    "saee_demo_surface_used": "local_mvp_demo",
                    "top_objection": "还需要真实外部用户试用和更多行业场景样本",
                    "evidence_missing": "真实客户试用记录、更多案例、长期运行报告、部署前后对比",
                    "notes": (
                        "Founder self-test confirms SAEE is understandable for "
                        "long-term stability comparison and deployment-decision "
                        "support, but external customer validation remains pending."
                    ),
                    "boundary_flags": {
                        "secrets_collected": False,
                        "production_data_collected": False,
                        "customer_data_uploaded": False,
                        "private_core_disclosed": False,
                        "production_ready_claim_made": False,
                    },
                }
            ],
        }
    )
    for key in FALSE_BOUNDARY_KEYS:
        data[key] = False
    data["customer_contacted"] = False
    return data


def commercial_go_no_go_with_context() -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings(
            {
                "SAEE_SUPPORT_CONTACT": "joy7758@gmail.com",
                "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(AUTH_EVIDENCE_PATH),
                "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(TENANT_STORAGE_EVIDENCE_PATH),
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(SUPPORT_EVIDENCE_PATH),
                "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(DATA_OPS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(OPERATIONS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
                    PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH
                ),
                "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(
                    BILLING_REVENUE_EVIDENCE_PATH
                ),
                "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(EVIDENCE_PATH),
            }
        )
    )


def blocker_state(go_no_go: dict[str, object]) -> tuple[list[str], list[str]]:
    blockers = go_no_go.get("blockers", [])
    require(isinstance(blockers, list), "go/no-go blockers must be a list")
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = str(item.get("blocker_id", ""))
        if item.get("satisfied") is True:
            satisfied.append(blocker_id)
        else:
            unsatisfied.append(blocker_id)
    return satisfied, unsatisfied


def write_report(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        f"""# SAEE Internal Founder Pilot Evidence Run v0.1

Status: pass for internal pilot-result evidence only.

## Summary

- run_status: {summary['run_status']}
- validation_status: {summary['validation_status']}
- customer_validation_input_validation_status: {summary['customer_validation_input_validation_status']}
- customer_validation_readiness_status: {summary['customer_validation_readiness_status']}
- pilot_results_evidence_complete: {str(summary['pilot_results_evidence_complete']).lower()}
- customer_value_evidence_complete: {str(summary['customer_value_evidence_complete']).lower()}
- claim_permission_evidence_complete: {str(summary['claim_permission_evidence_complete']).lower()}
- customer_validation_evidence_complete: {str(summary['customer_validation_evidence_complete']).lower()}
- production_customer_validation_ready: {str(summary['production_customer_validation_ready']).lower()}
- all_evidence_production_blocker_count: {summary['all_evidence_production_blocker_count']}
- all_evidence_remaining_blockers: {', '.join(summary['all_evidence_remaining_blockers'])}
- commercial_status_after_profile: {summary['commercial_status_after_profile']}
- production_launch_status_after_profile: {summary['production_launch_status_after_profile']}

## What This Evidence Means

This evidence records an internal founder self-test. It can support the
`pilot_results` evidence lane because a completed local pilot session was
recorded with scores and boundary review.

## What This Evidence Does Not Mean

It is not real external customer validation. It does not satisfy
`customer_validated`, does not approve public validation claims, does not
publish testimonials or case studies, and does not authorize launch.

## Boundary

- production_ready=false
- customer_validated=false
- product_launched=false
- customer_contacted=false
- private_core_exposed=false
- runtime_modified=false
- backend_modified=false
- kernel_modified=false
- api_schema_modified=false
- external_calls_made=false
- customer_data_collected=false
- customer_secrets_collected=false
- public_validation_claim_published=false
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        f"""# SAEE Internal Founder Pilot Evidence Run Gate

answer: internal_pilot_results_recorded_customer_validation_still_pending

reason: A founder self-test pilot record was captured and can support the
pilot-results evidence lane, but it is not external customer validation.

pilot_results_evidence_complete: {str(summary['pilot_results_evidence_complete']).lower()}
customer_validation_evidence_complete: {str(summary['customer_validation_evidence_complete']).lower()}
customer_validated: false
remaining_production_blocker_count: {summary['all_evidence_production_blocker_count']}
remaining_production_blockers: {', '.join(summary['all_evidence_remaining_blockers'])}

boundary:
production_ready: false
customer_validated: false
product_launched: false
customer_contacted: false
private_core_exposed: false
external_calls_made: false
public_validation_claim_published: false

next_action: obtain real external target-user or customer validation before any
commercial-launch claim.
""",
        encoding="utf-8",
    )


def main() -> None:
    write_json(INPUT_PATH, founder_pilot_input())
    validation = build_customer_validation_input_validation(INPUT_PATH)
    write_json(VALIDATION_PATH, validation)
    VALIDATION_MD_PATH.write_text(
        customer_validation_input_validation_markdown(validation),
        encoding="utf-8",
    )
    evidence = build_from_file(INPUT_PATH, EVIDENCE_PATH)
    readiness = evaluate_production_customer_validation_evidence(
        load_settings({"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(EVIDENCE_PATH)})
    )
    go_no_go = commercial_go_no_go_with_context()
    satisfied, unsatisfied = blocker_state(go_no_go)

    require(evidence["completed_session_count"] == 1, "one internal pilot session required")
    require(readiness["pilot_results_evidence_complete"] is True, "pilot evidence must be complete")
    require(
        readiness["customer_validation_evidence_complete"] is False,
        "customer validation evidence must remain incomplete",
    )
    require("pilot_results" in satisfied, "pilot_results must be satisfied by internal pilot evidence")
    require(unsatisfied == ["customer_validated"], "customer_validated must remain the only blocker")
    require(go_no_go["commercial_status"] == "hold", "commercial status must remain hold")
    require(go_no_go["production_launch_status"] == "hold", "launch status must remain hold")

    summary: dict[str, Any] = {
        "internal_founder_pilot_evidence_run_v0_1": True,
        "run_type": "internal_founder_self_test_pilot_evidence",
        "generated_by": "scripts/saee_internal_founder_pilot_evidence_run.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "run_status": "pass",
        "validation_status": "pass",
        "customer_validation_input_validation_status": validation["validation_status"],
        "customer_validation_input_builder_ready": validation["builder_ready"],
        "customer_validation_readiness_status": readiness["status"],
        "completed_session_count": evidence["completed_session_count"],
        "pilot_results_evidence_complete": readiness["pilot_results_evidence_complete"],
        "customer_value_evidence_complete": readiness["customer_value_evidence_complete"],
        "claim_permission_evidence_complete": readiness["claim_permission_evidence_complete"],
        "boundary_review_evidence_complete": readiness["boundary_review_evidence_complete"],
        "customer_validation_evidence_complete": readiness["customer_validation_evidence_complete"],
        "production_customer_validation_ready": readiness["production_customer_validation_ready"],
        "all_evidence_satisfied_blockers": satisfied,
        "all_evidence_remaining_blockers": unsatisfied,
        "all_evidence_production_blocker_count": go_no_go["production_blocker_count"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "blockers_closed_by_validator": 0,
        "blockers_closed_by_builder": 0,
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "internal_pilot_only": True,
        "external_customer_validation_performed": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "revenue_validated": False,
        "input_file": str(INPUT_PATH),
        "validation_file": str(VALIDATION_PATH),
        "evidence_file": str(EVIDENCE_PATH),
        "report_file": str(REPORT_PATH),
        "gate_file": str(GATE_PATH),
    }
    write_json(SUMMARY_PATH, summary)
    write_report(summary)
    print(
        "SAEE_INTERNAL_FOUNDER_PILOT_EVIDENCE_RUN: PASS "
        "pilot_results_evidence_complete=true remaining_blockers=1 "
        "customer_validated=false"
    )


if __name__ == "__main__":
    main()
