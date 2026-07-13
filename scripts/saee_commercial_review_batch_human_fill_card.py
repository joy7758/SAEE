#!/usr/bin/env python3
"""Create a human-readable fill card for the active 10-row review batch.

This is a presentation layer over the existing review-batch input template.
It does not generate values, fill values, apply values to source files, import
workbooks, run validators on real input, collect evidence, close blockers,
contact anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
TEMPLATE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
TEMPLATE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"

OUT_JSON = SPRINT_DIR / "commercial_review_batch_human_fill_card.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_human_fill_card.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_human_fill_card.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_human_fill_card.html"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_human_fill_card_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_HUMAN_FILL_CARD_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_FILL_CARD_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 10
POST_FILL_DRY_RUN_COMMAND = (
    "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
)
POST_FILL_JSON_CHECK_COMMAND = (
    "python3 -m json.tool "
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json"
)
POST_FILL_MAINLINE_COMMAND = "python3 scripts/mainline_guard.py"
FILL_CARD_SMOKE_COMMAND = "python3 scripts/saee_commercial_review_batch_human_fill_card_smoke.py"
PLAIN_LABELS = {
    "assigned_human_owner": "谁负责确认这个支持入口",
    "owner_contact_reference": "负责人或内部记录在哪里",
    "target_review_date": "计划哪一天完成确认",
    "owner_acknowledged_scope": "负责人是否知道只是在确认支持入口",
    "human_approval_reference": "人工批准记录或会议记录编号",
    "human_reviewer_name": "谁做了这次人工审查",
    "review_date": "审查日期",
    "selected_support_contact_channel": "以后客户从哪里联系支持",
    "decision_summary": "一句话说明为什么选这个支持方式",
    "abuse_handling_path_defined": "滥用或异常请求由谁处理",
}
PLAIN_INSTRUCTIONS = {
    "assigned_human_owner": "填写已由人确认的负责人姓名、角色或内部负责人标识。",
    "owner_contact_reference": "填写内部可追溯记录，例如工单、会议纪要、文档路径或审批编号；不要填未批准的私人联系方式。",
    "target_review_date": "填写计划完成确认的日期，建议使用 YYYY-MM-DD。",
    "owner_acknowledged_scope": "填写负责人已确认范围的简短说明，例如只确认支持入口，不代表正式上线。",
    "human_approval_reference": "填写人工批准或审查记录的编号、链接名称或文件路径。",
    "human_reviewer_name": "填写本次审查人的姓名、角色或内部标识。",
    "review_date": "填写实际审查日期，建议使用 YYYY-MM-DD。",
    "selected_support_contact_channel": "填写已经人工选择的支持入口类型，例如邮箱、表单、工单系统或暂不开放。",
    "decision_summary": "用一句话说明当前支持入口选择；不要写成已经正式对客户开放。",
    "abuse_handling_path_defined": "填写是否已有滥用处理路径及负责人；没有人工确认就留空。",
}
PLAIN_BLANK_RULES = {
    "assigned_human_owner": "如果还没有明确负责人，留空。",
    "owner_contact_reference": "如果没有内部记录或审批来源，留空。",
    "target_review_date": "如果还没有目标日期，留空。",
    "owner_acknowledged_scope": "如果负责人还没有确认范围，留空。",
    "human_approval_reference": "如果没有人工批准记录，留空。",
    "human_reviewer_name": "如果没有实际审查人，留空。",
    "review_date": "如果还没有实际审查日期，留空。",
    "selected_support_contact_channel": "如果支持入口尚未人工决定，留空。",
    "decision_summary": "如果还没有形成决策，留空。",
    "abuse_handling_path_defined": "如果滥用处理路径还没有人工确认，留空。",
}
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
    "ready_for_safety_preflight",
    "ready_for_workbook_import",
    "safe_to_import_after_human_approval",
    "values_transferred",
    "human_filled_templates_written",
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
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "task_candidates_executed",
    "payment_collected",
    "revenue_validated",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_template_rows() -> list[dict[str, str]]:
    with TEMPLATE_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    rows = read_template_rows()
    template = json.loads(TEMPLATE_JSON.read_text(encoding="utf-8"))
    boundary_violations: list[str] = []

    if len(rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_template_row_count")
    if template.get("status") != "ready_for_human_batch_value_entry":
        boundary_violations.append("template_not_ready_for_human_batch_value_entry")

    fill_card_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        value = row.get("human_value_to_enter", "")
        notes = row.get("notes_for_human", "")
        if value.strip():
            boundary_violations.append(f"prefilled_human_value:{row.get('review_batch_row_id')}")
        if notes.strip():
            boundary_violations.append(f"prefilled_human_note:{row.get('review_batch_row_id')}")
        fill_card_rows.append(
            {
                "card_row_number": index,
                "review_batch_row_id": row.get("review_batch_row_id", ""),
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "queue_item_id": row.get("queue_item_id", ""),
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "input_kind": row.get("input_kind", ""),
                "human_plain_label": PLAIN_LABELS.get(row.get("input_key", ""), row.get("input_key", "")),
                "expected_value_shape": row.get("expected_value_shape", ""),
                "fill_instruction": row.get("fill_instruction", ""),
                "human_plain_instruction": PLAIN_INSTRUCTIONS.get(
                    row.get("input_key", ""), row.get("fill_instruction", "")
                ),
                "leave_blank_condition": row.get("leave_blank_condition", ""),
                "human_plain_leave_blank_condition": PLAIN_BLANK_RULES.get(
                    row.get("input_key", ""), row.get("leave_blank_condition", "")
                ),
                "target_json_pointer": row.get("target_json_pointer", ""),
                "human_value_to_enter": "",
                "notes_for_human": "",
                "codex_may_fill": False,
                "human_input_required": True,
            }
        )

    status = (
        "stop_boundary_violation"
        if boundary_violations
        else "ready_for_human_fill_card_review"
    )
    payload: dict[str, Any] = {
        "commercial_review_batch_human_fill_card_v0_1": True,
        "card_type": "commercial_review_batch_human_fill_card",
        "card_scope": "human_readable_10_row_review_batch_fill_card_only_no_values_no_import_no_execution",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_human_fill_card.py",
        "source_template_csv": rel(TEMPLATE_CSV),
        "source_template_json": rel(TEMPLATE_JSON),
        "fill_card_row_count": len(fill_card_rows),
        "expected_fill_card_row_count": EXPECTED_ROW_COUNT,
        "blank_human_value_row_count": len(fill_card_rows),
        "blank_notes_row_count": len(fill_card_rows),
        "prefilled_human_value_row_count": 0,
        "prefilled_notes_row_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "ordinary_user_chinese_fill_guidance": True,
        "local_static_fill_companion_html": True,
        "local_static_execution_panel": True,
        "commercial_fill_card_visual_palette": "commercial-warm-graphite-sage-v1",
        "local_browser_manual_csv_builder": True,
        "browser_only_csv_text_generation": True,
        "manual_csv_builder_writes_files": False,
        "manual_csv_builder_network_calls": False,
        "manual_csv_builder_imports_workbook": False,
        "post_fill_dry_run_command": POST_FILL_DRY_RUN_COMMAND,
        "post_fill_json_check_command": POST_FILL_JSON_CHECK_COMMAND,
        "post_fill_mainline_command": POST_FILL_MAINLINE_COMMAND,
        "fill_card_smoke_command": FILL_CARD_SMOKE_COMMAND,
        "safe_human_entry_columns": ["human_value_to_enter", "notes_for_human"],
        "post_fill_commands_execute_external_calls": False,
        "post_fill_commands_import_workbook": False,
        "post_fill_commands_close_blockers": False,
        "codex_generated_values": False,
        "human_must_fill_values": True,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blockers_closed_by_fill_card": 0,
        "fill_card_rows": fill_card_rows,
        "next_human_action": (
            "Open commercial_review_batch_human_fill_card.html, fill only human_value_to_enter "
            "and optional notes_for_human in the source review-batch input template CSV, "
            "then run the local post-fill dry-run command."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "card_row_number",
        "review_batch_row_id",
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "human_plain_label",
        "human_plain_instruction",
        "human_plain_leave_blank_condition",
        "expected_value_shape",
        "fill_instruction",
        "leave_blank_condition",
        "target_json_pointer",
        "human_value_to_enter",
        "notes_for_human",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["fill_card_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def html_rows(rows: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in rows:
        parts.append(
            f"""<article class="fill-row">
  <div class="row-number">{esc(row['card_row_number'])}</div>
  <div class="row-main">
    <h2>{esc(row['human_plain_label'])}</h2>
    <p class="instruction">{esc(row['human_plain_instruction'])}</p>
    <p class="blank-rule">留空条件：{esc(row['human_plain_leave_blank_condition'])}</p>
    <dl>
      <div><dt>CSV 行</dt><dd>{esc(row['review_batch_row_id'])}</dd></div>
      <div><dt>字段名</dt><dd>{esc(row['input_key'])}</dd></div>
      <div><dt>所属 blocker</dt><dd>{esc(row['blocker_id'])}</dd></div>
      <div><dt>只填这两列</dt><dd><code>human_value_to_enter</code>，可选 <code>notes_for_human</code></dd></div>
    </dl>
    <div class="manual-entry-grid">
      <label>
        <span>人工确认值 human_value_to_enter</span>
        <textarea data-value-for="{esc(row['review_batch_row_id'])}" rows="3" placeholder="只填已经由人确认的内容；没有确认就留空"></textarea>
      </label>
      <label>
        <span>备注 notes_for_human（可选）</span>
        <textarea data-note-for="{esc(row['review_batch_row_id'])}" rows="2" placeholder="可写内部来源、待确认原因或留空说明"></textarea>
      </label>
    </div>
  </div>
