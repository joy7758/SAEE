#!/usr/bin/env python3
"""Build the remaining-gap packet for tenant_storage_isolation.

The phase-1 gap audit already shows that tenant_storage_isolation has 14 of 18
local public-shell evidence items present. This packet extracts the remaining
four production evidence gaps into a narrow human review template. It does not
change storage behavior, run migrations, update the canonical matrix, close a
blocker, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUTPUT_DIR = COMMERCIAL_DIR / "tenant_storage_isolation_evidence"

GAP_AUDIT_JSON = (
    COMMERCIAL_DIR
    / "phase_1_identity_tenant_gap_audit/phase_1_identity_tenant_gap_audit.local.json"
)
TENANT_EVIDENCE_JSON = OUTPUT_DIR / "tenant_storage_isolation_evidence.local.json"
SECURITY_REVIEW_PACKET_JSON = OUTPUT_DIR / "tenant_security_privacy_review_packet.local.json"
APPROVAL_VALIDATION_JSON = (
    COMMERCIAL_DIR
    / "phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_validation.local.json"
)

OUT_JSON = OUTPUT_DIR / "tenant_storage_remaining_gap_packet.local.json"
OUT_MD = OUTPUT_DIR / "tenant_storage_remaining_gap_packet.md"
OUT_CSV = OUTPUT_DIR / "tenant_storage_remaining_gap_packet.csv"
OUT_TEMPLATE = OUTPUT_DIR / "tenant_storage_remaining_gap_decision_template.json"
OUT_AUDIT = OUTPUT_DIR / "tenant_storage_remaining_gap_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "TENANT_STORAGE_REMAINING_GAP_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_TENANT_STORAGE_REMAINING_GAP_PACKET_GATE.md"

TARGET_BLOCKER_ID = "tenant_storage_isolation"

FALSE_FLAGS = [
    "human_decision_recorded",
    "remaining_gap_approval_recorded",
    "evidence_collection_authorized",
    "execution_authorized",
    "development_permission_granted",
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
    "production_database_modified",
    "storage_behavior_modified",
    "migration_executed",
    "live_customer_data_migrated",
    "customer_data_processed",
    "customer_data_processing_started",
    "production_tenant_storage_enabled",
    "production_tenant_storage_isolated",
    "tenant_storage_isolated",
    "tenant_authorization_enabled",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tenant_rows(gap: dict[str, Any]) -> list[dict[str, Any]]:
    rows = gap.get("gap_rows", [])
    return [
        row
        for row in rows
        if isinstance(row, dict) and row.get("blocker_id") == TARGET_BLOCKER_ID
    ]


def build_payload() -> dict[str, Any]:
    gap = read_json(GAP_AUDIT_JSON)
    tenant_evidence = read_json(TENANT_EVIDENCE_JSON)
    security_packet = read_json(SECURITY_REVIEW_PACKET_JSON)
    approval_validation = read_json(APPROVAL_VALIDATION_JSON)

    rows = tenant_rows(gap)
    present_rows = [
        row
        for row in rows
        if row.get("local_public_shell_value") is True
        and row.get("accepted_for_blocker_closure") is False
    ]
    missing_rows = [
        row for row in rows if row.get("local_public_shell_value") is not True
    ]

    boundary_violations: list[str] = []
    for source_name, source in [
        ("gap_audit", gap),
        ("tenant_evidence", tenant_evidence),
        ("security_packet", security_packet),
        ("approval_validation", approval_validation),
    ]:
        for flag in [
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "customer_contacted",
            "external_calls_made",
            "production_tenant_storage_isolated",
            "production_tenant_storage_enabled",
            "tenant_storage_isolated",
            "migration_executed",
            "storage_behavior_modified",
            "customer_data_processed",
        ]:
            if source.get(flag) is True:
                boundary_violations.append(f"{source_name}.{flag}")

    expected_missing = {
        "privacy_legal_review_completed",
    }
    actual_missing = {row.get("evidence_key") for row in missing_rows}

    if boundary_violations:
        status = "stop_boundary_violation"
    elif actual_missing == expected_missing and len(present_rows) == 17:
        status = "hold_remaining_one_agent_review_required"
    else:
        status = "hold_gap_shape_changed_reinspect_required"

    packet_rows: list[dict[str, Any]] = []
    for index, row in enumerate(missing_rows, start=1):
        evidence_key = str(row.get("evidence_key", ""))
        if evidence_key == "tenant_authorization_policy_reviewed":
            owner_lane = "engineering_security"
            review_question = "Has tenant authorization policy been reviewed and approved for production tenant storage?"
        elif evidence_key == "tenant_secret_boundary_reviewed":
            owner_lane = "security_privacy"
            review_question = "Has tenant secret boundary been reviewed without exposing private core or credentials?"
        elif evidence_key == "security_review_completed":
            owner_lane = "independent_agent_security"
            review_question = "Has an independent security agent completed the tenant storage adversarial review?"
        elif evidence_key == "privacy_legal_review_completed":
            owner_lane = "independent_agent_privacy_legal"
            review_question = "Has an independent privacy/legal agent completed review before any customer data processing claim?"
        else:
            owner_lane = "engineering_data_security"
            review_question = "Review the missing production tenant-storage evidence key."
        packet_rows.append(
            {
                "gap_id": f"TSG-{index:03d}",
                "blocker_id": TARGET_BLOCKER_ID,
                "evidence_key": evidence_key,
                "gap_status": row.get("gap_status", ""),
                "local_public_shell_value": row.get("local_public_shell_value") is True,
                "human_review_required": False,
                "agent_review_required": True,
                "external_dependency_required": row.get("external_dependency_required") is True,
                "owner_lane": owner_lane,
                "review_question": review_question,
                "default_decision": "hold",
                "closure_allowed_by_packet": False,
            }
        )

    payload: dict[str, Any] = {
        "tenant_storage_remaining_gap_packet_v0_1": True,
        "packet_type": "tenant_storage_remaining_gap_agent_review_packet",
        "packet_scope": "remaining_one_agent_review_only_no_execution_no_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_tenant_storage_remaining_gap_packet.py",
        "target_blocker_id": TARGET_BLOCKER_ID,
        "source_gap_audit_json": rel(GAP_AUDIT_JSON),
        "source_tenant_evidence_json": rel(TENANT_EVIDENCE_JSON),
        "source_security_review_packet_json": rel(SECURITY_REVIEW_PACKET_JSON),
        "source_approval_validation_json": rel(APPROVAL_VALIDATION_JSON),
        "required_evidence_item_count": len(rows),
        "local_public_shell_present_count": len(present_rows),
        "remaining_missing_evidence_count": len(missing_rows),
        "remaining_missing_evidence_keys": [row["evidence_key"] for row in packet_rows],
        "packet_rows": packet_rows,
        "tenant_security_privacy_packet_status": security_packet.get("packet_status", ""),
        "tenant_storage_approval_input_validation_status": approval_validation.get(
            "validation_status", ""
        ),
        "tenant_storage_approval_input_complete": approval_validation.get("input_complete")
        is True,
        "tenant_storage_builder_ready": approval_validation.get("builder_ready") is True,
        "human_review_required": False,
        "human_validation_used": False,
        "agent_review_required": True,
        "agent_validation_primary": True,
        "recommended_default_decision": "hold",
        "ready_for_closure": False,
        "ready_for_matrix_update": False,
        "ready_for_evidence_builder": False,
        "blockers_closed_by_packet": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "next_agent_action": (
            "Run the independent-agent privacy/legal review for the remaining item. "
            "Do not run migrations or closure until its evidence adapter passes."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def build_decision_template(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_type": "tenant_storage_remaining_gap_agent_review_input",
        "target_blocker_id": TARGET_BLOCKER_ID,
        "source_packet": rel(OUT_JSON),
        "review_actor_type": "independent_agent",
        "agent_reviewer_id": "",
        "human_validation_used": False,
        "review_date": "",
        "source_notes": "",
        "remaining_gap_decisions": [
            {
                "evidence_key": row["evidence_key"],
                "decision": "hold",
                "approved": False,
                "source_note": "",
                "owner_lane": row["owner_lane"],
            }
            for row in payload["packet_rows"]
        ],
        "authorize_evidence_builder": False,
        "authorize_matrix_update": False,
        "authorize_blocker_closure": False,
        "authorize_product_launch": False,
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
        "gap_id",
        "blocker_id",
        "evidence_key",
        "gap_status",
        "human_review_required",
        "agent_review_required",
        "external_dependency_required",
        "owner_lane",
        "default_decision",
        "closure_allowed_by_packet",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["packet_rows"]:
            writer.writerow({field: row.get(field) for field in fields})


def write_docs(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE tenant_storage_isolation 剩余缺口包",
        "",
        "Tenant Storage Remaining Gap Packet v0.1",
        "",
        "这个包只列出 `tenant_storage_isolation` 剩余的 1 个智能体审查缺口。它不执行迁移、不改存储行为、不关闭 blocker。",
        "",
        "```text",
        "tenant_storage_remaining_gap_packet_v0_1: true",
        f"status: {payload['status']}",
        f"target_blocker_id: {payload['target_blocker_id']}",
        f"required_evidence_item_count: {payload['required_evidence_item_count']}",
        f"local_public_shell_present_count: {payload['local_public_shell_present_count']}",
        f"remaining_missing_evidence_count: {payload['remaining_missing_evidence_count']}",
        f"tenant_storage_approval_input_complete: {str(payload['tenant_storage_approval_input_complete']).lower()}",
        f"tenant_storage_builder_ready: {str(payload['tenant_storage_builder_ready']).lower()}",
        "ready_for_evidence_builder: false",
        "ready_for_matrix_update: false",
        "ready_for_closure: false",
        "blockers_closed_by_packet: 0",
        "production_tenant_storage_isolated: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "```",
        "",
        "human_validation_used: false",
        "agent_validation_primary: true",
        "## 剩余 1 项",
        "",
        "| ID | Evidence key | Owner lane | Review question |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["packet_rows"]:
        lines.append(
            f"| {row['gap_id']} | `{row['evidence_key']}` | `{row['owner_lane']}` | {row['review_question']} |"
        )
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            "- 独立隐私/法律智能体生成可哈希复核的证据。",
            "- 通过后仍需单独的 evidence-builder 或 matrix-update 请求。",
            "- 本包不能修改 canonical gap matrix，也不能关闭 `tenant_storage_isolation`。",
        ]
    )
    text = "\n".join(lines) + "\n"
    TOP_DOC.write_text(text, encoding="utf-8")
    OUT_MD.write_text(text, encoding="utf-8")

    audit = [
        "# Tenant Storage Remaining Gap Packet Boundary Audit",
        "",
        "remaining_gap_packet_only: true",
        "human_decision_recorded: false",
        "human_validation_used: false",
        "agent_validation_primary: true",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
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
        "production_database_modified: false",
        "storage_behavior_modified: false",
        "migration_executed: false",
        "customer_data_processed: false",
        "production_tenant_storage_enabled: false",
        "production_tenant_storage_isolated: false",
        "tenant_storage_isolated: false",
    ]
    OUT_AUDIT.write_text("\n".join(audit) + "\n", encoding="utf-8")

    gate = [
        "# SAEE Tenant Storage Remaining Gap Packet Gate",
        "",
        "answer: hold",
        "recommend_for_agent_remaining_gap_review: true",
        "recommend_for_evidence_builder: false",
        "recommend_for_automatic_matrix_update: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "",
        "reason: tenant_storage_isolation has 17 local public-shell evidence items present, but 1 independent-agent privacy/legal review item remains missing.",
        "",
        "boundary:",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "canonical_gap_matrix_modified: false",
        "canonical_closure_board_modified: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_packet: 0",
        "production_tenant_storage_isolated: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "next_action: Independent-agent privacy/legal review of the final tenant-storage item.",
    ]
    GATE.write_text("\n".join(gate) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_TENANT_STORAGE_REMAINING_GAP_PACKET: "
        f"{payload['status']} "
        f"present={payload['local_public_shell_present_count']} "
        f"missing={payload['remaining_missing_evidence_count']} "
        "blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
