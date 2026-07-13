#!/usr/bin/env python3
"""Generate the commercial-readiness begin-here entrypoint.

This entrypoint is a read-only navigation layer over existing commercial
readiness artifacts. It does not generate values, fill human inputs, apply
local output, import workbooks, run validators on real input, collect evidence,
close blockers, contact customers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import csv
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "commercial_readiness_begin_here"
SUMMARY_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_action_summary/commercial_next_action_summary.local.json"
)
PROMPT_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_action_summary/commercial_next_human_input_prompt.local.json"
)
FILL_CARD_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.local.json"
)
FILL_CARD_CSV = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.csv"
)
QUALITY_GUIDE_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_review_batch_human_entry_quality_guide.local.json"
)
TEMPLATE_PREFLIGHT_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_review_batch_template_preflight.local.json"
)
VALIDATION_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_review_batch_validation.local.json"
)
POST_FILL_RUNBOOK_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_review_batch_post_fill_validation_runbook.local.json"
)
POST_FILL_CHECK_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/commercial_review_batch_post_fill_check.local.json"
)
SAFE_PREFILL_AUDIT_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_review_batch_safe_prefill_audit.local.json"
)
CLOSURE_BOARD_JSON = (
    COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json"
)
WORKBOOK_IMPORT_APPROVAL_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_approval_request_packet.local.json"
)
WORKBOOK_IMPORT_APPROVAL_MD = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_approval_request_packet.md"
)
WORKBOOK_IMPORT_APPROVAL_CSV = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_approval_request_packet.csv"
)
WORKBOOK_IMPORT_APPROVAL_AUDIT = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_approval_request_packet_boundary_audit.md"
)
WORKBOOK_IMPORT_APPLIED_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_execution_applied.local.json"
)
WORKBOOK_IMPORT_APPLIED_MD = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_execution_applied.md"
)
WORKBOOK_IMPORT_APPLIED_AUDIT = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_workbook_import_execution_applied_boundary_audit.md"
)
TEMPLATE_TRANSFER_REQUEST_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_template_transfer_execution_request_packet.local.json"
)
TEMPLATE_TRANSFER_REQUEST_MD = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_template_transfer_execution_request_packet.md"
)
TEMPLATE_TRANSFER_REQUEST_CSV = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_template_transfer_execution_request_packet.csv"
)
TEMPLATE_TRANSFER_REQUEST_AUDIT = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_template_transfer_execution_request_packet_boundary_audit.md"
)
VALIDATOR_APPROVAL_PACKET_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_approval_request_packet.local.json"
)
VALIDATOR_APPROVAL_PACKET_MD = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_approval_request_packet.md"
)
VALIDATOR_APPROVAL_PACKET_CSV = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_approval_request_packet.csv"
)
VALIDATOR_APPROVAL_PACKET_AUDIT = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_approval_request_packet_boundary_audit.md"
)
VALIDATOR_HOLD_OUTPUT_REVIEW_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_hold_output_review.local.json"
)
VALIDATOR_HOLD_OUTPUT_REVIEW_MD = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_hold_output_review.md"
)
VALIDATOR_HOLD_OUTPUT_REVIEW_CSV = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_hold_output_review.csv"
)
VALIDATOR_HOLD_OUTPUT_REVIEW_AUDIT = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/"
    "commercial_sprint_validator_hold_output_review_boundary_audit.md"
)

OUT_JSON = OUT_DIR / "commercial_readiness_begin_here.local.json"
OUT_MD = OUT_DIR / "commercial_readiness_begin_here.md"
OUT_CSV = OUT_DIR / "commercial_readiness_begin_here.csv"
OUT_HTML = OUT_DIR / "commercial_readiness_begin_here.html"
OUT_AUDIT = OUT_DIR / "commercial_readiness_begin_here_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_READINESS_BEGIN_HERE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_BEGIN_HERE_RECOMMENDATION_GATE.md"

FALSE_FLAGS = [
    "raw_values_recorded",
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "source_quick_fill_packet_modified",
    "batch_values_applied_to_source",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "evidence_collection_authorized",
    "execution_authorized",
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
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_row_preview(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "card_row_number": int(row["card_row_number"]),
                    "review_batch_row_id": row["review_batch_row_id"],
                    "input_key": row["input_key"],
                    "human_plain_label": row["human_plain_label"],
                    "human_plain_instruction": row["human_plain_instruction"],
                    "human_plain_leave_blank_condition": row[
                        "human_plain_leave_blank_condition"
                    ],
                    "target_json_pointer": row["target_json_pointer"],
                    "codex_may_fill": False,
                }
            )
    return rows


def build_payload() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON)
    prompt = load_json(PROMPT_JSON)
    fill_card = load_json(FILL_CARD_JSON)
    quality_guide = load_json(QUALITY_GUIDE_JSON)
    template_preflight = load_json(TEMPLATE_PREFLIGHT_JSON)
    validation = load_json(VALIDATION_JSON)
    post_fill_runbook = load_json(POST_FILL_RUNBOOK_JSON)
    post_fill_check = load_json(POST_FILL_CHECK_JSON)
    safe_prefill_audit = load_json(SAFE_PREFILL_AUDIT_JSON)
    closure_board = load_json(CLOSURE_BOARD_JSON)
    approval_packet = load_json(WORKBOOK_IMPORT_APPROVAL_JSON)
    workbook_import_applied = load_json(WORKBOOK_IMPORT_APPLIED_JSON)
    template_transfer_request = load_json(TEMPLATE_TRANSFER_REQUEST_JSON)
    validator_approval_packet = load_json(VALIDATOR_APPROVAL_PACKET_JSON)
    row_preview = load_row_preview(FILL_CARD_CSV)

    quality_guide_html = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/"
        "commercial_review_batch_human_entry_quality_guide.html"
    )
    fill_card_html = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.html"
    )
    template_preflight_md = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/commercial_review_batch_template_preflight.md"
    )
    post_fill_runbook_html = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/commercial_review_batch_post_fill_validation_runbook.html"
    )
    post_fill_check_md = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/commercial_review_batch_post_fill_check.md"
    )
    post_fill_check_command = "python3 scripts/saee_commercial_review_batch_post_fill_check.py"
    safe_prefill_audit_md = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/commercial_review_batch_safe_prefill_audit.md"
    )
    safe_prefill_audit_gate = (
        ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_RECOMMENDATION_GATE.md"
    )
    input_template_csv = (
        COMMERCIAL_DIR
        / "commercial_next_evidence_sprint/"
        "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
    )
    dry_run_script = (
        ROOT
        / "scripts/"
        "saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
    )
    closure_board_html = (
        COMMERCIAL_DIR
        / "commercial_blocker_closure_readiness_board/closure_readiness_board.html"
    )
    dry_run_command = (
        fill_card.get("post_fill_dry_run_command")
        or "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
    )

    actions = [
        {
            "step_id": "BEGIN-TTA-001",
            "title": "执行受控模板转写",
            "path": rel(TEMPLATE_TRANSFER_REQUEST_MD),
            "command": "",
            "human_action_required": True,
            "codex_execution_allowed": False,
        },
        {
            "step_id": "BEGIN-TTE-002",
            "title": "确认 64 条值已导入本地 workbook",
            "path": rel(WORKBOOK_IMPORT_APPLIED_MD),
            "command": "",
            "human_action_required": True,
            "codex_execution_allowed": False,
        },
        {
            "step_id": "BEGIN-TTA-003",
            "title": "确认转写后停止，不运行验证",
            "path": rel(TEMPLATE_TRANSFER_REQUEST_AUDIT),
            "command": "",
            "human_action_required": True,
            "codex_execution_allowed": False,
        },
        {
            "step_id": "BEGIN-TTA-004",
            "title": "只把模板转写作为下一步，不关闭事项",
            "path": rel(closure_board_html),
            "command": "",
            "human_action_required": True,
            "codex_execution_allowed": False,
        },
        {
            "step_id": "BEGIN-TTA-005",
            "title": "转写完成后停止，后续另行批准",
            "path": rel(SUMMARY_JSON),
            "command": "",
            "human_action_required": True,
            "codex_execution_allowed": False,
        },
        {
            "step_id": "BEGIN-TTE-006",
            "title": "保留工作簿导入审批和旧 10 行材料为只读历史参考",
            "path": rel(fill_card_html),
            "command": "",
            "human_action_required": True,
            "codex_execution_allowed": False,
        },
    ]
    if summary.get("status") == "ready_for_separate_evidence_builder_request":
        actions = [
            {
                "step_id": "BEGIN-EBR-001",
                "title": "确认 5 个 validator 已全部通过",
                "path": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_MD),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-EBR-002",
                "title": "如需继续，单独创建 evidence builder 执行请求",
                "path": rel(SUMMARY_JSON),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-EBR-003",
                "title": "不要从本页运行 evidence builder 或关闭 blocker",
                "path": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_AUDIT),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-EBR-004",
                "title": "继续保持不联系客户、不发布、不声称生产可用",
                "path": rel(closure_board_html),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
        ]
    elif summary.get("status") == "hold_validator_input_evidence_completion_required":
        actions = [
            {
                "step_id": "BEGIN-VIC-001",
                "title": "打开 validator hold 输出审查表",
                "path": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_MD),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VIC-002",
                "title": "补齐缺失的 metadata、evidence 和 source notes",
                "path": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_CSV),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VIC-003",
                "title": "补齐后重新运行本地 validators",
                "path": rel(SUMMARY_JSON),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VIC-004",
                "title": "仍然停止在 evidence builder 和 blocker closure 之前",
                "path": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_AUDIT),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
        ]
    elif summary.get("status") == "hold_validator_outputs_review_required":
        actions = [
            {
                "step_id": "BEGIN-VOR-001",
                "title": "审查 5 个 validator hold 输出",
                "path": rel(SUMMARY_JSON),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VOR-002",
                "title": "确认每个 hold 缺少什么证据",
                "path": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VOR-003",
                "title": "如需继续，另行创建 evidence builder 请求",
                "path": rel(SUMMARY_JSON),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VOR-004",
                "title": "保持证据收集和 blocker closure 暂停",
                "path": rel(closure_board_html),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
        ]
    elif summary.get("status") == "hold_validator_approval_required":
        actions = [
            {
                "step_id": "BEGIN-VAR-001",
                "title": "审查 5 个 validator 执行请求",
                "path": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VAR-002",
                "title": "确认 validator 仍未授权执行",
                "path": rel(VALIDATOR_APPROVAL_PACKET_AUDIT),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VAR-003",
                "title": "如需执行，另行创建 validator 执行请求",
                "path": rel(VALIDATOR_APPROVAL_PACKET_MD),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
            {
                "step_id": "BEGIN-VAR-004",
                "title": "保持证据收集和 blocker closure 暂停",
                "path": rel(closure_board_html),
                "command": "",
                "human_action_required": True,
                "codex_execution_allowed": False,
            },
        ]

    payload: dict[str, Any] = {
        "commercial_readiness_begin_here_v0_1": True,
        "entrypoint_type": "commercial_readiness_begin_here",
        "entrypoint_scope": "single_page_current_commercial_hold_next_human_action_no_execution",
        "status": summary.get("status", "hold_validator_approval_required"),
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_readiness_begin_here.py",
        "make_target": "make check-commercial-readiness-begin-here",
        "source_summary_json": rel(SUMMARY_JSON),
        "source_prompt_json": rel(PROMPT_JSON),
        "source_fill_card_json": rel(FILL_CARD_JSON),
        "source_fill_card_csv": rel(FILL_CARD_CSV),
        "source_quality_guide_json": rel(QUALITY_GUIDE_JSON),
        "source_template_preflight_json": rel(TEMPLATE_PREFLIGHT_JSON),
        "source_validation_json": rel(VALIDATION_JSON),
        "source_post_fill_runbook_json": rel(POST_FILL_RUNBOOK_JSON),
        "source_post_fill_check_json": rel(POST_FILL_CHECK_JSON),
        "source_post_fill_check_markdown": rel(post_fill_check_md),
        "source_safe_prefill_audit_json": rel(SAFE_PREFILL_AUDIT_JSON),
        "source_closure_board_json": rel(CLOSURE_BOARD_JSON),
        "source_workbook_import_approval_request_json": rel(WORKBOOK_IMPORT_APPROVAL_JSON),
        "source_workbook_import_approval_request_markdown": rel(WORKBOOK_IMPORT_APPROVAL_MD),
        "source_workbook_import_approval_request_csv": rel(WORKBOOK_IMPORT_APPROVAL_CSV),
        "source_workbook_import_approval_request_boundary_audit": rel(WORKBOOK_IMPORT_APPROVAL_AUDIT),
        "source_workbook_import_execution_applied_json": rel(WORKBOOK_IMPORT_APPLIED_JSON),
        "source_workbook_import_execution_applied_markdown": rel(WORKBOOK_IMPORT_APPLIED_MD),
        "source_workbook_import_execution_applied_boundary_audit": rel(
            WORKBOOK_IMPORT_APPLIED_AUDIT
        ),
        "source_template_transfer_execution_request_json": rel(
            TEMPLATE_TRANSFER_REQUEST_JSON
        ),
        "source_template_transfer_execution_request_markdown": rel(
            TEMPLATE_TRANSFER_REQUEST_MD
        ),
        "source_template_transfer_execution_request_csv": rel(
            TEMPLATE_TRANSFER_REQUEST_CSV
        ),
        "source_template_transfer_execution_request_boundary_audit": rel(
            TEMPLATE_TRANSFER_REQUEST_AUDIT
        ),
        "source_validator_approval_request_json": rel(VALIDATOR_APPROVAL_PACKET_JSON),
        "source_validator_approval_request_markdown": rel(VALIDATOR_APPROVAL_PACKET_MD),
        "source_validator_approval_request_csv": rel(VALIDATOR_APPROVAL_PACKET_CSV),
        "source_validator_approval_request_boundary_audit": rel(
            VALIDATOR_APPROVAL_PACKET_AUDIT
        ),
        "source_validator_hold_output_review_json": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_JSON),
        "source_validator_hold_output_review_markdown": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_MD),
        "source_validator_hold_output_review_csv": rel(VALIDATOR_HOLD_OUTPUT_REVIEW_CSV),
        "source_validator_hold_output_review_boundary_audit": rel(
            VALIDATOR_HOLD_OUTPUT_REVIEW_AUDIT
        ),
        "source_begin_here_html": rel(OUT_HTML),
        "source_quality_guide_html": rel(quality_guide_html),
        "source_template_preflight_markdown": rel(template_preflight_md),
        "source_fill_card_html": rel(fill_card_html),
        "source_post_fill_validation_runbook_html": rel(post_fill_runbook_html),
        "source_safe_prefill_audit_markdown": rel(safe_prefill_audit_md),
        "source_safe_prefill_audit_gate": rel(safe_prefill_audit_gate),
        "source_input_template_csv": rel(input_template_csv),
        "source_closure_readiness_board_html": rel(closure_board_html),
        "local_static_begin_here_html": True,
        "browser_readable_human_entrypoint": True,
        "browser_readable_closure_readiness_board": True,
        "plain_language_human_route_enabled": True,
        "plain_language_commercial_entry_v0_2": True,
        "plain_language_commercial_entry_v0_3": True,
        "ordinary_user_commercial_start_enabled": True,
        "commercial_begin_here_visual_palette": "commercial-clean-slate-mint-v2",
        "plain_language_human_route_step_count": 3,
        "plain_language_status_label": "暂不允许正式商用",
        "plain_language_next_action": "补齐 validator hold 审查表里列出的缺失输入；未单独批准前不执行证据 builder、不采证、不关闭事项。",
        "plain_language_stop_point": "停在缺失输入补齐和 validator 重跑准备；证据 builder 和证据收集仍需单独执行批准。",
        "plain_language_action_summary": "三步：先打开 hold 输出审查表，再补 metadata/evidence/source notes，最后重跑本地 validator。",
        "plain_language_one_sentence": "本地 validator 已运行并审查；下一步只补齐缺失输入证据。",
        "post_fill_dry_run_command": dry_run_command,
        "post_fill_json_check_command": fill_card.get(
            "post_fill_json_check_command",
            "python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json",
        ),
        "post_fill_mainline_command": fill_card.get(
            "post_fill_mainline_command",
            "python3 scripts/mainline_guard.py",
        ),
        "post_fill_quality_check_command": post_fill_check_command,
        "post_fill_commands_execute_external_calls": False,
        "post_fill_commands_import_workbook": False,
        "post_fill_commands_close_blockers": False,
        "approval_request_status": approval_packet.get("status"),
        "approval_request_count": approval_packet.get("approval_request_count"),
        "ready_import_approval_count": approval_packet.get("ready_import_approval_count"),
        "approved_import_count": approval_packet.get("approved_import_count"),
        "workbook_import_authorized_count": approval_packet.get("workbook_import_authorized_count"),
        "ready_for_workbook_import_approval": approval_packet.get("ready_for_workbook_import_approval") is True,
        "approval_missing_condition_count": approval_packet.get("missing_condition_count"),
        "approval_import_dry_run_ready": approval_packet.get("source_conditions", {}).get("import_dry_run_ready") is True,
        "approval_importer_ready": approval_packet.get("source_conditions", {}).get("importer_ready") is True,
        "approval_quick_fill_validator_ready": approval_packet.get("source_conditions", {}).get("quick_fill_validator_ready") is True,
        "approval_safety_preflight_passed": approval_packet.get("source_conditions", {}).get("safety_preflight_passed") is True,
        "separate_workbook_import_execution_request_required": approval_packet.get("separate_workbook_import_execution_request_required") is True,
        "workbook_import_execution_allowed": False,
        "workbook_import_execution_applied_status": workbook_import_applied.get("status"),
        "source_workbook_import_performed": workbook_import_applied.get("workbook_import_performed") is True,
        "source_workbook_written": workbook_import_applied.get("workbook_written") is True,
        "current_stage_import_completed": workbook_import_applied.get("workbook_import_performed") is True,
        "template_transfer_execution_request_status": template_transfer_request.get("status"),
        "ready_for_template_transfer_request": template_transfer_request.get("ready_for_template_transfer_request") is True,
        "ready_for_template_transfer_execution": template_transfer_request.get("ready_for_template_transfer_execution") is True,
        "ready_for_separate_human_template_transfer_execution_request": template_transfer_request.get(
            "ready_for_separate_human_template_transfer_execution_request"
        ) is True,
        "separate_template_transfer_execution_request_required": template_transfer_request.get(
            "separate_template_transfer_execution_request_required"
        ) is True,
        "required_transfer_ready_count": template_transfer_request.get("required_transfer_ready_count"),
        "target_template_count": template_transfer_request.get("target_template_count"),
        "template_transfer_authorized_count": template_transfer_request.get("template_transfer_authorized_count"),
        "template_transfer_authorized": template_transfer_request.get("template_transfer_authorized") is True,
        "template_transfer_performed": False,
        "template_transfer_execution_allowed": summary.get("template_transfer_execution_allowed") is True,
        "template_transfer_applier_execution_allowed": summary.get("template_transfer_applier_execution_allowed") is True,
        "ready_for_validator_approval": summary.get("ready_for_validator_approval") is True,
        "ready_for_validator_execution": False,
        "validator_execution_run_status": summary.get("validator_execution_run_status"),
        "validator_hold_output_review_status": summary.get(
            "validator_hold_output_review_status"
        ),
        "validator_hold_output_review_completed": summary.get(
            "validator_hold_output_review_completed"
        )
        is True,
        "validator_outputs_review_required": summary.get("validator_outputs_review_required") is True,
        "validator_missing_input_completion_required": summary.get(
            "validator_missing_input_completion_required"
        )
        is True,
        "rerun_validators_after_completion_required": summary.get(
            "rerun_validators_after_completion_required"
        )
        is True,
        "total_missing_metadata_field_count": int(
            summary.get("total_missing_metadata_field_count", 0) or 0
        ),
        "total_missing_evidence_item_count": int(
            summary.get("total_missing_evidence_item_count", 0) or 0
        ),
        "total_missing_source_note_count": int(
            summary.get("total_missing_source_note_count", 0) or 0
        ),
        "local_validators_run": summary.get("local_validators_run") is True,
        "planned_validator_count": validator_approval_packet.get("planned_validator_count"),
        "ready_validator_count": validator_approval_packet.get("ready_validator_count"),
        "validator_approval_request_status": validator_approval_packet.get("status"),
        "validator_approval_request_count": validator_approval_packet.get("approval_request_count"),
        "approved_validator_count": validator_approval_packet.get("approved_validator_count"),
        "validator_execution_authorized_count": validator_approval_packet.get(
            "validator_execution_authorized_count"
        ),
        "validators_run": summary.get("validators_run") is True,
        "validators_run_count": int(summary.get("validators_run_count", 0) or 0),
        "validator_hold_count": int(summary.get("validator_hold_count", 0) or 0),
        "validator_pass_count": int(summary.get("validator_pass_count", 0) or 0),
        "validator_stop_count": int(summary.get("validator_stop_count", 0) or 0),
        "builder_ready_count": int(summary.get("builder_ready_count", 0) or 0),
        "blockers_closed_by_validator_run": int(summary.get("blockers_closed_by_validator_run", 0) or 0),
        "requires_validator_approval_review": summary.get("requires_validator_approval_review") is True,
        "requires_validator_output_review": summary.get("requires_validator_output_review") is True,
        "requires_validator_input_completion": summary.get(
            "requires_validator_input_completion"
        )
        is True,
        "requires_validator_rerun_after_completion": summary.get(
            "requires_validator_rerun_after_completion"
        )
        is True,
        "requires_separate_validator_execution_request": summary.get(
            "requires_separate_validator_execution_request"
        ) is True,
        "requires_separate_evidence_builder_request": summary.get(
            "requires_separate_evidence_builder_request"
        ) is True,
        "first_action_id": summary.get("first_action_id", "NEXT-VAR-001"),
        "first_sequence_step_id": summary.get("first_sequence_step_id", "VAR-001"),
        "first_blocker_id": summary.get("first_blocker_id", "validator_approval_request"),
        "primary_human_input_lane": summary.get(
            "primary_human_input_lane", "commercial_sprint_validator_approval_review"
        ),
        "preferred_human_input_path": summary.get(
            "preferred_human_input_path", "validator_approval_request"
        ),
        "preferred_template_missing_value_row_count": summary.get("preferred_template_missing_value_row_count"),
        "full_quick_fill_missing_value_row_count": summary.get("full_quick_fill_missing_value_row_count"),
        "missing_value_row_count": summary.get("missing_value_row_count"),
        "production_blocker_count": summary.get("production_blocker_count"),
        "open_blocker_count": closure_board.get("open_blocker_count"),
        "closure_board_status": closure_board.get("status"),
        "closure_candidate_count": closure_board.get("closure_candidate_count"),
        "blockers_closed_by_closure_board": closure_board.get("blockers_closed_by_board"),
        "satisfied_production_checks": summary.get("satisfied_production_checks"),
        "quality_guide_status": quality_guide.get("status"),
        "quality_guide_row_count": quality_guide.get("guide_row_count"),
        "quality_guide_target_blocker_id": quality_guide.get("target_blocker_id"),
        "template_preflight_status": template_preflight.get("status"),
        "template_preflight_passed": template_preflight.get("preflight_passed") is True,
        "template_preflight_boundary_violation_count": template_preflight.get("boundary_violation_count"),
        "fill_card_row_count": fill_card.get("fill_card_row_count"),
        "blank_human_value_row_count": fill_card.get("blank_human_value_row_count"),
        "begin_here_row_preview_enabled": True,
        "begin_here_row_preview_source": rel(FILL_CARD_CSV),
        "begin_here_row_preview_count": len(row_preview),
        "begin_here_row_preview_rows": row_preview,
        "post_fill_runbook_status": post_fill_runbook.get("status"),
        "post_fill_validation_ready": post_fill_runbook.get("post_fill_validation_ready") is True,
        "post_fill_missing_human_value_row_count": post_fill_runbook.get("missing_human_value_row_count"),
        "post_fill_check_status": post_fill_check.get("status"),
        "post_fill_quality_lint_enabled": post_fill_check.get("quality_lint_enabled") is True,
        "post_fill_quality_lint_issue_count": int(
            post_fill_check.get("quality_lint_issue_count", 0) or 0
        ),
        "post_fill_forbidden_claim_lint_passed": post_fill_check.get(
            "forbidden_claim_lint_passed"
        )
        is True,
        "post_fill_shape_lint_passed": post_fill_check.get("shape_lint_passed") is True,
        "post_fill_ready_for_quality_safe_dry_run": post_fill_check.get(
            "ready_for_quality_safe_post_fill_dry_run"
        )
        is True,
        "safe_prefill_audit_status": safe_prefill_audit.get("status"),
        "safe_prefill_audit_target_blocker_id": safe_prefill_audit.get("target_blocker_id"),
        "safe_prefill_audit_template_row_count": safe_prefill_audit.get("template_row_count"),
        "safe_prefill_audit_human_required_row_count": safe_prefill_audit.get("human_required_row_count"),
        "codex_safe_prefill_count": safe_prefill_audit.get("codex_safe_prefill_count"),
        "safe_to_prefill_by_codex": safe_prefill_audit.get("safe_to_prefill_by_codex") is True,
        "placeholder_or_hold_prefill_allowed_count": safe_prefill_audit.get(
            "placeholder_or_hold_prefill_allowed_count"
        ),
        "blockers_closed_by_safe_prefill_audit": safe_prefill_audit.get("blockers_closed_by_audit"),
        "begin_here_safe_prefill_warning": True,
        "completed_batch_value_row_count": validation.get("completed_batch_value_row_count"),
        "missing_batch_value_row_count": validation.get("missing_batch_value_row_count"),
        "batch_validator_passed": validation.get("batch_validator_passed"),
        "ready_for_safety_preflight": summary.get("ready_for_safety_preflight") is True,
        "ready_for_workbook_import": summary.get("ready_for_workbook_import") is True,
        "human_input_required": False,
        "human_review_required": True,
        "begin_here_action_count": len(actions),
        "blockers_closed_by_begin_here": 0,
        "actions": actions,
        "stop_point": "停在 validator hold 输出审查；不执行 evidence builder、不发布、不把事项标记为已完成。",
        "next_human_action": summary.get("next_human_action"),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    payload["template_transfer_performed"] = summary.get("template_transfer_performed") is True
    payload["validators_run_on_real_input"] = summary.get("validators_run") is True
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = ["step_id", "title", "path", "command", "human_action_required", "codex_execution_allowed"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for action in payload["actions"]:
            writer.writerow({field: action.get(field, "") for field in fields})


def render_markdown(payload: dict[str, Any]) -> str:
    actions = "\n".join(
        [
            (
                f"| {a['step_id']} | {a['title']} | `{a['path']}` | "
                f"`{a['command']}` | {str(a['codex_execution_allowed']).lower()} |"
            )
            for a in payload["actions"]
        ]
    )
    row_preview = "\n".join(
        [
            (
                f"| {row['card_row_number']} | {row['human_plain_label']} | "
                f"{row['human_plain_instruction']} | "
                f"{row['human_plain_leave_blank_condition']} | "
                f"`{row['target_json_pointer']}` | false |"
            )
            for row in payload["begin_here_row_preview_rows"]
        ]
    )
    return f"""# SAEE Commercial Readiness Begin Here v0.1

