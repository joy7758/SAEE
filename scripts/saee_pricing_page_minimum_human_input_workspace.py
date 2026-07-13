#!/usr/bin/env python3
"""Generate the minimum human-input workspace for pricing_page.

This workspace reduces the pricing-page commercial blocker to the smallest
human-owned field inventory needed before the existing local validator can be
useful. It does not approve pricing, publish a page, create offers, configure
payment, contact customers, run evidence builders, close blockers, or claim
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
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
BILLING_DIR = COMMERCIAL_DIR / "billing_revenue_evidence"
OUT_DIR = BILLING_DIR / "pricing_page_minimum_human_input_workspace"
OUT_JSON = OUT_DIR / "pricing_page_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "pricing_page_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "pricing_page_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "pricing_page_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "pricing_page_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"

PROMPT_JSON = BILLING_DIR / "pricing_page_approval_input_prompt.local.json"
TEMPLATE_JSON = BILLING_DIR / "pricing_page_evidence_input.template.json"
VALIDATION_JSON = BILLING_DIR / "pricing_page_approval_input_validation.local.json"
REVIEW_PACKET_JSON = BILLING_DIR / "pricing_page_review_packet.local.json"
COPY_DRAFT_JSON = BILLING_DIR / "pricing_page_copy_draft.local.json"


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
        "human_values_generated_by_codex": False,
        "human_input_filled_by_codex": False,
        "validator_inputs_exported": False,
        "validators_run": False,
        "values_saved_by_workspace": False,
        "form_submission_enabled": False,
        "pricing_page_approved": False,
        "pricing_page_published": False,
        "pricing_page_claim_published": False,
        "pricing_page_publication_approved": False,
        "pricing_page_completed": False,
        "customer_facing_pricing_page_created": False,
        "sales_offer_generated": False,
        "sales_offer_sent": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "production_billing_enabled": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
    }


def field_rows(template: dict[str, Any]) -> list[dict[str, Any]]:
    metadata_fields = [
        "human_reviewer_name",
        "review_date",
        "commercial_owner",
        "product_owner",
        "accounting_owner",
        "legal_owner",
        "billing_owner",
        "review_record_reference",
        "decision_summary",
    ]
    evidence_keys = list(template.get("evidence_review", {}).keys())

    rows: list[dict[str, Any]] = []
    for field in metadata_fields:
        rows.append(
            {
                "field_id": f"pricing_page_evidence_input.{field}",
                "group": "metadata",
                "required": True,
                "where_to_fill": "pricing_page_evidence_input.human_filled.local.json",
                "human_instruction": "由人填写真实审批信息；Codex 不能代填。",
            }
        )

    for key in evidence_keys:
        rows.extend(
            [
                {
                    "field_id": f"pricing_page_evidence_input.evidence_review.{key}",
                    "group": "evidence_review",
                    "required": True,
                    "where_to_fill": "pricing_page_evidence_input.human_filled.local.json",
                    "human_instruction": "只有人工确认真实证据存在时才设为 true。",
                },
                {
                    "field_id": f"pricing_page_evidence_input.source_notes_by_key.{key}",
                    "group": "source_note",
                    "required": True,
                    "where_to_fill": "pricing_page_evidence_input.human_filled.local.json",
                    "human_instruction": "填写可追溯来源说明；不要写密钥、账号或付款凭据。",
                },
                {
                    "field_id": f"pricing_page_evidence_input.review_artifacts[{key}].artifact_reference",
                    "group": "review_artifact",
                    "required": True,
                    "where_to_fill": "pricing_page_evidence_input.human_filled.local.json",
                    "human_instruction": "填写人工审查材料或审批记录引用。",
                },
                {
                    "field_id": f"pricing_page_evidence_input.review_artifacts[{key}].owner_named",
                    "group": "review_artifact",
                    "required": True,
                    "where_to_fill": "pricing_page_evidence_input.human_filled.local.json",
                    "human_instruction": "对应负责人已明确时才设为 true。",
                },
                {
                    "field_id": f"pricing_page_evidence_input.review_artifacts[{key}].reviewed_by_human",
                    "group": "review_artifact",
                    "required": True,
                    "where_to_fill": "pricing_page_evidence_input.human_filled.local.json",
                    "human_instruction": "对应材料已由人审过时才设为 true。",
                },
            ]
        )
    return rows


def build_payload() -> dict[str, Any]:
    prompt = load_json(PROMPT_JSON)
    template = load_json(TEMPLATE_JSON)
    validation = load_json(VALIDATION_JSON)
    review_packet = load_json(REVIEW_PACKET_JSON)
    copy_draft = load_json(COPY_DRAFT_JSON)
    rows = field_rows(template)
    metadata_count = prompt.get("required_metadata_field_count", 9)
    evidence_count = prompt.get("required_pricing_page_evidence_item_count", 5)
    payload: dict[str, Any] = {
        "pricing_page_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_pricing_page_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "pricing_page",
        "source_prompt_json": rel(PROMPT_JSON),
        "source_template_json": rel(TEMPLATE_JSON),
        "source_validation_json": rel(VALIDATION_JSON),
        "source_review_packet_json": rel(REVIEW_PACKET_JSON),
        "source_copy_draft_json": rel(COPY_DRAFT_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "minimum_required_field_count": len(rows),
        "minimum_required_human_value_count": len(rows),
        "filled_value_count": 0,
        "blank_value_count": len(rows),
        "metadata_field_count": metadata_count,
        "pricing_page_evidence_key_count": evidence_count,
        "evidence_review_field_count": evidence_count,
        "source_note_field_count": evidence_count,
        "review_artifact_field_count": evidence_count * 3,
        "field_rows": rows,
        "prompt_status": prompt.get("status", "hold_human_pricing_page_input_required"),
        "validator_status": validation.get("validation_status", "hold"),
        "review_packet_status": review_packet.get("packet_status", "draft_ready_for_human_review"),
        "copy_draft_status": copy_draft.get("draft_status", "draft_not_approved"),
        "human_review_required": True,
        "human_input_required": True,
        "next_human_action": (
            "Copy pricing_page_evidence_input.template.json to the human_filled path, "
            "fill only human-approved metadata, evidence flags, source notes, and "
            "review-artifact references, then run the local validator. Do not publish "
            "pricing, create offers, configure payment, contact customers, or close blockers."
        ),
        "copy_commands": [
            (
                "cp phase_b_product/commercial_readiness/billing_revenue_evidence/"
                "pricing_page_evidence_input.template.json "
                "phase_b_product/commercial_readiness/billing_revenue_evidence/"
                "pricing_page_evidence_input.human_filled.local.json"
            )
        ],
        "post_fill_validation_commands": [
            (
                "python3 scripts/saee_pricing_page_approval_input_validator.py "
                "--input phase_b_product/commercial_readiness/billing_revenue_evidence/"
                "pricing_page_evidence_input.human_filled.local.json"
            )
        ],
        "separate_execution_only_after_human_approval": [
            (
                "python3 scripts/saee_pricing_page_evidence_builder.py "
                "--input phase_b_product/commercial_readiness/billing_revenue_evidence/"
                "pricing_page_evidence_input.human_filled.local.json"
            )
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
        "# SAEE Pricing Page Minimum Human Input Workspace v0.1",
        "",
        "`pricing_page_minimum_human_input_workspace_v0_1: true`",
        "",
        "## 目的",
        "",
        "这个工作台只回答一个问题：为了让 `pricing_page` 进入本地 validator，",
        "人类最少需要补哪些字段。它不填写价格、不批准定价、不发布定价页、",
        "不生成销售报价、不配置支付、不联系客户、不运行 evidence builder、不关闭 blocker。",
        "",
        "## 状态",
        "",
        f"- `status: {payload['status']}`",
        f"- `target_blocker_id: {payload['target_blocker_id']}`",
        f"- `minimum_required_field_count: {payload['minimum_required_field_count']}`",
        f"- `filled_value_count: {payload['filled_value_count']}`",
        f"- `blank_value_count: {payload['blank_value_count']}`",
        "- `pricing_page_published: false`",
        "- `pricing_page_approved: false`",
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
            "## 仍需单独批准",
            "",
            "```bash",
            *payload["separate_execution_only_after_human_approval"],
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
            "- `pricing_page_approved: false`",
            "- `pricing_page_published: false`",
            "- `payment_provider_configured: false`",
            "- `checkout_enabled: false`",
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
    <title>SAEE pricing_page 最小人工输入工作台</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f7f4;
        --card: #ffffff;
        --ink: #111111;
        --text: #343430;
        --muted: #5f6368;
        --line: #dedfe4;
        --accent: #3157ff;
        --soft: #eef2ff;
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
      .status {{ display: inline-flex; margin-top: 22px; padding: 8px 12px; border-radius: 999px; color: #2444d8; background: var(--soft); font-weight: 800; }}
      code {{ padding: 2px 6px; border-radius: 6px; background: #f1f3f7; color: var(--ink); word-break: break-word; }}
      table {{ width: 100%; margin-top: 28px; border-collapse: separate; border-spacing: 0; overflow: hidden; }}
      th, td {{ padding: 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
      th {{ color: var(--ink); background: #f1f3f7; }}
      tr:last-child td {{ border-bottom: 0; }}
      .commands {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }}
      .boundary {{ margin-top: 24px; background: #111111; color: #f7f7f4; }}
      .boundary h2 {{ color: #ffffff; }}
      .boundary code {{ background: rgba(255,255,255,0.1); color: #ffffff; }}
      @media (max-width: 840px) {{ .hero, .commands {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div>
          <h1>只看 pricing_page 最少要人填什么。</h1>
          <p>这个页面不保存输入，也不提交表单。它只是把定价页 blocker 的最小人工字段列清楚。</p>
          <span class="status">状态：{html.escape(payload['status'])}</span>
        </div>
        <aside class="card">
          <h2>当前边界</h2>
          <p><code>pricing_page_published: false</code></p>
          <p><code>pricing_page_approved: false</code></p>
          <p><code>values_saved_by_workspace: false</code></p>
          <p><code>production_ready: false</code></p>
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
        <p>本工作台不发布定价页、不生成报价、不配置支付、不联系客户、不运行 evidence builder、不导入工作簿、不关闭 blocker、不声明生产可用。</p>
      </section>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_audit(payload: dict[str, Any]) -> None:
    lines = [
        "# Pricing Page Minimum Human Input Workspace Boundary Audit",
        "",
        "Boundary decision: pass_hold.",
        "",
        "- Only minimum human-input field inventory created.",
        "- No pricing values generated by Codex.",
        "- No values saved by workspace.",
        "- No form submission enabled.",
        "- No validator inputs exported.",
        "- No validators run.",
        "- No evidence builder run.",
        "- No workbook import authorized.",
        "- No blocker closure authorized.",
        "- No pricing page approved.",
        "- No pricing page published.",
        "- No sales offer generated or sent.",
        "- No payment provider configured.",
        "- No checkout enabled.",
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
        f"""# Pricing Page Minimum Human Input Workspace

