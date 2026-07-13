#!/usr/bin/env python3
"""Smoke test the internal founder pilot evidence run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
SUMMARY_PATH = EVIDENCE_DIR / "internal_founder_pilot_evidence_run_summary.local.json"
INPUT_PATH = EVIDENCE_DIR / "customer_validation_evidence_input.internal_founder_pilot.local.json"
VALIDATION_PATH = EVIDENCE_DIR / "customer_validation_approval_input_validation.internal_founder_pilot.local.json"
VALIDATION_MD_PATH = EVIDENCE_DIR / "customer_validation_approval_input_validation.internal_founder_pilot.md"
EVIDENCE_PATH = EVIDENCE_DIR / "customer_validation_evidence.from_internal_founder_pilot.local.json"
REPORT_PATH = EVIDENCE_DIR / "internal_founder_pilot_evidence_run_report.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_INTERNAL_FOUNDER_PILOT_EVIDENCE_RUN_GATE.md"

REQUIRED_FILES = [
    SUMMARY_PATH,
    INPUT_PATH,
    VALIDATION_PATH,
    VALIDATION_MD_PATH,
    EVIDENCE_PATH,
    REPORT_PATH,
    GATE_PATH,
    ROOT / "scripts/saee_internal_founder_pilot_evidence_run.py",
]

EXPECTED_TRUE = {
    "internal_founder_pilot_evidence_run_v0_1": True,
    "internal_pilot_only": True,
    "pilot_results_evidence_complete": True,
    "customer_value_evidence_complete": True,
    "boundary_review_evidence_complete": True,
}

EXPECTED_FALSE = [
    "claim_permission_evidence_complete",
    "customer_validation_evidence_complete",
    "production_customer_validation_ready",
    "external_customer_validation_performed",
    "customer_validated",
    "production_ready",
    "product_launched",
    "customer_contacted",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "customer_data_collected",
    "customer_data_processing_started",
    "customer_secrets_collected",
    "public_validation_claim_published",
    "testimonial_published",
    "case_study_published",
    "revenue_validated",
]


def fail(message: str) -> None:
    raise SystemExit("SAEE_INTERNAL_FOUNDER_PILOT_EVIDENCE_RUN_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    summary = read_json(SUMMARY_PATH)
    evidence = read_json(EVIDENCE_PATH)
    validation = read_json(VALIDATION_PATH)

    expected_status = {
        "run_type": "internal_founder_self_test_pilot_evidence",
        "run_status": "pass",
        "validation_status": "pass",
        "customer_validation_input_validation_status": "hold",
        "customer_validation_readiness_status": "hold",
        "commercial_status_after_profile": "hold",
        "production_launch_status_after_profile": "hold",
    }
    for key, value in expected_status.items():
        if summary.get(key) != value:
            fail(f"summary {key} must be {value}")
    for key, value in EXPECTED_TRUE.items():
        if summary.get(key) is not value:
            fail(f"summary {key} must be {value}")
    for key in EXPECTED_FALSE:
        if summary.get(key) is not False:
            fail(f"summary {key} must be false")

    if summary.get("completed_session_count") != 1:
        fail("completed_session_count must be 1")
    if summary.get("all_evidence_production_blocker_count") != 1:
        fail("all_evidence_production_blocker_count must be 1")
    if summary.get("all_evidence_remaining_blockers") != ["customer_validated"]:
        fail("customer_validated must remain the only blocker")
    if "pilot_results" not in summary.get("all_evidence_satisfied_blockers", []):
        fail("pilot_results must be satisfied")
    if summary.get("blockers_closed_by_validator") != 0:
        fail("validator must close zero blockers directly")
    if summary.get("blockers_closed_by_builder") != 0:
        fail("builder must close zero blockers directly")
    if summary.get("blockers_closed_by_profile") != 0:
        fail("profile must close zero blockers directly")

    if evidence.get("completed_session_count") != 1:
        fail("evidence completed_session_count must be 1")
    if evidence.get("reviewer_approved_validation_claim") is not False:
        fail("evidence must not approve customer validation claim")
    if evidence.get("claim_scope_approved") is not False:
        fail("evidence must not approve claim scope")
    if validation.get("validation_status") != "hold":
        fail("validation must hold because public customer-validation claim is not approved")
    if validation.get("builder_ready") is not False:
        fail("validation builder_ready must remain false")

    print(
        "SAEE_INTERNAL_FOUNDER_PILOT_EVIDENCE_RUN_SMOKE: PASS "
        "pilot_results_evidence_complete=true remaining_blockers=1 "
        "customer_validated=false"
    )


if __name__ == "__main__":
    main()
