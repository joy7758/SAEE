#!/usr/bin/env python3
"""Build a human input prompt for SLA approval evidence.

This prompt narrows the `sla` blocker to the exact human-filled fields needed
before the existing SLA approval-input validator can pass. It does not approve
or publish SLA terms, complete legal review, publish support hours or response
targets, start support operations, contact customers/vendors, execute the
evidence builder, close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
TEMPLATE = EVIDENCE_DIR / "sla_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "sla_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "sla_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "sla_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "sla_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SLA_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SLA_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "sla_evidence_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "sla_terms_owner",
    "legal_reviewer_name",
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
    "sla_approved_by_codex",
    "sla_published_by_codex",
    "legal_review_completed_by_codex",
    "support_hours_published_by_codex",
    "response_targets_published_by_codex",
    "support_operations_started",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "codex_inferred_missing_evidence",
    "production_sla_claim_published",
    "production_support_claim_published",
    "support_contact_available",
    "customer_support_available",
    "sla_available",
    "on_call_rotation_available",
    "production_support_available",
    "support_vendor_contacted",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"SAEE_SLA_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_SLA_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sla_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit("SAEE_SLA_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing")
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = sla_keys(template)
    slots = template.get("sla_evidence_slots", [])
    if not isinstance(slots, list):
        raise SystemExit("SAEE_SLA_APPROVAL_INPUT_PROMPT: FAIL sla_evidence_slots missing")

    payload: dict[str, Any] = {
        "sla_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_sla_approval_input_prompt",
        "prompt_scope": "local_human_sla_input_prompt_only",
        "status": "hold_human_sla_input_required",
        "target_blocker_id": "sla",
        "category": "support",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_sla_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_sla_approval_input_prompt_html": rel(OUTPUT_HTML),
        "local_static_sla_approval_input_prompt_html": True,
        "browser_readable_sla_approval_input_prompt": True,
        "plain_language_sla_approval_input_prompt_v0_2": True,
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "sla_available": False,
        "sla_approved": False,
        "sla_published": False,
        "legal_review_completed": False,
        "support_hours_published": False,
        "response_targets_published": False,
        "support_operations_started": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_sla_evidence_item_count": len(keys),
        "completed_sla_evidence_item_count": 0,
        "sla_human_review_step_count": 4,
        "plain_language_status_label": (
            "SLA 还没有批准，也没有发布，不能对外承诺服务响应。"
        ),
        "plain_language_next_action": (
            "先由人审服务承诺负责人、法务审核人、支持时间、响应目标、"
            "升级路径和对外说明，再填写本地证据模板。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不发布 SLA、不启动支持运营、"
            "不联系客户、不关闭阻塞项。"
        ),
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "sla_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "sla_evidence_slot_required": True,
                "owner_named_required": True,
                "legal_or_commercial_review_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_sla_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make sla-approval-input-prompt",
        "check_target": "make check-sla-approval-input-prompt",
        "next_human_action": (
            "Copy the SLA evidence template, fill all metadata fields, set each "
            "SLA evidence review key only after human approval, add source notes "
            "and evidence-slot references, then run the validator. Stop before "
            "evidence-builder execution, SLA publication, support operations, "
            "customer/vendor contact, blocker closure, or production claims."
        ),
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_prompt"] = 0
    return payload


def render_metadata_list(fields: list[dict[str, Any]]) -> str:
    return "\n".join(f"- `{field['field_name']}`" for field in fields)


def render_key_list(keys: list[dict[str, Any]]) -> str:
    rows = [
        "| Evidence Key | Review Flag | Source Note | Evidence Slot | Owner Named | Legal/Commercial Review | Reviewed By Human | Codex May Fill |",
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
        for item in payload["sla_evidence_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE SLA 人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f8fafc;
        --card: #ffffff;
        --soft: #edf4ff;
        --ink: #111827;
        --text: #374151;
        --muted: #667085;
        --line: #e5e7eb;
        --accent: #2563eb;
        --danger: #b42318;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 100%);
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
        box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
      }}
      .status {{
        display: inline-flex;
        margin-top: 22px;
        padding: 8px 12px;
        border-radius: 999px;
        background: #fff1f0;
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
        background: #ffffff;
      }}
      .num {{
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #fff;
        font-weight: 900;
      }}
      .boundary {{
        margin-top: 28px;
        background: #0f172a;
        color: #f8fafc;
      }}
      .boundary h2 {{ color: #fff; }}
      .boundary code {{
        background: rgba(255, 255, 255, 0.12);
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
          <h1>先把服务承诺审清楚，再谈对外 SLA。</h1>
          <p>这个页面只帮人工审查 <code>sla</code> 需要填什么。它不是 SLA 发布页，也不会启动客服或联系客户。</p>
          <span class="status">{payload['plain_language_status_label']}</span>
        </div>
        <aside class="card">
          <h2>当前边界</h2>
          <ul>
            <li>Codex 可代执行：<code>false</code></li>
            <li>sla_available: <code>false</code></li>
            <li>sla_approved: <code>false</code></li>
            <li>sla_published: <code>false</code></li>
            <li>support_operations_started: <code>false</code></li>
            <li>customer_contacted: <code>false</code></li>
            <li>production_ready: <code>false</code></li>
            <li>private_core_exposed: <code>false</code></li>
          </ul>
        </aside>
      </section>

      <section class="steps">
        <div class="step"><span class="num">1</span><div><strong>复制本地模板。</strong><br><code>{payload['copy_template_command']}</code></div></div>
        <div class="step"><span class="num">2</span><div><strong>人工填写 SLA 审查信息。</strong><br>{payload['plain_language_next_action']}</div></div>
        <div class="step"><span class="num">3</span><div><strong>运行本地验证。</strong><br><code>{payload['validator_command']}</code></div></div>
        <div class="step"><span class="num">4</span><div><strong>验证后停下。</strong><br>{payload['plain_language_stop_point']}</div></div>
      </section>

      <section class="grid">
        <article class="card">
          <h2>要填的基本信息</h2>
          <ul>{metadata_items}</ul>
        </article>
        <article class="card">
          <h2>要逐项审的 SLA 证据</h2>
          <ul>{evidence_items}</ul>
        </article>
      </section>

      <section class="card boundary">
        <h2>这一步不能做什么</h2>
        <p>不批准 SLA，不发布 SLA，不完成法务审核，不发布支持时间或响应目标，不启动支持运营，不联系客户或供应商，不执行证据生成器，不关闭 blocker，不声明正式商用。</p>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["sla_evidence_keys_to_review"])
    content = f"""# SAEE SLA Approval Input Prompt

