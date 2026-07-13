#!/usr/bin/env python3
"""Build a human input prompt for tenant-billing-isolation approval evidence.

This prompt narrows the `tenant_billing_isolation` production blocker to the
exact human-filled fields needed before the existing tenant-billing-isolation
evidence builder can be considered by a later, separate execution request. It
does not approve a tenant billing account model, run cross-tenant billing
tests, configure payment-provider tenant mapping, collect payment, validate
revenue, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
TEMPLATE = EVIDENCE_DIR / "tenant_billing_isolation_evidence_input.template.json"
BUILDER_OUTPUT = EVIDENCE_DIR / "tenant_billing_isolation_evidence_builder_output.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "tenant_billing_isolation_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "tenant_billing_isolation_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "tenant_billing_isolation_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = (
    EVIDENCE_DIR / "tenant_billing_isolation_evidence_input.human_filled.local.json"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "commercial_owner",
    "accounting_owner",
    "legal_owner",
    "support_owner",
    "billing_owner",
    "payment_owner",
    "tenant_boundary_owner",
    "review_record_reference",
    "decision_summary",
]

TENANT_BILLING_ISOLATION_KEYS = [
    "tenant_billing_account_model_approved",
    "tenant_invoice_partitioning_tested",
    "tenant_payment_event_partitioning_tested",
    "cross_tenant_billing_access_tests_passed",
    "billing_audit_metadata_policy_approved",
    "tenant_billing_retention_policy_approved",
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
    "payment_provider_contacted",
    "payment_provider_configured",
    "checkout_enabled",
    "payment_provider_live_mode_enabled",
    "payment_link_created",
    "invoice_sent_to_customer",
    "tax_advisor_contacted",
    "legal_counsel_contacted",
    "tax_collection_started",
    "refund_policy_published",
    "tenant_billing_isolation_available",
    "tenant_billing_isolation_approved",
    "tenant_billing_isolation_published",
    "tenant_billing_isolated",
    "tenant_billing_isolation_enabled",
    "tenant_billing_account_model_available",
    "billing_audit_metadata_policy_available",
    "tenant_billing_export_policy_available",
    "tenant_billing_retention_policy_available",
    "tenant_invoice_numbering_available",
    "tenant_refund_partitioning_available",
    "tenant_privacy_security_review_completed",
    "tenant_billing_transaction_processed",
    "tenant_billing_invoice_or_charge_issued_to_customer",
    "tenant_billing_support_workflow_available",
    "payment_provider_tenant_mapping_approved",
    "payment_provider_tenant_mapping_configured",
    "tenant_billing_isolation_claim_published",
    "tenant_billing_isolation_completed_by_codex",
    "tenant_billing_isolation_execution_authorized",
    "codex_published_tenant_billing_isolation",
    "codex_processed_tenant_billing",
    "codex_configured_tenant_billing_handling",
    "codex_inferred_missing_evidence",
    "production_billing_enabled",
    "customer_payment_collected",
    "paid_pilot_completed",
    "revenue_validated",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT: "
            f"FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT: "
            f"FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def review_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT: "
            "FAIL evidence_review missing"
        )
    keys = list(review)
    if set(keys) != set(TENANT_BILLING_ISOLATION_KEYS):
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT: "
            "FAIL evidence_review keys changed"
        )
    return TENANT_BILLING_ISOLATION_KEYS


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    builder = read_json(BUILDER_OUTPUT)
    keys = review_keys(template)
    artifacts = template.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT: "
            "FAIL review_artifacts missing"
        )

    payload: dict[str, Any] = {
        "tenant_billing_isolation_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_tenant_billing_isolation_approval_input_prompt",
        "prompt_scope": "local_human_tenant_billing_isolation_input_prompt_only",
        "status": "hold_human_tenant_billing_isolation_input_required",
        "target_blocker_ids": ["tenant_billing_isolation"],
        "category": "billing_revenue",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_tenant_billing_isolation_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_builder_output": rel(BUILDER_OUTPUT),
        "source_tenant_billing_isolation_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "builder_status": builder.get("status", "hold"),
        "builder_ready": False,
        "local_static_tenant_billing_isolation_approval_input_prompt_html": True,
        "browser_readable_tenant_billing_isolation_approval_input_prompt": True,
        "plain_language_tenant_billing_isolation_entry_v0_2": True,
        "plain_language_status_label": "租户账单隔离还没有批准，也没有启用",
        "plain_language_next_action": (
            "先由人审租户账单账户模型、发票分区、支付事件分区和跨租户访问边界，再填写本地证据模板。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不批准租户账单模型、不运行跨租户测试、"
            "不配置支付平台租户映射、不收款、不关闭阻塞项。"
        ),
        "tenant_billing_isolation_human_review_step_count": 4,
        "tenant_billing_isolation_evidence_complete_for_review": False,
        "tenant_billing_isolation_available": False,
        "tenant_billing_isolation_approved": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_tenant_billing_isolation_evidence_item_count": len(keys),
        "completed_tenant_billing_isolation_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "tenant_billing_isolation_keys_to_review": [
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
            "python3 scripts/saee_tenant_billing_isolation_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make tenant-billing-isolation-approval-input-prompt",
        "check_target": "make check-tenant-billing-isolation-approval-input-prompt",
        "next_human_action": (
            "Copy the tenant-billing-isolation evidence template, fill all "
            "metadata fields, approve each tenant-billing evidence key only "
            "with source-backed human review, add source notes and artifact "
            "references, then stop. Evidence-builder execution, tenant billing "
            "account-model approval, cross-tenant billing tests, payment-provider "
            "tenant mapping, payment collection, revenue validation, blocker "
            "closure, and production claims remain separate."
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
        "## Tenant Billing Isolation Evidence Keys",
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
    return f"""# SAEE Tenant Billing Isolation Approval Input Prompt v0.1

