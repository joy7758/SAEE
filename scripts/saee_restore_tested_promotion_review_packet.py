#!/usr/bin/env python3
"""Build a human review packet for the restore_tested promotion decision.

This packet is a decision-prep surface only. It makes the already-generated
restore-tested local evidence promotion request easier to review, but it does
not promote evidence, modify the canonical matrix, close a blocker, contact
customers, launch product, or claim production readiness.
Machine-readable boundary: this packet does not promote evidence.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUTPUT_DIR = COMMERCIAL_DIR / "local_evidence_promotion_requests"

PARTIAL_QUEUE_JSON = (
    COMMERCIAL_DIR
    / "partial_evidence_promotion_queue/partial_evidence_promotion_queue.local.json"
)
PROMOTION_REQUEST_JSON = (
    OUTPUT_DIR / "restore_tested_local_evidence_promotion_request.local.json"
)
PROFILE_JSON = (
    COMMERCIAL_DIR / "data_operations_evidence/restore_tested_evidence_profile.local.json"
)

OUT_JSON = OUTPUT_DIR / "restore_tested_promotion_review_packet.local.json"
OUT_MD = OUTPUT_DIR / "restore_tested_promotion_review_packet.md"
OUT_CSV = OUTPUT_DIR / "restore_tested_promotion_review_packet.csv"
OUT_TEMPLATE = OUTPUT_DIR / "restore_tested_promotion_decision_template.json"
OUT_AUDIT = OUTPUT_DIR / "restore_tested_promotion_review_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "RESTORE_TESTED_PROMOTION_REVIEW_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_PROMOTION_REVIEW_PACKET_GATE.md"

TARGET_BLOCKER_ID = "restore_tested"

FALSE_FLAGS = [
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


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_queue_row(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("queue_rows", [])
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_id") == TARGET_BLOCKER_ID:
            return row
    return {}


def build_payload() -> dict[str, Any]:
    queue = read_json(PARTIAL_QUEUE_JSON)
    promotion_request = read_json(PROMOTION_REQUEST_JSON)
    profile = read_json(PROFILE_JSON)
    queue_row = find_queue_row(queue)

    source_ready = (
        queue_row.get("review_status") == "ready_for_human_promotion_review_no_closure"
        and promotion_request.get("status") == "ready_for_human_review_no_closure"
        and profile.get("status") == "pass"
        and profile.get("target_blocker_satisfied_by_profile") is True
    )

    boundary_violations: list[str] = []
    for source_name, source in [
        ("partial_queue", queue),
        ("promotion_request", promotion_request),
        ("profile", profile),
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
    elif source_ready:
        status = "hold_human_promotion_decision_required"
    else:
        status = "hold_source_evidence_not_ready_for_review"

    payload: dict[str, Any] = {
        "restore_tested_promotion_review_packet_v0_1": True,
        "packet_type": "human_promotion_review_packet_no_execution",
        "packet_scope": "decision_template_only_no_matrix_change_no_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_restore_tested_promotion_review_packet.py",
        "target_blocker_id": TARGET_BLOCKER_ID,
        "source_partial_queue_json": rel(PARTIAL_QUEUE_JSON),
        "source_promotion_request_json": rel(PROMOTION_REQUEST_JSON),
        "source_profile_json": rel(PROFILE_JSON),
        "source_partial_queue_status": queue.get("status", ""),
        "source_partial_queue_review_status": queue_row.get("review_status", "missing"),
        "source_promotion_request_status": promotion_request.get("status", ""),
        "source_profile_status": profile.get("status", ""),
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
        "human_decision_required": True,
        "human_decision_allowed_values": [
            "approve_separate_matrix_update_request",
            "hold",
            "reject",
        ],
        "recommended_default_decision": "hold",
        "recommended_default_reason": (
            "The local restore-tested evidence is reviewable, but approving matrix "
            "updates or blocker closure still requires a separate explicit request."
        ),
        "human_review_questions": [
            "Does the local restore drill evidence match the restore_tested blocker scope?",
            "Is a separate matrix-update request justified, or should this remain on hold?",
            "What evidence is still missing before data operations readiness can be closed?",
        ],
        "blockers_closed_by_packet": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "next_human_action": (
            "Fill restore_tested_promotion_decision_template.json only if a human "
            "wants to approve, hold, or reject a future separate matrix-update request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def build_decision_template(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_type": "restore_tested_promotion_human_decision_input",
        "target_blocker_id": TARGET_BLOCKER_ID,
        "source_packet": rel(OUT_JSON),
        "allowed_decision_values": payload["human_decision_allowed_values"],
        "decision": "",
        "human_reviewer": "",
        "decision_date": "",
        "reason": "",
        "authorize_separate_matrix_update_request": False,
        "authorize_blocker_closure": False,
        "authorize_product_launch": False,
        "notes": "",
    }


def write_json(payload: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_TEMPLATE.write_text(
        json.dumps(build_decision_template(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "target_blocker_id",
        "status",
        "source_partial_queue_review_status",
        "source_promotion_request_status",
        "source_profile_status",
        "source_profile_target_blocker_satisfied",
        "recommended_default_decision",
        "human_decision_required",
        "matrix_update_authorized",
        "blocker_closure_authorized",
        "blockers_closed_by_packet",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({field: payload.get(field) for field in fields})


def write_docs(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE restore_tested 提升审查包",
        "",
        "Restore Tested Promotion Review Packet v0.1",
        "",
        "这个文件只帮助人工审查 `restore_tested` 是否值得进入单独的 matrix-update 请求。它不执行提升、不修改矩阵、不关闭 blocker。",
        "",
        "```text",
        "restore_tested_promotion_review_packet_v0_1: true",
        f"status: {payload['status']}",
        f"target_blocker_id: {payload['target_blocker_id']}",
        f"source_partial_queue_review_status: {payload['source_partial_queue_review_status']}",
        f"source_promotion_request_status: {payload['source_promotion_request_status']}",
        f"source_profile_status: {payload['source_profile_status']}",
        f"source_profile_target_blocker_satisfied: {str(payload['source_profile_target_blocker_satisfied']).lower()}",
        f"recommended_default_decision: {payload['recommended_default_decision']}",
        "human_decision_required: true",
        "human_decision_recorded: false",
        "matrix_update_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_packet: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "```",
        "",
        "## 人工审查问题",
        "",
    ]
    for question in payload["human_review_questions"]:
        lines.append(f"- {question}")
    lines.extend(
        [
            "",
            "## 默认决策",
            "",
            "- 默认保持 `hold`。",
            "- 如需推进，必须另行创建单独的 matrix-update 或 blocker-closure 请求。",
            "- 本包不能单独作为关闭 `restore_tested` 的证据。",
            "",
            "## 相关文件",
            "",
            f"- `{payload['source_partial_queue_json']}`",
            f"- `{payload['source_promotion_request_json']}`",
            f"- `{payload['source_profile_json']}`",
            f"- `{rel(OUT_TEMPLATE)}`",
        ]
    )
    text = "\n".join(lines) + "\n"
    TOP_DOC.write_text(text, encoding="utf-8")
    OUT_MD.write_text(text, encoding="utf-8")

    audit = [
        "# Restore Tested Promotion Review Packet Boundary Audit",
        "",
        "review_packet_only: true",
        "human_decision_recorded: false",
        "promotion_authorized: false",
        "matrix_update_authorized: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_packet: 0",
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
        "# SAEE Restore Tested Promotion Review Packet Gate",
        "",
        "answer: conditional",
        "recommend_for_human_promotion_decision_review: true",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "",
        "reason: restore_tested has reviewable local evidence, but any matrix update or closure requires a separate explicit human-approved request.",
        "",
        "boundary:",
        "human_decision_recorded: false",
        "promotion_authorized: false",
        "matrix_update_authorized: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_packet: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "next_action: Human may fill restore_tested_promotion_decision_template.json; no execution is authorized by this packet.",
    ]
    GATE.write_text("\n".join(gate) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_RESTORE_TESTED_PROMOTION_REVIEW_PACKET: "
        f"{payload['status']} "
        "target=restore_tested "
        "human_decision_recorded=false "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
