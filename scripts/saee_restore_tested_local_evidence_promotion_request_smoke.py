#!/usr/bin/env python3
"""Smoke test for restore-tested local evidence promotion request."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_restore_tested_local_evidence_promotion_request.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/local_evidence_promotion_requests"
OUT_JSON = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.local.json"
OUT_MD = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.md"
OUT_CSV = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.csv"
OUT_AUDIT = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST_V0_1.md"
)
GATE = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST_SMOKE: FAIL: "
        + message
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
        "restore_tested_local_evidence_promotion_request_v0_1": True,
        "request_type": "local_evidence_promotion_request_no_closure",
        "request_scope": "human_review_request_only_no_matrix_change_no_blocker_closure",
        "status": "ready_for_human_review_no_closure",
        "target_blocker_id": "restore_tested",
        "source_profile_status": "pass",
        "source_profile_target_blocker_satisfied": True,
        "source_profile_restore_tested_available_for_go_no_go": True,
        "source_profile_production_restore_tested": True,
        "source_profile_satisfied_production_checks": 1,
        "source_profile_production_blocker_count_after_profile": 23,
        "source_profile_blockers_closed": 0,
        "source_profile_production_restore_policy_available": False,
        "canonical_gap_matrix_status": "open",
        "canonical_gap_matrix_local_evidence_ready": False,
        "canonical_gap_matrix_closure_allowed": False,
        "canonical_closure_board_candidate_count": 0,
        "canonical_closure_row_ready_for_human_final_review": False,
        "human_promotion_review_required": True,
        "separate_matrix_update_approval_required": True,
        "separate_blocker_closure_approval_required": True,
        "recommend_for_human_evidence_promotion_review": True,
        "recommend_for_automatic_matrix_update": False,
        "recommend_for_blocker_closure": False,
        "recommend_for_product_launch": False,
        "blockers_closed_by_request": 0,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    false_flags = [
        "promotion_authorized",
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

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 1, "CSV must contain one target row")
    require(rows[0]["target_blocker_id"] == "restore_tested", "CSV target mismatch")
    require(rows[0]["recommend_for_blocker_closure"] == "False", "CSV closure must be false")
    require(rows[0]["blockers_closed_by_request"] == "0", "CSV closed count must be zero")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "restore_tested_local_evidence_promotion_request_v0_1: true",
        "status: ready_for_human_review_no_closure",
        "source_profile_target_blocker_satisfied: true",
        "canonical_gap_matrix_closure_allowed: false",
        "blockers_closed_by_request: 0",
        "recommend_for_human_evidence_promotion_review: true",
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
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "canonical_gap_matrix_modified: true",
        "blockers_closed_by_request: 1",
    ]:
        require(token not in combined, f"forbidden token {token}")

    print(
        "SAEE_RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST_SMOKE: PASS "
        f"status={payload['status']} "
        "target=restore_tested "
        "blockers_closed=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
