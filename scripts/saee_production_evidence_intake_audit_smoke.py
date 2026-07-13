#!/usr/bin/env python3
"""Smoke check for the SAEE production evidence intake audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_evidence_intake_audit import (
    INTAKE_SPECS,
    OUTPUT_JSON,
    OUTPUT_MD,
    README_PATH,
    main as run_audit,
)

COMBINED_DATA_OPS_EVIDENCE_PATH = (
    "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_data_operations_evidence.combined_profile.local.json"
)
COMBINED_OPERATIONS_EVIDENCE_PATH = (
    "phase_b_product/commercial_readiness/operations_evidence/"
    "production_operations_evidence.combined_profile.local.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_EVIDENCE_INTAKE_AUDIT_SMOKE: FAIL: " + message
        )


def main() -> None:
    run_audit()
    require(OUTPUT_JSON.exists(), "intake JSON must exist")
    require(OUTPUT_MD.exists(), "intake Markdown must exist")
    require(README_PATH.exists(), "intake README must exist")
    audit = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))

    require(
        audit.get("intake_audit_type") == "saee_production_evidence_intake_audit",
        "wrong intake audit type",
    )
    require(audit.get("intake_scope") == "local_public_shell_evidence_intake_audit", "wrong scope")
    require(
        audit.get("local_evidence_categories_reviewed") == len(INTAKE_SPECS),
        "wrong category count",
    )
    require(audit.get("all_local_evidence_files_present") is True, "files must exist")
    require(audit.get("all_local_evidence_paths_configured") is True, "paths configured")
    require(audit.get("all_evidence_categories_ready") is False, "categories must not be ready")
    require(audit.get("human_review_required") is True, "human review required")
    require(audit.get("task_candidates_executed") is False, "no task executed")
    require(
        audit.get("development_permission_granted") is False,
        "no development permission granted",
    )
    for flag in [
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
    ]:
        require(audit.get(flag) is False, f"{flag} must be false")

    go = audit.get("commercial_go_no_go", {})
    require(go.get("production_launch_status") == "hold", "production launch hold")
    require(go.get("production_blocker_count") == 24, "24 blockers remain")
    require(go.get("total_production_checks") == 24, "24 production checks")
    require(go.get("blockers_closed_by_intake") == 0, "intake must close zero blockers")
    require(
        go.get("local_public_shell_review_candidate_count") == 1,
        "intake records one local public-shell review candidate",
    )
    require(
        go.get("local_profile_unsatisfied_blocker_count") == 23,
        "local profile still leaves 23 blocker checks unsatisfied",
    )
    require(
        len(go.get("unsatisfied_blocker_ids", [])) == 23,
        "23 blocker checks remain unsatisfied in local profile",
    )
    require(len(go.get("open_blocker_ids", [])) == 24, "24 blockers remain open")

    for item in audit.get("category_results", []):
        require(item.get("evidence_file_exists") is True, "evidence file exists")
        require(item.get("path_configured") is True, "evidence path configured")
        require(item.get("ready") is False, "local evidence category not ready")
        boundary = item.get("boundary", {})
        for flag, value in boundary.items():
            require(value is False, f"category boundary {flag} must be false")
    data_ops_paths = [
        item.get("local_path")
        for item in audit.get("category_results", [])
        if item.get("env_var") == "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH"
    ]
    operations_paths = [
        item.get("local_path")
        for item in audit.get("category_results", [])
        if item.get("env_var") == "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH"
    ]
    require(
        data_ops_paths == [COMBINED_DATA_OPS_EVIDENCE_PATH],
        "data operations intake path must point to combined profile",
    )
    require(
        operations_paths == [COMBINED_OPERATIONS_EVIDENCE_PATH],
        "operations intake path must point to combined profile",
    )

    combined = (
        OUTPUT_MD.read_text(encoding="utf-8")
        + "\n"
        + README_PATH.read_text(encoding="utf-8")
    )
    for token in [
        "local_public_shell_evidence_intake_audit",
        "production_launch_status: hold",
        "production_blocker_count: 24",
        "total_production_checks: 24",
        "blockers_closed_by_intake: 0",
        "local_public_shell_review_candidate_count: 1",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]:
        require(token in combined, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_EVIDENCE_INTAKE_AUDIT_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_EVIDENCE_INTAKE_AUDIT_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/production_evidence_intake/README.md",
        "/phase_b_product/commercial_readiness/production_evidence_intake/production_evidence_intake.local.json",
        "/phase_b_product/commercial_readiness/production_evidence_intake/production_evidence_intake.local.md",
        "/scripts/saee_production_evidence_intake_audit.py",
        "/scripts/saee_production_evidence_intake_audit_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_evidence_intake_audit_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_intake_hold",
        "production_evidence_intake_audit_v0_1": True,
        "intake_scope": "local_public_shell_evidence_intake_audit",
        "local_evidence_categories_reviewed": 8,
        "all_local_evidence_files_present": True,
        "all_local_evidence_paths_configured": True,
        "all_evidence_categories_ready": False,
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "blockers_closed_by_intake": 0,
        "local_public_shell_review_candidate_count": 1,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    for flag, expected_value in expected.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index {flag} must be {expected_value}",
        )

    print(
        "SAEE_PRODUCTION_EVIDENCE_INTAKE_AUDIT_SMOKE: PASS "
        "categories=8 production_launch_status=hold blockers_closed_by_intake=0 "
        "local_public_shell_review_candidate_count=1 "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
