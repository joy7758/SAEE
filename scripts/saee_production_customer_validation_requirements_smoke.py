#!/usr/bin/env python3
"""Smoke check for SAEE Production Customer Validation Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT / "phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.json"
)
MD_PATH = (
    ROOT / "phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.md"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_customer_validation_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")

    false_flags = [
        "production_customer_validation_implemented",
        "customer_validation_evidence_collected",
        "pilot_results_recorded",
        "customer_permission_recorded",
        "customer_contacted",
        "customer_validated",
        "product_market_fit_claimed",
        "revenue_validated",
        "production_readiness_claimed",
        "user_upload_enabled",
        "customer_data_processing_ready",
        "production_customer_validation_ready",
        "product_launched",
        "production_ready",
        "public_sdk_released",
        "private_core_exposed",
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_data_collected",
        "customer_secrets_collected",
    ]
    for flag in false_flags:
        require(data[flag] is False, f"{flag} false")
    require(data["pilot_sessions_completed"] == 0, "pilot sessions zero")

    blockers = set(data["validation_blockers_covered_as_requirements"])
    require(blockers == {"pilot_results", "customer_validated"}, "validation blockers mismatch")

    required_controls = {
        "human_approved_pilot_session_protocol",
        "target_user_profile_defined",
        "neutral_demo_script_used",
        "consent_and_permission_recorded",
        "feedback_form_completed",
        "success_criteria_applied",
        "pilot_result_reviewed",
        "negative_feedback_recorded",
        "no_private_core_disclosed",
        "no_customer_secrets_collected",
    }
    require(
        required_controls <= set(data["required_pilot_evidence_controls"]),
        "missing pilot evidence controls",
    )

    required_validation_evidence = {
        "customer_role_and_segment_recorded",
        "permission_to_use_feedback_recorded",
        "pain_point_fit_observed",
        "deployment_decision_value_observed",
        "recommendation_output_understood",
        "failure_summary_usefulness_observed",
        "go_hold_pivot_decision_recorded",
        "claim_scope_reviewed",
        "reviewer_approved_validation_claim",
    }
    require(
        required_validation_evidence <= set(data["required_customer_validation_evidence"]),
        "missing customer validation evidence",
    )

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_customer_validation_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_customer_validation_implemented: false",
        "customer_validation_evidence_collected: false",
        "pilot_results_recorded: false",
        "pilot_sessions_completed: 0",
        "customer_permission_recorded: false",
        "customer_contacted: false",
        "customer_validated: false",
        "product_market_fit_claimed: false",
        "revenue_validated: false",
        "production_readiness_claimed: false",
        "user_upload_enabled: false",
        "customer_data_processing_ready: false",
        "production_customer_validation_ready: false",
        "product_launched: false",
        "production_ready: false",
        "private_core_exposed: false",
        "customer_data_collected: false",
        "customer_secrets_collected: false",
        "answer: conditional",
        "recommend_for_requirements_definition: true",
        "recommend_for_customer_validation_claim: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_customer_validation_requirements.py",
        "/scripts/saee_production_customer_validation_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_customer_validation_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_customer_validation_requirements_v0_1": True,
        "production_customer_validation_implemented": False,
        "customer_validation_evidence_collected": False,
        "pilot_results_recorded": False,
        "pilot_sessions_completed": 0,
        "customer_permission_recorded": False,
        "customer_contacted": False,
        "customer_validated": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "user_upload_enabled": False,
        "customer_data_processing_ready": False,
        "production_customer_validation_ready": False,
        "product_launched": False,
        "production_ready": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
        "customer_data_collected": False,
        "customer_secrets_collected": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true pilot_results_recorded=false "
        "customer_validated=false customer_contacted=false "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
