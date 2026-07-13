#!/usr/bin/env python3
"""Build a human input prompt for invoice-process approval evidence.

This prompt narrows the `invoice_process` production blocker to the exact
human-filled fields needed before the existing invoice-process evidence
builder can be considered by a later, separate execution request. It does not
create invoice templates, create or send invoices, sign contracts, perform
reconciliation, contact customers, collect payment, validate revenue, close
blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
TEMPLATE = EVIDENCE_DIR / "invoice_process_evidence_input.template.json"
BUILDER_OUTPUT = EVIDENCE_DIR / "invoice_process_evidence_builder_output.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "invoice_process_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "invoice_process_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "invoice_process_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "INVOICE_PROCESS_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "invoice_process_evidence_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "commercial_owner",
    "invoice_owner",
    "accounting_owner",
    "support_owner",
    "review_record_reference",
    "decision_summary",
]

INVOICE_PROCESS_KEYS = [
    "invoice_owner_named",
    "invoice_workflow_approved",
    "contract_handoff_defined",
    "billing_support_handoff_defined",
    "payment_reconciliation_tested",
    "bookkeeping_review_completed",
]

BOUNDARY_FALSE_FLAGS = [
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
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "pricing_page_published",
    "sales_offer_sent",
    "paid_product_launched",
    "enterprise_contract_signed",
    "legal_counsel_contacted",
    "tax_advisor_contacted",
    "payment_provider_contacted",
    "payment_provider_configured",
    "checkout_enabled",
    "payment_provider_live_mode_enabled",
    "payment_link_created",
    "invoice_created",
    "invoice_template_published",
    "invoice_sent_to_customer",
    "tax_collection_started",
    "refund_policy_published",
    "production_billing_enabled",
    "customer_payment_collected",
    "paid_pilot_completed",
    "revenue_validated",
    "invoice_process_claim_published",
    "invoice_process_completed_by_codex",
    "invoice_process_execution_authorized",
    "codex_created_invoice",
    "codex_sent_invoice",
    "codex_signed_contract",
    "codex_performed_reconciliation",
    "codex_inferred_missing_evidence",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def review_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    keys = list(review)
    if set(keys) != set(INVOICE_PROCESS_KEYS):
        raise SystemExit(
            "SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT: FAIL evidence_review keys changed"
        )
    return INVOICE_PROCESS_KEYS


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    builder = read_json(BUILDER_OUTPUT)
    keys = review_keys(template)
    artifacts = template.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        raise SystemExit(
            "SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT: FAIL review_artifacts missing"
        )

    payload: dict[str, Any] = {
        "invoice_process_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_invoice_process_approval_input_prompt",
        "prompt_scope": "local_human_invoice_process_input_prompt_only",
        "status": "hold_human_invoice_process_input_required",
        "target_blocker_ids": ["invoice_process"],
        "category": "billing_revenue",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_invoice_process_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_builder_output": rel(BUILDER_OUTPUT),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "source_invoice_process_approval_input_prompt_html": rel(OUTPUT_HTML),
        "local_static_invoice_process_approval_input_prompt_html": True,
        "browser_readable_invoice_process_approval_input_prompt": True,
        "plain_language_invoice_process_review_entry_v0_2": True,
        "plain_language_status_label": "发票流程还没有批准，也没有启用",
        "plain_language_next_action": "先由人审发票模板、开票流程、合同和对账边界，再填写本地证据模板。",
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不创建发票、不发送发票、"
            "不签合同、不对账、不收款、不关闭阻塞项。"
        ),
        "invoice_process_human_review_step_count": 4,
        "builder_status": builder.get("status", "hold"),
        "builder_ready": False,
        "invoice_process_evidence_complete_for_review": False,
        "invoice_process_approved": False,
        "invoice_process_ready": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_invoice_process_evidence_item_count": len(keys),
        "completed_invoice_process_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "invoice_process_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "review_artifact_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "builder_command_after_separate_approval": (
            "python3 scripts/saee_invoice_process_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make invoice-process-approval-input-prompt",
        "check_target": "make check-invoice-process-approval-input-prompt",
        "next_human_action": (
            "先读发票流程审批输入提示，再复制模板并由人填写真实审批信息。"
            "填完后停止；evidence builder 执行、发票模板创建、发票发送、"
            "合同签署、对账、客户联系、收款、收入验证、阻塞项关闭和生产可用声明都需要单独批准。"
        ),
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_prompt"] = 0
    return payload


def render_key_table(items: list[dict[str, Any]]) -> str:
    rows = [
        "## Invoice Process Evidence Keys",
        "",
        "| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        rows.append(
            "| {key} | true only after human approval | required | required | required | required | false |".format(
                key=item["evidence_key"]
            )
        )
    return "\n".join(rows)


def render_markdown(payload: dict[str, Any]) -> str:
    return f"""# SAEE Invoice Process Approval Input Prompt v0.1

