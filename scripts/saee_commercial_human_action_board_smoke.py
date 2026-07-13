#!/usr/bin/env python3
"""Smoke check for the SAEE commercial human action board."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.local.json"
)
REPORT_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.md"
)
CSV_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.csv"
)
HTML_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.html"
)
BOUNDARY_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board_boundary_audit.md"
)
README_PATH = ROOT / "phase_b_product/commercial_readiness/commercial_human_action_board/README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_HUMAN_ACTION_BOARD_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_HUMAN_ACTION_BOARD_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_HUMAN_ACTION_BOARD_SMOKE: FAIL " + message)


def main() -> int:
    for path in [
        BOARD_PATH,
        REPORT_PATH,
        CSV_PATH,
        HTML_PATH,
        BOUNDARY_PATH,
        README_PATH,
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    board = json.loads(BOARD_PATH.read_text(encoding="utf-8"))
    expected_flags = {
        "board_type": "saee_commercial_human_action_board",
        "board_status": "hold_human_action_required",
        "board_scope": "local_commercial_human_action_review",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "total_required_evidence_item_count": 149,
        "total_local_public_shell_present_count": 37,
        "total_missing_production_evidence_count": 112,
        "source_human_action_board_html": "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.html",
        "local_static_human_action_board_html": True,
        "browser_readable_human_action_board": True,
        "blockers_closed_by_board": 0,
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
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
    for key, value in expected_flags.items():
        require(board.get(key) == value, f"{key} must be {value}")

    actions = board.get("action_rows", [])
    require(len(actions) == 24, "expected 24 action rows")
    require(board.get("ready_for_human_review_blocker_count", 0) > 0, "expected ready rows")
    require(board.get("blocked_by_dependency_blocker_count", 0) > 0, "expected blocked rows")
    require(board.get("active_sprint_blocker_count") == 5, "expected five active sprint blockers")
    require(
        board.get("active_sprint_ready_action_count") == 5,
        "expected five active sprint ready actions",
    )
    require(
        board.get("active_sprint_missing_value_row_count") == 64,
        "expected 64 active sprint missing values",
    )
    require(len(board.get("owner_lane_summary", [])) >= 5, "expected owner lane summary")
    require(board.get("blockers_ready_to_close") == [], "no blockers ready to close")
    active_rows = board.get("active_sprint_action_rows", [])
    require(len(active_rows) == 5, "expected five active sprint action rows")
    require(
        {row.get("blocker_id") for row in active_rows}
        == {
            "formal_security_review",
            "pricing_page",
            "production_monitoring",
            "production_restore_policy",
            "support_contact",
        },
        "active sprint blocker ids drifted",
    )
    for row in active_rows:
        require(
            row.get("dependency_state") == "ready_for_human_review",
            "active sprint rows must be ready for human review",
        )
        require(row.get("execution_allowed_by_board") is False, "active execution false")
        require(row.get("evidence_collection_authorized") is False, "active evidence false")
        require(row.get("closure_allowed_by_board") is False, "active closure false")
    for row in actions:
        require(row.get("status") == "open", "action row must keep blocker open")
        require(row.get("requires_human_approval") is True, "action row must require human approval")
        require(
            row.get("requires_separate_execution_request") is True,
            "action row must require separate execution request",
        )
        require(row.get("execution_allowed_by_board") is False, "execution must be false")
        require(row.get("closure_allowed_by_board") is False, "closure must be false")
        require(row.get("default_decision") == "hold", "default decision must be hold")
        require(row.get("first_evidence_items"), "each blocker should show evidence samples")

    report = REPORT_PATH.read_text(encoding="utf-8")
    gate = GATE_PATH.read_text(encoding="utf-8")
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    csv_text = CSV_PATH.read_text(encoding="utf-8")
    html_text = HTML_PATH.read_text(encoding="utf-8")
    for token in [
        "Status: hold_human_action_required.",
        "active_sprint_blocker_count: 5",
        "active_sprint_ready_action_count: 5",
        "active_sprint_missing_value_row_count: 64",
        "local_static_human_action_board_html: true",
        "browser_readable_human_action_board: true",
        "source_human_action_board_html: phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.html",
        "blockers_closed_by_board: 0",
        "execution_authorized: false",
        "production_ready: false",
        "Active Sprint Ready Actions",
        "support_contact",
        "production_monitoring",
    ]:
        require(token in report, f"report missing {token}")
    for token in [
        "SAEE 商用人工动作板",
        "先把能人工处理的阻塞项排清楚",
        "当前 sprint：先处理这 5 项",
        "支持联系人（support_contact）",
        "生产监控（production_monitoring）",
        "商业、财务与法务",
        "production_ready:</strong> false",
        "execution_authorized:</strong> false",
        "evidence_collection_authorized:</strong> false",
        "blockers_closed_by_board:</strong> 0",
    ]:
        require(token in html_text, f"HTML missing {token}")
    for token in ["<script", "fetch(", "XMLHttpRequest", "http://", "https://", "mailto:"]:
        require(token not in html_text, f"HTML contains forbidden token {token}")
    for token in [
        "recommend_for_human_action_triage: true",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "local_static_human_action_board_html: true",
        "source_human_action_board_html: phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.html",
    ]:
        require(token in gate, f"gate missing {token}")
    for token in [
        "task_candidates_executed: false",
        "blockers_closed_by_board: 0",
        "Final boundary decision: local human-action planning only.",
    ]:
        require(token in boundary, f"boundary missing {token}")
    require(len(csv_text.strip().splitlines()) == 25, "CSV must contain header plus 24 rows")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "execution_authorized: true",
        '"execution_authorized": true',
        "evidence_collection_authorized: true",
        '"evidence_collection_authorized": true',
        "recommend_for_automatic_execution: true",
        "recommend_for_blocker_closure: true",
    ]
    combined = "\n".join(
        [report, gate, boundary, html_text, README_PATH.read_text(encoding="utf-8")]
    )
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claims present: " + ", ".join(found))

    print(
        "SAEE_COMMERCIAL_HUMAN_ACTION_BOARD_SMOKE: PASS "
        f"open_blockers={board['open_blocker_count']} "
        f"ready_for_human_review={board['ready_for_human_review_blocker_count']} "
        f"blockers_closed_by_board={board['blockers_closed_by_board']} "
        f"production_ready={str(board['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
