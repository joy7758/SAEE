#!/usr/bin/env python3
"""Build the canonical next-action summary for SAEE commercial readiness.

This presentation layer reads the current local commercial readiness status and
active human-input board. It does not fill values, import workbooks, transfer
templates, run validators on real input, collect evidence, contact anyone,
close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_action_summary"
OUTPUT_JSON = OUTPUT_DIR / "commercial_next_action_summary.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_next_action_summary.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_next_action_summary.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_NEXT_ACTION_SUMMARY_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY_RECOMMENDATION_GATE.md"

STATUS_JSON = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_status.local.json"
ACTIVE_BOARD_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_active_human_input_board.local.json"
)
HUMAN_SEQUENCE_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "human_sequence_packet.local.json"
)
FIRST_OWNER_INPUT_REQUEST_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_input_request_packet.local.json"
)
FIRST_OWNER_INPUT_REQUEST_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "first_owner_input_request_packet.md"
)
QUICK_FILL_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_packet.csv"
)
REVIEW_BATCH_TEMPLATE_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
REVIEW_BATCH_QUALITY_GUIDE_HTML = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_human_entry_quality_guide.html"
)
REVIEW_BATCH_QUALITY_GUIDE_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_human_entry_quality_guide.local.json"
)
REVIEW_BATCH_TEMPLATE_PREFLIGHT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_template_preflight.local.json"
)
REVIEW_BATCH_TEMPLATE_PREFLIGHT_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_template_preflight.md"
)
POST_FILL_RUNBOOK_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_post_fill_validation_runbook.local.json"
)
POST_FILL_RUNBOOK_HTML = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_post_fill_validation_runbook.html"
)
POST_FILL_READINESS_PREVIEW_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_post_fill_readiness_preview.local.json"
)
POST_FILL_READINESS_PREVIEW_HTML = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_post_fill_readiness_preview.html"
)
WORKBOOK_IMPORT_APPROVAL_PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_approval_request_packet.md"
)
TEMPLATE_TRANSFER_REQUEST_PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_template_transfer_execution_request_packet.md"
)
VALIDATOR_APPROVAL_PACKET_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_validator_approval_request_packet.md"
)

BOUNDARY_FALSE_FLAGS = [
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
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "owner_contacted_by_codex",
    "owner_assigned_by_codex",
    "customer_data_collected",
    "customer_data_processed",
    "payment_collected",
    "revenue_validated",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_builder_executed",
    "blocker_closure_authorized",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY: FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY: FAIL {rel(path)} must be object")
    return data


def build_summary() -> dict[str, Any]:
    status = read_json(STATUS_JSON)
    board = read_json(ACTIVE_BOARD_JSON)
    human_sequence = read_json(HUMAN_SEQUENCE_JSON)
    first_owner_request = read_json(FIRST_OWNER_INPUT_REQUEST_JSON)
    quality_guide = read_json(REVIEW_BATCH_QUALITY_GUIDE_JSON)
    template_preflight = read_json(REVIEW_BATCH_TEMPLATE_PREFLIGHT_JSON)
    post_fill_runbook = read_json(POST_FILL_RUNBOOK_JSON)
    post_fill_preview = read_json(POST_FILL_READINESS_PREVIEW_JSON)
    template_transfer_ready = (
        status.get("status") == "ready_for_separate_human_template_transfer_execution_request"
        or status.get("ready_for_separate_human_template_transfer_execution_request") is True
    )
    template_transfer_execution_ready = (
        status.get("status") == "ready_for_template_transfer_execution"
        and status.get("ready_for_template_transfer_execution") is True
        and status.get("template_transfer_authorized") is True
        and status.get("template_transfer_execution_allowed") is True
    )
    validator_outputs_review_ready = (
        status.get("status") == "hold_validator_outputs_review_required"
        and status.get("validators_run") is True
        and status.get("local_validators_run") is True
        and int(status.get("validators_run_count", 0) or 0) == 5
        and int(status.get("validator_hold_count", 0) or 0) == 5
        and int(status.get("builder_ready_count", 0) or 0) == 0
        and int(status.get("blockers_closed_by_validator_run", 0) or 0) == 0
    )
    validator_missing_input_completion_ready = (
        status.get("status") == "hold_validator_input_evidence_completion_required"
        and status.get("validator_hold_output_review_completed") is True
        and status.get("validator_missing_input_completion_required") is True
        and int(status.get("validators_run_count", 0) or 0) == 5
        and int(status.get("validator_hold_count", 0) or 0) == 5
        and int(status.get("builder_ready_count", 0) or 0) == 0
        and int(status.get("blockers_closed_by_validator_run", 0) or 0) == 0
    )
    evidence_builder_request_ready = (
        status.get("status") == "ready_for_separate_evidence_builder_request"
        and status.get("validators_run") is True
        and status.get("local_validators_run") is True
        and int(status.get("validators_run_count", 0) or 0) == 5
        and int(status.get("validator_hold_count", 0) or 0) == 0
        and int(status.get("validator_pass_count", 0) or 0) == 5
        and int(status.get("builder_ready_count", 0) or 0) == 5
        and int(status.get("blockers_closed_by_validator_run", 0) or 0) == 0
    )
    validator_approval_ready = (
        status.get("status") == "hold_validator_approval_required"
        and status.get("ready_for_validator_approval") is True
        and status.get("ready_for_validator_execution") is False
        and int(status.get("ready_validator_count", 0) or 0) == 5
        and int(status.get("approved_validator_count", 0) or 0) == 0
        and int(status.get("validator_execution_authorized_count", 0) or 0) == 0
    )
    approval_ready = (
        board.get("ready_for_workbook_import_approval") is True
        and int(board.get("missing_value_row_count", 64)) == 0
    )
    next_action = {
        "action_id": "NEXT-RBT-001",
        "sequence_step_id": "AHI-001",
        "blocker_id": "commercial_sprint_review_batch_template",
        "category": "commercial_sprint_review_batch_template_human_input",
        "status": (
            "ready_for_human_workbook_import_approval"
            if approval_ready
            else "hold_human_quick_fill_required"
        ),
        "why_this_action": (
            "The active commercial sprint should use the 10-row quality guide "
            "before the 10-row review-batch template. Completing these values is required before the "
            "local template e2e dry run and any separate local-output apply or "
            "full quick-fill source-path review."
        ),
        "quality_guide": rel(REVIEW_BATCH_QUALITY_GUIDE_HTML),
        "template_preflight": rel(REVIEW_BATCH_TEMPLATE_PREFLIGHT_MD),
        "input_sheet": rel(REVIEW_BATCH_TEMPLATE_CSV),
        "post_fill_readiness_preview": rel(POST_FILL_READINESS_PREVIEW_HTML),
        "post_fill_validation_runbook": rel(POST_FILL_RUNBOOK_HTML),
        "required_human_fields": ["human_value_to_enter", "notes_for_human"],
        "quick_fill_row_count": board.get("quick_fill_row_count"),
        "preferred_human_input_path": board.get("preferred_human_input_path"),
        "preferred_batch_size": board.get("preferred_batch_size"),
        "preferred_template_row_count": board.get("preferred_template_row_count"),
        "preferred_template_missing_value_row_count": board.get(
            "preferred_template_missing_value_row_count"
        ),
        "full_quick_fill_missing_value_row_count": board.get(
            "full_quick_fill_missing_value_row_count"
        ),
        "selected_blocker_count": board.get("selected_blocker_count"),
        "completed_value_row_count": board.get("completed_value_row_count"),
        "missing_value_row_count": board.get("missing_value_row_count"),
        "next_manual_steps": board.get("next_manual_steps", []),
        "requires_human_input": True,
        "requires_template_preflight_reference": True,
        "requires_post_fill_readiness_preview": True,
        "requires_post_fill_validation_runbook": True,
        "requires_review_batch_template_e2e_dry_run": True,
        "requires_separate_local_output_apply_request": True,
        "requires_full_quick_fill_source_path_review": True,
        "requires_safety_preflight": False,
        "requires_quick_fill_validator": False,
        "requires_import_dry_run": False,
        "requires_workbook_import_approval_review": False,
        "requires_separate_workbook_import_execution_request": True,
        "execution_allowed_by_summary": False,
        "evidence_collection_authorized": False,
        "blocker_closure_allowed_by_summary": False,
        "default_decision": "hold",
    }
    if approval_ready:
        next_action.update(
            {
                "action_id": "NEXT-WIA-001",
                "sequence_step_id": "WIA-001",
                "blocker_id": "workbook_import_approval",
                "category": "commercial_sprint_workbook_import_approval_review",
                "status": "ready_for_human_workbook_import_approval",
                "why_this_action": (
                    "All 64 quick-fill source values are present and the local "
                    "safety/import-readiness checks have prepared a workbook import "
                    "approval request. A human must review that request before any "
                    "workbook write or downstream evidence work."
                ),
                "quality_guide": rel(WORKBOOK_IMPORT_APPROVAL_PACKET_MD),
                "template_preflight": rel(WORKBOOK_IMPORT_APPROVAL_PACKET_MD),
                "input_sheet": rel(WORKBOOK_IMPORT_APPROVAL_PACKET_MD),
                "post_fill_readiness_preview": rel(WORKBOOK_IMPORT_APPROVAL_PACKET_MD),
                "post_fill_validation_runbook": rel(WORKBOOK_IMPORT_APPROVAL_PACKET_MD),
                "required_human_fields": ["human_import_approval_decision"],
                "preferred_human_input_path": "workbook_import_approval_request",
                "preferred_batch_size": 1,
                "preferred_template_row_count": 1,
                "preferred_template_missing_value_row_count": 0,
                "next_manual_steps": [
                    {
                        "step_id": "WIA-001",
                        "stage": "workbook_import_approval_review",
                        "action": (
                            "Review commercial_sprint_workbook_import_approval_request_packet.md "
                            "and decide whether a separate workbook import execution request "
                            "should be issued."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                    {
                        "step_id": "WIA-002",
                        "stage": "separate_workbook_import_execution_request",
                        "action": (
                            "If import execution is desired, create a separate explicit "
                            "human execution request. This summary does not authorize import."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                ],
                "requires_human_input": True,
                "requires_template_preflight_reference": False,
                "requires_post_fill_readiness_preview": False,
                "requires_post_fill_validation_runbook": False,
                "requires_review_batch_template_e2e_dry_run": False,
                "requires_separate_local_output_apply_request": False,
                "requires_full_quick_fill_source_path_review": False,
                "requires_safety_preflight": False,
                "requires_quick_fill_validator": False,
                "requires_import_dry_run": False,
                "requires_workbook_import_approval_review": True,
                "requires_separate_workbook_import_execution_request": True,
            }
        )
    if template_transfer_ready:
        next_action.update(
            {
                "action_id": "NEXT-TTA-001" if template_transfer_execution_ready else "NEXT-TTE-001",
                "sequence_step_id": "TTA-001" if template_transfer_execution_ready else "TTE-001",
                "blocker_id": (
                    "template_transfer_applier_execution"
                    if template_transfer_execution_ready
                    else "template_transfer_execution_request"
                ),
                "category": (
                    "commercial_sprint_template_transfer_applier_execution"
                    if template_transfer_execution_ready
                    else "commercial_sprint_template_transfer_execution_request_review"
                ),
                "status": (
                    "ready_for_template_transfer_execution"
                    if template_transfer_execution_ready
                    else "ready_for_separate_human_template_transfer_execution_request"
                ),
                "why_this_action": (
                    "The 64 confirmed values have already been imported into the "
                    "local workbook, and a separate human approval record now "
                    "authorizes only the controlled local template-transfer "
                    "applier. Run that applier next, then stop before validators, "
                    "evidence collection, or blocker closure."
                    if template_transfer_execution_ready
                    else "The 64 confirmed values have already been imported into the "
                    "local workbook. A human must now review the separate template "
                    "transfer execution request before any values are copied into "
                    "target templates or validators run on real input."
                ),
                "quality_guide": rel(TEMPLATE_TRANSFER_REQUEST_PACKET_MD),
                "template_preflight": rel(TEMPLATE_TRANSFER_REQUEST_PACKET_MD),
                "input_sheet": rel(TEMPLATE_TRANSFER_REQUEST_PACKET_MD),
                "post_fill_readiness_preview": rel(TEMPLATE_TRANSFER_REQUEST_PACKET_MD),
                "post_fill_validation_runbook": rel(TEMPLATE_TRANSFER_REQUEST_PACKET_MD),
                "required_human_fields": (
                    ["run_controlled_template_transfer_applier"]
                    if template_transfer_execution_ready
                    else ["human_template_transfer_execution_decision"]
                ),
                "preferred_human_input_path": (
                    "template_transfer_applier_execution"
                    if template_transfer_execution_ready
                    else "template_transfer_execution_request"
                ),
                "preferred_batch_size": 1,
                "preferred_template_row_count": int(status.get("target_template_count", 5)),
                "preferred_template_missing_value_row_count": 0,
                "full_quick_fill_missing_value_row_count": int(
                    status.get("full_quick_fill_missing_value_row_count", 0)
                ),
                "selected_blocker_count": int(status.get("selected_blocker_count", 5)),
                "completed_value_row_count": int(status.get("completed_value_row_count", 64)),
                "missing_value_row_count": int(status.get("missing_value_row_count", 0)),
                "next_manual_steps": [
                    {
                        "step_id": "TTA-001" if template_transfer_execution_ready else "TTE-001",
                        "stage": (
                            "template_transfer_applier_execution"
                            if template_transfer_execution_ready
                            else "template_transfer_execution_request_review"
                        ),
                        "action": (
                            "Run only the controlled local template-transfer applier "
                            "authorized by commercial_sprint_template_transfer_execution_approval.local.json."
                            if template_transfer_execution_ready
                            else "Review commercial_sprint_template_transfer_execution_request_packet.md "
                            "and decide whether a separate documentation/data transfer "
                            "execution request should be issued."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                    {
                        "step_id": "TTA-002" if template_transfer_execution_ready else "TTE-002",
                        "stage": (
                            "stop_before_real_validators"
                            if template_transfer_execution_ready
                            else "separate_template_transfer_execution_request"
                        ),
                        "action": (
                            "After template transfer, stop before validator execution "
                            "on real input, evidence collection, blocker closure, or "
                            "production-readiness claims."
                            if template_transfer_execution_ready
                            else "If template transfer execution is desired, create a "
                            "separate explicit human execution request. This summary "
                            "does not authorize template transfer."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                ],
                "requires_human_input": True,
                "requires_template_preflight_reference": False,
                "requires_post_fill_readiness_preview": False,
                "requires_post_fill_validation_runbook": False,
                "requires_review_batch_template_e2e_dry_run": False,
                "requires_separate_local_output_apply_request": False,
                "requires_full_quick_fill_source_path_review": False,
                "requires_safety_preflight": False,
                "requires_quick_fill_validator": False,
                "requires_import_dry_run": False,
                "requires_workbook_import_approval_review": False,
                "requires_separate_workbook_import_execution_request": False,
                "requires_separate_template_transfer_execution_request": (
                    not template_transfer_execution_ready
                ),
                "template_transfer_execution_allowed": template_transfer_execution_ready,
            }
        )
    if validator_outputs_review_ready:
        next_action.update(
            {
                "action_id": "NEXT-VOR-001",
                "sequence_step_id": "VOR-001",
                "blocker_id": "validator_hold_outputs",
                "category": "commercial_sprint_validator_hold_output_review",
                "status": "hold_validator_outputs_review_required",
                "why_this_action": (
                    "The five approved local validators have run and all returned hold. "
                    "The next bounded step is human review of those hold outputs and "
                    "completion of missing input or boundary evidence before any separate "
                    "evidence-builder request. This does not authorize evidence collection, "
                    "blocker closure, customer contact, launch, or production-readiness claims."
                ),
                "quality_guide": status.get("source_validator_execution_run"),
                "template_preflight": status.get("source_validator_execution_run"),
                "input_sheet": status.get("source_validator_execution_run"),
                "post_fill_readiness_preview": status.get("source_validator_execution_run"),
                "post_fill_validation_runbook": status.get("source_validator_execution_run"),
                "required_human_fields": ["validator_hold_output_review_decision"],
                "preferred_human_input_path": "validator_hold_output_review",
                "preferred_batch_size": 1,
                "preferred_template_row_count": int(status.get("validators_run_count", 5)),
                "preferred_template_missing_value_row_count": 0,
                "full_quick_fill_missing_value_row_count": int(
                    status.get("full_quick_fill_missing_value_row_count", 0)
                ),
                "selected_blocker_count": int(status.get("selected_blocker_count", 5)),
                "completed_value_row_count": int(status.get("completed_value_row_count", 64)),
                "missing_value_row_count": int(status.get("missing_value_row_count", 0)),
                "next_manual_steps": [
                    {
                        "step_id": "VOR-001",
                        "stage": "validator_hold_output_review",
                        "action": (
                            "Review commercial_sprint_validator_execution_run.md and "
                            "identify the missing input or boundary evidence for each hold output."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                    {
                        "step_id": "VOR-002",
                        "stage": "separate_evidence_builder_request",
                        "action": (
                            "If any validator hold output is ready to resolve, create a separate "
                            "explicit evidence-builder request. This summary does not authorize builders."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                ],
                "requires_human_input": True,
                "requires_template_preflight_reference": False,
                "requires_post_fill_readiness_preview": False,
                "requires_post_fill_validation_runbook": False,
                "requires_review_batch_template_e2e_dry_run": False,
                "requires_separate_local_output_apply_request": False,
                "requires_full_quick_fill_source_path_review": False,
                "requires_safety_preflight": False,
                "requires_quick_fill_validator": False,
                "requires_import_dry_run": False,
                "requires_workbook_import_approval_review": False,
                "requires_separate_workbook_import_execution_request": False,
                "requires_separate_template_transfer_execution_request": False,
                "requires_validator_approval_review": False,
                "requires_validator_output_review": True,
                "requires_separate_validator_execution_request": False,
                "requires_separate_evidence_builder_request": True,
                "template_transfer_execution_allowed": False,
                "validator_execution_allowed": False,
            }
        )
    if validator_missing_input_completion_ready:
        next_action.update(
            {
                "action_id": "NEXT-VIC-001",
                "sequence_step_id": "VIC-001",
                "blocker_id": "validator_missing_input_evidence",
                "category": "commercial_sprint_validator_missing_input_completion",
                "status": "hold_validator_input_evidence_completion_required",
                "why_this_action": (
                    "The five approved local validators have run, all returned hold, "
                    "and the hold-output review has identified missing input evidence. "
                    "The next bounded step is to complete the missing metadata fields, "
                    "evidence review items, and source notes listed in the review, then "
                    "rerun local validators. This does not authorize evidence collection, "
                    "evidence builders, blocker closure, customer contact, launch, or "
                    "production-readiness claims."
                ),
                "quality_guide": status.get("source_validator_hold_output_review"),
                "template_preflight": status.get("source_validator_hold_output_review"),
                "input_sheet": status.get("source_validator_hold_output_review"),
                "post_fill_readiness_preview": status.get(
                    "source_validator_hold_output_review"
                ),
                "post_fill_validation_runbook": status.get(
                    "source_validator_hold_output_review"
                ),
                "required_human_fields": [
                    "missing_metadata_fields",
                    "missing_evidence_items",
                    "missing_source_notes",
                ],
                "preferred_human_input_path": "validator_missing_input_completion",
                "preferred_batch_size": 5,
                "preferred_template_row_count": int(status.get("validators_run_count", 5)),
                "preferred_template_missing_value_row_count": int(
                    status.get("total_missing_metadata_field_count", 0) or 0
                )
                + int(status.get("total_missing_evidence_item_count", 0) or 0)
                + int(status.get("total_missing_source_note_count", 0) or 0),
                "full_quick_fill_missing_value_row_count": int(
                    status.get("full_quick_fill_missing_value_row_count", 0)
                ),
                "selected_blocker_count": int(status.get("selected_blocker_count", 5)),
                "completed_value_row_count": int(status.get("completed_value_row_count", 64)),
                "missing_value_row_count": int(status.get("missing_value_row_count", 0)),
                "total_missing_metadata_field_count": int(
                    status.get("total_missing_metadata_field_count", 0) or 0
                ),
                "total_missing_evidence_item_count": int(
                    status.get("total_missing_evidence_item_count", 0) or 0
                ),
                "total_missing_source_note_count": int(
                    status.get("total_missing_source_note_count", 0) or 0
                ),
                "next_manual_steps": [
                    {
                        "step_id": "VIC-001",
                        "stage": "validator_missing_input_completion",
                        "action": (
                            "Open commercial_sprint_validator_hold_output_review.md "
                            "and complete the listed missing metadata fields, evidence "
                            "review items, and source notes in the human-filled input targets."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                    {
                        "step_id": "VIC-002",
                        "stage": "rerun_local_validators_after_completion",
                        "action": (
                            "After the missing inputs are complete, rerun the local validators. "
                            "Do not run evidence builders or close blockers until validators "
                            "pass and a separate explicit request exists."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                ],
                "requires_human_input": True,
                "requires_template_preflight_reference": False,
                "requires_post_fill_readiness_preview": False,
                "requires_post_fill_validation_runbook": False,
                "requires_review_batch_template_e2e_dry_run": False,
                "requires_separate_local_output_apply_request": False,
                "requires_full_quick_fill_source_path_review": False,
                "requires_safety_preflight": False,
                "requires_quick_fill_validator": False,
                "requires_import_dry_run": False,
                "requires_workbook_import_approval_review": False,
                "requires_separate_workbook_import_execution_request": False,
                "requires_separate_template_transfer_execution_request": False,
                "requires_validator_approval_review": False,
                "requires_validator_output_review": False,
                "requires_validator_input_completion": True,
                "requires_validator_rerun_after_completion": True,
                "requires_separate_validator_execution_request": False,
                "requires_separate_evidence_builder_request": True,
                "template_transfer_execution_allowed": False,
                "validator_execution_allowed": False,
            }
        )
    if evidence_builder_request_ready:
        next_action.update(
            {
                "action_id": "NEXT-EBR-001",
                "sequence_step_id": "EBR-001",
                "blocker_id": "separate_evidence_builder_request",
                "category": "commercial_sprint_evidence_builder_request_review",
                "status": "ready_for_separate_evidence_builder_request",
                "why_this_action": (
                    "All five local input validators passed on human-confirmed "
                    "input, but evidence builders still require a separate explicit "
                    "human-approved execution request. This step does not authorize "
                    "builder execution, blocker closure, customer contact, launch, "
                    "or production-readiness claims."
                ),
                "quality_guide": status.get("source_validator_hold_output_review"),
                "template_preflight": status.get("source_validator_hold_output_review"),
                "input_sheet": status.get("source_validator_hold_output_review"),
                "post_fill_readiness_preview": status.get(
                    "source_validator_hold_output_review"
                ),
                "post_fill_validation_runbook": status.get(
                    "source_validator_hold_output_review"
                ),
                "required_human_fields": ["human_evidence_builder_execution_decision"],
                "preferred_human_input_path": "separate_evidence_builder_request",
                "preferred_batch_size": 1,
                "preferred_template_row_count": int(status.get("validators_run_count", 5)),
                "preferred_template_missing_value_row_count": 0,
                "full_quick_fill_missing_value_row_count": int(
                    status.get("full_quick_fill_missing_value_row_count", 0)
                ),
                "selected_blocker_count": int(status.get("selected_blocker_count", 5)),
                "completed_value_row_count": int(status.get("completed_value_row_count", 64)),
                "missing_value_row_count": int(status.get("missing_value_row_count", 0)),
                "next_manual_steps": [
                    {
                        "step_id": "EBR-001",
                        "stage": "separate_evidence_builder_request_review",
                        "action": (
                            "Create and review a separate evidence-builder execution "
                            "request if you want to convert validated inputs into "
                            "local evidence outputs."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                    {
                        "step_id": "EBR-002",
                        "stage": "stop_before_blocker_closure",
                        "action": (
                            "Even after builder approval, blocker closure, customer "
                            "contact, launch, and production-readiness claims require "
                            "separate gates."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                ],
                "requires_human_input": True,
                "requires_template_preflight_reference": False,
                "requires_post_fill_readiness_preview": False,
                "requires_post_fill_validation_runbook": False,
                "requires_review_batch_template_e2e_dry_run": False,
                "requires_separate_local_output_apply_request": False,
                "requires_full_quick_fill_source_path_review": False,
                "requires_safety_preflight": False,
                "requires_quick_fill_validator": False,
                "requires_import_dry_run": False,
                "requires_workbook_import_approval_review": False,
                "requires_separate_workbook_import_execution_request": False,
                "requires_separate_template_transfer_execution_request": False,
                "requires_validator_approval_review": False,
                "requires_validator_output_review": False,
                "requires_validator_input_completion": False,
                "requires_validator_rerun_after_completion": False,
                "requires_separate_validator_execution_request": False,
                "requires_separate_evidence_builder_request": True,
                "template_transfer_execution_allowed": False,
                "validator_execution_allowed": False,
                "evidence_builder_execution_allowed": False,
            }
        )
    if validator_approval_ready:
        next_action.update(
            {
                "action_id": "NEXT-VAR-001",
                "sequence_step_id": "VAR-001",
                "blocker_id": "validator_approval_request",
                "category": "commercial_sprint_validator_approval_review",
                "status": "hold_validator_approval_required",
                "why_this_action": (
                    "Template transfer has completed into local human-filled "
                    "template files. The next bounded step is human review of "
                    "the five validator approval requests. This does not "
                    "authorize validator execution, evidence collection, blocker "
                    "closure, customer contact, launch, or production-readiness "
                    "claims."
                ),
                "quality_guide": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "template_preflight": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "input_sheet": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "post_fill_readiness_preview": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "post_fill_validation_runbook": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "required_human_fields": ["human_validator_approval_decision"],
                "preferred_human_input_path": "validator_approval_request",
                "preferred_batch_size": 1,
                "preferred_template_row_count": int(status.get("planned_validator_count", 5)),
                "preferred_template_missing_value_row_count": 0,
                "full_quick_fill_missing_value_row_count": int(
                    status.get("full_quick_fill_missing_value_row_count", 0)
                ),
                "selected_blocker_count": int(status.get("selected_blocker_count", 5)),
                "completed_value_row_count": int(status.get("completed_value_row_count", 64)),
                "missing_value_row_count": int(status.get("missing_value_row_count", 0)),
                "next_manual_steps": [
                    {
                        "step_id": "VAR-001",
                        "stage": "validator_approval_review",
                        "action": (
                            "Review commercial_sprint_validator_approval_request_packet.md "
                            "and decide whether the five local validators should be "
                            "approved for a separate execution request."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                    {
                        "step_id": "VAR-002",
                        "stage": "separate_validator_execution_request",
                        "action": (
                            "If validator execution is desired, create a separate "
                            "explicit human execution request. This summary does "
                            "not authorize validator execution."
                        ),
                        "command": "",
                        "execution_allowed_by_codex": False,
                    },
                ],
                "requires_human_input": True,
                "requires_template_preflight_reference": False,
                "requires_post_fill_readiness_preview": False,
                "requires_post_fill_validation_runbook": False,
                "requires_review_batch_template_e2e_dry_run": False,
                "requires_separate_local_output_apply_request": False,
                "requires_full_quick_fill_source_path_review": False,
                "requires_safety_preflight": False,
                "requires_quick_fill_validator": False,
                "requires_import_dry_run": False,
                "requires_workbook_import_approval_review": False,
                "requires_separate_workbook_import_execution_request": False,
                "requires_separate_template_transfer_execution_request": False,
                "requires_validator_approval_review": True,
                "requires_separate_validator_execution_request": True,
                "template_transfer_execution_allowed": False,
                "validator_execution_allowed": False,
            }
        )
    related_sequence_step = {
        "lane_id": "support_contact_owner_assignment",
        "sequence_step_id": human_sequence.get("current_step_id"),
        "blocker_id": human_sequence.get("first_blocker_id"),
        "status": human_sequence.get("status"),
        "entrypoint": human_sequence.get(
            "current_step_entrypoint", rel(FIRST_OWNER_INPUT_REQUEST_MD)
        ),
        "command_template_available": human_sequence.get(
            "current_step_command_template_available"
        )
        is True,
        "required_human_field_count": int(
            first_owner_request.get("required_human_field_count", 5)
        ),
        "completed_human_field_count": int(
            first_owner_request.get("completed_human_field_count", 0)
        ),
        "missing_human_field_count": int(
            first_owner_request.get("missing_human_field_count", 5)
        ),
        "execution_allowed_by_summary": False,
        "evidence_collection_authorized": False,
        "blocker_closure_allowed_by_summary": False,
        "default_decision": "hold",
    }
    payload: dict[str, Any] = {
        "commercial_next_action_summary_v0_1": True,
        "summary_type": "saee_commercial_next_action_summary",
        "summary_version": "v0.1",
        "summary_scope": (
            "local_commercial_readiness_validator_missing_input_completion_next_human_action"
            if validator_missing_input_completion_ready
            else
            "local_commercial_readiness_evidence_builder_request_next_human_action"
            if evidence_builder_request_ready
            else
            "local_commercial_readiness_validator_outputs_review_next_human_action"
            if validator_outputs_review_ready
            else
            "local_commercial_readiness_validator_approval_next_human_action"
            if validator_approval_ready
            else
            "local_commercial_readiness_template_transfer_execution_request_next_human_action"
            if template_transfer_ready and not template_transfer_execution_ready
            else "local_commercial_readiness_template_transfer_applier_execution_next_human_action"
            if template_transfer_execution_ready
            else "local_commercial_readiness_workbook_import_approval_next_human_action"
            if approval_ready
            else "local_commercial_readiness_review_batch_template_next_human_action"
        ),
        "status": (
            "hold_validator_input_evidence_completion_required"
            if validator_missing_input_completion_ready
            else
            "ready_for_separate_evidence_builder_request"
            if evidence_builder_request_ready
            else
            "hold_validator_outputs_review_required"
            if validator_outputs_review_ready
            else
            "hold_validator_approval_required"
            if validator_approval_ready
            else
            "ready_for_separate_human_template_transfer_execution_request"
            if template_transfer_ready and not template_transfer_execution_ready
            else "ready_for_template_transfer_execution"
            if template_transfer_execution_ready
            else "ready_for_human_workbook_import_approval"
            if approval_ready
            else "hold_human_quick_fill_required"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_next_action_summary.py",
        "source_commercial_readiness_status": rel(STATUS_JSON),
        "source_active_human_input_board": rel(ACTIVE_BOARD_JSON),
        "source_human_sequence_packet": rel(HUMAN_SEQUENCE_JSON),
        "source_first_owner_input_request_packet": rel(FIRST_OWNER_INPUT_REQUEST_JSON),
        "source_first_owner_input_request_markdown": rel(FIRST_OWNER_INPUT_REQUEST_MD),
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_review_batch_quality_guide_json": rel(REVIEW_BATCH_QUALITY_GUIDE_JSON),
        "source_review_batch_quality_guide_html": rel(REVIEW_BATCH_QUALITY_GUIDE_HTML),
        "source_review_batch_template_preflight_json": rel(REVIEW_BATCH_TEMPLATE_PREFLIGHT_JSON),
        "source_review_batch_template_preflight_markdown": rel(REVIEW_BATCH_TEMPLATE_PREFLIGHT_MD),
        "source_post_fill_readiness_preview_json": rel(POST_FILL_READINESS_PREVIEW_JSON),
        "source_post_fill_readiness_preview_html": rel(POST_FILL_READINESS_PREVIEW_HTML),
        "source_post_fill_runbook_json": rel(POST_FILL_RUNBOOK_JSON),
        "source_post_fill_validation_runbook_html": rel(POST_FILL_RUNBOOK_HTML),
        "source_validator_approval_request_packet": rel(VALIDATOR_APPROVAL_PACKET_MD),
        "source_validator_hold_output_review": status.get(
            "source_validator_hold_output_review"
        ),
        "source_review_batch_template_csv": rel(REVIEW_BATCH_TEMPLATE_CSV),
        "quality_guide_status": quality_guide.get("status"),
        "quality_guide_row_count": int(quality_guide.get("guide_row_count", 10)),
        "quality_guide_target_blocker_id": quality_guide.get("target_blocker_id"),
        "template_preflight_status": template_preflight.get("status"),
        "template_preflight_passed": template_preflight.get("preflight_passed") is True,
        "template_preflight_boundary_violation_count": int(
            template_preflight.get("boundary_violation_count", 0)
        ),
        "post_fill_runbook_status": post_fill_runbook.get("status"),
        "post_fill_validation_ready": post_fill_runbook.get("post_fill_validation_ready") is True,
        "post_fill_missing_human_value_row_count": int(
            post_fill_runbook.get("missing_human_value_row_count", 10)
        ),
        "post_fill_readiness_preview_status": post_fill_preview.get("status"),
        "post_fill_readiness_preview_ready": post_fill_preview.get("post_fill_check_ready")
        is True,
        "post_fill_readiness_preview_missing_human_value_row_count": int(
            post_fill_preview.get("missing_human_value_row_count", 10)
        ),
        "commercial_status": status.get("commercial_status", "hold"),
        "controlled_preview_status": status.get("controlled_preview_status", "hold"),
        "production_launch_status": status.get("production_launch_status", "hold"),
        "production_blocker_count": int(status.get("production_blocker_count", 24)),
        "satisfied_production_checks": int(status.get("satisfied_production_checks", 0)),
        "active_stage": status.get("active_stage", "human_quick_fill"),
        "preferred_human_input_path": (
            "validator_missing_input_completion"
            if validator_missing_input_completion_ready
            else
            "separate_evidence_builder_request"
            if evidence_builder_request_ready
            else
            "validator_hold_output_review"
            if validator_outputs_review_ready
            else
            "validator_approval_request"
            if validator_approval_ready
            else
            "template_transfer_applier_execution"
            if template_transfer_execution_ready
            else "template_transfer_execution_request"
            if template_transfer_ready
            else "workbook_import_approval_request"
            if approval_ready
            else board.get("preferred_human_input_path", "review_batch_10_row_template")
        ),
        "preferred_batch_size": (
            5 if validator_missing_input_completion_ready else
            1 if evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready else int(board.get("preferred_batch_size", 10))
        ),
        "preferred_template_row_count": (
            int(status.get("validators_run_count", 5))
            if validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready
            else
            int(status.get("planned_validator_count", 5))
            if validator_approval_ready
            else
            int(status.get("target_template_count", 5))
            if template_transfer_ready
            else 1
            if approval_ready
            else int(board.get("preferred_template_row_count", 10))
        ),
        "preferred_template_value_present_row_count": int(
            int(status.get("target_template_count", 5))
            if template_transfer_ready or validator_approval_ready or validator_outputs_review_ready or validator_missing_input_completion_ready or evidence_builder_request_ready
            else 1
            if approval_ready
            else board.get("preferred_template_value_present_row_count", 0)
        ),
        "preferred_template_missing_value_row_count": int(
            int(status.get("total_missing_metadata_field_count", 0) or 0)
            + int(status.get("total_missing_evidence_item_count", 0) or 0)
            + int(status.get("total_missing_source_note_count", 0) or 0)
            if validator_missing_input_completion_ready
            else
            0
            if evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready
            else board.get("preferred_template_missing_value_row_count", 10)
        ),
        "ready_for_preferred_template_human_fill": (
            False
            if validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready
            else board.get("ready_for_preferred_template_human_fill") is True
        ),
        "full_quick_fill_missing_value_row_count": int(
            status.get(
                "full_quick_fill_missing_value_row_count",
                board.get("full_quick_fill_missing_value_row_count", 64),
            )
        ),
        "quick_fill_row_count": int(board.get("quick_fill_row_count", 64)),
        "selected_blocker_count": int(board.get("selected_blocker_count", 5)),
        "completed_value_row_count": int(board.get("completed_value_row_count", 0)),
        "missing_value_row_count": int(board.get("missing_value_row_count", 64)),
        "ready_for_human_fill": board.get("ready_for_human_fill") is True,
        "ready_for_safety_preflight": board.get("ready_for_safety_preflight") is True,
        "ready_for_workbook_import": board.get("ready_for_workbook_import") is True,
        "ready_for_workbook_import_approval": board.get("ready_for_workbook_import_approval") is True,
        "next_action_count": 1,
        "first_action_id": next_action["action_id"],
        "first_sequence_step_id": next_action["sequence_step_id"],
        "first_blocker_id": next_action["blocker_id"],
        "next_actions": [next_action],
        "parallel_human_input_lane_count": 2,
        "primary_human_input_lane": (
            "commercial_sprint_validator_missing_input_completion"
            if validator_missing_input_completion_ready
            else
            "commercial_sprint_evidence_builder_request_review"
            if evidence_builder_request_ready
            else
            "commercial_sprint_validator_hold_output_review"
            if validator_outputs_review_ready
            else
            "commercial_sprint_validator_approval_review"
            if validator_approval_ready
            else
            "commercial_sprint_template_transfer_applier_execution"
            if template_transfer_execution_ready
            else "commercial_sprint_template_transfer_execution_request_review"
            if template_transfer_ready
            else "commercial_sprint_workbook_import_approval_review"
            if approval_ready
            else "commercial_sprint_review_batch_template"
        ),
        "related_human_sequence_lane": "support_contact_owner_assignment",
        "related_human_sequence_step_id": related_sequence_step["sequence_step_id"],
        "related_human_sequence_blocker_id": related_sequence_step["blocker_id"],
        "related_human_sequence_status": related_sequence_step["status"],
        "related_human_sequence_entrypoint": related_sequence_step["entrypoint"],
        "related_human_sequence_command_template_available": related_sequence_step[
            "command_template_available"
        ],
        "related_human_sequence_missing_human_field_count": related_sequence_step[
            "missing_human_field_count"
        ],
        "related_human_sequence_step": related_sequence_step,
        "next_action_reconciliation": (
            "The local validators have already run and all outputs remain hold. "
            "The validator hold-output review is complete and identified missing "
            "metadata fields, evidence review items, and source notes. The next "
            "lane is only completion of those missing inputs and a later local "
            "validator rerun. This does not authorize evidence builders, evidence "
            "collection, blocker closure, or production-readiness claims."
            if validator_missing_input_completion_ready
            else
            "All five local input validators have passed on human-confirmed "
            "inputs. The next lane is only a separate evidence-builder execution "
            "request review. This summary does not authorize evidence builders, "
            "evidence collection, blocker closure, customer contact, launch, or "
            "production-readiness claims."
            if evidence_builder_request_ready
            else
            "Template transfer has completed locally. The next lane is only "
            "human review of validator approval requests. This does not authorize "
            "validator execution on real input, evidence collection, blocker "
            "closure, or production-readiness claims."
            if validator_approval_ready
            else
            "The local validators have already run and all outputs remain hold. "
            "The next lane is only human review of validator hold outputs. This "
            "does not authorize evidence builders, evidence collection, blocker "
            "closure, or production-readiness claims."
            if validator_outputs_review_ready
            else
            "The separate template-transfer execution request has been approved. "
            "The next lane is only the controlled local template-transfer applier. "
            "This does not authorize validator execution on real input, evidence "
            "collection, blocker closure, or production-readiness claims."
            if template_transfer_execution_ready
            else
            "All 64 confirmed values have already been imported into the local "
            "workbook, so the primary next lane is human review of the separate "
            "template transfer execution request. This does not authorize "
            "template transfer, validator execution on real input, evidence "
            "collection, or blocker closure."
            if template_transfer_ready
            else "All 64 quick-fill rows are present, so the primary next lane is "
            "human review of the workbook import approval request. This does "
            "not authorize workbook import execution, evidence collection, or "
            "blocker closure."
            if approval_ready
            else "The 10-row review-batch template is the primary next human-input "
            "lane. The full 64-row quick-fill packet remains the complete source "
            "path after small-batch review. The support_contact owner-assignment "
            "lane is a related human sequence entrypoint for SEQ-001. No lane "
            "authorizes execution, evidence collection, import, or blocker closure."
        ),
        "human_input_required": True,
        "separate_template_preflight_reference_required": not (validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready),
        "separate_post_fill_readiness_preview_required": not (validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready),
        "separate_post_fill_validation_runbook_required": not (validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready),
        "separate_review_batch_template_e2e_dry_run_required": not (validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready or template_transfer_ready or approval_ready),
        "separate_local_output_apply_request_required": False,
        "separate_full_quick_fill_source_path_review_required": not (evidence_builder_request_ready or validator_approval_ready or template_transfer_ready or approval_ready),
        "separate_safety_preflight_required": False,
        "separate_validator_required": False,
        "separate_import_dry_run_required": False,
        "separate_workbook_import_approval_review_required": approval_ready and not (evidence_builder_request_ready or validator_approval_ready or template_transfer_ready),
        "separate_workbook_import_execution_request_required": False if (validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready) else not template_transfer_ready,
        "separate_template_transfer_execution_request_required": False if (validator_missing_input_completion_ready or evidence_builder_request_ready or validator_outputs_review_ready or validator_approval_ready) else (
            template_transfer_ready and not template_transfer_execution_ready
        ),
        "ready_for_template_transfer_request": template_transfer_ready,
        "ready_for_separate_human_template_transfer_execution_request": template_transfer_ready,
        "ready_for_template_transfer_execution": template_transfer_execution_ready,
        "human_template_transfer_execution_request_recorded": status.get(
            "human_template_transfer_execution_request_recorded"
        )
        is True,
        "human_template_transfer_execution_authorized": status.get(
            "human_template_transfer_execution_authorized"
        )
        is True,
        "required_transfer_ready_count": int(status.get("required_transfer_ready_count", 0)),
        "target_template_count": int(status.get("target_template_count", 0)),
        "source_workbook_import_performed": status.get("source_workbook_import_performed") is True,
        "source_workbook_written": status.get("source_workbook_written") is True,
        "current_stage_import_completed": status.get("current_stage_import_completed") is True,
        "template_transfer_authorized": status.get("template_transfer_authorized") is True,
        "template_transfer_performed": status.get("template_transfer_performed") is True,
        "template_transfer_values_transferred": status.get("template_transfer_values_transferred") is True,
        "template_transfer_human_filled_templates_written": status.get(
            "template_transfer_human_filled_templates_written"
        )
        is True,
        "template_transfer_values_transferred_count": int(
            status.get("template_transfer_values_transferred_count", 0) or 0
        ),
        "template_transfer_templates_written_count": int(
            status.get("template_transfer_templates_written_count", 0) or 0
        ),
        "template_transfer_execution_allowed": False if validator_approval_ready else template_transfer_execution_ready,
        "template_transfer_applier_execution_allowed": False if validator_approval_ready else template_transfer_execution_ready,
        "ready_for_validator_approval": status.get("ready_for_validator_approval") is True,
        "ready_for_validator_execution": False,
        "validator_execution_run_status": status.get("validator_execution_run_status"),
        "validator_hold_output_review_status": status.get(
            "validator_hold_output_review_status"
        ),
        "validator_hold_output_review_completed": (
            status.get("validator_hold_output_review_completed") is True
        ),
        "validator_outputs_review_required": validator_outputs_review_ready,
        "validator_missing_input_completion_required": (
            validator_missing_input_completion_ready
        ),
        "rerun_validators_after_completion_required": (
            status.get("rerun_validators_after_completion_required") is True
        ),
        "total_missing_metadata_field_count": int(
            status.get("total_missing_metadata_field_count", 0) or 0
        ),
        "total_missing_evidence_item_count": int(
            status.get("total_missing_evidence_item_count", 0) or 0
        ),
        "total_missing_source_note_count": int(
            status.get("total_missing_source_note_count", 0) or 0
        ),
        "local_validators_run": status.get("local_validators_run") is True,
        "planned_validator_count": int(status.get("planned_validator_count", 0) or 0),
        "ready_validator_count": int(status.get("ready_validator_count", 0) or 0),
        "validator_approval_request_count": int(
            status.get("validator_approval_request_count", 0) or 0
        ),
        "approved_validator_count": int(status.get("approved_validator_count", 0) or 0),
        "validator_execution_authorized_count": int(
            status.get("validator_execution_authorized_count", 0) or 0
        ),
        "validators_run": status.get("validators_run") is True,
        "validators_run_count": int(status.get("validators_run_count", 0) or 0),
        "validator_hold_count": int(status.get("validator_hold_count", 0) or 0),
        "validator_pass_count": int(status.get("validator_pass_count", 0) or 0),
        "validator_stop_count": int(status.get("validator_stop_count", 0) or 0),
        "builder_ready_count": int(status.get("builder_ready_count", 0) or 0),
        "blockers_closed_by_validator_run": int(status.get("blockers_closed_by_validator_run", 0) or 0),
        "requires_validator_approval_review": validator_approval_ready,
        "requires_validator_output_review": validator_outputs_review_ready,
        "requires_validator_input_completion": validator_missing_input_completion_ready,
        "requires_validator_rerun_after_completion": validator_missing_input_completion_ready,
        "requires_separate_validator_execution_request": validator_approval_ready,
        "requires_separate_evidence_builder_request": (
            evidence_builder_request_ready
            or validator_outputs_review_ready
            or validator_missing_input_completion_ready
        ),
        "next_human_action": (
            "Complete the missing metadata fields, evidence review items, and "
            "source notes listed in commercial_sprint_validator_hold_output_review.md. "
            "After completion, rerun the local validators. Do not run evidence "
            "builders, close blockers, contact anyone, launch, or claim production "
            "readiness from this summary."
            if validator_missing_input_completion_ready
            else
            "All five local input validators pass. If you want to continue, "
            "create a separate explicit evidence-builder execution request. "
            "Do not run evidence builders, close blockers, contact anyone, "
            "launch, or claim production readiness from this summary."
            if evidence_builder_request_ready
            else
            "Review commercial_sprint_validator_execution_run.md. All five local "
            "validators ran and returned hold. Complete missing input or boundary "
            "evidence before any separate evidence-builder request. Do not collect "
            "evidence, close blockers, contact anyone, launch, or claim production "
            "readiness from this summary."
            if validator_outputs_review_ready
            else
            "Review commercial_sprint_validator_approval_request_packet.md. If "
            "validator execution is desired, issue a separate explicit human "
            "execution request. Do not run validators, collect evidence, close "
            "blockers, contact anyone, launch, or claim production readiness "
            "from this summary."
            if validator_approval_ready
            else
            "Run only the controlled local template-transfer applier authorized "
            "by the separate human approval record. After transfer, stop before "
            "validators on real input, evidence collection, blocker closure, or "
            "production-readiness claims."
            if template_transfer_execution_ready
            else
            "Review commercial_sprint_template_transfer_execution_request_packet.md. "
            "If template transfer execution is desired, issue a separate explicit "
            "human execution request. Do not transfer templates, run validators "
            "on real input, collect evidence, or close blockers from this summary."
            if template_transfer_ready
            else "Review commercial_sprint_workbook_import_approval_request_packet.md. "
            "If workbook import execution is desired, issue a separate explicit "
            "human execution request. Do not run workbook import, template "
            "transfer, validators on real input, evidence collection, or blocker "
            "closure from this summary."
            if approval_ready
            else "Open the review-batch quality guide first, confirm template preflight "
            "is pass-ready, then Fill only human_value_to_enter and optional notes_for_human in "
            "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv, "
            "open the post-fill readiness preview to confirm whether the 10 rows now have "
            "human values, open the post-fill validation runbook, then run the local "
            "review-batch template e2e dry run. Stop before any "
            "local-output apply, source quick-fill update, workbook import, evidence "
            "collection, or blocker closure unless a separate human approval exists."
        ),
        "blockers_closed_by_summary": 0,
        "blockers_ready_to_close": [],
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["validators_run_on_real_input"] = payload.get("validators_run") is True
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    action = payload["next_actions"][0]
    related_sequence_step = payload["related_human_sequence_step"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "action_id",
                "sequence_step_id",
                "blocker_id",
                "status",
                "quality_guide",
                "template_preflight",
                "input_sheet",
                "post_fill_readiness_preview",
                "post_fill_validation_runbook",
                "preferred_human_input_path",
                "preferred_template_missing_value_row_count",
                "full_quick_fill_missing_value_row_count",
                "missing_value_row_count",
                "requires_human_input",
                "execution_allowed_by_summary",
                "blocker_closure_allowed_by_summary",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "action_id": action["action_id"],
                "sequence_step_id": action["sequence_step_id"],
                "blocker_id": action["blocker_id"],
                "status": action["status"],
                "quality_guide": action["quality_guide"],
                "template_preflight": action["template_preflight"],
                "input_sheet": action["input_sheet"],
                "post_fill_readiness_preview": action["post_fill_readiness_preview"],
                "post_fill_validation_runbook": action["post_fill_validation_runbook"],
                "preferred_human_input_path": action["preferred_human_input_path"],
                "preferred_template_missing_value_row_count": action[
                    "preferred_template_missing_value_row_count"
                ],
                "full_quick_fill_missing_value_row_count": action[
                    "full_quick_fill_missing_value_row_count"
                ],
                "missing_value_row_count": action["missing_value_row_count"],
                "requires_human_input": "true",
                "execution_allowed_by_summary": "false",
                "blocker_closure_allowed_by_summary": "false",
            }
        )

    content = f"""# SAEE Commercial Next Action Summary v0.1

