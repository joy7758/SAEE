#!/usr/bin/env python3
"""Build the SAEE commercial readiness dashboard.

This script consolidates existing commercial readiness evidence into one local
review surface. It does not execute blocker tasks, contact customers or
vendors, collect evidence, launch product, claim production readiness, or
modify runtime/backend/kernel/API schema/private core behavior.
"""

from __future__ import annotations

import csv
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS, load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_dashboard"
OUTPUT_JSON = OUTPUT_DIR / "commercial_readiness_dashboard.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_readiness_dashboard.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_readiness_dashboard.csv"
OUTPUT_HTML = OUTPUT_DIR / "commercial_readiness_dashboard.html"
OUTPUT_BOUNDARY = OUTPUT_DIR / "commercial_readiness_dashboard_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_READINESS_DASHBOARD_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_DASHBOARD_RECOMMENDATION_GATE.md"

GAP_MATRIX_PATH = (
    ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"
)
DEPENDENCY_PLAN_PATH = (
    ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
)
EVIDENCE_PACKET_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet/commercial_production_evidence_collection_packet.local.json"
)
COMMERCIAL_PROFILE_JSON_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.json"
)
COMMERCIAL_PROFILE_ENV_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.env.example"
)
COMMERCIAL_STATUS_PATH = (
    ROOT / "phase_b_product/commercial_readiness/commercial_readiness_status.local.json"
)

BEGIN_HERE_HTML = (
    "phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html"
)
REVIEW_BATCH_FILL_CARD_HTML = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.html"
)
POST_FILL_READINESS_PREVIEW_HTML = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_readiness_preview.html"
)
REVIEW_BATCH_QUALITY_GUIDE_HTML = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_entry_quality_guide.html"
)
REVIEW_BATCH_TEMPLATE_PREFLIGHT_MD = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.md"
)
COMPLETION_QUEUE_HTML = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.html"
)
POST_FILL_VALIDATION_RUNBOOK_HTML = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_validation_runbook.html"
)
CLOSURE_READINESS_BOARD_HTML = (
    "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.html"
)
QUICK_FILL_TEMPLATE_CSV = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
WORKBOOK_IMPORT_APPROVAL_REQUEST_MD = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_approval_request_packet.md"
)
WORKBOOK_IMPORT_DRY_RUN_MD = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_workbook_import_dry_run.md"
)
WORKBOOK_IMPORTER_MD = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_workbook_importer.md"
)

PRIORITY_PACKETS = [
    {
        "phase_number": 1,
        "path": ROOT
        / "phase_b_product/commercial_readiness/phase_1_identity_tenant_priority_evidence_collection/phase_1_identity_tenant_priority_evidence_collection.local.json",
        "template": "phase_b_product/commercial_readiness/phase_1_identity_tenant_priority_evidence_collection/phase_1_identity_tenant_evidence_input.priority.template.json",
    },
    {
        "phase_number": 2,
        "path": ROOT
        / "phase_b_product/commercial_readiness/phase_2_data_operations_priority_evidence_collection/phase_2_data_operations_priority_evidence_collection.local.json",
        "template": "phase_b_product/commercial_readiness/phase_2_data_operations_priority_evidence_collection/phase_2_data_operations_evidence_input.priority.template.json",
    },
    {
        "phase_number": 3,
        "path": ROOT
        / "phase_b_product/commercial_readiness/phase_3_support_security_legal_priority_evidence_collection/phase_3_support_security_legal_priority_evidence_collection.local.json",
        "template": "phase_b_product/commercial_readiness/phase_3_support_security_legal_priority_evidence_collection/phase_3_support_security_legal_evidence_input.priority.template.json",
    },
    {
        "phase_number": 4,
        "path": ROOT
        / "phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_priority_evidence_collection/phase_4_commercial_packaging_billing_priority_evidence_collection.local.json",
        "template": "phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_priority_evidence_collection/phase_4_commercial_packaging_billing_evidence_input.priority.template.json",
    },
    {
        "phase_number": 5,
        "path": ROOT
        / "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_priority_evidence_collection/phase_5_customer_validation_launch_priority_evidence_collection.local.json",
        "template": "phase_b_product/commercial_readiness/phase_5_customer_validation_launch_priority_evidence_collection/phase_5_customer_validation_launch_evidence_input.priority.template.json",
    },
]

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
    "blockers_closed_by_dashboard",
    "customer_data_collected",
    "customer_data_processed",
    "payment_collected",
    "revenue_validated",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_priority_packets() -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for meta in PRIORITY_PACKETS:
        packet = read_json(meta["path"])
        packet["_source_path"] = rel(meta["path"])
        packet["_template_path"] = meta["template"]
        packet["_phase_number"] = meta["phase_number"]
        packets.append(packet)
    return packets


