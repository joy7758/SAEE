#!/usr/bin/env python3
"""Write a local commercial readiness status snapshot.

This is a file-backed aggregation layer over the existing commercial go/no-go
service and the active commercial sprint human-input board. It does not read
external evidence paths, enter values, import workbooks, execute validators on
real input, collect evidence, close blockers, contact anyone, launch product,
or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

GO_NO_GO_JSON = COMMERCIAL_DIR / "commercial_go_no_go.local.json"
STATUS_JSON = COMMERCIAL_DIR / "commercial_readiness_status.local.json"
STATUS_MD = COMMERCIAL_DIR / "commercial_readiness_status.md"
STATUS_CSV = COMMERCIAL_DIR / "commercial_readiness_status.csv"
STATUS_HTML = COMMERCIAL_DIR / "commercial_readiness_status.html"
BOUNDARY_MD = COMMERCIAL_DIR / "commercial_readiness_status_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_READINESS_STATUS_SNAPSHOT_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_READINESS_STATUS_SNAPSHOT_RECOMMENDATION_GATE.md"
)

ACTIVE_BOARD_JSON = SPRINT_DIR / "commercial_sprint_active_human_input_board.local.json"
NEXT_ACTION_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_action_summary/commercial_next_action_summary.local.json"
)
BEGIN_HERE_JSON = (
    COMMERCIAL_DIR
    / "commercial_readiness_begin_here/commercial_readiness_begin_here.local.json"
)
APPROVAL_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_approval_request_packet.local.json"
WORKBOOK_IMPORT_APPLIED_JSON = (
    SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.local.json"
)
TEMPLATE_TRANSFER_REQUEST_JSON = (
    SPRINT_DIR / "commercial_sprint_template_transfer_execution_request_packet.local.json"
)
TEMPLATE_TRANSFER_APPROVAL_JSON = (
    SPRINT_DIR / "commercial_sprint_template_transfer_execution_approval.local.json"
)
TEMPLATE_TRANSFER_APPLIER_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.local.json"
)
POST_TRANSFER_VALIDATOR_SEQUENCE_JSON = (
    SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.local.json"
)
VALIDATOR_APPROVAL_PACKET_JSON = (
    SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.local.json"
)
VALIDATOR_EXECUTION_RUN_JSON = (
    SPRINT_DIR / "commercial_sprint_validator_execution_run.local.json"
)
VALIDATOR_HOLD_OUTPUT_REVIEW_JSON = (
    SPRINT_DIR / "commercial_sprint_validator_hold_output_review.local.json"
)
SAFETY_JSON = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.local.json"
IMPORT_DRY_RUN_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_import_dry_run.local.json"
)
IMPORTER_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_workbook_importer.local.json"
VALIDATION_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet_validation.local.json"

FALSE_FLAGS = [
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "customer_contacted",
    "vendor_contacted",
    "payment_collected",
    "revenue_validated",
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
    "development_permission_granted",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def missing_source_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "path": rel(path)}
    data = read_json(path)
    return {
        "status": data.get("status", "unknown"),
        "path": rel(path),
    }


def source_boundary_violations(sources: dict[str, dict[str, Any]]) -> list[str]:
    violations: list[str] = []
    source_allowed_true_flags = {
        "begin_here": {
            "validators_run_on_real_input",
        },
        "next_action_summary": {
            "validators_run_on_real_input",
        },
        "workbook_import_applied": {
            "human_execution_authorized",
            "workbook_import_authorized",
            "workbook_import_performed",
            "workbook_written",
        },
        "template_transfer_applier": {
            "apply_performed",
            "human_execution_authorized",
            "human_filled_templates_written",
            "values_transferred",
        },
        "validator_execution_run": {
            "human_validator_execution_authorized",
            "task_candidates_executed",
            "validator_execution_authorized",
            "validators_run_on_real_input",
        }
    }
    for source_name, payload in sources.items():
        for field in FALSE_FLAGS:
            if field in source_allowed_true_flags.get(source_name, set()):
                continue
            if payload.get(field) is True:
                violations.append(f"{source_name}:{field}_true")
        if int(payload.get("boundary_violation_count", 0) or 0) > 0:
            violations.append(f"{source_name}:boundary_violation_count_nonzero")
    return sorted(set(violations))


def build_snapshot() -> tuple[dict[str, Any], dict[str, Any]]:
    go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    active_board = read_json(ACTIVE_BOARD_JSON)
    next_action = read_json(NEXT_ACTION_JSON)
    begin_here = read_json(BEGIN_HERE_JSON)
    approval = read_json(APPROVAL_JSON)
    workbook_import_applied = read_json(WORKBOOK_IMPORT_APPLIED_JSON)
    template_transfer_request = read_json(TEMPLATE_TRANSFER_REQUEST_JSON)
    template_transfer_approval = read_json(TEMPLATE_TRANSFER_APPROVAL_JSON)
    template_transfer_applier = read_json(TEMPLATE_TRANSFER_APPLIER_JSON)
    post_transfer_validator_sequence = read_json(POST_TRANSFER_VALIDATOR_SEQUENCE_JSON)
    validator_approval_packet = read_json(VALIDATOR_APPROVAL_PACKET_JSON)
    validator_execution_run = read_json(VALIDATOR_EXECUTION_RUN_JSON)
    validator_hold_output_review = read_json(VALIDATOR_HOLD_OUTPUT_REVIEW_JSON)
    safety = read_json(SAFETY_JSON)
    import_dry_run = read_json(IMPORT_DRY_RUN_JSON)
    importer = read_json(IMPORTER_JSON)
    validation = read_json(VALIDATION_JSON)
    sources = {
        "go_no_go": go_no_go,
        "active_board": active_board,
        "next_action_summary": next_action,
        "begin_here": begin_here,
        "approval_packet": approval,
        "workbook_import_applied": workbook_import_applied,
        "template_transfer_request_packet": template_transfer_request,
        "template_transfer_execution_approval": template_transfer_approval,
        "template_transfer_applier": template_transfer_applier,
        "post_transfer_validator_sequence": post_transfer_validator_sequence,
        "validator_approval_request_packet": validator_approval_packet,
        "validator_execution_run": validator_execution_run,
        "validator_hold_output_review": validator_hold_output_review,
        "safety_preflight": safety,
        "import_dry_run": import_dry_run,
        "importer": importer,
        "quick_fill_validation": validation,
    }
    boundary_violations = source_boundary_violations(sources)

    commercial_status = str(go_no_go.get("commercial_status", "hold"))
    production_launch_status = str(go_no_go.get("production_launch_status", "hold"))
    template_transfer_request_ready = (
        template_transfer_request.get(
            "ready_for_separate_human_template_transfer_execution_request"
        )
        is True
        and template_transfer_request.get("ready_for_template_transfer_request") is True
        and workbook_import_applied.get("ready_for_template_transfer_request") is True
    )
    template_transfer_execution_ready = (
        template_transfer_request_ready
        and template_transfer_request.get("ready_for_template_transfer_execution") is True
        and template_transfer_request.get("template_transfer_authorized") is True
        and template_transfer_approval.get("template_transfer_authorized") is True
        and template_transfer_approval.get("human_execution_authorized") is True
    )
    template_transfer_performed = (
        template_transfer_applier.get("apply_performed") is True
        and template_transfer_applier.get("values_transferred") is True
        and template_transfer_applier.get("human_filled_templates_written") is True
        and int(template_transfer_applier.get("values_transferred_count", 0) or 0) == 64
        and int(template_transfer_applier.get("templates_written_count", 0) or 0) == 5
    )
    validator_approval_ready = (
        template_transfer_performed
        and validator_approval_packet.get("status") == "hold_validator_approval_required"
        and validator_approval_packet.get("ready_for_validator_approval") is True
        and validator_approval_packet.get("ready_for_validator_execution") is False
        and int(validator_approval_packet.get("ready_validator_count", 0) or 0) == 5
        and int(validator_approval_packet.get("approved_validator_count", 0) or 0) == 0
        and int(validator_approval_packet.get("validator_execution_authorized_count", 0) or 0) == 0
    )
    validator_execution_holds_completed = (
        validator_execution_run.get("status") == "completed_with_validator_holds"
        and validator_execution_run.get("human_validator_execution_authorized") is True
        and validator_execution_run.get("validator_execution_authorized") is True
        and int(validator_execution_run.get("validators_run_count", 0) or 0) == 5
        and int(validator_execution_run.get("validator_hold_count", 0) or 0) == 5
        and int(validator_execution_run.get("validator_pass_count", 0) or 0) == 0
        and int(validator_execution_run.get("validator_stop_count", 0) or 0) == 0
        and int(validator_execution_run.get("builder_ready_count", 0) or 0) == 0
        and int(validator_execution_run.get("blockers_closed_by_run", 0) or 0) == 0
    )
    validator_execution_passed_completed = (
        validator_execution_run.get("status") == "completed_all_validators_passed"
        and validator_execution_run.get("human_validator_execution_authorized") is True
        and validator_execution_run.get("validator_execution_authorized") is True
        and int(validator_execution_run.get("validators_run_count", 0) or 0) == 5
        and int(validator_execution_run.get("validator_hold_count", 0) or 0) == 0
        and int(validator_execution_run.get("validator_pass_count", 0) or 0) == 5
        and int(validator_execution_run.get("validator_stop_count", 0) or 0) == 0
        and int(validator_execution_run.get("builder_ready_count", 0) or 0) == 5
        and int(validator_execution_run.get("blockers_closed_by_run", 0) or 0) == 0
    )
    validator_execution_completed = (
        validator_execution_holds_completed or validator_execution_passed_completed
    )
    validator_hold_output_review_completed = (
        validator_hold_output_review.get("status")
        == "hold_missing_validator_input_evidence_reviewed"
        and validator_hold_output_review.get(
            "commercial_sprint_validator_hold_output_review_v0_1"
        )
        is True
        and int(
            validator_hold_output_review.get("validator_outputs_reviewed_count", 0)
            or 0
        )
        == 5
        and int(validator_hold_output_review.get("validator_hold_count", 0) or 0)
        == 5
        and int(validator_hold_output_review.get("validator_pass_count", 0) or 0)
        == 0
        and int(validator_hold_output_review.get("builder_ready_count", 0) or 0)
        == 0
        and int(validator_hold_output_review.get("blockers_closed_by_review", 0) or 0)
        == 0
        and validator_hold_output_review.get("evidence_builder_execution_allowed")
        is False
        and int(validator_hold_output_review.get("boundary_violation_count", 0) or 0)
        == 0
    )
    validator_hold_output_review_all_passed = (
        validator_hold_output_review.get("status")
        == "validators_passed_evidence_builder_request_required"
        and validator_hold_output_review.get(
            "commercial_sprint_validator_hold_output_review_v0_1"
        )
        is True
        and int(
            validator_hold_output_review.get("validator_outputs_reviewed_count", 0)
            or 0
        )
        == 5
        and int(validator_hold_output_review.get("validator_hold_count", 0) or 0)
        == 0
        and int(validator_hold_output_review.get("validator_pass_count", 0) or 0)
        == 5
        and int(validator_hold_output_review.get("builder_ready_count", 0) or 0)
        == 5
        and int(validator_hold_output_review.get("blockers_closed_by_review", 0) or 0)
        == 0
        and validator_hold_output_review.get("evidence_builder_execution_allowed")
        is False
        and int(validator_hold_output_review.get("boundary_violation_count", 0) or 0)
        == 0
    )
    if boundary_violations:
        status = "stop_boundary_violation"
        next_stage = "boundary_review"
    elif validator_hold_output_review_all_passed:
        status = "ready_for_separate_evidence_builder_request"
        next_stage = "separate_evidence_builder_request"
    elif validator_hold_output_review_completed:
        status = "hold_validator_input_evidence_completion_required"
        next_stage = "validator_missing_input_completion"
    elif validator_execution_holds_completed:
        status = "hold_validator_outputs_review_required"
        next_stage = "validator_outputs_review"
    elif validator_approval_ready:
        status = "hold_validator_approval_required"
        next_stage = "human_validator_approval"
    elif (
        template_transfer_performed
        and post_transfer_validator_sequence.get("ready_for_validator_approval") is True
    ):
        status = "ready_for_separate_validator_approval"
        next_stage = "validator_approval_request"
    elif template_transfer_performed:
        status = "template_transfer_applied_pending_validator_approval"
        next_stage = "post_transfer_validator_sequence"
    elif template_transfer_execution_ready:
        status = "ready_for_template_transfer_execution"
        next_stage = "template_transfer_applier_execution"
    elif template_transfer_request_ready:
        status = "ready_for_separate_human_template_transfer_execution_request"
        next_stage = "human_template_transfer_execution_request"
    else:
        status = str(active_board.get("status", "hold_human_quick_fill_required"))
        next_stage = str(active_board.get("current_stage", "human_quick_fill"))
    full_quick_fill_missing = active_board.get(
        "full_quick_fill_missing_value_row_count",
        next_action.get("full_quick_fill_missing_value_row_count"),
    )
    if status == "ready_for_separate_evidence_builder_request":
        next_human_action = (
            "All five local input validators pass and no missing validator input "
            "remains. If you want to continue, create a separate explicit human "
            "approved evidence-builder execution request. Do not run evidence "
            "builders, close blockers, contact anyone, launch, or claim production "
            "readiness from this status snapshot."
        )
    elif status == "hold_validator_input_evidence_completion_required":
        next_human_action = (
            "Complete the missing metadata fields, evidence review items, and "
            "source notes listed in commercial_sprint_validator_hold_output_review.md. "
            "After those human-filled inputs are complete, rerun the local validators. "
            "Do not run evidence builders, close blockers, contact anyone, launch, "
            "or claim production readiness from this status snapshot."
        )
    elif status == "hold_validator_outputs_review_required":
        next_human_action = (
            "Review the completed local validator outputs. All five validators ran "
            "under explicit human authorization and all returned hold. Complete the "
            "missing input or boundary evidence for those hold outputs before any "
            "separate evidence-builder request. Do not close blockers, contact "
            "anyone, launch, or claim production readiness from this status snapshot."
        )
    elif status == "hold_validator_approval_required":
        next_human_action = (
            "Review the validator approval request packet and decide whether to "
            "approve the five local validators for a separate execution request. "
            "Do not run validators, collect evidence, execute evidence builders, "
            "close blockers, contact anyone, launch, or claim production readiness "
            "from this status snapshot."
        )
    elif status == "ready_for_separate_validator_approval":
        next_human_action = (
            "Generate and review the validator approval request packet. Template "
            "transfer has completed locally, but validator execution on real input "
            "still requires separate explicit human approval."
        )
    elif status == "template_transfer_applied_pending_validator_approval":
        next_human_action = (
            "Template transfer is complete. Generate the post-transfer validator "
            "sequence and approval request before running any validator separately."
        )
    elif status == "ready_for_template_transfer_execution":
        next_human_action = (
            "Run only the controlled local template transfer applier that was "
            "separately approved by the human review record. This may transfer "
            "the already imported workbook values into local human-filled "
            "templates, but it must not run validators on real input, collect "
            "evidence, close blockers, contact anyone, launch, or claim "
            "production readiness."
        )
    elif status == "ready_for_separate_human_template_transfer_execution_request":
        next_human_action = (
            "Review the template transfer execution request. The workbook import "
            "has already been applied by a prior explicitly authorized step, but "
            "template transfer, validator execution on real input, evidence "
            "collection, blocker closure, launch, and production-readiness claims "
            "still require separate explicit human approval."
        )
    elif status == "ready_for_human_workbook_import_approval":
        next_human_action = (
            "Review the workbook import approval request. Do not run workbook "
            "import, template transfer, validator execution on real input, "
            "evidence collection, or blocker closure unless a separate explicit "
            "human execution request exists."
        )
    else:
        next_human_action = (
            "Open the begin-here page, read the 10-row quality guide, confirm "
            "the blank template preflight, fill only the 10 preferred "
            "human_value_to_enter rows, check the post-fill readiness preview, "
            "read the post-fill validation runbook, run the post-fill quality "
            "lint wrapper, then run the local review-batch e2e dry run. Stop "
            "before workbook import, evidence collection, or blocker closure "
            "unless a separate human approval exists."
        )

    snapshot: dict[str, Any] = {
        "commercial_readiness_status_snapshot_v0_1": True,
        "snapshot_type": "local_default_commercial_readiness_status",
        "status": status,
        "commercial_status": commercial_status,
        "controlled_preview_status": go_no_go.get("controlled_preview_status"),
        "controlled_preview_preflight_status": go_no_go.get(
            "controlled_preview_preflight_status"
        ),
        "production_launch_status": production_launch_status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_readiness_status_snapshot.py",
        "source_settings": "load_settings_empty_default_no_external_evidence_paths",
        "source_go_no_go_json": rel(GO_NO_GO_JSON),
        "source_go_no_go_service": "saee_backend/services/commercial_go_no_go.py",
        "source_commercial_readiness_status_html": rel(STATUS_HTML),
        "local_static_commercial_readiness_status_html": True,
        "browser_readable_commercial_readiness_status": True,
        "source_active_human_input_board": rel(ACTIVE_BOARD_JSON),
        "source_next_action_summary": rel(NEXT_ACTION_JSON),
        "source_begin_here": rel(BEGIN_HERE_JSON),
        "source_workbook_import_approval_packet": rel(APPROVAL_JSON),
        "source_workbook_import_execution_applied": rel(WORKBOOK_IMPORT_APPLIED_JSON),
        "source_template_transfer_execution_request_packet": rel(
            TEMPLATE_TRANSFER_REQUEST_JSON
        ),
        "source_template_transfer_execution_approval": rel(
            TEMPLATE_TRANSFER_APPROVAL_JSON
        ),
        "source_template_transfer_applier": rel(TEMPLATE_TRANSFER_APPLIER_JSON),
        "source_post_transfer_validator_sequence": rel(
            POST_TRANSFER_VALIDATOR_SEQUENCE_JSON
        ),
        "source_validator_approval_request_packet": rel(VALIDATOR_APPROVAL_PACKET_JSON),
        "source_validator_execution_run": rel(VALIDATOR_EXECUTION_RUN_JSON),
        "source_validator_hold_output_review": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_JSON),
        "source_safety_preflight": rel(SAFETY_JSON),
        "source_import_dry_run": rel(IMPORT_DRY_RUN_JSON),
        "source_importer": rel(IMPORTER_JSON),
        "source_quick_fill_validation": rel(VALIDATION_JSON),
        "go_no_go_type": go_no_go.get("go_no_go_type"),
        "readiness_score": go_no_go.get("readiness_score"),
        "total_production_checks": go_no_go.get("total_production_checks"),
        "satisfied_production_checks": go_no_go.get("satisfied_production_checks"),
        "production_blocker_count": go_no_go.get("production_blocker_count"),
        "unsatisfied_blocker_count": len(go_no_go.get("unsatisfied_blockers", [])),
        "active_stage": next_stage,
        "active_board_status": active_board.get("status"),
        "next_action_summary_status": status,
        "begin_here_status": status,
        "preferred_human_input_path": (
            "separate_evidence_builder_request"
            if status == "ready_for_separate_evidence_builder_request"
            else "validator_missing_input_completion"
            if validator_hold_output_review_completed
            else "validator_hold_output_review"
            if validator_execution_holds_completed
            else "validator_approval_request"
            if validator_approval_ready
            else "validator_approval_request"
            if status == "ready_for_separate_validator_approval"
            else "post_transfer_validator_sequence"
            if status == "template_transfer_applied_pending_validator_approval"
            else "template_transfer_applier_execution"
            if template_transfer_execution_ready
            else "template_transfer_execution_request"
            if template_transfer_request_ready
            else next_action.get("preferred_human_input_path")
        ),
        "preferred_template_missing_value_row_count": (
            0
            if status == "ready_for_separate_evidence_builder_request"
            else next_action.get("preferred_template_missing_value_row_count")
        ),
        "full_quick_fill_missing_value_row_count": full_quick_fill_missing,
        "quality_guide_status": next_action.get("quality_guide_status"),
        "quality_guide_row_count": next_action.get("quality_guide_row_count"),
        "source_review_batch_quality_guide_html": next_action.get(
            "source_review_batch_quality_guide_html"
        ),
        "source_review_batch_template_preflight_markdown": next_action.get(
            "source_review_batch_template_preflight_markdown"
        ),
        "template_preflight_status": next_action.get("template_preflight_status"),
        "template_preflight_passed": next_action.get("template_preflight_passed") is True,
        "template_preflight_boundary_violation_count": int(
            next_action.get("template_preflight_boundary_violation_count", 0) or 0
        ),
        "source_post_fill_readiness_preview_html": next_action.get(
            "source_post_fill_readiness_preview_html"
        ),
        "post_fill_readiness_preview_status": next_action.get(
            "post_fill_readiness_preview_status"
        ),
        "post_fill_readiness_preview_ready": next_action.get(
            "post_fill_readiness_preview_ready"
        )
        is True,
        "post_fill_readiness_preview_missing_human_value_row_count": next_action.get(
            "post_fill_readiness_preview_missing_human_value_row_count"
        ),
        "source_post_fill_validation_runbook_html": next_action.get(
            "source_post_fill_validation_runbook_html"
        ),
        "post_fill_runbook_status": next_action.get("post_fill_runbook_status"),
        "post_fill_validation_ready": next_action.get("post_fill_validation_ready") is True,
        "post_fill_missing_human_value_row_count": next_action.get(
            "post_fill_missing_human_value_row_count"
        ),
        "source_post_fill_check_markdown": begin_here.get("source_post_fill_check_markdown"),
        "post_fill_quality_check_command": begin_here.get("post_fill_quality_check_command"),
        "post_fill_check_status": begin_here.get("post_fill_check_status"),
        "post_fill_quality_lint_enabled": begin_here.get("post_fill_quality_lint_enabled")
        is True,
        "post_fill_quality_lint_issue_count": int(
            begin_here.get("post_fill_quality_lint_issue_count", 0) or 0
        ),
        "post_fill_forbidden_claim_lint_passed": begin_here.get(
            "post_fill_forbidden_claim_lint_passed"
        )
        is True,
        "post_fill_shape_lint_passed": begin_here.get("post_fill_shape_lint_passed")
        is True,
        "post_fill_ready_for_quality_safe_dry_run": begin_here.get(
            "post_fill_ready_for_quality_safe_dry_run"
        )
        is True,
        "source_begin_here_html": begin_here.get("source_begin_here_html"),
        "begin_here_action_count": begin_here.get("begin_here_action_count"),
        "plain_language_human_route_enabled": begin_here.get(
            "plain_language_human_route_enabled"
        )
        is True,
        "plain_language_human_route_step_count": begin_here.get(
            "plain_language_human_route_step_count"
        ),
        "quick_fill_row_count": active_board.get("quick_fill_row_count"),
        "selected_blocker_count": active_board.get("selected_blocker_count"),
        "completed_value_row_count": active_board.get("completed_value_row_count"),
        "missing_value_row_count": active_board.get("missing_value_row_count"),
        "ready_for_human_fill": active_board.get("ready_for_human_fill") is True,
        "ready_for_safety_preflight": active_board.get("ready_for_safety_preflight")
        is True,
        "safe_to_import_after_human_approval": safety.get(
            "safe_to_import_after_human_approval"
        )
        is True,
        "ready_for_workbook_import": validation.get("ready_for_workbook_import")
        is True,
        "ready_for_workbook_import_approval": approval.get(
            "ready_for_workbook_import_approval"
        )
        is True,
        "source_workbook_import_execution_applied_status": workbook_import_applied.get(
            "status"
        ),
        "source_workbook_import_performed": workbook_import_applied.get(
            "workbook_import_performed"
        )
        is True,
        "source_workbook_written": workbook_import_applied.get("workbook_written") is True,
        "current_stage_import_completed": workbook_import_applied.get(
            "workbook_import_performed"
        )
        is True,
        "template_transfer_execution_request_status": template_transfer_request.get(
            "status"
        ),
        "ready_for_template_transfer_request": template_transfer_request.get(
            "ready_for_template_transfer_request"
        )
        is True,
        "ready_for_separate_human_template_transfer_execution_request": template_transfer_request.get(
            "ready_for_separate_human_template_transfer_execution_request"
        )
        is True,
        "ready_for_template_transfer_execution": template_transfer_request.get(
            "ready_for_template_transfer_execution"
        )
        is True,
        "separate_template_transfer_execution_request_required": template_transfer_request.get(
            "separate_template_transfer_execution_request_required"
        )
        is True
        and not template_transfer_execution_ready,
        "human_template_transfer_execution_request_recorded": template_transfer_approval.get(
            "human_execution_request_recorded"
        )
        is True,
        "human_template_transfer_execution_authorized": template_transfer_approval.get(
            "human_execution_authorized"
        )
        is True,
        "required_transfer_ready_count": template_transfer_request.get(
            "required_transfer_ready_count"
        ),
        "target_template_count": template_transfer_request.get("target_template_count"),
        "template_transfer_authorized": template_transfer_approval.get(
            "template_transfer_authorized"
        )
        is True,
        "template_transfer_applier_status": template_transfer_applier.get("status"),
        "template_transfer_performed": template_transfer_performed,
        "template_transfer_values_transferred": template_transfer_applier.get(
            "values_transferred"
        )
        is True,
        "template_transfer_human_filled_templates_written": template_transfer_applier.get(
            "human_filled_templates_written"
        )
        is True,
        "template_transfer_values_transferred_count": int(
            template_transfer_applier.get("values_transferred_count", 0) or 0
        ),
        "template_transfer_templates_written_count": int(
            template_transfer_applier.get("templates_written_count", 0) or 0
        ),
        "template_transfer_execution_allowed": False,
        "template_transfer_applier_execution_allowed": False,
        "post_transfer_validator_sequence_status": post_transfer_validator_sequence.get(
            "status"
        ),
        "validator_approval_request_status": validator_approval_packet.get("status"),
        "validator_execution_run_status": validator_execution_run.get("status"),
        "validator_hold_output_review_status": validator_hold_output_review.get("status"),
        "validator_hold_output_review_completed": validator_hold_output_review_completed,
        "validator_outputs_review_required": (
            validator_execution_holds_completed and not validator_hold_output_review_completed
        ),
        "validator_missing_input_completion_required": (
            validator_hold_output_review_completed
            and validator_hold_output_review.get("missing_input_completion_required")
            is True
        ),
        "rerun_validators_after_completion_required": (
            validator_hold_output_review.get(
                "rerun_validators_after_completion_required"
            )
            is True
        ),
        "total_missing_metadata_field_count": int(
            validator_hold_output_review.get("total_missing_metadata_field_count", 0)
            or 0
        ),
        "total_missing_evidence_item_count": int(
            validator_hold_output_review.get("total_missing_evidence_item_count", 0)
            or 0
        ),
        "total_missing_source_note_count": int(
            validator_hold_output_review.get("total_missing_source_note_count", 0)
            or 0
        ),
        "local_validators_run": validator_execution_completed,
        "validators_run_count": int(validator_execution_run.get("validators_run_count", 0) or 0),
        "validator_hold_count": int(validator_execution_run.get("validator_hold_count", 0) or 0),
        "validator_pass_count": int(validator_execution_run.get("validator_pass_count", 0) or 0),
        "validator_stop_count": int(validator_execution_run.get("validator_stop_count", 0) or 0),
        "builder_ready_count": int(validator_execution_run.get("builder_ready_count", 0) or 0),
        "blockers_closed_by_validator_run": int(validator_execution_run.get("blockers_closed_by_run", 0) or 0),
        "planned_validator_count": int(
            validator_approval_packet.get("planned_validator_count", 0) or 0
        ),
        "ready_validator_count": int(
            validator_approval_packet.get("ready_validator_count", 0) or 0
        ),
        "validator_approval_request_count": int(
            validator_approval_packet.get("approval_request_count", 0) or 0
        ),
        "approved_validator_count": int(
            validator_approval_packet.get("approved_validator_count", 0) or 0
        ),
        "validator_execution_authorized_count": int(
            validator_approval_packet.get("validator_execution_authorized_count", 0)
            or 0
        ),
        "ready_for_validator_approval": (
            validator_approval_packet.get("ready_for_validator_approval") is True
            and not validator_execution_completed
        ),
        "ready_for_validator_execution": False,
        "validators_run": validator_execution_completed,
        "separate_validator_execution_request_required": not validator_execution_completed,
        "separate_evidence_builder_request_required": (
            status == "ready_for_separate_evidence_builder_request"
        ),
        "approval_request_count": (
            int(validator_approval_packet.get("approval_request_count", 0) or 0)
            if validator_approval_ready
            else approval.get("approval_request_count", 0)
        ),
        "ready_import_approval_count": approval.get("ready_import_approval_count", 0),
        "source_statuses": {
            "active_board": missing_source_status(ACTIVE_BOARD_JSON),
            "next_action_summary": missing_source_status(NEXT_ACTION_JSON),
            "begin_here": missing_source_status(BEGIN_HERE_JSON),
            "workbook_import_approval_packet": missing_source_status(APPROVAL_JSON),
            "workbook_import_execution_applied": missing_source_status(
                WORKBOOK_IMPORT_APPLIED_JSON
            ),
            "template_transfer_execution_request_packet": missing_source_status(
                TEMPLATE_TRANSFER_REQUEST_JSON
            ),
            "template_transfer_execution_approval": missing_source_status(
                TEMPLATE_TRANSFER_APPROVAL_JSON
            ),
            "template_transfer_applier": missing_source_status(
                TEMPLATE_TRANSFER_APPLIER_JSON
            ),
            "post_transfer_validator_sequence": missing_source_status(
                POST_TRANSFER_VALIDATOR_SEQUENCE_JSON
            ),
            "validator_approval_request_packet": missing_source_status(
                VALIDATOR_APPROVAL_PACKET_JSON
            ),
            "validator_execution_run": missing_source_status(VALIDATOR_EXECUTION_RUN_JSON),
            "validator_hold_output_review": missing_source_status(
                VALIDATOR_HOLD_OUTPUT_REVIEW_JSON
            ),
            "safety_preflight": missing_source_status(SAFETY_JSON),
            "import_dry_run": missing_source_status(IMPORT_DRY_RUN_JSON),
            "importer": missing_source_status(IMPORTER_JSON),
            "quick_fill_validation": missing_source_status(VALIDATION_JSON),
        },
        "top_unsatisfied_blockers": [
            item.get("blocker_id")
            for item in go_no_go.get("unsatisfied_blockers", [])[:10]
        ],
        "active_quick_fill_blockers": [
            {
                "blocker_id": row.get("blocker_id"),
                "quick_fill_row_count": row.get("quick_fill_row_count"),
                "missing_value_row_count": row.get("missing_value_row_count"),
                "status": row.get("status"),
            }
            for row in active_board.get("board_rows", [])
        ],
        "human_input_required": True,
        "human_review_required": True,
        "separate_workbook_import_execution_request_required": True,
        "separate_template_transfer_execution_request_required": False,
        "next_human_action": next_human_action,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
    }
    for flag in FALSE_FLAGS:
        snapshot[flag] = False
    snapshot["template_transfer_performed"] = template_transfer_performed
    snapshot["validators_run_on_real_input"] = validator_execution_completed
    snapshot["validator_execution_authorized"] = validator_execution_completed
    snapshot["human_validator_execution_authorized"] = validator_execution_completed
    snapshot["template_transfer_values_transferred"] = template_transfer_applier.get(
        "values_transferred"
    ) is True
    snapshot["template_transfer_human_filled_templates_written"] = (
        template_transfer_applier.get("human_filled_templates_written") is True
    )

    go_no_go_payload = dict(go_no_go)
    go_no_go_payload["generated_by"] = "scripts/saee_commercial_readiness_status_snapshot.py"
    go_no_go_payload["source_settings"] = "load_settings_empty_default_no_external_evidence_paths"
    return go_no_go_payload, snapshot


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def status_lines(snapshot: dict[str, Any]) -> list[str]:
    return [
        "commercial_readiness_status_snapshot_v0_1: true",
        f"status: {snapshot['status']}",
        f"commercial_status: {snapshot['commercial_status']}",
        f"controlled_preview_status: {snapshot['controlled_preview_status']}",
        f"production_launch_status: {snapshot['production_launch_status']}",
        f"readiness_score: {snapshot['readiness_score']}",
        f"total_production_checks: {snapshot['total_production_checks']}",
        f"satisfied_production_checks: {snapshot['satisfied_production_checks']}",
        f"production_blocker_count: {snapshot['production_blocker_count']}",
        f"active_stage: {snapshot['active_stage']}",
        f"next_action_summary_status: {snapshot['next_action_summary_status']}",
        f"begin_here_status: {snapshot['begin_here_status']}",
        f"preferred_human_input_path: {snapshot['preferred_human_input_path']}",
        f"preferred_template_missing_value_row_count: {snapshot['preferred_template_missing_value_row_count']}",
        f"full_quick_fill_missing_value_row_count: {snapshot['full_quick_fill_missing_value_row_count']}",
        f"quality_guide_status: {snapshot['quality_guide_status']}",
        f"quality_guide_row_count: {snapshot['quality_guide_row_count']}",
        f"source_review_batch_quality_guide_html: {snapshot['source_review_batch_quality_guide_html']}",
        f"source_review_batch_template_preflight_markdown: {snapshot['source_review_batch_template_preflight_markdown']}",
        f"template_preflight_status: {snapshot['template_preflight_status']}",
        f"template_preflight_passed: {str(snapshot['template_preflight_passed']).lower()}",
        f"template_preflight_boundary_violation_count: {snapshot['template_preflight_boundary_violation_count']}",
        f"source_post_fill_readiness_preview_html: {snapshot['source_post_fill_readiness_preview_html']}",
        f"post_fill_readiness_preview_status: {snapshot['post_fill_readiness_preview_status']}",
        f"post_fill_readiness_preview_ready: {str(snapshot['post_fill_readiness_preview_ready']).lower()}",
        f"post_fill_readiness_preview_missing_human_value_row_count: {snapshot['post_fill_readiness_preview_missing_human_value_row_count']}",
        f"source_post_fill_validation_runbook_html: {snapshot['source_post_fill_validation_runbook_html']}",
        f"post_fill_runbook_status: {snapshot['post_fill_runbook_status']}",
        f"post_fill_validation_ready: {str(snapshot['post_fill_validation_ready']).lower()}",
        f"post_fill_missing_human_value_row_count: {snapshot['post_fill_missing_human_value_row_count']}",
        f"source_post_fill_check_markdown: {snapshot['source_post_fill_check_markdown']}",
        f"post_fill_quality_check_command: {snapshot['post_fill_quality_check_command']}",
        f"post_fill_check_status: {snapshot['post_fill_check_status']}",
        f"post_fill_quality_lint_enabled: {str(snapshot['post_fill_quality_lint_enabled']).lower()}",
        f"post_fill_quality_lint_issue_count: {snapshot['post_fill_quality_lint_issue_count']}",
        f"post_fill_forbidden_claim_lint_passed: {str(snapshot['post_fill_forbidden_claim_lint_passed']).lower()}",
        f"post_fill_shape_lint_passed: {str(snapshot['post_fill_shape_lint_passed']).lower()}",
        f"post_fill_ready_for_quality_safe_dry_run: {str(snapshot['post_fill_ready_for_quality_safe_dry_run']).lower()}",
        f"source_begin_here_html: {snapshot['source_begin_here_html']}",
        f"begin_here_action_count: {snapshot['begin_here_action_count']}",
        f"plain_language_human_route_enabled: {str(snapshot['plain_language_human_route_enabled']).lower()}",
        f"plain_language_human_route_step_count: {snapshot['plain_language_human_route_step_count']}",
        f"quick_fill_row_count: {snapshot['quick_fill_row_count']}",
        f"selected_blocker_count: {snapshot['selected_blocker_count']}",
        f"completed_value_row_count: {snapshot['completed_value_row_count']}",
        f"missing_value_row_count: {snapshot['missing_value_row_count']}",
        f"ready_for_human_fill: {str(snapshot['ready_for_human_fill']).lower()}",
        f"ready_for_safety_preflight: {str(snapshot['ready_for_safety_preflight']).lower()}",
        f"safe_to_import_after_human_approval: {str(snapshot['safe_to_import_after_human_approval']).lower()}",
        f"ready_for_workbook_import: {str(snapshot['ready_for_workbook_import']).lower()}",
        f"ready_for_workbook_import_approval: {str(snapshot['ready_for_workbook_import_approval']).lower()}",
        f"source_workbook_import_execution_applied_status: {snapshot['source_workbook_import_execution_applied_status']}",
        f"source_workbook_import_performed: {str(snapshot['source_workbook_import_performed']).lower()}",
        f"source_workbook_written: {str(snapshot['source_workbook_written']).lower()}",
        f"current_stage_import_completed: {str(snapshot['current_stage_import_completed']).lower()}",
        f"template_transfer_execution_request_status: {snapshot['template_transfer_execution_request_status']}",
        f"ready_for_template_transfer_request: {str(snapshot['ready_for_template_transfer_request']).lower()}",
        f"ready_for_separate_human_template_transfer_execution_request: {str(snapshot['ready_for_separate_human_template_transfer_execution_request']).lower()}",
        f"ready_for_template_transfer_execution: {str(snapshot['ready_for_template_transfer_execution']).lower()}",
        f"separate_template_transfer_execution_request_required: {str(snapshot['separate_template_transfer_execution_request_required']).lower()}",
        f"human_template_transfer_execution_request_recorded: {str(snapshot['human_template_transfer_execution_request_recorded']).lower()}",
        f"human_template_transfer_execution_authorized: {str(snapshot['human_template_transfer_execution_authorized']).lower()}",
        f"required_transfer_ready_count: {snapshot['required_transfer_ready_count']}",
        f"target_template_count: {snapshot['target_template_count']}",
        f"template_transfer_applier_status: {snapshot['template_transfer_applier_status']}",
        f"template_transfer_performed: {str(snapshot['template_transfer_performed']).lower()}",
        f"template_transfer_values_transferred: {str(snapshot['template_transfer_values_transferred']).lower()}",
        f"template_transfer_human_filled_templates_written: {str(snapshot['template_transfer_human_filled_templates_written']).lower()}",
        f"template_transfer_values_transferred_count: {snapshot['template_transfer_values_transferred_count']}",
        f"template_transfer_templates_written_count: {snapshot['template_transfer_templates_written_count']}",
        f"post_transfer_validator_sequence_status: {snapshot['post_transfer_validator_sequence_status']}",
        f"validator_approval_request_status: {snapshot['validator_approval_request_status']}",
        f"validator_execution_run_status: {snapshot['validator_execution_run_status']}",
        f"validator_hold_output_review_status: {snapshot['validator_hold_output_review_status']}",
        f"validator_hold_output_review_completed: {str(snapshot['validator_hold_output_review_completed']).lower()}",
        f"validator_outputs_review_required: {str(snapshot['validator_outputs_review_required']).lower()}",
        f"validator_missing_input_completion_required: {str(snapshot['validator_missing_input_completion_required']).lower()}",
        f"rerun_validators_after_completion_required: {str(snapshot['rerun_validators_after_completion_required']).lower()}",
        f"total_missing_metadata_field_count: {snapshot['total_missing_metadata_field_count']}",
        f"total_missing_evidence_item_count: {snapshot['total_missing_evidence_item_count']}",
        f"total_missing_source_note_count: {snapshot['total_missing_source_note_count']}",
        f"local_validators_run: {str(snapshot['local_validators_run']).lower()}",
        f"validators_run_count: {snapshot['validators_run_count']}",
        f"validator_hold_count: {snapshot['validator_hold_count']}",
        f"validator_pass_count: {snapshot['validator_pass_count']}",
        f"validator_stop_count: {snapshot['validator_stop_count']}",
        f"builder_ready_count: {snapshot['builder_ready_count']}",
        f"blockers_closed_by_validator_run: {snapshot['blockers_closed_by_validator_run']}",
        f"planned_validator_count: {snapshot['planned_validator_count']}",
        f"ready_validator_count: {snapshot['ready_validator_count']}",
        f"validator_approval_request_count: {snapshot['validator_approval_request_count']}",
        f"approved_validator_count: {snapshot['approved_validator_count']}",
        f"validator_execution_authorized_count: {snapshot['validator_execution_authorized_count']}",
        f"ready_for_validator_approval: {str(snapshot['ready_for_validator_approval']).lower()}",
        f"ready_for_validator_execution: {str(snapshot['ready_for_validator_execution']).lower()}",
        f"validators_run: {str(snapshot['validators_run']).lower()}",
        f"separate_validator_execution_request_required: {str(snapshot['separate_validator_execution_request_required']).lower()}",
        f"separate_evidence_builder_request_required: {str(snapshot['separate_evidence_builder_request_required']).lower()}",
        f"approval_request_count: {snapshot['approval_request_count']}",
        f"ready_import_approval_count: {snapshot['ready_import_approval_count']}",
        "human_input_required: true",
        "human_review_required: true",
        "separate_workbook_import_execution_request_required: true",
        f"template_transfer_authorized: {str(snapshot['template_transfer_authorized']).lower()}",
        f"template_transfer_execution_allowed: {str(snapshot['template_transfer_execution_allowed']).lower()}",
        f"template_transfer_applier_execution_allowed: {str(snapshot['template_transfer_applier_execution_allowed']).lower()}",
        f"boundary_violation_count: {snapshot['boundary_violation_count']}",
        "workbook_import_authorized: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "values_transferred: false",
        f"validators_run_on_real_input: {str(snapshot['validators_run_on_real_input']).lower()}",
        "real_evidence_created: false",
        "evidence_collection_authorized: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]


def blocker_table(snapshot: dict[str, Any]) -> str:
    rows = [
        "| Blocker | Quick-fill rows | Missing values | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in snapshot["active_quick_fill_blockers"]:
        rows.append(
            "| {blocker_id} | {quick_fill_row_count} | {missing_value_row_count} | {status} |".format(
                **row
            )
        )
    return "\n".join(rows)


def write_csv(path: Path, snapshot: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "quick_fill_row_count",
        "missing_value_row_count",
        "status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in snapshot["active_quick_fill_blockers"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(path: Path, snapshot: dict[str, Any], title: str) -> None:
    path.write_text(
        f"""# {title}

