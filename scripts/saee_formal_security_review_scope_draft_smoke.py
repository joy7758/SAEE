#!/usr/bin/env python3
"""Smoke check for the SAEE formal security review scope draft."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_V0_1.md"
)
DRAFT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "formal_security_review_scope_draft.local.json"
)
DRAFT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "formal_security_review_scope_draft.md"
)
BOUNDARY_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "formal_security_review_scope_draft_boundary_audit.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_SMOKE: FAIL " + message
        )


def main() -> int:
    for path in [TOP_DOC, DRAFT_JSON, DRAFT_MD, BOUNDARY_AUDIT, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    draft = json.loads(DRAFT_JSON.read_text(encoding="utf-8"))
    expected = {
        "draft_type": "saee_formal_security_review_scope_draft",
        "draft_version": "v0.1",
        "draft_status": "draft_not_approved",
        "review_scope": "formal_security_review_scope_draft_for_human_review_only",
        "blocker_target": "formal_security_review",
        "draft_scope_available": True,
        "human_review_required": True,
        "separate_review_execution_approval_required": True,
        "blocker_closure_allowed_by_draft": False,
        "formal_security_review_completed": False,
        "formal_security_review_report_available": False,
        "security_reviewer_assigned": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "penetration_test_completed": False,
        "dependency_review_completed": False,
        "review_findings_triaged": False,
        "remediation_plan_approved": False,
        "production_security_ready": False,
        "production_privacy_security_legal_ready": False,
        "customer_data_processing_approved": False,
        "customer_data_processed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "private_core_inspected": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "production_ready": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(draft.get(key) == expected_value, f"{key} must be {expected_value}")

    required_sections = {
        "review_authority_and_approval",
        "review_object_and_asset_inventory",
        "public_shell_threat_model_review",
        "authentication_authorization_review",
        "tenant_boundary_review",
        "data_operations_backup_restore_review",
        "dependency_and_supply_chain_review_plan",
        "vulnerability_management_handoff",
        "private_core_exclusion",
        "customer_data_exclusion",
        "findings_triage_process",
        "remediation_acceptance_boundary",
        "approval_record",
    }
    require(required_sections <= set(draft.get("scope_sections", [])), "missing scope sections")
    require(len(draft.get("review_areas", [])) >= 4, "expected review areas")
    for area in draft.get("review_areas", []):
        require(area.get("private_core_in_scope") is False, "private core must be out of scope")

    combined = "\n".join(
        [
            TOP_DOC.read_text(encoding="utf-8"),
            DRAFT_MD.read_text(encoding="utf-8"),
            BOUNDARY_AUDIT.read_text(encoding="utf-8"),
            GATE.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "formal_security_review_scope_draft_v0_1: true",
        "draft_type: saee_formal_security_review_scope_draft",
        "draft_status: draft_not_approved",
        "review_scope: formal_security_review_scope_draft_for_human_review_only",
        "blocker_closure_allowed_by_draft: false",
        "formal_security_review_completed: false",
        "formal_security_review_report_available: false",
        "security_vendor_contacted: false",
        "penetration_test_completed: false",
        "dependency_review_completed: false",
        "review_findings_triaged: false",
        "production_security_ready: false",
        "production_ready: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_scope_review: true",
        "recommend_for_formal_security_review_claim: false",
        "recommend_for_review_execution: false",
        "recommend_for_security_vendor_contact: false",
        "recommend_for_penetration_test: false",
        "recommend_for_blocker_closure: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing tokens: " + ", ".join(missing))

    forbidden_tokens = [
        "formal_security_review_completed: true",
        '"formal_security_review_completed": true',
        "formal_security_review_report_available: true",
        '"formal_security_review_report_available": true',
        "security_vendor_contacted: true",
        '"security_vendor_contacted": true',
        "penetration_test_completed: true",
        '"penetration_test_completed": true',
        "dependency_review_completed: true",
        '"dependency_review_completed": true',
        "review_findings_triaged: true",
        '"review_findings_triaged": true',
        "production_security_ready: true",
        '"production_security_ready": true',
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "recommend_for_blocker_closure: true",
        "recommend_for_review_execution: true",
        "recommend_for_formal_security_review_claim: true",
        "recommend_for_production_readiness_claim: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_scope_draft.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_scope_draft.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_scope_draft_boundary_audit.md",
        "/docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_RECOMMENDATION_GATE.md",
        "/scripts/saee_formal_security_review_scope_draft.py",
        "/scripts/saee_formal_security_review_scope_draft_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("formal_security_review_scope_draft_v0_1", {})
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_SMOKE: PASS "
        "draft_not_approved=true formal_security_review_completed=false "
        "production_ready=false private_core_exposed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
