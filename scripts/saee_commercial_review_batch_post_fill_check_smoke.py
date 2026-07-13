#!/usr/bin/env python3
"""Smoke test for the commercial review batch post-fill check."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_check.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_post_fill_check.md"
OUT_BOUNDARY = SPRINT_DIR / "commercial_review_batch_post_fill_check_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK_RECOMMENDATION_GATE.md"
SOURCE_TEMPLATE = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/saee_commercial_review_batch_post_fill_check.py"],
        cwd=ROOT,
        check=True,
    )
    for path in [OUT_JSON, OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE, SOURCE_TEMPLATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    with SOURCE_TEMPLATE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    require(payload["commercial_review_batch_post_fill_check_v0_1"] is True, "marker false")
    require(payload["check_type"] == "local_10_row_post_fill_readiness_wrapper", "wrong check type")
    require(payload["review_batch_row_count"] == 0, "review batch row count should be zero after supersession")
    require(payload["missing_human_value_row_count"] == 0, "superseded template should have no missing rows")
    require(payload["filled_human_value_row_count"] == 0, "current template should have no values")
    require(
        payload["status"] == "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "current status should show superseded route",
    )
    require(payload["human_input_required"] is False, "human input should not be required for superseded template")
    require(payload["review_batch_route_superseded"] is True, "route should be superseded")
    require(payload["ready_for_workbook_import_approval_review"] is True, "should point to approval review")
    require(payload["quality_lint_enabled"] is True, "quality lint must be enabled")
    require(
        payload["quality_lint_scope"] == "local_boundary_shape_lint_no_raw_values",
        "wrong quality lint scope",
    )
    require(payload["quality_lint_issue_count"] == 0, "current blank template has lint issues")
    require(payload["quality_lint_issues"] == [], "current blank template lint issue list")
    require(payload["forbidden_claim_lint_passed"] is True, "forbidden claim lint must pass")
    require(payload["shape_lint_passed"] is True, "shape lint must pass")
    require(
        payload["ready_for_quality_safe_post_fill_dry_run"] is False,
        "quality-safe dry run must wait for values",
    )
    require(payload["ready_to_run_post_fill_e2e_dry_run"] is False, "must not be e2e ready yet")
    require(payload["post_fill_e2e_dry_run_executed"] is False, "must not run e2e with missing values")
    require(payload["boundary_violation_count"] == 0, "boundary violation count")
    require(payload["blockers_closed_by_check"] == 0, "blocker closure count")
    for row in rows:
        require(row.get("human_value_to_enter", "") == "", "source template value was filled")

    false_flags = [
        "values_generated_by_codex",
        "human_values_filled_by_codex",
        "raw_values_recorded",
        "workbook_import_performed",
        "evidence_collection_authorized",
        "blocker_closure_authorized",
        "blockers_closed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "customer_contacted",
        "customer_validated",
        "product_launched",
        "production_ready",
        "production_ready_claim",
    ]
    for flag in false_flags:
        require(payload.get(flag) is False, f"{flag} must be false")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "SAEE 10 行填写后本地检查",
        "commercial_review_batch_post_fill_check_v0_1: true",
        "status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "quality_lint_enabled: true",
        "quality_lint_issue_count: 0",
        "forbidden_claim_lint_passed: true",
        "shape_lint_passed: true",
        "ready_for_quality_safe_post_fill_dry_run: false",
        "review_batch_route_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "完整 quick-fill 值已进入 workbook import approval review 状态",
        "不生成真实人工值",
        "不把人工填写原文写进 lint 输出",
        "会拦截生产可用、客户验证、外部验证、公开私有核心等危险表述",
        "不导入工作簿",
        "不关闭 blocker",
        "recommend_for_local_post_fill_check: true",
        "recommend_for_boundary_shape_lint: true",
        "recommend_for_workbook_import: false",
        "production_ready: false",
    ]
    for token in required_tokens:
        require(token in combined, f"missing token {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "workbook_import_performed: true",
        '"workbook_import_performed": true',
    ]
    for token in forbidden_tokens:
        require(token not in combined, f"forbidden token {token}")

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK_SMOKE: PASS "
        f"status={payload['status']} "
        f"missing={payload['missing_human_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