commercial_readiness_begin_here_v0_1: true
entrypoint_scope: {payload['entrypoint_scope']}
status: {payload['status']}
commercial_status: hold
production_launch_status: hold

## Summary

This is the shortest current path for commercial-readiness work.

- first_action_id: {payload['first_action_id']}
- first_blocker_id: {payload['first_blocker_id']}
- preferred_human_input_path: {payload['preferred_human_input_path']}
- preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}
- full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
- production_blocker_count: {payload['production_blocker_count']}
- open_blocker_count: {payload['open_blocker_count']}
- closure_board_status: {payload['closure_board_status']}
- closure_candidate_count: {payload['closure_candidate_count']}
- blockers_closed_by_closure_board: {payload['blockers_closed_by_closure_board']}
- local_static_begin_here_html: true
- plain_language_commercial_entry_v0_2: true
- plain_language_commercial_entry_v0_3: true
- ordinary_user_commercial_start_enabled: true
- commercial_begin_here_visual_palette: {payload['commercial_begin_here_visual_palette']}
- plain_language_status_label: {payload['plain_language_status_label']}
- plain_language_next_action: {payload['plain_language_next_action']}
- plain_language_stop_point: {payload['plain_language_stop_point']}
- plain_language_action_summary: {payload['plain_language_action_summary']}
- plain_language_one_sentence: {payload['plain_language_one_sentence']}
- source_begin_here_html: {payload['source_begin_here_html']}
- source_quality_guide_html: {payload['source_quality_guide_html']}
- source_template_preflight_markdown: {payload['source_template_preflight_markdown']}
- source_fill_card_html: {payload['source_fill_card_html']}
- source_fill_card_csv: {payload['source_fill_card_csv']}
- source_post_fill_validation_runbook_html: {payload['source_post_fill_validation_runbook_html']}
- source_post_fill_check_markdown: {payload['source_post_fill_check_markdown']}
- source_safe_prefill_audit_markdown: {payload['source_safe_prefill_audit_markdown']}
- source_safe_prefill_audit_gate: {payload['source_safe_prefill_audit_gate']}
- source_workbook_import_approval_request_markdown: {payload['source_workbook_import_approval_request_markdown']}
- source_workbook_import_approval_request_csv: {payload['source_workbook_import_approval_request_csv']}
- source_workbook_import_approval_request_boundary_audit: {payload['source_workbook_import_approval_request_boundary_audit']}
- source_workbook_import_execution_applied_markdown: {payload['source_workbook_import_execution_applied_markdown']}
- source_workbook_import_execution_applied_boundary_audit: {payload['source_workbook_import_execution_applied_boundary_audit']}
- source_template_transfer_execution_request_markdown: {payload['source_template_transfer_execution_request_markdown']}
- source_template_transfer_execution_request_csv: {payload['source_template_transfer_execution_request_csv']}
- source_template_transfer_execution_request_boundary_audit: {payload['source_template_transfer_execution_request_boundary_audit']}
- source_validator_approval_request_markdown: {payload['source_validator_approval_request_markdown']}
- source_validator_approval_request_csv: {payload['source_validator_approval_request_csv']}
- source_validator_approval_request_boundary_audit: {payload['source_validator_approval_request_boundary_audit']}
- source_validator_approval_request_markdown: {payload['source_validator_approval_request_markdown']}
- source_validator_approval_request_csv: {payload['source_validator_approval_request_csv']}
- source_validator_approval_request_boundary_audit: {payload['source_validator_approval_request_boundary_audit']}
- approval_request_status: {payload['approval_request_status']}
- approval_request_count: {payload['approval_request_count']}
- ready_import_approval_count: {payload['ready_import_approval_count']}
- approved_import_count: {payload['approved_import_count']}
- workbook_import_authorized_count: {payload['workbook_import_authorized_count']}
- ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}
- ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}
- ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}
- approval_missing_condition_count: {payload['approval_missing_condition_count']}
- approval_import_dry_run_ready: {str(payload['approval_import_dry_run_ready']).lower()}
- approval_importer_ready: {str(payload['approval_importer_ready']).lower()}
- approval_quick_fill_validator_ready: {str(payload['approval_quick_fill_validator_ready']).lower()}
- approval_safety_preflight_passed: {str(payload['approval_safety_preflight_passed']).lower()}
- separate_workbook_import_execution_request_required: {str(payload['separate_workbook_import_execution_request_required']).lower()}
- workbook_import_execution_applied_status: {payload['workbook_import_execution_applied_status']}
- source_workbook_import_performed: {str(payload['source_workbook_import_performed']).lower()}
- source_workbook_written: {str(payload['source_workbook_written']).lower()}
- current_stage_import_completed: {str(payload['current_stage_import_completed']).lower()}
- template_transfer_execution_request_status: {payload['template_transfer_execution_request_status']}
- ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
- ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
- ready_for_separate_human_template_transfer_execution_request: {str(payload['ready_for_separate_human_template_transfer_execution_request']).lower()}
- separate_template_transfer_execution_request_required: {str(payload['separate_template_transfer_execution_request_required']).lower()}
- required_transfer_ready_count: {payload['required_transfer_ready_count']}
- target_template_count: {payload['target_template_count']}
- template_transfer_authorized_count: {payload['template_transfer_authorized_count']}
- template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
- template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
- template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
- template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
- validator_approval_request_status: {payload['validator_approval_request_status']}
- ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
- ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
- planned_validator_count: {payload['planned_validator_count']}
- ready_validator_count: {payload['ready_validator_count']}
- validator_approval_request_count: {payload['validator_approval_request_count']}
- approved_validator_count: {payload['approved_validator_count']}
- validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
- validators_run: {str(payload['validators_run']).lower()}
- requires_validator_approval_review: {str(payload['requires_validator_approval_review']).lower()}
- requires_separate_validator_execution_request: {str(payload['requires_separate_validator_execution_request']).lower()}
- source_input_template_csv: {payload['source_input_template_csv']}
- source_closure_readiness_board_html: {payload['source_closure_readiness_board_html']}
- template_preflight_status: {payload['template_preflight_status']}
- template_preflight_passed: {str(payload['template_preflight_passed']).lower()}
- template_preflight_boundary_violation_count: {payload['template_preflight_boundary_violation_count']}
- post_fill_runbook_status: {payload['post_fill_runbook_status']}
- post_fill_validation_ready: {str(payload['post_fill_validation_ready']).lower()}
- post_fill_missing_human_value_row_count: {payload['post_fill_missing_human_value_row_count']}
- post_fill_check_status: {payload['post_fill_check_status']}
- post_fill_quality_lint_enabled: {str(payload['post_fill_quality_lint_enabled']).lower()}
- post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}
- post_fill_forbidden_claim_lint_passed: {str(payload['post_fill_forbidden_claim_lint_passed']).lower()}
- post_fill_shape_lint_passed: {str(payload['post_fill_shape_lint_passed']).lower()}
- post_fill_ready_for_quality_safe_dry_run: {str(payload['post_fill_ready_for_quality_safe_dry_run']).lower()}
- safe_prefill_audit_status: {payload['safe_prefill_audit_status']}
- safe_to_prefill_by_codex: {str(payload['safe_to_prefill_by_codex']).lower()}
- codex_safe_prefill_count: {payload['codex_safe_prefill_count']}
- safe_prefill_audit_human_required_row_count: {payload['safe_prefill_audit_human_required_row_count']}
- blockers_closed_by_safe_prefill_audit: {payload['blockers_closed_by_safe_prefill_audit']}
- begin_here_safe_prefill_warning: true
- post_fill_dry_run_command: `{payload['post_fill_dry_run_command']}`
- begin_here_row_preview_enabled: true
- begin_here_row_preview_source: {payload['begin_here_row_preview_source']}
- begin_here_row_preview_count: {payload['begin_here_row_preview_count']}
- blockers_closed_by_begin_here: 0
- production_ready: false
- customer_validated: false
- product_launched: false