{chr(10).join(status_lines(snapshot))}

## Purpose

This snapshot gives external coding and retrieval agents one file-backed place
to answer: is SAEE commercially ready now?

Current answer: no. SAEE remains in commercial hold because the default local
go/no-go has 24 unsatisfied production checks. The workbook import and template
transfer were applied by prior explicitly authorized local steps. The local
validator execution run has completed and all five validator outputs remain
hold. The validator hold-output review has identified the missing input
evidence now blocking progress. The current preferred path is only completion
of those missing metadata fields, evidence review items, and source notes,
followed by a local validator rerun. No evidence builder execution, blocker
closure, launch, or production-readiness claim is authorized by this snapshot.

## Active Human Input Blockers

{blocker_table(snapshot)}

## Current Human Review Path

- Begin here: `{snapshot['source_begin_here_html']}`
- Preferred path: `{snapshot['preferred_human_input_path']}`
- Workbook import applied record: `{snapshot['source_workbook_import_execution_applied']}`
- Template transfer request packet: `{snapshot['source_template_transfer_execution_request_packet']}`
- Template transfer approval record: `{snapshot['source_template_transfer_execution_approval']}`
- Validator execution run: `{snapshot['source_validator_execution_run']}`
- Validator hold output review: `{snapshot['source_validator_hold_output_review']}`
- Quality guide: `{snapshot['source_review_batch_quality_guide_html']}`
- Blank template preflight: `{snapshot['source_review_batch_template_preflight_markdown']}`
- Post-fill readiness preview: `{snapshot['source_post_fill_readiness_preview_html']}`
- Post-fill validation runbook: `{snapshot['source_post_fill_validation_runbook_html']}`
- preferred_template_missing_value_row_count: {snapshot['preferred_template_missing_value_row_count']}
- full_quick_fill_missing_value_row_count: {snapshot['full_quick_fill_missing_value_row_count']}
- template_preflight_passed: {str(snapshot['template_preflight_passed']).lower()}
- post_fill_readiness_preview_ready: {str(snapshot['post_fill_readiness_preview_ready']).lower()}
- post_fill_validation_ready: {str(snapshot['post_fill_validation_ready']).lower()}
- validator_hold_output_review_completed: {str(snapshot['validator_hold_output_review_completed']).lower()}
- validator_missing_input_completion_required: {str(snapshot['validator_missing_input_completion_required']).lower()}
- total_missing_metadata_field_count: {snapshot['total_missing_metadata_field_count']}
- total_missing_evidence_item_count: {snapshot['total_missing_evidence_item_count']}
- total_missing_source_note_count: {snapshot['total_missing_source_note_count']}

