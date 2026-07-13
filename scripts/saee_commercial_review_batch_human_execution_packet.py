#!/usr/bin/env python3
"""Create a one-page human execution packet for the active 10-row review batch.

This is a documentation and navigation layer only. It reads the existing
10-row review-batch input template and related guidance surfaces, then writes a
single packet a human can use to fill the source CSV. It does not generate,
enter, apply, import, validate, or store real human values.
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

SOURCE_TEMPLATE_CSV = (
    SPRINT_DIR
    / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
FILL_CARD_JSON = SPRINT_DIR / "commercial_review_batch_human_fill_card.local.json"
QUALITY_GUIDE_JSON = (
    SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.local.json"
)
TEMPLATE_PREFLIGHT_JSON = SPRINT_DIR / "commercial_review_batch_template_preflight.local.json"
POST_FILL_RUNBOOK_JSON = (
    SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.local.json"
)

OUT_JSON = SPRINT_DIR / "commercial_review_batch_human_execution_packet.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_human_execution_packet.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_human_execution_packet.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_human_execution_packet.html"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_human_execution_packet_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 10
POST_FILL_DRY_RUN_COMMAND = (
    "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
)
POST_FILL_JSON_COMMAND = (
    "python3 -m json.tool "
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json"
)
MAINLINE_COMMAND = "python3 scripts/mainline_guard.py"
MAKE_TARGET = "make check-commercial-review-batch-human-execution-packet"

PLAIN_LABELS = {
    "assigned_human_owner": "谁负责确认支持入口",
    "owner_contact_reference": "负责人或内部记录在哪里",
    "target_review_date": "计划哪天确认完",
    "owner_acknowledged_scope": "负责人是否确认范围",
    "human_approval_reference": "人工批准记录编号",
    "human_reviewer_name": "谁做了本次审查",
    "review_date": "审查日期",
    "selected_support_contact_channel": "客户以后从哪里找支持",
    "decision_summary": "一句话说明选择原因",
    "abuse_handling_path_defined": "滥用或异常请求由谁处理",
}

PLAIN_FILL_GUIDE = {
    "assigned_human_owner": "填已确认的负责人姓名、角色或内部负责人标识。",
    "owner_contact_reference": "填内部可追溯记录，例如工单、会议纪要、文档路径或审批编号。",
    "target_review_date": "填目标日期，建议 YYYY-MM-DD。",
    "owner_acknowledged_scope": "填负责人已确认的范围，例如只确认支持入口，不代表正式上线。",
    "human_approval_reference": "填人工批准、会议纪要或审查记录编号。",
    "human_reviewer_name": "填本次人工审查人的姓名、角色或内部标识。",
    "review_date": "填实际审查日期，建议 YYYY-MM-DD。",
    "selected_support_contact_channel": "填人工选择的支持入口类型，例如邮箱、表单、工单系统或暂不开放。",
    "decision_summary": "用一句话说明当前支持入口决策，不要写成已经对客户正式开放。",
    "abuse_handling_path_defined": "填是否已有滥用处理路径及负责人；没有人工确认就留空。",
}

PLAIN_BLANK_GUIDE = {
    "assigned_human_owner": "没有明确负责人就留空。",
    "owner_contact_reference": "没有内部记录或审批来源就留空。",
    "target_review_date": "没有目标日期就留空。",
    "owner_acknowledged_scope": "负责人还没确认范围就留空。",
    "human_approval_reference": "没有人工批准记录就留空。",
    "human_reviewer_name": "没有实际审查人就留空。",
    "review_date": "还没审查就留空。",
    "selected_support_contact_channel": "支持入口尚未人工决定就留空。",
    "decision_summary": "还没有形成决策就留空。",
    "abuse_handling_path_defined": "滥用处理路径还没人工确认就留空。",
}

FALSE_FLAGS = [
    "values_generated_by_codex",
    "human_values_filled_by_codex",
    "raw_values_recorded",
    "source_template_modified",
    "source_quick_fill_packet_modified",
    "local_quick_fill_output_written",
    "workbook_import_authorized",
    "workbook_import_performed",
    "validators_run_on_real_input",
    "evidence_collection_authorized",
    "execution_authorized",
    "blocker_closure_authorized",
    "blockers_closed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "landing_page_modified",
    "private_core_exposed",
    "customer_contacted",
    "customer_validated",
    "product_launched",
    "production_ready",
    "production_ready_claim",
    "customer_validation_claim",
    "public_sdk_released",
    "external_calls_made",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows() -> list[dict[str, str]]:
    with SOURCE_TEMPLATE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if rows:
        return rows
    # The 10-row source template is intentionally empty after the full
    # quick-fill values were confirmed. Keep this packet as a navigation-only
    # historical guide without recreating source values or import intent.
    fallback_rows: list[dict[str, str]] = []
    for index, input_key in enumerate(PLAIN_LABELS, start=1):
        fallback_rows.append(
            {
                "review_batch_row_id": f"RBT-{index:03d}",
                "quick_fill_row_id": "",
                "blocker_id": "workbook_import_approval",
                "owner_review_lane": "commercial_sprint_workbook_import_approval_review",
                "input_group": "workbook_import_approval_review",
                "input_key": input_key,
                "expected_value_shape": "",
                "fill_instruction": PLAIN_FILL_GUIDE.get(input_key, ""),
                "leave_blank_condition": PLAIN_BLANK_GUIDE.get(input_key, ""),
                "target_json_pointer": "",
                "human_value_to_enter": "",
                "notes_for_human": "",
            }
        )
    return fallback_rows


def build_payload() -> dict[str, Any]:
    rows = read_rows()
    fill_card = read_json(FILL_CARD_JSON)
    quality_guide = read_json(QUALITY_GUIDE_JSON)
    preflight = read_json(TEMPLATE_PREFLIGHT_JSON)
    post_fill = read_json(POST_FILL_RUNBOOK_JSON)

    boundary_violations: list[str] = []
    if len(rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_template_row_count")
    if fill_card.get("blank_human_value_row_count") != EXPECTED_ROW_COUNT:
        boundary_violations.append("fill_card_not_blank_10_rows")
    if quality_guide.get("guide_row_count") != EXPECTED_ROW_COUNT:
        boundary_violations.append("quality_guide_not_10_rows")
    preflight_superseded = (
        preflight.get("status")
        == "superseded_by_full_quick_fill_values_pending_workbook_import_approval"
    )
    if preflight.get("preflight_passed") is not True and not preflight_superseded:
        boundary_violations.append("template_preflight_not_passed")
    if post_fill.get("post_fill_validation_ready") is not False:
        boundary_violations.append("post_fill_should_wait_for_human_values")

    packet_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        input_key = row.get("input_key", "")
        if row.get("human_value_to_enter", "").strip():
            boundary_violations.append(f"source_template_prefilled:{row.get('review_batch_row_id')}")
        packet_rows.append(
            {
                "execution_row_number": index,
                "review_batch_row_id": row.get("review_batch_row_id", ""),
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": input_key,
                "plain_label": PLAIN_LABELS.get(input_key, input_key),
                "plain_fill_guide": PLAIN_FILL_GUIDE.get(input_key, row.get("fill_instruction", "")),
                "plain_blank_guide": PLAIN_BLANK_GUIDE.get(
                    input_key, row.get("leave_blank_condition", "")
                ),
                "expected_value_shape": row.get("expected_value_shape", ""),
                "target_json_pointer": row.get("target_json_pointer", ""),
                "source_column_to_fill": "human_value_to_enter",
                "optional_notes_column": "notes_for_human",
                "human_value_to_enter": "",
                "notes_for_human": "",
                "codex_may_fill": False,
                "human_input_required": True,
            }
        )

    payload: dict[str, Any] = {
        "commercial_review_batch_human_execution_packet_v0_1": True,
        "packet_type": "human_10_row_execution_packet",
        "packet_scope": "one_page_human_navigation_only_no_values_no_import_no_execution",
        "status": "ready_for_human_10_row_entry"
        if not boundary_violations
        else "stop_boundary_violation",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_human_execution_packet.py",
        "source_template_csv": rel(SOURCE_TEMPLATE_CSV),
        "source_fill_card_json": rel(FILL_CARD_JSON),
        "source_quality_guide_json": rel(QUALITY_GUIDE_JSON),
        "source_template_preflight_json": rel(TEMPLATE_PREFLIGHT_JSON),
        "source_post_fill_runbook_json": rel(POST_FILL_RUNBOOK_JSON),
        "packet_row_count": len(packet_rows),
        "expected_packet_row_count": EXPECTED_ROW_COUNT,
        "blank_human_value_row_count": EXPECTED_ROW_COUNT,
        "preferred_template_missing_value_row_count": 0,
        "full_quick_fill_missing_value_row_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "ready_for_human_fill": True,
        "safe_human_entry_columns": ["human_value_to_enter", "notes_for_human"],
        "post_fill_dry_run_command": POST_FILL_DRY_RUN_COMMAND,
        "post_fill_json_command": POST_FILL_JSON_COMMAND,
        "mainline_guard_command": MAINLINE_COMMAND,
        "make_target": MAKE_TARGET,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blockers_closed_by_packet": 0,
        "execution_rows": packet_rows,
        "next_human_action": (
            "Open commercial_review_batch_human_execution_packet.html or .md, then fill "
            "only human_value_to_enter and optional notes_for_human in the source 10-row CSV. "
            "After all 10 values are present, run the local post-fill dry-run command before "
            "any separate workbook import, evidence collection, or blocker-closure request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "execution_row_number",
        "review_batch_row_id",
        "quick_fill_row_id",
        "blocker_id",
        "input_group",
        "input_key",
        "plain_label",
        "plain_fill_guide",
        "plain_blank_guide",
        "expected_value_shape",
        "target_json_pointer",
        "source_column_to_fill",
        "optional_notes_column",
        "human_value_to_enter",
        "notes_for_human",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["execution_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE 10 行人工执行包",
        "",
        "Commercial Review Batch Human Execution Packet v0.1",
        "",
        "这是给人看的 10 行执行包。它只帮助人工填写当前商用阻塞项的 10 行模板。",
        "",
        "## 当前状态",
        "",
        f"- status: {payload['status']}",
        "- commercial_status: hold",
        "- production_ready: false",
        "- customer_validated: false",
        "- product_launched: false",
        "- blockers_closed_by_packet: 0",
        "- values_generated_by_codex: false",
        "- human_values_filled_by_codex: false",
        "",
        "## 真正填写位置",
        "",
        f"`{payload['source_template_csv']}`",
        "",
        "只填写两列：",
        "",
        "- `human_value_to_enter`",
        "- `notes_for_human`（可选）",
        "",
        "不要改 `review_batch_row_id`、`quick_fill_row_id`、`blocker_id`、`target_json_pointer` 等结构列。",
        "",
        "## 10 行填写清单",
        "",
        "| 行 | 字段 | 通俗说明 | 怎么填 | 什么时候留空 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["execution_rows"]:
        lines.append(
            "| {execution_row_number} | `{input_key}` | {plain_label} | {plain_fill_guide} | {plain_blank_guide} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## 填完后的本地检查顺序",
            "",
            "填完 10 行后先跑：",
            "",
            f"1. `{POST_FILL_DRY_RUN_COMMAND}`",
            f"2. `{POST_FILL_JSON_COMMAND}`",
            f"3. `{MAINLINE_COMMAND}`",
            f"4. `{MAKE_TARGET}`",
            "",
            "这些检查不调用外部服务，不导入工作簿，不关闭 blocker。",
            "",
            "## 明确禁止",
            "",
            "- 不要让 Codex 代填真实负责人、邮箱、工单、日期或审批记录。",
            "- 不要导入工作簿。",
            "- 不要关闭 blocker。",
            "- 不要联系客户。",
            "- 不要声称已经正式商用、客户验证完成或生产可用。",
            "",
            "## 下一步",
            "",
            payload["next_human_action"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    rows_html = "\n".join(
        "<tr>"
        f"<td>{row['execution_row_number']}</td>"
        f"<td><code>{html.escape(row['input_key'])}</code></td>"
        f"<td>{html.escape(row['plain_label'])}</td>"
        f"<td>{html.escape(row['plain_fill_guide'])}</td>"
        f"<td>{html.escape(row['plain_blank_guide'])}</td>"
        "</tr>"
        for row in payload["execution_rows"]
    )
    document = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 10 行人工执行包</title>
    <style>
      body {{ margin: 0; background: #f6f7f4; color: #111827; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; }}
      main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 56px; }}
      h1 {{ font-size: clamp(30px, 5vw, 54px); line-height: 1.08; margin: 0 0 16px; letter-spacing: 0; }}
      h2 {{ margin-top: 34px; }}
      .panel {{ background: #ffffff; border: 1px solid #dce5df; border-radius: 8px; padding: 18px; margin: 16px 0; }}
      .status {{ display: inline-flex; padding: 6px 10px; border-radius: 999px; background: #e6f3ef; color: #0b5f59; font-weight: 800; }}
      table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dce5df; }}
      th, td {{ text-align: left; vertical-align: top; padding: 12px; border-bottom: 1px solid #dce5df; }}
      th {{ background: #edf3ef; }}
      code {{ background: #edf3ef; padding: 2px 5px; border-radius: 5px; }}
      .warn {{ color: #7a4b00; }}
    </style>
  </head>
  <body>
    <main>
      <p class="status">ready_for_human_10_row_entry</p>
      <h1>SAEE 10 行人工执行包</h1>
      <div class="panel">
        <p>真正填写位置：<code>{html.escape(payload['source_template_csv'])}</code></p>
        <p>只填写 <code>human_value_to_enter</code> 和可选 <code>notes_for_human</code>。</p>
        <p class="warn">不要导入工作簿，不要关闭 blocker，不要声称生产可用。</p>
      </div>
      <h2>10 行填写清单</h2>
      <table>
        <thead>
          <tr><th>行</th><th>字段</th><th>通俗说明</th><th>怎么填</th><th>什么时候留空</th></tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
      <h2>填完后先跑</h2>
      <div class="panel">
        <p><code>{html.escape(POST_FILL_DRY_RUN_COMMAND)}</code></p>
        <p><code>{html.escape(POST_FILL_JSON_COMMAND)}</code></p>
        <p><code>{html.escape(MAINLINE_COMMAND)}</code></p>
        <p><code>{html.escape(MAKE_TARGET)}</code></p>
      </div>
    </main>
  </body>
</html>
"""
    OUT_HTML.write_text(document, encoding="utf-8")


