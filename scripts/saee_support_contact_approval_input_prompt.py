#!/usr/bin/env python3
"""Build a human input prompt for support-contact decision evidence.

This prompt narrows the `support_contact` blocker to the exact human-filled
fields needed before the existing support-contact approval-input validator can
pass. It does not approve, configure, publish, or test a support contact;
contact customers/vendors; execute the evidence builder; close blockers; or
claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
TEMPLATE = EVIDENCE_DIR / "support_contact_decision_input.template.json"
VALIDATION = EVIDENCE_DIR / "support_contact_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "support_contact_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "support_contact_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "support_contact_approval_input_prompt.html"
AGENT_INDEX = ROOT / "agent-index.json"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "support_contact_decision_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "selected_support_contact_channel",
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
    "support_contact_approved_by_codex",
    "support_contact_configured_by_codex",
    "support_contact_published_by_codex",
    "support_contact_tested_by_codex",
    "codex_published_support_contact",
    "codex_sent_support_contact_test",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "codex_inferred_missing_evidence",
    "customer_facing_support_contact_configured",
    "support_contact_available",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "customer_support_available",
    "production_support_available",
    "support_process_available",
    "sla_available",
    "on_call_rotation_available",
    "staffed_support_started",
    "support_case_created",
    "sla_published",
    "on_call_rotation_started",
    "support_operations_started",
    "support_vendor_contacted",
    "support_contact_claim_published",
    "production_support_claim_published",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_agent_index(payload: dict[str, Any]) -> None:
    if AGENT_INDEX.exists():
        index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
        if not isinstance(index, dict):
            raise SystemExit(
                "SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT: FAIL agent-index must be object"
            )
    else:
        index = {}

    existing = index.get("support_contact_approval_input_prompt_v0_1", {})
    entry_keys = [
        "support_contact_approval_input_prompt_v0_1",
        "status",
        "prompt_type",
        "prompt_scope",
        "category",
        "target_blocker_id",
        "required_metadata_field_count",
        "completed_metadata_field_count",
        "required_support_contact_evidence_item_count",
        "completed_support_contact_evidence_item_count",
        "candidate_contact_slot_count",
        "minimum_completed_contact_slot_count",
        "completed_contact_slot_count",
        "validation_status",
        "builder_ready",
        "ready_for_evidence_builder",
        "support_contact_available",
        "support_contact_approved",
        "support_contact_configured",
        "support_contact_published",
        "support_contact_test_performed",
        "customer_facing_support_contact_configured",
        "support_operations_started",
        "production_support_available",
        "support_process_available",
        "customer_support_available",
        "sla_available",
        "on_call_rotation_available",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "support_vendor_contacted",
        "public_sdk_released",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
        "execution_authorized",
        "evidence_collection_authorized",
        "development_permission_granted",
        "task_candidates_executed",
        "human_review_required",
        "separate_validator_required",
        "separate_evidence_builder_request_required",
        "support_contact_approved_by_codex",
        "support_contact_configured_by_codex",
        "support_contact_published_by_codex",
        "support_contact_tested_by_codex",
        "codex_published_support_contact",
        "codex_sent_support_contact_test",
        "codex_contacted_customer",
        "codex_contacted_vendor",
        "codex_inferred_missing_evidence",
        "support_contact_claim_published",
        "production_support_claim_published",
        "blockers_closed_by_prompt",
    ]
    entry = {key: payload[key] for key in entry_keys}
    entry["entrypoints"] = existing.get(
        "entrypoints",
        {
            "input_template": rel(TEMPLATE),
            "prompt_json": rel(OUTPUT_JSON),
            "prompt_markdown": rel(OUTPUT_MD),
            "recommendation_gate": rel(GATE),
            "runner": "scripts/saee_support_contact_approval_input_prompt.py",
            "smoke": "scripts/saee_support_contact_approval_input_prompt_smoke.py",
            "top_doc": rel(TOP_DOC),
        },
    )
    index["support_contact_approval_input_prompt_v0_1"] = entry
    AGENT_INDEX.write_text(
        json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def support_contact_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    return sorted(review)


def candidate_slots(template: dict[str, Any]) -> list[dict[str, Any]]:
    slots = template.get("candidate_contact_slots", [])
    if not isinstance(slots, list):
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT: FAIL candidate_contact_slots missing"
        )
    return [slot for slot in slots if isinstance(slot, dict)]


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = support_contact_keys(template)
    slots = candidate_slots(template)

    payload: dict[str, Any] = {
        "support_contact_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_support_contact_approval_input_prompt",
        "prompt_scope": "local_human_support_contact_input_prompt_only",
        "status": "hold_human_support_contact_input_required",
        "target_blocker_id": "support_contact",
        "category": "support",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_support_contact_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_support_contact_approval_input_prompt_html": rel(OUTPUT_HTML),
        "local_static_support_contact_approval_input_prompt_html": True,
        "browser_readable_support_contact_approval_input_prompt": True,
        "plain_language_support_contact_approval_input_prompt_v0_2": True,
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "support_contact_available": False,
        "support_contact_approved": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "customer_facing_support_contact_configured": False,
        "support_operations_started": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_support_contact_evidence_item_count": len(keys),
        "completed_support_contact_evidence_item_count": 0,
        "candidate_contact_slot_count": len(slots),
        "minimum_completed_contact_slot_count": 1,
        "completed_contact_slot_count": 0,
        "support_contact_human_review_step_count": 4,
        "plain_language_status_label": (
            "客户支持入口还没有批准，也没有启用。"
        ),
        "plain_language_next_action": (
            "先由人审支持渠道、负责人、滥用处理、客户通知路径和测试计划，"
            "再填写本地证据模板。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不发布支持入口、"
            "不联系客户、不启用客服流程、不关闭阻塞项。"
        ),
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "support_contact_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "source_note_key_required": f"source_notes_by_key.{key}",
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "candidate_contact_slots_to_fill": [
            {
                "slot_id": str(slot.get("slot_id", "")),
                "contact_channel_required": True,
                "display_value_redacted_required": True,
                "owner_named_required": True,
                "abuse_handling_reviewed_required": True,
                "customer_notice_route_reviewed_required": True,
                "test_plan_reviewed_required": True,
                "human_source_note_required": True,
                "codex_may_fill": False,
            }
            for slot in slots
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_support_contact_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make support-contact-approval-input-prompt",
        "check_target": "make check-support-contact-approval-input-prompt",
        "next_human_action": (
            "Copy the support-contact decision template, fill all metadata "
            "fields, select one support contact channel, set each evidence "
            "review key only after human approval, add source notes, complete at "
            "least one candidate contact slot, then run the validator. Stop "
            "before support-contact publication, tests, evidence-builder "
            "execution, customer/vendor contact, blocker closure, or production "
            "claims."
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
        "| Evidence Key | Review Flag | Source Note | Codex May Fill |",
        "| --- | --- | --- | --- |",
    ]
    for item in keys:
        key = item["evidence_key"]
        rows.append(f"| `{key}` | set true only after human approval | required | false |")
    return "\n".join(rows)


def render_slot_list(slots: list[dict[str, Any]]) -> str:
    rows = [
        "| Slot ID | Contact Channel | Redacted Display Value | Owner Named | Abuse Handling | Customer Notice Route | Test Plan | Source Note | Codex May Fill |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in slots:
        slot_id = item["slot_id"]
        rows.append(
            f"| `{slot_id}` | required | required | required | required | required | required | required | false |"
        )
    return "\n".join(rows)


def render_html(payload: dict[str, Any]) -> str:
    metadata_items = "\n".join(
        f"<li><code>{item['field_name']}</code></li>"
        for item in payload["metadata_fields_to_fill"]
    )
    evidence_items = "\n".join(
        f"<li><code>{item['evidence_key']}</code></li>"
        for item in payload["support_contact_evidence_keys_to_review"]
    )
    slot_items = "\n".join(
        f"<li><code>{item['slot_id']}</code></li>"
        for item in payload["candidate_contact_slots_to_fill"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 客户支持联系入口人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f6f7fb;
        --card: #ffffff;
        --soft: #eef2f7;
        --ink: #101828;
        --text: #344054;
        --muted: #667085;
        --line: #d8dee8;
        --accent: #4f46e5;
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
        max-width: 760px;
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
        box-shadow: 0 18px 48px rgba(16, 24, 40, 0.06);
      }}
      .status {{
        display: inline-flex;
        margin-top: 22px;
        padding: 8px 12px;
        border-radius: 999px;
        background: #fff1f3;
        color: var(--danger);
        font-weight: 800;
        font-size: 13px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
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
        background: #fbfcff;
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
        background: #111827;
        color: #eef2f7;
      }}
      .boundary h2 {{ color: #fff; }}
      .boundary code {{
        background: rgba(255, 255, 255, 0.08);
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
          <h1>先把客户支持入口审清楚，再决定能不能公开给用户。</h1>
          <p>这个页面只帮人工审查 <code>support_contact</code> 需要填什么。它不是客服入口，也不会发送消息。</p>
          <span class="status">{payload['plain_language_status_label']}</span>
        </div>
        <aside class="card">
          <h2>当前边界</h2>
          <ul>
            <li>Codex 可代执行：<code>false</code></li>
            <li>support_contact_available: <code>false</code></li>
            <li>support_contact_published: <code>false</code></li>
            <li>customer_contacted: <code>false</code></li>
            <li>production_ready: <code>false</code></li>
            <li>private_core_exposed: <code>false</code></li>
          </ul>
        </aside>
      </section>

      <section class="steps">
        <div class="step"><span class="num">1</span><div><strong>复制本地模板。</strong><br><code>{payload['copy_template_command']}</code></div></div>
        <div class="step"><span class="num">2</span><div><strong>人工填写支持入口信息。</strong><br>{payload['plain_language_next_action']}</div></div>
        <div class="step"><span class="num">3</span><div><strong>运行本地验证。</strong><br><code>{payload['validator_command']}</code></div></div>
        <div class="step"><span class="num">4</span><div><strong>验证后停下。</strong><br>{payload['plain_language_stop_point']}</div></div>
      </section>

      <section class="grid">
        <article class="card">
          <h2>要填的基本信息</h2>
          <ul>{metadata_items}</ul>
        </article>
        <article class="card">
          <h2>要逐项审的证据</h2>
          <ul>{evidence_items}</ul>
        </article>
        <article class="card">
          <h2>候选支持入口</h2>
          <ul>{slot_items}</ul>
        </article>
      </section>

      <section class="card boundary">
        <h2>这一步不能做什么</h2>
        <p>不发布支持入口，不配置客服，不发测试消息，不联系客户或供应商，不执行证据生成器，不关闭 blocker，不声明正式商用。</p>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["support_contact_evidence_keys_to_review"])
    slot_table = render_slot_list(payload["candidate_contact_slots_to_fill"])
    content = f"""# SAEE Support Contact Approval Input Prompt

