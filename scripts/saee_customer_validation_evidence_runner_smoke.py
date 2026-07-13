#!/usr/bin/env python3
"""Smoke check for the local customer-validation evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_customer_validation_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_customer_validation_evidence,
)
from scripts.saee_customer_validation_evidence_runner import (
    OUTPUT_PATH,
    main as run_runner,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_EVIDENCE_RUNNER_SMOKE: FAIL: " + message
        )


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    require(
        evidence.get("customer_validation_evidence_type")
        == "production_customer_validation_evidence",
        "wrong customer-validation evidence type",
    )
    require(
        evidence.get("evidence_scope")
        == "local_public_shell_customer_validation_review_packet",
        "wrong evidence scope",
    )
    for flag in [
        "first_user_test_plan_available",
        "feedback_form_available",
        "success_criteria_available",
        "pilot_result_template_available",
        "pilot_session_protocol_available",
        "boundary_flags_reviewed",
        "no_private_core_disclosed",
        "no_customer_secrets_collected",
        "no_customer_upload_required",
        "no_production_ready_claim_added",
        "no_public_launch_claim_added",
    ]:
        require(evidence.get(flag) is True, f"{flag} must be recorded true")
    for flag in [
        "at_least_one_human_approved_pilot_session_completed",
        "pilot_result_template_completed",
        "feedback_form_completed",
        "success_criteria_applied",
        "pilot_result_reviewed_by_human",
        "customer_role_and_segment_recorded",
        "pain_point_fit_observed",
        "deployment_decision_value_observed",
        "recommendation_output_understood",
        "failure_summary_usefulness_observed",
        "go_hold_pivot_decision_recorded",
        "real_customer_or_target_user_feedback_recorded",
        "permission_to_use_feedback_recorded",
        "customer_problem_fit_reviewed",
        "decision_usefulness_observed",
        "claim_scope_approved",
        "customer_validation_record_approved_by_human",
        "reviewer_approved_validation_claim",
        "negative_feedback_recorded",
    ]:
        require(evidence.get(flag) is False, f"{flag} must remain false")

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    local_results = evidence.get("local_public_shell_results", {})
    for flag in [
        "first_user_test_plan_available",
        "feedback_form_available",
        "success_criteria_available",
        "pilot_result_template_available",
        "pilot_session_protocol_available",
    ]:
        require(local_results.get(flag) is True, f"local result {flag} must be true")
    require(local_results.get("pilot_sessions_completed") == 0, "pilot count must be 0")
    for flag in [
        "pilot_results_recorded",
        "customer_permission_recorded",
        "customer_contacted",
        "customer_validated",
        "product_market_fit_claimed",
        "revenue_validated",
        "production_readiness_claimed",
        "user_upload_enabled",
        "customer_data_processing_ready",
        "external_calls_made",
    ]:
        require(local_results.get(flag) is False, f"local result {flag} must be false")

    readiness = evaluate_production_customer_validation_evidence(
        load_settings(
            {"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(OUTPUT_PATH)}
        )
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    for flag in [
        "pilot_results_evidence_complete",
        "customer_value_evidence_complete",
        "claim_permission_evidence_complete",
        "boundary_review_evidence_complete",
        "customer_validation_evidence_complete",
        "production_customer_validation_ready",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")
    for flag in [
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
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_CUSTOMER_VALIDATION_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "customer_validation_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_customer_validation_review_packet",
        "first_user_test_plan_available: true",
        "pilot_sessions_completed: 0",
        "real_customer_or_target_user_feedback_recorded: false",
        "permission_to_use_feedback_recorded: false",
        "customer_validation_evidence_complete: false",
        "production_customer_validation_ready: false",
        "customer_validated: false",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_RUNNER_V0_1.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json",
        "/scripts/saee_customer_validation_evidence_runner.py",
        "/scripts/saee_customer_validation_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("customer_validation_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "customer_validation_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_customer_validation_review_packet",
        "first_user_test_plan_available": True,
        "feedback_form_available": True,
        "success_criteria_available": True,
        "pilot_result_template_available": True,
        "pilot_sessions_completed": 0,
        "real_customer_or_target_user_feedback_recorded": False,
        "permission_to_use_feedback_recorded": False,
        "customer_validation_evidence_complete": False,
        "production_customer_validation_ready": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "customer_data_collected": False,
        "user_upload_enabled": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "paid_pilot_completed": False,
        "blockers_closed_by_default": 0,
    }
    for flag, expected_value in expected.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index {flag} must be {expected_value}",
        )

    print(
        "SAEE_CUSTOMER_VALIDATION_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "production_customer_validation_ready=false "
        "customer_validated=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
