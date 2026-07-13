#!/usr/bin/env python3
"""Build a human input prompt for payment-provider approval evidence.

This prompt narrows the `payment_provider` production blocker to the exact
human-filled fields needed before the existing payment-provider evidence
builder can be considered by a later, separate execution request. It does not
select or contact a payment provider, configure payment modes, enable checkout,
create payment links, process webhooks, collect payment, validate revenue,
close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
TEMPLATE = EVIDENCE_DIR / "payment_provider_evidence_input.template.json"
BUILDER_OUTPUT = EVIDENCE_DIR / "payment_provider_evidence_builder_output.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "payment_provider_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "payment_provider_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "payment_provider_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "payment_provider_evidence_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "commercial_owner",
    "payment_owner",
    "security_owner",
    "review_record_reference",
    "decision_summary",
]

PAYMENT_PROVIDER_KEYS = [
    "payment_provider_selected",
    "test_mode_configuration_reviewed",
    "checkout_enablement_approval_required",
    "webhook_signature_validation_tested",
    "payment_event_redaction_reviewed",
    "security_review_completed",
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
    "payment_provider_selected",
    "payment_provider_contacted",
    "payment_provider_configured",
    "checkout_enabled",
    "payment_provider_live_mode_enabled",
    "payment_link_created",
    "webhook_endpoint_created",
    "webhook_secret_configured",
    "invoice_sent_to_customer",
    "tax_collection_started",
    "refund_policy_published",
    "production_billing_enabled",
    "customer_payment_collected",
    "paid_pilot_completed",
    "revenue_validated",
    "codex_selected_payment_provider",
    "codex_contacted_payment_provider",
    "codex_configured_payment_provider",
    "codex_enabled_checkout",
    "codex_created_payment_link",
    "codex_processed_payment",
    "codex_inferred_missing_evidence",
    "payment_provider_claim_published",
    "payment_provider_completed_by_codex",
    "payment_provider_execution_authorized",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def review_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    keys = list(review)
    if set(keys) != set(PAYMENT_PROVIDER_KEYS):
        raise SystemExit(
            "SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT: FAIL evidence_review keys changed"
        )
    return PAYMENT_PROVIDER_KEYS


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    builder = read_json(BUILDER_OUTPUT)
    keys = review_keys(template)
    artifacts = template.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        raise SystemExit(
            "SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT: FAIL review_artifacts missing"
        )

    payload: dict[str, Any] = {
        "payment_provider_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_payment_provider_approval_input_prompt",
        "prompt_scope": "local_human_payment_provider_input_prompt_only",
        "status": "hold_human_payment_provider_input_required",
        "target_blocker_ids": ["payment_provider"],
        "category": "billing_revenue",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_payment_provider_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_builder_output": rel(BUILDER_OUTPUT),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "source_payment_provider_approval_input_prompt_html": rel(OUTPUT_HTML),
        "local_static_payment_provider_approval_input_prompt_html": True,
        "browser_readable_payment_provider_approval_input_prompt": True,
        "plain_language_payment_provider_review_entry_v0_2": True,
        "plain_language_status_label": "支付服务还没有选择，也没有配置",
        "plain_language_next_action": "先由人审支付服务、结账、回调和安全边界，再填写本地证据模板。",
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不选择支付服务、不联系供应商、"
            "不配置支付、不启用结账、不收款、不关闭阻塞项。"
        ),
        "payment_provider_human_review_step_count": 4,
        "builder_status": builder.get("status", "hold"),
        "builder_ready": False,
        "payment_provider_evidence_complete_for_review": False,
        "payment_provider_selected": False,
        "payment_provider_configured": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_payment_provider_evidence_item_count": len(keys),
        "completed_payment_provider_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "payment_provider_keys_to_review": [
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
            "python3 scripts/saee_payment_provider_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make payment-provider-approval-input-prompt",
        "check_target": "make check-payment-provider-approval-input-prompt",
        "next_human_action": (
            "先读支付服务审批输入提示，再复制模板并由人填写真实审批信息。"
            "填完后停止；evidence builder 执行、服务选择、供应商联系、支付配置、"
            "结账、回调、收款、收入验证、客户联系、阻塞项关闭和生产可用声明都需要单独批准。"
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
        "## Payment Provider Evidence Keys",
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
    return f"""# SAEE Payment Provider Approval Input Prompt v0.1

