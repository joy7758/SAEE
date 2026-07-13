#!/usr/bin/env python3
"""Smoke test for the restore_tested promotion decision validator."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_restore_tested_promotion_decision_validator.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/local_evidence_promotion_requests"
OUT_JSON = OUTPUT_DIR / "restore_tested_promotion_decision_validation.local.json"
OUT_MD = OUTPUT_DIR / "restore_tested_promotion_decision_validation.md"
OUT_CSV = OUTPUT_DIR / "restore_tested_promotion_decision_validation.csv"
OUT_AUDIT = OUTPUT_DIR / "restore_tested_promotion_decision_validation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR_SMOKE: FAIL: " + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_AUDIT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "restore_tested_promotion_decision_validator_v0_1": True,
        "validator_type": "human_promotion_decision_input_validator_no_execution",
        "validator_scope": "validate_decision_template_only_no_matrix_change_no_closure",
        "status": "hold_human_decision_missing",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "restore_tested",
        "source_packet_status": "hold_human_promotion_decision_required",
        "decision": "",
        "human_reviewer_present": False,
        "decision_date_present": False,
        "reason_present": False,
        "decision_fields_complete": False,
        "authorize_separate_matrix_update_request": False,
        "authorize_blocker_closure": False,
        "authorize_product_launch": False,
        "matrix_update_request_ready": False,
        "final_hold_recorded": False,
        "final_reject_recorded": False,
        "matrix_update_executed": False,
        "blockers_closed_by_validator": 0,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(
        payload.get("allowed_decision_values")
        == ["approve_separate_matrix_update_request", "hold", "reject"],
        "allowed decision values changed",
    )

    false_flags = [
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "blockers_closed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "evidence_collection_authorized",
        "execution_authorized",
        "development_permission_granted",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 1, "CSV must contain one target row")
    require(rows[0]["target_blocker_id"] == "restore_tested", "CSV target mismatch")
    require(rows[0]["status"] == "hold_human_decision_missing", "CSV status mismatch")
    require(rows[0]["matrix_update_request_ready"] == "False", "CSV matrix update ready must be false")
    require(rows[0]["blockers_closed_by_validator"] == "0", "CSV closed count must be zero")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "restore_tested_promotion_decision_validator_v0_1: true",
        "status: hold_human_decision_missing",
        "decision: missing",
        "decision_fields_complete: false",
        "authorize_separate_matrix_update_request: false",
        "authorize_blocker_closure: false",
        "authorize_product_launch: false",
        "matrix_update_request_ready: false",
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_validator: 0",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
    ]:
        require(token in combined, f"missing token {token}")
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "matrix_update_executed: true",
        "canonical_gap_matrix_modified: true",
        "blocker_closure_authorized: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "blockers_closed_by_validator: 1",
    ]:
        require(token not in combined, f"forbidden token {token}")

    print(
        "SAEE_RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR_SMOKE: PASS "
        f"status={payload['status']} "
        "target=restore_tested matrix_update_ready=false blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