## 人现在只做这件事

一句话：{payload['plain_language_one_sentence']}

先打开 validator hold 输出审查表，补齐列出的 metadata、evidence 和
source notes。补齐后才重新运行本地 validator。这一步不会执行 evidence
builder，不会把任何 blocker 标记为完成，也不会产生正式生产证据。

## 先看这 3 件事

1. 现在还不能正式商用：还有 {payload['production_blocker_count']} 个上线前事项没补齐。
2. 本轮不是 evidence builder 执行：它只补齐 validator 缺失输入。
3. 补齐也不能直接上线：后续真实验证、证据收集和 blocker closure 都要单独请求。

## 不要做这 4 件事

- 不要把空白或猜测内容当成真实商用证据。
- 不要让 Codex 代填人工确认值。
- 不要在本入口运行 evidence builder、收集正式证据或把事项标记为已完成。
- 不要说 SAEE 已生产可用、已客户验证或已正式发布。

## Validator 缺失输入补齐

当前 validator 已运行并完成 hold 输出审查，进入缺失输入补齐：
`template_transfer_execution_request_status: {payload['template_transfer_execution_request_status']}`，
`ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}`，
`template_transfer_performed: {str(payload['template_transfer_performed']).lower()}`，
`ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}`，
`ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}`，
`validator_hold_output_review_completed: {str(payload['validator_hold_output_review_completed']).lower()}`。

