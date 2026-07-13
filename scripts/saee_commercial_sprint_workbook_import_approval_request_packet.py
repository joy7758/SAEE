#!/usr/bin/env python3
"""Prepare a human approval request packet for commercial sprint workbook import.

This packet reads existing local safety and completion surfaces for the
quick-fill -> workbook import path. It does not approve import, run the importer
in apply mode, write workbook output, transfer templates, run validators on real
input, collect evidence, execute builders, close blockers, contact anyone,
launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"

SAFETY_JSON = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.local.json"
QUICK_FILL_VALIDATION_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"
)
IMPORT_DRY_RUN_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.local.json"
)
IMPORTER_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_IMPORT_ROW_COUNT = 64

FALSE_FLAGS = [
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


def source_boundary_violations(sources: dict[str, dict[str, Any]]) -> list[str]:
    violations: list[str] = []
    forbidden_true_fields = [
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
    ]
    for source_name, payload in sources.items():
        for field in forbidden_true_fields:
            if payload.get(field) is True:
                violations.append(f"{source_name}:{field}_true")
        if payload.get("workbook_written") is True:
            violations.append(f"{source_name}:workbook_written_true")
        if payload.get("apply_performed") is True:
            violations.append(f"{source_name}:apply_performed_true")
        if int(payload.get("boundary_violation_count", 0) or 0) > 0:
            violations.append(f"{source_name}:boundary_violation_count_nonzero")
    return sorted(set(violations))


def build_payload() -> dict[str, Any]:
    safety = read_json(SAFETY_JSON)
    quick_fill = read_json(QUICK_FILL_VALIDATION_JSON)
    import_dry_run = read_json(IMPORT_DRY_RUN_JSON)
    importer = read_json(IMPORTER_JSON)
    sources = {
        "safety_preflight": safety,
        "quick_fill_validator": quick_fill,
        "import_dry_run": import_dry_run,
        "importer": importer,
    }

    boundary_violations = source_boundary_violations(sources)
    source_conditions = {
        "safety_preflight_passed": (
            safety.get("status") == "pass_no_sensitive_values_found_pending_import_approval"
            and safety.get("safe_to_import_after_human_approval") is True
            and safety.get("filled_value_row_count") == EXPECTED_IMPORT_ROW_COUNT
            and safety.get("secret_pattern_hit_count") == 0
        ),
        "quick_fill_validator_ready": (
            quick_fill.get("status") == "ready_for_workbook_import_pending_human_approval"
            and quick_fill.get("ready_for_workbook_import") is True
            and quick_fill.get("completed_quick_fill_row_count") == EXPECTED_IMPORT_ROW_COUNT
            and quick_fill.get("missing_quick_fill_row_count") == 0
        ),
        "import_dry_run_ready": (
            import_dry_run.get("status") == "ready_for_workbook_import_pending_human_approval"
            and import_dry_run.get("ready_for_workbook_import") is True
            and import_dry_run.get("would_import_row_count") == EXPECTED_IMPORT_ROW_COUNT
        ),
        "importer_ready": (
            importer.get("status") == "ready_for_apply_pending_explicit_human_command"
            and importer.get("ready_for_workbook_import") is True
            and importer.get("import_ready_row_count") == EXPECTED_IMPORT_ROW_COUNT
            and importer.get("apply_performed") is False
            and importer.get("workbook_written") is False
        ),
    }
    ready_for_approval = all(source_conditions.values()) and not boundary_violations
    if boundary_violations:
        status = "stop_boundary_violation"
    elif ready_for_approval:
        status = "ready_for_human_workbook_import_approval"
    else:
        status = "hold_human_input_required"

    missing_conditions = [
        name for name, passed in source_conditions.items() if not passed
    ]
    request = {
        "request_id": "WIA-001",
        "request_type": "workbook_import_approval_request",
        "source_quick_fill_csv": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_packet.csv",
        "target_workbook_csv": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_workbook.imported_from_quick_fill.local.csv",
        "expected_import_row_count": EXPECTED_IMPORT_ROW_COUNT,
        "ready_for_human_approval": ready_for_approval,
        "human_import_approval_recorded": False,
        "workbook_import_authorized": False,
        "import_execution_allowed": False,
        "recommended_human_decision": "approve" if ready_for_approval else "hold",
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
        "commercial_sprint_workbook_import_approval_request_packet_v0_1": True,
        "packet_type": "controlled_workbook_import_approval_request_packet",
        "packet_scope": "pre_workbook_import_approval_request_only_no_import_no_transfer_no_evidence",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py",
        "source_safety_preflight_json": rel(SAFETY_JSON),
        "source_quick_fill_validation_json": rel(QUICK_FILL_VALIDATION_JSON),
        "source_import_dry_run_json": rel(IMPORT_DRY_RUN_JSON),
        "source_importer_json": rel(IMPORTER_JSON),
        "source_safety_preflight_status": safety.get("status"),
        "source_quick_fill_validator_status": quick_fill.get("status"),
        "source_import_dry_run_status": import_dry_run.get("status"),
        "source_importer_status": importer.get("status"),
        "source_conditions": source_conditions,
        "missing_condition_count": len(missing_conditions),
        "missing_conditions": missing_conditions,
        "approval_request_count": 1,
        "ready_import_approval_count": 1 if ready_for_approval else 0,
        "approved_import_count": 0,
        "workbook_import_authorized_count": 0,
        "ready_for_workbook_import_approval": ready_for_approval,
        "ready_for_workbook_import_execution": False,
        "human_import_approval_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_request_required": True,
        "separate_validator_execution_request_required": True,
        "approval_requests": [request],
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "next_human_action": (
            "Fill quick-fill values, run safety preflight, run quick-fill validator, "
            "run import dry-run, then review this approval request before any "
            "separate workbook import execution."
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
        "ready_for_human_approval",
        "human_import_approval_recorded",
        "workbook_import_authorized",
        "import_execution_allowed",
        "recommended_human_decision",
        "missing_conditions",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for request in payload["approval_requests"]:
            row = dict(request)
            row["missing_conditions"] = "|".join(request["missing_conditions"])
            writer.writerow({field: row.get(field, "") for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_workbook_import_approval_request_packet_v0_1: true",
        f"status: {payload['status']}",
        f"packet_scope: {payload['packet_scope']}",
        f"source_safety_preflight_status: {payload['source_safety_preflight_status']}",
        f"source_quick_fill_validator_status: {payload['source_quick_fill_validator_status']}",
        f"source_import_dry_run_status: {payload['source_import_dry_run_status']}",
        f"source_importer_status: {payload['source_importer_status']}",
        f"approval_request_count: {payload['approval_request_count']}",
        f"ready_import_approval_count: {payload['ready_import_approval_count']}",
        f"approved_import_count: {payload['approved_import_count']}",
        f"workbook_import_authorized_count: {payload['workbook_import_authorized_count']}",
        f"missing_condition_count: {payload['missing_condition_count']}",
        f"ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}",
        "ready_for_workbook_import_execution: false",
        "human_import_approval_required: true",
        "separate_workbook_import_execution_request_required: true",
        "separate_template_transfer_request_required: true",
        "separate_validator_execution_request_required: true",
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

This packet gives humans a single local approval-request surface for the
quick-fill -> workbook import step after safety preflight, quick-fill
validation, import dry-run, and importer readiness are all satisfied.

## Boundary

This packet does not approve import and does not run the importer in apply
mode. It writes no workbook output, transfers no template values, runs no
validators, collects no evidence, executes no builders, closes no blockers,
contacts no customers/vendors, launches no product, and makes no production
readiness or customer-validation claim.
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Workbook Import Approval Request Packet Recommendation Gate

answer: conditional
recommend_for_workbook_import_approval_request: true
recommend_for_human_approval_collection: true
recommend_for_workbook_import_execution: false
recommend_for_auto_approval: false
recommend_for_template_transfer: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

{chr(10).join(status_lines(payload))}

Reason: this packet is recommendable only as a local human approval-request
surface. It does not authorize or execute workbook import.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_markdown(OUT_MD, payload, "Commercial Sprint Workbook Import Approval Request Packet v0.1")
    write_markdown(OUT_BOUNDARY, payload, "Commercial Sprint Workbook Import Approval Request Packet Boundary Audit")
    write_markdown(TOP_DOC, payload, "SAEE Commercial Sprint Workbook Import Approval Request Packet v0.1")
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_APPROVAL_REQUEST_PACKET: PASS "
        f"status={payload['status']} "
        f"ready_import_approval_count={payload['ready_import_approval_count']} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