Status: {payload['status']}.

plain_language_invoice_process_review_entry_v0_2: true
plain_language_status_label: {payload['plain_language_status_label']}
plain_language_next_action: {payload['plain_language_next_action']}
plain_language_stop_point: {payload['plain_language_stop_point']}
invoice_process_human_review_step_count: {payload['invoice_process_human_review_step_count']}

This is a local, human-facing input prompt for the `invoice_process`
production blocker. It tells commercial, invoice, accounting, and support
owners which source-backed fields must be filled before the existing
invoice-process evidence builder can be considered in a separate request.

It does not create invoice templates, create or send invoices, sign contracts,
perform reconciliation, contact customers, collect payment, validate revenue,
close blockers, launch product, or claim production readiness.

## Summary

- invoice_process_approval_input_prompt_v0_1: true
- prompt_type: {payload['prompt_type']}
- prompt_scope: {payload['prompt_scope']}
- status: {payload['status']}
- target_blocker_ids: invoice_process
- required_metadata_field_count: {payload['required_metadata_field_count']}
- required_invoice_process_evidence_item_count: {payload['required_invoice_process_evidence_item_count']}
- completed_metadata_field_count: 0
- completed_invoice_process_evidence_item_count: 0
- builder_ready: false
- ready_for_evidence_builder: false
- invoice_process_approved: false
- invoice_process_ready: false
- invoice_created: false
- invoice_template_published: false
- invoice_sent_to_customer: false
- enterprise_contract_signed: false
- customer_payment_collected: false
- revenue_validated: false
- blockers_closed_by_prompt: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Human Metadata To Fill

| Field | Required | Codex May Fill |
| --- | --- | --- |
{chr(10).join(f"| {item['field_name']} | true | false |" for item in payload['metadata_fields_to_fill'])}

{render_key_table(payload['invoice_process_keys_to_review'])}

## Commands

Copy the template:

```bash
{payload['copy_template_command']}
```

Only after a separate human-approved evidence-builder execution request:

```bash
{payload['builder_command_after_separate_approval']}
```

## Boundary

- codex_created_invoice: false
- codex_sent_invoice: false
- codex_signed_contract: false
- codex_performed_reconciliation: false
- invoice_process_claim_published: false
- invoice_process_completed_by_codex: false
- invoice_process_execution_authorized: false
- invoice_process_approved: false
- invoice_process_ready: false
- invoice_created: false
- invoice_template_published: false
- invoice_sent_to_customer: false
- enterprise_contract_signed: false
- payment_provider_configured: false
- checkout_enabled: false
- payment_link_created: false
- customer_payment_collected: false
- revenue_validated: false
- production_billing_enabled: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false

## Next Human Action