- source_template_transfer_execution_request_markdown: {payload['source_template_transfer_execution_request_markdown']}
- source_template_transfer_execution_request_csv: {payload['source_template_transfer_execution_request_csv']}
- source_template_transfer_execution_request_boundary_audit: {payload['source_template_transfer_execution_request_boundary_audit']}
- source_validator_approval_request_markdown: {payload['source_validator_approval_request_markdown']}
- source_validator_approval_request_csv: {payload['source_validator_approval_request_csv']}
- source_validator_approval_request_boundary_audit: {payload['source_validator_approval_request_boundary_audit']}
- source_validator_hold_output_review_markdown: {payload['source_validator_hold_output_review_markdown']}
- source_validator_hold_output_review_csv: {payload['source_validator_hold_output_review_csv']}
- source_validator_hold_output_review_boundary_audit: {payload['source_validator_hold_output_review_boundary_audit']}
- ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
- ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
- ready_for_separate_human_template_transfer_execution_request: {str(payload['ready_for_separate_human_template_transfer_execution_request']).lower()}
- template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
- template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
- template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
- separate_template_transfer_execution_request_required: {str(payload['separate_template_transfer_execution_request_required']).lower()}
- validator_approval_request_status: {payload['validator_approval_request_status']}
- ready_validator_count: {payload['ready_validator_count']}
- approved_validator_count: {payload['approved_validator_count']}
- validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
- validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
- validator_outputs_review_required: {str(payload['validator_outputs_review_required']).lower()}
- validator_missing_input_completion_required: {str(payload['validator_missing_input_completion_required']).lower()}
- rerun_validators_after_completion_required: {str(payload['rerun_validators_after_completion_required']).lower()}
- total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
- total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
- total_missing_source_note_count: {payload['total_missing_source_note_count']}

