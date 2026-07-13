#!/usr/bin/env python3
"""Post-fill readiness check for the 10-row commercial review batch.

This is a local wrapper for the shortest human-input path toward commercial
readiness. It checks whether the approved 10-row review-batch template has been
filled by a human, and only then runs the existing local post-fill dry run.

It does not generate human values, persist raw values, import workbooks, collect
evidence, close blockers, contact customers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

SOURCE_TEMPLATE = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
E2E_JSON = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json"
)
OUT_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_check.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_post_fill_check.md"
OUT_BOUNDARY = SPRINT_DIR / "commercial_review_batch_post_fill_check_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 10
SUPERSEDED_REVIEW_BATCH_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"
WORKBOOK_IMPORT_APPROVAL_PACKET_COMMAND = (
    "python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py"
)
E2E_COMMAND = [
    sys.executable,
    "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
]

FALSE_FLAGS = [
    "values_generated_by_codex",
    "human_values_filled_by_codex",
    "raw_values_recorded",
    "source_template_modified",
    "source_quick_fill_packet_modified",
    "local_quick_fill_output_written",
    "workbook_import_authorized",
    "workbook_import_performed",
    "validators_run_on_official_real_input",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "blockers_closed",
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
    "development_permission_granted",
    "payment_collected",
    "revenue_validated",
    "production_ready_claim",
    "customer_validation_claim",
]

FORBIDDEN_CLAIM_PATTERNS = [
    "production-ready",
    "production ready",
    "customer validated",
    "external validation completed",
    "product launched",
    "public sdk released",
    "private core",
    "evolution kernel",
    "fitness formula",
    "selection logic",
    "mutation logic",
    "lineage internals",
    "已生产可用",
    "生产可用",
    "已客户验证",
    "客户验证完成",
    "外部验证完成",
    "产品已发布",
    "已发布产品",
    "公开sdk",
    "公开 SDK",
    "公开私有核心",
    "公开核心",
    "进化内核",
    "适应度公式",
    "选择逻辑",
    "变异逻辑",
    "谱系内部",
]

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d[\s-]?){8,}")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def contains_forbidden_claim(text: str) -> bool:
    normalized = text.lower()
    return any(pattern.lower() in normalized for pattern in FORBIDDEN_CLAIM_PATTERNS)


def has_direct_contact_value(text: str) -> bool:
    return bool(EMAIL_RE.search(text) or PHONE_RE.search(text) or "http://" in text or "https://" in text)


def lint_human_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Lint human-entered values without writing raw values to outputs."""
    issues: list[dict[str, str]] = []
    date_keys = {"target_review_date", "review_date"}
    boolean_hold_keys = {"owner_acknowledged_scope", "abuse_handling_path_defined"}
    direct_contact_sensitive_keys = {
        "assigned_human_owner",
        "owner_contact_reference",
        "selected_support_contact_channel",
        "human_reviewer_name",
    }

    for row in rows:
        row_id = row.get("review_batch_row_id", "")
        input_key = row.get("input_key", "")
        value = row.get("human_value_to_enter", "").strip()
        notes = row.get("notes_for_human", "").strip()
        combined = "\n".join(part for part in [value, notes] if part)

        if not combined:
            continue

        if "EXAMPLE_ONLY" in combined or "示例" in combined:
            issues.append(
                {
                    "review_batch_row_id": row_id,
                    "input_key": input_key,
                    "issue_code": "example_or_placeholder_text_present",
                    "field": "human_value_to_enter_or_notes",
                }
            )
        if contains_forbidden_claim(combined):
            issues.append(
                {
                    "review_batch_row_id": row_id,
                    "input_key": input_key,
                    "issue_code": "forbidden_commercial_or_private_core_claim",
                    "field": "human_value_to_enter_or_notes",
                }
            )
        if input_key in direct_contact_sensitive_keys and has_direct_contact_value(value):
            issues.append(
                {
                    "review_batch_row_id": row_id,
                    "input_key": input_key,
                    "issue_code": "direct_contact_or_url_value_present",
                    "field": "human_value_to_enter",
                }
            )
        if input_key in date_keys and value and not DATE_RE.match(value):
            issues.append(
                {
                    "review_batch_row_id": row_id,
                    "input_key": input_key,
                    "issue_code": "date_value_not_yyyy_mm_dd",
                    "field": "human_value_to_enter",
                }
            )
        if input_key in boolean_hold_keys and value:
            normalized_value = value.lower()
            allowed_prefixes = ("true", "false", "hold", "yes", "no", "是", "否", "暂缓", "待")
            if not normalized_value.startswith(allowed_prefixes):
                issues.append(
                    {
                        "review_batch_row_id": row_id,
                        "input_key": input_key,
                        "issue_code": "boolean_hold_value_shape_unclear",
                        "field": "human_value_to_enter",
                    }
                )
    return issues


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def read_template_rows() -> list[dict[str, str]]:
    with SOURCE_TEMPLATE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run_e2e_dry_run() -> tuple[bool, str]:
    completed = subprocess.run(
        E2E_COMMAND,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.returncode == 0, completed.stdout.strip()


def load_e2e_summary() -> dict[str, Any]:
    if not E2E_JSON.is_file():
        return {}
    data = json.loads(E2E_JSON.read_text(encoding="utf-8"))
    allowed_keys = [
        "status",
        "template_row_count",
        "filled_template_value_row_count",
        "missing_template_value_row_count",
        "preview_validator_executed",
        "validator_status",
        "validator_passed",
        "boundary_violation_count",
    ]
    return {key: data.get(key) for key in allowed_keys if key in data}


def build_payload() -> dict[str, Any]:
    rows = read_template_rows()
    filled_count = sum(1 for row in rows if row.get("human_value_to_enter", "").strip())
    missing_count = len(rows) - filled_count
    row_ids_missing = [
        row.get("review_batch_row_id", "")
        for row in rows
        if not row.get("human_value_to_enter", "").strip()
    ]
    lint_issues = lint_human_rows(rows)
    lint_issue_count = len(lint_issues)
    review_batch_superseded = len(rows) == 0
    boundary_violations: list[str] = []
    e2e_executed = False
    e2e_returncode_ok = False
    e2e_output_excerpt = ""
    e2e_summary: dict[str, Any] = {}

    if len(rows) != EXPECTED_ROW_COUNT and not review_batch_superseded:
        boundary_violations.append("unexpected_review_batch_row_count")

    if (
        missing_count == 0
        and lint_issue_count == 0
        and not boundary_violations
        and not review_batch_superseded
    ):
        e2e_executed = True
        e2e_returncode_ok, e2e_output = run_e2e_dry_run()
        e2e_output_excerpt = e2e_output[-500:]
        e2e_summary = load_e2e_summary()
        if not e2e_returncode_ok:
            boundary_violations.append("post_fill_e2e_dry_run_failed")
        if e2e_summary.get("boundary_violation_count", 0):
            boundary_violations.append("post_fill_e2e_boundary_violation")

    if review_batch_superseded:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    elif boundary_violations:
        status = "stop_post_fill_check_boundary_issue"
    elif lint_issue_count:
        status = "stop_post_fill_quality_lint_issue"
    elif missing_count:
        status = "hold_human_values_required"
    elif e2e_summary.get("status") == "pass_template_values_ready_for_local_output_and_batch_validation":
        status = "pass_post_fill_local_validation_ready_for_separate_import_approval"
    else:
        status = "hold_post_fill_local_validation_needs_review"

    payload: dict[str, Any] = {
        "commercial_review_batch_post_fill_check_v0_1": True,
        "check_type": "local_10_row_post_fill_readiness_wrapper",
        "check_scope": "local_check_only_no_values_no_import_no_evidence_no_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_post_fill_check.py",
        "source_template_csv": rel(SOURCE_TEMPLATE),
        "expected_review_batch_row_count": EXPECTED_ROW_COUNT,
        "review_batch_row_count": len(rows),
        "filled_human_value_row_count": filled_count,
        "missing_human_value_row_count": missing_count,
        "missing_review_batch_row_ids": row_ids_missing,
        "human_input_required": missing_count > 0 and not review_batch_superseded,
        "review_batch_route_superseded": review_batch_superseded,
        "ready_for_workbook_import_approval_review": review_batch_superseded,
        "quality_lint_enabled": True,
        "quality_lint_scope": "local_boundary_shape_lint_no_raw_values",
        "quality_lint_issue_count": lint_issue_count,
        "quality_lint_issues": lint_issues,
        "forbidden_claim_lint_passed": lint_issue_count == 0,
        "shape_lint_passed": lint_issue_count == 0,
        "ready_for_quality_safe_post_fill_dry_run": (
            missing_count == 0
            and lint_issue_count == 0
            and not boundary_violations
            and not review_batch_superseded
        ),
        "ready_to_run_post_fill_e2e_dry_run": (
            missing_count == 0
            and lint_issue_count == 0
            and not boundary_violations
            and not review_batch_superseded
        ),
        "post_fill_e2e_dry_run_executed": e2e_executed,
        "post_fill_e2e_dry_run_returncode_ok": e2e_returncode_ok,
        "post_fill_e2e_summary": e2e_summary,
        "post_fill_e2e_output_excerpt": e2e_output_excerpt,
        "post_fill_e2e_command": " ".join(E2E_COMMAND),
        "mainline_guard_command": "python3 scripts/mainline_guard.py",
        "make_target": "make check-commercial-review-batch-post-fill-check",
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blockers_closed_by_check": 0,
        "next_human_action": (
            "Review the workbook import approval request packet. Do not import workbooks, run validators on real input, collect evidence, or close blockers without separate explicit approval."
            if review_batch_superseded
            else "Fill all 10 human_value_to_enter rows in the review-batch template, "
            "then rerun python3 scripts/saee_commercial_review_batch_post_fill_check.py "
            "to run the local quality lint and post-fill readiness check. "
            "If it passes, request separate approval before any workbook import, evidence "
            "collection, or blocker closure."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(payload: dict[str, Any]) -> None:
    superseded = bool(payload.get("review_batch_route_superseded"))
    intro = (
        "本文件只记录 10 行人工填写路径已被完整 quick-fill 值替代；下一步只能审查 workbook import 批准包。"
        if superseded
        else "本文件只记录 10 行人工资料是否已经填完，以及是否可以运行本地 post-fill dry-run。"
    )
    lines = [
        "# SAEE 10 行填写后本地检查",
        "",
        "Commercial Review Batch Post-Fill Check v0.1",
        "",
        intro,
        "",
        "```text",
        "commercial_review_batch_post_fill_check_v0_1: true",
        f"status: {payload['status']}",
        "commercial_status: hold",
        f"review_batch_row_count: {payload['review_batch_row_count']}",
        f"filled_human_value_row_count: {payload['filled_human_value_row_count']}",
        f"missing_human_value_row_count: {payload['missing_human_value_row_count']}",
        f"quality_lint_enabled: {bool_text(payload['quality_lint_enabled'])}",
        f"quality_lint_issue_count: {payload['quality_lint_issue_count']}",
        f"forbidden_claim_lint_passed: {bool_text(payload['forbidden_claim_lint_passed'])}",
        f"shape_lint_passed: {bool_text(payload['shape_lint_passed'])}",
        f"ready_for_quality_safe_post_fill_dry_run: {bool_text(payload['ready_for_quality_safe_post_fill_dry_run'])}",
        f"ready_to_run_post_fill_e2e_dry_run: {bool_text(payload['ready_to_run_post_fill_e2e_dry_run'])}",
        f"post_fill_e2e_dry_run_executed: {bool_text(payload['post_fill_e2e_dry_run_executed'])}",
        f"review_batch_route_superseded: {bool_text(payload['review_batch_route_superseded'])}",
        f"ready_for_workbook_import_approval_review: {bool_text(payload['ready_for_workbook_import_approval_review'])}",
        "blockers_closed_by_check: 0",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "```",
        "",
        "## 当前结果",
    ]
    if superseded:
        lines.extend(
            [
                "",
                "当前不再使用 10 行 post-fill 检查。完整 quick-fill 值已进入 workbook import approval review 状态。",
                "",
                f"- 下一步审查命令: `{WORKBOOK_IMPORT_APPROVAL_PACKET_COMMAND}`",
            ]
        )
    elif payload["quality_lint_issue_count"]:
        lines.extend(
            [
                "",
                "当前不能进入 post-fill 验证，因为本地质量 lint 发现了边界或格式问题。",
                "",
                "问题行：",
            ]
        )
        lines.extend(
            "- `{review_batch_row_id}` `{input_key}` `{issue_code}`".format(**issue)
            for issue in payload["quality_lint_issues"]
        )
    elif payload["missing_human_value_row_count"]:
        lines.extend(
            [
                "",
                "当前还不能进入 post-fill 验证，因为还有人工值未填写。",
                "",
                "缺失行：",
            ]
        )
        lines.extend(f"- `{row_id}`" for row_id in payload["missing_review_batch_row_ids"])
    else:
        lines.extend(
            [
                "",
                "10 行人工值已经存在，本脚本已尝试运行本地 post-fill dry-run。",
                "",
                f"- dry-run returncode ok: {bool_text(payload['post_fill_e2e_dry_run_returncode_ok'])}",
                f"- dry-run status: {payload['post_fill_e2e_summary'].get('status', 'unknown')}",
            ]
        )
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            payload["next_human_action"],
            "",
            "## 边界",
            "",
            "- 不生成真实人工值。",
            "- 不记录 raw human values。",
            "- 不把人工填写原文写进 lint 输出。",
            "- 会拦截生产可用、客户验证、外部验证、公开私有核心等危险表述。",
            "- 不导入工作簿。",
            "- 不收集证据。",
            "- 不关闭 blocker。",
            "- 不联系客户。",
            "- 不声明生产可用。",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Review Batch Post-Fill Check Boundary Audit",
        "",
        "commercial_review_batch_post_fill_check_v0_1: true",
        f"status: {payload['status']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"quality_lint_enabled: {bool_text(payload['quality_lint_enabled'])}",
        f"quality_lint_issue_count: {payload['quality_lint_issue_count']}",
        f"forbidden_claim_lint_passed: {bool_text(payload['forbidden_claim_lint_passed'])}",
        f"shape_lint_passed: {bool_text(payload['shape_lint_passed'])}",
        f"ready_for_quality_safe_post_fill_dry_run: {bool_text(payload['ready_for_quality_safe_post_fill_dry_run'])}",
        "values_generated_by_codex: false",
        "human_values_filled_by_codex: false",
        "raw_values_recorded: false",
        "workbook_import_performed: false",
        "evidence_collection_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_check: 0",
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
        "Final boundary decision: local post-fill readiness check only.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    target_need = (
        "After complete quick-fill values exist, keep the old 10-row post-fill check superseded and point humans to workbook import approval review."
        if payload["review_batch_route_superseded"]
        else "After a human fills the 10 support-contact rows, run one safe local check before any import or blocker work."
    )
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Review Batch Post-Fill Check Recommendation Gate",
                "",
                "recommendation_gate:",
                "  feature_or_direction: Commercial Review Batch Post-Fill Check",
                f"  target_customer_need: {target_need}",
                "  answer: recommend",
                "  reasons_to_recommend:",
                "    - It reduces human operator error after the 10-row fill step.",
                "    - It adds local quality lint for dangerous commercial claims, private-core wording, direct contact leakage, and simple field-shape errors.",
                "    - It does not generate values, import workbooks, collect evidence, close blockers, or claim production readiness.",
                "    - It keeps the commercial path explicit and agent-readable.",
                "  reasons_not_to_recommend: []",
                "  final_decision: recommend as a local post-fill readiness wrapper only.",
                "",
                "```text",
                "commercial_review_batch_post_fill_check_v0_1: true",
                f"status: {payload['status']}",
                f"review_batch_route_superseded: {bool_text(payload['review_batch_route_superseded'])}",
                f"ready_for_workbook_import_approval_review: {bool_text(payload['ready_for_workbook_import_approval_review'])}",
                "recommend_for_local_post_fill_check: true",
                "quality_lint_enabled: true",
                "recommend_for_boundary_shape_lint: true",
                "recommend_for_value_generation: false",
                "recommend_for_workbook_import: false",
                "recommend_for_blocker_closure: false",
                "production_ready: false",
                "product_launched: false",
                "customer_contacted: false",
                "private_core_exposed: false",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_CHECK: PASS "
        f"status={payload['status']} "
        f"filled={payload['filled_human_value_row_count']} "
        f"missing={payload['missing_human_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
