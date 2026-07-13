#!/usr/bin/env python3
"""Validate human input for the restore_tested promotion decision template.

This validator is intentionally non-executing. It can tell whether the human
decision template is blank, valid for a future separate matrix-update request,
or invalid. It does not update the canonical matrix, close blockers, launch
product, contact customers, or claim production readiness.
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

PACKET_JSON = OUTPUT_DIR / "restore_tested_promotion_review_packet.local.json"
DECISION_TEMPLATE_JSON = OUTPUT_DIR / "restore_tested_promotion_decision_template.json"

OUT_JSON = OUTPUT_DIR / "restore_tested_promotion_decision_validation.local.json"
OUT_MD = OUTPUT_DIR / "restore_tested_promotion_decision_validation.md"
OUT_CSV = OUTPUT_DIR / "restore_tested_promotion_decision_validation.csv"
OUT_AUDIT = OUTPUT_DIR / "restore_tested_promotion_decision_validation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR_GATE.md"

TARGET_BLOCKER_ID = "restore_tested"

FALSE_FLAGS = [
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


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def build_payload() -> dict[str, Any]:
    packet = read_json(PACKET_JSON)
    template = read_json(DECISION_TEMPLATE_JSON)
    allowed_values = packet.get("human_decision_allowed_values", [])
    decision = str(template.get("decision") or "").strip()
    reason = str(template.get("reason") or "").strip()
    reviewer = str(template.get("human_reviewer") or "").strip()
    decision_date = str(template.get("decision_date") or "").strip()
    authorize_matrix_update = template.get("authorize_separate_matrix_update_request") is True
    authorize_closure = template.get("authorize_blocker_closure") is True
    authorize_launch = template.get("authorize_product_launch") is True

    boundary_violations: list[str] = []
    for source_name, source in [("packet", packet), ("template", template)]:
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
    if authorize_closure:
        boundary_violations.append("template.authorize_blocker_closure")
    if authorize_launch:
        boundary_violations.append("template.authorize_product_launch")

    decision_fields_complete = bool(
        decision and reason and reviewer and decision_date and decision in allowed_values
    )
    matrix_update_request_ready = bool(
        decision == "approve_separate_matrix_update_request"
        and decision_fields_complete
        and authorize_matrix_update
        and not authorize_closure
        and not authorize_launch
    )
    final_hold_recorded = bool(
        decision == "hold"
        and decision_fields_complete
        and not authorize_matrix_update
        and not authorize_closure
        and not authorize_launch
    )
    final_reject_recorded = bool(
        decision == "reject"
        and decision_fields_complete
        and not authorize_matrix_update
        and not authorize_closure
        and not authorize_launch
    )

    if boundary_violations:
        status = "stop_boundary_violation"
    elif not decision:
        status = "hold_human_decision_missing"
    elif decision not in allowed_values:
        status = "stop_invalid_decision_value"
    elif matrix_update_request_ready:
        status = "ready_for_separate_matrix_update_request_no_closure"
    elif final_hold_recorded:
        status = "final_hold_recorded_no_action"
    elif final_reject_recorded:
        status = "final_reject_recorded_no_action"
    else:
        status = "hold_incomplete_or_inconsistent_human_decision"

    payload: dict[str, Any] = {
        "restore_tested_promotion_decision_validator_v0_1": True,
        "validator_type": "human_promotion_decision_input_validator_no_execution",
        "validator_scope": "validate_decision_template_only_no_matrix_change_no_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_restore_tested_promotion_decision_validator.py",
        "target_blocker_id": TARGET_BLOCKER_ID,
        "source_packet_json": rel(PACKET_JSON),
        "source_decision_template_json": rel(DECISION_TEMPLATE_JSON),
        "source_packet_status": packet.get("status", ""),
        "allowed_decision_values": allowed_values,
        "decision": decision,
        "human_reviewer_present": bool(reviewer),
        "decision_date_present": bool(decision_date),
        "reason_present": bool(reason),
        "decision_fields_complete": decision_fields_complete,
        "authorize_separate_matrix_update_request": authorize_matrix_update,
        "authorize_blocker_closure": authorize_closure,
        "authorize_product_launch": authorize_launch,
        "matrix_update_request_ready": matrix_update_request_ready,
        "final_hold_recorded": final_hold_recorded,
        "final_reject_recorded": final_reject_recorded,
        "matrix_update_executed": False,
        "blockers_closed_by_validator": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "next_human_action": (
            "Fill decision, human_reviewer, decision_date, and reason in the "
            "decision template if a human wants to record approve, hold, or reject. "
            "A ready validator output still requires a separate execution request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "target_blocker_id",
        "status",
        "decision",
        "decision_fields_complete",
        "authorize_separate_matrix_update_request",
        "authorize_blocker_closure",
        "authorize_product_launch",
        "matrix_update_request_ready",
        "blockers_closed_by_validator",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({field: payload.get(field) for field in fields})


def write_docs(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE restore_tested 提升决策验证器",
        "",
        "Restore Tested Promotion Decision Validator v0.1",
        "",
        "这个验证器只检查人工决策模板是否完整、是否安全。它不执行 matrix update，也不关闭 blocker。",
        "",
        "```text",
        "restore_tested_promotion_decision_validator_v0_1: true",
        f"status: {payload['status']}",
        f"target_blocker_id: {payload['target_blocker_id']}",
        f"source_packet_status: {payload['source_packet_status']}",
        f"decision: {payload['decision'] or 'missing'}",
        f"decision_fields_complete: {str(payload['decision_fields_complete']).lower()}",
        f"authorize_separate_matrix_update_request: {str(payload['authorize_separate_matrix_update_request']).lower()}",
        f"authorize_blocker_closure: {str(payload['authorize_blocker_closure']).lower()}",
        f"authorize_product_launch: {str(payload['authorize_product_launch']).lower()}",
        f"matrix_update_request_ready: {str(payload['matrix_update_request_ready']).lower()}",
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "```",
        "",
        "## 允许的人工决策",
        "",
    ]
    for value in payload["allowed_decision_values"]:
        lines.append(f"- `{value}`")
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            "- 当前默认模板为空，因此状态应保持 `hold_human_decision_missing`。",
            "- 即使未来验证结果为 `ready_for_separate_matrix_update_request_no_closure`，仍需要单独执行请求。",
            "- 本验证器不能直接修改 canonical gap matrix 或 closure board。",
        ]
    )
    text = "\n".join(lines) + "\n"
    TOP_DOC.write_text(text, encoding="utf-8")
    OUT_MD.write_text(text, encoding="utf-8")

    audit = [
        "# Restore Tested Promotion Decision Validator Boundary Audit",
        "",
        "validator_only: true",
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_validator: 0",
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
        "# SAEE Restore Tested Promotion Decision Validator Gate",
        "",
        "answer: hold",
        "recommend_for_human_decision_validation: true",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "",
        "reason: The validator can check a human decision template, but it cannot execute a matrix update or close restore_tested.",
        "",
        "boundary:",
        "matrix_update_executed: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_validator: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "next_action: Human may fill the decision template, then rerun this validator.",
    ]
    GATE.write_text("\n".join(gate) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_RESTORE_TESTED_PROMOTION_DECISION_VALIDATOR: "
        f"{payload['status']} "
        "target=restore_tested "
        f"matrix_update_ready={str(payload['matrix_update_request_ready']).lower()} "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