## 旧 10 行材料只作历史参考

Safe-prefill audit 明确记录 `safe_to_prefill_by_codex: false`、
`codex_safe_prefill_count: 0`、`human_required_row_count: 10`。这些材料
不再是当前第一步，只保留为历史审计和只读参考。

- source_safe_prefill_audit_markdown: {payload['source_safe_prefill_audit_markdown']}
- source_safe_prefill_audit_gate: {payload['source_safe_prefill_audit_gate']}
- source_workbook_import_approval_request_markdown: {payload['source_workbook_import_approval_request_markdown']}
- source_workbook_import_approval_request_csv: {payload['source_workbook_import_approval_request_csv']}
- source_workbook_import_approval_request_boundary_audit: {payload['source_workbook_import_approval_request_boundary_audit']}
- approval_request_status: {payload['approval_request_status']}
- ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}
- ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}
- approval_missing_condition_count: {payload['approval_missing_condition_count']}
- separate_workbook_import_execution_request_required: {str(payload['separate_workbook_import_execution_request_required']).lower()}
- workbook_import_execution_allowed: false
- safe_prefill_audit_status: {payload['safe_prefill_audit_status']}
- safe_to_prefill_by_codex: {str(payload['safe_to_prefill_by_codex']).lower()}
- codex_safe_prefill_count: {payload['codex_safe_prefill_count']}
- human_required_row_count: {payload['safe_prefill_audit_human_required_row_count']}
- blockers_closed_by_safe_prefill_audit: {payload['blockers_closed_by_safe_prefill_audit']}

## 旧 10 行材料包含什么

这只是旧人工填写导航，不是当前执行入口，也不是自动填值。每一行只提醒
人当时要确认什么；Codex 仍然不得填写 `human_value_to_enter`。
旧字段名包括 `human_value_to_enter` 和可选 `notes_for_human`，这里只作只读说明。
工作簿导入审批和导入执行记录也只作历史参考；当前入口不再请求导入执行。

| 行 | 人要确认什么 | 怎么填 | 什么时候留空 | 写入位置 | Codex 可否代填 |
| --- | --- | --- | --- | --- | --- |
{row_preview}

## 完成准备度只读参考

当前完成准备度看板显示 `closure_candidate_count: 0`，也就是现在没有
任何事项可以标记为完成。该看板只作为审批前后的只读参考，不授权完成
事项，不导入工作簿，不声明生产可用。

