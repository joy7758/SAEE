#!/usr/bin/env python3
"""Build the first-owner input request packet for the support_contact blocker.

The packet turns the current commercial next action into a human-readable and
agent-readable request surface. It does not assign owners, contact owners,
collect evidence, execute work, close blockers, launch product, or claim
production readiness.
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
NEXT_ACTION_SUMMARY = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_action_summary/"
    "commercial_next_action_summary.local.json"
)
COMPLETION_CSV = SPRINT_DIR / "first_owner_input_completion.csv"
COMPLETION_GUIDE = SPRINT_DIR / "first_owner_input_completion_guide.md"
VALIDATOR_OUTPUT = SPRINT_DIR / "first_owner_input_validation.local.json"
TEMPLATE_INPUT = SPRINT_DIR / "first_owner_input.template.json"
RECOMMENDED_HUMAN_FILLED_INPUT = SPRINT_DIR / "first_owner_input.human_filled.local.json"
FIRST_OWNER_ACTION_PACKET_JSON = SPRINT_DIR / "first_owner_action_packet.local.json"
OUTPUT_JSON = SPRINT_DIR / "first_owner_input_request_packet.local.json"
OUTPUT_MD = SPRINT_DIR / "first_owner_input_request_packet.md"
OUTPUT_CSV = SPRINT_DIR / "first_owner_input_request_packet.csv"
OUTPUT_HTML = SPRINT_DIR / "first_owner_input_request_packet.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET_RECOMMENDATION_GATE.md"
)

REQUIRED_FIELDS = [
    "assigned_human_owner",
    "owner_contact_reference",
    "target_review_date",
    "owner_acknowledged_scope",
    "human_approval_reference",
]

FIELD_LABELS = {
    "assigned_human_owner": "负责人姓名或内部代号",
    "owner_contact_reference": "内部联系方式或协作入口",
    "target_review_date": "目标审查日期",
    "owner_acknowledged_scope": "负责人是否确认范围",
    "human_approval_reference": "人工批准记录编号或链接说明",
}

FIELD_HINTS = {
    "assigned_human_owner": "填写真人负责人，不要让 Codex 自动指定。",
    "owner_contact_reference": "填写内部可追踪的联系引用，不要写外部客户隐私。",
    "target_review_date": "使用 YYYY-MM-DD 格式。",
    "owner_acknowledged_scope": "填 true/false；只有负责人已确认边界时才填 true。",
    "human_approval_reference": "填写人审记录、会议纪要或内部批准编号。",
}

BOUNDARY_FALSE = {
    "owner_assigned_by_codex": False,
    "owner_contacted_by_codex": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "task_candidates_executed": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET: "
            f"FAIL {path} must contain an object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_next_action() -> dict[str, Any]:
    summary = read_json(NEXT_ACTION_SUMMARY)
    action_packet = read_json(FIRST_OWNER_ACTION_PACKET_JSON)
    command_template = str(action_packet.get("human_fill_shell_command", "")).strip()
    if not command_template:
        command_template = (
            "python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py \\\n"
            "  --single-blocker-id support_contact \\\n"
            "  --assigned-human-owner \"<human owner>\" \\\n"
            "  --owner-contact-reference \"<internal owner reference>\" \\\n"
            "  --target-review-date \"YYYY-MM-DD\" \\\n"
            "  --owner-acknowledged-scope true \\\n"
            "  --human-approval-reference \"<human approval record>\" \\\n"
            "  --output-input-json phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.human_filled.local.json"
        )
    actions = summary.get("next_actions")
    if not isinstance(actions, list) or not actions:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET: "
            "FAIL next action summary has no next_actions"
        )
    first = actions[0]
    if not isinstance(first, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET: "
            "FAIL first next action must be an object"
        )
    if first.get("blocker_id") != "support_contact" or first.get("sequence_step_id") != "SEQ-001":
        return {
            "action_id": "NEXT-001",
            "sequence_step_id": "SEQ-001",
            "blocker_id": "support_contact",
            "exact_generation_command": command_template,
            "next_validator_command": "python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py",
        }
    action = dict(first)
    action["action_id"] = action.get("action_id") or "NEXT-001"
    action["sequence_step_id"] = "SEQ-001"
    action["blocker_id"] = "support_contact"
    action["exact_generation_command"] = command_template
    action["next_validator_command"] = (
        "python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py"
    )
    return action


def build_payload(action: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "first_owner_input_request_packet_v0_1": True,
        "packet_type": "saee_commercial_evidence_sprint_first_owner_input_request_packet",
        "packet_version": "v0.1",
        "status": "hold_human_first_owner_input_request_required",
        "action_id": action.get("action_id", "NEXT-001"),
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": "support_contact",
        "category": "support",
        "source_next_action_summary": rel(NEXT_ACTION_SUMMARY),
        "source_completion_csv": rel(COMPLETION_CSV),
        "source_completion_guide": rel(COMPLETION_GUIDE),
        "source_first_owner_action_packet": rel(FIRST_OWNER_ACTION_PACKET_JSON),
        "source_first_owner_input_request_html": rel(OUTPUT_HTML),
        "source_first_owner_input_template": rel(TEMPLATE_INPUT),
        "recommended_human_filled_input_path": rel(RECOMMENDED_HUMAN_FILLED_INPUT),
        "local_static_first_owner_input_request_html": True,
        "browser_readable_first_owner_input_request": True,
        "copy_ready_blank_json_template_in_html": True,
        "validator_output": rel(VALIDATOR_OUTPUT),
        "request_packet_ready": True,
        "human_input_required": True,
        "required_human_fields": REQUIRED_FIELDS,
        "required_human_field_count": len(REQUIRED_FIELDS),
        "completed_human_field_count": 0,
        "missing_human_field_count": len(REQUIRED_FIELDS),
        "ready_for_first_owner_input_validator": False,
        "ready_for_evidence_collection": False,
        "ready_for_separate_evidence_collection_request": False,
        "separate_validator_required": True,
        "separate_evidence_collection_request_required": True,
        "blockers_closed_by_request_packet": 0,
        "next_generation_command_template": action.get("exact_generation_command", ""),
        "next_generation_command_template_available": bool(
            str(action.get("exact_generation_command", "")).strip()
        ),
        "next_validator_command": action.get("next_validator_command", ""),
        "next_human_action": (
            "Fill the five support_contact first-owner fields, generate "
            "first_owner_input.human_filled.local.json, then run the first-owner "
            "input validator. Do not collect evidence or close blockers."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet.py",
    }
    payload.update(BOUNDARY_FALSE)
    return payload


def bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def first_owner_blank_template() -> dict[str, Any]:
    if TEMPLATE_INPUT.exists():
        return read_json(TEMPLATE_INPUT)
    return {
        "template_type": "saee_commercial_evidence_sprint_first_owner_input",
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "sequence_step_id": "SEQ-001",
        "first_blocker_id": "support_contact",
        "required_human_fields": REQUIRED_FIELDS,
        "first_owner_input": {
            "blocker_id": "support_contact",
            "phase_id": "phase_3_support_security_legal",
            "category": "support",
            "owner_review_lane": "support_operations",
            "required_evidence": (
                "Customer-facing support intake contact, ownership, response "
                "procedure, and abuse handling."
            ),
            "assigned_human_owner": "",
            "owner_contact_reference": "",
            "target_review_date": "",
            "owner_acknowledged_scope": False,
            "human_approval_reference": "",
            "notes": "",
        },
        "boundary_review": {key: False for key in BOUNDARY_FALSE},
        "human_reviewer_name": "",
        "review_date": "",
        "review_notes": "",
    }


def write_html(payload: dict[str, Any]) -> None:
    field_rows = []
    for field in REQUIRED_FIELDS:
        field_rows.append(
            f"""
            <tr>
              <td><strong>{escape(FIELD_LABELS[field])}</strong><br><code>{escape(field)}</code></td>
              <td>{escape(FIELD_HINTS[field])}</td>
              <td>未填写</td>
            </tr>
            """
        )

    boundary_items = [
        ("owner_assigned_by_codex", payload["owner_assigned_by_codex"]),
        ("owner_contacted_by_codex", payload["owner_contacted_by_codex"]),
        ("evidence_collection_authorized", payload["evidence_collection_authorized"]),
        ("execution_authorized", payload["execution_authorized"]),
        ("blockers_closed_by_request_packet", payload["blockers_closed_by_request_packet"]),
        ("production_ready", payload["production_ready"]),
        ("customer_validated", payload["customer_validated"]),
        ("product_launched", payload["product_launched"]),
        ("private_core_exposed", payload["private_core_exposed"]),
    ]
    boundary_html = "\n".join(
        f"<li><strong>{escape(key)}:</strong> {escape(bool_text(value) if isinstance(value, bool) else value)}</li>"
        for key, value in boundary_items
    )
    blank_template_json = json.dumps(first_owner_blank_template(), ensure_ascii=False, indent=2)

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 支持联系人负责人填写页</title>
  <style>
    :root {{
      --bg: #f8f7f2;
      --text: #171717;
      --muted: #5f675f;
      --line: #dedbd2;
      --card: #fffdf8;
      --accent: #10a37f;
      --accent-soft: #e5f3ed;
      --warn: #8a5a10;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(135deg, #fffdf8 0%, var(--bg) 62%, #edf4ef 100%);
      color: var(--text);
      line-height: 1.55;
    }}
    main {{
      width: min(1040px, calc(100% - 32px));
      margin: 0 auto;
      padding: 42px 0 58px;
    }}
    header {{
      padding: 34px 0 24px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{ color: var(--accent); font-weight: 700; }}
    h1 {{
      max-width: 780px;
      margin: 12px 0 14px;
      font-size: clamp(32px, 6vw, 66px);
      line-height: 1.04;
      letter-spacing: 0;
    }}
    .lead {{
      max-width: 760px;
      color: var(--muted);
      font-size: 18px;
      margin: 0;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 28px 0;
    }}
    .stat, section {{
      background: rgba(255, 253, 248, 0.9);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 18px;
      box-shadow: 0 18px 45px rgba(23, 23, 23, 0.06);
    }}
    .stat strong {{
      display: block;
      color: var(--accent);
      font-size: 34px;
      line-height: 1;
    }}
    .stat span, p {{ color: var(--muted); }}
    section {{ margin: 24px 0; overflow-x: auto; }}
    h2 {{ margin: 0 0 12px; font-size: 24px; letter-spacing: 0; }}
    table {{
      width: 100%;
      min-width: 680px;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      background: rgba(229, 243, 237, 0.62);
    }}
    code, pre {{
      background: rgba(23, 23, 23, 0.06);
      border-radius: 8px;
    }}
    code {{ padding: 2px 6px; }}
    pre {{
      padding: 14px;
      white-space: pre-wrap;
      overflow-x: auto;
    }}
    .template-box {{
      max-height: 520px;
      border: 1px solid var(--line);
    }}
    .notice {{
      background: var(--accent-soft);
      border-color: rgba(16, 163, 127, 0.28);
    }}
    .warning {{
      background: #fff6df;
      border-color: #ead59a;
      color: var(--warn);
    }}
    ul {{ margin: 10px 0 0; padding-left: 20px; }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">SAEE 商用第一步</div>
      <h1>先指定“支持联系人”的真人负责人。</h1>
      <p class="lead">这是 support_contact 阻塞项的负责人填写页。它只告诉人该填哪 5 个字段，不会自动分配负责人、不会联系任何人、不会收集证据。</p>
    </header>

    <div class="stats">
      <div class="stat"><strong>{payload['required_human_field_count']}</strong><span>需要人工填写的字段</span></div>
      <div class="stat"><strong>{payload['completed_human_field_count']}</strong><span>当前已填写字段</span></div>
      <div class="stat"><strong>{payload['missing_human_field_count']}</strong><span>仍缺字段</span></div>
      <div class="stat"><strong>0</strong><span>已关闭 blocker</span></div>
    </div>

    <section class="notice">
      <h2>人现在该做什么</h2>
      <p>把下面 5 个字段填进本地输入文件，然后再运行本地 validator。不要在这一步收集证据、联系客户或关闭 blocker。</p>
    </section>

    <section>
      <h2>需要填写的 5 个字段</h2>
      <table>
        <thead>
          <tr>
            <th>字段</th>
            <th>怎么填</th>
            <th>当前状态</th>
          </tr>
        </thead>
        <tbody>{''.join(field_rows)}</tbody>
      </table>
    </section>

    <section>
      <h2>本地生成命令模板</h2>
      <p>人把占位符替换成真实的人审信息后，再运行该命令。</p>
      <pre>{escape(payload['next_generation_command_template'])}</pre>
    </section>

    <section>
      <h2>空白 JSON 模板</h2>
      <p>如果不想用命令行参数，也可以按这个结构填写本地文件：<code>{escape(rel(RECOMMENDED_HUMAN_FILLED_INPUT))}</code>。只填真人负责人和内部人审信息，不要写客户隐私、密钥、外部账号密码或私有核心内容。</p>
      <pre class="template-box">{escape(blank_template_json)}</pre>
    </section>

    <section>
      <h2>下一条本地验证命令</h2>
      <pre>{escape(payload['next_validator_command'])} --input {escape(rel(RECOMMENDED_HUMAN_FILLED_INPUT))}</pre>
    </section>

    <section class="warning">
      <h2>边界</h2>
      <p>这个页面不是执行批准，也不是生产就绪证明。</p>
      <ul>{boundary_html}</ul>
    </section>
  </main>
</body>
</html>
"""
    OUTPUT_HTML.write_text(html_text, encoding="utf-8")