sla_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_sla_evidence_item_count: {payload['required_sla_evidence_item_count']}
completed_sla_evidence_item_count: {payload['completed_sla_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
sla_available: false
sla_approved: false
sla_published: false
legal_review_completed: false
support_hours_published: false
response_targets_published: false
support_operations_started: false
source_sla_approval_input_prompt_html: {payload['source_sla_approval_input_prompt_html']}
local_static_sla_approval_input_prompt_html: true
browser_readable_sla_approval_input_prompt: true
plain_language_sla_approval_input_prompt_v0_2: true
sla_human_review_step_count: {payload['sla_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`sla` approval input before validator use.

## Metadata Fields To Fill

{metadata}

## SLA Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, SLA approval, SLA
publication, support-hours publication, response-target publication, legal
review completion, support operations, customer/vendor contact, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve SLA terms, publish SLA terms, complete legal
review, publish support hours, publish response targets, start support
operations, contact customers or vendors, execute the evidence builder, close
blockers, launch product, modify runtime/backend/kernel/API schema, expose
private core, or claim production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE SLA Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_sla_input_prompt: true
recommend_for_sla_approval_by_codex: false
recommend_for_sla_publication: false
recommend_for_legal_review_completion: false
recommend_for_support_hours_publication: false
recommend_for_response_targets_publication: false
recommend_for_support_operations_start: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the `sla`
approval template. It makes required metadata and SLA evidence keys explicit
without approving, publishing, or operating SLA commitments.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- ready_for_evidence_builder: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- sla_available: false
- sla_approved: false
- sla_published: false
- legal_review_completed: false
- support_hours_published: false
- response_targets_published: false
- support_operations_started: false
- production_support_available: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_SLA_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "sla_evidence_keys="
        + ",".join(item["evidence_key"] for item in payload["sla_evidence_keys_to_review"])
    )
    print(f"html_entrypoint={payload['source_sla_approval_input_prompt_html']}")
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print("boundary=human_input_only_no_sla_approval_no_publication_no_blocker_closure")


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
