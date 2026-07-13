#!/usr/bin/env python3
"""Build a unified human-input entrypoint for the support_contact blocker.

This script links the 10-row commercial fill card, the combined support-contact
bridge template, the bridge completion helper, the existing validators, and the
support-contact readiness board into one agent-readable navigation surface.

It does not generate or enter values, export human-filled validator inputs,
run validators, configure or publish support, collect evidence, close blockers,
contact anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"
SUPPORT_DIR = COMMERCIAL_DIR / "support_evidence"
BRIDGE_DIR = SUPPORT_DIR / "support_contact_human_input_bridge"

FILL_CARD_JSON = SPRINT_DIR / "commercial_review_batch_human_fill_card.local.json"
FILL_CARD_MD = SPRINT_DIR / "commercial_review_batch_human_fill_card.md"
BRIDGE_TEMPLATE = BRIDGE_DIR / "support_contact_human_input_bridge_input.template.json"
BRIDGE_GUIDE = BRIDGE_DIR / "support_contact_human_input_bridge_completion_guide.md"
READINESS_BOARD_JSON = SUPPORT_DIR / "support_contact_readiness_board.local.json"
READINESS_BOARD_MD = SUPPORT_DIR / "support_contact_readiness_board.md"
DECISION_PACKET_JSON = SUPPORT_DIR / "support_contact_decision_packet.local.json"

OUT_JSON = SUPPORT_DIR / "support_contact_human_input_entrypoint.local.json"
OUT_MD = SUPPORT_DIR / "support_contact_human_input_entrypoint.md"
OUT_HTML = SUPPORT_DIR / "support_contact_human_input_entrypoint.html"
OUT_CSV = SUPPORT_DIR / "support_contact_human_input_entrypoint.csv"
OUT_AUDIT = SUPPORT_DIR / "support_contact_human_input_entrypoint_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "SUPPORT_CONTACT_HUMAN_INPUT_ENTRYPOINT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_INPUT_ENTRYPOINT_RECOMMENDATION_GATE.md"

FALSE_FLAGS = [
    "raw_values_recorded",
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "human_input_filled_by_codex",
    "validator_inputs_exported",
    "validators_run",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "customer_facing_support_contact_configured",
    "customer_support_available",
    "production_support_available",
    "support_process_available",
    "sla_available",
    "on_call_rotation_available",
    "workbook_import_authorized",
    "workbook_import_performed",
    "evidence_collection_authorized",
    "execution_authorized",
    "blocker_closure_authorized",
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
    "support_vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "task_candidates_executed",
    "production_ready_claim",
    "customer_validation_claim",
]

SUPPORT_KEYS = [
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"SAEE_SUPPORT_CONTACT_HUMAN_INPUT_ENTRYPOINT: FAIL {rel(path)} must be object")
    return value


def missing_first_owner_fields(template: dict[str, Any]) -> list[str]:
    first_owner = template.get("first_owner_input", {})
    if not isinstance(first_owner, dict):
        return ["first_owner_input"]
    missing: list[str] = []
    for field in [
        "assigned_human_owner",
        "owner_contact_reference",
        "target_review_date",
        "human_approval_reference",
    ]:
        if not str(first_owner.get(field, "")).strip():
            missing.append(f"first_owner_input.{field}")
    if first_owner.get("owner_acknowledged_scope") is not True:
        missing.append("first_owner_input.owner_acknowledged_scope")
    return missing


def missing_support_decision_fields(template: dict[str, Any]) -> list[str]:
    support = template.get("support_contact_decision_input", {})
    if not isinstance(support, dict):
        return ["support_contact_decision_input"]
    missing: list[str] = []
    for field in [
        "human_reviewer_name",
        "review_date",
        "selected_support_contact_channel",
        "decision_summary",
    ]:
        if not str(support.get(field, "")).strip():
            missing.append(f"support_contact_decision_input.{field}")
    review = support.get("evidence_review", {})
    notes = support.get("source_notes_by_key", {})
    if not isinstance(review, dict):
        missing.append("support_contact_decision_input.evidence_review")
        review = {}
    if not isinstance(notes, dict):
        missing.append("support_contact_decision_input.source_notes_by_key")
        notes = {}
    for key in SUPPORT_KEYS:
        if review.get(key) is not True:
            missing.append(f"support_contact_decision_input.evidence_review.{key}")
        if not str(notes.get(key, "")).strip():
            missing.append(f"support_contact_decision_input.source_notes_by_key.{key}")
    slots = support.get("candidate_contact_slots", [])
    complete_slots = 0
    if isinstance(slots, list):
        for slot in slots:
            if not isinstance(slot, dict):
                continue
            if (
                str(slot.get("contact_channel", "")).strip()
                and str(slot.get("display_value_redacted", "")).strip()
                and str(slot.get("human_source_note", "")).strip()
                and slot.get("owner_named") is True
                and slot.get("abuse_handling_reviewed") is True
                and slot.get("customer_notice_route_reviewed") is True
                and slot.get("test_plan_reviewed") is True
            ):
                complete_slots += 1
    if complete_slots < 1:
        missing.append("support_contact_decision_input.candidate_contact_slots")
    return missing


def build_steps() -> list[dict[str, Any]]:
    return [
        {
            "step_id": "SCHIE-001",
            "title": "先看 10 行填写卡",
            "entrypoint": rel(FILL_CARD_MD),
            "command": "打开填写卡，确认要补的 10 行；不要让 Codex 代填。",
            "execution_allowed": False,
            "human_action_required": True,
        },
        {
            "step_id": "SCHIE-002",
            "title": "人工填写支持入口合并表",
            "entrypoint": rel(BRIDGE_TEMPLATE),
            "command": "复制模板为 support_contact_human_input_bridge_input.human_filled.local.json，只由人填写真实负责人和支持入口信息。",
            "execution_allowed": False,
            "human_action_required": True,
        },
        {
            "step_id": "SCHIE-003",
            "title": "人工填完后导出本地检查输入",
            "entrypoint": rel(BRIDGE_GUIDE),
            "command": "python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py --combined-input phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json",
            "execution_allowed": False,
            "human_action_required": True,
        },
        {
            "step_id": "SCHIE-004",
            "title": "导出后再跑两个本地检查",
            "entrypoint": "scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py and scripts/saee_support_contact_approval_input_validator.py",
            "command": "只有人工填写并导出检查输入后，才分别运行负责人检查和支持入口决策检查。",
            "execution_allowed": False,
            "human_action_required": True,
        },
        {
            "step_id": "SCHIE-005",
            "title": "刷新支持入口准备度看板",
            "entrypoint": rel(READINESS_BOARD_MD),
            "command": "python3 scripts/saee_support_contact_readiness_board.py",
            "execution_allowed": False,
            "human_action_required": True,
        },
    ]


def build_payload() -> dict[str, Any]:
    fill_card = read_json(FILL_CARD_JSON)
    bridge_template = read_json(BRIDGE_TEMPLATE)
    readiness = read_json(READINESS_BOARD_JSON)
    decision = read_json(DECISION_PACKET_JSON)
    missing_first_owner = missing_first_owner_fields(bridge_template)
    missing_support = missing_support_decision_fields(bridge_template)
    payload: dict[str, Any] = {
        "support_contact_human_input_entrypoint_v0_1": True,
        "entrypoint_type": "support_contact_human_input_navigation",
        "entrypoint_scope": "unified_human_input_navigation_only_no_values_no_export_no_execution",
        "status": "ready_for_human_support_contact_input_navigation",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "support_contact",
        "plain_language_support_contact_entry_v0_2": True,
        "plain_language_status_label": "支持入口仍未配置",
        "plain_language_next_action": "先指定负责人，再人工填写支持入口信息。",
        "plain_language_stop_point": "只到本地检查为止；没有单独批准，不发布支持入口、不关闭阻塞项。",
        "support_contact_human_route_step_count": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_support_contact_human_input_entrypoint.py",
        "source_fill_card_json": rel(FILL_CARD_JSON),
        "source_fill_card_markdown": rel(FILL_CARD_MD),
        "source_bridge_template": rel(BRIDGE_TEMPLATE),
        "source_bridge_guide": rel(BRIDGE_GUIDE),
        "source_readiness_board_json": rel(READINESS_BOARD_JSON),
        "source_readiness_board_markdown": rel(READINESS_BOARD_MD),
        "source_decision_packet_json": rel(DECISION_PACKET_JSON),
        "source_support_contact_human_input_entrypoint_html": rel(OUT_HTML),
        "local_static_support_contact_human_input_entrypoint_html": True,
        "browser_readable_support_contact_human_input_entrypoint": True,
        "review_batch_fill_card_row_count": int(fill_card.get("fill_card_row_count", 0)),
        "review_batch_blank_value_row_count": int(fill_card.get("blank_human_value_row_count", 0)),
        "combined_bridge_input_row_count": int(bridge_template.get("combined_input_row_count", 0)),
        "readiness_step_count": int(readiness.get("readiness_step_count", 0)),
        "readiness_completed_step_count": int(readiness.get("completed_step_count", 0)),
        "readiness_incomplete_step_count": int(readiness.get("incomplete_step_count", 0)),
        "missing_first_owner_field_count": len(missing_first_owner),
        "missing_support_decision_field_count": len(missing_support),
        "missing_first_owner_fields": missing_first_owner,
        "missing_support_decision_fields": missing_support,
        "decision_required_human_field_count": len(decision.get("required_human_decision_fields", [])),
        "steps": build_steps(),
        "human_input_required": True,
        "human_review_required": True,
        "blockers_closed_by_entrypoint": 0,
        "next_human_action": (
            "先看 10 行填写卡，再复制合并输入模板并由人填写真实负责人和支持入口信息。"
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = ["step_id", "title", "entrypoint", "command", "execution_allowed", "human_action_required"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for step in payload["steps"]:
            writer.writerow({field: step.get(field, "") for field in fields})


def write_markdown(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {step_id} | {title} | `{entrypoint}` | `{command}` | {execution_allowed} |".format(
            **step
        )
        for step in payload["steps"]
    )
    body = f"""# SAEE Support Contact Human Input Entrypoint v0.1