def build_phase_rows(priority_packets: list[dict[str, Any]], phases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    title_by_phase = {phase.get("phase_id"): phase.get("title", "") for phase in phases}
    rows: list[dict[str, Any]] = []
    for packet in priority_packets:
        required = int(packet.get("required_evidence_item_count", 0))
        local_present = int(packet.get("local_public_shell_present_count", 0))
        missing = int(packet.get("missing_production_evidence_count", 0))
        rows.append(
            {
                "phase_number": packet["_phase_number"],
                "phase_id": packet.get("phase_id", ""),
                "title": title_by_phase.get(packet.get("phase_id"), ""),
                "target_blocker_count": int(packet.get("target_blocker_count", 0)),
                "target_blockers": packet.get("target_blockers", []),
                "required_evidence_item_count": required,
                "local_public_shell_present_count": local_present,
                "missing_production_evidence_count": missing,
                "local_evidence_ratio": round(local_present / required, 4) if required else 0.0,
                "blockers_closed_by_collection": int(packet.get("blockers_closed_by_collection", 0)),
                "status": packet.get("status", ""),
                "human_review_required": packet.get("human_review_required") is True,
                "manual_collection_required": packet.get("manual_collection_required") is True,
                "execution_authorized": packet.get("execution_authorized") is True,
                "evidence_collection_authorized": packet.get("evidence_collection_authorized") is True,
                "source_packet": packet["_source_path"],
                "priority_template": packet["_template_path"],
            }
        )
    return rows


def build_blocker_rows(
    go_no_go: dict[str, Any],
    gap_matrix: dict[str, Any],
    dependency_plan: dict[str, Any],
    priority_packets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    blocker_by_id = {row.get("blocker_id"): row for row in go_no_go.get("blockers", [])}
    matrix_by_id = {row.get("blocker_id"): row for row in gap_matrix.get("matrix", [])}
    plan_by_id = {row.get("blocker_id"): row for row in dependency_plan.get("blockers", [])}
    priority_by_blocker: dict[str, dict[str, int]] = {}
    phase_by_blocker: dict[str, str] = {}
    for packet in priority_packets:
        phase_id = str(packet.get("phase_id", ""))
        for summary in packet.get("blocker_summary", []):
            blocker_id = str(summary.get("blocker_id", ""))
            priority_by_blocker[blocker_id] = {
                "required_items": int(summary.get("required_items", 0)),
                "local_public_shell_present": int(summary.get("local_public_shell_present", 0)),
                "missing_production_evidence": int(summary.get("missing_production_evidence", 0)),
            }
            phase_by_blocker[blocker_id] = phase_id

    rows: list[dict[str, Any]] = []
    for blocker_id in sorted(blocker_by_id):
        blocker = blocker_by_id[blocker_id]
        matrix = matrix_by_id.get(blocker_id, {})
        plan = plan_by_id.get(blocker_id, {})
        priority = priority_by_blocker.get(
            blocker_id,
            {
                "required_items": 0,
                "local_public_shell_present": 0,
                "missing_production_evidence": 0,
            },
        )
        rows.append(
            {
                "blocker_id": blocker_id,
                "category": blocker.get("category", ""),
                "phase_id": phase_by_blocker.get(blocker_id, plan.get("phase_id", "")),
                "status": "closed" if blocker.get("satisfied") is True else "open",
                "satisfied": blocker.get("satisfied") is True,
                "owner_review_lane": matrix.get("owner_review_lane", plan.get("owner_review_lane", "")),
                "required_evidence": matrix.get("required_evidence", plan.get("required_evidence", "")),
                "local_evidence_path": matrix.get("local_evidence_path", plan.get("local_evidence_path", "")),
                "required_evidence_item_count": priority["required_items"],
                "local_public_shell_present_count": priority["local_public_shell_present"],
                "missing_production_evidence_count": priority["missing_production_evidence"],
                "external_dependency_required": plan.get("external_dependency_required") is True
                or matrix.get("external_dependency_required") is True,
                "engineering_implementation_required": plan.get("engineering_implementation_required") is True
                or matrix.get("engineering_implementation_required") is True,
                "human_approval_required": True,
                "requires_separate_execution_request": True,
                "closure_allowed_by_dashboard": False,
                "execution_allowed_by_dashboard": False,
                "next_required_action": matrix.get(
                    "next_required_action",
                    plan.get("next_human_action", "Human review required before any execution."),
                ),
            }
        )
    return rows


def build_category_summary(blocker_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[str, dict[str, int | str]] = {}
    for row in blocker_rows:
        category = str(row["category"])
        item = summary.setdefault(
            category,
            {
                "category": category,
                "blocker_count": 0,
                "open_blocker_count": 0,
                "required_evidence_item_count": 0,
                "local_public_shell_present_count": 0,
                "missing_production_evidence_count": 0,
            },
        )
        item["blocker_count"] = int(item["blocker_count"]) + 1
        if row["status"] == "open":
            item["open_blocker_count"] = int(item["open_blocker_count"]) + 1
        item["required_evidence_item_count"] = int(item["required_evidence_item_count"]) + int(
            row["required_evidence_item_count"]
        )
        item["local_public_shell_present_count"] = int(item["local_public_shell_present_count"]) + int(
            row["local_public_shell_present_count"]
        )
        item["missing_production_evidence_count"] = int(item["missing_production_evidence_count"]) + int(
            row["missing_production_evidence_count"]
        )
    return [dict(row) for row in sorted(summary.values(), key=lambda item: str(item["category"]))]


def build_profile_overlay(default_go_no_go: dict[str, Any]) -> dict[str, Any]:
    if not COMMERCIAL_PROFILE_JSON_PATH.exists():
        return {
            "overlay_type": "local_commercial_evidence_profile_comparison",
            "profile_overlay_available": False,
            "profile_interpretation": "profile_missing_default_dashboard_only",
        }

    profile = read_json(COMMERCIAL_PROFILE_JSON_PATH)
    profile_env = dict(profile.get("profile_env", {}))
    profile_go_no_go = evaluate_commercial_go_no_go(load_settings(profile_env))
    default_satisfied_ids = {
        row.get("blocker_id")
        for row in default_go_no_go.get("blockers", [])
        if row.get("satisfied") is True
    }
    profile_satisfied_ids = [
        str(row.get("blocker_id"))
        for row in profile_go_no_go.get("blockers", [])
        if row.get("satisfied") is True
    ]
    newly_satisfied_ids = [
        blocker_id
        for blocker_id in profile_satisfied_ids
        if blocker_id not in default_satisfied_ids
    ]
    profile_policy = profile.get("commercial_go_no_go", {})

    return {
        "overlay_type": "local_commercial_evidence_profile_comparison",
        "profile_overlay_available": True,
        "source_profile": rel(COMMERCIAL_PROFILE_JSON_PATH),
        "source_profile_env": rel(COMMERCIAL_PROFILE_ENV_PATH),
        "profile_status": profile.get("profile_status", ""),
        "profile_closes_blockers_by_default": profile.get(
            "profile_closes_blockers_by_default"
        )
        is True,
        "default_production_blocker_count": int(
            default_go_no_go.get("production_blocker_count", 0)
        ),
        "profile_evaluator_production_blocker_count": int(
            profile_go_no_go.get("production_blocker_count", 0)
        ),
        "profile_evaluator_satisfied_production_checks": int(
            profile_go_no_go.get("satisfied_production_checks", 0)
        ),
        "profile_policy_production_blocker_count": int(
            profile_policy.get("production_blocker_count", 0)
        ),
        "profile_policy_blockers_closed_by_profile": int(
            profile_policy.get("blockers_closed_by_profile", 0)
        ),
        "profile_policy_local_public_shell_review_candidate_count": int(
            profile_policy.get("local_public_shell_review_candidate_count", 0)
        ),
        "profile_policy_local_profile_unsatisfied_blocker_count": int(
            profile_policy.get("local_profile_unsatisfied_blocker_count", 0)
        ),
        "satisfied_by_profile_evaluator_ids": profile_satisfied_ids,
        "newly_satisfied_by_profile_evaluator_ids": newly_satisfied_ids,
        "data_operations_combined_profile_integrated": profile.get(
            "data_operations_combined_profile_integrated"
        )
        is True,
        "operations_combined_profile_integrated": profile.get(
            "operations_combined_profile_integrated"
        )
        is True,
        "data_operations_evidence_path": profile.get("data_operations_evidence_path", ""),
        "operations_evidence_path": profile.get("operations_evidence_path", ""),
        "profile_production_ready": profile_go_no_go.get("production_ready") is True,
        "profile_customer_validated": profile_go_no_go.get("customer_validated") is True,
        "profile_product_launched": profile_go_no_go.get("product_launched") is True,
        "profile_private_core_exposed": profile_go_no_go.get("private_core_exposed")
        is True,
        "profile_boundary_violation_count": int(
            profile_go_no_go.get("boundary_violation_count", 0)
        ),
        "profile_interpretation": "review_only_path_profile_not_blocker_closure",
    }


def build_dashboard() -> dict[str, Any]:
    go_no_go = evaluate_commercial_go_no_go(SETTINGS)
    profile_overlay = build_profile_overlay(go_no_go)
    gap_matrix = read_json(GAP_MATRIX_PATH)
    dependency_plan = read_json(DEPENDENCY_PLAN_PATH)
    evidence_packet = read_json(EVIDENCE_PACKET_PATH)
    commercial_status = read_json(COMMERCIAL_STATUS_PATH)
    priority_packets = load_priority_packets()
    phase_rows = build_phase_rows(priority_packets, dependency_plan.get("phases", []))
    blocker_rows = build_blocker_rows(go_no_go, gap_matrix, dependency_plan, priority_packets)
    category_summary = build_category_summary(blocker_rows)
    total_required = int(evidence_packet.get("total_required_evidence_item_count", 0))
    total_local = int(evidence_packet.get("total_local_public_shell_present_count", 0))
    total_missing = int(evidence_packet.get("total_missing_production_evidence_count", 0))

    human_readiness_entrypoints = [
        {
            "step": 1,
            "label": "从这里开始",
            "path": BEGIN_HERE_HTML,
            "purpose": "确认当前商用状态和人工填写顺序。",
            "execution_allowed": False,
        },
        {
            "step": 2,
            "label": "查看工作簿导入批准请求",
            "path": WORKBOOK_IMPORT_APPROVAL_REQUEST_MD,
            "purpose": "确认 64 条人工值已经齐全，但不授权导入。",
            "execution_allowed": False,
        },
        {
            "step": 3,
            "label": "查看 64 条已确认值来源",
            "path": COMPLETION_QUEUE_HTML,
            "purpose": "确认当前缺失值已经清零，仍不关闭任何 blocker。",
            "execution_allowed": False,
        },
        {
            "step": 4,
            "label": "查看导入前 dry run",
            "path": WORKBOOK_IMPORT_DRY_RUN_MD,
            "purpose": "只读检查导入预览；没有单独批准不得执行真实导入。",
            "execution_allowed": False,
        },
        {
            "step": 5,
            "label": "查看导入器边界",
            "path": WORKBOOK_IMPORTER_MD,
            "purpose": "确认导入器当前未被授权执行。",
            "execution_allowed": False,
        },
        {
            "step": 6,
            "label": "查看 64 行完整补证据队列",
            "path": COMPLETION_QUEUE_HTML,
            "purpose": "按 blocker 和 owner lane 查看全部缺失人工值。",
            "execution_allowed": False,
        },
        {
            "step": 7,
            "label": "填后本地验证手册",
            "path": POST_FILL_VALIDATION_RUNBOOK_HTML,
            "purpose": "人工填值后再运行本地 dry run 和守卫。",
            "execution_allowed": False,
        },
        {
            "step": 8,
            "label": "阻塞点关闭准备板",
            "path": CLOSURE_READINESS_BOARD_HTML,
            "purpose": "只用于最终人工审查；当前没有可关闭 blocker。",
            "execution_allowed": False,
        },
    ]

    return {
        "commercial_readiness_dashboard_v0_1": True,
        "dashboard_type": "saee_commercial_readiness_dashboard",
        "dashboard_version": "0.1",
        "status": "commercial_hold_no_launch",
        "dashboard_status": "commercial_hold_no_launch",
        "dashboard_scope": "local_commercial_readiness_review",
        "generated_by": "scripts/saee_commercial_readiness_dashboard.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_dashboard_html": rel(OUTPUT_HTML),
        "local_static_dashboard_html": True,
        "browser_readable_dashboard_entrypoint": True,
        "source_begin_here_html": BEGIN_HERE_HTML,
        "source_review_batch_human_entry_quality_guide_html": REVIEW_BATCH_QUALITY_GUIDE_HTML,
        "source_review_batch_template_preflight_markdown": REVIEW_BATCH_TEMPLATE_PREFLIGHT_MD,
        "source_review_batch_human_fill_card_html": REVIEW_BATCH_FILL_CARD_HTML,
        "source_post_fill_readiness_preview_html": POST_FILL_READINESS_PREVIEW_HTML,
        "source_completion_queue_html": COMPLETION_QUEUE_HTML,
        "source_post_fill_validation_runbook_html": POST_FILL_VALIDATION_RUNBOOK_HTML,
        "source_closure_readiness_board_html": CLOSURE_READINESS_BOARD_HTML,
        "source_quick_fill_review_batch_template_csv": QUICK_FILL_TEMPLATE_CSV,
        "source_workbook_import_approval_request_markdown": WORKBOOK_IMPORT_APPROVAL_REQUEST_MD,
        "source_workbook_import_dry_run_markdown": WORKBOOK_IMPORT_DRY_RUN_MD,
        "source_workbook_importer_markdown": WORKBOOK_IMPORTER_MD,
        "entrypoints": {
            "begin_here_html": BEGIN_HERE_HTML,
            "review_batch_template_preflight_markdown": REVIEW_BATCH_TEMPLATE_PREFLIGHT_MD,
            "review_batch_human_fill_card_html": REVIEW_BATCH_FILL_CARD_HTML,
            "post_fill_readiness_preview_html": POST_FILL_READINESS_PREVIEW_HTML,
            "completion_queue_html": COMPLETION_QUEUE_HTML,
            "post_fill_validation_runbook_html": POST_FILL_VALIDATION_RUNBOOK_HTML,
            "closure_readiness_board_html": CLOSURE_READINESS_BOARD_HTML,
            "quick_fill_review_batch_template_csv": QUICK_FILL_TEMPLATE_CSV,
            "workbook_import_approval_request_markdown": WORKBOOK_IMPORT_APPROVAL_REQUEST_MD,
            "workbook_import_dry_run_markdown": WORKBOOK_IMPORT_DRY_RUN_MD,
            "workbook_importer_markdown": WORKBOOK_IMPORTER_MD,
        },
        "human_readiness_entrypoints": human_readiness_entrypoints,
        "entrypoints": {
            "begin_here_html": BEGIN_HERE_HTML,
            "workbook_import_approval_request_markdown": WORKBOOK_IMPORT_APPROVAL_REQUEST_MD,
            "confirmed_values_source_html": COMPLETION_QUEUE_HTML,
            "workbook_import_dry_run_markdown": WORKBOOK_IMPORT_DRY_RUN_MD,
            "workbook_importer_markdown": WORKBOOK_IMPORTER_MD,
            "completion_queue_html": COMPLETION_QUEUE_HTML,
            "post_fill_validation_runbook_html": POST_FILL_VALIDATION_RUNBOOK_HTML,
            "closure_readiness_board_html": CLOSURE_READINESS_BOARD_HTML,
            "quick_fill_review_batch_template_csv": QUICK_FILL_TEMPLATE_CSV,
        },
        "preferred_template_missing_value_row_count": int(
            commercial_status.get("preferred_template_missing_value_row_count", 0) or 0
        ),
        "full_quick_fill_missing_value_row_count": int(
            commercial_status.get("full_quick_fill_missing_value_row_count", 0) or 0
        ),
        "closure_candidate_count": 0,
        "source_go_no_go": "scripts/saee_commercial_go_no_go.py",
        "source_gap_matrix": rel(GAP_MATRIX_PATH),
        "source_dependency_plan": rel(DEPENDENCY_PLAN_PATH),
        "source_evidence_packet": rel(EVIDENCE_PACKET_PATH),
        "source_commercial_evidence_profile": rel(COMMERCIAL_PROFILE_JSON_PATH),
        "commercial_status": go_no_go.get("commercial_status"),
        "production_launch_status": go_no_go.get("production_launch_status"),
        "production_blocker_count": int(go_no_go.get("production_blocker_count", 0)),
        "open_blocker_count": len([row for row in blocker_rows if row["status"] == "open"]),
        "satisfied_production_checks": int(go_no_go.get("satisfied_production_checks", 0)),
        "total_production_checks": int(go_no_go.get("total_production_checks", 0)),
        "boundary_violation_count": int(go_no_go.get("boundary_violation_count", 0)),
        "total_required_evidence_item_count": total_required,
        "total_local_public_shell_present_count": total_local,
        "total_missing_production_evidence_count": total_missing,
        "local_evidence_ratio": round(total_local / total_required, 4) if total_required else 0.0,
        "blockers_closed_by_dashboard": 0,
        "local_profile_overlay_available": profile_overlay.get(
            "profile_overlay_available"
        )
        is True,
        "profile_evaluator_production_blocker_count": profile_overlay.get(
            "profile_evaluator_production_blocker_count", 0
        ),
        "profile_evaluator_satisfied_production_checks": profile_overlay.get(
            "profile_evaluator_satisfied_production_checks", 0
        ),
        "profile_policy_blockers_closed_by_profile": profile_overlay.get(
            "profile_policy_blockers_closed_by_profile", 0
        ),
        "profile_policy_local_public_shell_review_candidate_count": profile_overlay.get(
            "profile_policy_local_public_shell_review_candidate_count", 0
        ),
        "profile_newly_satisfied_by_evaluator_ids": profile_overlay.get(
            "newly_satisfied_by_profile_evaluator_ids", []
        ),
        "profile_interpretation": profile_overlay.get("profile_interpretation", ""),
        "blockers_ready_to_close": [],
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "next_human_action": (
            "Open the begin-here page and review the workbook import approval request "
            "packet. Do not run workbook import, template transfer, validator execution "
            "on real input, evidence collection, or blocker closure unless a separate "
            "explicit human execution request exists."
        ),
        "phase_summary": phase_rows,
        "category_summary": category_summary,
        "blocker_dashboard": blocker_rows,
        "profile_overlay": profile_overlay,
        "priority_packet_count": len(priority_packets),
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "customer_data_collected": False,
        "customer_data_processed": False,
        "payment_collected": False,
        "revenue_validated": False,
        "production_claim_added": False,
        "launch_claim_added": False,
        "customer_validation_claim_added": False,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, dashboard: dict[str, Any]) -> None:
    fieldnames = [
        "blocker_id",
        "category",
        "phase_id",
        "status",
        "owner_review_lane",
        "required_evidence_item_count",
        "local_public_shell_present_count",
        "missing_production_evidence_count",
        "external_dependency_required",
        "engineering_implementation_required",
        "human_approval_required",
        "closure_allowed_by_dashboard",
        "execution_allowed_by_dashboard",
        "local_evidence_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in dashboard["blocker_dashboard"]:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, dashboard: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Readiness Dashboard v0.1",
        "",
        "Status: commercial_hold_no_launch.",
        "",
        "This dashboard consolidates existing local commercial readiness evidence. It does not execute blocker tasks, collect evidence, contact customers or vendors, launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- commercial_status: {dashboard['commercial_status']}",
        f"- production_launch_status: {dashboard['production_launch_status']}",
        f"- production_blocker_count: {dashboard['production_blocker_count']}",
        f"- open_blocker_count: {dashboard['open_blocker_count']}",
        f"- satisfied_production_checks: {dashboard['satisfied_production_checks']}/{dashboard['total_production_checks']}",
        f"- total_required_evidence_item_count: {dashboard['total_required_evidence_item_count']}",
        f"- total_local_public_shell_present_count: {dashboard['total_local_public_shell_present_count']}",
        f"- total_missing_production_evidence_count: {dashboard['total_missing_production_evidence_count']}",
        f"- local_evidence_ratio: {dashboard['local_evidence_ratio']}",
        f"- blockers_closed_by_dashboard: {dashboard['blockers_closed_by_dashboard']}",
        f"- local_profile_overlay_available: {str(dashboard['local_profile_overlay_available']).lower()}",
        f"- profile_evaluator_production_blocker_count: {dashboard['profile_evaluator_production_blocker_count']}",
        f"- profile_evaluator_satisfied_production_checks: {dashboard['profile_evaluator_satisfied_production_checks']}",
        f"- profile_policy_blockers_closed_by_profile: {dashboard['profile_policy_blockers_closed_by_profile']}",
        f"- profile_policy_local_public_shell_review_candidate_count: {dashboard['profile_policy_local_public_shell_review_candidate_count']}",
        f"- profile_interpretation: {dashboard['profile_interpretation']}",
        f"- preferred_template_missing_value_row_count: {dashboard['preferred_template_missing_value_row_count']}",
        f"- full_quick_fill_missing_value_row_count: {dashboard['full_quick_fill_missing_value_row_count']}",
        f"- closure_candidate_count: {dashboard['closure_candidate_count']}",
        "",
        "## Local Profile Overlay",
        "",
        "The local commercial evidence profile is shown as review context only. It may make a local evaluator projection more specific, but it does not close blockers, authorize evidence collection, or change launch status.",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| source_profile | `{dashboard['profile_overlay'].get('source_profile', '')}` |",
        f"| source_profile_env | `{dashboard['profile_overlay'].get('source_profile_env', '')}` |",
        f"| profile_status | {dashboard['profile_overlay'].get('profile_status', '')} |",
        f"| default_production_blocker_count | {dashboard['profile_overlay'].get('default_production_blocker_count', 0)} |",
        f"| profile_evaluator_production_blocker_count | {dashboard['profile_overlay'].get('profile_evaluator_production_blocker_count', 0)} |",
        f"| profile_evaluator_satisfied_production_checks | {dashboard['profile_overlay'].get('profile_evaluator_satisfied_production_checks', 0)} |",
        f"| newly_satisfied_by_profile_evaluator_ids | {', '.join(dashboard['profile_overlay'].get('newly_satisfied_by_profile_evaluator_ids', [])) or 'none'} |",
        f"| profile_policy_blockers_closed_by_profile | {dashboard['profile_overlay'].get('profile_policy_blockers_closed_by_profile', 0)} |",
        f"| profile_policy_local_public_shell_review_candidate_count | {dashboard['profile_overlay'].get('profile_policy_local_public_shell_review_candidate_count', 0)} |",
        f"| data_operations_combined_profile_integrated | {str(dashboard['profile_overlay'].get('data_operations_combined_profile_integrated', False)).lower()} |",
        f"| operations_combined_profile_integrated | {str(dashboard['profile_overlay'].get('operations_combined_profile_integrated', False)).lower()} |",
        f"| profile_interpretation | {dashboard['profile_overlay'].get('profile_interpretation', '')} |",
        "",
        "## Human Readiness Entrypoints",
        "",
        "Use these browser-readable local surfaces in order. They are review and input aids only; none of them authorizes execution, evidence collection, product launch, customer contact, or blocker closure.",
        "",
        "| Step | Label | Path | Purpose | Execution allowed |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in dashboard["human_readiness_entrypoints"]:
        lines.append(
            "| {step} | {label} | `{path}` | {purpose} | {execution_allowed} |".format(
                **{key: html.escape(str(value), quote=True) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Phase Summary",
            "",
            "| Phase | Target blockers | Required evidence | Local public-shell | Missing production | Closed | Template |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in dashboard["phase_summary"]:
        lines.append(
            "| {phase_id} | {target_blocker_count} | {required_evidence_item_count} | "
            "{local_public_shell_present_count} | {missing_production_evidence_count} | "
            "{blockers_closed_by_collection} | `{priority_template}` |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Category Summary",
            "",
            "| Category | Blockers | Open | Required evidence | Local public-shell | Missing production |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in dashboard["category_summary"]:
        lines.append(
            "| {category} | {blocker_count} | {open_blocker_count} | "
            "{required_evidence_item_count} | {local_public_shell_present_count} | "
            "{missing_production_evidence_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Blocker Dashboard",
            "",
            "| Blocker | Category | Phase | Status | Required | Local | Missing | Owner lane |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in dashboard["blocker_dashboard"]:
        lines.append(
            "| {blocker_id} | {category} | {phase_id} | {status} | "
            "{required_evidence_item_count} | {local_public_shell_present_count} | "
            "{missing_production_evidence_count} | {owner_review_lane} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "- runtime_modified: false",
            "- backend_modified: false",
            "- kernel_modified: false",
            "- api_schema_modified: false",
            "- customer_contacted: false",
            "- external_calls_made: false",
            "- task_candidates_executed: false",
            "- development_permission_granted: false",
            "- execution_authorized: false",
            "- evidence_collection_authorized: false",
            "",
            "## Next Human Action",
            "",
            dashboard["next_human_action"],
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(path: Path, dashboard: dict[str, Any]) -> None:
    def esc(value: object) -> str:
        return html.escape(str(value), quote=True)

    phase_cards = "\n".join(
        """
          <article class="phase-card">
            <p class="eyebrow">{phase_id}</p>
            <h3>第 {phase_number} 阶段</h3>
            <dl>
              <div><dt>阻塞点</dt><dd>{target_blocker_count}</dd></div>
              <div><dt>需要证据</dt><dd>{required_evidence_item_count}</dd></div>
              <div><dt>已占位</dt><dd>{local_public_shell_present_count}</dd></div>
              <div><dt>还缺</dt><dd>{missing_production_evidence_count}</dd></div>
            </dl>
          </article>
        """.format(**{key: esc(value) for key, value in row.items()})
        for row in dashboard["phase_summary"]
    )
    blocker_rows = "\n".join(
        """
          <tr>
            <td>{blocker_id}</td>
            <td>{category}</td>
            <td>{phase_id}</td>
            <td>{status}</td>
            <td>{missing_production_evidence_count}</td>
          </tr>
        """.format(**{key: esc(value) for key, value in row.items()})
        for row in dashboard["blocker_dashboard"]
    )
    category_rows = "\n".join(
        """
          <tr>
            <td>{category}</td>
            <td>{open_blocker_count}</td>
            <td>{required_evidence_item_count}</td>
            <td>{local_public_shell_present_count}</td>
            <td>{missing_production_evidence_count}</td>
          </tr>
        """.format(**{key: esc(value) for key, value in row.items()})
        for row in dashboard["category_summary"]
    )
    entrypoint_cards = "\n".join(
        """
          <article class="entry-card">
            <span>{step}</span>
            <h3>{label}</h3>
            <p>{purpose}</p>
            <code>{path}</code>
          </article>
        """.format(**{key: esc(value) for key, value in row.items()})
        for row in dashboard["human_readiness_entrypoints"]
    )
    html_text = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 商用准备总览</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f8f7f2;
        --surface: #ffffff;
        --soft: #eef3ed;
        --text: #171717;
        --muted: #63675f;
        --line: #deded5;
        --accent: #10a37f;
        --accent-dark: #087a5a;
        --danger: #9f2f24;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: radial-gradient(circle at 80% 0%, rgba(16, 163, 127, 0.12), transparent 32%), var(--bg);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
      }}
      main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0; }}
      .hero {{
        padding: clamp(28px, 5vw, 56px);
        border: 1px solid var(--line);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.86);
        box-shadow: 0 18px 48px rgba(23, 23, 23, 0.08);
      }}
      .eyebrow {{ margin: 0 0 10px; color: var(--accent-dark); font-size: 13px; font-weight: 800; }}
      h1 {{ max-width: 760px; margin: 0; font-size: clamp(36px, 5vw, 64px); line-height: 1.04; letter-spacing: 0; }}
      .lead {{ max-width: 760px; margin: 22px 0 0; color: var(--muted); font-size: 18px; }}
      .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 28px; }}
      .stat, .phase-card, .panel {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
      }}
      .stat {{ padding: 18px; }}
      .stat strong {{ display: block; font-size: 30px; line-height: 1; }}
      .stat span {{ display: block; margin-top: 8px; color: var(--muted); font-size: 13px; }}
      .danger strong {{ color: var(--danger); }}
      section {{ margin-top: 28px; }}
      h2 {{ margin: 0 0 14px; font-size: 28px; line-height: 1.15; }}
      .entry-grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }}
      .entry-card {{
        min-height: 190px;
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
      }}
      .entry-card span {{
        display: inline-grid;
        width: 32px;
        height: 32px;
        place-items: center;
        border-radius: 8px;
        color: #fff;
        background: var(--accent-dark);
        font-weight: 800;
      }}
      .entry-card h3 {{ margin: 14px 0 8px; font-size: 17px; }}
      .entry-card p {{ margin: 0 0 12px; color: var(--muted); font-size: 13px; }}
      .entry-card code {{
        display: block;
        color: var(--accent-dark);
        font-size: 12px;
        overflow-wrap: anywhere;
      }}
      .phase-grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }}
      .phase-card {{ padding: 16px; }}
      .phase-card h3 {{ margin: 0 0 12px; font-size: 17px; }}
      dl {{ display: grid; gap: 8px; margin: 0; }}
      dl div {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; }}
      dt {{ color: var(--muted); font-size: 13px; }}
      dd {{ margin: 0; font-weight: 800; }}
      .panel {{ overflow: hidden; }}
      table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
      th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
      th {{ background: var(--soft); font-size: 13px; }}
      tr:last-child td {{ border-bottom: 0; }}
      .boundary {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; padding: 0; margin: 0; list-style: none; }}
      .boundary li {{ padding: 12px 14px; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); color: var(--muted); }}
      .boundary strong {{ color: var(--text); }}
      .next {{ padding: 18px; border-left: 4px solid var(--accent); background: var(--soft); border-radius: 10px; }}
      code {{ color: var(--accent-dark); }}
      @media (max-width: 900px) {{
        .stats, .entry-grid, .phase-grid, .boundary {{ grid-template-columns: 1fr 1fr; }}
      }}
      @media (max-width: 640px) {{
        main {{ width: min(100% - 24px, 1120px); padding: 24px 0; }}
        .stats, .entry-grid, .phase-grid, .boundary {{ grid-template-columns: 1fr; }}
        table {{ font-size: 12px; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p class="eyebrow">SAEE 商用准备 · 本地总览</p>
        <h1>现在还不能正式商用。</h1>
        <p class="lead">
          这个页面把当前商用阻塞点放在一起，方便人工审查下一步该补什么证据。它不会执行任务，不会联系客户，不会发布产品，也不会关闭阻塞点。
        </p>
        <div class="stats" aria-label="商用准备关键数字">
          <div class="stat danger"><strong>{esc(dashboard['open_blocker_count'])}</strong><span>仍然打开的生产阻塞点</span></div>
          <div class="stat"><strong>{esc(dashboard['total_required_evidence_item_count'])}</strong><span>需要的生产证据项</span></div>
          <div class="stat"><strong>{esc(dashboard['total_local_public_shell_present_count'])}</strong><span>已有本地公开壳证据</span></div>
          <div class="stat danger"><strong>{esc(dashboard['total_missing_production_evidence_count'])}</strong><span>仍缺的生产证据</span></div>
        </div>
      </section>

      <section>
        <h2>下一步商用准备入口</h2>
        <div class="entry-grid">
{entrypoint_cards}
        </div>
      </section>

      <section>
        <h2>五个阶段</h2>
        <div class="phase-grid">
{phase_cards}
        </div>
      </section>

      <section>
        <h2>按类别看缺口</h2>
        <div class="panel">
          <table>
            <thead>
              <tr><th>类别</th><th>打开阻塞点</th><th>需要证据</th><th>已有占位</th><th>仍缺证据</th></tr>
            </thead>
            <tbody>
{category_rows}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>24 个阻塞点</h2>
        <div class="panel">
          <table>
            <thead>
              <tr><th>阻塞点</th><th>类别</th><th>阶段</th><th>状态</th><th>仍缺证据</th></tr>
            </thead>
            <tbody>
{blocker_rows}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>边界</h2>
        <ul class="boundary">
          <li><strong>production_ready:</strong> false</li>
          <li><strong>product_launched:</strong> false</li>
          <li><strong>customer_validated:</strong> false</li>
          <li><strong>private_core_exposed:</strong> false</li>
          <li><strong>execution_authorized:</strong> false</li>
          <li><strong>evidence_collection_authorized:</strong> false</li>
          <li><strong>runtime_modified:</strong> false</li>
          <li><strong>backend_modified:</strong> false</li>
          <li><strong>kernel_modified:</strong> false</li>
        </ul>
      </section>

      <section>
        <h2>下一步</h2>
        <p class="next">{esc(dashboard['next_human_action'])}</p>
      </section>
    </main>
  </body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def write_boundary(path: Path, dashboard: dict[str, Any]) -> None:
    lines = [
        "# Commercial Readiness Dashboard Boundary Audit",
        "",
        "The dashboard is local review infrastructure only.",
        "",
    ]
    for flag in BOUNDARY_FALSE_FLAGS:
        lines.append(f"- {flag}: {str(dashboard[flag]).lower()}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(path: Path, dashboard: dict[str, Any]) -> None:
    path.write_text(
        "\n".join(
            [
                "# SAEE Commercial Readiness Dashboard",
                "",
                "Status: local commercial readiness dashboard, hold, no launch.",
                "",
                "This folder consolidates go/no-go, production blocker, dependency, evidence packet, and Phase 1-5 priority evidence collection status into one review surface.",
                "",
                "It is not an execution queue and does not close blockers.",
                "",
                "Key outputs:",
                "",
                "- `commercial_readiness_dashboard.local.json`",
                "- `commercial_readiness_dashboard.html`",
                "- `commercial_readiness_dashboard.md`",
                "- `commercial_readiness_dashboard.csv`",
                "- `commercial_readiness_dashboard_boundary_audit.md`",
                "",
                "Current status:",
                "",
                f"- commercial_status: {dashboard['commercial_status']}",
                f"- production_launch_status: {dashboard['production_launch_status']}",
                f"- production_blocker_count: {dashboard['production_blocker_count']}",
                f"- open_blocker_count: {dashboard['open_blocker_count']}",
                f"- total_required_evidence_item_count: {dashboard['total_required_evidence_item_count']}",
                f"- total_missing_production_evidence_count: {dashboard['total_missing_production_evidence_count']}",
                "- local_static_dashboard_html: true",
                "- browser_readable_dashboard_entrypoint: true",
                "- blockers_closed_by_dashboard: 0",
                f"- local_profile_overlay_available: {str(dashboard['local_profile_overlay_available']).lower()}",
                f"- profile_evaluator_satisfied_production_checks: {dashboard['profile_evaluator_satisfied_production_checks']}",
                f"- profile_policy_blockers_closed_by_profile: {dashboard['profile_policy_blockers_closed_by_profile']}",
                f"- profile_policy_local_public_shell_review_candidate_count: {dashboard['profile_policy_local_public_shell_review_candidate_count']}",
                f"- source_begin_here_html: `{dashboard['source_begin_here_html']}`",
                f"- source_review_batch_human_entry_quality_guide_html: `{dashboard['source_review_batch_human_entry_quality_guide_html']}`",
                f"- source_review_batch_template_preflight_markdown: `{dashboard['source_review_batch_template_preflight_markdown']}`",
                f"- source_review_batch_human_fill_card_html: `{dashboard['source_review_batch_human_fill_card_html']}`",
                f"- source_post_fill_readiness_preview_html: `{dashboard['source_post_fill_readiness_preview_html']}`",
                f"- source_completion_queue_html: `{dashboard['source_completion_queue_html']}`",
                f"- source_post_fill_validation_runbook_html: `{dashboard['source_post_fill_validation_runbook_html']}`",
                f"- source_closure_readiness_board_html: `{dashboard['source_closure_readiness_board_html']}`",
                f"- preferred_template_missing_value_row_count: {dashboard['preferred_template_missing_value_row_count']}",
                f"- full_quick_fill_missing_value_row_count: {dashboard['full_quick_fill_missing_value_row_count']}",
                f"- closure_candidate_count: {dashboard['closure_candidate_count']}",
                "- production_ready: false",
                "- customer_validated: false",
                "- product_launched: false",
                "- private_core_exposed: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_doc(path: Path, dashboard: dict[str, Any]) -> None:
    path.write_text(
        "\n".join(
            [
                "# SAEE Commercial Readiness Dashboard v0.1",
                "",
                "commercial_readiness_dashboard_v0_1: true",
                "dashboard_scope: local_commercial_readiness_review",
                f"commercial_status: {dashboard['commercial_status']}",
                f"production_launch_status: {dashboard['production_launch_status']}",
                f"production_blocker_count: {dashboard['production_blocker_count']}",
                f"open_blocker_count: {dashboard['open_blocker_count']}",
                f"satisfied_production_checks: {dashboard['satisfied_production_checks']}/{dashboard['total_production_checks']}",
                f"total_required_evidence_item_count: {dashboard['total_required_evidence_item_count']}",
                f"total_local_public_shell_present_count: {dashboard['total_local_public_shell_present_count']}",
                f"total_missing_production_evidence_count: {dashboard['total_missing_production_evidence_count']}",
                "local_static_dashboard_html: true",
                "browser_readable_dashboard_entrypoint: true",
                "blockers_closed_by_dashboard: 0",
                f"local_profile_overlay_available: {str(dashboard['local_profile_overlay_available']).lower()}",
                f"profile_evaluator_production_blocker_count: {dashboard['profile_evaluator_production_blocker_count']}",
                f"profile_evaluator_satisfied_production_checks: {dashboard['profile_evaluator_satisfied_production_checks']}",
                f"profile_policy_blockers_closed_by_profile: {dashboard['profile_policy_blockers_closed_by_profile']}",
                f"profile_policy_local_public_shell_review_candidate_count: {dashboard['profile_policy_local_public_shell_review_candidate_count']}",
                f"profile_interpretation: {dashboard['profile_interpretation']}",
                f"source_begin_here_html: {dashboard['source_begin_here_html']}",
                f"source_review_batch_human_entry_quality_guide_html: {dashboard['source_review_batch_human_entry_quality_guide_html']}",
                f"source_review_batch_template_preflight_markdown: {dashboard['source_review_batch_template_preflight_markdown']}",
                f"source_review_batch_human_fill_card_html: {dashboard['source_review_batch_human_fill_card_html']}",
                f"source_post_fill_readiness_preview_html: {dashboard['source_post_fill_readiness_preview_html']}",
                f"source_completion_queue_html: {dashboard['source_completion_queue_html']}",
                f"source_post_fill_validation_runbook_html: {dashboard['source_post_fill_validation_runbook_html']}",
                f"source_closure_readiness_board_html: {dashboard['source_closure_readiness_board_html']}",
                f"source_quick_fill_review_batch_template_csv: {dashboard['source_quick_fill_review_batch_template_csv']}",
                f"source_workbook_import_approval_request_markdown: {dashboard['source_workbook_import_approval_request_markdown']}",
                f"source_workbook_import_dry_run_markdown: {dashboard['source_workbook_import_dry_run_markdown']}",
                f"source_workbook_importer_markdown: {dashboard['source_workbook_importer_markdown']}",
                f"preferred_template_missing_value_row_count: {dashboard['preferred_template_missing_value_row_count']}",
                "64 条人工确认值已经齐全；下一步只能由人单独批准是否导入工作簿。",
                f"full_quick_fill_missing_value_row_count: {dashboard['full_quick_fill_missing_value_row_count']}",
                f"closure_candidate_count: {dashboard['closure_candidate_count']}",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "execution_authorized: false",
                "evidence_collection_authorized: false",
                "",
                "This dashboard is a local review surface only. It does not execute tasks, collect evidence, contact customers, contact vendors, approve launch, or claim production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_gate(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# SAEE Commercial Readiness Dashboard Recommendation Gate",
                "",
                "answer: conditional",
                "recommend_for_local_commercial_review: true",
                "recommend_for_human_readiness_triage: true",
                "recommend_for_production_readiness_claim: false",
                "recommend_for_customer_validation_claim: false",
                "recommend_for_product_launch: false",
                "recommend_for_automatic_execution: false",
                "recommend_for_evidence_collection_authorization: false",
                "recommend_for_blocker_closure: false",
                "",
                "Reason: the dashboard improves commercial review visibility but does not provide missing production evidence or authorize execution.",
                "",
                "Boundary:",
                "",
                "- runtime_modified: false",
                "- backend_modified: false",
                "- kernel_modified: false",
                "- api_schema_modified: false",
                "- private_core_exposed: false",
                "- production_ready: false",
                "- customer_validated: false",
                "- product_launched: false",
                "- customer_contacted: false",
                "- external_calls_made: false",
                "- task_candidates_executed: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_outputs(dashboard: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_JSON, dashboard)
    write_csv(OUTPUT_CSV, dashboard)
    write_html(OUTPUT_HTML, dashboard)
    write_markdown(OUTPUT_MD, dashboard)
    write_boundary(OUTPUT_BOUNDARY, dashboard)
    write_readme(README_PATH, dashboard)
    write_doc(DOC_PATH, dashboard)
    write_gate(GATE_PATH)


def main() -> None:
    dashboard = build_dashboard()
    write_outputs(dashboard)
    print(
        "SAEE_COMMERCIAL_READINESS_DASHBOARD: PASS "
        f"production_blockers={dashboard['production_blocker_count']} "
        f"open_blockers={dashboard['open_blocker_count']} "
        f"required_evidence={dashboard['total_required_evidence_item_count']} "
        f"missing_production={dashboard['total_missing_production_evidence_count']} "
        f"blockers_closed_by_dashboard={dashboard['blockers_closed_by_dashboard']}"
    )


if __name__ == "__main__":
    main()