- source_closure_readiness_board_html: {payload['source_closure_readiness_board_html']}
- browser_readable_closure_readiness_board: true
- blockers_closed_by_closure_board: 0

## Begin Here Actions

| 步骤 | 要做什么 | 文件 | 命令 | Codex 是否可代执行 |
| --- | --- | --- | --- | --- |
{actions}

## Stop Point

{payload['stop_point']}

Do not run validators on official real input, collect evidence, contact
customers, close blockers, launch product, or claim production readiness from
this entrypoint.

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- workbook_import_authorized: false
- template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
- template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
- template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
- template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
- ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
- ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
- approved_validator_count: {payload['approved_validator_count']}
- validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
- validators_run: {str(payload['validators_run']).lower()}
- validator_execution_run_status: {payload['validator_execution_run_status']}
- validator_outputs_review_required: {str(payload['validator_outputs_review_required']).lower()}
- local_validators_run: {str(payload['local_validators_run']).lower()}
- validators_run_count: {payload['validators_run_count']}
- validator_hold_count: {payload['validator_hold_count']}
- builder_ready_count: {payload['builder_ready_count']}
- blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
- requires_validator_output_review: {str(payload['requires_validator_output_review']).lower()}
- requires_separate_evidence_builder_request: {str(payload['requires_separate_evidence_builder_request']).lower()}
- validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_begin_here: 0
- post_fill_quality_check_command: {payload['post_fill_quality_check_command']}
- post_fill_quality_lint_enabled: {str(payload['post_fill_quality_lint_enabled']).lower()}
- post_fill_commands_execute_external_calls: false
- post_fill_commands_import_workbook: false
- post_fill_commands_close_blockers: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- production_ready: false
- customer_validated: false
- product_launched: false
"""


def root_relative_href(root_rel_path: str) -> str:
    """Return an href from OUT_DIR to a repo-relative path."""
    target = ROOT / root_rel_path
    return Path(os.path.relpath(target.resolve(), OUT_DIR.resolve())).as_posix()


def render_html(payload: dict[str, Any]) -> str:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    action_cards = "\n".join(
        f"""
        <article class="action-card">
          <span>{esc(action['step_id'])}</span>
          <h3>{esc(action['title'])}</h3>
          <p><strong>文件：</strong><code>{esc(action['path'])}</code></p>
          <p><strong>命令：</strong><code>{esc(action['command'] or '无')}</code></p>
          <p class="safe">Codex 是否可代执行：否</p>
        </article>
        """
        for action in payload["actions"]
    )
    row_preview_cards = "\n".join(
        f"""
        <article class="row-card">
          <span>{esc(row['card_row_number'])}</span>
          <div>
            <h3>{esc(row['human_plain_label'])}</h3>
            <p>{esc(row['human_plain_instruction'])}</p>
            <p class="muted">留空条件：{esc(row['human_plain_leave_blank_condition'])}</p>
            <code>{esc(row['target_json_pointer'])}</code>
            <p class="safe">Codex 可否代填：否</p>
          </div>
        </article>
        """
        for row in payload["begin_here_row_preview_rows"]
    )
    quality_guide_href = root_relative_href(payload["source_quality_guide_html"])
    preflight_href = root_relative_href(payload["source_template_preflight_markdown"])
    fill_card_href = root_relative_href(payload["source_fill_card_html"])
    post_fill_href = root_relative_href(payload["source_post_fill_validation_runbook_html"])
    post_fill_check_href = root_relative_href(payload["source_post_fill_check_markdown"])
    safe_prefill_href = root_relative_href(payload["source_safe_prefill_audit_markdown"])
    csv_href = root_relative_href(payload["source_input_template_csv"])
    closure_board_href = root_relative_href(payload["source_closure_readiness_board_html"])
    approval_md_href = root_relative_href(payload["source_workbook_import_approval_request_markdown"])
    approval_csv_href = root_relative_href(payload["source_workbook_import_approval_request_csv"])
    approval_audit_href = root_relative_href(payload["source_workbook_import_approval_request_boundary_audit"])
    workbook_import_applied_href = root_relative_href(
        payload["source_workbook_import_execution_applied_markdown"]
    )
    template_transfer_md_href = root_relative_href(
        payload["source_template_transfer_execution_request_markdown"]
    )
    template_transfer_csv_href = root_relative_href(
        payload["source_template_transfer_execution_request_csv"]
    )
    template_transfer_audit_href = root_relative_href(
        payload["source_template_transfer_execution_request_boundary_audit"]
    )
    validator_approval_md_href = root_relative_href(
        payload["source_validator_approval_request_markdown"]
    )
    validator_approval_csv_href = root_relative_href(
        payload["source_validator_approval_request_csv"]
    )
    validator_approval_audit_href = root_relative_href(
        payload["source_validator_approval_request_boundary_audit"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 商用准备从这里开始</title>
    <style>
      :root {{
        color-scheme: light;
        --palette-name: commercial-clean-slate-mint-v2;
        --bg: #f7f7f4;
        --surface: #ffffff;
        --surface-soft: #eeeeea;
        --text: #1f211f;
        --muted: #66706a;
        --line: #deded8;
        --ink: #111311;
        --accent: #138c72;
        --accent-strong: #0f6f5d;
        --accent-soft: #e9f4ef;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background:
          radial-gradient(circle at 8% 4%, rgba(19, 140, 114, 0.1), transparent 28rem),
          linear-gradient(135deg, #ffffff 0%, var(--bg) 62%, #eff6f2 100%);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.6;
      }}
      main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0 64px; }}
      header {{
        display: grid;
        gap: 18px;
        padding: clamp(28px, 5vw, 58px);
        border: 1px solid var(--line);
        border-radius: 10px;
        background:
          radial-gradient(circle at 82% 12%, rgba(19, 140, 114, 0.12), transparent 30%),
          linear-gradient(135deg, var(--surface) 0%, var(--accent-soft) 100%);
      }}
      .kicker {{ margin: 0; color: var(--accent-strong); font-size: 13px; font-weight: 900; }}
      h1 {{ margin: 0; max-width: 820px; font-size: clamp(34px, 5vw, 62px); line-height: 1.04; letter-spacing: 0; }}
      h2 {{ margin: 0 0 14px; font-size: clamp(24px, 3vw, 36px); line-height: 1.15; letter-spacing: 0; }}
      h3 {{ margin: 0 0 10px; font-size: 18px; }}
      p {{ margin: 0; }}
      .lead {{ max-width: 760px; color: var(--muted); font-size: 18px; }}
      .status-grid, .action-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin-top: 24px;
      }}
      .row-preview-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-top: 18px;
      }}
      .status-card, .action-card, .panel {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
      }}
      .status-card {{ min-height: 112px; padding: 18px; }}
      .status-card strong {{ display: block; font-size: 26px; line-height: 1; }}
      .status-card span {{ display: block; margin-top: 9px; color: var(--muted); font-size: 13px; }}
      section {{ margin-top: 34px; }}
      .panel {{ padding: 24px; }}
      .primary-actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
      a.button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        padding: 0 16px;
        border-radius: 8px;
        color: #fff;
        background: var(--ink);
        font-weight: 800;
        text-decoration: none;
      }}
      a.secondary {{ color: var(--ink); background: var(--surface); border: 1px solid var(--line); }}
      .action-card {{ padding: 18px; }}
      .row-card {{
        display: grid;
        grid-template-columns: 44px 1fr;
        gap: 14px;
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
      }}
      .row-card span {{
        display: grid;
        place-items: center;
        width: 38px;
        height: 38px;
        border-radius: 8px;
        color: #fff;
        background: var(--accent-strong);
        font-weight: 900;
      }}
      .row-card p {{ color: var(--text); }}
      .row-card .muted {{ margin-top: 8px; color: var(--muted); }}
      .action-card span {{
        display: inline-grid;
        place-items: center;
        min-width: 42px;
        height: 30px;
        margin-bottom: 14px;
        border-radius: 8px;
        color: #fff;
        background: var(--accent-strong);
        font-size: 12px;
        font-weight: 900;
      }}
      code {{
        display: inline-block;
        max-width: 100%;
        padding: 2px 5px;
        border-radius: 6px;
        background: var(--surface-soft);
        color: var(--ink);
        overflow-wrap: anywhere;
      }}
      .safe {{ margin-top: 10px; color: var(--accent-strong); font-weight: 800; }}
      .command-panel {{
        display: grid;
        gap: 10px;
        padding: 18px;
        border-radius: 10px;
        background: var(--ink);
        color: #fff;
      }}
      .command-panel code {{ color: #fff; background: rgba(255, 255, 255, 0.12); }}
      ul {{ display: grid; gap: 8px; padding-left: 20px; margin: 12px 0 0; }}
      li {{ color: var(--muted); }}
      @media (max-width: 860px) {{
        .status-grid, .action-grid, .row-preview-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      }}
      @media (max-width: 560px) {{
        main {{ width: min(100% - 24px, 1120px); padding-top: 24px; }}
        header {{ padding: 24px; }}
        .status-grid, .action-grid, .row-preview-grid {{ grid-template-columns: 1fr; }}
        .primary-actions {{ display: grid; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="kicker">SAEE 商用准备入口</p>
        <h1>现在还不能正式商用，先审查 validator。</h1>
        <p class="lead">一句话：模板转写已完成；下一步只审查 5 个 validator 是否可进入单独执行请求。这个页面只告诉人下一步怎么判断；现在不运行验证、不采证、不把事项标记为已完成，也不代表产品已经上线。</p>
        <div class="status-grid" aria-label="当前状态">
          <div class="status-card"><strong>{esc(payload['production_blocker_count'])}</strong><span>上线前事项仍未补齐</span></div>
          <div class="status-card"><strong>{esc(payload['missing_value_row_count'])}</strong><span>总缺失人工值</span></div>
          <div class="status-card"><strong>{esc(payload['ready_validator_count'])}</strong><span>待审查 validator</span></div>
          <div class="status-card"><strong>{esc(payload['approved_validator_count'])}</strong><span>已批准 validator</span></div>
        </div>
      </header>

      <section class="panel">
        <p class="kicker">人现在只做这件事</p>
        <h2>三步：先看 validator 审批请求，再决定批准或暂缓，最后停止。</h2>
        <p>先确认模板转写已经完成。然后只审查 validator 批准请求。审批后停止，不运行验证、不采证、不关闭事项。</p>
        <div class="primary-actions">
          <a class="button" href="{esc(validator_approval_md_href)}">打开 validator 审批请求</a>
          <a class="button secondary" href="{esc(validator_approval_csv_href)}">查看审批 CSV</a>
          <a class="button secondary" href="{esc(validator_approval_audit_href)}">查看审批边界</a>
          <a class="button secondary" href="{esc(closure_board_href)}">查看完成准备度</a>
        </div>
      </section>

      <section class="panel">
        <p class="kicker">先看这 3 件事</p>
        <h2>这是商用准备，不是上线开关。</h2>
        <ul>
          <li>现在还不能正式商用：还有 <strong>{esc(payload['production_blocker_count'])}</strong> 个上线前事项没补齐。</li>
          <li>本轮只允许审查 validator 审批请求：审批后必须停止。</li>
          <li>批准也不能直接上线：真实执行、证据收集和事项关闭都要单独请求。</li>
        </ul>
      </section>

      <section class="panel">
        <p class="kicker">不要做这 4 件事</p>
        <h2>避免把准备材料误写成商用事实。</h2>
        <ul>
          <li>不要把空白或猜测内容当成真实商用证据。</li>
          <li>不要让 Codex 代填人工确认值。</li>
          <li>不要在审批后继续收集正式证据、运行验证或把事项标记为已完成。</li>
          <li>不要说 SAEE 已生产可用、已客户验证或已正式发布。</li>
        </ul>
      </section>

      <section class="panel">
        <p class="kicker">Validator 审批状态</p>
        <h2>已准备进入人工审批，不允许运行。</h2>
        <p>当前 <code>validator_execution_run_status: {esc(payload['validator_execution_run_status'])}</code>，<code>validators_run: {esc(str(payload['validators_run']).lower())}</code>，<code>validator_hold_count: {esc(payload['validator_hold_count'])}</code>，<code>builder_ready_count: {esc(payload['builder_ready_count'])}</code>，<code>blockers_closed_by_validator_run: {esc(payload['blockers_closed_by_validator_run'])}</code>。</p>
        <div class="primary-actions">
          <a class="button secondary" href="{esc(validator_approval_md_href)}">查看 validator 审批请求</a>
          <a class="button secondary" href="{esc(workbook_import_applied_href)}">查看导入记录</a>
        </div>
      </section>

      <section class="panel">
        <p class="kicker">旧 10 行材料只作历史参考</p>
        <h2>旧材料不是当前第一步。</h2>
        <p>Safe-prefill audit 显示 <code>safe_to_prefill_by_codex: false</code>，<code>codex_safe_prefill_count: {esc(payload['codex_safe_prefill_count'])}</code>，<code>human_required_row_count: {esc(payload['safe_prefill_audit_human_required_row_count'])}</code>。这些材料只保留为审计参考，不授权 Codex 代填；工作簿导入记录也只作历史参考。</p>
        <div class="primary-actions">
          <a class="button secondary" href="{esc(safe_prefill_href)}">查看不可代填审计</a>
          <a class="button secondary" href="{esc(safe_prefill_href)}">打开不可代填审计</a>
          <a class="button secondary" href="{esc(fill_card_href)}">查看旧 10 行说明</a>
        </div>
      </section>

      <section class="panel">
        <p class="kicker">旧 10 行材料包含什么</p>
        <h2>只读参考，不是当前执行入口。</h2>
        <p>下面只是把旧 10 行 CSV 的中文说明放在同一页，方便回看。旧字段名包括 <code>human_value_to_enter</code> 和可选 <code>notes_for_human</code>。这里不写入任何值，也不允许 Codex 代填。</p>
        <div class="row-preview-grid">
          {row_preview_cards}
        </div>
      </section>

      <section class="panel">
        <p class="kicker">完成准备度只读参考</p>
        <h2>现在没有任何事项可以标记为完成。</h2>
        <p>完成准备度看板显示 <code>closure_candidate_count: {esc(payload['closure_candidate_count'])}</code>，<code>blockers_closed_by_closure_board: {esc(payload['blockers_closed_by_closure_board'])}</code>。先补人工证据，再重新运行验证。</p>
        <div class="primary-actions">
          <a class="button secondary" href="{esc(closure_board_href)}">打开完成准备度看板</a>
        </div>
      </section>

      <section>
        <p class="kicker">执行顺序</p>
        <h2>四步，审批后停。</h2>
        <div class="action-grid">
          {action_cards}
        </div>
      </section>

      <section class="panel">
        <p class="kicker">后续仍需单独请求</p>
        <h2>审批记录不是 validator 执行。</h2>
        <div class="command-panel">
          <code>template_transfer_authorized: {esc(str(payload['template_transfer_authorized']).lower())}</code>
          <code>template_transfer_performed: {esc(str(payload['template_transfer_performed']).lower())}</code>
          <code>template_transfer_execution_allowed: {esc(str(payload['template_transfer_execution_allowed']).lower())}</code>
          <code>template_transfer_applier_execution_allowed: {esc(str(payload['template_transfer_applier_execution_allowed']).lower())}</code>
          <code>ready_for_validator_approval: {esc(str(payload['ready_for_validator_approval']).lower())}</code>
          <code>ready_for_validator_execution: {esc(str(payload['ready_for_validator_execution']).lower())}</code>
          <code>validators_run: {esc(str(payload['validators_run']).lower())}</code>
          <code>blockers_closed_by_begin_here: 0</code>
        </div>
      </section>

      <section class="panel">
        <p class="kicker">边界</p>
        <h2>这个入口不能做的事。</h2>
        <ul>
          <li>不生成或猜测人工值。</li>
          <li>不再次导入工作簿，不重新执行模板转写。</li>
          <li>不运行真实输入验证器，不收集证据，不把事项标记为已完成。</li>
          <li>不联系客户，不发布产品，不声明生产可用。</li>
          <li>不修改运行时、后端、内核、接口结构或私有核心。</li>
        </ul>
      </section>
    </main>
  </body>
</html>
"""