support_contact_human_input_entrypoint_v0_1: true
entrypoint_scope: {payload['entrypoint_scope']}
status: {payload['status']}
commercial_status: {payload['commercial_status']}
production_launch_status: {payload['production_launch_status']}
target_blocker_id: {payload['target_blocker_id']}
plain_language_support_contact_entry_v0_2: true
plain_language_status_label: {payload['plain_language_status_label']}
plain_language_next_action: {payload['plain_language_next_action']}
plain_language_stop_point: {payload['plain_language_stop_point']}
support_contact_human_route_step_count: {payload['support_contact_human_route_step_count']}

## Summary

- review_batch_fill_card_row_count: {payload['review_batch_fill_card_row_count']}
- combined_bridge_input_row_count: {payload['combined_bridge_input_row_count']}
- local_static_support_contact_human_input_entrypoint_html: true
- browser_readable_support_contact_human_input_entrypoint: true
- source_support_contact_human_input_entrypoint_html: `{payload['source_support_contact_human_input_entrypoint_html']}`
- readiness_step_count: {payload['readiness_step_count']}
- readiness_completed_step_count: {payload['readiness_completed_step_count']}
- missing_first_owner_field_count: {payload['missing_first_owner_field_count']}
- missing_support_decision_field_count: {payload['missing_support_decision_field_count']}
- blockers_closed_by_entrypoint: 0
- production_ready: false
- customer_validated: false
- product_launched: false

