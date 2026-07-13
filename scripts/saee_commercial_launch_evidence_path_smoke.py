#!/usr/bin/env python3
"""Smoke check for the SAEE commercial launch evidence path."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_launch_evidence_path/commercial_launch_evidence_path.local.json"
)
REPORT = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_launch_evidence_path/commercial_launch_evidence_path_report.md"
)
DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_EVIDENCE_PATH_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_LAUNCH_EVIDENCE_PATH_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_LAUNCH_EVIDENCE_PATH_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_launch_evidence_path.py"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    require(SUMMARY.exists(), "summary JSON missing")
    require(REPORT.exists(), "report missing")
    require(DOC.exists(), "doc missing")
    require(GATE.exists(), "gate missing")
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    expected = {
        "commercial_launch_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_full_commercial_launch_evidence_path",
        "path_status": "pass_fixture_only",
        "fixture_only": True,
        "real_production_evidence_collected": False,
        "real_customer_validation_collected": False,
        "real_payment_or_revenue_evidence_collected": False,
        "real_legal_security_review_completed": False,
        "human_launch_approval_recorded": False,
        "default_commercial_status": "hold",
        "default_production_launch_status": "hold",
        "default_production_blocker_count": 24,
        "full_fixture_commercial_status_after_fixture": "go",
        "full_fixture_production_launch_status_after_fixture": "go",
        "satisfied_production_checks_after_full_fixture": 24,
        "total_production_checks_after_full_fixture": 24,
        "production_blocker_count_after_full_fixture": 0,
        "boundary_violation_count_after_full_fixture": 0,
        "commercial_launch_path_proven_by_fixture": True,
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_real_evidence_required": True,
        "separate_human_launch_approval_required": True,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "customer_data_processed": False,
        "revenue_validated": False,
    }
    for key, expected_value in expected.items():
        require(data.get(key) == expected_value, f"{key} must be {expected_value}")

    statuses = data.get("readiness_statuses_after_fixture")
    require(isinstance(statuses, dict), "readiness statuses must be object")
    for label in [
        "auth",
        "support",
        "data_ops",
        "operations",
        "privacy_security_legal",
        "billing_revenue",
        "tenant_storage",
        "customer_validation",
    ]:
        require(statuses.get(label) == "pass", f"{label} fixture status must pass")

    satisfied = data.get("target_blockers_satisfied_by_fixture")
    unsatisfied = data.get("target_blockers_unsatisfied_by_fixture")
    require(isinstance(satisfied, list), "satisfied blockers must be list")
    require(len(satisfied) == 24, "fixture must satisfy 24 production blockers")
    require(unsatisfied == [], "fixture must leave no unsatisfied target blockers")

    combined = "\n".join(
        [
            REPORT.read_text(encoding="utf-8"),
            DOC.read_text(encoding="utf-8"),
            GATE.read_text(encoding="utf-8"),
        ]
    )
    for phrase in [
        "fixture-only",
        "not production launch approval",
        "No real production evidence was collected",
        "No customer validation was collected",
        "No product, backend, runtime, kernel, API schema, landing page, or private core was modified.",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_path: 0",
    ]:
        require(phrase in combined, f"missing boundary phrase: {phrase}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_launch_evidence_path/commercial_launch_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/commercial_launch_evidence_path/commercial_launch_evidence_path_report.md",
        "/docs/strategy/SAEE_COMMERCIAL_LAUNCH_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_launch_evidence_path_v0_1", {})
    for key, expected_value in expected.items():
        if key in {
            "commercial_launch_evidence_path_v0_1",
            "path_type",
            "path_status",
            "fixture_only",
            "default_commercial_status",
            "default_production_blocker_count",
            "production_blocker_count_after_full_fixture",
            "blockers_closed_by_path",
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "external_calls_made",
            "customer_contacted",
            "revenue_validated",
        }:
            require(entry.get(key) == expected_value, f"agent-index {key} mismatch")

    print(
        "SAEE_COMMERCIAL_LAUNCH_EVIDENCE_PATH_SMOKE: PASS "
        "path_status=pass_fixture_only default_blockers=24 fixture_blockers=0 "
        "blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
