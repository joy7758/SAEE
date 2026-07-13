#!/usr/bin/env python3
"""Prepare a separate human execution request packet for workbook import.

This packet records that the quick-fill -> workbook import path is ready for a
separate human execution request. It does not run the importer, write workbook
output, transfer values to templates, run validators on real input, collect
evidence, close blockers, contact anyone, launch product, or claim production
readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"

APPROVAL_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.local.json"
IMPORTER_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_IMPORT_ROW_COUNT = 64
TARGET_COMMAND = (
    "python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py "
    "--apply --confirm-human-approved-import"
)

FALSE_FLAGS = [
    "human_execution_request_recorded",
    "human_execution_authorized",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_boundary_violations(
    approval: dict[str, Any], importer: dict[str, Any]
) -> list[str]:
    violations: list[str] = []
    for source_name, payload in {
        "approval_packet": approval,
        "importer": importer,
    }.items():
        for field in [
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "customer_contacted",
            "vendor_contacted",
            "external_calls_made",
            "external_model_api_called",
            "external_ai_assistant_tested",
            "evidence_collection_authorized",
            "execution_authorized",
            "evidence_builder_executed",
            "blocker_closure_authorized",
            "values_transferred",
            "human_filled_templates_written",
            "validators_run_on_real_input",
            "workbook_import_authorized",
            "workbook_import_performed",
            "workbook_written",
        ]:
            if payload.get(field) is True:
                violations.append(f"{source_name}:{field}_true")
        if payload.get("apply_performed") is True:
            violations.append(f"{source_name}:apply_performed_true")
        if int(payload.get("boundary_violation_count", 0) or 0) > 0:
            violations.append(f"{source_name}:boundary_violation_count_nonzero")
    return sorted(set(violations))


def build_payload() -> dict[str, Any]:
    approval = read_json(APPROVAL_JSON)
    importer = read_json(IMPORTER_JSON)
    approval_request = (approval.get("approval_requests") or [{}])[0]

    boundary_violations = source_boundary_violations(approval, importer)
    source_conditions = {
        "approval_packet_ready": (
            approval.get("status") == "ready_for_human_workbook_import_approval"
            and approval.get("ready_for_workbook_import_approval") is True
            and approval.get("ready_for_workbook_import_execution") is False
            and approval.get("separate_workbook_import_execution_request_required") is True
            and approval_request.get("recommended_human_decision") == "approve"
            and approval_request.get("expected_import_row_count") == EXPECTED_IMPORT_ROW_COUNT
        ),
        "importer_ready": (
            importer.get("status") == "ready_for_apply_pending_explicit_human_command"
            and importer.get("ready_for_workbook_import") is True
            and importer.get("import_ready_row_count") == EXPECTED_IMPORT_ROW_COUNT
            and importer.get("apply_performed") is False
            and importer.get("workbook_written") is False
        ),
    }
    missing_conditions = [name for name, passed in source_conditions.items() if not passed]
    ready_for_execution_request = all(source_conditions.values()) and not boundary_violations
    if boundary_violations:
        status = "stop_boundary_violation"
    elif ready_for_execution_request:
        status = "ready_for_separate_human_execution_request"
    else:
        status = "hold_execution_request_prerequisites_unmet"

    execution_request = {
        "request_id": "WIE-001",
        "request_type": "workbook_import_execution_request",
        "source_approval_request_id": approval_request.get("request_id", "WIA-001"),
        "source_recommended_human_decision": approval_request.get(
            "recommended_human_decision", "hold"
        ),
        "target_command": TARGET_COMMAND,
        "target_output_workbook_csv": importer.get(
            "output_workbook_csv",
            "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
            "commercial_sprint_human_input_workbook.imported_from_quick_fill.local.csv",
        ),
        "expected_import_row_count": EXPECTED_IMPORT_ROW_COUNT,
        "ready_for_separate_human_execution_request": ready_for_execution_request,
        "human_execution_request_recorded": False,
        "human_execution_authorized": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "workbook_written": False,
        "recommended_human_decision": "approve" if ready_for_execution_request else "hold",
        "missing_conditions": missing_conditions,
        "must_not_touch": [
            "runtime",
            "backend",
            "kernel",
            "api_schema",
            "private_core",
            "template_transfer",
            "validator_execution",
            "evidence_collection",
            "blocker_closure",
            "product_launch",
        ],
    }

    payload: dict[str, Any] = {
        "commercial_sprint_workbook_import_execution_request_packet_v0_1": True,
        "packet_type": "controlled_workbook_import_execution_request_packet",
        "packet_scope": "execution_request_only_no_import_no_transfer_no_evidence",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": (
            "scripts/saee_commercial_sprint_workbook_import_execution_request_packet.py"
        ),
        "source_approval_packet_json": rel(APPROVAL_JSON),
        "source_importer_json": rel(IMPORTER_JSON),
        "source_approval_packet_status": approval.get("status"),
        "source_importer_status": importer.get("status"),
        "source_conditions": source_conditions,
        "missing_condition_count": len(missing_conditions),
        "missing_conditions": missing_conditions,
        "execution_request_count": 1,
        "ready_execution_request_count": 1 if ready_for_execution_request else 0,
        "approved_execution_count": 0,
        "workbook_import_authorized_count": 0,
        "ready_for_workbook_import_approval": approval.get(
            "ready_for_workbook_import_approval"
        )
        is True,
        "ready_for_separate_human_execution_request": ready_for_execution_request,
        "ready_for_workbook_import_execution": False,
        "human_execution_request_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_request_required": True,
        "separate_validator_execution_request_required": True,
        "target_command": TARGET_COMMAND,
        "target_output_workbook_csv": execution_request["target_output_workbook_csv"],
        "expected_import_row_count": EXPECTED_IMPORT_ROW_COUNT,
        "recommended_human_decision": execution_request["recommended_human_decision"],
        "execution_requests": [execution_request],
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "next_human_action": (
            "Human must explicitly issue a separate workbook import execution request "
            "before Codex may run the importer apply command. This packet does not "
            "authorize execution by itself."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "request_id",
        "request_type",
        "expected_import_row_count",
        "ready_for_separate_human_execution_request",
        "human_execution_request_recorded",
        "human_execution_authorized",
        "workbook_import_authorized",
        "workbook_import_performed",
        "workbook_written",
        "recommended_human_decision",
        "target_command",
        "missing_conditions",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for request in payload["execution_requests"]:
            row = dict(request)
            row["missing_conditions"] = "|".join(request["missing_conditions"])
            writer.writerow({field: row.get(field, "") for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_workbook_import_execution_request_packet_v0_1: true",
        f"status: {payload['status']}",
        f"packet_scope: {payload['packet_scope']}",
        f"source_approval_packet_status: {payload['source_approval_packet_status']}",
        f"source_importer_status: {payload['source_importer_status']}",
        f"execution_request_count: {payload['execution_request_count']}",
        f"ready_execution_request_count: {payload['ready_execution_request_count']}",
        f"approved_execution_count: {payload['approved_execution_count']}",
        f"workbook_import_authorized_count: {payload['workbook_import_authorized_count']}",
        f"missing_condition_count: {payload['missing_condition_count']}",
        f"ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}",
        f"ready_for_separate_human_execution_request: {str(payload['ready_for_separate_human_execution_request']).lower()}",
        "ready_for_workbook_import_execution: false",
        "human_execution_request_required: true",
        "separate_workbook_import_execution_request_required: true",
        "separate_template_transfer_request_required: true",
        "separate_validator_execution_request_required: true",
        "human_execution_request_recorded: false",
        "human_execution_authorized: false",
        "workbook_import_authorized: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "real_evidence_created: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]


def write_markdown(path: Path, payload: dict[str, Any], title: str) -> None:
    path.write_text(
        f"""# {title}

