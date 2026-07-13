#!/usr/bin/env python3
"""Build the active human-input board for the commercial sprint.

The board compresses the current quick-fill state into a human-readable action
surface. It does not enter values, import a workbook, transfer templates, run
validators on real input, collect evidence, execute builders, close blockers,
contact anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"

QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
QUICK_FILL_VALIDATION_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"
)
SAFETY_PREFLIGHT_JSON = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.local.json"
IMPORT_DRY_RUN_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.local.json"
)
IMPORTER_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"
APPROVAL_PACKET_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.local.json"
GUIDANCE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_guidance.local.json"
REVIEW_BATCH_TEMPLATE_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"
)
REVIEW_BATCH_TEMPLATE_IMPORTER_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.local.json"
)
REVIEW_BATCH_TEMPLATE_E2E_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json"
)

OUT_JSON = SPRINT_DIR / "commercial_sprint_active_human_input_board.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_active_human_input_board.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_active_human_input_board.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_active_human_input_board_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 64
BOARD_SCOPE = "preferred_review_batch_template_and_full_quick_fill_status_only_no_values_no_import_no_execution"

FALSE_FLAGS = [
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "raw_values_recorded",
    "quick_fill_imported_to_workbook",
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
    "task_candidates_executed",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def source_boundary_violations(sources: dict[str, dict[str, Any]]) -> list[str]:
    violations: list[str] = []
    forbidden_true_fields = [
        "quick_fill_values_entered_by_codex",
        "human_input_filled_by_codex",
        "raw_values_recorded",
        "quick_fill_imported_to_workbook",
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
        "task_candidates_executed",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "vendor_contacted",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
    ]
    for source_name, payload in sources.items():
        for field in forbidden_true_fields:
            if payload.get(field) is True:
                violations.append(f"{source_name}:{field}_true")
        if int(payload.get("boundary_violation_count", 0) or 0) > 0:
            violations.append(f"{source_name}:boundary_violation_count_nonzero")
    return sorted(set(violations))


def group_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["blocker_id"]].append(row)

    board_rows: list[dict[str, Any]] = []
    for blocker_id, blocker_rows in sorted(grouped.items()):
        completed = [
            row
            for row in blocker_rows
            if row.get("human_value_to_enter", "").strip()
        ]
        owner_lanes = sorted({row["owner_review_lane"] for row in blocker_rows})
        input_groups = sorted({row["input_group"] for row in blocker_rows})
        missing_ids = [
            row["quick_fill_row_id"]
            for row in blocker_rows
            if not row.get("human_value_to_enter", "").strip()
        ]
        board_rows.append(
            {
                "blocker_id": blocker_id,
                "owner_review_lanes": owner_lanes,
                "input_groups": input_groups,
                "quick_fill_row_count": len(blocker_rows),
                "completed_value_row_count": len(completed),
                "missing_value_row_count": len(blocker_rows) - len(completed),
                "missing_quick_fill_row_ids": missing_ids,
                "status": (
                    "hold_missing_human_values"
                    if len(completed) < len(blocker_rows)
                    else "filled_pending_safety_preflight"
                ),
                "next_human_action": (
                    "Review the workbook import approval request; do not import, "
                    "collect evidence, or close blockers without separate approval."
                ),
                "workbook_import_authorized": False,
                "evidence_collection_authorized": False,
                "blocker_closure_authorized": False,
            }
        )
    return board_rows


def determine_stage(
    missing_value_row_count: int,
    validation: dict[str, Any],
    safety: dict[str, Any],
    dry_run: dict[str, Any],
    approval: dict[str, Any],
) -> tuple[str, str]:
    if missing_value_row_count > 0:
        return "hold_human_quick_fill_required", "human_quick_fill"
    if safety.get("safe_to_import_after_human_approval") is not True:
        return "hold_safety_preflight_required", "safety_preflight"
    if validation.get("ready_for_workbook_import") is not True:
        return "hold_quick_fill_validator_required", "quick_fill_validator"
    if dry_run.get("ready_for_workbook_import") is not True:
        return "hold_import_dry_run_required", "workbook_import_dry_run"
    if approval.get("ready_for_workbook_import_approval") is not True:
        return "hold_workbook_import_approval_request_refresh_required", "approval_request_refresh"
    return "ready_for_human_workbook_import_approval", "human_workbook_import_approval_review"


def build_payload() -> dict[str, Any]:
    rows = read_csv(QUICK_FILL_CSV)
    validation = read_json(QUICK_FILL_VALIDATION_JSON)
    safety = read_json(SAFETY_PREFLIGHT_JSON)
    dry_run = read_json(IMPORT_DRY_RUN_JSON)
    importer = read_json(IMPORTER_JSON)
    approval = read_json(APPROVAL_PACKET_JSON)
    guidance = read_json(GUIDANCE_JSON)
    review_batch_template = read_json(REVIEW_BATCH_TEMPLATE_JSON)
    review_batch_template_importer = read_json(REVIEW_BATCH_TEMPLATE_IMPORTER_JSON)
    review_batch_template_e2e = read_json(REVIEW_BATCH_TEMPLATE_E2E_JSON)
    sources = {
        "quick_fill_validation": validation,
        "safety_preflight": safety,
        "import_dry_run": dry_run,
        "importer": importer,
        "approval_packet": approval,
        "guidance": guidance,
        "review_batch_template": review_batch_template,
        "review_batch_template_importer": review_batch_template_importer,
        "review_batch_template_e2e": review_batch_template_e2e,
    }
    boundary_violations = source_boundary_violations(sources)
    if len(rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_quick_fill_row_count")

    completed_value_row_count = sum(
        1 for row in rows if row.get("human_value_to_enter", "").strip()
    )
    missing_value_row_count = len(rows) - completed_value_row_count
    status, current_stage = determine_stage(
        missing_value_row_count, validation, safety, dry_run, approval
    )
    if boundary_violations:
        status = "stop_boundary_violation"
        current_stage = "boundary_review"

    board_rows = group_rows(rows)
    next_manual_steps = [
        {
            "step_id": "AHI-001",
            "stage": "review_batch_template_human_fill",
            "action": (
                "Fill only human_value_to_enter and optional notes_for_human in "
                "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv."
            ),
            "command": "",
            "execution_allowed_by_codex": False,
        },
        {
            "step_id": "AHI-002",
            "stage": "review_batch_template_e2e_dry_run",
            "action": (
                "Run the local 10-row template e2e dry run after human values "
                "are filled."
            ),
            "command": (
                "python3 scripts/saee_commercial_sprint_human_input_quick_fill_"
                "review_batch_template_e2e_dry_run.py"
            ),
            "execution_allowed_by_codex": False,
        },
        {
            "step_id": "AHI-003",
            "stage": "separate_local_output_apply_request",
            "action": (
                "If the e2e dry run passes, request separate explicit approval "
                "before any local-output apply/import step."
            ),
            "command": "",
            "execution_allowed_by_codex": False,
        },
        {
            "step_id": "AHI-004",
            "stage": "full_quick_fill_source_path_review",
            "action": (
                "Keep the 64-row source quick-fill path as the complete source "
                "path after the small-batch review; do not overwrite it in this board."
            ),
            "command": "",
            "execution_allowed_by_codex": False,
        },
    ]

    payload: dict[str, Any] = {
        "commercial_sprint_active_human_input_board_v0_1": True,
        "board_type": "current_commercial_sprint_human_input_board",
        "board_scope": BOARD_SCOPE,
        "status": status,
        "current_stage": current_stage,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_active_human_input_board.py",
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_quick_fill_validation_json": rel(QUICK_FILL_VALIDATION_JSON),
        "source_safety_preflight_json": rel(SAFETY_PREFLIGHT_JSON),
        "source_import_dry_run_json": rel(IMPORT_DRY_RUN_JSON),
        "source_importer_json": rel(IMPORTER_JSON),
        "source_approval_packet_json": rel(APPROVAL_PACKET_JSON),
        "source_guidance_json": rel(GUIDANCE_JSON),
        "source_review_batch_template_json": rel(REVIEW_BATCH_TEMPLATE_JSON),
        "source_review_batch_template_importer_json": rel(
            REVIEW_BATCH_TEMPLATE_IMPORTER_JSON
        ),
        "source_review_batch_template_e2e_json": rel(REVIEW_BATCH_TEMPLATE_E2E_JSON),
        "source_quick_fill_validator_status": validation.get("status"),
        "source_safety_preflight_status": safety.get("status"),
        "source_import_dry_run_status": dry_run.get("status"),
        "source_importer_status": importer.get("status"),
        "source_approval_packet_status": approval.get("status"),
        "source_review_batch_template_status": review_batch_template.get("status"),
        "source_review_batch_template_importer_status": review_batch_template_importer.get(
            "status"
        ),
        "source_review_batch_template_e2e_status": review_batch_template_e2e.get(
            "status"
        ),
        "preferred_human_input_path": "workbook_import_approval_request",
        "preferred_batch_size": int(
            review_batch_template.get("template_row_count", 0) or 0
        ),
        "preferred_template_row_count": int(
            review_batch_template.get("template_row_count", 0) or 0
        ),
        "preferred_template_value_present_row_count": int(
            review_batch_template_e2e.get("template_value_present_row_count", 0) or 0
        ),
        "preferred_template_missing_value_row_count": int(
            review_batch_template_e2e.get("missing_template_value_row_count", 0) or 0
        ),
        "preferred_template_e2e_preview_validator_executed": (
            review_batch_template_e2e.get("preview_validator_executed") is True
        ),
        "preferred_template_e2e_preview_validator_passed": (
            review_batch_template_e2e.get("preview_validator_passed") is True
        ),
        "ready_for_preferred_template_human_fill": (
            int(review_batch_template_e2e.get("missing_template_value_row_count", 0) or 0)
            > 0
            and not boundary_violations
        ),
        "full_quick_fill_row_count": len(rows),
        "full_quick_fill_missing_value_row_count": missing_value_row_count,
        "quick_fill_row_count": len(rows),
        "selected_blocker_count": len(board_rows),
        "completed_value_row_count": completed_value_row_count,
        "missing_value_row_count": missing_value_row_count,
        "ready_for_human_fill": missing_value_row_count > 0 and not boundary_violations,
        "ready_for_safety_preflight": missing_value_row_count == 0 and not boundary_violations,
        "safe_to_import_after_human_approval": safety.get(
            "safe_to_import_after_human_approval"
        )
        is True,
        "ready_for_workbook_import": validation.get("ready_for_workbook_import") is True,
        "ready_for_workbook_import_approval": approval.get(
            "ready_for_workbook_import_approval"
        )
        is True,
        "approval_request_count": int(approval.get("approval_request_count", 0) or 0),
        "ready_import_approval_count": int(
            approval.get("ready_import_approval_count", 0) or 0
        ),
        "next_manual_step_count": len(next_manual_steps),
        "next_manual_steps": next_manual_steps,
        "board_rows": board_rows,
        "human_input_required": True,
        "human_review_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_request_required": True,
        "separate_validator_execution_request_required": True,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(set(boundary_violations)),
        "next_human_action": (
            "Review the workbook import approval request and the 64 confirmed "
            "values. Do not run workbook import, validators on real input, "
            "evidence collection, or blocker closure without separate approval."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "owner_review_lanes",
        "quick_fill_row_count",
        "completed_value_row_count",
        "missing_value_row_count",
        "status",
        "next_human_action",
        "workbook_import_authorized",
        "evidence_collection_authorized",
        "blocker_closure_authorized",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["board_rows"]:
            out = dict(row)
            out["owner_review_lanes"] = "|".join(row["owner_review_lanes"])
            writer.writerow({field: out.get(field, "") for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_active_human_input_board_v0_1: true",
        f"status: {payload['status']}",
        f"current_stage: {payload['current_stage']}",
        f"board_scope: {payload['board_scope']}",
        f"source_quick_fill_validator_status: {payload['source_quick_fill_validator_status']}",
        f"source_safety_preflight_status: {payload['source_safety_preflight_status']}",
        f"source_import_dry_run_status: {payload['source_import_dry_run_status']}",
        f"source_importer_status: {payload['source_importer_status']}",
        f"source_approval_packet_status: {payload['source_approval_packet_status']}",
        f"source_review_batch_template_status: {payload['source_review_batch_template_status']}",
        f"source_review_batch_template_importer_status: {payload['source_review_batch_template_importer_status']}",
        f"source_review_batch_template_e2e_status: {payload['source_review_batch_template_e2e_status']}",
        f"preferred_human_input_path: {payload['preferred_human_input_path']}",
        f"preferred_batch_size: {payload['preferred_batch_size']}",
        f"preferred_template_row_count: {payload['preferred_template_row_count']}",
        f"preferred_template_value_present_row_count: {payload['preferred_template_value_present_row_count']}",
        f"preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}",
        "preferred_template_e2e_preview_validator_executed: "
        f"{str(payload['preferred_template_e2e_preview_validator_executed']).lower()}",
        "preferred_template_e2e_preview_validator_passed: "
        f"{str(payload['preferred_template_e2e_preview_validator_passed']).lower()}",
        "ready_for_preferred_template_human_fill: "
        f"{str(payload['ready_for_preferred_template_human_fill']).lower()}",
        f"full_quick_fill_row_count: {payload['full_quick_fill_row_count']}",
        f"full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"selected_blocker_count: {payload['selected_blocker_count']}",
        f"completed_value_row_count: {payload['completed_value_row_count']}",
        f"missing_value_row_count: {payload['missing_value_row_count']}",
        f"ready_for_human_fill: {str(payload['ready_for_human_fill']).lower()}",
        f"ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}",
        f"safe_to_import_after_human_approval: {str(payload['safe_to_import_after_human_approval']).lower()}",
        f"ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}",
        f"ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}",
        f"approval_request_count: {payload['approval_request_count']}",
        f"ready_import_approval_count: {payload['ready_import_approval_count']}",
        f"next_manual_step_count: {payload['next_manual_step_count']}",
        "human_input_required: true",
        "human_review_required: true",
        "separate_workbook_import_execution_request_required: true",
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


def markdown_table(payload: dict[str, Any]) -> str:
    rows = [
        "| Blocker | Rows | Missing | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in payload["board_rows"]:
        rows.append(
            "| {blocker_id} | {quick_fill_row_count} | {missing_value_row_count} | {status} |".format(
                **row
            )
        )
    return "\n".join(rows)


def write_markdown(path: Path, payload: dict[str, Any], title: str) -> None:
    path.write_text(
        f"""# {title}

