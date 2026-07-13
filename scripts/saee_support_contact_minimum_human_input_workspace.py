#!/usr/bin/env python3
"""Generate the minimum human-input workspace for support_contact.

This workspace reduces the first commercial blocker to the minimum human
decision fields needed before any local validator can become useful. It does
not fill values, save human input, export validator inputs, run evidence
builders, publish a support contact, contact customers, close blockers, or
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
SUPPORT_DIR = COMMERCIAL_DIR / "support_evidence"
OUT_DIR = SUPPORT_DIR / "support_contact_minimum_human_input_workspace"
OUT_JSON = OUT_DIR / "support_contact_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "support_contact_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "support_contact_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "support_contact_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "support_contact_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"

ENTRYPOINT_JSON = SUPPORT_DIR / "support_contact_human_input_entrypoint.local.json"
DECISION_TEMPLATE = SUPPORT_DIR / "support_contact_decision_input.template.json"
BRIDGE_TEMPLATE = (
    SUPPORT_DIR
    / "support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json"
)
FIRST_PRIORITY_JSON = (
    SUPPORT_DIR
    / "support_contact_first_priority_packet/support_contact_first_priority_packet.local.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def false_boundary() -> dict[str, bool]:
    return {
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "workbook_import_authorized": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "development_permission_granted": False,
        "production_ready_claim": False,
        "customer_validation_claim": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "support_contact_claim_published": False,
        "human_values_generated_by_codex": False,
        "human_input_filled_by_codex": False,
        "validator_inputs_exported": False,
        "validators_run": False,
        "values_saved_by_workspace": False,
        "form_submission_enabled": False,
    }


def field_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "field_id": "first_owner_input.assigned_human_owner",
            "group": "first_owner",
            "required": True,
            "where_to_fill": "support_contact_human_input_bridge_input.human_filled.local.json",
            "human_instruction": "填写负责推进 support_contact 的人名或内部角色。",
        },
        {
            "field_id": "first_owner_input.owner_contact_reference",
            "group": "first_owner",
            "required": True,
            "where_to_fill": "support_contact_human_input_bridge_input.human_filled.local.json",
            "human_instruction": "填写内部可追溯的负责人联系方式或工单引用，不要写敏感凭据。",
        },
        {
            "field_id": "first_owner_input.target_review_date",
            "group": "first_owner",
            "required": True,
            "where_to_fill": "support_contact_human_input_bridge_input.human_filled.local.json",
            "human_instruction": "填写目标审查日期。",
        },
        {
            "field_id": "first_owner_input.human_approval_reference",
            "group": "first_owner",
            "required": True,
            "where_to_fill": "support_contact_human_input_bridge_input.human_filled.local.json",
            "human_instruction": "填写人工批准来源，例如本地会议纪要或内部审批编号。",
        },
        {
            "field_id": "first_owner_input.owner_acknowledged_scope",
            "group": "first_owner",
            "required": True,
            "where_to_fill": "support_contact_human_input_bridge_input.human_filled.local.json",
            "human_instruction": "负责人确认只推进支持入口证据，不发布产品、不联系客户。",
        },
        {
            "field_id": "support_contact_decision_input.human_reviewer_name",
            "group": "decision_metadata",
            "required": True,
            "where_to_fill": "support_contact_decision_input.human_filled.local.json",
            "human_instruction": "填写实际审查人。",
        },
        {
            "field_id": "support_contact_decision_input.review_date",
            "group": "decision_metadata",
            "required": True,
            "where_to_fill": "support_contact_decision_input.human_filled.local.json",
            "human_instruction": "填写审查日期。",
        },
        {
            "field_id": "support_contact_decision_input.selected_support_contact_channel",
            "group": "decision_metadata",
            "required": True,
            "where_to_fill": "support_contact_decision_input.human_filled.local.json",
            "human_instruction": "填写被人工选定的支持渠道类型或内部引用。",
        },
        {
            "field_id": "support_contact_decision_input.decision_summary",
            "group": "decision_metadata",
            "required": True,
            "where_to_fill": "support_contact_decision_input.human_filled.local.json",
            "human_instruction": "用一句话说明为什么该支持入口可进入下一步本地验证。",
        },
    ]
    evidence_keys = [
        "customer_facing_support_contact_configured",
        "support_contact_owner_named",
        "abuse_handling_path_defined",
        "customer_notice_route_defined",
        "support_contact_test_recorded",
    ]
    for key in evidence_keys:
        rows.append(
            {
                "field_id": f"support_contact_decision_input.evidence_review.{key}",
                "group": "evidence_review",
                "required": True,
                "where_to_fill": "support_contact_decision_input.human_filled.local.json",
                "human_instruction": "只有人工确认真实证据存在时才设为 true。",
            }
        )
        rows.append(
            {
                "field_id": f"support_contact_decision_input.source_notes_by_key.{key}",
                "group": "source_notes",
                "required": True,
                "where_to_fill": "support_contact_decision_input.human_filled.local.json",
                "human_instruction": "填写人工可追溯来源说明；不要写密钥、密码或私人凭据。",
            }
        )
    rows.append(
        {
            "field_id": "support_contact_decision_input.candidate_contact_slots[minimum_one_complete]",
            "group": "candidate_contact_slot",
            "required": True,
            "where_to_fill": "support_contact_decision_input.human_filled.local.json",
            "human_instruction": "至少补全一个候选支持入口槽位；只记录人工批准的公开/可公开信息。",
        }
    )
    return rows


def build_payload() -> dict[str, Any]:
    entrypoint = load_json(ENTRYPOINT_JSON)
    decision_template = load_json(DECISION_TEMPLATE)
    bridge_template = load_json(BRIDGE_TEMPLATE)
    first_priority = load_json(FIRST_PRIORITY_JSON)
    rows = field_rows()
    payload: dict[str, Any] = {
        "support_contact_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_support_contact_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "support_contact",
        "source_entrypoint_json": rel(ENTRYPOINT_JSON),
        "source_decision_template": rel(DECISION_TEMPLATE),
        "source_bridge_template": rel(BRIDGE_TEMPLATE),
        "source_first_priority_packet": rel(FIRST_PRIORITY_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "minimum_required_field_count": len(rows),
        "minimum_required_human_value_count": len(rows),
        "filled_value_count": 0,
        "blank_value_count": len(rows),
        "field_rows": rows,
        "first_owner_field_count": entrypoint.get("missing_first_owner_field_count", 5),
        "support_decision_field_count": entrypoint.get(
            "missing_support_decision_field_count", 15
        ),
        "candidate_contact_slot_count": len(
            decision_template.get("candidate_contact_slots", [])
        ),
        "minimum_completed_contact_slot_count": 1,
        "combined_bridge_input_row_count": bridge_template.get("combined_input_row_count", 16),
        "first_priority_status": first_priority.get("status", "hold"),
        "human_review_required": True,
        "human_input_required": True,
        "next_human_action": (
            "Copy the bridge template and decision template to human_filled.local.json "
            "files, fill only human-approved values, then run local validators. "
            "Do not publish a support contact or close blockers from this workspace."
        ),
        "copy_commands": [
            (
                "cp phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json "
                "phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json"
            ),
            (
                "cp phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_decision_input.template.json "
                "phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_decision_input.human_filled.local.json"
            ),
        ],
        "post_fill_validation_commands": [
            (
                "python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py "
                "--combined-input phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json"
            ),
            (
                "python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py "
                "--input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
                "first_owner_input.human_filled.local.json"
            ),
            (
                "python3 scripts/saee_support_contact_approval_input_validator.py "
                "--input phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_decision_input.human_filled.local.json"
            ),
            "python3 scripts/saee_support_contact_readiness_board.py",
        ],
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    payload.update(false_boundary())
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_csv(payload: dict[str, Any]) -> None:
    fields = ["field_id", "group", "required", "where_to_fill", "human_instruction"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload["field_rows"])


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Support Contact Minimum Human Input Workspace v0.1",
        "",
        "`support_contact_minimum_human_input_workspace_v0_1: true`",
        "",
        "## 目的",
        "",
        "这个工作台只回答一个问题：为了推进 `support_contact` 这个第一优先商用阻塞项，",
        "人类最少需要补哪些字段。它不填写值、不保存值、不发布支持入口、不联系客户、",
        "不运行证据 builder、不导入工作簿、不关闭 blocker。",
        "",
        "## 状态",
        "",
        f"- `status: {payload['status']}`",
        f"- `target_blocker_id: {payload['target_blocker_id']}`",
        f"- `minimum_required_field_count: {payload['minimum_required_field_count']}`",
        f"- `filled_value_count: {payload['filled_value_count']}`",
        f"- `blank_value_count: {payload['blank_value_count']}`",
        "- `support_contact_published: false`",
        "- `production_ready: false`",
        "- `product_launched: false`",
        "",
        "## 最小字段清单",
        "",
        "| 字段 | 分组 | 必填 | 填到哪里 | 人工说明 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["field_rows"]:
        lines.append(
            "| `{field_id}` | {group} | {required} | `{where}` | {instruction} |".format(
                field_id=row["field_id"],
                group=row["group"],
                required=str(row["required"]).lower(),
                where=row["where_to_fill"],
                instruction=row["human_instruction"],
            )
        )
    lines.extend(
        [
            "",
            "## 复制模板",
            "",
            "```bash",
            *payload["copy_commands"],
            "```",
            "",
            "## 人工填写后再运行",
            "",
            "```bash",
            *payload["post_fill_validation_commands"],
            "```",
            "",
            "## 明确边界",
            "",
            "- `values_saved_by_workspace: false`",
            "- `form_submission_enabled: false`",
            "- `validator_inputs_exported: false`",
            "- `validators_run: false`",
            "- `evidence_collection_authorized: false`",
            "- `blocker_closure_authorized: false`",
            "- `support_contact_configured: false`",
            "- `support_contact_published: false`",
            "- `customer_contacted: false`",
            "- `production_ready: false`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "<tr><td><code>{field}</code></td><td>{group}</td><td>{where}</td><td>{note}</td></tr>".format(
            field=html.escape(row["field_id"]),
            group=html.escape(row["group"]),
            where=html.escape(row["where_to_fill"]),
            note=html.escape(row["human_instruction"]),
        )
        for row in payload["field_rows"]
    )
    copy_commands = "<br>".join(html.escape(cmd) for cmd in payload["copy_commands"])
    validation_commands = "<br>".join(
        html.escape(cmd) for cmd in payload["post_fill_validation_commands"]
    )
    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE support_contact 最小人工输入工作台</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f7f2;
        --card: #ffffff;
        --ink: #111111;
        --text: #343430;
        --muted: #63635f;
        --line: #e2e1da;
        --accent: #10a37f;
        --soft: #e8f6f1;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.65;
      }}
      main {{ width: min(1160px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0 72px; }}
      h1 {{ margin: 0; color: var(--ink); font-size: clamp(34px, 5vw, 58px); line-height: 1.08; letter-spacing: 0; }}
      h2 {{ margin: 0 0 14px; color: var(--ink); }}
      p {{ margin: 16px 0 0; }}
      .hero {{ display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 24px; align-items: start; }}
      .card, table {{ border: 1px solid var(--line); border-radius: 10px; background: var(--card); box-shadow: 0 18px 48px rgba(17, 17, 17, 0.06); }}
      .card {{ padding: 22px; }}
      .status {{ display: inline-flex; margin-top: 22px; padding: 8px 12px; border-radius: 999px; color: #0e7f67; background: var(--soft); font-weight: 800; }}
      code {{ padding: 2px 6px; border-radius: 6px; background: #f0f0eb; color: var(--ink); word-break: break-word; }}
      table {{ width: 100%; margin-top: 28px; border-collapse: separate; border-spacing: 0; overflow: hidden; }}
      th, td {{ padding: 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
      th {{ color: var(--ink); background: #f0f0eb; }}
      tr:last-child td {{ border-bottom: 0; }}
      .commands {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }}
      .boundary {{ margin-top: 24px; background: #111111; color: #f7f7f2; }}
      .boundary h2 {{ color: #ffffff; }}
      .boundary code {{ background: rgba(255,255,255,0.1); color: #ffffff; }}
      @media (max-width: 840px) {{ .hero, .commands {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div>
          <h1>只看 support_contact 最少要人填什么。</h1>
          <p>这个页面不保存输入，也不提交表单。它只是把第一优先商用 blocker 的最小人工字段列清楚。</p>
          <span class="status">状态：{html.escape(payload['status'])}</span>
        </div>
        <aside class="card">
          <h2>当前边界</h2>
          <p><code>support_contact_published: false</code></p>
          <p><code>values_saved_by_workspace: false</code></p>
          <p><code>production_ready: false</code></p>
          <p><code>blocker_closure_authorized: false</code></p>
        </aside>
      </section>

      <table>
        <thead><tr><th>字段</th><th>分组</th><th>填到哪里</th><th>说明</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>

      <section class="commands">
        <article class="card">
          <h2>先复制模板</h2>
          <p><code>{copy_commands}</code></p>
        </article>
        <article class="card">
          <h2>人工填完后再跑</h2>
          <p><code>{validation_commands}</code></p>
        </article>
      </section>

      <section class="card boundary">
        <h2>禁止越界</h2>
        <p>本工作台不发布支持入口、不联系客户、不运行证据 builder、不导入工作簿、不关闭 blocker、不声明生产可用。</p>
      </section>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_audit(payload: dict[str, Any]) -> None:
    lines = [
        "# Support Contact Minimum Human Input Workspace Boundary Audit",
        "",
        "Boundary decision: pass_hold.",
        "",
        "- Only minimum human-input field inventory created.",
        "- No values generated by Codex.",
        "- No values saved by workspace.",
        "- No form submission enabled.",
        "- No validator inputs exported.",
        "- No validators run.",
        "- No evidence builder run.",
        "- No workbook import authorized.",
        "- No blocker closure authorized.",
        "- No support contact configured.",
        "- No support contact published.",
        "- No customer contacted.",
        "- No runtime modified.",
        "- No backend modified.",
        "- No kernel modified.",
        "- No API schema modified.",
        "- No private core exposed.",
        "- No production-ready claim added.",
        "",
        "Machine flags:",
        "",
    ]
    for key, value in sorted(false_boundary().items()):
        lines.append(f"- `{key}: {str(value).lower()}`")
    lines.extend(
        [
            f"- `minimum_required_field_count: {payload['minimum_required_field_count']}`",
            f"- `blank_value_count: {payload['blank_value_count']}`",
        ]
    )
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(payload: dict[str, Any]) -> None:
    OUT_README.write_text(
        f"""# Support Contact Minimum Human Input Workspace

