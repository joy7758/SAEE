#!/usr/bin/env python3
"""Generate the post-fill validation runbook for the 10-row commercial review batch.

This surface tells a human what to run after the 10-row review-batch input
template has been filled. It does not fill values, infer values, write
workbooks, import evidence, contact anyone, close blockers, launch product, or
claim production readiness.
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
TEMPLATE_CSV = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
TEMPLATE_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"
)

OUT_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.html"
OUT_BOUNDARY = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 10
SUPERSEDED_REVIEW_BATCH_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"

DRY_RUN_COMMANDS = [
    {
        "step": "template_importer_dry_run",
        "command": "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py",
        "purpose": "Check whether human-filled template rows can be copied into a local quick-fill output without writing anything.",
    },
    {
        "step": "template_e2e_dry_run",
        "command": "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py",
        "purpose": "Validate the human-filled template through a temporary preview quick-fill CSV and selected-batch validator.",
    },
    {
        "step": "mainline_guard",
        "command": "python3 scripts/mainline_guard.py",
        "purpose": "Confirm the repository still preserves commercial and private-core boundaries.",
    },
    {
        "step": "importer_make_check",
        "command": "make check-commercial-sprint-human-input-quick-fill-review-batch-input-template-importer",
        "purpose": "Run importer smoke and JSON validation.",
    },
    {
        "step": "e2e_make_check",
        "command": "make check-commercial-sprint-human-input-quick-fill-review-batch-template-e2e-dry-run",
        "purpose": "Run post-fill E2E dry-run smoke and JSON validation.",
    },
]

SEPARATE_APPROVAL_ONLY_COMMANDS = [
    {
        "step": "local_output_apply_after_separate_approval",
        "command": (
            "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py "
            "--apply --confirm-human-approved-template-import"
        ),
        "purpose": "Write a local quick-fill output CSV only after separate explicit human approval.",
    }
]

FALSE_FLAGS = [
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "source_quick_fill_packet_modified",
    "batch_values_applied_to_source",
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
    "task_candidates_executed",
    "payment_collected",
    "revenue_validated",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_template_rows() -> list[dict[str, str]]:
    with TEMPLATE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    rows = read_template_rows()
    template_meta = json.loads(TEMPLATE_JSON.read_text(encoding="utf-8"))
    blank_rows = [
        row for row in rows if not row.get("human_value_to_enter", "").strip()
    ]
    filled_rows = [
        row for row in rows if row.get("human_value_to_enter", "").strip()
    ]
    row_count = len(rows)
    template_superseded = (
        template_meta.get("status") == SUPERSEDED_REVIEW_BATCH_STATUS
        and row_count == 0
    )
    structure_ok = row_count == EXPECTED_ROW_COUNT
    ready = structure_ok and not blank_rows and not template_superseded
    status = "ready_for_post_fill_local_validation_sequence" if ready else "hold_human_values_required_before_post_fill_sequence"
    if template_superseded:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    dry_run_commands = (
        [
            {
                "step": "workbook_import_approval_packet",
                "command": "python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py",
                "purpose": "Refresh the human approval packet before any separate workbook import execution request.",
            },
            {
                "step": "mainline_guard",
                "command": "python3 scripts/mainline_guard.py",
                "purpose": "Confirm the repository still preserves commercial and private-core boundaries.",
            },
        ]
        if template_superseded
        else DRY_RUN_COMMANDS
    )
    separate_approval_only_commands = [] if template_superseded else SEPARATE_APPROVAL_ONLY_COMMANDS

    payload: dict[str, Any] = {
        "commercial_review_batch_post_fill_validation_runbook_v0_1": True,
        "runbook_scope": "post_human_fill_local_validation_sequence_only_no_values_no_import_no_execution",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "source_input_template_csv": rel(TEMPLATE_CSV),
        "source_post_fill_html": rel(OUT_HTML),
        "local_static_post_fill_html": True,
        "browser_readable_post_fill_entrypoint": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_post_fill_validation_runbook.py",
        "template_row_count": row_count,
        "expected_template_row_count": EXPECTED_ROW_COUNT,
        "filled_human_value_row_count": len(filled_rows),
        "missing_human_value_row_count": len(blank_rows),
        "post_fill_validation_ready": ready,
        "post_fill_runbook_superseded": template_superseded,
        "ready_for_workbook_import_approval_review": template_superseded,
        "human_input_required": not template_superseded,
        "dry_run_command_count": len(dry_run_commands),
        "dry_run_commands": dry_run_commands,
        "separate_approval_only_command_count": len(separate_approval_only_commands),
        "separate_approval_only_commands": separate_approval_only_commands,
        "next_human_action": (
            "review the workbook import approval request packet; do not use the superseded 10-row post-fill runbook"
            if template_superseded
            else "fill all 10 human_value_to_enter rows before running the post-fill validation sequence"
            if not ready
            else "run the dry-run validation commands in order before requesting any local-output apply approval"
        ),
        "blockers_closed_by_runbook": 0,
        "boundary_violations": [],
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["step", "command", "purpose", "execution_boundary"])
        writer.writeheader()
        for command in payload["dry_run_commands"]:
            writer.writerow({**command, "execution_boundary": "dry_run_no_write"})
        for command in payload["separate_approval_only_commands"]:
            writer.writerow({**command, "execution_boundary": "separate_human_approval_required"})


def markdown_summary(payload: dict[str, Any], title: str) -> str:
    fill_heading = (
        "## Superseded Review Batch Route"
        if payload["post_fill_runbook_superseded"]
        else "## Fill First"
    )
    lines = [
        f"# {title}",
        "",
        "commercial_review_batch_post_fill_validation_runbook_v0_1: true",
        f"runbook_scope: {payload['runbook_scope']}",
        f"status: {payload['status']}",
        "commercial_status: hold",
        "production_launch_status: hold",
        "",
        "## Summary",
        "",
        f"- template_row_count: {payload['template_row_count']}",
        f"- expected_template_row_count: {payload['expected_template_row_count']}",
        f"- filled_human_value_row_count: {payload['filled_human_value_row_count']}",
        f"- missing_human_value_row_count: {payload['missing_human_value_row_count']}",
        f"- post_fill_validation_ready: {str(payload['post_fill_validation_ready']).lower()}",
        f"- post_fill_runbook_superseded: {str(payload['post_fill_runbook_superseded']).lower()}",
        f"- ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}",
        f"- local_static_post_fill_html: {str(payload['local_static_post_fill_html']).lower()}",
        f"- browser_readable_post_fill_entrypoint: {str(payload['browser_readable_post_fill_entrypoint']).lower()}",
        f"- source_post_fill_html: `{payload['source_post_fill_html']}`",
        f"- blockers_closed_by_runbook: {payload['blockers_closed_by_runbook']}",
        "- production_ready: false",
        "- customer_validated: false",
        "- product_launched: false",
        "",
        fill_heading,
        "",
        (
            "The 10-row post-fill route is superseded. No review-batch template rows remain to fill."
            if payload["post_fill_runbook_superseded"]
            else "Before running the post-fill sequence, a human must fill all 10 `human_value_to_enter` rows in:"
        ),
        "",
        f"`{payload['source_input_template_csv']}`",
        "",
        (
            "Codex must not import the workbook or run real-input validators without separate explicit approval."
            if payload["post_fill_runbook_superseded"]
            else "Codex must not generate, infer, or enter those values."
        ),
        "",
        "## Browser Entry",
        "",
        "A local static browser page is available for humans who prefer a visual checklist:",
        "",
        f"`{payload['source_post_fill_html']}`",
        "",
        "The HTML page is static, uses no JavaScript, makes no backend call, and does not import or apply any values.",
        "",
        "## Post-Fill Dry-Run Command Sequence",
        "",
    ]
    for index, command in enumerate(payload["dry_run_commands"], start=1):
        lines.extend(
            [
                f"{index}. `{command['command']}`",
                f"   - purpose: {command['purpose']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Separate Approval Only",
            "",
            "The following command is not authorized by this runbook. Use it only after a separate explicit human approval request:",
            "",
        ]
    )
    for command in payload["separate_approval_only_commands"]:
        lines.extend(
            [
                f"- `{command['command']}`",
                f"  - purpose: {command['purpose']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
        ]
    )
    for flag in FALSE_FLAGS:
        lines.append(f"- {flag}: false")
    lines.append("")
    lines.append("This runbook does not fill values, import a workbook, run evidence builders, close blockers, contact customers, launch product, or claim production readiness.")
    lines.append("")
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any]) -> None:
    OUT_MD.write_text(
        markdown_summary(payload, "SAEE Commercial Review Batch Post-Fill Validation Runbook v0.1"),
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        markdown_summary(payload, "SAEE Commercial Review Batch Post-Fill Validation Runbook v0.1"),
        encoding="utf-8",
    )


def write_html(payload: dict[str, Any]) -> None:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    superseded = payload["post_fill_runbook_superseded"]
    hero_title = (
        "10 行填写流程已停用。"
        if superseded
        else "填完 10 行后，先跑本地 dry-run。"
    )
    hero_lead = (
        "完整 quick-fill 值已经进入下一步：等待人工确认是否允许导入工作簿。这个页面只记录旧流程已停用。"
        if superseded
        else "这个页面只告诉你人工填写后该怎么检查。它不会填写数据，不会导入工作簿，不会关闭阻塞点，也不会让 SAEE 变成正式商用。"
    )
    first_step_title = "第一步：查看工作簿导入批准包" if superseded else "第一步：先确认 10 行都填完"
    first_step_body = "当前不需要填写 10 行模板。请审查批准包，并在单独明确批准前不要导入工作簿。" if superseded else "需要人工填写的源文件："
    second_step_title = "第二步：只跑本地确认命令" if superseded else "第二步：按顺序跑这些本地 dry-run"
    separate_intro = (
        "当前没有旧模板写入命令获得授权。任何工作簿导入都必须另走单独批准。"
        if superseded
        else "下面命令现在没有授权执行。只有在单独人工批准后，才可以写入本地 quick-fill 输出。"
    )

    dry_run_items = "\n".join(
        f"""
        <li>
          <code>{esc(command['command'])}</code>
          <p>{esc(command['purpose'])}</p>
        </li>
        """
        for command in payload["dry_run_commands"]
    )
    separate_items = "\n".join(
        f"""
        <li>
          <code>{esc(command['command'])}</code>
          <p>{esc(command['purpose'])}</p>
        </li>
        """
        for command in payload["separate_approval_only_commands"]
    )
    html_text = f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>SAEE 填写后本地检查步骤</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f8fb;
        --surface: #ffffff;
        --soft: #eef3ff;
        --text: #111827;
        --muted: #667085;
        --line: #d9e2ef;
        --accent: #316bff;
        --danger: #b42318;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.6;
      }}
      main {{
        width: min(980px, calc(100% - 32px));
        margin: 0 auto;
        padding: 56px 0;
      }}
      header, section {{
        margin-bottom: 18px;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
        box-shadow: 0 18px 48px rgba(17, 24, 39, 0.06);
      }}
      header {{
        padding: clamp(28px, 6vw, 52px);
        background: linear-gradient(135deg, #ffffff 0%, #eef3ff 100%);
      }}
      section {{ padding: 26px; }}
      h1, h2, p {{ margin-top: 0; }}
      h1 {{
        max-width: 760px;
        font-size: clamp(34px, 5vw, 58px);
        line-height: 1.05;
        letter-spacing: 0;
      }}
      h2 {{ font-size: 24px; }}
      .kicker {{
        color: var(--accent);
        font-weight: 800;
      }}
      .lead {{
        max-width: 760px;
        color: var(--muted);
        font-size: 18px;
      }}
      .stats {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin-top: 24px;
      }}
      .stat {{
        min-height: 92px;
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255,255,255,0.76);
      }}
      .stat strong {{
        display: block;
        font-size: 26px;
      }}
      .stat span {{ color: var(--muted); font-size: 13px; }}
      code {{
        display: block;
        padding: 12px 14px;
        border-radius: 10px;
        background: #101828;
        color: #ffffff;
        overflow-wrap: anywhere;
        font-size: 13px;
      }}
      ol, ul {{
        display: grid;
        gap: 12px;
        padding-left: 22px;
      }}
      li p {{
        margin: 8px 0 0;
        color: var(--muted);
      }}
      .warning {{
        border-color: #ffd6d1;
        background: #fff5f4;
      }}
      .warning strong {{ color: var(--danger); }}
      .boundary-list {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px 16px;
        padding: 0;
        list-style: none;
      }}
      .boundary-list li {{
        padding: 10px 12px;
        border-radius: 9px;
        background: var(--soft);
        color: var(--muted);
      }}
      @media (max-width: 720px) {{
        .stats, .boundary-list {{ grid-template-columns: 1fr; }}
        main {{ padding-top: 24px; }}
      }}
    </style>
  </head>
  <body>
	    <main>
	      <header>
	        <p class=\"kicker\">SAEE 商用准备 · 填写后本地检查</p>
	        <h1>{esc(hero_title)}</h1>
	        <p class=\"lead\">
	          {esc(hero_lead)}
	        </p>
        <div class=\"stats\" aria-label=\"当前状态\">
          <div class=\"stat\"><strong>{esc(payload['template_row_count'])}</strong><span>本批行数</span></div>
          <div class=\"stat\"><strong>{esc(payload['missing_human_value_row_count'])}</strong><span>仍缺人工值</span></div>
          <div class=\"stat\"><strong>{esc(payload['dry_run_command_count'])}</strong><span>dry-run 命令</span></div>
          <div class=\"stat\"><strong>0</strong><span>已关闭阻塞点</span></div>
        </div>
	      </header>

	      <section>
	        <h2>{esc(first_step_title)}</h2>
	        <p>{esc(first_step_body)}</p>
	        <code>{esc(payload['source_input_template_csv'])}</code>
	        <p>当前状态：{esc(payload['status'])}</p>
	      </section>

	      <section>
	        <h2>{esc(second_step_title)}</h2>
        <ol>
          {dry_run_items}
        </ol>
      </section>

	      <section class=\"warning\">
	        <h2>需要单独批准的命令</h2>
	        <p><strong>现在没有授权执行。</strong>{esc(separate_intro)}</p>
        <ul>
          {separate_items}
        </ul>
      </section>

      <section>
        <h2>边界</h2>
        <ul class=\"boundary-list\">
          <li>production_ready: false</li>
          <li>product_launched: false</li>
          <li>customer_validated: false</li>
          <li>workbook_import_authorized: false</li>
          <li>evidence_collection_authorized: false</li>
          <li>blockers_closed_by_runbook: 0</li>
          <li>runtime_modified: false</li>
          <li>backend_modified: false</li>
          <li>kernel_modified: false</li>
          <li>private_core_exposed: false</li>
        </ul>
      </section>
    </main>
  </body>
</html>
"""
    OUT_HTML.write_text(html_text, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Review Batch Post-Fill Validation Runbook Boundary Audit",
        "",
        "- local_runbook_only: true",
        "- human_values_generated_by_codex: false",
        "- quick_fill_values_entered_by_codex: false",
        "- source_quick_fill_packet_modified: false",
        "- batch_values_applied_to_source: false",
        "- local_quick_fill_output_written: false",
        "- workbook_import_authorized: false",
        "- workbook_import_performed: false",
        "- validators_run_on_real_input: false",
        "- evidence_collection_authorized: false",
        "- execution_authorized: false",
        "- blocker_closure_authorized: false",
        "- blockers_closed_by_runbook: 0",
        "- runtime_modified: false",
        "- backend_modified: false",
        "- kernel_modified: false",
        "- api_schema_modified: false",
        "- private_core_exposed: false",
        "- production_ready: false",
        "- customer_validated: false",
        "- product_launched: false",
        "",
        "No validators run on real input.",
        "No workbook import authorized or performed.",
        "No evidence collection authorized.",
        "No blocker closure authorized.",
        "",
        "Final decision: boundary safe; this runbook is a local instruction surface only.",
        "",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines), encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    reason = (
        "The 10-row post-fill runbook is superseded by complete quick-fill values and now points only to workbook import approval review, without authorizing workbook import, real-input validators, evidence collection, blocker closure, customer contact, launch, or production-readiness claims."
        if payload["post_fill_runbook_superseded"]
        else "The runbook gives humans a bounded local command sequence after they fill the 10-row commercial review batch, without authorizing value generation, workbook import, evidence collection, blocker closure, customer contact, launch, or production-readiness claims."
    )
    next_action = (
        "Review the workbook import approval request packet; do not run workbook import unless a separate explicit human execution request is created."
        if payload["post_fill_runbook_superseded"]
        else "Human fills the 10-row template, then runs the dry-run validation commands listed in the runbook."
    )
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Review Batch Post-Fill Validation Runbook Recommendation Gate",
                "",
                "answer: recommend",
                f"reason: {reason}",
                "",
                "boundary:",
                "  runbook_scope: post_human_fill_local_validation_sequence_only_no_values_no_import_no_execution",
                f"  status: {payload['status']}",
                f"  template_row_count: {payload['template_row_count']}",
                f"  missing_human_value_row_count: {payload['missing_human_value_row_count']}",
                "  human_values_generated_by_codex: false",
                "  quick_fill_values_entered_by_codex: false",
                "  workbook_import_authorized: false",
                "  evidence_collection_authorized: false",
                "  blockers_closed_by_runbook: 0",
                "  product_launched: false",
                "  production_ready: false",
                "  private_core_exposed: false",
                "",
                f"next_action: {next_action}",
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
    write_boundary(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK: PASS "
        f"status={payload['status']} "
        f"missing_human_value_row_count={payload['missing_human_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