Status: {payload['status']}.

plain_language_payment_provider_review_entry_v0_2: true
plain_language_status_label: {payload['plain_language_status_label']}
plain_language_next_action: {payload['plain_language_next_action']}
plain_language_stop_point: {payload['plain_language_stop_point']}
payment_provider_human_review_step_count: {payload['payment_provider_human_review_step_count']}

This is a local, human-facing input prompt for the `payment_provider`
production blocker. It tells commercial, payment, and security owners which
source-backed fields must be filled before the existing payment-provider
evidence builder can be considered in a separate request.

It does not select or contact a payment provider, configure test or live mode,
enable checkout, create payment links, process webhooks, collect payment,
validate revenue, close blockers, launch product, or claim production
readiness.

## Summary

- payment_provider_approval_input_prompt_v0_1: true
- prompt_type: {payload['prompt_type']}
- prompt_scope: {payload['prompt_scope']}
- status: {payload['status']}
- target_blocker_ids: payment_provider
- required_metadata_field_count: {payload['required_metadata_field_count']}
- required_payment_provider_evidence_item_count: {payload['required_payment_provider_evidence_item_count']}
- completed_metadata_field_count: 0
- completed_payment_provider_evidence_item_count: 0
- builder_ready: false
- ready_for_evidence_builder: false
- payment_provider_selected: false
- payment_provider_configured: false
- checkout_enabled: false
- payment_link_created: false
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

{render_key_table(payload['payment_provider_keys_to_review'])}

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

