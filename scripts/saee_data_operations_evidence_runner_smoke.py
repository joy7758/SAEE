#!/usr/bin/env python3
"""Smoke check for the local data-operations evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_data_operations_evidence,
)
from scripts.saee_data_operations_evidence_runner import (
    OUTPUT_PATH,
    RESTORE_TEST_PLAN_PATH,
    RESTORE_TEST_REPORT_PATH,
    main as run_runner,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_DATA_OPERATIONS_EVIDENCE_RUNNER_SMOKE: FAIL: " + message)


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    require(RESTORE_TEST_PLAN_PATH.exists(), "restore test plan file must exist")
    require(RESTORE_TEST_REPORT_PATH.exists(), "restore test report file must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    restore_test_plan = json.loads(RESTORE_TEST_PLAN_PATH.read_text(encoding="utf-8"))
    restore_test_report = json.loads(RESTORE_TEST_REPORT_PATH.read_text(encoding="utf-8"))

    require(
        evidence.get("data_operations_evidence_type") == "production_data_operations_evidence",
        "wrong data operations evidence type",
    )
    require(
        evidence.get("evidence_scope") == "local_public_shell_backup_restore_drill",
        "wrong evidence scope",
    )
    require(
        evidence.get("isolated_restore_environment_used") is True,
        "isolated restore evidence must be true",
    )
    require(
        evidence.get("restore_integrity_checks_passed") is True,
        "restore integrity checks must pass",
    )
    require(
        evidence.get("rto_rpo_observed_and_recorded") is True,
        "local observed timing must be recorded",
    )
    require(
        evidence.get("credential_secret_exclusion_reviewed") is True,
        "credential exclusion evidence must be recorded",
    )
    require(
        evidence.get("production_like_restore_test_plan_approved") is True,
        "local restore test plan approval evidence must be recorded",
    )
    require(
        evidence.get("restore_test_report_reviewed") is True,
        "local restore test report review evidence must be recorded",
    )
    require(
        evidence.get("production_restore_policy_approved") is False,
        "must not claim production restore policy approval",
    )

    require(
        restore_test_plan.get("restore_test_plan_type")
        == "local_public_shell_restore_test_plan",
        "wrong restore test plan type",
    )
    require(
        restore_test_plan.get("production_like_restore_test_plan_approved") is True,
        "restore test plan must record local approval",
    )
    require(
        restore_test_report.get("restore_test_report_type")
        == "local_public_shell_restore_test_report",
        "wrong restore test report type",
    )
    require(
        restore_test_report.get("restore_test_report_reviewed") is True,
        "restore test report must record local review",
    )
    for payload_name, payload in [
        ("restore test plan", restore_test_plan),
        ("restore test report", restore_test_report),
    ]:
        flags = payload.get("boundary_flags", {})
        for key in [
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
            "external_calls_made",
            "customer_contacted",
            "production_data_path_modified",
            "restore_to_live_path_enabled",
            "live_restore_performed",
            "credentials_restored",
            "private_core_restored",
        ]:
            require(flags.get(key) is False, f"{payload_name} {key} must be false")

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    readiness = evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    require(readiness["restore_tested"] is True, "restore test evidence should now be complete")
    require(
        readiness["restore_test_evidence_complete"] is True,
        "restore test evidence alias should now be complete",
    )
    require(
        readiness["production_restore_tested"] is True,
        "production-like restore test evidence should now be locally complete",
    )
    require(
        readiness["production_restore_policy_available"] is False,
        "production restore policy evidence must remain incomplete",
    )
    require(
        readiness["production_restore_policy_evidence_complete"] is False,
        "production restore policy evidence alias must remain incomplete",
    )
    require(
        readiness["production_data_operations_ready"] is False,
        "production data operations must remain incomplete",
    )
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
        "production_data_path_modified",
        "restore_to_live_path_enabled",
        "live_restore_performed",
        "credentials_restored",
        "private_core_restored",
    ]:
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/DATA_OPERATIONS_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_DATA_OPERATIONS_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "data_operations_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_backup_restore_drill",
        "production_data_operations_ready: false",
        "restore_tested: true",
        "production_restore_tested: true",
        "production_restore_policy_available: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/DATA_OPERATIONS_EVIDENCE_RUNNER_V0_1.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/README.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/restore_test_plan.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/restore_test_report.local.json",
        "/scripts/saee_data_operations_evidence_runner.py",
        "/scripts/saee_data_operations_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("data_operations_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "data_operations_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_backup_restore_drill",
        "isolated_restore_environment_used": True,
        "restore_integrity_checks_passed": True,
        "rto_rpo_observed_and_recorded": True,
        "production_like_restore_test_plan_approved": True,
        "restore_test_report_reviewed": True,
        "production_restore_policy_approved": False,
        "production_data_operations_ready": False,
        "restore_tested": True,
        "production_restore_tested": True,
        "production_restore_policy_available": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "live_restore_performed": False,
    }
    for flag, expected_value in expected.items():
        require(entry.get(flag) == expected_value, f"agent-index {flag} must be {expected_value}")

    print(
        "SAEE_DATA_OPERATIONS_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "restore_tested=true "
        "production_data_operations_ready=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
