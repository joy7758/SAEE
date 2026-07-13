#!/usr/bin/env python3
"""Smoke test for the restore_tested promotion review packet."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_restore_tested_promotion_review_packet.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/local_evidence_promotion_requests"
OUT_JSON = OUTPUT_DIR / "restore_tested_promotion_review_packet.local.json"
OUT_MD = OUTPUT_DIR / "restore_tested_promotion_review_packet.md"
OUT_CSV = OUTPUT_DIR / "restore_tested_promotion_review_packet.csv"
OUT_TEMPLATE = OUTPUT_DIR / "restore_tested_promotion_decision_template.json"
OUT_AUDIT = OUTPUT_DIR / "restore_tested_promotion_review_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/RESTORE_TESTED_PROMOTION_REVIEW_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_PROMOTION_REVIEW_PACKET_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_RESTORE_TESTED_PROMOTION_REVIEW_PACKET_SMOKE: FAIL: " + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_TEMPLATE, OUT_AUDIT, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "restore_tested_promotion_review_packet_v0_1": True,
        "packet_type": "human_promotion_review_packet_no_execution",
        "packet_scope": "decision_template_only_no_matrix_change_no_closure",
        "status": "hold_human_promotion_decision_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "restore_tested",
        "source_partial_queue_review_status": "ready_for_human_promotion_review_no_closure",
        "source_promotion_request_status": "ready_for_human_review_no_closure",
        "source_profile_status": "pass",
        "source_profile_target_blocker_satisfied": True,
        "source_profile_restore_tested_available_for_go_no_go": True,
        "source_profile_production_restore_tested": True,
        "source_profile_satisfied_production_checks": 1,
        "source_profile_production_blocker_count_after_profile": 23,
        "source_profile_blockers_closed": 0,
        "source_profile_production_restore_policy_available": False,
        "human_decision_required": True,
        "recommended_default_decision": "hold",
        "blockers_closed_by_packet": 0,
        "boundary_violation_count": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(
        payload.get("human_decision_allowed_values")
        == ["approve_separate_matrix_update_request", "hold", "reject"],
        "allowed decision values changed",
    )

    false_flags = [
        "human_decision_recorded",
        "promotion_authorized",
        "matrix_update_authorized",
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

    template = json.loads(OUT_TEMPLATE.read_text(encoding="utf-8"))
    require(template.get("decision") == "", "template decision must be blank")
    require(
        template.get("authorize_separate_matrix_update_request") is False,
        "template must not authorize matrix update by default",
    )
    require(
        template.get("authorize_blocker_closure") is False,
        "template must not authorize blocker closure by default",
    )
    require(
        template.get("authorize_product_launch") is False,
        "template must not authorize product launch by default",
    )

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 1, "CSV must contain one target row")
    require(rows[0]["target_blocker_id"] == "restore_tested", "CSV target mismatch")
    require(rows[0]["recommended_default_decision"] == "hold", "CSV default decision mismatch")
    require(rows[0]["matrix_update_authorized"] == "False", "CSV matrix update must be false")
    require(rows[0]["blocker_closure_authorized"] == "False", "CSV closure must be false")
    require(rows[0]["blockers_closed_by_packet"] == "0", "CSV closed count must be zero")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_AUDIT, TOP_DOC, GATE]
    )
    for token in [
        "restore_tested_promotion_review_packet_v0_1: true",
        "status: hold_human_promotion_decision_required",
        "source_partial_queue_review_status: ready_for_human_promotion_review_no_closure",
        "source_promotion_request_status: ready_for_human_review_no_closure",
        "source_profile_target_blocker_satisfied: true",
        "recommended_default_decision: hold",
        "human_decision_recorded: false",
        "matrix_update_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_packet: 0",
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
        "human_decision_recorded: true",
        "matrix_update_authorized: true",
        "blocker_closure_authorized: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_product_launch: true",
        "blockers_closed_by_packet: 1",
    ]:
        require(token not in combined, f"forbidden token {token}")

    print(
        "SAEE_RESTORE_TESTED_PROMOTION_REVIEW_PACKET_SMOKE: PASS "
        f"status={payload['status']} "
        "target=restore_tested "
        "human_decision_recorded=false blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