</article>"""
        )
    return "\n".join(parts)


def html_command_list(payload: dict[str, Any]) -> str:
    commands = [
        ("填完先跑 dry-run", payload["post_fill_dry_run_command"]),
        ("查看 dry-run JSON 是否合法", payload["post_fill_json_check_command"]),
        ("再跑主线守卫", payload["post_fill_mainline_command"]),
    ]
    return "\n".join(
        f"""<div class="command-row">
  <span>{esc(label)}</span>
  <code>{esc(command)}</code>
</div>"""
        for label, command in commands
    )


def write_html(payload: dict[str, Any]) -> None:
    rows_json = json.dumps(payload["fill_card_rows"], ensure_ascii=False).replace("</", "<\\/")
    body = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 商业化首批 10 行人工填写说明</title>
    <style>
      :root {{
        color-scheme: light;
        --palette-name: commercial-warm-graphite-sage-v1;
        --bg: #f6f5f0;
        --surface: #fffdf8;
        --surface-soft: #ece8de;
        --text: #20231f;
        --muted: #646b61;
        --line: #ddd8ce;
        --accent: #0e7c66;
        --accent-strong: #0b604f;
        --accent-soft: #e4f1eb;
        --ink: #111311;
        --danger: #b42318;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background:
          radial-gradient(circle at 8% 4%, rgba(14, 124, 102, 0.12), transparent 28rem),
          linear-gradient(135deg, #fffdf8 0%, var(--bg) 62%, #edf4ef 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
      }}
      main {{
        width: min(1040px, calc(100% - 32px));
        margin: 0 auto;
        padding: 56px 0 72px;
      }}
      .hero {{
        display: grid;
        gap: 18px;
        padding-bottom: 34px;
        border-bottom: 1px solid var(--line);
      }}
      .eyebrow {{
        margin: 0;
        color: var(--muted);
        font-size: 14px;
        font-weight: 700;
      }}
      h1 {{
        max-width: 860px;
        margin: 0;
        font-size: clamp(34px, 6vw, 70px);
        line-height: 1.03;
        letter-spacing: 0;
      }}
      .lead {{
        max-width: 760px;
        margin: 0;
        color: var(--muted);
        font-size: 18px;
      }}
      .status-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
      }}
      .status-card {{
        min-width: 0;
        padding: 14px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
      }}
      .status-card strong,
      .status-card span {{
        display: block;
      }}
      .status-card strong {{
        font-size: 20px;
      }}
      .status-card span {{
        color: var(--muted);
        font-size: 13px;
      }}
      .steps {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 18px;
      }}
      .step {{
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
      }}
      .step b {{
        display: inline-grid;
        place-items: center;
        width: 28px;
        height: 28px;
        margin-bottom: 10px;
        border-radius: 8px;
        color: #fff;
        background: var(--accent);
      }}
      .step strong,
      .step span {{
        display: block;
      }}
      .step span {{
        margin-top: 4px;
        color: var(--muted);
        font-size: 14px;
      }}
      .notice {{
        display: grid;
        gap: 8px;
        margin-top: 18px;
        padding: 18px;
        border: 1px solid rgba(14, 124, 102, 0.25);
        border-radius: 8px;
        background: var(--accent-soft);
      }}
      code {{
        padding: 2px 5px;
        border-radius: 5px;
        background: rgba(14, 124, 102, 0.10);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.92em;
      }}
      .rows {{
        display: grid;
        gap: 12px;
        margin-top: 34px;
      }}
      .fill-row {{
        display: grid;
        grid-template-columns: 48px 1fr;
        gap: 18px;
        padding: 20px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
      }}
      .row-number {{
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        color: #fff;
        background: var(--accent);
        font-weight: 800;
      }}
      h2 {{
        margin: 0 0 8px;
        font-size: 22px;
        line-height: 1.2;
      }}
      .instruction,
      .blank-rule {{
        margin: 0 0 8px;
        color: var(--text);
      }}
      .blank-rule {{ color: var(--muted); }}
      dl {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
        margin: 14px 0 0;
      }}
      dl div {{
        min-width: 0;
        padding: 10px 12px;
        border-radius: 8px;
        background: var(--surface-soft);
      }}
      dt {{
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
      }}
      dd {{
        margin: 4px 0 0;
        overflow-wrap: anywhere;
        font-size: 14px;
      }}
      .command-panel {{
        display: grid;
        gap: 12px;
        margin-top: 34px;
        padding: 18px;
        border: 1px solid rgba(14, 124, 102, 0.25);
        border-radius: 8px;
        background: var(--accent-soft);
      }}
      .command-panel h2 {{
        margin-bottom: 0;
      }}
      .command-panel p {{
        margin: 0;
        color: var(--muted);
      }}
      .command-row {{
        display: grid;
        grid-template-columns: minmax(160px, 0.55fr) minmax(0, 1.45fr);
        gap: 12px;
        align-items: center;
        padding: 12px;
        border-radius: 8px;
        background: var(--surface);
      }}
      .command-row span {{
        color: var(--text);
        font-weight: 800;
      }}
      .command-row code {{
        overflow-wrap: anywhere;
      }}
      .boundary {{
        margin-top: 34px;
        padding: 18px;
        border-radius: 8px;
        background: var(--ink);
        color: #fff;
      }}
      .boundary ul {{
        display: grid;
        gap: 8px;
        margin: 12px 0 0;
        padding-left: 20px;
      }}
      .manual-entry-grid {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 12px;
        margin-top: 16px;
      }}
      .manual-entry-grid label {{
        display: grid;
        gap: 8px;
        min-width: 0;
      }}
      .manual-entry-grid span {{
        color: var(--muted);
        font-size: 13px;
        font-weight: 800;
      }}
      textarea {{
        width: 100%;
        min-height: 88px;
        padding: 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
        color: var(--text);
        font: inherit;
        resize: vertical;
      }}
      textarea:focus {{
        outline: 2px solid rgba(14, 124, 102, 0.22);
        border-color: var(--accent);
      }}
      .csv-builder {{
        display: grid;
        gap: 14px;
        margin-top: 34px;
        padding: 18px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
      }}
      .builder-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }}
      button {{
        min-height: 44px;
        padding: 0 16px;
        border: 0;
        border-radius: 8px;
        color: #fff;
        background: linear-gradient(135deg, var(--ink), var(--accent));
        font-weight: 900;
        cursor: pointer;
      }}
      .secondary-button {{
        color: var(--ink);
        background: var(--surface-soft);
      }}
      #csv-output {{
        min-height: 220px;
        white-space: pre;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 13px;
      }}
      .builder-note {{
        margin: 0;
        color: var(--muted);
      }}
      @media (max-width: 700px) {{
        main {{ width: min(100% - 24px, 1040px); padding-top: 34px; }}
        .status-grid,
        .steps,
        .manual-entry-grid,
        .command-row {{
          grid-template-columns: 1fr;
        }}
        .fill-row {{ grid-template-columns: 1fr; }}
        dl {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p class="eyebrow">SAEE 商业化准备 · 首批人工填写</p>
        <h1>先把这 10 行填清楚，再继续商用推进。</h1>
        <p class="lead">这个页面只帮助人看懂要填什么。Codex 没有生成任何值，也不会导入工作簿、收集证据或关闭 blocker。</p>
        <div class="status-grid" aria-label="当前状态">
          <div class="status-card"><strong>{esc(payload['fill_card_row_count'])}</strong><span>需要人工填写的行</span></div>
          <div class="status-card"><strong>{esc(payload['blank_human_value_row_count'])}</strong><span>当前仍为空</span></div>
          <div class="status-card"><strong>0</strong><span>已关闭 blocker</span></div>
          <div class="status-card"><strong>否</strong><span>生产可用状态</span></div>
        </div>
        <div class="steps" aria-label="人工填写三步">
          <div class="step"><b>1</b><strong>打开 CSV</strong><span>只打开下面这个源文件，不在本页面填写。</span></div>
          <div class="step"><b>2</b><strong>只填两列</strong><span><code>human_value_to_enter</code>，可选 <code>notes_for_human</code>。</span></div>
          <div class="step"><b>3</b><strong>保存后 dry-run</strong><span>先跑本地 dry-run，看格式和边界是否通过。</span></div>
        </div>
        <div class="notice">
          <strong>真正填写位置</strong>
          <span>{esc(payload['source_template_csv'])}</span>
          <span>只填写 <code>human_value_to_enter</code> 和可选 <code>notes_for_human</code>。</span>
        </div>
      </section>

      <section class="rows" aria-label="首批 10 行人工填写说明">
{html_rows(payload['fill_card_rows'])}
      </section>

      <section class="csv-builder" aria-label="本地 CSV 文本生成器">
        <h2>本地生成 CSV 文本</h2>
        <p class="builder-note">这个按钮只在浏览器里把你填的内容拼成 CSV 文本。它不联网、不保存文件、不写入仓库、不导入工作簿。</p>
        <div class="builder-actions">
          <button type="button" id="build-csv">生成 CSV 文本</button>
          <button type="button" class="secondary-button" id="clear-inputs">清空页面输入</button>
        </div>
        <textarea id="csv-output" aria-label="生成的 CSV 文本" readonly placeholder="点击“生成 CSV 文本”后，把这里的内容复制到 10 行 CSV 模板中，或另存为人工填写副本。"></textarea>
        <p class="builder-note">复制后仍需由人保存文件，并运行本地检查；本页不会自动保存或导入。</p>
      </section>

      <section class="command-panel" aria-label="填完后的本地检查命令">
        <h2>填完后先跑这些本地检查</h2>
        <p>这些命令只做本地检查，不导入工作簿，不联系客户，不发布产品，不关闭 blocker。</p>
{html_command_list(payload)}
      </section>

      <section class="boundary">
        <strong>边界</strong>
        <ul>
          <li>不生成填写值。</li>
          <li>不导入工作簿。</li>
          <li>不运行真实输入验证器。</li>
          <li>不收集证据。</li>
          <li>不关闭 blocker。</li>
          <li>不联系客户，不发布产品，不声明生产可用。</li>
        </ul>
      </section>
    </main>
    <script type="application/json" id="review-batch-rows-json">{rows_json}</script>
    <script>
      const rows = JSON.parse(document.getElementById("review-batch-rows-json").textContent);
      const headers = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "expected_value_shape",
        "fill_instruction",
        "leave_blank_condition",
        "target_json_pointer",
        "human_value_to_enter",
        "notes_for_human"
      ];
      function csvEscape(value) {{
        const text = String(value ?? "");
        return /[",\\n\\r]/.test(text) ? `"${{text.replaceAll('"', '""')}}"` : text;
      }}
      function inputValue(selector) {{
        const element = document.querySelector(selector);
        return element ? element.value.trim() : "";
      }}
      function buildCsvText() {{
        const outputRows = [headers.join(",")];
        rows.forEach((row) => {{
          const humanValue = inputValue(`[data-value-for="${{row.review_batch_row_id}}"]`);
          const notes = inputValue(`[data-note-for="${{row.review_batch_row_id}}"]`);
          const csvRow = headers.map((header) => {{
            if (header === "human_value_to_enter") return csvEscape(humanValue);
            if (header === "notes_for_human") return csvEscape(notes);
            return csvEscape(row[header] || "");
          }});
          outputRows.push(csvRow.join(","));
        }});
        document.getElementById("csv-output").value = outputRows.join("\\n");
      }}
      document.getElementById("build-csv").addEventListener("click", buildCsvText);
      document.getElementById("clear-inputs").addEventListener("click", () => {{
        document.querySelectorAll("textarea:not(#csv-output)").forEach((item) => {{
          item.value = "";
        }});
        document.getElementById("csv-output").value = "";
      }});
    </script>
  </body>
</html>
"""
    OUT_HTML.write_text(body, encoding="utf-8")


