#!/usr/bin/env python3
"""Smoke test the commercial matrix-update execution request packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_matrix_update_execution_request_packet.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/matrix_update_requests"
SUMMARY = OUT_DIR / "commercial_matrix_update_execution_request_packet.local.json"
REPORT = OUT_DIR / "commercial_matrix_update_execution_request_packet.md"
CSV = OUT_DIR / "commercial_matrix_update_execution_request_packet.csv"
BOUNDARY = OUT_DIR / "commercial_matrix_update_execution_request_packet_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_GATE.md"
GAP_MATRIX = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"
CLOSURE_BOARD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/"
    "closure_readiness_board.local.json"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_SMOKE: FAIL " + message
    )


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
    require(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET: PASS" in result.stdout,
        "runner did not pass",
    )
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_matrix_update_execution_request_packet_v0_1": True,
        "request_type": "matrix_update_execution_request_packet_no_execution",
        "request_scope": "apply_review_ready_markers_only_to_support_group_and_pricing_page",
        "status": "ready_for_explicit_human_execution_approval_no_closure",
        "target_count": 5,
        "recommended_human_decision": "approve_matrix_update_execution_review_ready_markers_only",
        "requires_explicit_human_execution_approval": True,
        "separate_blocker_closure_approval_required": True,
        "separate_pricing_publication_approval_required": True,
        "boundary_violation_count": 0,
        "human_execution_approved": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_execution_request": 0,
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
    require(
        payload.get("target_blockers")
        == ["support_contact", "customer_support", "sla", "on_call_rotation", "pricing_page"],
        "target blockers mismatch",
    )
    require(payload.get("boundary_violations") == [], "must have no boundary violations")
    targets = payload.get("execution_targets", [])
    require(len(targets) == 5, "must contain five execution targets")
    require(
        all(target.get("requested_matrix_status_after_update") == "open" for target in targets),
        "requested update must keep blockers open",
    )
    require(
        all(target.get("requested_review_ready_marker_only") is True for target in targets),
        "requested update must be marker-only",
    )
    require(
        all(target.get("requested_local_evidence_ready_after_update") is False for target in targets),
        "requested update must not set local_evidence_ready",
    )
    require(
        all(target.get("requested_closure_allowed_after_update") is False for target in targets),
        "requested update must not allow closure",
    )
    require(
        all(target.get("blocker_closure_allowed_by_this_request") is False for target in targets),
        "execution request must not authorize closure",
    )

    gap_matrix = read_json(GAP_MATRIX)
    matrix_by_id = {
        row.get("blocker_id"): row
        for row in gap_matrix.get("matrix", [])
        if isinstance(row, dict)
    }
    for blocker_id in payload["target_blockers"]:
        row = matrix_by_id.get(blocker_id)
        require(isinstance(row, dict), f"missing matrix row {blocker_id}")
        require(row.get("status") == "open", f"{blocker_id} matrix status must remain open")
        require(row.get("local_evidence_ready") is False, f"{blocker_id} local evidence must remain false")
        require(
            row.get("closure_allowed_by_matrix") is False,
            f"{blocker_id} closure_allowed_by_matrix must remain false",
        )
    closure_board = read_json(CLOSURE_BOARD)
    require(
        closure_board.get("blockers_closed_by_board") == 0,
        "closure board must not close blockers",
    )
    require(
        closure_board.get("closure_candidate_count") == 0,
        "closure board must not contain closure candidates",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "commercial_matrix_update_execution_request_packet_v0_1: true",
        "ready_for_explicit_human_execution_approval_no_closure",
        "human_execution_approved=false",
        "matrix_update_executed=false",
        "canonical_gap_matrix_modified=false",
        "canonical_closure_board_modified=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_execution_request=0",
        "pricing_page_published=false",
        "checkout_enabled=false",
        "production_ready=false",
        "answer: ready_for_explicit_human_execution_approval_no_closure",
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
        "blockers_closed_by_execution_request=1",
        "open_blocker_count_reduced=true",
        "pricing_page_published=true",
        "checkout_enabled=true",
        "customer_payment_collected=true",
        "revenue_validated=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.csv",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_request_packet.py",
        "/scripts/saee_commercial_matrix_update_execution_request_packet_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("commercial_matrix_update_execution_request_packet_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "request_type",
        "request_scope",
        "target_count",
        "target_blockers",
        "recommended_human_decision",
        "requires_explicit_human_execution_approval",
        "separate_blocker_closure_approval_required",
        "human_execution_approved",
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "blockers_closed_by_execution_request",
        "open_blocker_count_reduced",
        "pricing_page_published",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "customer_validated",
        "production_ready",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")
    require(
        entry.get("make_target") == "make check-commercial-matrix-update-execution-request-packet",
        "make target mismatch",
    )

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Commercial Matrix Update Execution Request Packet v0.1",
        "commercial_matrix_update_execution_request_packet_v0_1",
        "ready_for_explicit_human_execution_approval_no_closure",
        "target_count=5",
        "human_execution_approved=false",
        "matrix_update_executed=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_execution_request=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_REQUEST_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