def write_csv() -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "field_name",
                "required",
                "provided",
                "human_instruction",
                "must_not_do",
            ],
        )
        writer.writeheader()
        for field in REQUIRED_FIELDS:
            writer.writerow(
                {
                    "field_name": field,
                    "required": "true",
                    "provided": "false",
                    "human_instruction": "Fill this value manually before running the completion helper.",
                    "must_not_do": "Codex must not infer, assign, contact, or approve this field.",
                }
            )


def markdown_lines(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# SAEE First Owner Input Request Packet",
        "",
        "first_owner_input_request_packet_v0_1: true",
        f"status: {payload['status']}",
        f"action_id: {payload['action_id']}",
        "first_blocker_id: support_contact",
        "sequence_step_id: SEQ-001",
        "request_packet_ready: true",
        "required_human_field_count: 5",
        "completed_human_field_count: 0",
        "missing_human_field_count: 5",
        "owner_assigned_by_codex: false",
        "owner_contacted_by_codex: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_request_packet: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "local_static_first_owner_input_request_html: true",
        "browser_readable_first_owner_input_request: true",
        "copy_ready_blank_json_template_in_html: true",
        f"source_first_owner_input_request_html: {payload['source_first_owner_input_request_html']}",
        f"source_first_owner_input_template: {payload['source_first_owner_input_template']}",
        f"recommended_human_filled_input_path: {payload['recommended_human_filled_input_path']}",
        "",
        "## Purpose",
        "",
        "This packet turns the current commercial next action into a bounded human input request for the `support_contact` first-owner step.",
        "",
        "## Required Human Fields",
        "",
    ]
    for field in REQUIRED_FIELDS:
        lines.append(f"- `{field}`")
    lines.extend(
        [
            "",
            "## Human Procedure",
            "",
            "1. Fill the five required fields in `first_owner_input_completion.csv` or provide them to the completion helper command.",
            "2. Generate `first_owner_input.human_filled.local.json` with the completion helper.",
            "3. Run the first-owner input validator on the generated JSON.",
            "4. Stop. Evidence collection and blocker closure require later separate approvals.",
            "",
            "## Browser-Readable Entry",
            "",
            f"`{payload['source_first_owner_input_request_html']}`",
            "",
            "## Blank JSON Template",
            "",
            "A human may fill the blank local template and save it as the recommended human-filled input path before running the validator.",
            "",
            f"- source template: `{payload['source_first_owner_input_template']}`",
            f"- recommended filled input path: `{payload['recommended_human_filled_input_path']}`",
            "- do not include customer secrets, passwords, external account credentials, private-core content, or raw customer data.",
            "",
            "## Command Template",
            "",
            "```bash",
            str(payload["next_generation_command_template"]),
            "```",
            "",
            "## Validator Command",
            "",
            "```bash",
            str(payload["next_validator_command"]),
            "```",
            "",
            "## Boundary",
            "",
            "This packet does not assign an owner, contact an owner, contact customers or vendors, collect evidence, execute tasks, close blockers, launch product, or claim production readiness.",
            "",
        ]
    )
    return lines