This directory contains a local, browser-readable workspace for the minimum
human inputs required before the `support_contact` blocker can move to local
validation.

- `support_contact_minimum_human_input_workspace_v0_1: true`
- `status: {payload['status']}`
- `minimum_required_field_count: {payload['minimum_required_field_count']}`
- `blank_value_count: {payload['blank_value_count']}`
- `values_saved_by_workspace: false`
- `support_contact_published: false`
- `production_ready: false`

It does not save values, submit forms, call external services, publish support
contacts, contact customers, import workbooks, run evidence builders, or close
blockers.
""",
        encoding="utf-8",
    )


def write_top_docs(payload: dict[str, Any]) -> None:
    text = f"""# SAEE Support Contact Minimum Human Input Workspace v0.1

support_contact_minimum_human_input_workspace_v0_1: true
status: {payload['status']}
target_blocker_id: support_contact
minimum_required_field_count: {payload['minimum_required_field_count']}
blank_value_count: {payload['blank_value_count']}
support_contact_published: false
values_saved_by_workspace: false
production_ready: false
product_launched: false
customer_validated: false

This is a human-input field inventory only. It does not authorize publication,
evidence collection, workbook import, blocker closure, or production readiness.

Artifacts:
- `phase_b_product/commercial_readiness/support_evidence/support_contact_minimum_human_input_workspace/support_contact_minimum_human_input_workspace.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_minimum_human_input_workspace/support_contact_minimum_human_input_workspace.html`
- `scripts/saee_support_contact_minimum_human_input_workspace.py`
- `scripts/saee_support_contact_minimum_human_input_workspace_smoke.py`
"""
    TOP_DOC.write_text(text, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Support Contact Minimum Human Input Workspace Gate

answer: hold_minimum_human_input_required
reason: The workspace identifies the minimum human-filled fields for the first-priority `support_contact` blocker, but no values were entered and no evidence was collected.

boundary:
- support_contact_published: false
- values_saved_by_workspace: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- production_ready: false
- product_launched: false
- customer_validated: false
- private_core_exposed: false

next_action: A human may copy the listed templates, fill human-approved values locally, and then run the listed validators. Do not publish a support contact or close blockers without a separate explicit request.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_readme(payload)
    write_top_docs(payload)
    print(
        "SAEE_SUPPORT_CONTACT_MINIMUM_HUMAN_INPUT_WORKSPACE: PASS "
        f"status={payload['status']} "
        f"fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
