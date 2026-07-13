#!/usr/bin/env python3
"""Build a human input prompt for customer-support process evidence.

This prompt narrows the `customer_support` blocker to the exact human-filled
fields needed before the existing customer-support approval-input validator can
pass. It does not approve, configure, publish, staff, or start customer support;
create support cases; send customer communications; contact customers/vendors;
execute the evidence builder; close blockers; or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
TEMPLATE = EVIDENCE_DIR / "customer_support_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "customer_support_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "customer_support_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "customer_support_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "customer_support_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "customer_support_evidence_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "support_process_owner",
    "decision_summary",
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
    "customer_support_approved_by_codex",
    "customer_support_configured_by_codex",
    "customer_support_published_by_codex",
    "support_process_started_by_codex",
    "support_case_created_by_codex",
    "customer_communication_sent_by_codex",
    "support_vendor_contacted_by_codex",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "codex_inferred_missing_evidence",
    "support_operations_started",
    "staffed_support_started",
    "support_case_created",
    "customer_communication_sent",
    "customer_support_claim_published",
    "production_support_claim_published",
    "production_support_available",
    "support_process_available",
    "support_contact_available",
    "customer_support_available",
    "sla_available",
    "on_call_rotation_available",
    "support_vendor_contacted",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def customer_support_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = customer_support_keys(template)
    slots = template.get("process_evidence_slots", [])
    if not isinstance(slots, list):
        raise SystemExit(
            "SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT: FAIL process_evidence_slots missing"
        )

    payload: dict[str, Any] = {
        "customer_support_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_customer_support_approval_input_prompt",
        "prompt_scope": "local_human_customer_support_input_prompt_only",
        "status": "hold_human_customer_support_input_required",
        "target_blocker_id": "customer_support",
        "category": "support",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_customer_support_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_customer_support_approval_input_prompt_html": rel(OUTPUT_HTML),
        "local_static_customer_support_approval_input_prompt_html": True,
        "browser_readable_customer_support_approval_input_prompt": True,
        "plain_language_customer_support_approval_input_prompt_v0_2": True,
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "customer_support_available": False,
        "customer_support_approved": False,
        "customer_support_configured": False,
        "customer_support_published": False,
        "support_operations_started": False,
        "support_process_started": False,
        "support_case_created": False,
        "customer_communication_sent": False,
        "staffed_support_started": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_customer_support_evidence_item_count": len(keys),
        "completed_customer_support_evidence_item_count": 0,
        "customer_support_human_review_step_count": 4,
        "plain_language_status_label": (
            "客户支持流程还没有批准，也没有启用。"
        ),
        "plain_language_next_action": (
            "先由人审支持负责人、处理流程、工单记录、客户通知和支持人员安排，"
            "再填写本地证据模板。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不创建工单、不联系客户、"
            "不启用客服、不关闭阻塞项。"
        ),
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "customer_support_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "process_evidence_slot_required": True,
                "evidence_reference_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_customer_support_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make customer-support-approval-input-prompt",
        "check_target": "make check-customer-support-approval-input-prompt",
        "next_human_action": (
            "Copy the customer-support evidence template, fill all metadata "
            "fields, set each customer-support evidence review key only after "
            "human approval, add source notes and process-slot references, then "
            "run the validator. Stop before evidence-builder execution, staffed "
            "support, support-case creation, customer communication, customer or "
            "vendor contact, blocker closure, or production claims."
        ),
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_prompt"] = 0
    return payload


def render_metadata_list(fields: list[dict[str, Any]]) -> str:
    return "\n".join(f"- `{field['field_name']}`" for field in fields)


def render_key_list(keys: list[dict[str, Any]]) -> str:
    rows = [
        "| Evidence Key | Review Flag | Source Note | Process Slot | Evidence Reference | Owner Named | Reviewed By Human | Codex May Fill |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in keys:
        key = item["evidence_key"]
        rows.append(
            f"| `{key}` | set true only after human approval | required | required | required | required | required | false |"
        )
    return "\n".join(rows)


def render_html(payload: dict[str, Any]) -> str:
    metadata_items = "\n".join(
        f"<li><code>{item['field_name']}</code></li>"
        for item in payload["metadata_fields_to_fill"]
    )
    evidence_items = "\n".join(
        f"<li><code>{item['evidence_key']}</code></li>"
        for item in payload["customer_support_evidence_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 客户支持流程人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f4f1ea;
        --card: #fffdf8;
        --soft: #ebe6db;
        --ink: #151814;
        --text: #363a34;
        --muted: #6f6a60;
        --line: #ded7c9;
        --accent: #16715f;
        --danger: #9d3328;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #fffdf8 0%, var(--bg) 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.65;
      }}
      main {{
        width: min(1080px, calc(100% - 32px));
        margin: 0 auto;
        padding: clamp(36px, 7vw, 76px) 0;
      }}
      .hero {{
        display: grid;
        grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.75fr);
        gap: 28px;
        align-items: start;
      }}
      h1 {{
        margin: 0;
        max-width: 780px;
        color: var(--ink);
        font-size: clamp(34px, 5vw, 58px);
        line-height: 1.08;
        letter-spacing: 0;
      }}
      h2 {{
        margin: 0 0 12px;
        color: var(--ink);
        font-size: 22px;
      }}
      p {{ margin: 16px 0 0; }}
      code {{
        padding: 2px 6px;
        border-radius: 6px;
        background: var(--soft);
        color: var(--ink);
        font-size: 0.92em;
      }}
      .card {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--card);
        padding: 22px;
        box-shadow: 0 18px 48px rgba(36, 35, 31, 0.08);
      }}
      .status {{
        display: inline-flex;
        margin-top: 22px;
        padding: 8px 12px;
        border-radius: 999px;
        background: #f4ded9;
        color: var(--danger);
        font-weight: 800;
        font-size: 13px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        margin-top: 28px;
      }}
      ul {{
        margin: 0;
        padding-left: 20px;
      }}
      li + li {{ margin-top: 8px; }}
      .steps {{
        display: grid;
        gap: 12px;
        margin-top: 26px;
      }}
      .step {{
        display: grid;
        grid-template-columns: 36px 1fr;
        gap: 12px;
        align-items: start;
        padding: 14px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #faf7ef;
      }}
      .num {{
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: var(--ink);
        color: #fff;
        font-weight: 900;
      }}
      .boundary {{
        margin-top: 28px;
        background: #1e2a24;
        color: #f4f1ea;
      }}
      .boundary h2 {{ color: #fff; }}
      .boundary code {{
        background: rgba(255, 255, 255, 0.09);
        color: #fff;
      }}
      @media (max-width: 840px) {{
        .hero, .grid {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div>
          <h1>先把客服流程审清楚，再决定能不能对用户承诺支持。</h1>
          <p>这个页面只帮人工审查 <code>customer_support</code> 需要填什么。它不是客服系统，也不会创建工单或联系客户。</p>
          <span class="status">{payload['plain_language_status_label']}</span>
        </div>
        <aside class="card">
          <h2>当前边界</h2>
          <ul>
            <li>Codex 可代执行：<code>false</code></li>
            <li>customer_support_available: <code>false</code></li>
            <li>customer_support_published: <code>false</code></li>
            <li>support_case_created: <code>false</code></li>
            <li>customer_contacted: <code>false</code></li>
            <li>production_ready: <code>false</code></li>
            <li>private_core_exposed: <code>false</code></li>
          </ul>
        </aside>
      </section>

      <section class="steps">
        <div class="step"><span class="num">1</span><div><strong>复制本地模板。</strong><br><code>{payload['copy_template_command']}</code></div></div>
        <div class="step"><span class="num">2</span><div><strong>人工填写客服流程信息。</strong><br>{payload['plain_language_next_action']}</div></div>
        <div class="step"><span class="num">3</span><div><strong>运行本地验证。</strong><br><code>{payload['validator_command']}</code></div></div>
        <div class="step"><span class="num">4</span><div><strong>验证后停下。</strong><br>{payload['plain_language_stop_point']}</div></div>
      </section>

      <section class="grid">
        <article class="card">
          <h2>要填的基本信息</h2>
          <ul>{metadata_items}</ul>
        </article>
        <article class="card">
          <h2>要逐项审的客服证据</h2>
          <ul>{evidence_items}</ul>
        </article>
      </section>

      <section class="card boundary">
        <h2>这一步不能做什么</h2>
        <p>不启用客服，不创建工单，不发送客户通知，不联系客户或供应商，不执行证据生成器，不关闭 blocker，不声明正式商用。</p>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["customer_support_evidence_keys_to_review"])
    content = f"""# SAEE Customer Support Approval Input Prompt

