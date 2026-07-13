#!/usr/bin/env python3
"""Smoke check for SAEE Production Customer Validation Evidence Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_customer_validation_evidence import (
    evaluate_production_customer_validation_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_SMOKE: FAIL: " + message
        )


def write_customer_validation_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "customer_validation_evidence_type": "production_customer_validation_evidence",
        "at_least_one_human_approved_pilot_session_completed": True,
        "pilot_result_template_completed": True,
        "feedback_form_completed": True,
        "success_criteria_applied": True,
        "boundary_flags_reviewed": True,
        "pilot_result_reviewed_by_human": True,
        "customer_role_and_segment_recorded": True,
        "pain_point_fit_observed": True,
        "deployment_decision_value_observed": True,
        "recommendation_output_understood": True,
        "failure_summary_usefulness_observed": True,
        "go_hold_pivot_decision_recorded": True,
        "real_customer_or_target_user_feedback_recorded": True,
        "permission_to_use_feedback_recorded": True,
        "customer_problem_fit_reviewed": True,
        "decision_usefulness_observed": True,
        "claim_scope_approved": True,
        "customer_validation_record_approved_by_human": True,
        "reviewer_approved_validation_claim": True,
        "no_private_core_disclosed": True,
        "no_customer_secrets_collected": True,
        "no_customer_upload_required": True,
        "no_production_ready_claim_added": True,
        "no_public_launch_claim_added": True,
        "negative_feedback_recorded": True,
        "production_ready": unsafe,
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
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "unsolicited_customer_contact": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "user_upload_enabled": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "paid_pilot_completed": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_customer_validation_evidence(load_settings({}))
    require(
        local["production_customer_validation_evidence_type"]
        == "production_customer_validation_evidence_readiness",
        "wrong evidence type",
    )
    require(
        local["production_customer_validation_evidence_readiness_v0_1"] is True,
        "readiness flag",
    )
    require(local["status"] == "hold", "default evidence status must hold")
    require(
        local["customer_validation_evidence_path_configured"] is False,
        "default path false",
    )
    for field in [
        "pilot_results_evidence_complete",
        "customer_value_evidence_complete",
        "claim_permission_evidence_complete",
        "boundary_review_evidence_complete",
        "customer_validation_evidence_complete",
        "production_customer_validation_ready",
    ]:
        require(local[field] is False, f"default {field} false")
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
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
        require(local[flag] is False, f"default {flag} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "CUSTOMER_VALIDATION_EVIDENCE.json"
        write_customer_validation_evidence(evidence_path)
        settings = load_settings(
            {
                "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(
                    evidence_path
                )
            }
        )
        configured = evaluate_production_customer_validation_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_CUSTOMER_VALIDATION_EVIDENCE.json"
        write_customer_validation_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_customer_validation_evidence(
            load_settings(
                {
                    "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(
                        unsafe_path
                    )
                }
            )
        )

    require(configured["status"] == "pass", "complete evidence should pass")
    for field in [
        "pilot_results_evidence_complete",
        "customer_value_evidence_complete",
        "claim_permission_evidence_complete",
        "boundary_review_evidence_complete",
        "customer_validation_evidence_complete",
        "production_customer_validation_ready",
    ]:
        require(configured[field] is True, f"configured {field} true")
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
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
        require(configured[flag] is False, f"configured {flag} false")

    blocked = blocker_ids(go_no_go)
    for blocker in ["pilot_results", "customer_validated"]:
        require(blocker not in blocked, f"{blocker} should be satisfied by evidence")
    require(
        go_no_go["production_customer_validation_evidence_status"] == "pass",
        "go/no-go should expose customer validation evidence pass",
    )
    for field in [
        "customer_validation_evidence_pilot_results_complete",
        "customer_validation_evidence_customer_value_complete",
        "customer_validation_evidence_claim_permission_complete",
        "customer_validation_evidence_boundary_review_complete",
        "customer_validation_evidence_complete",
    ]:
        require(go_no_go[field] is True, f"go/no-go {field} true")
    require(go_no_go["commercial_status"] == "hold", "evidence alone must not launch")
    require(
        go_no_go["production_launch_status"] == "hold",
        "production launch must still hold when other blockers remain",
    )
    require(go_no_go["production_ready"] is False, "go/no-go production false")
    require(go_no_go["customer_validated"] is False, "go/no-go customer false")
    require(go_no_go["product_launched"] is False, "go/no-go launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require(
        "production_ready" in unsafe["boundary_violations"],
        "unsafe evidence must detect boundary",
    )
    require(unsafe["production_ready"] is False, "unsafe output production false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join([doc, gate])
    for token in [
        "production_customer_validation_evidence_readiness_v0_1: true",
        "default_status: hold",
        "customer_validation_evidence_path_configured_default: false",
        "pilot_results_evidence_complete_default: false",
        "customer_value_evidence_complete_default: false",
        "claim_permission_evidence_complete_default: false",
        "boundary_review_evidence_complete_default: false",
        "customer_validation_evidence_complete_default: false",
        "production_customer_validation_ready_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "external_model_api_called: false",
        "external_ai_assistant_tested: false",
        "customer_contacted_by_codex: false",
        "automated_customer_contact: false",
        "user_upload_enabled: false",
        "customer_data_collected: false",
        "customer_secrets_collected: false",
        "product_market_fit_claimed: false",
        "revenue_validated: false",
        "public_validation_claim_published: false",
        "answer: conditional",
        "recommend_for_customer_validation_evidence_review: true",
        "recommend_for_customer_contact: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_customer_validation_evidence.py",
        "/scripts/saee_production_customer_validation_evidence_readiness.py",
        "/scripts/saee_production_customer_validation_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_customer_validation_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_customer_validation_evidence_readiness_hold",
        "production_customer_validation_evidence_readiness_v0_1": True,
        "customer_validation_evidence_path_configured_default": False,
        "pilot_results_evidence_complete_default": False,
        "customer_value_evidence_complete_default": False,
        "claim_permission_evidence_complete_default": False,
        "boundary_review_evidence_complete_default": False,
        "customer_validation_evidence_complete_default": False,
        "production_customer_validation_ready_default": False,
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
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "unsolicited_customer_contact": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "user_upload_enabled": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "paid_pilot_completed": False,
    }
    for key, expected_value in expected.items():
        require(
            entry.get(key) == expected_value,
            f"agent-index {key} must be {expected_value}",
        )

    print(
        "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "validation_blockers_satisfied_by_evidence=true production_launch_status=hold "
        "production_ready=false customer_validated=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
