#!/usr/bin/env python3
"""Smoke test commercial matrix-update execution applier."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_execution_applier.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
SUMMARY = OUT_DIR / "commercial_matrix_update_execution_applier.local.json"
REPORT = OUT_DIR / "commercial_matrix_update_execution_applier.md"
CSV = OUT_DIR / "commercial_matrix_update_execution_applier.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_execution_applier_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_GATE.md"
REQUEST = OUT_DIR / "commercial_matrix_update_execution_request_packet.local.json"
APPROVAL = OUT_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
GAP_MATRIX = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"

TARGET_BLOCKERS = [
    "support_contact",
    "customer_support",
    "sla",
    "on_call_rotation",
    "pricing_page",
]


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path} must be valid JSON: {exc}")
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def run_default() -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER: PASS" in result.stdout, "runner did not pass")
    return read_json(SUMMARY)


def assert_default(payload: dict[str, Any]) -> None:
    expected = {
        "commercial_matrix_update_execution_applier_v0_1": True,
        "applier_type": "matrix_review_ready_marker_applier",
        "status": "hold_human_execution_approval_required",
        "execution_mode": "dry_run_no_write",
        "apply_requested": False,
        "human_apply_confirmation_provided": False,
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "apply_preconditions_met": False,
        "apply_performed": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "target_count": 5,
        "apply_row_count": 0,
        "blocker_closure_authorized": False,
        "blockers_closed_by_applier": 0,
        "open_blocker_count_reduced": False,
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
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("target_blockers") == TARGET_BLOCKERS, "target blockers mismatch")
    require(payload.get("boundary_violations") == [], "default boundary violations must be empty")
    require(payload.get("applied_rows") == [], "default must not apply rows")


def assert_docs() -> None:
    for path in [REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "commercial_matrix_update_execution_applier_v0_1: true",
        "hold_human_execution_approval_required",
        "execution_mode: dry_run_no_write",
        "apply_performed: false",
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_applier: 0",
        "production_ready: false",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blocker_closure_authorized=true",
        "blockers_closed_by_applier=1",
        "open_blocker_count_reduced=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")


def assert_canonical_matrix_unchanged() -> None:
    matrix = read_json(GAP_MATRIX)
    rows = {
        row.get("blocker_id"): row
        for row in matrix.get("matrix", [])
        if isinstance(row, dict)
    }
    for blocker_id in TARGET_BLOCKERS:
        row = rows.get(blocker_id)
        require(isinstance(row, dict), f"missing matrix row {blocker_id}")
        require(row.get("status") == "open", f"{blocker_id} status must remain open")
        require(row.get("local_evidence_ready") is False, f"{blocker_id} evidence must remain false")
        require(row.get("closure_allowed_by_matrix") is False, f"{blocker_id} closure must remain false")
        require("review_ready_marker_applied" not in row, f"{blocker_id} canonical marker must not be applied")


def assert_apply_fixture() -> None:
    with tempfile.TemporaryDirectory() as temp:
        tempdir = Path(temp)
        tmp_matrix = tempdir / "gap_matrix.local.json"
        tmp_output = tempdir / "gap_matrix.marked.local.json"
        tmp_approval = tempdir / "approval_ready.local.json"
        shutil.copy2(GAP_MATRIX, tmp_matrix)
        approval = read_json(APPROVAL)
        approval.update(
            {
                "status": "ready_for_matrix_update_execution_no_closure",
                "human_execution_approved": True,
                "ready_for_matrix_update_execution": True,
                "approval_input_complete": True,
                "missing_fields": [],
            }
        )
        tmp_approval.write_text(json.dumps(approval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--approval-validation",
                str(tmp_approval),
                "--gap-matrix",
                str(tmp_matrix),
                "--output-gap-matrix",
                str(tmp_output),
                "--apply",
                "--confirm-human-approved-matrix-update",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        require("apply_performed=true" in result.stdout, "apply fixture must perform")
        payload = read_json(SUMMARY)
        require(payload.get("status") == "review_ready_markers_applied_no_closure", "fixture status mismatch")
        require(payload.get("execution_mode") == "apply_write_gap_matrix_output", "fixture execution mode mismatch")
        require(payload.get("apply_performed") is True, "fixture apply must be true")
        require(payload.get("matrix_update_executed") is True, "fixture matrix update must be true")
        require(payload.get("canonical_gap_matrix_modified") is False, "fixture must not modify canonical matrix")
        require(payload.get("apply_row_count") == 5, "fixture must apply five rows")
        require(tmp_output.is_file(), "fixture output matrix missing")
        output = read_json(tmp_output)
        rows = {
            row.get("blocker_id"): row
            for row in output.get("matrix", [])
            if isinstance(row, dict)
        }
        for blocker_id in TARGET_BLOCKERS:
            row = rows.get(blocker_id)
            require(row.get("status") == "open", f"{blocker_id} fixture status must remain open")
            require(row.get("local_evidence_ready") is False, f"{blocker_id} fixture evidence must remain false")
            require(row.get("closure_allowed_by_matrix") is False, f"{blocker_id} fixture closure must remain false")
            require(row.get("review_ready_marker_applied") is True, f"{blocker_id} marker missing")
            require(row.get("review_ready_marker_scope") == "review_ready_markers_only_no_closure", "marker scope mismatch")
        run_default()


def assert_index_and_llms(payload: dict[str, Any]) -> None:
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_applier.py",
        "/scripts/saee_commercial_matrix_update_execution_applier_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")
    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_matrix_update_execution_applier_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "execution_mode",
        "apply_requested",
        "human_execution_approved",
        "ready_for_matrix_update_execution",
        "apply_performed",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "blocker_closure_authorized",
        "blockers_closed_by_applier",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")
    require(entry.get("make_target") == "make check-commercial-matrix-update-execution-applier", "make target mismatch")


def main() -> None:
    payload = run_default()
    assert_default(payload)
    assert_docs()
    assert_index_and_llms(payload)
    assert_canonical_matrix_unchanged()
    assert_apply_fixture()
    payload = read_json(SUMMARY)
    assert_default(payload)
    assert_canonical_matrix_unchanged()
    print("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPLIER_SMOKE: PASS")


if __name__ == "__main__":
    main()