Status: {payload['status']}.

This is a local, human-facing input prompt for the
`tenant_billing_isolation` production blocker. It tells commercial,
accounting, legal, support, billing, payment, and tenant-boundary owners
which source-backed fields must be filled before the existing tenant-billing
isolation evidence builder can be considered in a separate request.

It does not approve a tenant billing account model, run cross-tenant billing
tests, configure payment-provider tenant mapping, collect payment, validate
revenue, close blockers, launch product, or claim production readiness.

## Summary

- tenant_billing_isolation_approval_input_prompt_v0_1: true
- plain_language_tenant_billing_isolation_entry_v0_2: true
- local_static_tenant_billing_isolation_approval_input_prompt_html: true
- browser_readable_tenant_billing_isolation_approval_input_prompt: true
- source_tenant_billing_isolation_approval_input_prompt_html: {payload['source_tenant_billing_isolation_approval_input_prompt_html']}
- plain_language_status_label: {payload['plain_language_status_label']}
- plain_language_next_action: {payload['plain_language_next_action']}
- plain_language_stop_point: {payload['plain_language_stop_point']}
- tenant_billing_isolation_human_review_step_count: {payload['tenant_billing_isolation_human_review_step_count']}
- prompt_type: {payload['prompt_type']}
- prompt_scope: {payload['prompt_scope']}
- status: {payload['status']}
- target_blocker_ids: tenant_billing_isolation
- required_metadata_field_count: {payload['required_metadata_field_count']}
- required_tenant_billing_isolation_evidence_item_count: {payload['required_tenant_billing_isolation_evidence_item_count']}
- completed_metadata_field_count: 0
- completed_tenant_billing_isolation_evidence_item_count: 0
- builder_ready: false
- ready_for_evidence_builder: false
- tenant_billing_isolation_available: false
- tenant_billing_isolation_approved: false
- tenant_billing_isolation_published: false
- tenant_billing_isolated: false
- tenant_billing_isolation_enabled: false
- tenant_billing_account_model_available: false
- billing_audit_metadata_policy_available: false
- tenant_billing_retention_policy_available: false
- tenant_invoice_numbering_available: false
- tenant_privacy_security_review_completed: false
- payment_provider_tenant_mapping_approved: false
- payment_provider_tenant_mapping_configured: false
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

{render_key_table(payload['tenant_billing_isolation_keys_to_review'])}

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