This directory contains a local, browser-readable workspace for the minimum
human inputs required before the `pricing_page` blocker can move to local
validation.

- `pricing_page_minimum_human_input_workspace_v0_1: true`
- `status: {payload['status']}`
- `minimum_required_field_count: {payload['minimum_required_field_count']}`
- `blank_value_count: {payload['blank_value_count']}`
- `values_saved_by_workspace: false`
- `pricing_page_approved: false`
- `pricing_page_published: false`
- `production_ready: false`

It does not save values, submit forms, call external services, publish pricing,
create offers, configure payment, contact customers, import workbooks, run
evidence builders, or close blockers.
""",
        encoding="utf-8",
    )


def write_top_docs(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        f"""# SAEE Pricing Page Minimum Human Input Workspace v0.1

pricing_page_minimum_human_input_workspace_v0_1: true
status: {payload['status']}
target_blocker_id: pricing_page
minimum_required_field_count: {payload['minimum_required_field_count']}
blank_value_count: {payload['blank_value_count']}
pricing_page_approved: false
pricing_page_published: false
values_saved_by_workspace: false
production_ready: false
product_launched: false
customer_validated: false

This is a human-input field inventory only. It does not authorize pricing
publication, offer generation, payment setup, evidence collection, workbook
import, blocker closure, or production readiness.

Artifacts:
- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_minimum_human_input_workspace/pricing_page_minimum_human_input_workspace.local.json`
- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_minimum_human_input_workspace/pricing_page_minimum_human_input_workspace.html`
- `scripts/saee_pricing_page_minimum_human_input_workspace.py`
- `scripts/saee_pricing_page_minimum_human_input_workspace_smoke.py`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Pricing Page Minimum Human Input Workspace Gate

answer: hold_minimum_human_input_required
reason: The workspace identifies the minimum human-filled fields for the `pricing_page` blocker, but no values were entered and no evidence was collected.

boundary:
- pricing_page_approved: false
- pricing_page_published: false
- values_saved_by_workspace: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- payment_provider_configured: false
- checkout_enabled: false
- customer_contacted: false
- production_ready: false
- product_launched: false
- customer_validated: false
- private_core_exposed: false

next_action: A human may copy the listed template, fill human-approved values locally, and then run the listed validator. Do not publish pricing, configure payment, contact customers, or close blockers without a separate explicit request.
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
        "SAEE_PRICING_PAGE_MINIMUM_HUMAN_INPUT_WORKSPACE: PASS "
        f"status={payload['status']} "
        f"fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