def write_markdown(payload: dict[str, Any]) -> None:
    text = "\n".join(markdown_lines(payload))
    OUTPUT_MD.write_text(text, encoding="utf-8")
    TOP_DOC.write_text(text, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    text = f"""# SAEE Commercial Evidence Sprint First Owner Input Request Packet Recommendation Gate

answer: recommend
recommend_for_human_first_owner_input_request: true
recommend_for_owner_assignment_by_codex: false
recommend_for_evidence_collection: false
recommend_for_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

reason: This packet makes the current support_contact first-owner human input step explicit and reviewable without assigning owners, contacting anyone, collecting evidence, executing work, closing blockers, or claiming production readiness.

status: {payload['status']}
action_id: {payload['action_id']}
first_blocker_id: support_contact
sequence_step_id: SEQ-001
required_human_field_count: 5
completed_human_field_count: 0
missing_human_field_count: 5
owner_assigned_by_codex: false
owner_contacted_by_codex: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_request_packet: 0
production_ready: false
customer_validated: false
product_launched: false
local_static_first_owner_input_request_html: true
browser_readable_first_owner_input_request: true
source_first_owner_input_request_html: {payload['source_first_owner_input_request_html']}
source_first_owner_input_template: {payload['source_first_owner_input_template']}
recommended_human_filled_input_path: {payload['recommended_human_filled_input_path']}
copy_ready_blank_json_template_in_html: true

next_action: Human fills the five required owner fields, then runs the first-owner input validator. Evidence collection requires a separate approved request.
"""
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(text, encoding="utf-8")


def main() -> None:
    action = load_next_action()
    payload = build_payload(action)
    write_json(OUTPUT_JSON, payload)
    write_csv()
    write_html(payload)
    write_markdown(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_EVIDENCE_SPRINT_FIRST_OWNER_INPUT_REQUEST_PACKET: "
        f"PASS status={payload['status']} required_human_field_count=5 "
        "blockers_closed_by_request_packet=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