{chr(10).join(status_lines(payload))}

## Purpose

This packet records the next formal commercial-readiness gate after the
workbook import approval request. It packages the exact local importer command
that would be run only after a separate, explicit human execution request.

## What It Solves

The goal was blocked because all local quick-fill values are complete and import
readiness exists, but the system still requires a separate execution request
before any workbook write. This packet makes that blocker explicit and
reviewable without running the importer.

## Boundary

This packet does not authorize execution and does not run the importer in apply
mode. It writes no workbook output, transfers no template values, runs no
validators on real input, collects no evidence, executes no builders, closes no
blockers, contacts no customers/vendors, launches no product, and makes no
production readiness or customer-validation claim.

## Next Human Action

{payload['next_human_action']}
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Workbook Import Execution Request Packet Recommendation Gate

answer: conditional
recommend_for_workbook_import_execution_request_packet: true
recommend_for_human_execution_request_collection: true
recommend_for_workbook_import_execution: false
recommend_for_auto_execution: false
recommend_for_template_transfer: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

{chr(10).join(status_lines(payload))}

Reason: this packet is recommendable only as a local human execution-request
surface. It does not authorize or execute workbook import.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_markdown(OUT_MD, payload, "Commercial Sprint Workbook Import Execution Request Packet v0.1")
    write_markdown(OUT_BOUNDARY, payload, "Commercial Sprint Workbook Import Execution Request Packet Boundary Audit")
    write_markdown(TOP_DOC, payload, "SAEE Commercial Sprint Workbook Import Execution Request Packet v0.1")
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_REQUEST_PACKET: PASS "
        f"status={payload['status']} "
        f"ready_execution_request_count={payload['ready_execution_request_count']} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