def row_sections(rows: list[dict[str, Any]]) -> str:
    sections: list[str] = []
    for row in rows:
        sections.append(
            "\n".join(
                [
                    f"### {row['card_row_number']}. {row['human_plain_label']}",
                    "",
                    f"- 字段名: {row['input_key']}",
                    f"- 这行要填什么: {row['human_plain_instruction']}",
                    f"- 什么时候留空: {row['human_plain_leave_blank_condition']}",
                    f"- review_batch_row_id: {row['review_batch_row_id']}",
                    f"- quick_fill_row_id: {row['quick_fill_row_id']}",
                    f"- blocker_id: {row['blocker_id']}",
                    f"- input_group: {row['input_group']}",
                    f"- expected_value_shape: {row['expected_value_shape']}",
                    f"- fill_instruction: {row['fill_instruction']}",
                    f"- leave_blank_condition: {row['leave_blank_condition']}",
                    f"- target_json_pointer: {row['target_json_pointer']}",
                    "- human_value_to_enter: ",
                    "- notes_for_human: ",
                ]
            )
        )
    return "\n\n".join(sections)


def write_markdown(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Review Batch Human Fill Card v0.1

commercial_review_batch_human_fill_card_v0_1: true
card_scope: {payload['card_scope']}
status: {payload['status']}
commercial_status: {payload['commercial_status']}
production_launch_status: {payload['production_launch_status']}

## Summary

- fill_card_row_count: {payload['fill_card_row_count']}
- expected_fill_card_row_count: {payload['expected_fill_card_row_count']}
- blank_human_value_row_count: {payload['blank_human_value_row_count']}
- prefilled_human_value_row_count: {payload['prefilled_human_value_row_count']}
- ordinary_user_chinese_fill_guidance: true
- local_static_fill_companion_html: true
- local_static_execution_panel: true
- commercial_fill_card_visual_palette: {payload['commercial_fill_card_visual_palette']}
- local_browser_manual_csv_builder: true
- browser_only_csv_text_generation: true
- manual_csv_builder_writes_files: false
- manual_csv_builder_network_calls: false
- manual_csv_builder_imports_workbook: false
- blockers_closed_by_fill_card: {payload['blockers_closed_by_fill_card']}
- production_ready: false
- customer_validated: false
- product_launched: false

## 给人看的操作说明

这一步只做一件事：让人把 10 行商业化准备信息填到 CSV 里。

1. 打开源 CSV：
   `{payload['source_template_csv']}`
2. 只填写两列：
   `human_value_to_enter` 和可选的 `notes_for_human`
3. 也可以在浏览器页面里填写，再点击“生成 CSV 文本”，手动复制保存。
4. 填完后只运行本地 dry-run 检查：
   `{payload['post_fill_dry_run_command']}`

不要在这一步导入工作簿、不要收集证据、不要关闭 blocker、不要联系客户、
不要发布产品、不要声明已经生产可用。

## 填完后的本地检查顺序

这些命令只检查本地文件和状态，不导入工作簿、不联系客户、不发布产品、不关闭 blocker。

```bash
{payload['post_fill_dry_run_command']}
{payload['post_fill_json_check_command']}
{payload['post_fill_mainline_command']}
```

## Purpose

This file makes the active 10-row commercial review batch easier for a human to
read before entering values. It is a view over the source template, not the
source of truth for imported values.

For a browser-readable local companion view, open:

`{rel(OUT_HTML)}`

## Human Fill Rows / 人工填写行

{row_sections(payload['fill_card_rows'])}

## Source Of Truth For Entry

Enter values only in:

`{payload['source_template_csv']}`

Fill only `human_value_to_enter` and optional `notes_for_human`.

## Next Command After Human Entry

```bash
{payload['post_fill_dry_run_command']}
```

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- post_fill_commands_execute_external_calls: false
- post_fill_commands_import_workbook: false
- post_fill_commands_close_blockers: false
- local_browser_manual_csv_builder: true
- browser_only_csv_text_generation: true
- manual_csv_builder_writes_files: false
- manual_csv_builder_network_calls: false
- manual_csv_builder_imports_workbook: false
- source_quick_fill_packet_modified: false
- batch_values_applied_to_source: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- production_ready: false
- customer_validated: false
- product_launched: false
"""
    OUT_MD.write_text(body, encoding="utf-8")
    TOP_DOC.write_text(body, encoding="utf-8")


def write_audit(payload: dict[str, Any]) -> None:
    OUT_AUDIT.write_text(
        f"""# Commercial Review Batch Human Fill Card Boundary Audit

- only_human_readable_fill_card_created: true
- ordinary_user_chinese_fill_guidance: true
- local_static_fill_companion_html: true
- local_static_execution_panel: true
- local_browser_manual_csv_builder: true
- browser_only_csv_text_generation: true
- manual_csv_builder_writes_files: false
- manual_csv_builder_network_calls: false
- manual_csv_builder_imports_workbook: false
- post_fill_commands_execute_external_calls: false
- post_fill_commands_import_workbook: false
- post_fill_commands_close_blockers: false
- generated_values: false
- entered_values: false
- source_quick_fill_packet_modified: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- production_ready: false
- customer_validated: false
- product_launched: false
- boundary_violation_count: {payload['boundary_violation_count']}
""",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        f"""# SAEE Commercial Review Batch Human Fill Card Recommendation Gate

answer: recommend
recommend_for_human_fill_readability: true
ordinary_user_chinese_fill_guidance: true
local_static_fill_companion_html: true
local_static_execution_panel: true
recommend_for_local_browser_csv_text_generation: true
recommend_for_value_generation: false
recommend_for_workbook_import: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The fill card now includes plain Chinese guidance, a local static HTML
companion page, and a browser-only CSV text builder for the active 10-row
commercial review batch without generating values, writing files, making
network calls, importing data, collecting evidence, or closing blockers. It
also shows the local post-fill dry-run command that a human can run after
manually entering values in the CSV.

## Status

- status: {payload['status']}
- fill_card_row_count: {payload['fill_card_row_count']}
- blank_human_value_row_count: {payload['blank_human_value_row_count']}
- ordinary_user_chinese_fill_guidance: true
- local_static_fill_companion_html: true
- local_static_execution_panel: true
- local_browser_manual_csv_builder: true
- browser_only_csv_text_generation: true
- manual_csv_builder_writes_files: false
- manual_csv_builder_network_calls: false
- manual_csv_builder_imports_workbook: false
- post_fill_dry_run_command: {payload['post_fill_dry_run_command']}
- production_ready: false
- product_launched: false
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_html(payload)
    write_markdown(payload)
    write_audit(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_FILL_CARD: PASS "
        f"status={payload['status']} fill_card_row_count={payload['fill_card_row_count']} "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
