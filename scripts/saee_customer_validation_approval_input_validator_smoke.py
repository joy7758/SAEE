#!/usr/bin/env python3
"""Smoke check for the customer validation approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_customer_validation_evidence_builder import REVIEW_KEY_GROUPS
from scripts.saee_customer_validation_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)


VALIDATOR_SCRIPT = ROOT / "scripts/saee_customer_validation_approval_input_validator.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    session_boundary_flags = {
        "secrets_collected": False,
        "production_data_collected": False,
        "customer_data_uploaded": False,
        "private_core_disclosed": False,
        "production_ready_claim_made": False,
    }
    if unsafe:
        session_boundary_flags["private_core_disclosed"] = True
    return {
        "customer_validation_evidence_input_v0_1": True,
        "pilot_result_template_v0_1": True,
        "boundary_note": "Fixture-only validator smoke input.",
        "aggregate_metrics": {
            "session_count": 1,
            "understanding_rate": 4.5,
            "trust_rate": 4.2,
            "decision_influence_rate": 4.0,
            "repeat_usage_intent": 4.0,
            "go_hold_pivot": "go",
        },
        "evidence_review": {key: True for key in REVIEW_KEY_GROUPS},
        "sessions": [
            {
                "session_id": "PILOT-20260705-001",
                "session_date": "2026-07-05",
                "participant_role": "AI platform owner",
                "team_type": "enterprise_ai_platform",
                "current_evaluation_method": "manual spreadsheet and trace review",
                "saee_demo_surface_used": "local_mvp_demo",
                "candidate_count": 3,
                "understanding_score": 5,
                "trust_score": 4,
                "decision_influence_score": 4,
                "repeat_usage_intent_score": 4,
                "willing_to_test_own_candidates": True,
                "time_to_value_minutes": 12,
                "top_objection": "Needs production evidence before buying.",
                "evidence_missing": "No customer deployment evidence yet.",
                "notes": "Fixture-only validator smoke session.",
                "boundary_flags": session_boundary_flags,
            }
        ],
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
        "customer_contacted": False,
    }


def main() -> None:
    require(VALIDATOR_SCRIPT.exists(), "validator script missing")
    default_run = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    expected_default = {
        "validator_type": "saee_customer_validation_approval_input_validator",
        "validation_status": "hold",
        "input_complete": False,
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "pilot_results_recorded_by_validator": False,
        "customer_validation_approved_by_validator": False,
        "customer_validation_claim_published_by_validator": False,
        "customer_validation_evidence_built_by_validator": False,
        "production_customer_validation_ready_by_validator": False,
        "codex_contacted_customer": False,
        "codex_executed_pilot": False,
        "codex_inferred_missing_results": False,
        "codex_collected_customer_data": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
    }
    for key, value in expected_default.items():
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(default_summary["missing_evidence_review"], "default input must miss review flags")
    require(default_summary["missing_completed_session"] is True, "default input misses session")
    require(DEFAULT_OUTPUT_PATH.exists(), "default validation output missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_input.json"
        unsafe_path = tmp / "unsafe_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)

    require(complete_summary["validation_status"] == "pass", "complete input must pass")
    require(complete_summary["input_complete"] is True, "complete input complete")
    require(complete_summary["builder_ready"] is True, "complete input builder ready")
    require(complete_summary["blockers_closed_by_validator"] == 0, "complete input closes no blockers")
    require(complete_summary["customer_validated"] is False, "complete input does not validate customer")
    require(unsafe_summary["validation_status"] == "stop", "unsafe input stops")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_summary["builder_ready"] is False, "unsafe input not builder ready")

    subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "customer_validation_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_customer_validation_input_pre_builder_check",
        "target_blocker_ids: pilot_results, customer_validated",
        "blockers_closed_by_validator: 0",
        "pilot_results_recorded_by_validator: false",
        "customer_validation_approved_by_validator: false",
        "customer_validation_claim_published_by_validator: false",
        "customer_validation_evidence_built_by_validator: false",
        "production_customer_validation_ready_by_validator: false",
        "codex_contacted_customer: false",
        "codex_executed_pilot: false",
        "codex_inferred_missing_results: false",
        "codex_collected_customer_data: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_customer_contact: false",
        "recommend_for_pilot_execution: false",
        "recommend_for_customer_validation_claim: false",
        "recommend_for_customer_validation_approval: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_market_fit_claim: false",
        "recommend_for_testimonial_publication: false",
        "recommend_for_case_study_publication: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_customer_validation_approval_input_validator.py",
        "/scripts/saee_customer_validation_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("customer_validation_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "hold",
        "validator_type": "saee_customer_validation_approval_input_validator",
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "pilot_results_recorded_by_validator": False,
        "customer_validation_approved_by_validator": False,
        "customer_validation_claim_published_by_validator": False,
        "production_customer_validation_ready_by_validator": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=hold builder_ready=false blockers_closed_by_validator=0 "
        "customer_validated=false"
    )


if __name__ == "__main__":
    main()
