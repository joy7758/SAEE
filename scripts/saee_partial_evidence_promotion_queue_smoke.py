#!/usr/bin/env python3
"""Smoke test for the SAEE partial evidence promotion queue."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_partial_evidence_promotion_queue.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/partial_evidence_promotion_queue"
OUT_JSON = OUTPUT_DIR / "partial_evidence_promotion_queue.local.json"
OUT_MD = OUTPUT_DIR / "partial_evidence_promotion_queue.md"
OUT_CSV = OUTPUT_DIR / "partial_evidence_promotion_queue.csv"
OUT_AUDIT = OUTPUT_DIR / "partial_evidence_promotion_queue_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PARTIAL_EVIDENCE_PROMOTION_QUEUE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PARTIAL_EVIDENCE_PROMOTION_QUEUE_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_PARTIAL_EVIDENCE_PROMOTION_QUEUE_SMOKE: FAIL: " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_AUDIT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "partial_evidence_promotion_queue_v0_1": True,
        "queue_type": "local_partial_evidence_promotion_queue",
        "queue_scope": "human_review_queue_only_no_matrix_change_no_closure",
        "status": "ready_for_human_partial_evidence_review_no_closure",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "partial_local_evidence_blocker_count": 3,
        "ready_for_human_promotion_review_count": 3,
        "needs_human_or_engineering_followup_count": 0,
        "recommend_for_human_partial_evidence_review": True,
        "recommend_for_automatic_matrix_update": False,
        "recommend_for_blocker_closure": False,
        "recommend_for_product_launch": False,
        "human_review_required": True,
        "separate_matrix_update_approval_required": True,
        "separate_blocker_closure_approval_required": True,
        "blockers_closed_by_queue": 0,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    require(
        payload.get("queue_blocker_ids")
        == ["tenant_storage_isolation", "restore_tested", "production_restore_policy"],
        "queue blocker order changed",
    )
    rows = payload.get("queue_rows", [])
    require(len(rows) == 3, "queue must contain three rows")
    by_id = {row["blocker_id"]: row for row in rows}
    require(
        by_id["restore_tested"]["review_status"]
        == "ready_for_human_promotion_review_no_closure",
        "restore_tested review status changed",
    )
    require(
        by_id["production_restore_policy"]["review_status"]
        == "ready_for_human_promotion_review_no_closure",
        "production_restore_policy review status changed",
    )
    require(
        by_id["production_restore_policy"]["existing_source_path_count"] == 3,
        "restore policy reconciliation source must be present",
    )
    require(
        by_id["tenant_storage_isolation"]["review_status"]
        == "ready_for_human_promotion_review_no_closure",
        "tenant_storage_isolation review status changed",
    )
    require(
        by_id["tenant_storage_isolation"]["existing_source_path_count"] == 3,
        "tenant storage reconciliation source must be present",
    )
    for row in rows:
        require(row["closure_allowed_by_queue"] is False, "queue must not allow closure")
        require(row["canonical_closure_ready_for_human_final_review"] is False, "canonical closure must remain false")

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

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 3, "CSV must contain three rows")
    require(
        all(row["closure_allowed_by_queue"] == "False" for row in csv_rows),
        "CSV closure allowed must be false",
    )

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "partial_evidence_promotion_queue_v0_1: true",
        "status: ready_for_human_partial_evidence_review_no_closure",
        "partial_local_evidence_blocker_count: 3",
        "ready_for_human_promotion_review_count: 3",
        "needs_human_or_engineering_followup_count: 0",
        "recommend_for_human_partial_evidence_review: true",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "blockers_closed_by_queue: 0",
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
        "blockers_closed_by_queue: 1",
    ]:
        require(token not in combined, f"forbidden token {token}")

    print(
        "SAEE_PARTIAL_EVIDENCE_PROMOTION_QUEUE_SMOKE: PASS "
        f"status={payload['status']} "
        "partial=3 ready_review=3 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