## Purpose

这个文件是当前 `support_contact` 商用阻塞项的人工填写入口。
它把 10 行填写卡、合并输入模板、导出工具、本地检查和准备度看板串起来。
它不是联系人来源，不会替人填写，也不会执行发布、收集证据或关闭阻塞项。

## Steps

| 步骤 | 要做什么 | 入口 | 命令 / 人工动作 | 是否允许 Codex 执行 |
| --- | --- | --- | --- | --- |
{rows}

## Missing Human Fields

### First Owner

{chr(10).join('- `' + field + '`' for field in payload['missing_first_owner_fields'])}

### Support Decision

{chr(10).join('- `' + field + '`' for field in payload['missing_support_decision_fields'])}

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- human_input_filled_by_codex: false
- validator_inputs_exported: false
- validators_run: false
- support_contact_configured: false
- support_contact_published: false
- support_contact_test_performed: false
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


def write_html(payload: dict[str, Any]) -> None:
    step_cards = "\n".join(
        f"""
        <article>
          <p class=\"step-id\">{step['step_id']}</p>
          <h2>{step['title']}</h2>
          <p><strong>入口：</strong><code>{step['entrypoint']}</code></p>
          <p><strong>人工动作：</strong><code>{step['command']}</code></p>
          <p class=\"safe\">Codex 可代执行：false · 需要人工操作：true</p>
        </article>
        """
        for step in payload["steps"]
    )
    first_owner_fields = "\n".join(
        f"<li><code>{field}</code></li>" for field in payload["missing_first_owner_fields"]
    )
    support_fields = "\n".join(
        f"<li><code>{field}</code></li>" for field in payload["missing_support_decision_fields"]
    )
    body = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 支持入口人工填写</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f8f6;
        --surface: #ffffff;
        --surface-soft: #edf1ee;
        --text: #161918;
        --muted: #5f6863;
        --line: #dde4df;
        --accent: #0f766e;
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
        width: min(1120px, calc(100% - 32px));
        margin: 0 auto;
        padding: 48px 0 64px;
      }}
      header {{
        display: grid;
        gap: 16px;
        padding: 34px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: linear-gradient(135deg, #ffffff 0%, #e6f4f1 100%);
      }}
      h1 {{
        margin: 0;
        max-width: 820px;
        font-size: clamp(30px, 5vw, 56px);
        line-height: 1.06;
        letter-spacing: 0;
      }}
      h2 {{ margin: 0 0 10px; font-size: 20px; }}
      p {{ margin: 0; }}
      .kicker {{
        color: var(--accent);
        font-size: 13px;
        font-weight: 800;
      }}
      .lead {{
        max-width: 760px;
        color: var(--muted);
        font-size: 18px;
      }}
      .metrics, .steps, .fields, .boundary {{
        display: grid;
        gap: 14px;
        margin-top: 22px;
      }}
      .metrics {{
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }}
      .metric, article, .field-card, .boundary {{
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
      }}
      .metric {{ padding: 18px; }}
      .metric strong {{ display: block; font-size: 28px; line-height: 1.1; }}
      .metric span {{ color: var(--muted); font-size: 13px; }}
      .steps {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      article {{ padding: 20px; }}
      code {{
        padding: 2px 5px;
        border-radius: 6px;
        background: var(--surface-soft);
        font-size: 0.92em;
        overflow-wrap: anywhere;
      }}
      .step-id {{
        margin-bottom: 8px;
        color: var(--accent);
        font-size: 12px;
        font-weight: 800;
      }}
      .safe {{ margin-top: 10px; color: var(--muted); font-size: 13px; }}
      .fields {{
        grid-template-columns: 1fr 1fr;
      }}
      .field-card {{ padding: 22px; }}
      ul {{ margin: 12px 0 0; padding-left: 20px; }}
      li {{ margin: 7px 0; }}
      .boundary {{
        padding: 22px;
        background: #fff;
      }}
      .boundary ul {{
        columns: 2;
      }}
      .warning {{
        color: var(--danger);
        font-weight: 800;
      }}
      @media (max-width: 820px) {{
        .metrics, .steps, .fields {{ grid-template-columns: 1fr; }}
        header {{ padding: 24px; }}
        .boundary ul {{ columns: 1; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="kicker">支持入口仍未配置</p>
        <h1>先指定负责人，再填写支持入口。</h1>
        <p class="lead">
          这是当前商用阻塞项 <strong>support_contact</strong> 的浏览器可读入口。它只告诉人该填什么、看哪个文件、跑哪个本地检查；不会生成联系人、不会发布支持入口、不会联系客户，也不会关闭阻塞项。
        </p>
      </header>

      <section class="metrics" aria-label="当前状态">
        <div class="metric"><strong>{payload['review_batch_fill_card_row_count']}</strong><span>10 行填写卡</span></div>
        <div class="metric"><strong>{payload['combined_bridge_input_row_count']}</strong><span>合并输入字段</span></div>
        <div class="metric"><strong>{payload['missing_first_owner_field_count']}</strong><span>缺少负责人字段</span></div>
        <div class="metric"><strong>{payload['missing_support_decision_field_count']}</strong><span>缺少支持入口决策字段</span></div>
      </section>

      <section class="steps" aria-label="人工步骤">
        {step_cards}
      </section>

      <section class="fields" aria-label="缺失字段">
        <div class="field-card">
          <h2>先补负责人字段</h2>
          <p>这些字段需要真人填写，Codex 不会猜。</p>
          <ul>{first_owner_fields}</ul>
        </div>
        <div class="field-card">
          <h2>再补支持入口决策字段</h2>
          <p>这些字段需要真实来源和人工确认。</p>
          <ul>{support_fields}</ul>
        </div>
      </section>

      <section class="boundary" aria-label="边界">
        <h2>边界</h2>
        <p class="warning">这不是生产发布，也不是客户支持入口已经可用。</p>
        <ul>
          <li>support_contact_configured: false</li>
          <li>support_contact_published: false</li>
          <li>support_contact_test_performed: false</li>
          <li>human_values_generated_by_codex: false</li>
          <li>validator_inputs_exported: false</li>
          <li>validators_run: false</li>
          <li>evidence_collection_authorized: false</li>
          <li>execution_authorized: false</li>
          <li>blockers_closed_by_entrypoint: 0</li>
          <li>production_ready: false</li>
          <li>customer_validated: false</li>
          <li>product_launched: false</li>
          <li>runtime_modified: false</li>
          <li>backend_modified: false</li>
          <li>kernel_modified: false</li>
          <li>api_schema_modified: false</li>
          <li>private_core_exposed: false</li>
        </ul>
      </section>
    </main>
  </body>
</html>
"""
    OUT_HTML.write_text(body, encoding="utf-8")


def write_audit(payload: dict[str, Any]) -> None:
    OUT_AUDIT.write_text(
        f"""# Support Contact Human Input Entrypoint Boundary Audit

- navigation_surface_only: true
- values_generated: false
- values_entered: false
- validator_inputs_exported: false
- validators_run: false
- support_contact_configured: false
- support_contact_published: false
- support_contact_test_performed: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_entrypoint: {payload['blockers_closed_by_entrypoint']}
""",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        f"""# SAEE Support Contact Human Input Entrypoint Recommendation Gate

answer: recommend
recommend_for_human_input_navigation: true
recommend_for_value_generation: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_support_contact_publication: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

This entrypoint improves the human path for the first active commercial blocker
without generating values or granting execution permission. The browser-readable
surface now uses plain Chinese instructions for owner assignment, support-contact
decision entry, local export, local validation, and readiness-board refresh.

## Status

- status: {payload['status']}
- target_blocker_id: support_contact
- plain_language_support_contact_entry_v0_2: true
- plain_language_status_label: {payload['plain_language_status_label']}
- plain_language_next_action: {payload['plain_language_next_action']}
- plain_language_stop_point: {payload['plain_language_stop_point']}
- missing_first_owner_field_count: {payload['missing_first_owner_field_count']}
- missing_support_decision_field_count: {payload['missing_support_decision_field_count']}
- production_ready: false
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_gate(payload)
    print(
        "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_ENTRYPOINT: PASS "
        f"status={payload['status']} target_blocker_id=support_contact "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
