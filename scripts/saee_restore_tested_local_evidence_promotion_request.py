#!/usr/bin/env python3
"""Create a human-review request for promoting restore-tested local evidence.

The existing restore-tested profile shows that one local public-shell restore
test can satisfy the `restore_tested` evaluator input. This script makes that
fact reviewable without changing the canonical blocker matrix, closing a
blocker, touching runtime/backend/kernel/API schema, contacting anyone, or
claiming production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
DATA_OPS_DIR = COMMERCIAL_DIR / "data_operations_evidence"
CLOSURE_DIR = COMMERCIAL_DIR / "commercial_blocker_closure_readiness_board"
OUTPUT_DIR = COMMERCIAL_DIR / "local_evidence_promotion_requests"

PROFILE_JSON = DATA_OPS_DIR / "restore_tested_evidence_profile.local.json"
PROFILE_REPORT = DATA_OPS_DIR / "restore_tested_evidence_profile_report.md"
GAP_MATRIX_JSON = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"
CLOSURE_BOARD_JSON = CLOSURE_DIR / "closure_readiness_board.local.json"

OUT_JSON = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.local.json"
OUT_MD = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.md"
OUT_CSV = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.csv"
OUT_AUDIT = OUTPUT_DIR / "restore_tested_local_evidence_promotion_request_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST_GATE.md"

TARGET_BLOCKER_ID = "restore_tested"


FALSE_FLAGS = [
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


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_row(rows: list[dict[str, Any]], blocker_id: str) -> dict[str, Any]:
    for row in rows:
        if row.get("blocker_id") == blocker_id:
            return row
    return {}


def matrix_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("matrix")
    return rows if isinstance(rows, list) else []


def closure_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("blocker_closure_readiness_review")
    return rows if isinstance(rows, list) else []


def build_payload() -> dict[str, Any]:
    profile = read_json(PROFILE_JSON)
    gap_matrix = read_json(GAP_MATRIX_JSON)
    closure_board = read_json(CLOSURE_BOARD_JSON)
    matrix_row = find_row(matrix_rows(gap_matrix), TARGET_BLOCKER_ID)
    closure_row = find_row(closure_rows(closure_board), TARGET_BLOCKER_ID)

    profile_ready = (
        profile.get("status") == "pass"
        and profile.get("target_blocker_satisfied_by_profile") is True
        and profile.get("production_restore_tested") is True
        and profile.get("blockers_closed_by_profile") == 0
        and profile.get("production_ready") is False
    )
    canonical_still_open = (
        matrix_row.get("status") != "closed"
        and matrix_row.get("closure_allowed_by_matrix") is not True
        and closure_row.get("closure_ready_for_human_final_review") is not True
    )
    boundary_violations: list[str] = []
    for source_name, source in [
        ("profile", profile),
        ("gap_matrix", gap_matrix),
        ("closure_board", closure_board),
    ]:
        for flag in [
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "customer_contacted",
            "external_calls_made",
        ]:
            if source.get(flag) is True:
                boundary_violations.append(f"{source_name}.{flag}")

    if boundary_violations:
        status = "stop_boundary_violation"
    elif profile_ready and canonical_still_open:
        status = "ready_for_human_review_no_closure"
    else:
        status = "hold_profile_or_canonical_state_needs_review"

    payload: dict[str, Any] = {
        "restore_tested_local_evidence_promotion_request_v0_1": True,
        "request_type": "local_evidence_promotion_request_no_closure",
        "request_scope": "human_review_request_only_no_matrix_change_no_blocker_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_restore_tested_local_evidence_promotion_request.py",
        "target_blocker_id": TARGET_BLOCKER_ID,
        "source_profile_json": rel(PROFILE_JSON),
        "source_profile_report": rel(PROFILE_REPORT),
        "source_gap_matrix_json": rel(GAP_MATRIX_JSON),
        "source_closure_board_json": rel(CLOSURE_BOARD_JSON),
        "source_profile_status": profile.get("status"),
        "source_profile_target_blocker_satisfied": profile.get(
            "target_blocker_satisfied_by_profile"
        )
        is True,
        "source_profile_restore_tested_available_for_go_no_go": profile.get(
            "restore_tested_available_for_go_no_go"
        )
        is True,
        "source_profile_production_restore_tested": profile.get(
            "production_restore_tested"
        )
        is True,
        "source_profile_satisfied_production_checks": profile.get(
            "profile_satisfied_production_checks", 0
        ),
        "source_profile_total_production_checks": profile.get(
            "profile_total_production_checks", 24
        ),
        "source_profile_production_blocker_count_after_profile": profile.get(
            "profile_production_blocker_count", 24
        ),
        "source_profile_blockers_closed": profile.get("blockers_closed_by_profile", 0),
        "source_profile_production_restore_policy_available": profile.get(
            "production_restore_policy_available"
        )
        is True,
        "canonical_gap_matrix_status": matrix_row.get("status", "missing"),
        "canonical_gap_matrix_local_evidence_ready": matrix_row.get(
            "local_evidence_ready"
        )
        is True,
        "canonical_gap_matrix_closure_allowed": matrix_row.get(
            "closure_allowed_by_matrix"
        )
        is True,
        "canonical_closure_board_status": closure_board.get("status", ""),
        "canonical_closure_board_candidate_count": closure_board.get(
            "closure_candidate_count", 0
        ),
        "canonical_closure_row_status": closure_row.get("closure_status", "missing"),
        "canonical_closure_row_ready_for_human_final_review": closure_row.get(
            "closure_ready_for_human_final_review"
        )
        is True,
        "human_promotion_review_required": True,
        "separate_matrix_update_approval_required": True,
        "separate_blocker_closure_approval_required": True,
        "recommend_for_human_evidence_promotion_review": status
        == "ready_for_human_review_no_closure",
        "recommend_for_automatic_matrix_update": False,
        "recommend_for_blocker_closure": False,
        "recommend_for_product_launch": False,
        "blockers_closed_by_request": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "review_questions": [
            "Does the local public-shell restore drill evidence match the intended restore_tested blocker scope?",
            "Should this profile be promoted into a separate human-approved matrix update request?",
            "What production restore policy evidence is still missing before data operations can be marked ready?",
        ],
        "next_human_action": (
            "Review this request and decide whether to create a separate matrix-update "
            "or blocker-closure request. Do not close restore_tested from this request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "target_blocker_id",
        "status",
        "source_profile_status",
        "source_profile_target_blocker_satisfied",
        "source_profile_satisfied_production_checks",
        "source_profile_production_blocker_count_after_profile",
        "canonical_gap_matrix_status",
        "canonical_gap_matrix_local_evidence_ready",
        "canonical_gap_matrix_closure_allowed",
        "canonical_closure_row_status",
        "recommend_for_human_evidence_promotion_review",
        "recommend_for_blocker_closure",
        "blockers_closed_by_request",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({field: payload.get(field) for field in fields})


def write_docs(payload: dict[str, Any]) -> None:
    status = payload["status"]
    lines = [
        "# SAEE restore_tested 本地证据提升请求",
        "",
        "Restore Tested Local Evidence Promotion Request v0.1",
        "",
        "这不是 blocker 关闭记录。它只把已经存在的本地恢复演练 profile 整理成一个人工审查请求。",
        "",
        "```text",
        "restore_tested_local_evidence_promotion_request_v0_1: true",
        f"status: {status}",
        f"target_blocker_id: {payload['target_blocker_id']}",
        f"source_profile_status: {payload['source_profile_status']}",
        f"source_profile_target_blocker_satisfied: {str(payload['source_profile_target_blocker_satisfied']).lower()}",
        f"source_profile_satisfied_production_checks: {payload['source_profile_satisfied_production_checks']}",
        f"source_profile_production_blocker_count_after_profile: {payload['source_profile_production_blocker_count_after_profile']}",
        f"canonical_gap_matrix_status: {payload['canonical_gap_matrix_status']}",
        f"canonical_gap_matrix_closure_allowed: {str(payload['canonical_gap_matrix_closure_allowed']).lower()}",
        f"canonical_closure_board_candidate_count: {payload['canonical_closure_board_candidate_count']}",
        f"human_promotion_review_required: {str(payload['human_promotion_review_required']).lower()}",
        "promotion_authorized: false",
        "blockers_closed_by_request: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "```",
        "",
        "## 为什么有用",
        "",
        "现有 profile 显示 `restore_tested` 可作为本地恢复演练证据进入人工审查，但正式 blocker 矩阵和 closure board 仍未允许关闭。这个文件把二者分开，避免把 local profile 误写成生产就绪。",
        "",
        "## 人工审查问题",
        "",
    ]
    for question in payload["review_questions"]:
        lines.append(f"- {question}")
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 不修改 gap matrix。",
            "- 不修改 closure board。",
            "- 不关闭 `restore_tested` blocker。",
            "- 不收集外部证据。",
            "- 不联系客户。",
            "- 不发布产品。",
            "- 不声明生产可用。",
        ]
    )
    text = "\n".join(lines) + "\n"
    TOP_DOC.write_text(text, encoding="utf-8")
    OUT_MD.write_text(text, encoding="utf-8")

    audit = [
        "# Restore Tested Promotion Request Boundary Audit",
        "",
        "local_evidence_promotion_request_only: true",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "promotion_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_request: 0",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "private_core_exposed: false",
        "product_launched: false",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "external_calls_made: false",
    ]
    OUT_AUDIT.write_text("\n".join(audit) + "\n", encoding="utf-8")

    gate = [
        "# SAEE Restore Tested Local Evidence Promotion Request Gate",
        "",
        "answer: conditional",
        "recommend_for_human_evidence_promotion_review: true",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "",
        "reason: Local restore-tested profile is available, but the canonical matrix and closure board still require separate human approval before any promotion or closure.",
        "",
        "boundary:",
        "promotion_authorized: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blockers_closed_by_request: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "next_action: Human review only. If accepted, create a separate explicit matrix-update or blocker-closure request.",
    ]
    GATE.write_text("\n".join(gate) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_RESTORE_TESTED_LOCAL_EVIDENCE_PROMOTION_REQUEST: "
        f"{payload['status']} "
        f"target={payload['target_blocker_id']} "
        f"blockers_closed={payload['blockers_closed_by_request']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
