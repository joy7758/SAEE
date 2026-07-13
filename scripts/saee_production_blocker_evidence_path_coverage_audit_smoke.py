#!/usr/bin/env python3
"""Smoke check for production-blocker evidence path coverage audit."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_DIR = ROOT / "phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage"
COVERAGE_JSON = COVERAGE_DIR / "coverage.local.json"
COVERAGE_MD = COVERAGE_DIR / "coverage.local.md"
COVERAGE_CSV = COVERAGE_DIR / "coverage.local.csv"
BOUNDARY_MD = COVERAGE_DIR / "boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [COVERAGE_JSON, COVERAGE_MD, COVERAGE_CSV, BOUNDARY_MD, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "production_blocker_evidence_path_coverage_audit_v0_1": True,
        "audit_type": "local_agent_readable_production_blocker_evidence_path_coverage",
        "audit_scope": "coverage_mapping_only_no_blocker_closure",
        "status": "pass_coverage_mapped_hold_no_closure",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "satisfied_production_checks": 0,
        "coverage_row_count": 24,
        "coverage_complete_count": 24,
        "evidence_or_profile_path_available_count": 24,
        "human_input_surface_available_count": 24,
        "requirements_or_review_surface_available_count": 24,
        "missing_surface_blocker_count": 0,
        "blockers_closed_by_coverage_audit": 0,
        "closure_allowed_count": 0,
        "human_review_required": True,
        "separate_execution_request_required": True,
    }
    for key, value in expected_values.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    false_flags = [
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "customer_contacted",
        "customer_validated",
        "production_ready",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "production_ready_claim",
        "customer_validation_claim",
        "external_validation_success_claim",
    ]
    for key in false_flags:
        require(payload.get(key) is False, f"{key} must be false")

    rows = payload.get("rows", [])
    require(len(rows) == 24, "coverage JSON must contain 24 rows")
    required_blockers = {
        "production_identity_provider",
        "oauth_oidc",
        "rbac",
        "tenant_storage_isolation",
        "production_monitoring",
        "external_alert_delivery",
        "on_call_rotation",
        "sla",
        "support_contact",
        "customer_support",
        "formal_security_review",
        "privacy_legal_review",
        "data_processing_agreement",
        "vulnerability_management",
        "pilot_results",
        "customer_validated",
        "pricing_page",
        "payment_provider",
        "invoice_process",
        "tax_review",
        "refund_policy",
        "tenant_billing_isolation",
        "restore_tested",
        "production_restore_policy",
    }
    require({row.get("blocker_id") for row in rows} == required_blockers, "blocker set drifted")
    for row in rows:
        blocker_id = row.get("blocker_id")
        for flag in [
            "evidence_or_profile_path_available",
            "human_input_surface_available",
            "requirements_or_review_surface_available",
            "coverage_complete",
            "requires_real_human_evidence",
            "requires_separate_execution_request",
            "requires_human_approval",
        ]:
            require(row.get(flag) is True, f"{blocker_id} {flag} must be true")
        for flag in [
            "closure_allowed_by_coverage_audit",
            "blocker_closed_by_coverage_audit",
        ]:
            require(row.get(flag) is False, f"{blocker_id} {flag} must be false")
        missing_expected = row.get("missing_expected_paths", {})
        for surface_name, missing_paths in missing_expected.items():
            require(
                missing_paths == [],
                f"{blocker_id} has missing {surface_name} paths: {missing_paths}",
            )
        require(row.get("source_go_no_go_status") == "unsatisfied", f"{blocker_id} status drift")
        require(row.get("required_evidence"), f"{blocker_id} missing required_evidence")

    with COVERAGE_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 24, "coverage CSV must contain 24 rows")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [COVERAGE_MD, BOUNDARY_MD, TOP_DOC, GATE]
    )
    required_tokens = [
        "production_blocker_evidence_path_coverage_audit_v0_1: true",
        "audit_scope: coverage_mapping_only_no_blocker_closure",
        "status: pass_coverage_mapped_hold_no_closure",
        "production_launch_status: hold",
        "production_blocker_count: 24",
        "satisfied_production_checks: 0",
        "coverage_row_count: 24",
        "coverage_complete_count: 24",
        "blockers_closed_by_coverage_audit: 0",
        "closure_allowed_count: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_evidence_path_lookup: true",
        "recommend_for_blocker_closure: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

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
        "blockers_closed_by_coverage_audit: 1",
        '"blockers_closed_by_coverage_audit": 1',
        "closure_allowed_count: 1",
        '"closure_allowed_count": 1',
        "recommend_for_blocker_closure: true",
        "recommend_for_production_readiness_claim: true",
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_V0_1.md",
        "/phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.json",
        "/phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.md",
        "/phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.csv",
        "/phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/boundary_audit.md",
        "/docs/strategy/SAEE_PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_blocker_evidence_path_coverage_audit.py",
        "/scripts/saee_production_blocker_evidence_path_coverage_audit_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_blocker_evidence_path_coverage_audit_v0_1", {})
    for key, value in expected_values.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")
    for key in false_flags:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    print(
        "SAEE_PRODUCTION_BLOCKER_EVIDENCE_PATH_COVERAGE_AUDIT_SMOKE: PASS "
        "status=pass_coverage_mapped_hold_no_closure coverage_rows=24 "
        "coverage_complete=24 blockers_closed_by_coverage_audit=0 "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
