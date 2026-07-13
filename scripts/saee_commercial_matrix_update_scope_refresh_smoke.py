#!/usr/bin/env python3
"""Smoke test for the no-execution commercial matrix scope refresh packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_scope_refresh.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh"
SUMMARY = OUT_DIR / "commercial_matrix_update_scope_refresh.local.json"
REPORT = OUT_DIR / "commercial_matrix_update_scope_refresh.md"
CSV = OUT_DIR / "commercial_matrix_update_scope_refresh.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_scope_refresh_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_GATE.md"
CURRENT_REQUEST = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.local.json"
CURRENT_EXECUTION_REQUEST = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.local.json"
GAP_MATRIX = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_SMOKE: FAIL " + message)


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
    require("SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_matrix_update_scope_refresh_v0_1": True,
        "refresh_type": "review_ready_marker_scope_refresh_packet_no_activation_no_execution",
        "status": "ready_for_human_scope_refresh_review_no_execution",
        "canonical_open_blocker_count": 24,
        "previous_target_count": 5,
        "refreshed_target_count": 23,
        "retained_target_count": 5,
        "added_target_count": 18,
        "removed_target_count": 0,
        "not_cataloged_blocker_count": 1,
        "not_cataloged_blocker_ids": ["customer_validated"],
        "scope_refresh_packet_generated": True,
        "human_scope_review_required": True,
        "exact_human_execution_approval_still_required": True,
        "separate_blocker_closure_approval_still_required": True,
        "recommendation_gate": "conditional",
        "would_recommend_to_potential_customer": "conditional",
        "boundary_violation_count": 0,
        "active_matrix_request_replaced": False,
        "execution_request_regenerated": False,
        "approval_scope_changed": False,
        "scope_refresh_execution_authorized": False,
        "matrix_update_execution_authorized": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_scope_refresh": 0,
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
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")

    refreshed = payload.get("refreshed_target_ids")
    previous = payload.get("previous_target_ids")
    require(isinstance(refreshed, list) and len(refreshed) == 23, "must contain 23 refreshed ids")
    require(len(set(refreshed)) == 23, "refreshed ids must be unique")
    require("customer_validated" not in refreshed, "customer validation must remain excluded")
    require(isinstance(previous, list) and len(previous) == 5, "must retain five previous ids")
    require(set(previous).issubset(refreshed), "all previous ids must be retained")
    require(payload.get("retained_target_ids") == previous, "retained ids must match previous ids")
    require(len(payload.get("added_target_ids", [])) == 18, "must add 18 scope candidates")
    require(payload.get("removed_target_ids") == [], "must remove no current candidate")

    rows = payload.get("scope_refresh_rows")
    require(isinstance(rows, list) and len(rows) == 23, "scope refresh must contain 23 rows")
    for row in rows:
        require(row.get("review_ready_marker_candidate") is True, "every row must be review-ready")
        require(row.get("current_matrix_status") == "open", "canonical status must remain open")
        require(row.get("current_matrix_local_evidence_ready") is False, "canonical local evidence must remain false")
        require(row.get("current_matrix_closure_allowed") is False, "canonical closure must remain false")
        require(row.get("proposed_status_after_future_update") == "open", "future status must remain open")
        require(row.get("proposed_local_evidence_ready_after_future_update") is False, "must not set local evidence ready")
        require(row.get("proposed_closure_allowed_after_future_update") is False, "must not allow closure")
        require(row.get("requires_separate_human_scope_confirmation") is True, "scope confirmation required")
        require(row.get("requires_exact_human_execution_approval_after_scope_confirmation") is True, "exact approval required")
        require(row.get("execution_allowed_by_scope_refresh") is False, "scope refresh must not allow execution")
        require(row.get("closure_allowed_by_scope_refresh") is False, "scope refresh must not allow closure")

    with CSV.open(encoding="utf-8", newline="") as handle:
        require(len(list(csv.DictReader(handle))) == 23, "CSV must contain 23 rows")

    current_request = read_json(CURRENT_REQUEST)
    current_execution_request = read_json(CURRENT_EXECUTION_REQUEST)
    require(len(current_request.get("target_blockers", [])) == 5, "active request must remain five-row")
    require(len(current_execution_request.get("target_blockers", [])) == 5, "execution request must remain five-row")
    require(current_request.get("matrix_update_executed") is False, "active request must not execute")
    require(current_execution_request.get("matrix_update_executed") is False, "execution request must not execute")

    matrix = read_json(GAP_MATRIX)
    matrix_rows = matrix.get("matrix", [])
    require(len(matrix_rows) == 24, "canonical matrix must retain 24 rows")
    require(all(row.get("status") == "open" for row in matrix_rows), "all canonical blockers must remain open")
    require(all(row.get("local_evidence_ready") is False for row in matrix_rows), "canonical local evidence must remain false")
    require(all(row.get("closure_allowed_by_matrix") is False for row in matrix_rows), "canonical closure must remain false")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "previous_target_count: 5",
        "refreshed_target_count: 23",
        "added_target_count: 18",
        "not_cataloged_blocker_ids: customer_validated",
        "human_scope_review_required: true",
        "exact_human_execution_approval_still_required: true",
        "active_matrix_request_replaced=false",
        "approval_scope_changed=false",
        "matrix_update_executed=false",
        "blockers_closed_by_scope_refresh=0",
        "production_ready=false",
        "customer_validated=false",
        "answer: conditional_human_scope_review_required_no_execution",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "active_matrix_request_replaced=true",
        "approval_scope_changed=true",
        "matrix_update_executed=true",
        "blocker_closure_authorized=true",
        "production_ready=true",
        "customer_validated=true",
        "private_core_exposed=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_GATE.md",
        "/scripts/saee_commercial_matrix_update_scope_refresh.py",
        "/scripts/saee_commercial_matrix_update_scope_refresh_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    entry = read_json(ROOT / "agent-index.json").get("commercial_matrix_update_scope_refresh_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key in [
        "status", "canonical_open_blocker_count", "previous_target_count",
        "refreshed_target_count", "retained_target_count", "added_target_count",
        "removed_target_count", "not_cataloged_blocker_ids",
        "scope_refresh_packet_generated", "human_scope_review_required",
        "exact_human_execution_approval_still_required", "recommendation_gate",
        "active_matrix_request_replaced", "execution_request_regenerated",
        "approval_scope_changed", "matrix_update_execution_authorized",
        "matrix_update_executed", "blocker_closure_authorized",
        "blockers_closed_by_scope_refresh", "production_ready",
        "customer_validated", "private_core_exposed",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    runner_text = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["requests.", "urllib.", "httpx.", "webbrowser", "selenium"]:
        require(forbidden not in runner_text, f"runner must not call external services: {forbidden}")

    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_SCOPE_REFRESH_SMOKE: PASS "
        "previous=5 refreshed=23 added=18 active_request_replaced=false "
        "matrix_update_executed=false blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