## Entry Files

- `phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.local.json`
- `phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.md`
- `phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.csv`
- `phase_b_product/commercial_readiness/commercial_next_action_summary/README.md`

## Status

commercial_next_action_summary_v0_1: true
summary_scope: {payload['summary_scope']}
status: {payload['status']}
first_action_id: {payload['first_action_id']}
first_sequence_step_id: {payload['first_sequence_step_id']}
first_blocker_id: {payload['first_blocker_id']}
commercial_status: {payload['commercial_status']}
controlled_preview_status: {payload['controlled_preview_status']}
production_launch_status: {payload['production_launch_status']}
production_blocker_count: {payload['production_blocker_count']}
satisfied_production_checks: {payload['satisfied_production_checks']}
source_review_batch_quality_guide_html: {payload['source_review_batch_quality_guide_html']}
quality_guide_status: {payload['quality_guide_status']}
quality_guide_row_count: {payload['quality_guide_row_count']}
quality_guide_target_blocker_id: {payload['quality_guide_target_blocker_id']}
source_review_batch_template_preflight_markdown: {payload['source_review_batch_template_preflight_markdown']}
template_preflight_status: {payload['template_preflight_status']}
template_preflight_passed: {str(payload['template_preflight_passed']).lower()}
template_preflight_boundary_violation_count: {payload['template_preflight_boundary_violation_count']}
source_post_fill_readiness_preview_html: {payload['source_post_fill_readiness_preview_html']}
post_fill_readiness_preview_status: {payload['post_fill_readiness_preview_status']}
post_fill_readiness_preview_ready: {str(payload['post_fill_readiness_preview_ready']).lower()}
post_fill_readiness_preview_missing_human_value_row_count: {payload['post_fill_readiness_preview_missing_human_value_row_count']}
source_post_fill_validation_runbook_html: {payload['source_post_fill_validation_runbook_html']}
source_validator_approval_request_packet: {payload['source_validator_approval_request_packet']}
source_validator_hold_output_review: {payload['source_validator_hold_output_review']}
validator_execution_run_status: {payload['validator_execution_run_status']}
validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
validator_hold_output_review_completed: {str(payload['validator_hold_output_review_completed']).lower()}
validator_outputs_review_required: {str(payload['validator_outputs_review_required']).lower()}
validator_missing_input_completion_required: {str(payload['validator_missing_input_completion_required']).lower()}
rerun_validators_after_completion_required: {str(payload['rerun_validators_after_completion_required']).lower()}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
local_validators_run: {str(payload['local_validators_run']).lower()}
post_fill_runbook_status: {payload['post_fill_runbook_status']}
post_fill_validation_ready: {str(payload['post_fill_validation_ready']).lower()}
post_fill_missing_human_value_row_count: {payload['post_fill_missing_human_value_row_count']}
active_stage: {payload['active_stage']}
parallel_human_input_lane_count: {payload['parallel_human_input_lane_count']}
primary_human_input_lane: {payload['primary_human_input_lane']}
preferred_human_input_path: {payload['preferred_human_input_path']}
preferred_batch_size: {payload['preferred_batch_size']}
preferred_template_row_count: {payload['preferred_template_row_count']}
preferred_template_value_present_row_count: {payload['preferred_template_value_present_row_count']}
preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}
ready_for_preferred_template_human_fill: {str(payload['ready_for_preferred_template_human_fill']).lower()}
full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
related_human_sequence_lane: {payload['related_human_sequence_lane']}
related_sequence_step_id: {related_sequence_step['sequence_step_id']}
related_sequence_blocker_id: {related_sequence_step['blocker_id']}
related_sequence_status: {related_sequence_step['status']}
related_sequence_entrypoint: {related_sequence_step['entrypoint']}
related_sequence_command_template_available: {str(related_sequence_step['command_template_available']).lower()}
related_sequence_missing_human_field_count: {related_sequence_step['missing_human_field_count']}
quick_fill_row_count: {payload['quick_fill_row_count']}
selected_blocker_count: {payload['selected_blocker_count']}
completed_value_row_count: {payload['completed_value_row_count']}
missing_value_row_count: {payload['missing_value_row_count']}
ready_for_human_fill: {str(payload['ready_for_human_fill']).lower()}
ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}
ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}
ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}
human_input_required: {str(payload['human_input_required']).lower()}
separate_template_preflight_reference_required: {str(payload['separate_template_preflight_reference_required']).lower()}
separate_post_fill_readiness_preview_required: {str(payload['separate_post_fill_readiness_preview_required']).lower()}
separate_post_fill_validation_runbook_required: {str(payload['separate_post_fill_validation_runbook_required']).lower()}
separate_review_batch_template_e2e_dry_run_required: {str(payload['separate_review_batch_template_e2e_dry_run_required']).lower()}
separate_local_output_apply_request_required: {str(payload['separate_local_output_apply_request_required']).lower()}
separate_full_quick_fill_source_path_review_required: {str(payload['separate_full_quick_fill_source_path_review_required']).lower()}
separate_safety_preflight_required: {str(payload['separate_safety_preflight_required']).lower()}
separate_validator_required: {str(payload['separate_validator_required']).lower()}
separate_import_dry_run_required: {str(payload['separate_import_dry_run_required']).lower()}
separate_workbook_import_approval_review_required: {str(payload['separate_workbook_import_approval_review_required']).lower()}
separate_workbook_import_execution_request_required: {str(payload['separate_workbook_import_execution_request_required']).lower()}
separate_template_transfer_execution_request_required: {str(payload['separate_template_transfer_execution_request_required']).lower()}
ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
ready_for_separate_human_template_transfer_execution_request: {str(payload['ready_for_separate_human_template_transfer_execution_request']).lower()}
ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
human_template_transfer_execution_request_recorded: {str(payload['human_template_transfer_execution_request_recorded']).lower()}
human_template_transfer_execution_authorized: {str(payload['human_template_transfer_execution_authorized']).lower()}
required_transfer_ready_count: {payload['required_transfer_ready_count']}
target_template_count: {payload['target_template_count']}
source_workbook_import_performed: {str(payload['source_workbook_import_performed']).lower()}
source_workbook_written: {str(payload['source_workbook_written']).lower()}
current_stage_import_completed: {str(payload['current_stage_import_completed']).lower()}
template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
template_transfer_values_transferred: {str(payload['template_transfer_values_transferred']).lower()}
template_transfer_human_filled_templates_written: {str(payload['template_transfer_human_filled_templates_written']).lower()}
template_transfer_values_transferred_count: {payload['template_transfer_values_transferred_count']}
template_transfer_templates_written_count: {payload['template_transfer_templates_written_count']}
template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
planned_validator_count: {payload['planned_validator_count']}
ready_validator_count: {payload['ready_validator_count']}
validator_approval_request_count: {payload['validator_approval_request_count']}
approved_validator_count: {payload['approved_validator_count']}
validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
validators_run: {str(payload['validators_run']).lower()}
validators_run_count: {payload['validators_run_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_pass_count: {payload['validator_pass_count']}
validator_stop_count: {payload['validator_stop_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
requires_validator_approval_review: {str(payload['requires_validator_approval_review']).lower()}
requires_validator_output_review: {str(payload['requires_validator_output_review']).lower()}
requires_validator_input_completion: {str(payload['requires_validator_input_completion']).lower()}
requires_validator_rerun_after_completion: {str(payload['requires_validator_rerun_after_completion']).lower()}
requires_separate_validator_execution_request: {str(payload['requires_separate_validator_execution_request']).lower()}
requires_separate_evidence_builder_request: {str(payload['requires_separate_evidence_builder_request']).lower()}
blockers_closed_by_summary: 0
workbook_import_authorized: false
workbook_import_performed: false
workbook_written: false
values_transferred: false
validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}
real_evidence_created: false
evidence_collection_authorized: false
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Next Human Action

{payload['next_human_action']}

## Related Human Sequence Lane

The `support_contact` owner-assignment lane remains a related human sequence
entrypoint for `SEQ-001`:

- entrypoint: `{related_sequence_step['entrypoint']}`
- command_template_available: {str(related_sequence_step['command_template_available']).lower()}
- missing_human_field_count: {related_sequence_step['missing_human_field_count']}

This lane is not an automatic execution route. It requires separate human owner
input and does not authorize evidence collection or blocker closure.

## Stop Point

Only human review of validator hold outputs is currently in scope. Stop before
evidence builders, evidence collection, blocker closure, customer/vendor
contact, product launch, and production-readiness claims unless a separate
human approval exists.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    README_PATH.write_text(content, encoding="utf-8")
    DOC_PATH.write_text(content, encoding="utf-8")
    GATE_PATH.write_text(
        content
        + f"""
## Recommendation Gate

answer: conditional
recommend_for_next_human_action_guidance: true
recommend_for_validator_outputs_review: {str(payload['requires_validator_output_review']).lower()}
recommend_for_template_transfer_execution_request_review: {str(payload['separate_template_transfer_execution_request_required']).lower()}
recommend_for_review_batch_template_human_input: {str(not payload['separate_workbook_import_approval_review_required'] and not payload['separate_template_transfer_execution_request_required'] and not payload['ready_for_template_transfer_execution']).lower()}
recommend_for_quick_fill_human_input: false
recommend_for_workbook_import_approval_request: {str(payload['separate_workbook_import_approval_review_required']).lower()}
recommend_for_template_transfer_execution: false
recommend_for_validator_approval_review: {str(payload['requires_validator_approval_review']).lower()}
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_workbook_import_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_summary()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_NEXT_ACTION_SUMMARY: PASS "
        f"status={payload['status']} "
        f"missing_value_row_count={payload['missing_value_row_count']} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
