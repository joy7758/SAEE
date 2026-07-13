#!/usr/bin/env python3
"""Smoke test the commercial final human inspection record."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_final_human_inspection"
OUTPUT_JSON = OUTPUT_DIR / "commercial_final_human_inspection_record.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_final_human_inspection_record.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_final_human_inspection_record.csv"
BOUNDARY_AUDIT = OUTPUT_DIR / "commercial_final_human_inspection_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD_GATE.md"
RUNNER = ROOT / "scripts/saee_commercial_final_human_inspection_record.py"


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [OUTPUT_JSON, OUTPUT_MD, OUTPUT_CSV, BOUNDARY_AUDIT, GATE, RUNNER]:
        require(path.is_file(), f"missing required file {path.relative_to(ROOT)}")

    record = read_json(OUTPUT_JSON)
    expected = {
        "commercial_final_human_inspection_record_v0_1": True,
        "record_type": "local_commercial_final_human_inspection_record",
        "status": "hold_external_customer_validation_required",
        "human_inspection_confirmed": True,
        "human_inspection_statement": "人工检查完毕，没有问题，确认",
        "manual_check_completed": True,
        "manual_check_result": "confirmed_no_issue_in_local_evidence_surfaces",
        "local_evidence_lane_count": 7,
        "local_evidence_lanes_passed": True,
        "formal_commercial_status": "hold",
        "production_launch_status": "hold",
        "remaining_production_blocker_count_after_local_human_evidence": 1,
        "external_customer_validation_required": True,
        "external_customer_validation_performed": False,
        "external_customer_validation_claim_allowed": False,
        "default_commercial_go_no_go_overwritten": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "next_goal_blocker": "customer_validated",
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "public_sdk_released": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_inspection": 0,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
    }
    for key, value in expected.items():
        require(record.get(key) == value, f"{key} must be {value}")
    require(
        record.get("remaining_production_blockers_after_local_human_evidence")
        == ["customer_validated"],
        "customer_validated must remain the only blocker",
    )
    lane_review = record.get("lane_review", [])
    require(isinstance(lane_review, list), "lane_review must be list")
    require(len(lane_review) == 7, "lane_review must contain seven lanes")
    require(
        all(item.get("local_evidence_passed") is True for item in lane_review),
        "all lane evidence rows must pass",
    )
    require(
        all(item.get("production_ready") is False for item in lane_review),
        "lane sources must not claim production_ready",
    )
    require(
        all(item.get("customer_validated") is False for item in lane_review),
        "lane sources must not claim customer_validated",
    )
    require(
        all(item.get("product_launched") is False for item in lane_review),
        "lane sources must not claim product_launched",
    )
    require(
        all(item.get("private_core_exposed") is False for item in lane_review),
        "lane sources must not expose private core",
    )

    combined = (
        OUTPUT_MD.read_text(encoding="utf-8")
        + "\n"
        + BOUNDARY_AUDIT.read_text(encoding="utf-8")
        + "\n"
        + GATE.read_text(encoding="utf-8")
    )
    for token in [
        "commercial_final_human_inspection_record_v0_1: true",
        "status: hold_external_customer_validation_required",
        "人工检查完毕，没有问题，确认",
        "remaining_production_blockers_after_local_human_evidence: customer_validated",
        "external_customer_validation_required: true",
        "external_customer_validation_performed: false",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_inspection: 0",
        "answer: hold_external_customer_validation_required",
    ]:
        require(token in combined, "missing report/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/commercial_final_human_inspection/commercial_final_human_inspection_record.md",
        "/phase_b_product/commercial_readiness/commercial_final_human_inspection/commercial_final_human_inspection_record.local.json",
        "/phase_b_product/commercial_readiness/commercial_final_human_inspection/commercial_final_human_inspection_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD_GATE.md",
        "/scripts/saee_commercial_final_human_inspection_record.py",
        "/scripts/saee_commercial_final_human_inspection_record_smoke.py",
    ]:
        require(token in llms, "llms.txt missing token: " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "commercial-final-human-inspection-record-smoke:",
        "check-commercial-final-human-inspection-record:",
        "scripts/saee_commercial_final_human_inspection_record_smoke.py",
    ]:
        require(token in makefile, "Makefile missing token: " + token)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_final_human_inspection_record_v0_1", {})
    require(isinstance(entry, dict), "agent-index entry must be object")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_COMMERCIAL_FINAL_HUMAN_INSPECTION_RECORD_SMOKE: PASS "
        "remaining_blocker=customer_validated production_ready=false"
    )


if __name__ == "__main__":
    main()
