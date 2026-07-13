#!/usr/bin/env python3
"""Smoke check for SAEE Phase 3 support/security/legal gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit/phase_3_support_security_legal_gap_audit.local.json"
)
REPORT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit/phase_3_support_security_legal_gap_audit.md"
)
CSV_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit/phase_3_support_security_legal_gap_audit.csv"
)
README_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit/README.md"
)
DOC_PATH = (
    ROOT / "phase_b_product/commercial_readiness/PHASE_3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    print(
        f"SAEE_PHASE3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT_SMOKE: FAIL {message}",
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
        audit.get("audit_type") == "saee_phase_3_support_security_legal_gap_audit",
        "wrong audit type",
    )
    require(
        audit.get("audit_scope")
        == "local_public_shell_to_production_support_security_legal_gap_review",
        "wrong audit scope",
    )
    require(audit.get("phase_id") == "phase_3_support_security_legal", "wrong phase")
    require(audit.get("target_blocker_count") == 7, "expected 7 blockers")
    require(audit.get("required_evidence_item_count") == 45, "expected 45 items")
    require(audit.get("local_public_shell_present_count") == 10, "expected 10 local items")
    require(
        audit.get("missing_production_evidence_count") == 35,
        "expected 35 missing production evidence items",
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
        "support_vendor_contacted_by_codex",
        "support_contact_published",
        "customer_support_activated",
        "sla_approved",
        "security_reviewer_contacted_by_codex",
        "formal_security_review_completed",
        "privacy_legal_review_completed",
        "legal_counsel_contacted_by_codex",
        "dpa_approved",
        "dpa_sent_to_customer",
        "vulnerability_management_activated",
        "security_contact_published",
        "customer_data_processed",
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
        "customer_contacted",
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

    required_blockers = {
        "support_contact",
        "customer_support",
        "sla",
        "formal_security_review",
        "privacy_legal_review",
        "data_processing_agreement",
        "vulnerability_management",
    }
    require(set(audit.get("target_blockers", [])) == required_blockers, "target blockers changed")
    summary_ids = {row.get("blocker_id") for row in audit.get("blocker_summary", [])}
    require(required_blockers <= summary_ids, "missing blocker summaries")
    for row in audit.get("gap_rows", []):
        require(row.get("accepted_for_blocker_closure") is False, "row closes blocker")
        require(row.get("human_review_required") is True, "row must require review")
        require(row.get("external_dependency_required") is True, "phase 3 rows require external evidence")

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
        "recommend_for_blocker_closure: true",
        "recommend_for_execution_authorization: true",
        "recommend_for_support_activation: true",
        "recommend_for_sla_approval: true",
        "recommend_for_security_review_claim: true",
        "recommend_for_legal_review_claim: true",
        "recommend_for_dpa_use: true",
        "recommend_for_vulnerability_management_activation: true",
        "blockers_closed_by_audit: 1",
        "accepted_for_blocker_closure_count: 1",
        "execution_authorized: true",
        "support_contact_published: true",
        "customer_support_activated: true",
        "sla_approved: true",
        "dpa_approved: true",
        "vulnerability_management_activated: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    print(
        "SAEE_PHASE3_SUPPORT_SECURITY_LEGAL_GAP_AUDIT_SMOKE: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        f"production_ready={str(audit['production_ready']).lower()}"
    )


if __name__ == "__main__":
    main()
