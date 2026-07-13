#!/usr/bin/env python3
"""Generate the first-priority support-contact human packet.

The packet turns the current first commercial blocker into a short human
navigation surface. It does not create support contacts, fill values, run
validators, export inputs, import workbooks, collect evidence, close blockers,
or change product behavior.
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SUPPORT_DIR = COMMERCIAL_DIR / "support_evidence"
OUT_DIR = SUPPORT_DIR / "support_contact_first_priority_packet"
OUT_JSON = OUT_DIR / "support_contact_first_priority_packet.local.json"
OUT_MD = OUT_DIR / "support_contact_first_priority_packet.md"
OUT_CSV = OUT_DIR / "support_contact_first_priority_packet.csv"
OUT_HTML = OUT_DIR / "support_contact_first_priority_packet.html"
OUT_AUDIT = OUT_DIR / "support_contact_first_priority_packet_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_FIRST_PRIORITY_PACKET_GATE.md"

PRIORITY_JSON = (
    COMMERCIAL_DIR
    / "commercial_blocker_priority_index/commercial_blocker_priority_index.local.json"
)
FILL_CARD_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.local.json"
)
ENTRYPOINT_JSON = SUPPORT_DIR / "support_contact_human_input_entrypoint.local.json"
APPROVAL_PROMPT_JSON = SUPPORT_DIR / "support_contact_approval_input_prompt.local.json"
READINESS_BOARD_JSON = SUPPORT_DIR / "support_contact_readiness_board.local.json"
BRIDGE_TEMPLATE = (
    SUPPORT_DIR
    / "support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bool_text(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def source(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_payload() -> dict[str, Any]:
    priority = load_json(PRIORITY_JSON)
    fill_card = load_json(FILL_CARD_JSON)
    entrypoint = load_json(ENTRYPOINT_JSON)
    approval_prompt = load_json(APPROVAL_PROMPT_JSON)
    readiness = load_json(READINESS_BOARD_JSON)
    bridge_template = load_json(BRIDGE_TEMPLATE)

    first_row = priority.get("priority_rows", [{}])[0]
    false_boundaries = {
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
        "raw_values_recorded": False,
        "human_values_generated_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "human_input_filled_by_codex": False,
        "validator_inputs_exported": False,
        "validators_run": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "support_contact_claim_published": False,
    }

    human_steps = [
        {
            "step_id": "SCFP-001",
            "title": "先打开 10 行填写卡",
            "entrypoint": fill_card["source_template_csv"],
            "human_action": "只填写 human_value_to_enter 和 notes_for_human 两列；没有人工确认就留空。",
            "codex_execution_allowed": False,
        },
        {
            "step_id": "SCFP-002",
            "title": "复制支持入口合并模板",
            "entrypoint": source(BRIDGE_TEMPLATE),
            "human_action": "复制为 support_contact_human_input_bridge_input.human_filled.local.json 后由人填写。",
            "codex_execution_allowed": False,
        },
        {
            "step_id": "SCFP-003",
            "title": "填写负责人信息",
            "entrypoint": "first_owner_input",
            "human_action": "填写负责人、内部记录、目标日期、审批引用和范围确认。",
            "codex_execution_allowed": False,
        },
        {
            "step_id": "SCFP-004",
            "title": "填写支持入口判断",
            "entrypoint": "support_contact_decision_input",
            "human_action": "由人确认支持渠道、负责人、滥用处理、客户通知路径、测试记录和来源说明。",
            "codex_execution_allowed": False,
        },
        {
            "step_id": "SCFP-005",
            "title": "人工填完后导出本地检查输入",
            "entrypoint": (
                "phase_b_product/commercial_readiness/support_evidence/"
                "support_contact_human_input_bridge/support_contact_human_input_bridge_completion_guide.md"
            ),
            "human_action": (
                "运行 completion helper，但只在人工填写完成后运行；不要发布支持入口。"
            ),
            "codex_execution_allowed": False,
        },
        {
            "step_id": "SCFP-006",
            "title": "运行本地验证并刷新看板",
            "entrypoint": "scripts/saee_support_contact_approval_input_validator.py",
            "human_action": "分别运行负责人检查、支持入口输入检查和 readiness board 刷新。",
            "codex_execution_allowed": False,
        },
    ]

    payload: dict[str, Any] = {
        "support_contact_first_priority_packet_v0_1": True,
        "packet_type": "support_contact_first_priority_human_packet",
        "packet_scope": "first_priority_human_navigation_only_no_values_no_export_no_execution",
        "status": "hold_human_support_contact_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "support_contact",
        "source_priority_index": source(PRIORITY_JSON),
        "source_fill_card_json": source(FILL_CARD_JSON),
        "source_fill_card_markdown": fill_card.get("source_template_csv", ""),
        "source_human_entrypoint_json": source(ENTRYPOINT_JSON),
        "source_human_entrypoint_html": entrypoint.get(
            "source_support_contact_human_input_entrypoint_html", ""
        ),
        "source_bridge_template": source(BRIDGE_TEMPLATE),
        "source_approval_prompt_json": source(APPROVAL_PROMPT_JSON),
        "source_readiness_board_json": source(READINESS_BOARD_JSON),
        "first_priority_rank": first_row.get("rank", 1),
        "first_priority_tier": first_row.get("priority_tier", "active_10_row_review_batch"),
        "review_batch_fill_card_row_count": fill_card.get("fill_card_row_count", 10),
        "review_batch_blank_value_row_count": fill_card.get("blank_human_value_row_count", 10),
        "combined_bridge_input_row_count": bridge_template.get("combined_input_row_count", 16),
        "missing_first_owner_field_count": entrypoint.get("missing_first_owner_field_count", 5),
        "missing_support_decision_field_count": entrypoint.get(
            "missing_support_decision_field_count", 15
        ),
        "candidate_contact_slot_count": approval_prompt.get("candidate_contact_slot_count", 2),
        "minimum_completed_contact_slot_count": approval_prompt.get(
            "minimum_completed_contact_slot_count", 1
        ),
        "readiness_step_count": entrypoint.get("readiness_step_count", 5),
        "readiness_completed_step_count": entrypoint.get("readiness_completed_step_count", 0),
        "readiness_incomplete_step_count": entrypoint.get("readiness_incomplete_step_count", 5),
        "readiness_board_status": readiness.get("status", "hold"),
        "human_review_required": True,
        "human_input_required": True,
        "make_target": "make check-support-contact-first-priority-packet",
        "human_steps": human_steps,
        "next_human_action": (
            "Open this packet, fill the support_contact 10-row review batch and "
            "the combined bridge template manually, then run local validators. "
            "Stop before support-contact publication, external contact, evidence "
            "builder execution, workbook import, or blocker closure."
        ),
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    payload.update(false_boundaries)
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = ["step_id", "title", "entrypoint", "human_action", "codex_execution_allowed"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["human_steps"]:
            writer.writerow(row)


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Support Contact First Priority Packet v0.1",
        "",
        "`support_contact_first_priority_packet_v0_1: true`",
        "",
        "## 当前结论",
        "",
        "这是 `support_contact` 第一优先阻塞项的人审导航包。它只告诉人下一步怎么填，",
        "不会生成联系人、不会发布支持入口、不会联系客户、不会导入工作簿、不会关闭 blocker。",
        "",
        "## 当前状态",
        "",
        f"- `status: {payload['status']}`",
        f"- `target_blocker_id: {payload['target_blocker_id']}`",
        f"- `first_priority_rank: {payload['first_priority_rank']}`",
        f"- `review_batch_fill_card_row_count: {payload['review_batch_fill_card_row_count']}`",
        f"- `review_batch_blank_value_row_count: {payload['review_batch_blank_value_row_count']}`",
        f"- `combined_bridge_input_row_count: {payload['combined_bridge_input_row_count']}`",
        f"- `missing_first_owner_field_count: {payload['missing_first_owner_field_count']}`",
        f"- `missing_support_decision_field_count: {payload['missing_support_decision_field_count']}`",
        "- `production_ready: false`",
        "- `product_launched: false`",
        "- `customer_validated: false`",
        "",
        "## 人工步骤",
        "",
        "| Step | 要做什么 | 入口 | 人工动作 | Codex 可执行 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in payload["human_steps"]:
        lines.append(
            "| {step_id} | {title} | `{entrypoint}` | {human_action} | {allowed} |".format(
                step_id=step["step_id"],
                title=step["title"],
                entrypoint=step["entrypoint"],
                human_action=step["human_action"],
                allowed=step["codex_execution_allowed"],
            )
        )
    lines.extend(
        [
            "",
            "## 关键入口",
            "",
            f"- 10 行填写卡 JSON：`{payload['source_fill_card_json']}`",
            f"- 支持入口总入口 HTML：`{payload['source_human_entrypoint_html']}`",
            f"- 合并输入模板：`{payload['source_bridge_template']}`",
            f"- 支持入口输入提示 JSON：`{payload['source_approval_prompt_json']}`",
            f"- 准备度看板 JSON：`{payload['source_readiness_board_json']}`",
            "",
            "## 边界",
            "",
            "- `raw_values_recorded: false`",
            "- `human_values_generated_by_codex: false`",
            "- `quick_fill_values_entered_by_codex: false`",
            "- `validator_inputs_exported: false`",
            "- `validators_run: false`",
            "- `support_contact_configured: false`",
            "- `support_contact_published: false`",
            "- `support_contact_test_performed: false`",
            "- `workbook_import_authorized: false`",
            "- `evidence_collection_authorized: false`",
            "- `execution_authorized: false`",
            "- `blocker_closure_authorized: false`",
            "- `runtime_modified: false`",
            "- `backend_modified: false`",
            "- `kernel_modified: false`",
            "- `api_schema_modified: false`",
            "- `private_core_exposed: false`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    step_rows = []
    for step in payload["human_steps"]:
        step_rows.append(
            "<tr>"
            f"<td>{html.escape(step['step_id'])}</td>"
            f"<td>{html.escape(step['title'])}</td>"
            f"<td><code>{html.escape(step['entrypoint'])}</code></td>"
            f"<td>{html.escape(step['human_action'])}</td>"
            "</tr>"
        )
    text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 支持入口第一阻塞项人审包</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f7f4; color: #202124; }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 48px 20px; }}
    h1 {{ font-size: 40px; line-height: 1.1; margin: 0 0 12px; }}
    p, li {{ line-height: 1.7; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 28px 0; }}
    .card {{ background: white; border: 1px solid #e4e1da; border-radius: 14px; padding: 18px; box-shadow: 0 12px 40px rgba(15,17,21,.06); }}
    .label {{ color: #6f6f68; font-size: 13px; }}
    .value {{ font-size: 24px; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #e4e1da; border-radius: 14px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #eeeae3; text-align: left; vertical-align: top; }}
    th {{ background: #f0efea; }}
    code {{ background: #efede8; padding: 2px 5px; border-radius: 5px; }}
    .boundary {{ border-left: 4px solid #2b5fd9; padding-left: 16px; }}
  </style>
</head>
<body>
<main>
  <h1>支持入口第一阻塞项人审包</h1>
  <p>这是给人看的下一步入口：先补 <strong>support_contact</strong>。本页不会生成联系人，不会发布支持入口，不会联系客户，不会关闭 blocker。</p>
  <section class="grid">
    <div class="card"><div class="label">状态</div><div class="value">{html.escape(payload['status'])}</div></div>
    <div class="card"><div class="label">10 行填写卡</div><div class="value">{payload['review_batch_fill_card_row_count']}</div></div>
    <div class="card"><div class="label">空值</div><div class="value">{payload['review_batch_blank_value_row_count']}</div></div>
    <div class="card"><div class="label">阻塞项</div><div class="value">support_contact</div></div>
  </section>
  <section class="boundary">
    <p><strong>先做：</strong>打开 10 行填写卡，人工填写已确认的负责人、审批记录、支持入口判断和来源说明。</p>
    <p><strong>停止点：</strong><code>support_contact_published=false</code>，<code>evidence_collection_authorized=false</code>，<code>blocker_closure_authorized=false</code>。</p>
  </section>
  <h2>人工步骤</h2>
  <table><thead><tr><th>Step</th><th>要做什么</th><th>入口</th><th>人工动作</th></tr></thead><tbody>
    {''.join(step_rows)}
  </tbody></table>
</main>
</body>
</html>
"""
    OUT_HTML.write_text(text, encoding="utf-8")