support_contact_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_support_contact_evidence_item_count: {payload['required_support_contact_evidence_item_count']}
completed_support_contact_evidence_item_count: {payload['completed_support_contact_evidence_item_count']}
candidate_contact_slot_count: {payload['candidate_contact_slot_count']}
minimum_completed_contact_slot_count: {payload['minimum_completed_contact_slot_count']}
completed_contact_slot_count: {payload['completed_contact_slot_count']}
builder_ready: false
ready_for_evidence_builder: false
support_contact_available: false
support_contact_approved: false
support_contact_configured: false
support_contact_published: false
support_contact_test_performed: false
customer_facing_support_contact_configured: false
support_operations_started: false
source_support_contact_approval_input_prompt_html: {payload['source_support_contact_approval_input_prompt_html']}
local_static_support_contact_approval_input_prompt_html: true
browser_readable_support_contact_approval_input_prompt: true
plain_language_support_contact_approval_input_prompt_v0_2: true
support_contact_human_review_step_count: {payload['support_contact_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`support_contact` decision input before validator use.

## Metadata Fields To Fill

{metadata}

## Support Contact Evidence Keys To Review

{evidence_table}

## Candidate Contact Slots To Fill

{slot_table}

## Copy Template

```bash
{payload['copy_template_command']}
```

## Validate Human-Filled Input

```bash
{payload['validator_command']}
```

## Stop Point

After validation, stop. Evidence-builder execution, support-contact approval,
support-contact publication, support-contact tests, customer/vendor contact,
blocker closure, launch, and production-readiness claims require separate
approvals.

## Boundary

This prompt does not approve, configure, publish, or test a support contact;
contact customers or vendors; execute the evidence builder; close blockers;
launch product; modify runtime/backend/kernel/API schema; expose private core;
or claim production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Support Contact Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_support_contact_input_prompt: true
recommend_for_support_contact_approval_by_codex: false
recommend_for_support_contact_publication: false
recommend_for_support_contact_configuration: false
recommend_for_support_contact_test: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`support_contact` decision template. It makes required metadata, evidence keys,
and candidate contact slot fields explicit without approving, publishing,
testing, or operating support contact infrastructure.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- ready_for_evidence_builder: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- support_contact_available: false
- support_contact_approved: false
- support_contact_configured: false
- support_contact_published: false
- support_contact_test_performed: false
- customer_facing_support_contact_configured: false
- production_support_available: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_SUPPORT_CONTACT_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "support_contact_evidence_keys="
        + ",".join(
            item["evidence_key"] for item in payload["support_contact_evidence_keys_to_review"]
        )
    )
    print(f"candidate_contact_slot_count={payload['candidate_contact_slot_count']}")
    print(f"html_entrypoint={payload['source_support_contact_approval_input_prompt_html']}")
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(
        "boundary=human_input_only_no_support_contact_approval_no_publication_no_blocker_closure"
    )


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    update_agent_index(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
