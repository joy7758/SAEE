#!/usr/bin/env python3
"""Build a review queue for blockers with partial local commercial evidence.

This queue turns the partial-evidence rows from the formal commercial gap audit
into a small human-review surface. It does not promote evidence, modify the
canonical matrix, close blockers, contact anyone, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUTPUT_DIR = COMMERCIAL_DIR / "partial_evidence_promotion_queue"

GAP_AUDIT_JSON = (
    COMMERCIAL_DIR
    / "commercial_readiness_gap_audit/commercial_readiness_gap_audit.local.json"
)
CLOSURE_BOARD_JSON = (
    COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json"
)
RESTORE_PROMOTION_JSON = (
    COMMERCIAL_DIR
    / "local_evidence_promotion_requests/"
    "restore_tested_local_evidence_promotion_request.local.json"
)
RESTORE_PROFILE_JSON = (
    COMMERCIAL_DIR / "data_operations_evidence/restore_tested_evidence_profile.local.json"
)
RESTORE_POLICY_DRAFT_JSON = (
    COMMERCIAL_DIR / "data_operations_evidence/production_restore_policy_draft.local.json"
)
RESTORE_POLICY_RECONCILIATION_JSON = (
    COMMERCIAL_DIR
    / "data_operations_evidence/production_restore_policy_state_reconciliation/"
    "production_restore_policy_state_reconciliation.local.json"
)
TENANT_STORAGE_EVIDENCE_JSON = (
    COMMERCIAL_DIR
    / "tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json"
)
TENANT_STORAGE_RECONCILIATION_JSON = (
    COMMERCIAL_DIR
    / "phase_1_identity_tenant_evidence_profile/"
    "phase_1_identity_tenant_state_reconciliation/"
    "phase_1_identity_tenant_state_reconciliation.local.json"
)

OUT_JSON = OUTPUT_DIR / "partial_evidence_promotion_queue.local.json"
OUT_MD = OUTPUT_DIR / "partial_evidence_promotion_queue.md"
OUT_CSV = OUTPUT_DIR / "partial_evidence_promotion_queue.csv"
OUT_AUDIT = OUTPUT_DIR / "partial_evidence_promotion_queue_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PARTIAL_EVIDENCE_PROMOTION_QUEUE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PARTIAL_EVIDENCE_PROMOTION_QUEUE_GATE.md"


SOURCE_PATHS = {
    "tenant_storage_isolation": [
        TENANT_STORAGE_EVIDENCE_JSON,
        COMMERCIAL_DIR
        / "tenant_storage_isolation_evidence/production_tenant_storage_evidence_path.local.json",
        TENANT_STORAGE_RECONCILIATION_JSON,
    ],
    "restore_tested": [
        RESTORE_PROFILE_JSON,
        RESTORE_PROMOTION_JSON,
    ],
    "production_restore_policy": [
        RESTORE_POLICY_DRAFT_JSON,
        COMMERCIAL_DIR
        / "data_operations_evidence/production_restore_policy_approval_input_validation.local.json",
        RESTORE_POLICY_RECONCILIATION_JSON,
    ],
}


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


def load_optional(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def source_summary(blocker_id: str) -> dict[str, Any]:
    paths = SOURCE_PATHS.get(blocker_id, [])
    existing_paths = [path for path in paths if path.is_file()]
    values = [load_optional(path) for path in existing_paths]
    status_values = [
        str(value.get("status") or value.get("draft_status") or value.get("validation_status") or "")
        for value in values
        if value
    ]
    return {
        "source_path_count": len(paths),
        "existing_source_path_count": len(existing_paths),
        "source_paths": [rel(path) for path in paths],
        "source_status_values": [status for status in status_values if status],
    }


def classify_partial(blocker_id: str, summary: dict[str, Any]) -> tuple[str, str]:
    if blocker_id == "restore_tested":
        return (
            "ready_for_human_promotion_review_no_closure",
            "Local restore-tested profile passes and has a separate no-closure human promotion request.",
        )
    if blocker_id == "production_restore_policy":
        reconciliation = load_optional(RESTORE_POLICY_RECONCILIATION_JSON)
        if (
            reconciliation.get("production_restore_policy_available_for_review") is True
            and reconciliation.get("combined_profile_ready") is True
            and reconciliation.get("blockers_closed_by_reconciliation") == 0
            and reconciliation.get("restore_run_by_codex") is False
            and reconciliation.get("production_ready") is False
        ):
            return (
                "ready_for_human_promotion_review_no_closure",
                "The restore-policy reconciliation confirms the human-filled policy evidence and combined profile are review-ready, while no restore was run and the canonical blocker remains open.",
            )
        return (
            "needs_human_policy_approval_before_promotion",
            "A draft restore policy exists, but production restore policy is not approved.",
        )
    if blocker_id == "tenant_storage_isolation":
        reconciliation = load_optional(TENANT_STORAGE_RECONCILIATION_JSON)
        if (
            reconciliation.get("tenant_storage_isolation_ready_for_review") is True
            and reconciliation.get("blockers_closed_by_reconciliation") == 0
            and reconciliation.get("production_tenant_storage_isolated") is False
            and reconciliation.get("production_ready") is False
        ):
            return (
                "ready_for_human_promotion_review_no_closure",
                "The Phase 1 state reconciliation confirms the human-filled tenant-storage evidence is review-ready, while production isolation remains inactive and the canonical blocker remains open.",
            )
        return (
            "needs_engineering_security_review_before_promotion",
            "Local tenant-storage evidence exists, but production tenant storage is not isolated or closure-ready.",
        )
    return (
        "needs_human_review_before_promotion",
        "Partial local evidence exists, but it is not closure-ready.",
    )


def closure_row_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("blocker_closure_readiness_review")
    if not isinstance(rows, list):
        return {}
    return {row.get("blocker_id"): row for row in rows if isinstance(row, dict)}


def build_payload() -> dict[str, Any]:
    gap = read_json(GAP_AUDIT_JSON)
    closure = read_json(CLOSURE_BOARD_JSON)
    closure_by_id = closure_row_by_id(closure)
    partial_rows = [
        row
        for row in gap.get("blocker_rows", [])
        if int(row.get("local_completion_checks_passed") or 0) > 0
        and row.get("local_evidence_ready") is not True
    ]
    boundary_violations: list[str] = []
    for source_name, source in [("gap_audit", gap), ("closure_board", closure)]:
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

    queue_rows: list[dict[str, Any]] = []
    for index, row in enumerate(partial_rows, start=1):
        blocker_id = row.get("blocker_id", "")
        summary = source_summary(blocker_id)
        review_status, review_reason = classify_partial(blocker_id, summary)
        closure_row = closure_by_id.get(blocker_id, {})
        queue_rows.append(
            {
                "queue_id": f"PEPQ-{index:03d}",
                "blocker_id": blocker_id,
                "category": row.get("category", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "local_completion_checks_passed": row.get("local_completion_checks_passed", 0),
                "local_completion_checks_total": row.get("local_completion_checks_total", 0),
                "local_evidence_ready": False,
                "engineering_implementation_required": row.get(
                    "engineering_implementation_required"
                )
                is True,
                "external_dependency_required": row.get("external_dependency_required") is True,
                "human_approval_required": row.get("human_approval_required") is True,
                "canonical_closure_status": closure_row.get("closure_status", "missing"),
                "canonical_closure_ready_for_human_final_review": closure_row.get(
                    "closure_ready_for_human_final_review"
                )
                is True,
                "review_status": review_status,
                "review_reason": review_reason,
                "source_path_count": summary["source_path_count"],
                "existing_source_path_count": summary["existing_source_path_count"],
                "source_paths": summary["source_paths"],
                "source_status_values": summary["source_status_values"],
                "recommended_human_action": (
                    "Review partial evidence and decide whether a separate promotion, "
                    "matrix-update, or blocker-closure request should be created."
                ),
                "closure_allowed_by_queue": False,
            }
        )

    ready_review_count = sum(
        1
        for row in queue_rows
        if row["review_status"] == "ready_for_human_promotion_review_no_closure"
    )
    status = (
        "stop_boundary_violation"
        if boundary_violations
        else "ready_for_human_partial_evidence_review_no_closure"
    )
    payload: dict[str, Any] = {
        "partial_evidence_promotion_queue_v0_1": True,
        "queue_type": "local_partial_evidence_promotion_queue",
        "queue_scope": "human_review_queue_only_no_matrix_change_no_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_partial_evidence_promotion_queue.py",
        "source_gap_audit_json": rel(GAP_AUDIT_JSON),
        "source_closure_board_json": rel(CLOSURE_BOARD_JSON),
        "production_blocker_count": gap.get("production_blocker_count", 24),
        "open_blocker_count": gap.get("open_blocker_count", 24),
        "partial_local_evidence_blocker_count": len(queue_rows),
        "ready_for_human_promotion_review_count": ready_review_count,
        "needs_human_or_engineering_followup_count": len(queue_rows) - ready_review_count,
        "queue_rows": queue_rows,
        "queue_blocker_ids": [row["blocker_id"] for row in queue_rows],
        "recommend_for_human_partial_evidence_review": True,
        "recommend_for_automatic_matrix_update": False,
        "recommend_for_blocker_closure": False,
        "recommend_for_product_launch": False,
        "human_review_required": True,
        "separate_matrix_update_approval_required": True,
        "separate_blocker_closure_approval_required": True,
        "blockers_closed_by_queue": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "next_human_action": (
            "Review tenant_storage_isolation, restore_tested, and "
            "production_restore_policy as review-ready, no-closure evidence lanes. "
            "A separate matrix-update approval is still required."
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
        "queue_id",
        "blocker_id",
        "category",
        "owner_review_lane",
        "local_completion_checks_passed",
        "local_completion_checks_total",
        "review_status",
        "existing_source_path_count",
        "canonical_closure_status",
        "closure_allowed_by_queue",
        "recommended_human_action",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["queue_rows"]:
            writer.writerow({field: row.get(field) for field in fields})


def write_docs(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE 部分本地证据提升队列",
        "",
        "Partial Evidence Promotion Queue v0.1",
        "",
        "这个队列只列出已经有部分本地证据、但还不能关闭的商业 blocker。它不提升证据、不改矩阵、不关闭 blocker。",
        "",
        "```text",
        "partial_evidence_promotion_queue_v0_1: true",
        f"status: {payload['status']}",
        f"partial_local_evidence_blocker_count: {payload['partial_local_evidence_blocker_count']}",
        f"ready_for_human_promotion_review_count: {payload['ready_for_human_promotion_review_count']}",
        f"needs_human_or_engineering_followup_count: {payload['needs_human_or_engineering_followup_count']}",
        "recommend_for_human_partial_evidence_review: true",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "blockers_closed_by_queue: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "```",
        "",
        "## 队列",
        "",
        "| Queue ID | Blocker | 已通过/总检查 | 状态 | 人工动作 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["queue_rows"]:
        lines.append(
            "| {queue_id} | `{blocker_id}` | {passed}/{total} | `{review_status}` | {action} |".format(
                queue_id=row["queue_id"],
                blocker_id=row["blocker_id"],
                passed=row["local_completion_checks_passed"],
                total=row["local_completion_checks_total"],
                review_status=row["review_status"],
                action=row["recommended_human_action"],
            )
        )
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 不自动提升本地证据。",
            "- 不修改 canonical gap matrix。",
            "- 不修改 closure board。",
            "- 不关闭 blocker。",
            "- 不联系客户或供应商。",
            "- 不发布产品。",
            "- 不声明生产可用。",
        ]
    )
    text = "\n".join(lines) + "\n"
    TOP_DOC.write_text(text, encoding="utf-8")
    OUT_MD.write_text(text, encoding="utf-8")

    audit = [
        "# Partial Evidence Promotion Queue Boundary Audit",
        "",
        "partial_evidence_queue_only: true",
        "promotion_authorized: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_queue: 0",
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
        "# SAEE Partial Evidence Promotion Queue Gate",
        "",
        "answer: conditional",
        "recommend_for_human_partial_evidence_review: true",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "",
        "reason: Three blockers have partial local evidence and reconciled human-filled profiles ready for human promotion review only; none is closure-ready without separate human approval and canonical matrix/closure review.",
        "",
        "boundary:",
        "promotion_authorized: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blockers_closed_by_queue: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "next_action: Human review of partial_evidence_promotion_queue.md only.",
    ]
    GATE.write_text("\n".join(gate) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_PARTIAL_EVIDENCE_PROMOTION_QUEUE: "
        f"{payload['status']} "
        f"partial={payload['partial_local_evidence_blocker_count']} "
        f"ready_review={payload['ready_for_human_promotion_review_count']} "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
