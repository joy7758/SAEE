#!/usr/bin/env python3
"""Smoke check for the commercial readiness state consistency audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_state_consistency_audit"
AUDIT_JSON = AUDIT_DIR / "commercial_readiness_state_consistency_audit.local.json"
AUDIT_MD = AUDIT_DIR / "commercial_readiness_state_consistency_audit.md"
BOUNDARY_MD = AUDIT_DIR / "commercial_readiness_state_consistency_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT_SMOKE: FAIL: "
            + message
        )


def main() -> None:
    require(AUDIT_JSON.exists(), "audit JSON must exist")
    payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    for path in [AUDIT_MD, BOUNDARY_MD, TOP_DOC, GATE]:
        require(path.exists(), f"{path} must exist")

    expected = {
        "commercial_readiness_state_consistency_audit_v0_1": True,
        "audit_type": "local_agent_readable_commercial_state_consistency",
        "status": "pass_consistent_hold_state",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "satisfied_production_checks": 0,
        "missing_value_row_count": 0,
        "lane_reconciliation_status": "pass_parallel_lanes_documented",
        "human_input_lane_split_documented": True,
        "parallel_human_input_lane_count": 2,
        "primary_human_input_lane": "commercial_sprint_workbook_import_approval_review",
        "primary_human_input_blocker_id": "workbook_import_approval",
        "preferred_human_input_path": "workbook_import_approval_request",
        "preferred_template_missing_value_row_count": 0,
        "related_human_sequence_lane": "support_contact_owner_assignment",
        "related_human_sequence_blocker_id": "support_contact",
        "strategic_sprint_candidate_blocker_id": "formal_security_review",
        "external_calibration_status": "completed_with_human_results_hold",
        "external_calibration_records_entered": 6,
        "external_calibration_validation_status": "hold",
        "external_calibration_human_results_imported": True,
        "external_validation_success_claim": False,
        "internal_self_play_status": "pass",
        "full_manual_external_test_completed": False,
        "codex_external_calls_made": False,
        "browser_automation_used": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "workbook_import_authorized": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "failed_check_count": 0,
        "contradiction_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(payload.get("failed_checks") == [], "failed checks must be empty")
    require(payload.get("contradictions") == [], "contradictions must be empty")
    require(len(payload.get("checks", [])) >= 60, "audit must include broad state checks")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [AUDIT_MD, BOUNDARY_MD, TOP_DOC, GATE]
    )
    required_tokens = [
        "status: pass_consistent_hold_state",
        "commercial_status: hold",
        "external_calibration_status: completed_with_human_results_hold",
        "external_calibration_validation_status: hold",
        "external_validation_success_claim: false",
        "internal_self_play_status: pass",
        "lane_reconciliation_status: pass_parallel_lanes_documented",
        "human_input_lane_split_documented: true",
        "primary_human_input_lane: commercial_sprint_workbook_import_approval_review",
        "related_human_sequence_lane: support_contact_owner_assignment",
        "strategic_sprint_candidate_blocker_id: formal_security_review",
        "workbook import approval",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_state_lookup: true",
        "recommend_for_formal_launch_decision: false",
        "recommend_for_external_validation_success_claim: false",
    ]
    for token in required_tokens:
        require(token in combined, f"missing doc token: {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "external_validation_success_claim: true",
        '"external_validation_success_claim": true',
        "recommend_for_formal_launch_decision: true",
        "recommend_for_production_readiness_claim: true",
        "recommend_for_external_validation_success_claim: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_READINESS_STATE_CONSISTENCY_AUDIT_SMOKE: PASS "
        f"status={payload['status']} "
        f"external_calibration_status={payload['external_calibration_status']} "
        "production_ready=false external_validation_success_claim=false"
    )


if __name__ == "__main__":
    main()
