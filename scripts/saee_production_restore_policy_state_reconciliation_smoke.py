#!/usr/bin/env python3
"""Smoke test for production-restore-policy state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_production_restore_policy_state_reconciliation.py"
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_restore_policy_state_reconciliation"
)
SUMMARY = OUT_DIR / "production_restore_policy_state_reconciliation.local.json"
REPORT = OUT_DIR / "production_restore_policy_state_reconciliation.md"
BOUNDARY = OUT_DIR / "production_restore_policy_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION: PASS" in result.stdout,
        "runner did not pass",
    )
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "production_restore_policy_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_production_restore_policy_state_reconciliation_no_restore_no_closure",
        "target_blocker_id": "production_restore_policy",
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "approval_input_complete": True,
        "approval_builder_ready": True,
        "builder_output_ready": True,
        "production_restore_policy_available_for_review": True,
        "restore_tested_profile_ready": True,
        "combined_profile_ready": True,
        "production_restore_policy_satisfied_by_profile": True,
        "restore_tested_satisfied_by_profile": True,
        "restore_run_by_codex": False,
        "restore_policy_published_by_codex": False,
        "restore_policy_approved_by_codex": False,
        "live_data_path_touched": False,
        "customer_data_processed": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("status") == "ready_for_human_data_operations_profile_review_no_closure",
        "status must be review-ready no-closure",
    )
    require(payload.get("resolved_current_path") == "combined_profile", "resolved path mismatch")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Production Restore Policy State Reconciliation",
        "production_restore_policy_satisfied_by_profile=true",
        "restore_tested_satisfied_by_profile=true",
        "restore_run_by_codex=false",
        "live_data_path_touched=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "No restore run by Codex",
        "answer: hold_human_review_required_no_restore_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "restore_run_by_codex=true",
        "live_data_path_touched=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_state_reconciliation/production_restore_policy_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_state_reconciliation/production_restore_policy_state_reconciliation.md",
        "/docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_production_restore_policy_state_reconciliation.py",
        "/scripts/saee_production_restore_policy_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("production_restore_policy_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing production_restore_policy_state_reconciliation_v0_1")
    for key in [
        "status",
        "target_blocker_id",
        "resolved_current_path",
        "production_restore_policy_available_for_review",
        "restore_tested_profile_ready",
        "combined_profile_ready",
        "production_restore_policy_satisfied_by_profile",
        "restore_tested_satisfied_by_profile",
        "restore_run_by_codex",
        "live_data_path_touched",
        "customer_data_processed",
        "blockers_closed_by_reconciliation",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Production Restore Policy State Reconciliation v0.1",
        "production_restore_policy_satisfied_by_profile=true",
        "restore_run_by_codex=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
