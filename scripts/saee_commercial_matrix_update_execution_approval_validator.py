#!/usr/bin/env python3
"""Validate human approval for matrix-update execution without executing it."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "matrix_update_requests"
DEFAULT_INPUT = OUT_DIR / "commercial_matrix_update_execution_approval_input.human_filled.local.json"
TEMPLATE = OUT_DIR / "commercial_matrix_update_execution_approval_input.template.json"
SOURCE_REQUEST = OUT_DIR / "commercial_matrix_update_execution_request_packet.local.json"
VALIDATION = OUT_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
VALIDATION_MD = OUT_DIR / "commercial_matrix_update_execution_approval_validation.md"
AGENT_INDEX = ROOT / "agent-index.json"

EXPECTED_DECISION = "approve_matrix_update_execution_review_ready_markers_only"
REQUIRED_TRUE = [
    "approve_matrix_update_execution_review_ready_markers_only",
    "confirm_no_blocker_closure",
    "confirm_no_pricing_publication",
    "confirm_no_checkout_enablement",
    "confirm_no_production_ready_claim",
    "confirm_no_customer_validation_claim",
    "confirm_no_product_launch",
]
FALSE_FLAGS = {
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_approval_validator": 0,
    "open_blocker_count_reduced": False,
    "pricing_page_published": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate(input_path: Path) -> dict[str, Any]:
    source_request = read_json(SOURCE_REQUEST)
    missing: list[str] = []
    boundary_violations: list[str] = []
    approval: dict[str, Any] = {}
    if not input_path.exists():
        missing.append("human_filled_input_file")
    else:
        approval = read_json(input_path)

    for field in ["human_decision", "human_reviewer", "decision_date", "approval_reference"]:
        if not approval.get(field):
            missing.append(field)
    if approval.get("human_decision") != EXPECTED_DECISION:
        missing.append("human_decision_expected_value")
    for field in REQUIRED_TRUE:
        if approval.get(field) is not True:
            missing.append(field)
    if source_request.get("status") != "ready_for_explicit_human_execution_approval_no_closure":
        boundary_violations.append("source_request.status")
    for field in [
        "matrix_update_executed",
        "canonical_gap_matrix_modified",
        "canonical_closure_board_modified",
        "blocker_closure_authorized",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
    ]:
        if source_request.get(field) is True:
            boundary_violations.append(f"source_request.{field}")

    if boundary_violations:
        status = "stop_boundary_violation"
        human_execution_approved = False
        ready = False
    elif missing:
        status = "hold_human_execution_approval_input_required"
        human_execution_approved = False
        ready = False
    else:
        status = "ready_for_matrix_update_execution_no_closure"
        human_execution_approved = True
        ready = True

    return {
        "commercial_matrix_update_execution_approval_validation_v0_1": True,
        "validator_type": "matrix_update_execution_approval_input_validator",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_template": rel(TEMPLATE),
        "source_human_filled_input": rel(input_path),
        "source_execution_request_packet": rel(SOURCE_REQUEST),
        "target_blockers": source_request.get("target_blockers", []),
        "human_decision": approval.get("human_decision", ""),
        "human_reviewer": approval.get("human_reviewer", ""),
        "decision_date": approval.get("decision_date", ""),
        "approval_reference": approval.get("approval_reference", ""),
        "human_execution_approved": human_execution_approved,
        "ready_for_matrix_update_execution": ready,
        "approval_input_complete": not missing and not boundary_violations,
        "missing_fields": sorted(set(missing)),
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(boundary_violations),
        "next_human_action": (
            "Run the separate matrix-update applier only after explicit human approval is present."
            if ready
            else "Complete the human-filled approval input or keep matrix update on hold."
        ),
        **FALSE_FLAGS,
    }


def update_agent_index(payload: dict[str, Any]) -> None:
    index = read_json(AGENT_INDEX)
    entry = index.get("commercial_matrix_update_execution_approval_input_v0_1", {})
    if not isinstance(entry, dict):
        entry = {}
    entry.update(
        {
            "status": payload["status"],
            "human_execution_approved": payload["human_execution_approved"],
            "ready_for_matrix_update_execution": payload["ready_for_matrix_update_execution"],
            "matrix_update_executed": False,
            "canonical_gap_matrix_modified": False,
            "canonical_closure_board_modified": False,
            "blocker_closure_authorized": False,
            "blockers_closed_by_approval_validator": 0,
            "production_ready": False,
            "customer_validated": False,
            "product_launched": False,
            "private_core_exposed": False,
        }
    )
    index["commercial_matrix_update_execution_approval_input_v0_1"] = entry
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_report(payload: dict[str, Any]) -> None:
    VALIDATION_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Validation

Status: `{payload['status']}`

- human_execution_approved: `{str(payload['human_execution_approved']).lower()}`
- ready_for_matrix_update_execution: `{str(payload['ready_for_matrix_update_execution']).lower()}`
- approval_input_complete: `{str(payload['approval_input_complete']).lower()}`
- missing_fields: `{len(payload['missing_fields'])}`
- boundary_violation_count: `{payload['boundary_violation_count']}`
- matrix_update_executed: `false`
- canonical_gap_matrix_modified: `false`
- blocker_closure_authorized: `false`
- blockers_closed_by_approval_validator: `0`
- production_ready: `false`
- customer_validated: `false`

Next action: {payload['next_human_action']}
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    payload = validate(input_path)
    write_json(VALIDATION, payload)
    write_report(payload)
    update_agent_index(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_VALIDATOR: PASS "
        f"status={payload['status']} "
        f"human_execution_approved={str(payload['human_execution_approved']).lower()} "
        "matrix_update_executed=false blockers_closed_by_approval_validator=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