{chr(10).join(status_lines(payload))}

## Purpose

This board shows the active human-input state for the current commercial
sprint. It supersedes older first-owner-only next-action views for this sprint
by pointing humans first to the 10-row review-batch template path while keeping
the 64-row quick-fill packet as the complete source path.

## Board

{markdown_table(payload)}

## Manual Sequence

1. Fill only `human_value_to_enter` and optional `notes_for_human` in
   `commercial_sprint_human_input_quick_fill_review_batch_input_template.csv`.
2. Run `python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py`.
3. If the e2e dry run passes, request separate explicit approval before any
   local-output apply/import step.
4. Keep the 64-row source quick-fill path as the complete source path after the
   small-batch review; this board does not overwrite it.

## Boundary

No values were generated or entered by Codex. No workbook import was authorized
or performed. No workbook file was written. No templates were filled. No
validators were run on real input. No evidence was collected, no blocker was
closed, no customer or vendor was contacted, no product was launched, and no
production-readiness or customer-validation claim was made.
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Active Human Input Board Recommendation Gate

answer: conditional
recommend_for_active_human_input_guidance: true
recommend_for_quick_fill_status_compression: true
recommend_for_value_generation: false
recommend_for_workbook_import_execution: false
recommend_for_template_transfer: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

{chr(10).join(status_lines(payload))}

Reason: this board is recommendable as current human-input guidance only. It
does not provide values and does not authorize import, validation execution,
evidence collection, or blocker closure.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_markdown(OUT_MD, payload, "Commercial Sprint Active Human Input Board v0.1")
    write_markdown(OUT_BOUNDARY, payload, "Commercial Sprint Active Human Input Board Boundary Audit")
    write_markdown(TOP_DOC, payload, "SAEE Commercial Sprint Active Human Input Board v0.1")
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_ACTIVE_HUMAN_INPUT_BOARD: PASS "
        f"status={payload['status']} "
        f"missing_value_row_count={payload['missing_value_row_count']} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
