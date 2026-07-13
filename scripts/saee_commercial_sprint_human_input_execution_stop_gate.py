#!/usr/bin/env python3
"""Create a local execution stop gate for missing commercial human inputs.

This gate is intentionally conservative. It reads the active commercial
quick-fill status and records whether Codex may proceed beyond human-fill
support. When the current 64 required human values are blank, the only allowed
next actor is a human reviewer filling the quick-fill CSV. The script does not
fill values, import workbooks, run validators on real input, collect evidence,
execute tasks, close blockers, contact anyone, launch product, or claim
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
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"
NEXT_ACTION_JSON = COMMERCIAL_DIR / "commercial_next_action_summary/commercial_next_action_summary.local.json"
READINESS_JSON = SPRINT_DIR / "commercial_sprint_human_input_readiness_audit.local.json"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
ACTIVE_BOARD_JSON = SPRINT_DIR / "commercial_sprint_active_human_input_board.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_execution_stop_gate_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE_RECOMMENDATION_GATE.md"


FALSE_FLAGS = {
    "codex_execution_allowed": False,
    "workbook_import_allowed": False,
    "validator_execution_on_real_input_allowed": False,
    "template_transfer_allowed": False,
    "evidence_collection_allowed": False,
    "evidence_builder_execution_allowed": False,
    "blocker_closure_allowed": False,
    "production_launch_allowed": False,
    "development_permission_granted": False,
    "human_values_filled_by_codex": False,
    "quick_fill_values_entered_by_codex": False,
    "workbook_import_performed": False,
    "workbook_written": False,
    "validators_run_on_real_input": False,
    "values_transferred": False,
    "human_filled_templates_written": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "evidence_builder_executed": False,
    "blocker_closure_authorized": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "vendor_contacted": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "payment_collected": False,
    "revenue_validated": False,
    "production_ready_claim": False,
    "customer_validation_claim": False,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE: FAIL {path} must be an object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    next_action = read_json(NEXT_ACTION_JSON)
    readiness = read_json(READINESS_JSON)
    active_board = read_json(ACTIVE_BOARD_JSON)
    quick_rows = read_csv(QUICK_FILL_CSV)

    row_count = len(quick_rows)
    completed_value_count = sum(1 for row in quick_rows if row.get("human_value_to_enter", "").strip())
    missing_value_count = row_count - completed_value_count
    readiness_ready_count = int(readiness.get("ready_for_human_input_row_count", 0))
    readiness_missing_context = int(readiness.get("missing_context_row_count", 0))

    stop_required = missing_value_count > 0
    status = (
        "stop_codex_execution_human_values_required"
        if stop_required and readiness_missing_context == 0
        else "hold_context_or_value_review_required"
    )

    gate_rows = [
        {
            "gate_id": "HISTOP-001",
            "condition": "missing_quick_fill_human_values",
            "current_value": missing_value_count,
            "required_before_continue": 0,
            "decision": "stop_codex_execution" if missing_value_count else "allow_next_local_review",
            "allowed_next_actor": "human_reviewer" if missing_value_count else "separate_human_approved_local_validator",
            "allowed_action": (
                "Fill human_value_to_enter and optional notes_for_human in the quick-fill CSV."
                if missing_value_count
                else "Run the separate local safety preflight and validator commands."
            ),
            "forbidden_action": (
                "Codex must not import workbooks, transfer templates, run validators on real input, "
                "collect evidence, execute builders, close blockers, launch product, or claim readiness."
            ),
        },
        {
            "gate_id": "HISTOP-002",
            "condition": "quick_fill_context_complete",
            "current_value": readiness_ready_count,
            "required_before_continue": row_count,
            "decision": "context_ready_for_human_fill" if readiness_ready_count == row_count else "hold_context_gap",
            "allowed_next_actor": "human_reviewer",
            "allowed_action": (
                "Use the complete context to review the workbook import approval request."
                if not missing_value_count
                else "Use the ready context to fill values manually."
            ),
            "forbidden_action": "Codex must not infer, suggest, or prefill human evidence values.",
        },
        {
            "gate_id": "HISTOP-003",
            "condition": "workbook_import_authorization",
            "current_value": False,
            "required_before_continue": "separate_human_approval_after_values_exist",
            "decision": "stop_import_not_authorized",
            "allowed_next_actor": "human_approver",
            "allowed_action": "Review approval request only; no workbook import action is allowed at this gate.",
            "forbidden_action": "Do not run apply/import/transfer paths from this gate.",
        },
    ]

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_execution_stop_gate_v0_1": True,
        "gate_type": "local_codex_execution_stop_gate_for_missing_human_values",
        "gate_scope": "human_quick_fill_blocker_only_no_values_no_execution",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_execution_stop_gate.py",
        "source_files": {
            "next_action_summary": rel(NEXT_ACTION_JSON),
            "readiness_audit": rel(READINESS_JSON),
            "quick_fill_csv": rel(QUICK_FILL_CSV),
            "active_human_input_board": rel(ACTIVE_BOARD_JSON),
        },
        "source_statuses": {
            "next_action_summary": next_action.get("status"),
            "readiness_audit": readiness.get("status"),
            "active_human_input_board": active_board.get("status"),
        },
        "quick_fill_row_count": row_count,
        "completed_value_row_count": completed_value_count,
        "missing_value_row_count": missing_value_count,
        "ready_for_human_input_row_count": readiness_ready_count,
        "missing_context_row_count": readiness_missing_context,
        "human_input_required": missing_value_count > 0,
        "human_fill_only": missing_value_count > 0,
        "allowed_next_actor": "human_reviewer" if missing_value_count > 0 else "separate_human_approved_local_validator",
        "codex_may_continue_generating_execution_materials": False,
        "codex_may_fill_values": False,
        "codex_may_run_import": False,
        "codex_may_run_real_input_validators": False,
        "codex_may_collect_evidence": False,
        "codex_may_close_blockers": False,
        "safe_next_human_action": (
            (
                "Fill only human_value_to_enter and optional notes_for_human in "
                "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
                "commercial_sprint_human_input_quick_fill_packet.csv."
            )
            if missing_value_count
            else (
                "Review the completed human quick-fill values and explicitly approve "
                "or reject the next local-only workbook-import approval step. Codex "
                "still must not import the workbook or run validators on real input "
                "without separate human approval."
            )
        ),
        "post_human_fill_commands": [
            "python3 scripts/saee_commercial_sprint_human_input_safety_preflight.py",
            "python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py",
            "python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py",
            "python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py",
        ],
        "gate_rows": gate_rows,
        "blockers_closed_by_gate": 0,
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "gate_id",
        "condition",
        "current_value",
        "required_before_continue",
        "decision",
        "allowed_next_actor",
        "allowed_action",
        "forbidden_action",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload["gate_rows"])


def write_docs(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {gate_id} | {condition} | {current_value} | {decision} | {allowed_next_actor} |".format(**row)
        for row in payload["gate_rows"]
    )
    md = f"""# Commercial Sprint Human Input Execution Stop Gate v0.1