customer_support_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_customer_support_evidence_item_count: {payload['required_customer_support_evidence_item_count']}
completed_customer_support_evidence_item_count: {payload['completed_customer_support_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
customer_support_available: false
customer_support_approved: false
customer_support_configured: false
customer_support_published: false
support_operations_started: false
support_process_started: false
support_case_created: false
customer_communication_sent: false
staffed_support_started: false
source_customer_support_approval_input_prompt_html: {payload['source_customer_support_approval_input_prompt_html']}
local_static_customer_support_approval_input_prompt_html: true
browser_readable_customer_support_approval_input_prompt: true
plain_language_customer_support_approval_input_prompt_v0_2: true
customer_support_human_review_step_count: {payload['customer_support_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`customer_support` process input before validator use.

## Metadata Fields To Fill

{metadata}

## Customer Support Evidence Keys To Review

{evidence_table}

## Copy Template

```bash
{payload['copy_template_command']}
```

## Validate Human-Filled Input

```bash
{payload['validator_command']}
```

## Stop Point

After validation, stop. Evidence-builder execution, customer-support approval,
customer-support publication, staffing support, support-case creation, customer
communication, support operations, customer/vendor contact, blocker closure,
launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve, configure, publish, staff, or start customer
support; create support cases; send customer communications; contact customers
or vendors; execute the evidence builder; close blockers; launch product;
modify runtime/backend/kernel/API schema; expose private core; or claim
production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Customer Support Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_customer_support_input_prompt: true
recommend_for_customer_support_approval_by_codex: false
recommend_for_customer_support_publication: false
recommend_for_customer_support_configuration: false
recommend_for_staffed_support_start: false
recommend_for_support_case_creation: false
recommend_for_customer_communication: false
recommend_for_support_operations_start: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`customer_support` process template. It makes required metadata and
customer-support evidence keys explicit without approving, publishing, staffing,
or operating support.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- ready_for_evidence_builder: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- customer_support_available: false
- customer_support_approved: false
- customer_support_configured: false
- customer_support_published: false
- support_operations_started: false
- support_case_created: false
- customer_communication_sent: false
- staffed_support_started: false
- production_support_available: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_CUSTOMER_SUPPORT_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "customer_support_evidence_keys="
        + ",".join(
            item["evidence_key"]
            for item in payload["customer_support_evidence_keys_to_review"]
        )
    )
    print(f"html_entrypoint={payload['source_customer_support_approval_input_prompt_html']}")
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(
        "boundary=human_input_only_no_customer_support_approval_no_publication_no_blocker_closure"
    )


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