- codex_published_tenant_billing_isolation: false
- codex_processed_tenant_billing: false
- codex_configured_tenant_billing_handling: false
- tenant_billing_isolation_claim_published: false
- tenant_billing_isolation_completed_by_codex: false
- tenant_billing_isolation_execution_authorized: false
- tenant_billing_isolation_available: false
- tenant_billing_isolation_approved: false
- tenant_billing_isolation_published: false
- tenant_billing_isolated: false
- tenant_billing_isolation_enabled: false
- tenant_billing_account_model_available: false
- billing_audit_metadata_policy_available: false
- tenant_billing_export_policy_available: false
- tenant_billing_retention_policy_available: false
- tenant_invoice_numbering_available: false
- tenant_refund_partitioning_available: false
- tenant_privacy_security_review_completed: false
- tenant_billing_transaction_processed: false
- tenant_billing_invoice_or_charge_issued_to_customer: false
- tenant_billing_support_workflow_available: false
- payment_provider_tenant_mapping_approved: false
- payment_provider_tenant_mapping_configured: false
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
        f"<li><strong>{item['field_name']}</strong><span>人来填写，Codex 不代填。</span></li>"
        for item in payload["metadata_fields_to_fill"]
    )
    evidence_rows = "\n".join(
        f"<li><strong>{item['evidence_key']}</strong><span>只有人审通过、有来源和证据后，才可以填 true。</span></li>"
        for item in payload["tenant_billing_isolation_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 租户账单隔离人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f7f2;
        --surface: #ffffff;
        --soft: #eef1eb;
        --text: #1f2623;
        --muted: #626b66;
        --line: #deded6;
        --accent: #0c7f64;
        --danger: #b54032;
        --shadow: 0 18px 46px rgba(31, 38, 35, 0.08);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 54%, var(--soft) 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.65;
      }}
      main {{
        width: min(1120px, calc(100% - 36px));
        margin: 0 auto;
        padding: clamp(34px, 6vw, 72px) 0;
      }}
      .hero {{
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
        gap: 24px;
        align-items: stretch;
      }}
      .panel, .card, .list {{
        border: 1px solid var(--line);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: var(--shadow);
      }}
      .panel {{ padding: clamp(24px, 4vw, 42px); }}
      .kicker {{
        margin: 0 0 12px;
        color: var(--accent);
        font-size: 14px;
        font-weight: 800;
      }}
      h1 {{
        margin: 0;
        max-width: 760px;
        font-size: clamp(34px, 5vw, 58px);
        line-height: 1.08;
        letter-spacing: 0;
      }}
      h2 {{ margin: 0 0 14px; font-size: clamp(24px, 3vw, 34px); line-height: 1.18; }}
      p {{ margin: 16px 0 0; color: var(--muted); font-size: 17px; }}
      .status {{
        display: grid;
        gap: 12px;
        padding: 22px;
      }}
      .status strong {{ font-size: 22px; }}
      .status code {{
        display: inline-block;
        padding: 4px 7px;
        border-radius: 7px;
        background: var(--soft);
        color: var(--text);
        font-size: 13px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 24px;
      }}
      .card {{ padding: 22px; box-shadow: none; }}
      .card h3 {{ margin: 0 0 8px; font-size: 19px; }}
      .card p {{ margin: 0; font-size: 15px; }}
      .danger {{
        color: var(--danger);
        font-weight: 800;
      }}
      .list {{
        margin-top: 28px;
        padding: 24px;
        box-shadow: none;
      }}
      ul {{ margin: 0; padding: 0; list-style: none; }}
      li {{
        display: grid;
        grid-template-columns: minmax(180px, 0.6fr) minmax(0, 1fr);
        gap: 14px;
        padding: 12px 0;
        border-bottom: 1px solid var(--line);
      }}
      li:last-child {{ border-bottom: 0; }}
      li span {{ color: var(--muted); }}
      .boundary {{
        margin-top: 28px;
        padding: 24px;
        border-radius: 12px;
        background: #1f2623;
        color: #fff;
      }}
      .boundary p {{ color: rgba(255, 255, 255, 0.78); }}
      .boundary code {{
        display: inline-block;
        margin: 6px 8px 0 0;
        padding: 5px 8px;
        border-radius: 7px;
        background: rgba(255, 255, 255, 0.12);
        color: #fff;
        font-size: 13px;
      }}
      @media (max-width: 820px) {{
        .hero, .grid, li {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div class="panel">
          <p class="kicker">SAEE 租户账单隔离人工审批入口</p>
          <h1>先把租户账单边界审清楚，再决定能不能支持多租户付费。</h1>
          <p>{payload['plain_language_status_label']}。</p>
          <p>{payload['plain_language_next_action']}</p>
          <p class="danger">{payload['plain_language_stop_point']}</p>
        </div>
        <aside class="status panel" aria-label="当前状态">
          <strong>当前只能准备材料</strong>
          <code>status: {payload['status']}</code>
          <code>builder_ready: false</code>
          <code>tenant_billing_isolation_approved: false</code>
          <code>tenant_billing_isolated: false</code>
          <code>production_ready: false</code>
        </aside>
      </section>

      <section class="grid" aria-label="人工审查步骤">
        <article class="card">
          <h3>1. 先确认谁负责</h3>
          <p>商业、财务、法务、支持、账单、支付和租户边界负责人都要明确。Codex 可代执行：false。</p>
        </article>
        <article class="card">
          <h3>2. 再审账单隔离证据</h3>
          <p>确认租户账户模型、发票分区、支付事件分区和跨租户访问测试是否有真实证据。Codex 可代执行：false。</p>
        </article>
        <article class="card">
          <h3>3. 只填写本地模板</h3>
          <p>把来源、证据、负责人和审查结论写进本地模板，不自动运行 evidence builder。Codex 可代执行：false。</p>
        </article>
        <article class="card">
          <h3>4. 停在人审门口</h3>
          <p>没有单独执行批准，不配置支付平台，不收款，不关闭 blocker。Codex 可代执行：false。</p>
        </article>
      </section>

      <section class="list">
        <h2>需要人填写的基本信息</h2>
        <ul>
          {metadata_rows}
        </ul>
      </section>

      <section class="list">
        <h2>需要人审的账单隔离项目</h2>
        <ul>
          {evidence_rows}
        </ul>
      </section>

      <section class="boundary">
        <h2>边界声明</h2>
        <p>本页只是本地静态 HTML 人审入口。不会批准租户账单模型，不会运行跨租户测试，不会配置支付平台租户映射，不会收款，也不会关闭商用阻塞项。</p>
        <code>runtime_modified: false</code>
        <code>backend_modified: false</code>
        <code>kernel_modified: false</code>
        <code>api_schema_modified: false</code>
        <code>private_core_exposed: false</code>
        <code>product_launched: false</code>
        <code>customer_payment_collected: false</code>
        <code>revenue_validated: false</code>
      </section>
    </main>
  </body>
</html>
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE Tenant Billing Isolation Approval Input Prompt Recommendation Gate

answer: recommend_for_human_tenant_billing_isolation_input_prompt

reason: The prompt makes tenant-billing-isolation approval evidence
requirements agent-readable and human-fillable without approving a tenant
billing account model, running cross-tenant billing tests, configuring
payment-provider tenant mapping, collecting payment, validating revenue, or
executing tenant billing work.

recommend_for_tenant_billing_account_model_approval: false
recommend_for_cross_tenant_billing_test_execution: false
recommend_for_payment_provider_tenant_mapping_configuration: false
recommend_for_payment_collection: false
recommend_for_revenue_validation: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

status: {payload['status']}
required_metadata_field_count: {payload['required_metadata_field_count']}
required_tenant_billing_isolation_evidence_item_count: {payload['required_tenant_billing_isolation_evidence_item_count']}
plain_language_tenant_billing_isolation_entry_v0_2: true
browser_readable_tenant_billing_isolation_approval_input_prompt: true
source_tenant_billing_isolation_approval_input_prompt_html: {payload['source_tenant_billing_isolation_approval_input_prompt_html']}
plain_language_status_label: {payload['plain_language_status_label']}
builder_ready: false
ready_for_evidence_builder: false
tenant_billing_isolation_available: false
tenant_billing_isolation_approved: false
tenant_billing_isolation_published: false
tenant_billing_isolated: false
tenant_billing_isolation_enabled: false
tenant_billing_account_model_available: false
billing_audit_metadata_policy_available: false
tenant_billing_retention_policy_available: false
tenant_invoice_numbering_available: false
tenant_privacy_security_review_completed: false
payment_provider_tenant_mapping_approved: false
payment_provider_tenant_mapping_configured: false
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
- tenant_billing_isolation_published: false
- tenant_billing_isolated: false
- payment_provider_tenant_mapping_configured: false
- customer_payment_collected: false
- revenue_validated: false

next_action: Human owners may copy the tenant-billing-isolation evidence
template and fill the required fields. Evidence-builder execution remains a
separate step.
"""


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    markdown = render_markdown(payload)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(markdown, encoding="utf-8")
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(render_gate(payload), encoding="utf-8")
    print("SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"required_metadata_field_count={payload['required_metadata_field_count']}")
    print(
        "required_tenant_billing_isolation_evidence_item_count="
        f"{payload['required_tenant_billing_isolation_evidence_item_count']}"
    )
    print(f"copy_template_command={payload['copy_template_command']}")
    print(f"html_entrypoint={rel(OUTPUT_HTML)}")
    print(
        "builder_command_after_separate_approval="
        f"{payload['builder_command_after_separate_approval']}"
    )


if __name__ == "__main__":
    main()
