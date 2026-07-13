#!/usr/bin/env python3
"""Smoke test commercial matrix-update execution dry run."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_execution_dry_run.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
SUMMARY = OUT_DIR / "commercial_matrix_update_execution_dry_run.local.json"
REPORT = OUT_DIR / "commercial_matrix_update_execution_dry_run.md"
CSV = OUT_DIR / "commercial_matrix_update_execution_dry_run.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_execution_dry_run_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_GATE.md"
GAP_MATRIX = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"

TARGET_BLOCKERS = [
    "support_contact",
    "customer_support",
    "sla",
    "on_call_rotation",
    "pricing_page",
]


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
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
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_matrix_update_execution_dry_run_v0_1": True,
        "dry_run_type": "matrix_update_execution_no_write_preview",
        "status": "hold_human_execution_approval_required",
        "dry_run_only": True,
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "apply_performed": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_dry_run": 0,
        "open_blocker_count_reduced": False,
        "target_count": 5,
        "would_update_count": 0,
        "blocked_preview_count": 5,
        "boundary_violation_count": 0,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
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
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("target_blockers") == TARGET_BLOCKERS, "target blockers mismatch")
    require(payload.get("boundary_violations") == [], "must have no boundary violations")
    rows = payload.get("preview_rows")
    require(isinstance(rows, list) and len(rows) == 5, "must contain five preview rows")
    for row in rows:
        require(row.get("blocker_id") in TARGET_BLOCKERS, "unexpected blocker id")
        require(row.get("current_status") == "open", "target current status must remain open")
        require(row.get("current_local_evidence_ready") is False, "target evidence must remain false")
        require(row.get("current_closure_allowed_by_matrix") is False, "target closure must remain false")
        require(row.get("blocked_reason") == "human_execution_approval_missing", "approval block reason missing")
        require(row.get("would_update_if_approved") is False, "current state must not preview update as approved")
        require(row.get("would_keep_status") == "open", "preview must keep blockers open")
        require(row.get("would_keep_local_evidence_ready") is False, "preview must not set evidence ready")
        require(row.get("would_keep_closure_allowed_by_matrix") is False, "preview must not allow closure")
        require(row.get("closure_allowed_by_dry_run") is False, "dry run must not allow closure")

    matrix = read_json(GAP_MATRIX)
    matrix_by_id = {
        row.get("blocker_id"): row
        for row in matrix.get("matrix", [])
        if isinstance(row, dict)
    }
    for blocker_id in TARGET_BLOCKERS:
        row = matrix_by_id.get(blocker_id)
        require(isinstance(row, dict), f"missing matrix row {blocker_id}")
        require(row.get("status") == "open", f"{blocker_id} matrix status must remain open")
        require(row.get("local_evidence_ready") is False, f"{blocker_id} local evidence must remain false")
        require(row.get("closure_allowed_by_matrix") is False, f"{blocker_id} closure must remain false")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "commercial_matrix_update_execution_dry_run_v0_1: true",
        "hold_human_execution_approval_required",
        "dry_run_only: true",
        "apply_performed: false",
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_dry_run: 0",
        "production_ready: false",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "matrix_update_executed=true",
        "canonical_gap_matrix_modified=true",
        "canonical_closure_board_modified=true",
        "blocker_closure_authorized=true",
        "blockers_closed_by_dry_run=1",
        "open_blocker_count_reduced=true",
        "pricing_page_published=true",
        "checkout_enabled=true",
        "customer_payment_collected=true",
        "revenue_validated=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_dry_run.py",
        "/scripts/saee_commercial_matrix_update_execution_dry_run_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("commercial_matrix_update_execution_dry_run_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "dry_run_only",
        "human_execution_approved",
        "ready_for_matrix_update_execution",
        "apply_performed",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "blockers_closed_by_dry_run",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")
    require(
        entry.get("make_target") == "make check-commercial-matrix-update-execution-dry-run",
        "make target mismatch",
    )

    print("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_DRY_RUN_SMOKE: PASS")


if __name__ == "__main__":
    main()
