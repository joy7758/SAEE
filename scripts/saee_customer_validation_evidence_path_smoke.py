#!/usr/bin/env python3
"""Smoke check for the SAEE customer-validation evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_customer_validation_evidence import (
    evaluate_production_customer_validation_evidence,
)
from scripts.saee_customer_validation_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    FIXTURE_EVIDENCE_PATH,
    FIXTURE_INPUT_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_customer_validation_evidence_path.py"
TARGET_BLOCKERS = ["pilot_results", "customer_validated"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CUSTOMER_VALIDATION_EVIDENCE_PATH_SMOKE: FAIL: " + message)


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    run = subprocess.run(
        [sys.executable, str(RUNNER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    result = json.loads(run.stdout)
    expected = {
        "customer_validation_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_customer_validation_evidence_path",
        "path_status": "pass_fixture_only",
        "fixture_only": True,
        "real_pilot_session_completed": False,
        "real_customer_feedback_collected": False,
        "real_permission_to_use_feedback_recorded": False,
        "real_customer_validation_approved": False,
        "real_customer_validation_claim_published": False,
        "real_customer_contacted": False,
        "real_customer_data_collected": False,
        "customer_validation_readiness_status_after_fixture": "pass",
        "pilot_results_evidence_complete_after_fixture": True,
        "customer_value_evidence_complete_after_fixture": True,
        "claim_permission_evidence_complete_after_fixture": True,
        "boundary_review_evidence_complete_after_fixture": True,
        "customer_validation_evidence_complete_after_fixture": True,
        "production_customer_validation_ready_after_fixture": True,
        "customer_validation_blocker_path_proven": True,
        "customer_validation_target_blockers_satisfied_count_after_fixture": 2,
        "commercial_status_after_fixture": "hold",
        "production_launch_status_after_fixture": "hold",
        "satisfied_production_checks_after_fixture": 2,
        "total_production_checks_after_fixture": 24,
        "production_blocker_count_after_fixture": 22,
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
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
        "human_real_evidence_required": True,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
    }
    for flag, expected_value in expected.items():
        require(result.get(flag) == expected_value, f"{flag} must be {expected_value}")
    require(
        result["customer_validation_target_blockers_satisfied_by_fixture"]
        == TARGET_BLOCKERS,
        "target blockers changed",
    )
    require(
        result["customer_validation_target_blockers_unsatisfied_by_fixture"] == [],
        "no target blockers should be unsatisfied in fixture",
    )

    for path in [DEFAULT_OUTPUT_PATH, FIXTURE_INPUT_PATH, FIXTURE_EVIDENCE_PATH]:
        require(path.exists(), f"{path} missing")
        json.loads(path.read_text(encoding="utf-8"))
    require(json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8")) == result, "persisted result differs")

    readiness = evaluate_production_customer_validation_evidence(
        load_settings(
            {"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(FIXTURE_EVIDENCE_PATH)}
        )
    )
    require(readiness["status"] == "pass", "fixture evidence readiness must pass")
    require(
        readiness["customer_validation_evidence_complete"] is True,
        "fixture evidence must be complete",
    )
    require(
        readiness["production_customer_validation_ready"] is True,
        "fixture evidence readiness must be true for path proof",
    )
    require(readiness["customer_validated"] is False, "readiness must not claim customer_validated")
    require(readiness["production_ready"] is False, "readiness must not claim production_ready")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "customer_validation_evidence_path_v0_1: true",
        "path_type: local_fixture_only_customer_validation_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_pilot_session_completed: false",
        "real_customer_feedback_collected: false",
        "real_permission_to_use_feedback_recorded: false",
        "real_customer_validation_approved: false",
        "real_customer_validation_claim_published: false",
        "real_customer_contacted: false",
        "real_customer_data_collected: false",
        "customer_validation_readiness_status_after_fixture: pass",
        "pilot_results_evidence_complete_after_fixture: true",
        "customer_value_evidence_complete_after_fixture: true",
        "claim_permission_evidence_complete_after_fixture: true",
        "boundary_review_evidence_complete_after_fixture: true",
        "customer_validation_evidence_complete_after_fixture: true",
        "production_customer_validation_ready_after_fixture: true",
        "customer_validation_blocker_path_proven: true",
        "customer_validation_target_blockers_satisfied_count_after_fixture: 2",
        "production_blocker_count_after_fixture: 22",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_customer_validation_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_validation_claim: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    for token in [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "real_pilot_session_completed: true",
        "\"real_pilot_session_completed\": true",
        "real_customer_feedback_collected: true",
        "\"real_customer_feedback_collected\": true",
        "real_permission_to_use_feedback_recorded: true",
        "\"real_permission_to_use_feedback_recorded\": true",
        "real_customer_validation_approved: true",
        "\"real_customer_validation_approved\": true",
        "real_customer_validation_claim_published: true",
        "\"real_customer_validation_claim_published\": true",
        "real_customer_contacted: true",
        "\"real_customer_contacted\": true",
        "real_customer_data_collected: true",
        "\"real_customer_data_collected\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "public_validation_claim_published: true",
        "\"public_validation_claim_published\": true",
        "testimonial_published: true",
        "\"testimonial_published\": true",
        "case_study_published: true",
        "\"case_study_published\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_validation_claim: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path_report.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.fixture_input.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.fixture_evidence.local.json",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_customer_validation_evidence_path.py",
        "/scripts/saee_customer_validation_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("customer_validation_evidence_path_v0_1", {})
    expected_index = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_customer_validation_evidence_path",
        "fixture_only": True,
        "real_pilot_session_completed": False,
        "real_customer_feedback_collected": False,
        "real_permission_to_use_feedback_recorded": False,
        "real_customer_validation_approved": False,
        "real_customer_validation_claim_published": False,
        "real_customer_contacted": False,
        "real_customer_data_collected": False,
        "customer_validation_blocker_path_proven": True,
        "pilot_results_evidence_complete_after_fixture": True,
        "customer_value_evidence_complete_after_fixture": True,
        "claim_permission_evidence_complete_after_fixture": True,
        "boundary_review_evidence_complete_after_fixture": True,
        "customer_validation_evidence_complete_after_fixture": True,
        "production_customer_validation_ready_after_fixture": True,
        "customer_validation_target_blockers_satisfied_count_after_fixture": 2,
        "production_blocker_count_after_fixture": 22,
        "blockers_closed_by_path": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
    }
    for flag, expected_value in expected_index.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index customer_validation_evidence_path_v0_1 {flag} must be {expected_value}",
        )

    print("SAEE_CUSTOMER_VALIDATION_EVIDENCE_PATH_SMOKE: PASS")


if __name__ == "__main__":
    main()
