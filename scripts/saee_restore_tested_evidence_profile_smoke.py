#!/usr/bin/env python3
"""Smoke check for the SAEE restore-tested evidence profile."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
    evaluate_production_data_operations_evidence,
)
from scripts.saee_restore_tested_evidence_profile import (
    DEFAULT_DATA_OPS_OUTPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SOURCE_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_profile,
)


PROFILE_SCRIPT = ROOT / "scripts/saee_restore_tested_evidence_profile.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_RESTORE_TESTED_EVIDENCE_PROFILE_SMOKE: FAIL: " + message)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def minimal_source(*, complete: bool = True, unsafe: bool = False) -> dict[str, object]:
    data: dict[str, object] = {
        "data_operations_evidence_type": "production_data_operations_evidence",
        "evidence_scope": "smoke_fixture",
        "generated_by": "smoke_fixture",
        "local_public_shell_results": {"restore_drill_status": "pass"},
    }
    for key in RESTORE_TEST_KEYS:
        data[key] = complete
    if not complete:
        data["restore_test_report_reviewed"] = False
    for key in RESTORE_POLICY_KEYS:
        data[key] = False
    for key in FORBIDDEN_TRUE_KEYS:
        data[key] = False
    if unsafe:
        data["production_ready"] = True
    return data


def data_ops_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def go_no_go(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def blocker_satisfied(report: dict[str, object], blocker_id: str) -> bool:
    return any(
        item["blocker_id"] == blocker_id and item["satisfied"] is True
        for item in report["blockers"]
    )


def main() -> None:
    require(PROFILE_SCRIPT.exists(), "profile script missing")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/saee_data_operations_evidence_runner.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_run = subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    summary = json.loads(default_run.stdout)
    require(summary["status"] == "pass", "default profile must pass")
    require(
        summary["source_restore_test_evidence_complete"] is True,
        "source restore-test evidence must be complete",
    )
    require(
        summary["restore_tested_available_for_go_no_go"] is True,
        "restore_tested must be available for explicit go/no-go profile",
    )
    require(summary["production_restore_tested"] is True, "production_restore_tested profile true")
    require(
        summary["production_restore_policy_available"] is False,
        "production restore policy must remain false",
    )
    require(
        summary["production_data_operations_ready"] is False,
        "production data operations must remain false",
    )
    require(summary["commercial_status_after_profile"] == "hold", "commercial status hold")
    require(
        summary["production_launch_status_after_profile"] == "hold",
        "production launch status hold",
    )
    require(summary["target_blocker_satisfied_by_profile"] is True, "restore_tested satisfied")
    require(summary["profile_satisfied_production_checks"] == 1, "one production check satisfied")
    require(summary["profile_production_blocker_count"] == 23, "23 blockers remain")
    require(summary["blockers_closed_by_profile"] == 0, "profile closes zero blockers")
    require(summary["production_ready"] is False, "production ready false")
    require(summary["customer_validated"] is False, "customer validated false")
    require(summary["product_launched"] is False, "product launched false")
    require(summary["private_core_exposed"] is False, "private core false")
    require(DEFAULT_SOURCE_PATH.exists(), "default source missing")
    require(DEFAULT_OUTPUT_PATH.exists(), "default profile output missing")
    require(DEFAULT_DATA_OPS_OUTPUT_PATH.exists(), "default data ops output missing")

    readiness = data_ops_readiness(DEFAULT_DATA_OPS_OUTPUT_PATH)
    report = go_no_go(DEFAULT_DATA_OPS_OUTPUT_PATH)
    require(readiness["restore_tested"] is True, "readiness restore_tested true")
    require(readiness["production_restore_policy_available"] is False, "readiness policy false")
    require(readiness["production_data_operations_ready"] is False, "readiness ready false")
    require(blocker_satisfied(report, "restore_tested"), "go/no-go restore_tested satisfied")
    require(not blocker_satisfied(report, "production_restore_policy"), "policy remains unsatisfied")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        incomplete_source = tmp / "incomplete.json"
        incomplete_summary = tmp / "incomplete_summary.json"
        incomplete_data_ops = tmp / "incomplete_data_ops.json"
        unsafe_source = tmp / "unsafe.json"
        unsafe_summary = tmp / "unsafe_summary.json"
        unsafe_data_ops = tmp / "unsafe_data_ops.json"
        write_json(incomplete_source, minimal_source(complete=False))
        write_json(unsafe_source, minimal_source(unsafe=True))

        incomplete = build_profile(
            incomplete_source,
            incomplete_summary,
            incomplete_data_ops,
            write_documents=False,
        )
        unsafe = build_profile(
            unsafe_source,
            unsafe_summary,
            unsafe_data_ops,
            write_documents=False,
        )
        incomplete_readiness = data_ops_readiness(incomplete_data_ops)
        unsafe_readiness = data_ops_readiness(unsafe_data_ops)

    require(incomplete["status"] == "hold", "incomplete source must hold")
    require(
        incomplete["restore_tested_available_for_go_no_go"] is False,
        "incomplete source cannot set restore_tested",
    )
    require(incomplete_readiness["restore_tested"] is False, "incomplete readiness false")
    require(unsafe["status"] == "stop", "unsafe source must stop")
    require(unsafe["source_boundary_violation_count"] > 0, "unsafe source records violations")
    require(unsafe["restore_tested_available_for_go_no_go"] is False, "unsafe cannot set restore")
    require(unsafe_readiness["restore_tested"] is False, "unsafe readiness restore false")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH])
    for token in [
        "restore_tested_evidence_profile_v0_1: true",
        "profile_scope: local_restore_tested_evidence_profile_from_public_shell_drill",
        "restore_tested_available_for_go_no_go: true",
        "production_restore_policy_available: false",
        "production_data_operations_ready: false",
        "commercial_status_after_profile: hold",
        "profile_production_blocker_count: 23",
        "blockers_closed_by_profile: 0",
        "recommend_for_restore_tested_evidence_review: true",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/RESTORE_TESTED_EVIDENCE_PROFILE_V0_1.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/restore_tested_evidence_profile.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_tested.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/restore_tested_evidence_profile_report.md",
        "/docs/strategy/SAEE_RESTORE_TESTED_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md",
        "/scripts/saee_restore_tested_evidence_profile.py",
        "/scripts/saee_restore_tested_evidence_profile_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("restore_tested_evidence_profile_v0_1", {})
    expected = {
        "status": "local_restore_tested_profile_available_hold",
        "profile_scope": "local_restore_tested_evidence_profile_from_public_shell_drill",
        "restore_tested_available_for_go_no_go": True,
        "production_restore_tested": True,
        "production_restore_policy_available": False,
        "production_data_operations_ready": False,
        "commercial_status_after_profile": "hold",
        "production_launch_status_after_profile": "hold",
        "profile_satisfied_production_checks": 1,
        "profile_production_blocker_count": 23,
        "blockers_closed_by_profile": 0,
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
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_RESTORE_TESTED_EVIDENCE_PROFILE_SMOKE: PASS "
        "restore_tested_available_for_go_no_go=true "
        "production_restore_policy_available=false "
        "commercial_status_after_profile=hold "
        "profile_production_blocker_count=23 "
        "blockers_closed_by_profile=0"
    )


if __name__ == "__main__":
    main()