## Next Human Action

{snapshot['next_human_action']}

## Browser-Readable Status

- HTML status page: `{snapshot['source_commercial_readiness_status_html']}`
- local_static_commercial_readiness_status_html: true
- browser_readable_commercial_readiness_status: true

## Boundary

This snapshot did not enter human values, import a workbook, transfer templates,
collect evidence, close blockers, contact customers or vendors, launch product,
release an SDK, expose private core, or claim production readiness. It only
records that the previously authorized local validator run completed with hold
outputs and that the next local action is human review of those hold outputs.
""",
        encoding="utf-8",
    )


def write_html(path: Path, snapshot: dict[str, Any]) -> None:
    blocker_cards = "\n".join(
        f"""
          <article class="blocker-card">
            <strong>{row.get('blocker_id')}</strong>
            <span>{row.get('missing_value_row_count')} 个值待人工填写</span>
            <small>{row.get('status')}</small>
          </article>
        """
        for row in snapshot["active_quick_fill_blockers"]
    )
    path.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 商用状态总览</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f5f3ee;
        --surface: #ffffff;
        --soft: #ece9e2;
        --text: #11110f;
        --muted: #62645f;
        --line: #ddd7cc;
        --accent: #10a37f;
        --accent-soft: #e7f4ef;
        --warn: #8a5a12;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(112deg, #ffffff 0%, var(--bg) 58%, #e8f2ed 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.65;
      }}
      main {{
        width: min(1120px, calc(100% - 32px));
        margin: 0 auto;
        padding: 56px 0;
      }}
      .hero {{
        display: grid;
        gap: 22px;
        padding: clamp(28px, 5vw, 56px);
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.86);
      }}
      .kicker {{
        margin: 0;
        color: var(--accent);
        font-size: 14px;
        font-weight: 800;
      }}
      h1 {{
        margin: 0;
        max-width: 780px;
        font-size: clamp(34px, 5vw, 64px);
        line-height: 1.05;
        letter-spacing: 0;
      }}
      .lead {{
        max-width: 760px;
        margin: 0;
        color: var(--muted);
        font-size: 19px;
      }}
      .status-pill {{
        width: fit-content;
        padding: 8px 12px;
        border-radius: 999px;
        color: var(--warn);
        background: #f8efe0;
        font-weight: 800;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin-top: 24px;
      }}
      .metric, .panel, .blocker-card {{
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
      }}
      .metric {{
        min-height: 124px;
        padding: 18px;
      }}
      .metric strong {{
        display: block;
        font-size: 32px;
        line-height: 1;
      }}
      .metric span {{
        display: block;
        margin-top: 10px;
        color: var(--muted);
        font-size: 14px;
      }}
      .sections {{
        display: grid;
        grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
        gap: 18px;
        margin-top: 18px;
      }}
      .panel {{
        padding: 24px;
      }}
      h2 {{
        margin: 0 0 12px;
        font-size: 26px;
        line-height: 1.15;
      }}
      ul, ol {{
        padding-left: 22px;
        margin: 12px 0 0;
        color: var(--muted);
      }}
      li + li {{ margin-top: 8px; }}
      .blocker-list {{
        display: grid;
        gap: 10px;
        margin-top: 14px;
      }}
      .blocker-card {{
        padding: 14px;
      }}
      .blocker-card strong,
      .blocker-card span,
      .blocker-card small {{
        display: block;
      }}
      .blocker-card span {{
        margin-top: 4px;
        color: var(--muted);
      }}
      .blocker-card small {{
        margin-top: 4px;
        color: var(--accent);
        font-weight: 700;
      }}
      .next {{
        background: var(--accent-soft);
      }}
      footer {{
        margin-top: 22px;
        color: var(--muted);
        font-size: 13px;
      }}
      @media (max-width: 820px) {{
        .grid, .sections {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p class="kicker">SAEE 商用状态总览</p>
        <h1>现在还不能正式商用。</h1>
        <p class="lead">
          这个页面只回答一个问题：SAEE 现在能不能作为正式商用产品发布？
          当前答案是不能。原因是还有生产级证据没有补齐；下一步只允许执行受控的本地模板转写。
        </p>
        <span class="status-pill">当前状态：{snapshot['commercial_status']} / {snapshot['production_launch_status']}</span>
      </section>

      <section class="grid" aria-label="核心状态">
        <div class="metric">
          <strong>{snapshot['production_blocker_count']}</strong>
          <span>个生产阻塞项仍未关闭</span>
        </div>
        <div class="metric">
          <strong>{snapshot['preferred_template_missing_value_row_count']}</strong>
          <span>行优先人工填写，完整缺口为 {snapshot['full_quick_fill_missing_value_row_count']} 行</span>
        </div>
        <div class="metric">
          <strong>{snapshot['satisfied_production_checks']}</strong>
          <span>个生产检查已满足</span>
        </div>
        <div class="metric">
          <strong>否</strong>
          <span>未发布、未客户验证、未生产可用</span>
        </div>
      </section>

      <section class="sections">
        <article class="panel next">
          <h2>下一步执行受控模板转写</h2>
          <p>{snapshot['next_human_action']}</p>
          <ol>
            <li>打开已获人工批准的 template transfer execution request。</li>
            <li>确认 workbook import 已由前一步授权执行并留下记录。</li>
            <li>只运行受控本地模板转写工具，把本地 workbook 值写入目标模板。</li>
            <li>不运行真实验证器，不采集证据，不关闭 blocker，不声明生产可用。</li>
          </ol>
        </article>

        <article class="panel">
          <h2>不能声称什么</h2>
          <ul>
            <li>不能声称生产可用。</li>
            <li>不能声称已经客户验证。</li>
            <li>不能声称已经发布产品。</li>
            <li>不能声称已经授权证据收集或执行。</li>
            <li>不能暴露私有核心、运行时、内核或接口结构。</li>
          </ul>
        </article>
      </section>

      <section class="panel" style="margin-top: 18px;">
        <h2>当前优先处理的阻塞项</h2>
        <div class="blocker-list">
{blocker_cards}
        </div>
      </section>

      <footer>
        本页为本地静态 HTML 状态页；不调用后端，不联系客户，不执行外部请求，不修改 SAEE 核心。
      </footer>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_gate(path: Path, snapshot: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Readiness Status Snapshot Recommendation Gate

answer: conditional
recommend_for_commercial_status_lookup: true
recommend_for_formal_launch_decision: false
recommend_for_evidence_collection: false
recommend_for_workbook_import_execution: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

{chr(10).join(status_lines(snapshot))}

Reason: this snapshot is recommendable as a local status surface only. It makes
the current commercial hold state easier for agents to find, but it does not
authorize launch, workbook import, evidence collection, blocker closure, or any
production readiness claim.
""",
        encoding="utf-8",
    )


def main() -> None:
    go_no_go, snapshot = build_snapshot()
    write_json(GO_NO_GO_JSON, go_no_go)
    write_json(STATUS_JSON, snapshot)
    write_csv(STATUS_CSV, snapshot)
    write_markdown(STATUS_MD, snapshot, "SAEE Commercial Readiness Status Snapshot v0.1")
    write_markdown(BOUNDARY_MD, snapshot, "SAEE Commercial Readiness Status Snapshot Boundary Audit")
    write_markdown(TOP_DOC, snapshot, "SAEE Commercial Readiness Status Snapshot v0.1")
    write_html(STATUS_HTML, snapshot)
    write_gate(GATE, snapshot)
    print(
        "SAEE_COMMERCIAL_READINESS_STATUS_SNAPSHOT: PASS "
        f"status={snapshot['status']} "
        f"production_blocker_count={snapshot['production_blocker_count']} "
        f"missing_value_row_count={snapshot['missing_value_row_count']} "
        "production_ready=false product_launched=false"
    )


if __name__ == "__main__":
    main()