def render_audit(payload: dict[str, Any]) -> str:
    return f"""# Commercial Readiness Begin Here Boundary Audit

- entrypoint_scope: {payload['entrypoint_scope']}
- status: {payload['status']}
- local_static_begin_here_html: true
- source_quality_guide_html: {payload['source_quality_guide_html']}
- source_template_preflight_markdown: {payload['source_template_preflight_markdown']}
- template_preflight_passed: {str(payload['template_preflight_passed']).lower()}
- source_post_fill_validation_runbook_html: {payload['source_post_fill_validation_runbook_html']}
- post_fill_validation_ready: {str(payload['post_fill_validation_ready']).lower()}
- source_post_fill_check_markdown: {payload['source_post_fill_check_markdown']}
- post_fill_check_status: {payload['post_fill_check_status']}
- post_fill_quality_check_command: {payload['post_fill_quality_check_command']}
- post_fill_quality_lint_enabled: {str(payload['post_fill_quality_lint_enabled']).lower()}
- post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}
- post_fill_forbidden_claim_lint_passed: {str(payload['post_fill_forbidden_claim_lint_passed']).lower()}
- post_fill_shape_lint_passed: {str(payload['post_fill_shape_lint_passed']).lower()}
- post_fill_ready_for_quality_safe_dry_run: {str(payload['post_fill_ready_for_quality_safe_dry_run']).lower()}
- source_safe_prefill_audit_markdown: {payload['source_safe_prefill_audit_markdown']}
- source_safe_prefill_audit_gate: {payload['source_safe_prefill_audit_gate']}
- source_workbook_import_execution_applied_markdown: {payload['source_workbook_import_execution_applied_markdown']}
- source_template_transfer_execution_request_markdown: {payload['source_template_transfer_execution_request_markdown']}
- source_template_transfer_execution_request_csv: {payload['source_template_transfer_execution_request_csv']}
- source_template_transfer_execution_request_boundary_audit: {payload['source_template_transfer_execution_request_boundary_audit']}
- workbook_import_execution_applied_status: {payload['workbook_import_execution_applied_status']}
- source_workbook_import_performed: {str(payload['source_workbook_import_performed']).lower()}
- source_workbook_written: {str(payload['source_workbook_written']).lower()}
- template_transfer_execution_request_status: {payload['template_transfer_execution_request_status']}
- ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
- ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
- ready_for_separate_human_template_transfer_execution_request: {str(payload['ready_for_separate_human_template_transfer_execution_request']).lower()}
- separate_template_transfer_execution_request_required: {str(payload['separate_template_transfer_execution_request_required']).lower()}
- required_transfer_ready_count: {payload['required_transfer_ready_count']}
- target_template_count: {payload['target_template_count']}
- template_transfer_authorized_count: {payload['template_transfer_authorized_count']}
- template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
- template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
- template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
- template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
- validator_approval_request_status: {payload['validator_approval_request_status']}
- ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
- ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
- planned_validator_count: {payload['planned_validator_count']}
- ready_validator_count: {payload['ready_validator_count']}
- approved_validator_count: {payload['approved_validator_count']}
- validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
- validators_run: {str(payload['validators_run']).lower()}
- safe_prefill_audit_status: {payload['safe_prefill_audit_status']}
- safe_to_prefill_by_codex: {str(payload['safe_to_prefill_by_codex']).lower()}
- codex_safe_prefill_count: {payload['codex_safe_prefill_count']}
- safe_prefill_audit_human_required_row_count: {payload['safe_prefill_audit_human_required_row_count']}
- blockers_closed_by_safe_prefill_audit: {payload['blockers_closed_by_safe_prefill_audit']}
- begin_here_safe_prefill_warning: true
- browser_readable_closure_readiness_board: true
- source_closure_readiness_board_html: {payload['source_closure_readiness_board_html']}
- closure_candidate_count: {payload['closure_candidate_count']}
- blockers_closed_by_closure_board: {payload['blockers_closed_by_closure_board']}
- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- workbook_import_authorized: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_begin_here: 0
- post_fill_quality_lint_enabled: {str(payload['post_fill_quality_lint_enabled']).lower()}
- post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}
- post_fill_ready_for_quality_safe_dry_run: {str(payload['post_fill_ready_for_quality_safe_dry_run']).lower()}
- post_fill_commands_execute_external_calls: false
- post_fill_commands_import_workbook: false
- post_fill_commands_close_blockers: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- production_ready: false
- customer_validated: false
- product_launched: false

Boundary decision: pass. This is a navigation surface only.
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Readiness Begin Here Recommendation Gate

answer: recommend

reason: This entrypoint gives a human the shortest current commercial-readiness
path: confirm that template transfer has completed, then review the five
validator approval requests and stop. Use the closure readiness board only as a
read-only reference. Stop before validator execution, evidence collection,
blocker closure, launch, or production-readiness claims.

recommend_for_human_navigation: true
recommend_for_template_transfer_execution_request_review: false
recommend_for_workbook_import_approval_review: false
recommend_for_workbook_import_execution: false
recommend_for_template_transfer_execution: false
recommend_for_validator_approval_review: true
recommend_for_validator_execution: false
recommend_for_quality_guided_human_entry: false
recommend_for_template_preflight_reference: false
recommend_for_post_fill_validation_runbook: false
recommend_for_post_fill_quality_lint_wrapper: false
recommend_for_safe_prefill_warning: true
recommend_for_10_row_human_entry: false
recommend_for_browser_readable_local_entrypoint: true
recommend_for_closure_readiness_reference: true
recommend_for_value_generation_by_codex: false
recommend_for_codex_prefill: false
recommend_for_workbook_import_execution: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production: false

boundary:
  runtime_modified: false
  backend_modified: false
  kernel_modified: false
  api_schema_modified: false
  private_core_exposed: false
  production_ready: false
  customer_validated: false
  product_launched: false
  blockers_closed_by_begin_here: 0
  approval_request_status: {payload['approval_request_status']}
  ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}
  ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}
  separate_workbook_import_execution_request_required: true
  workbook_import_execution_allowed: false
  workbook_import_execution_applied_status: {payload['workbook_import_execution_applied_status']}
  source_workbook_import_performed: {str(payload['source_workbook_import_performed']).lower()}
  template_transfer_execution_request_status: {payload['template_transfer_execution_request_status']}
  ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
  ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
  ready_for_separate_human_template_transfer_execution_request: {str(payload['ready_for_separate_human_template_transfer_execution_request']).lower()}
  separate_template_transfer_execution_request_required: {str(payload['separate_template_transfer_execution_request_required']).lower()}
  template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
  template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
  template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
  template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
  ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
  ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
  approved_validator_count: {payload['approved_validator_count']}
  validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
  validators_run: {str(payload['validators_run']).lower()}
  begin_here_safe_prefill_warning: true
  safe_prefill_audit_status: {payload['safe_prefill_audit_status']}
  safe_to_prefill_by_codex: false
  codex_safe_prefill_count: 0
  safe_prefill_audit_human_required_row_count: {payload['safe_prefill_audit_human_required_row_count']}
  blockers_closed_by_safe_prefill_audit: 0
  closure_candidate_count: 0
  blockers_closed_by_closure_board: 0
  local_static_begin_here_html: true
  browser_readable_closure_readiness_board: true
  post_fill_quality_lint_enabled: {str(payload['post_fill_quality_lint_enabled']).lower()}
  post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}
  post_fill_ready_for_quality_safe_dry_run: {str(payload['post_fill_ready_for_quality_safe_dry_run']).lower()}

next_action: Human opens the validator approval request, confirms the
post-transfer boundary state, records approve or hold, then stops. Validator
execution requires a separate explicit request.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    markdown = render_markdown(payload)
    OUT_MD.write_text(markdown, encoding="utf-8")
    OUT_README.write_text(markdown, encoding="utf-8")
    TOP_DOC.write_text(markdown, encoding="utf-8")
    OUT_HTML.write_text(render_html(payload), encoding="utf-8")
    OUT_AUDIT.write_text(render_audit(payload), encoding="utf-8")
    GATE.write_text(render_gate(payload), encoding="utf-8")
    print(
        "SAEE_COMMERCIAL_READINESS_BEGIN_HERE: PASS "
        f"status={payload['status']} "
        f"preferred_template_missing_value_row_count={payload['preferred_template_missing_value_row_count']} "
        "blockers_closed_by_begin_here=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