- codex_selected_payment_provider: false
- codex_contacted_payment_provider: false
- codex_configured_payment_provider: false
- codex_enabled_checkout: false
- codex_created_payment_link: false
- codex_processed_payment: false
- payment_provider_claim_published: false
- payment_provider_completed_by_codex: false
- payment_provider_execution_authorized: false
- payment_provider_selected: false
- payment_provider_contacted: false
- payment_provider_configured: false
- checkout_enabled: false
- payment_provider_live_mode_enabled: false
- payment_link_created: false
- webhook_endpoint_created: false
- webhook_secret_configured: false
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
        for item in payload["payment_provider_keys_to_review"]
    )
    steps = [
        ("1", "先确认不启用支付", "这一步只审证据要求，不选择服务商，不开通账号，不配置密钥。"),
        ("2", "人工审支付边界", "商业、支付、安全负责人确认结账、回调、脱敏和安全检查。"),
        ("3", "填写本地模板", "复制 payment_provider_evidence_input.template.json 后由人填写真实审批信息。"),
        ("4", "停在审批记录", "builder、供应商联系、checkout、webhook、收款都需要单独批准。"),
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
  <title>SAEE 支付服务人工审批入口</title>
  <style>
    :root {{
      --bg: #f7f8f6;
      --surface: #ffffff;
      --surface-soft: #edf1ee;
      --text: #161918;
      --muted: #5f6863;
      --line: #dde4df;
      --accent: #0f766e;
      --accent-strong: #0b5f59;
      --danger: #b91c1c;
      --shadow: 0 24px 70px rgba(19, 32, 27, 0.12);
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 14% 8%, rgba(15, 118, 110, 0.12), transparent 30%),
        linear-gradient(180deg, #ffffff 0%, var(--bg) 46%, #edf1ee 100%);
      color: var(--text);
    }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 56px 0; }}
    .hero {{
      background: linear-gradient(135deg, #ffffff 0%, #e6f4f1 100%);
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 40px;
      box-shadow: var(--shadow);
    }}
    .kicker {{ margin: 0 0 10px; color: var(--accent-strong); font-weight: 700; }}
    h1 {{ margin: 0; font-size: clamp(34px, 5vw, 64px); line-height: 1.04; letter-spacing: 0; max-width: 780px; }}
    .lead {{ max-width: 780px; color: var(--muted); font-size: 20px; line-height: 1.7; }}
    .metrics, .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 24px; }}
    .metric, .step, .panel {{
      background: rgba(255, 255, 255, 0.82);
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
    th {{ color: #2f3a35; background: var(--surface-soft); }}
    code {{
      display: block;
      white-space: pre-wrap;
      padding: 14px;
      background: #111827;
      color: #ecfeff;
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
      <h1>先把收款风险审清楚，再决定能不能接支付。</h1>
      <p class="lead">
        这是 `payment_provider` 的人工审批入口。它只帮人看清楚要审什么、谁来审、停在哪里；
        不会选择支付服务，不会联系供应商，不会配置支付，不会开结账，不会收款，也不会关闭商用阻塞项。
      </p>
      <div class="metrics">
        <div class="metric"><strong>{payload['required_metadata_field_count']}</strong><span>个审批元数据字段</span></div>
        <div class="metric"><strong>{payload['required_payment_provider_evidence_item_count']}</strong><span>个支付证据项</span></div>
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
      <h2>要审的支付服务证据</h2>
      <table>
        <thead><tr><th>证据项</th><th>人工审批</th><th>来源说明</th><th>记录引用</th></tr></thead>
        <tbody>{key_rows}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>本地命令</h2>
      <p>这里只复制模板。builder、供应商联系、支付配置、checkout、webhook 和收款都需要单独批准。</p>
      <code>{payload['copy_template_command']}</code>
    </section>

    <section class="panel">
      <h2>边界</h2>
      <p class="danger">不选择支付服务、不联系供应商、不配置支付、不启用结账、不创建付款链接、不收款、不关闭 blocker、不声明生产可用。</p>
      <p>
        payment_provider_selected: false · payment_provider_configured: false · checkout_enabled: false ·
        payment_link_created: false · customer_payment_collected: false · revenue_validated: false · production_ready: false
      </p>
    </section>
  </main>
</body>
</html>
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE Payment Provider Approval Input Prompt Recommendation Gate

answer: recommend_for_human_payment_provider_input_prompt

reason: The prompt makes the payment-provider approval evidence requirements
agent-readable, browser-readable, and human-fillable without selecting,
contacting, configuring, or executing payment-provider work.

plain_language_payment_provider_review_entry_v0_2: true
plain_language_status_label: {payload['plain_language_status_label']}
plain_language_next_action: {payload['plain_language_next_action']}
plain_language_stop_point: {payload['plain_language_stop_point']}

recommend_for_payment_provider_selection: false
recommend_for_payment_provider_contact: false
recommend_for_payment_provider_configuration: false
recommend_for_checkout_enablement: false
recommend_for_payment_link_creation: false
recommend_for_webhook_setup: false
recommend_for_payment_collection: false
recommend_for_revenue_validation: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

status: {payload['status']}
required_metadata_field_count: {payload['required_metadata_field_count']}
required_payment_provider_evidence_item_count: {payload['required_payment_provider_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
payment_provider_selected: false
payment_provider_configured: false
checkout_enabled: false
payment_link_created: false
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
- payment_provider_selected: false
- payment_provider_contacted: false
- payment_provider_configured: false
- checkout_enabled: false
- payment_provider_live_mode_enabled: false
- payment_link_created: false
- webhook_endpoint_created: false
- webhook_secret_configured: false
- customer_payment_collected: false
- revenue_validated: false

next_action: Human owners may copy the payment-provider evidence template and
fill the required fields. Evidence-builder execution remains a separate step.
"""


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    markdown = render_markdown(payload)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    TOP_DOC.write_text(markdown, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    GATE.write_text(render_gate(payload), encoding="utf-8")
    print("SAEE_PAYMENT_PROVIDER_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"required_metadata_field_count={payload['required_metadata_field_count']}")
    print(
        "required_payment_provider_evidence_item_count="
        f"{payload['required_payment_provider_evidence_item_count']}"
    )
    print(f"copy_template_command={payload['copy_template_command']}")
    print(f"html_entrypoint={payload['source_payment_provider_approval_input_prompt_html']}")
    print(
        "builder_command_after_separate_approval="
        f"{payload['builder_command_after_separate_approval']}"
    )


if __name__ == "__main__":
    main()
