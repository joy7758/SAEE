#!/usr/bin/env python3
"""Smoke check for the SAEE commercial readiness dashboard."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_dashboard"
OUTPUT_JSON = OUTPUT_DIR / "commercial_readiness_dashboard.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_readiness_dashboard.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_readiness_dashboard.csv"
OUTPUT_HTML = OUTPUT_DIR / "commercial_readiness_dashboard.html"
OUTPUT_BOUNDARY = OUTPUT_DIR / "commercial_readiness_dashboard_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_READINESS_DASHBOARD_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_DASHBOARD_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    print(f"SAEE_COMMERCIAL_READINESS_DASHBOARD_SMOKE: FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [
        OUTPUT_JSON,
        OUTPUT_MD,
        OUTPUT_CSV,
        OUTPUT_HTML,
        OUTPUT_BOUNDARY,
        README_PATH,
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    dashboard = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    require(
        dashboard.get("dashboard_type") == "saee_commercial_readiness_dashboard",
        "wrong dashboard type",
    )
    require(dashboard.get("dashboard_version") == "0.1", "wrong dashboard version")
    require(dashboard.get("dashboard_status") == "commercial_hold_no_launch", "wrong status")
    require(
        dashboard.get("dashboard_scope") == "local_commercial_readiness_review",
        "wrong scope",
    )
    expected_values = {
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "satisfied_production_checks": 0,
        "total_production_checks": 24,
        "boundary_violation_count": 0,
        "total_required_evidence_item_count": 149,
        "total_local_public_shell_present_count": 37,
        "total_missing_production_evidence_count": 112,
        "source_dashboard_html": "phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.html",
        "local_static_dashboard_html": True,
        "browser_readable_dashboard_entrypoint": True,
        "source_begin_here_html": "phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html",
        "source_review_batch_human_entry_quality_guide_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_entry_quality_guide.html",
        "source_review_batch_template_preflight_markdown": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.md",
        "source_review_batch_human_fill_card_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.html",
        "source_post_fill_readiness_preview_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_readiness_preview.html",
        "source_completion_queue_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.html",
        "source_post_fill_validation_runbook_html": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_validation_runbook.html",
        "source_closure_readiness_board_html": "phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.html",
        "source_quick_fill_review_batch_template_csv": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.csv",
        "source_workbook_import_approval_request_markdown": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_approval_request_packet.md",
        "source_workbook_import_dry_run_markdown": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_workbook_import_dry_run.md",
        "source_workbook_importer_markdown": "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_workbook_importer.md",
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "closure_candidate_count": 0,
        "blockers_closed_by_dashboard": 0,
        "blockers_ready_to_close": [],
        "local_profile_overlay_available": True,
        "profile_evaluator_production_blocker_count": 23,
        "profile_evaluator_satisfied_production_checks": 1,
        "profile_policy_blockers_closed_by_profile": 0,
        "profile_policy_local_public_shell_review_candidate_count": 1,
        "profile_interpretation": "review_only_path_profile_not_blocker_closure",
        "priority_packet_count": 5,
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
    }
    for key, expected in expected_values.items():
        require(dashboard.get(key) == expected, f"{key} drifted")
    entrypoints = dashboard.get("human_readiness_entrypoints", [])
    require(len(entrypoints) == 8, "must contain eight human readiness entrypoints")
    require(
        [entry.get("step") for entry in entrypoints] == [1, 2, 3, 4, 5, 6, 7, 8],
        "human readiness entrypoint order changed",
    )
    require(
        all(entry.get("execution_allowed") is False for entry in entrypoints),
        "human readiness entrypoints must not allow execution",
    )
    require(
        [entry.get("path") for entry in entrypoints]
        == [
            expected_values["source_begin_here_html"],
            expected_values["source_workbook_import_approval_request_markdown"],
            expected_values["source_completion_queue_html"],
            expected_values["source_workbook_import_dry_run_markdown"],
            expected_values["source_workbook_importer_markdown"],
            expected_values["source_completion_queue_html"],
            expected_values["source_post_fill_validation_runbook_html"],
            expected_values["source_closure_readiness_board_html"],
        ],
        "human readiness entrypoint paths changed",
    )

    false_flags = [
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
        "customer_data_collected",
        "customer_data_processed",
        "payment_collected",
        "revenue_validated",
        "production_claim_added",
        "launch_claim_added",
        "customer_validation_claim_added",
    ]
    drifted = [flag for flag in false_flags if dashboard.get(flag) is not False]
    require(not drifted, "boundary flags drifted: " + ", ".join(drifted))

    phase_summary = dashboard.get("phase_summary", [])
    require(len(phase_summary) == 5, "must contain five phase rows")
    require(
        [row.get("phase_number") for row in phase_summary] == [1, 2, 3, 4, 5],
        "phase order changed",
    )
    expected_phase_counts = [
        (33, 16, 17),
        (26, 8, 18),
        (45, 10, 35),
        (33, 2, 31),
        (12, 1, 11),
    ]
    for row, expected in zip(phase_summary, expected_phase_counts, strict=True):
        require(
            (
                row.get("required_evidence_item_count"),
                row.get("local_public_shell_present_count"),
                row.get("missing_production_evidence_count"),
            )
            == expected,
            f"phase {row.get('phase_number')} counts drifted",
        )
        require(row.get("blockers_closed_by_collection") == 0, "phase closed blocker")
        require(row.get("execution_authorized") is False, "phase authorized execution")
        require(
            row.get("evidence_collection_authorized") is False,
            "phase authorized collection",
        )

    blocker_rows = dashboard.get("blocker_dashboard", [])
    require(len(blocker_rows) == 24, "must contain 24 blocker rows")
    require(all(row.get("status") == "open" for row in blocker_rows), "all blockers must remain open")
    require(
        all(row.get("closure_allowed_by_dashboard") is False for row in blocker_rows),
        "dashboard must not allow closure",
    )
    require(
        all(row.get("execution_allowed_by_dashboard") is False for row in blocker_rows),
        "dashboard must not allow execution",
    )
    require(
        sum(int(row.get("required_evidence_item_count", 0)) for row in blocker_rows) == 149,
        "blocker required evidence total mismatch",
    )
    require(
        sum(int(row.get("local_public_shell_present_count", 0)) for row in blocker_rows)
        == 37,
        "blocker local evidence total mismatch",
    )
    require(
        sum(int(row.get("missing_production_evidence_count", 0)) for row in blocker_rows)
        == 112,
        "blocker missing evidence total mismatch",
    )
    require(len(dashboard.get("category_summary", [])) == 8, "must contain 8 categories")
    profile_overlay = dashboard.get("profile_overlay", {})
    require(
        profile_overlay.get("profile_overlay_available") is True,
        "profile overlay must be available",
    )
    require(
        profile_overlay.get("profile_evaluator_production_blocker_count") == 23,
        "profile evaluator blocker count must show local profile projection",
    )
    require(
        profile_overlay.get("profile_evaluator_satisfied_production_checks") == 1,
        "profile evaluator must satisfy one local-profile check",
    )
    require(
        profile_overlay.get("newly_satisfied_by_profile_evaluator_ids") == ["restore_tested"],
        "profile overlay must identify restore_tested as the only local evaluator change",
    )
    require(
        profile_overlay.get("profile_policy_blockers_closed_by_profile") == 0,
        "profile policy must close zero blockers",
    )
    require(
        profile_overlay.get("profile_policy_local_public_shell_review_candidate_count") == 1,
        "profile policy must record one local public-shell review candidate",
    )
    require(
        profile_overlay.get("data_operations_combined_profile_integrated") is True,
        "data operations combined profile must be integrated",
    )
    require(
        profile_overlay.get("operations_combined_profile_integrated") is True,
        "operations combined profile must be integrated",
    )
    for flag in [
        "profile_production_ready",
        "profile_customer_validated",
        "profile_product_launched",
        "profile_private_core_exposed",
    ]:
        require(profile_overlay.get(flag) is False, f"{flag} must remain false")
    require(
        profile_overlay.get("profile_boundary_violation_count") == 0,
        "profile overlay must have no boundary violations",
    )

    with OUTPUT_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 24, "CSV must contain 24 rows")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUTPUT_MD, OUTPUT_HTML, OUTPUT_BOUNDARY, README_PATH, DOC_PATH, GATE_PATH]
    )
    required_phrases = [
        "SAEE 商用准备总览",
        "现在还不能正式商用。",
        "这个页面把当前商用阻塞点放在一起",
        "commercial_readiness_dashboard_v0_1: true",
        "dashboard_scope: local_commercial_readiness_review",
        "production_blocker_count: 24",
        "open_blocker_count: 24",
        "total_required_evidence_item_count: 149",
        "total_local_public_shell_present_count: 37",
        "total_missing_production_evidence_count: 112",
        "local_static_dashboard_html: true",
        "browser_readable_dashboard_entrypoint: true",
        "source_begin_here_html:",
        "source_review_batch_human_entry_quality_guide_html:",
        "source_review_batch_template_preflight_markdown:",
        "source_review_batch_human_fill_card_html:",
        "source_post_fill_readiness_preview_html:",
        "source_completion_queue_html:",
        "source_post_fill_validation_runbook_html:",
        "source_closure_readiness_board_html:",
        "source_workbook_import_approval_request_markdown:",
        "source_workbook_import_dry_run_markdown:",
        "source_workbook_importer_markdown:",
        "preferred_template_missing_value_row_count: 0",
        "full_quick_fill_missing_value_row_count: 0",
        "closure_candidate_count: 0",
        "Human Readiness Entrypoints",
        "从这里开始",
        "查看工作簿导入批准请求",
        "查看 64 条已确认值来源",
        "查看导入前 dry run",
        "查看导入器边界",
        "查看 64 行完整补证据队列",
        "填后本地验证手册",
        "阻塞点关闭准备板",
        "blockers_closed_by_dashboard: 0",
        "local_profile_overlay_available: true",
        "profile_evaluator_production_blocker_count: 23",
        "profile_evaluator_satisfied_production_checks: 1",
        "profile_policy_blockers_closed_by_profile: 0",
        "profile_policy_local_public_shell_review_candidate_count: 1",
        "profile_interpretation: review_only_path_profile_not_blocker_closure",
        "newly_satisfied_by_profile_evaluator_ids | restore_tested",
        "operations_combined_profile_integrated | true",
        "recommend_for_local_commercial_review: true",
        "recommend_for_production_readiness_claim: false",
        "recommend_for_product_launch: false",
        "recommend_for_automatic_execution: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "task_candidates_executed: false",
        "development_permission_granted: false",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in combined]
    require(not missing, "missing dashboard phrases: " + ", ".join(missing))

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "task_candidates_executed: true",
        '"task_candidates_executed": true',
        "development_permission_granted: true",
        '"development_permission_granted": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "recommend_for_product_launch: true",
        "recommend_for_production_readiness_claim: true",
        "recommend_for_automatic_execution: true",
        "recommend_for_evidence_collection_authorization: true",
        "recommend_for_blocker_closure: true",
        "blockers_closed_by_dashboard: 1",
        '"blockers_closed_by_dashboard": 1',
        "open_blocker_count: 0",
        '"open_blocker_count": 0',
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "mailto:",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_COMMERCIAL_READINESS_DASHBOARD_SMOKE: PASS")


if __name__ == "__main__":
    main()
