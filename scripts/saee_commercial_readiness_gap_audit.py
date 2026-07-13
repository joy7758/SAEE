#!/usr/bin/env python3
"""Audit the remaining gap between current SAEE state and formal commercial use.

This is a local truth-surface generator. It reads existing commercial readiness
profiles and summarizes why SAEE is not yet ready for formal commercial launch.
It does not fill human values, import workbooks, collect evidence, close
blockers, contact customers, modify runtime/backend/kernel/API schema, launch
product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"
OUT_DIR = COMMERCIAL_DIR / "commercial_readiness_gap_audit"

STATUS_JSON = COMMERCIAL_DIR / "commercial_readiness_status.local.json"
GO_NO_GO_JSON = COMMERCIAL_DIR / "commercial_go_no_go.local.json"
GAP_MATRIX_JSON = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"
ACTIVE_BOARD_JSON = SPRINT_DIR / "commercial_sprint_active_human_input_board.local.json"
NEXT_ACTION_JSON = (
    COMMERCIAL_DIR / "commercial_next_action_summary/commercial_next_action_summary.local.json"
)
POST_FILL_CHECK_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_check.local.json"
REVIEW_BATCH_TEMPLATE_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)

OUT_JSON = OUT_DIR / "commercial_readiness_gap_audit.local.json"
OUT_MD = OUT_DIR / "commercial_readiness_gap_audit.md"
OUT_CSV = OUT_DIR / "commercial_readiness_gap_audit.csv"
OUT_BOUNDARY = OUT_DIR / "commercial_readiness_gap_audit_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_READINESS_GAP_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_GAP_AUDIT_RECOMMENDATION_GATE.md"

FALSE_FLAGS = [
    "production_ready",
    "formal_commercial_ready",
    "ready_for_customer_push",
    "ready_for_paid_customer",
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
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def build_payload() -> dict[str, Any]:
    status = read_json(STATUS_JSON)
    go_no_go = read_json(GO_NO_GO_JSON)
    gap_matrix = read_json(GAP_MATRIX_JSON)
    active_board = read_json(ACTIVE_BOARD_JSON)
    next_action = read_json(NEXT_ACTION_JSON)
    post_fill = read_json(POST_FILL_CHECK_JSON)
    review_rows = read_csv_rows(REVIEW_BATCH_TEMPLATE_CSV)

    matrix_rows = gap_matrix.get("matrix", [])
    blockers = go_no_go.get("blockers", [])
    open_blockers = [row for row in matrix_rows if row.get("status") == "open"]
    category_counts = Counter(str(row.get("category", "unknown")) for row in open_blockers)
    owner_lane_counts = Counter(
        str(row.get("owner_review_lane", "unknown")) for row in open_blockers
    )
    local_ready_count = sum(1 for row in open_blockers if row.get("local_evidence_ready") is True)
    partial_local_count = sum(
        1
        for row in open_blockers
        if int(row.get("local_completion_checks_passed", 0) or 0) > 0
        and row.get("local_evidence_ready") is not True
    )
    engineering_required_count = sum(
        1 for row in open_blockers if row.get("engineering_implementation_required") is True
    )
    external_dependency_count = sum(
        1 for row in open_blockers if row.get("external_dependency_required") is True
    )
    human_approval_count = sum(
        1 for row in open_blockers if row.get("human_approval_required") is True
    )

    review_batch_filled_count = sum(
        1 for row in review_rows if row.get("human_value_to_enter", "").strip()
    )
    review_batch_missing_count = len(review_rows) - review_batch_filled_count

    source_payloads = {
        "status": status,
        "go_no_go": go_no_go,
        "gap_matrix": gap_matrix,
        "active_board": active_board,
        "next_action": next_action,
        "post_fill_check": post_fill,
    }
    source_allowed_true_flags = {
        "status": {"validators_run_on_real_input"},
        "next_action": {"validators_run_on_real_input"},
    }
    boundary_violations: list[str] = []
    for source_name, payload in source_payloads.items():
        for flag in FALSE_FLAGS:
            if flag in source_allowed_true_flags.get(source_name, set()):
                continue
            if payload.get(flag) is True:
                boundary_violations.append(f"{source_name}:{flag}_true")
        if int(payload.get("boundary_violation_count", 0) or 0) > 0:
            boundary_violations.append(f"{source_name}:boundary_violation_count_nonzero")

    post_fill_quality_lint_enabled = post_fill.get("quality_lint_enabled") is True
    post_fill_quality_lint_issue_count = int(
        post_fill.get("quality_lint_issue_count", 0) or 0
    )
    post_fill_forbidden_claim_lint_passed = (
        post_fill.get("forbidden_claim_lint_passed") is True
    )
    post_fill_shape_lint_passed = post_fill.get("shape_lint_passed") is True
    post_fill_ready_for_quality_safe_dry_run = (
        post_fill.get("ready_for_quality_safe_post_fill_dry_run") is True
    )

    if boundary_violations:
        audit_status = "stop_boundary_violation"
    elif (
        post_fill_quality_lint_issue_count > 0
        or post_fill_forbidden_claim_lint_passed is False
        or post_fill_shape_lint_passed is False
    ):
        audit_status = "stop_post_fill_quality_lint_issue"
    elif open_blockers:
        audit_status = "hold_formal_commercial_requirements_unmet"
    else:
        audit_status = "pass_ready_for_separate_formal_go_no_go_review"

    blocker_rows = []
    for row in open_blockers:
        blocker_rows.append(
            {
                "blocker_id": row.get("blocker_id"),
                "category": row.get("category"),
                "owner_review_lane": row.get("owner_review_lane"),
                "local_completion_checks_passed": row.get("local_completion_checks_passed", 0),
                "local_completion_checks_total": row.get("local_completion_checks_total", 0),
                "local_evidence_ready": row.get("local_evidence_ready") is True,
                "engineering_implementation_required": row.get(
                    "engineering_implementation_required"
                )
                is True,
                "external_dependency_required": row.get("external_dependency_required") is True,
                "human_approval_required": row.get("human_approval_required") is True,
                "closure_allowed_by_audit": False,
                "required_evidence": row.get("required_evidence", ""),
                "next_required_action": row.get("next_required_action", ""),
            }
        )

    payload: dict[str, Any] = {
        "commercial_readiness_gap_audit_v0_1": True,
        "audit_type": "formal_commercial_readiness_gap_audit",
        "audit_scope": "local_evidence_gap_audit_no_execution_no_closure",
        "status": audit_status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_readiness_gap_audit.py",
        "make_target": "make check-commercial-readiness-gap-audit",
        "formal_commercial_ready": False,
        "ready_for_customer_push": False,
        "ready_for_paid_customer": False,
        "would_recommend_for_paid_customer_today": False,
        "production_blocker_count": int(go_no_go.get("production_blocker_count", 0) or 0),
        "open_blocker_count": len(open_blockers),
        "go_no_go_blocker_count": len([b for b in blockers if not b.get("satisfied")]),
        "local_evidence_ready_blocker_count": local_ready_count,
        "partial_local_evidence_blocker_count": partial_local_count,
        "engineering_implementation_required_count": engineering_required_count,
        "external_dependency_required_count": external_dependency_count,
        "human_approval_required_count": human_approval_count,
        "category_counts": dict(sorted(category_counts.items())),
        "owner_review_lane_counts": dict(sorted(owner_lane_counts.items())),
        "human_input_missing_value_row_count": int(
            status.get("missing_value_row_count", 0) or 0
        ),
        "preferred_template_missing_value_row_count": int(
            status.get("preferred_template_missing_value_row_count", 0) or 0
        ),
        "review_batch_row_count": len(review_rows),
        "review_batch_filled_value_row_count": review_batch_filled_count,
        "review_batch_missing_value_row_count": review_batch_missing_count,
        "post_fill_check_status": post_fill.get("status"),
        "post_fill_check_ready_to_run": post_fill.get("ready_to_run_post_fill_e2e_dry_run")
        is True,
        "post_fill_quality_lint_enabled": post_fill_quality_lint_enabled,
        "post_fill_quality_lint_scope": post_fill.get("quality_lint_scope", ""),
        "post_fill_quality_lint_issue_count": post_fill_quality_lint_issue_count,
        "post_fill_forbidden_claim_lint_passed": post_fill_forbidden_claim_lint_passed,
        "post_fill_shape_lint_passed": post_fill_shape_lint_passed,
        "post_fill_ready_for_quality_safe_dry_run": post_fill_ready_for_quality_safe_dry_run,
        "next_human_action": status.get("next_human_action"),
        "primary_blocker_path": "fill_10_row_review_batch_then_post_fill_local_check",
        "primary_local_command_after_human_fill": (
            "python3 scripts/saee_commercial_review_batch_post_fill_check.py"
        ),
        "allowed_local_actions": [
            "read current commercial gap audit",
            "fill human_value_to_enter rows manually",
            "rerun local post-fill check after human values exist",
            "run local smoke and mainline guard",
        ],
        "forbidden_actions": [
            "generate or infer human evidence values",
            "import workbook without separate human approval",
            "collect external evidence without separate approval",
            "close blockers from this audit",
            "contact customers or vendors",
            "launch product",
            "claim production readiness or customer validation",
        ],
        "blockers_closed_by_audit": 0,
        "accepted_for_blocker_closure_count": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(set(boundary_violations)),
        "source_status_json": rel(STATUS_JSON),
        "source_go_no_go_json": rel(GO_NO_GO_JSON),
        "source_gap_matrix_json": rel(GAP_MATRIX_JSON),
        "source_active_board_json": rel(ACTIVE_BOARD_JSON),
        "source_next_action_json": rel(NEXT_ACTION_JSON),
        "source_post_fill_check_json": rel(POST_FILL_CHECK_JSON),
        "source_review_batch_template_csv": rel(REVIEW_BATCH_TEMPLATE_CSV),
        "blocker_rows": blocker_rows,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "category",
        "owner_review_lane",
        "local_completion_checks_passed",
        "local_completion_checks_total",
        "local_evidence_ready",
        "engineering_implementation_required",
        "external_dependency_required",
        "human_approval_required",
        "closure_allowed_by_audit",
        "required_evidence",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["blocker_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(payload: dict[str, Any]) -> None:
    category_lines = [
        f"- {category}: {count}" for category, count in payload["category_counts"].items()
    ]
    top_blocker_lines = []
    for row in payload["blocker_rows"][:10]:
        top_blocker_lines.append(
            "- `{blocker_id}` ({category}): {required_evidence}".format(**row)
        )
    lines = [
        "# SAEE 正式商用差距审计",
        "",
        "Commercial Readiness Gap Audit v0.1",
        "",
        "结论：当前不能正式商用。这个审计只说明还缺什么，不执行任何候选任务。",
        "",
        "```text",
        "commercial_readiness_gap_audit_v0_1: true",
        f"status: {payload['status']}",
        "commercial_status: hold",
        "formal_commercial_ready: false",
        "ready_for_customer_push: false",
        "ready_for_paid_customer: false",
        f"production_blocker_count: {payload['production_blocker_count']}",
        f"open_blocker_count: {payload['open_blocker_count']}",
        f"human_input_missing_value_row_count: {payload['human_input_missing_value_row_count']}",
        f"preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}",
        f"review_batch_missing_value_row_count: {payload['review_batch_missing_value_row_count']}",
        f"post_fill_quality_lint_enabled: {bool_text(payload['post_fill_quality_lint_enabled'])}",
        f"post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}",
        f"post_fill_forbidden_claim_lint_passed: {bool_text(payload['post_fill_forbidden_claim_lint_passed'])}",
        f"post_fill_shape_lint_passed: {bool_text(payload['post_fill_shape_lint_passed'])}",
        f"post_fill_ready_for_quality_safe_dry_run: {bool_text(payload['post_fill_ready_for_quality_safe_dry_run'])}",
        "blockers_closed_by_audit: 0",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "```",
        "",
        "## 为什么还不能正式商用",
        "",
        f"- 生产 blocker 仍有 `{payload['open_blocker_count']}` 个未关闭。",
        f"- 真实人工输入缺失值：`{payload['human_input_missing_value_row_count']}` 行。",
        f"- 导入前优先确认值缺失：`{payload['preferred_template_missing_value_row_count']}` 行。",
        f"- post-fill 质量 lint 问题数：`{payload['post_fill_quality_lint_issue_count']}`。",
        f"- 当前尚未达到可安全运行 post-fill dry run：`{bool_text(payload['post_fill_ready_for_quality_safe_dry_run'])}`。",
        f"- 需要工程实现的 blocker：`{payload['engineering_implementation_required_count']}` 个。",
        f"- 需要外部依赖或人工确认的 blocker：`{payload['external_dependency_required_count']}` 个。",
        "",
        "## blocker 分类",
        "",
        *category_lines,
        "",
        "## 前 10 个未关闭 blocker",
        "",
        *top_blocker_lines,
        "",
        "## 下一步",
        "",
        str(payload["next_human_action"]),
        "",
        "人工填完优先 10 行后，运行：",
        "",
        "```bash",
        payload["primary_local_command_after_human_fill"],
        "```",
        "",
        "## 禁止事项",
        "",
        *[f"- {item}" for item in payload["forbidden_actions"]],
    ]
    text = "\n".join(lines) + "\n"
    OUT_MD.write_text(text, encoding="utf-8")
    TOP_DOC.write_text(text, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Readiness Gap Audit Boundary Audit",
        "",
        "commercial_readiness_gap_audit_v0_1: true",
        f"status: {payload['status']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"post_fill_quality_lint_enabled: {bool_text(payload['post_fill_quality_lint_enabled'])}",
        f"post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}",
        f"post_fill_forbidden_claim_lint_passed: {bool_text(payload['post_fill_forbidden_claim_lint_passed'])}",
        f"post_fill_shape_lint_passed: {bool_text(payload['post_fill_shape_lint_passed'])}",
        f"post_fill_ready_for_quality_safe_dry_run: {bool_text(payload['post_fill_ready_for_quality_safe_dry_run'])}",
        "local_evidence_gap_audit_only: true",
        "human_values_generated_by_codex: false",
        "workbook_import_authorized: false",
        "workbook_import_performed: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_audit: 0",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "private_core_exposed: false",
        "customer_contacted: false",
        "customer_validated: false",
        "product_launched: false",
        "production_ready: false",
        "production_ready_claim: false",
        "",
        "Final boundary decision: observe and summarize current commercial gaps only.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Readiness Gap Audit Recommendation Gate",
                "",
                "recommendation_gate:",
                "  feature_or_direction: Commercial Readiness Gap Audit",
                "  target_customer_need: Before formal commercial use, know exactly which launch blockers and human evidence rows remain open.",
                "  answer: recommend",
                "  reasons_to_recommend:",
                "    - It gives a conservative current-state audit for formal commercial readiness.",
                "    - It keeps production launch, customer contact, evidence collection, and blocker closure disabled.",
                "    - It helps humans choose the next evidence task without changing SAEE behavior.",
                "  reasons_not_to_recommend: []",
                "  final_decision: recommend as local readiness audit only.",
                "",
                "```text",
                "commercial_readiness_gap_audit_v0_1: true",
                f"status: {payload['status']}",
                "recommend_for_local_gap_audit: true",
                "recommend_for_customer_push: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_product_launch: false",
                "production_ready: false",
                "customer_validated: false",
                f"post_fill_quality_lint_enabled: {bool_text(payload['post_fill_quality_lint_enabled'])}",
                f"post_fill_quality_lint_issue_count: {payload['post_fill_quality_lint_issue_count']}",
                f"post_fill_ready_for_quality_safe_dry_run: {bool_text(payload['post_fill_ready_for_quality_safe_dry_run'])}",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_READINESS_GAP_AUDIT: PASS "
        f"status={payload['status']} "
        f"open_blockers={payload['open_blocker_count']} "
        f"missing_values={payload['human_input_missing_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