commercial_sprint_human_input_execution_stop_gate_v0_1: true
gate_scope: {payload["gate_scope"]}
status: {payload["status"]}
commercial_status: hold
production_launch_status: hold

## Purpose
This gate prevents Codex from moving past the human-confirmed value stage
without separate human approval, even after required values are present.

## Current State
- quick_fill_row_count: {payload["quick_fill_row_count"]}
- completed_value_row_count: {payload["completed_value_row_count"]}
- missing_value_row_count: {payload["missing_value_row_count"]}
- ready_for_human_input_row_count: {payload["ready_for_human_input_row_count"]}
- missing_context_row_count: {payload["missing_context_row_count"]}
- human_fill_only: {str(payload["human_fill_only"]).lower()}
- allowed_next_actor: {payload["allowed_next_actor"]}

## Gate Decisions
| Gate | Condition | Current Value | Decision | Allowed Next Actor |
| --- | --- | ---: | --- | --- |
{rows}

## Allowed Next Human Action
{payload["safe_next_human_action"]}

## Forbidden Actions
Codex must not fill values, import the workbook, transfer templates, run
validators on real input, collect evidence, execute evidence builders, close
blockers, contact anyone, launch the product, or claim production readiness.

## Boundary State
- codex_execution_allowed: false
- workbook_import_allowed: false
- validator_execution_on_real_input_allowed: false
- evidence_collection_allowed: false
- blocker_closure_allowed: false
- production_launch_allowed: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
"""
    OUT_MD.write_text(md, encoding="utf-8")
    TOP_DOC.write_text(md, encoding="utf-8")

    boundary = f"""# Commercial Sprint Human Input Execution Stop Gate Boundary Audit

commercial_sprint_human_input_execution_stop_gate_v0_1: true
status: {payload["status"]}
gate_scope: {payload["gate_scope"]}

- No human values filled by Codex: true
- No workbook import performed: true
- No validators run on real input: true
- No evidence collection authorized: true
- No blocker closure authorized: true
- No runtime modified: true
- No backend modified: true
- No kernel modified: true
- No API schema modified: true
- No private core exposed: true
- No product launched: true
- No customer contacted: true
- No production-ready claim added: true

Final boundary decision: stop Codex execution until a separate human approval
authorizes the next local-only action.
"""
    OUT_BOUNDARY.write_text(boundary, encoding="utf-8")

    gate = f"""# SAEE Commercial Sprint Human Input Execution Stop Gate Recommendation Gate

answer: stop_codex_execution_until_separate_human_approval

reason: The active commercial sprint has {payload["missing_value_row_count"]} missing human quick-fill values. Codex still cannot import workbooks, run validators on real input, collect evidence, or close blockers without separate human approval.

recommend_for_human_quick_fill: {str(payload["human_input_required"]).lower()}
recommend_for_workbook_import_approval_review: {str(not payload["human_input_required"]).lower()}
recommend_for_codex_execution: false
recommend_for_workbook_import: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_production: false

boundary:
- codex_execution_allowed: false
- workbook_import_allowed: false
- validator_execution_on_real_input_allowed: false
- evidence_collection_allowed: false
- blocker_closure_allowed: false
- production_launch_allowed: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: {payload["safe_next_human_action"]}
"""
    GATE.write_text(gate, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_EXECUTION_STOP_GATE: PASS "
        f"status={payload['status']} missing_value_row_count={payload['missing_value_row_count']} "
        f"codex_execution_allowed={str(payload['codex_execution_allowed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )


if __name__ == "__main__":
    main()