{payload['next_human_action']}
"""


def render_html(payload: dict[str, Any]) -> str:
    metadata_rows = "\n".join(
        f"<tr><td>{item['field_name']}</td><td>人必须填写</td><td>Codex 不可代填</td></tr>"
        for item in payload["metadata_fields_to_fill"]
    )
    key_rows = "\n".join(
        "<tr><td>{key}</td><td>必须有人审记录</td><td>需要来源说明</td><td>需要附件或记录引用</td></tr>".format(
            key=item["evidence_key"]
        )
        for item in payload["invoice_process_keys_to_review"]
    )
    steps = [
        ("1", "先确认不启用开票", "这一步只审证据要求，不创建模板，不开发票，不发给客户。"),
        ("2", "人工审开票边界", "商业、发票、会计和支持负责人确认模板、合同交接、支持交接和对账要求。"),
        ("3", "填写本地模板", "复制 invoice_process_evidence_input.template.json 后由人填写真实审批信息。"),
        ("4", "停在审批记录", "builder、发票模板、发票发送、合同签署、对账和收款都需要单独批准。"),
    ]
    step_cards = "\n".join(
        f"""
        <article class="step">
          <span>{number}</span>
          <h3>{title}</h3>
          <p>{body}</p>
          <small>Codex 可代执行：false · 需要人工操作：true</small>
        </article>
        """
        for number, title, body in steps
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SAEE 发票流程人工审批入口</title>
  <style>
    :root {{
      --bg: #f6f8fc;
      --surface: #ffffff;
      --surface-soft: #eef3fb;
      --text: #111827;
      --muted: #5d6678;
      --line: #dde5f2;
      --accent: #155eef;
      --accent-strong: #0f47bd;
      --danger: #b91c1c;
      --shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 14% 8%, rgba(21, 94, 239, 0.12), transparent 30%),
        linear-gradient(180deg, #ffffff 0%, var(--bg) 46%, #eef3fb 100%);
      color: var(--text);
    }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 56px 0; }}
    .hero {{
      background: linear-gradient(135deg, #ffffff 0%, #eaf1ff 100%);
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 40px;
      box-shadow: var(--shadow);
    }}
    .kicker {{ margin: 0 0 10px; color: var(--accent-strong); font-weight: 700; }}
    h1 {{ margin: 0; font-size: clamp(34px, 5vw, 64px); line-height: 1.04; letter-spacing: 0; max-width: 820px; }}
    .lead {{ max-width: 820px; color: var(--muted); font-size: 20px; line-height: 1.7; }}
    .metrics, .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 24px; }}
    .metric, .step, .panel {{
      background: rgba(255, 255, 255, 0.86);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 20px;
    }}
    .metric strong {{ display: block; font-size: 30px; }}
    .metric span, .step p, .panel p, small {{ color: var(--muted); line-height: 1.6; }}
    section {{ margin-top: 28px; }}
    h2 {{ font-size: 24px; margin: 0 0 14px; }}
    .step span {{
      display: inline-grid;
      place-items: center;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #111827;
      color: #fff;
      font-weight: 700;
    }}
    table {{ width: 100%; border-collapse: collapse; overflow: hidden; background: var(--surface); border-radius: 18px; }}
    th, td {{ padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ color: #30394d; background: var(--surface-soft); }}
    code {{
      display: block;
      white-space: pre-wrap;
      padding: 14px;
      background: #111827;
      color: #eef3ff;
      border-radius: 14px;
      line-height: 1.6;
    }}
    .danger {{ color: var(--danger); font-weight: 700; }}
    @media (max-width: 840px) {{
      main {{ width: min(100% - 20px, 1120px); padding: 24px 0; }}
      .hero {{ padding: 24px; border-radius: 22px; }}
      .metrics, .grid {{ grid-template-columns: 1fr; }}
      table {{ font-size: 14px; }}
      th, td {{ padding: 10px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <p class="kicker">{payload['plain_language_status_label']}</p>
      <h1>先把发票流程审清楚，再决定能不能用于付费试点。</h1>
      <p class="lead">
        这是 `invoice_process` 的人工审批入口。它只帮人看清楚要审什么、谁来审、停在哪里；
        不会创建发票，不会发送发票，不会签合同，不会对账，不会收款，也不会关闭商用阻塞项。
      </p>
      <div class="metrics">
        <div class="metric"><strong>{payload['required_metadata_field_count']}</strong><span>个审批元数据字段</span></div>
        <div class="metric"><strong>{payload['required_invoice_process_evidence_item_count']}</strong><span>个发票流程证据项</span></div>
        <div class="metric"><strong>0</strong><span>个已关闭阻塞项</span></div>
      </div>
    </section>

    <section>
      <h2>人要怎么做</h2>
      <div class="grid">{step_cards}</div>
    </section>

    <section class="panel">
      <h2>要填的负责人信息</h2>
      <table>
        <thead><tr><th>字段</th><th>要求</th><th>Codex 能不能代填</th></tr></thead>
        <tbody>{metadata_rows}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>要审的发票流程证据</h2>
      <table>
        <thead><tr><th>证据项</th><th>人工审批</th><th>来源说明</th><th>记录引用</th></tr></thead>
        <tbody>{key_rows}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>本地命令</h2>
      <p>这里只复制模板。builder、发票模板创建、发票发送、合同签署、对账和收款都需要单独批准。</p>
      <code>{payload['copy_template_command']}</code>
    </section>

    <section class="panel">
      <h2>边界</h2>
      <p class="danger">不创建发票、不发送发票、不签合同、不对账、不收款、不关闭 blocker、不声明生产可用。</p>
      <p>
        invoice_process_approved: false · invoice_created: false · invoice_template_published: false ·
        invoice_sent_to_customer: false · enterprise_contract_signed: false · customer_payment_collected: false ·
        revenue_validated: false · production_ready: false
      </p>
    </section>
  </main>
</body>
</html>
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE Invoice Process Approval Input Prompt Recommendation Gate

answer: recommend_for_human_invoice_process_input_prompt

reason: The prompt makes the invoice-process approval evidence requirements
agent-readable, browser-readable, and human-fillable without creating invoices,
sending invoices, signing contracts, performing reconciliation, or executing
invoice work.

plain_language_invoice_process_review_entry_v0_2: true
plain_language_status_label: {payload['plain_language_status_label']}
plain_language_next_action: {payload['plain_language_next_action']}
plain_language_stop_point: {payload['plain_language_stop_point']}

recommend_for_invoice_template_creation: false
recommend_for_invoice_sending: false
recommend_for_contract_signing: false
recommend_for_reconciliation_execution: false
recommend_for_payment_collection: false
recommend_for_revenue_validation: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

status: {payload['status']}
required_metadata_field_count: {payload['required_metadata_field_count']}
required_invoice_process_evidence_item_count: {payload['required_invoice_process_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
invoice_process_approved: false
invoice_process_ready: false
invoice_created: false
invoice_template_published: false
invoice_sent_to_customer: false
enterprise_contract_signed: false
customer_payment_collected: false
revenue_validated: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

boundary:
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- invoice_process_approved: false
- invoice_process_ready: false
- invoice_created: false
- invoice_template_published: false
- invoice_sent_to_customer: false
- enterprise_contract_signed: false
- payment_provider_configured: false
- checkout_enabled: false
- customer_payment_collected: false
- revenue_validated: false

next_action: Human owners may copy the invoice-process evidence template and
fill the required fields. Evidence-builder execution remains a separate step.
"""


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    markdown = render_markdown(payload)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(markdown, encoding="utf-8")
    GATE.write_text(render_gate(payload), encoding="utf-8")
    print("SAEE_INVOICE_PROCESS_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"required_metadata_field_count={payload['required_metadata_field_count']}")
    print(
        "required_invoice_process_evidence_item_count="
        f"{payload['required_invoice_process_evidence_item_count']}"
    )
    print(f"copy_template_command={payload['copy_template_command']}")
    print(f"html_entrypoint={rel(OUTPUT_HTML)}")
    print(
        "builder_command_after_separate_approval="
        f"{payload['builder_command_after_separate_approval']}"
    )


if __name__ == "__main__":
    main()