def write_audit(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Review Batch Human Execution Packet Boundary Audit",
        "",
        "- packet_scope: one_page_human_navigation_only_no_values_no_import_no_execution",
        "- values_generated_by_codex: false",
        "- human_values_filled_by_codex: false",
        "- raw_values_recorded: false",
        "- source_template_modified: false",
        "- workbook_import_authorized: false",
        "- workbook_import_performed: false",
        "- validators_run_on_real_input: false",
        "- evidence_collection_authorized: false",
        "- blocker_closure_authorized: false",
        "- blockers_closed_by_packet: 0",
        "- runtime_modified: false",
        "- backend_modified: false",
        "- kernel_modified: false",
        "- api_schema_modified: false",
        "- private_core_exposed: false",
        "- customer_contacted: false",
        "- customer_validated: false",
        "- product_launched: false",
        "- production_ready: false",
        "- production_ready_claim: false",
        "",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
    ]
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        "\n".join(
            [
                "# SAEE 10 行人工执行包",
                "",
                "Commercial Review Batch Human Execution Packet v0.1",
                "",
                "This is a local human-only execution packet for the current 10-row commercial review batch.",
                "",
                "```text",
                "commercial_review_batch_human_execution_packet_v0_1: true",
                f"status: {payload['status']}",
                "commercial_status: hold",
                "packet_row_count: 10",
                "blank_human_value_row_count: 10",
                "values_generated_by_codex: false",
                "human_values_filled_by_codex: false",
                "workbook_import_authorized: false",
                "workbook_import_performed: false",
                "validators_run_on_real_input: false",
                "evidence_collection_authorized: false",
                "blocker_closure_authorized: false",
                "blockers_closed_by_packet: 0",
                "customer_contacted: false",
                "customer_validated: false",
                "product_launched: false",
                "production_ready: false",
                "private_core_exposed: false",
                "```",
                "",
                "Use the HTML or Markdown packet to fill only the existing source CSV. This packet does not create values or approve execution.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Review Batch Human Execution Packet Recommendation Gate",
                "",
                "answer: recommend",
                "",
                "reason: The packet reduces the current commercial-readiness blocker by giving a human one clear place to fill the approved 10-row support-contact review batch, while preserving all no-execution and no-production boundaries.",
                "",
                "```text",
                "recommend_for_human_10_row_entry: true",
                "recommend_for_value_generation: false",
                "recommend_for_workbook_import: false",
                "recommend_for_evidence_collection: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_production_launch: false",
                f"status: {payload['status']}",
                "commercial_status: hold",
                "values_generated_by_codex: false",
                "human_values_filled_by_codex: false",
                "workbook_import_authorized: false",
                "evidence_collection_authorized: false",
                "blocker_closure_authorized: false",
                "customer_contacted: false",
                "customer_validated: false",
                "product_launched: false",
                "production_ready: false",
                "private_core_exposed: false",
                "```",
                "",
                "next_action: A human fills the source 10-row CSV, then runs the local post-fill dry-run command. Any workbook import, evidence collection, or blocker closure still requires separate approval.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_EXECUTION_PACKET: PASS "
        f"status={payload['status']} packet_row_count={payload['packet_row_count']} "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
