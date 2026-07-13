#!/usr/bin/env python3
"""Smoke check for SAEE Phase 5 customer validation/launch gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit/phase_5_customer_validation_launch_gap_audit.local.json"
)
REPORT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit/phase_5_customer_validation_launch_gap_audit.md"
)
CSV_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit/phase_5_customer_validation_launch_gap_audit.csv"
)
README_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit/README.md"
)
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    print(
        f"SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT_SMOKE: FAIL {message}",
        file=sys.stderr,
    )
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [AUDIT_PATH, REPORT_PATH, CSV_PATH, README_PATH, DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    require(
        audit.get("audit_type") == "saee_phase_5_customer_validation_launch_gap_audit",
        "wrong audit type",
    )
    require(
        audit.get("audit_scope")
        == "local_public_shell_to_production_customer_validation_launch_gap_review",
        "wrong audit scope",
    )
    require(
        audit.get("phase_id") == "phase_5_customer_validation_and_launch_review",
        "wrong phase",
    )
    require(audit.get("target_blocker_count") == 2, "expected 2 blockers")
    require(audit.get("required_evidence_item_count") == 12, "expected 12 items")
    require(audit.get("local_public_shell_present_count") == 1, "expected 1 local item")
    require(
        audit.get("missing_production_evidence_count") == 11,
        "expected 11 missing production evidence items",
    )
    require(audit.get("accepted_for_blocker_closure_count") == 0, "must accept zero closures")
    require(audit.get("blockers_ready_to_close") == [], "no blocker can be ready to close")
    require(audit.get("blockers_closed_by_audit") == 0, "must close zero blockers")
    require(audit.get("human_review_required") is True, "human review required")
    require(audit.get("execution_authorized") is False, "must not authorize execution")
    require(
        audit.get("evidence_collection_authorized") is False,
        "must not authorize evidence collection",
    )

    for flag in [
        "customer_contacted_by_codex",
        "automated_customer_contact",
        "unsolicited_customer_contact",
        "codex_executed_pilot",
        "pilot_session_started",
        "pilot_session_completed",
        "pilot_results_recorded",
        "feedback_form_completed",
        "customer_data_collected",
        "customer_data_processing_started",
        "customer_secrets_collected",
        "permission_to_use_feedback_recorded",
        "public_validation_claim_published",
        "case_study_published",
        "testimonial_published",
        "product_market_fit_claimed",
        "production_readiness_claimed",
        "customer_validated",
        "product_launched",
        "launch_approved",
        "public_launch_claim_added",
        "production_ready",
        "revenue_validated",
        "user_upload_enabled",
        "public_sdk_released",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
    ]:
        require(audit.get(flag) is False, f"{flag} must be false")

    local_go = audit.get("local_profile_go_no_go", {})
    require(local_go.get("commercial_status") == "hold", "local profile must hold")
    require(local_go.get("production_launch_status") == "hold", "production launch must hold")
    require(local_go.get("boundary_violation_count") == 0, "boundary violations must be zero")
    require(local_go.get("satisfied_production_checks") == 0, "local profile must satisfy zero production checks")
    require(local_go.get("production_blocker_count") == 24, "24 production blockers remain open")
    require(local_go.get("total_production_checks") == 24, "24 production checks expected")
    require(
        local_go.get("local_public_shell_review_candidate_count") == 1,
        "one local public-shell review candidate expected",
    )

    required_blockers = {"pilot_results", "customer_validated"}
    require(set(audit.get("target_blockers", [])) == required_blockers, "target blockers changed")
    summary_ids = {row.get("blocker_id") for row in audit.get("blocker_summary", [])}
    require(required_blockers <= summary_ids, "missing blocker summaries")
    require(len(audit.get("gap_rows", [])) == 12, "expected 12 gap rows")
    require(len(audit.get("blocker_summary", [])) == 2, "expected 2 blocker summaries")

    for row in audit.get("gap_rows", []):
        require(row.get("accepted_for_blocker_closure") is False, "row closes blocker")
        require(row.get("human_review_required") is True, "row must require review")
        require(
            row.get("external_dependency_required") is True,
            "phase 5 rows require external or human customer evidence",
        )
        require(
            row.get("engineering_implementation_required") is False,
            "phase 5 rows should not be engineering implementation tasks",
        )

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [REPORT_PATH, README_PATH, DOC_PATH, GATE_PATH]
    )
    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "customer_contacted_by_codex: true",
        "codex_executed_pilot: true",
        "pilot_session_completed: true",
        "pilot_results_recorded: true",
        "customer_data_collected: true",
        "public_validation_claim_published: true",
        "case_study_published: true",
        "testimonial_published: true",
        "product_market_fit_claimed: true",
        "launch_approved: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_execution_authorization: true",
        "recommend_for_customer_contact: true",
        "recommend_for_pilot_execution: true",
        "recommend_for_customer_validation_claim: true",
        "recommend_for_case_study_publication: true",
        "recommend_for_testimonial_publication: true",
        "recommend_for_product_market_fit_claim: true",
        "recommend_for_launch_approval: true",
        "blockers_closed_by_audit: 1",
        "accepted_for_blocker_closure_count: 1",
        "execution_authorized: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    print(
        "SAEE_PHASE5_CUSTOMER_VALIDATION_LAUNCH_GAP_AUDIT_SMOKE: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        f"production_ready={str(audit['production_ready']).lower()}"
    )


if __name__ == "__main__":
    main()