def write_audit(payload: dict[str, Any]) -> None:
    text = f"""# SAEE Support Contact First Priority Packet Boundary Audit

- `support_contact_first_priority_packet_v0_1: true`
- `packet_scope: {payload['packet_scope']}`
- `status: {payload['status']}`
- `target_blocker_id: support_contact`
- `raw_values_recorded: false`
- `human_values_generated_by_codex: false`
- `quick_fill_values_entered_by_codex: false`
- `validator_inputs_exported: false`
- `validators_run: false`
- `support_contact_configured: false`
- `support_contact_published: false`
- `support_contact_test_performed: false`
- `workbook_import_authorized: false`
- `evidence_collection_authorized: false`
- `execution_authorized: false`
- `blocker_closure_authorized: false`
- `runtime_modified: false`
- `backend_modified: false`
- `kernel_modified: false`
- `api_schema_modified: false`
- `private_core_exposed: false`
- `production_ready: false`
- `customer_validated: false`
- `product_launched: false`

This packet is a navigation surface only. It does not fill values, export
validator inputs, run validators, configure a support contact, publish a support
contact, contact customers or vendors, import a workbook, collect evidence,
close blockers, or claim production readiness.
"""
    OUT_AUDIT.write_text(text, encoding="utf-8")


def write_readme(payload: dict[str, Any]) -> None:
    text = f"""# Support Contact First Priority Packet

- `support_contact_first_priority_packet_v0_1=true`
- `status={payload['status']}`
- `target_blocker_id=support_contact`
- `review_batch_fill_card_row_count={payload['review_batch_fill_card_row_count']}`
- `review_batch_blank_value_row_count={payload['review_batch_blank_value_row_count']}`
- `combined_bridge_input_row_count={payload['combined_bridge_input_row_count']}`
- `production_ready=false`
- `support_contact_published=false`
- `blocker_closure_authorized=false`

This folder is a human navigation packet for the first commercial blocker only.
It does not execute support operations or change product behavior.
"""
    OUT_README.write_text(text, encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    text = f"""# Support Contact First Priority Packet v0.1

- `support_contact_first_priority_packet_v0_1=true`
- `packet_type={payload['packet_type']}`
- `packet_scope={payload['packet_scope']}`
- `status={payload['status']}`
- `target_blocker_id=support_contact`
- `review_batch_fill_card_row_count={payload['review_batch_fill_card_row_count']}`
- `review_batch_blank_value_row_count={payload['review_batch_blank_value_row_count']}`
- `combined_bridge_input_row_count={payload['combined_bridge_input_row_count']}`
- `missing_first_owner_field_count={payload['missing_first_owner_field_count']}`
- `missing_support_decision_field_count={payload['missing_support_decision_field_count']}`
- `support_contact_published=false`
- `evidence_collection_authorized=false`
- `blocker_closure_authorized=false`
- `production_ready=false`

Entrypoints:

- `phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.md`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.csv`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.html`
- `phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet_boundary_audit.md`
"""
    TOP_DOC.write_text(text, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    text = f"""# SAEE Support Contact First Priority Packet Gate

answer: conditional

reason:
This packet is recommended as a local human navigation surface for the first
commercial blocker. It is not recommended as product execution, support contact
publication, customer contact, evidence collection, workbook import, or blocker
closure.

recommend_for_human_navigation: true
recommend_for_product_launch: false
recommend_for_support_contact_publication: false
recommend_for_customer_contact: false
recommend_for_evidence_collection: false
recommend_for_workbook_import_execution: false
recommend_for_blocker_closure: false

status: {payload['status']}
target_blocker_id: support_contact
review_batch_fill_card_row_count: {payload['review_batch_fill_card_row_count']}
review_batch_blank_value_row_count: {payload['review_batch_blank_value_row_count']}

boundary:
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
support_contact_configured: false
support_contact_published: false
customer_contacted: false
production_ready: false
product_launched: false
blocker_closure_authorized: false

next_action:
Human fills the support-contact input files and runs local validators. Any
publication, external test, evidence-builder execution, workbook import, or
blocker closure requires a separate explicit request.
"""
    GATE.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_readme(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_SUPPORT_CONTACT_FIRST_PRIORITY_PACKET: PASS "
        f"status={payload['status']} "
        f"target={payload['target_blocker_id']} "
        f"blank_rows={payload['review_batch_blank_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
