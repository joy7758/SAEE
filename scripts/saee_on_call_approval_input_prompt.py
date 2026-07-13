#!/usr/bin/env python3
"""Build a human input prompt for on-call approval evidence.

This prompt narrows the `on_call_rotation` blocker to the exact human-filled
fields needed before the existing on-call approval-input validator can pass. It
does not start on-call rotation, publish escalation schedules, assign incident
commanders, start support operations, contact customers/vendors, execute the
evidence builder, close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
TEMPLATE = EVIDENCE_DIR / "on_call_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "on_call_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "on_call_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "on_call_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "on_call_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/ON_CALL_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_ON_CALL_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "on_call_evidence_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "on_call_owner",
    "incident_operations_owner",
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
    "on_call_rotation_started",
    "on_call_rotation_started_by_codex",
    "escalation_schedule_published",
    "escalation_schedule_published_by_codex",
    "incident_commander_assigned",
    "incident_commander_assigned_by_codex",
    "support_operations_started",
    "support_case_created",
    "customer_communication_sent",
    "staffed_support_started",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "codex_inferred_missing_evidence",
    "production_on_call_claim_published",
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
        raise SystemExit(f"SAEE_ON_CALL_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_ON_CALL_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def on_call_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit("SAEE_ON_CALL_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing")
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = on_call_keys(template)
    slots = template.get("on_call_evidence_slots", [])
    if not isinstance(slots, list):
        raise SystemExit("SAEE_ON_CALL_APPROVAL_INPUT_PROMPT: FAIL on_call_evidence_slots missing")

    payload: dict[str, Any] = {
        "on_call_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_on_call_approval_input_prompt",
        "prompt_scope": "local_human_on_call_input_prompt_only",
        "status": "hold_human_on_call_input_required",
        "target_blocker_id": "on_call_rotation",
        "category": "operations",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_on_call_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_on_call_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "local_static_on_call_approval_input_prompt_html": True,
        "browser_readable_on_call_approval_input_prompt": True,
        "plain_language_on_call_approval_input_prompt_v0_2": True,
        "on_call_human_review_step_count": 4,
        "plain_language_status_label": (
            "值班安排还没有人工批准，也没有开始，不能对外承诺有人值守。"
        ),
        "plain_language_next_action": (
            "请人类负责人确认值班负责人、事件负责人、升级安排和证据来源；"
            "确认前不要启动值班、发布升级表或声明正式支持。"
        ),
        "plain_language_stop_point": (
            "填完并验证输入后停止；启动值班、发布升级表、指派事件指挥、"
            "运行 evidence builder、联系客户或关闭 blocker 都需要单独批准。"
        ),
        "builder_ready": False,
        "on_call_rotation_available": False,
        "on_call_rotation_approved": False,
        "on_call_rotation_started": False,
        "escalation_schedule_published": False,
        "incident_commander_assigned": False,
        "support_operations_started": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_on_call_evidence_item_count": len(keys),
        "completed_on_call_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "on_call_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "on_call_evidence_slot_required": True,
                "evidence_reference_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_on_call_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make on-call-approval-input-prompt",
        "check_target": "make check-on-call-approval-input-prompt",
        "next_human_action": (
            "Copy the on-call evidence template, fill all metadata fields, set "
            "each on-call evidence review key only after human approval, add "
            "source notes and on-call evidence-slot references, then run the "
            "validator. Stop before evidence-builder execution, on-call start, "
            "escalation schedule publication, incident commander assignment, "
            "support operations, customer/vendor contact, blocker closure, or "
            "production claims."
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
        "| Evidence Key | Review Flag | Source Note | Evidence Slot | Evidence Reference | Owner Named | Reviewed By Human | Codex May Fill |",
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
        f"<li><code>{field['field_name']}</code></li>"
        for field in payload["metadata_fields_to_fill"]
    )
    evidence_items = "\n".join(
        f"<li><strong>{item['evidence_key']}</strong><span>需要人工确认、来源说明、证据槽位、证据引用、负责人和人工复核。</span></li>"
        for item in payload["on_call_evidence_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 值班安排人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f6f6f3;
        --surface: #ffffff;
        --surface-soft: #eef3ef;
        --text: #232521;
        --muted: #686d64;
        --line: #e2e1dc;
        --accent: #1f7a68;
        --ink: #141613;
        --danger: #9f3a32;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.6;
      }}
      main {{
        width: min(1040px, calc(100% - 32px));
        margin: 0 auto;
        padding: 48px 0 64px;
      }}
      header {{
        display: grid;
        gap: 18px;
        padding: 28px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
        box-shadow: 0 20px 54px rgba(20, 22, 19, 0.08);
      }}
      .label {{
        margin: 0;
        color: var(--accent);
        font-size: 13px;
        font-weight: 800;
      }}
      h1 {{
        max-width: 820px;
        margin: 0;
        color: var(--ink);
        font-size: clamp(34px, 5vw, 58px);
        line-height: 1.05;
        letter-spacing: 0;
      }}
      p {{ margin: 0; }}
      .lead {{
        max-width: 760px;
        color: var(--muted);
        font-size: 18px;
      }}
      .status-grid, .cards {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-top: 22px;
      }}
      .pill, .card {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
      }}
      .pill {{
        padding: 16px;
      }}
      .pill span {{
        display: block;
        color: var(--muted);
        font-size: 13px;
      }}
      .pill strong {{
        display: block;
        margin-top: 4px;
        color: var(--ink);
        font-size: 20px;
      }}
      section {{
        margin-top: 24px;
        padding: 24px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.86);
      }}
      h2 {{
        margin: 0 0 12px;
        color: var(--ink);
        font-size: 24px;
        line-height: 1.18;
      }}
      ol, ul {{
        margin: 0;
        padding-left: 22px;
      }}
      li + li {{ margin-top: 8px; }}
      code {{
        padding: 2px 5px;
        border-radius: 6px;
        background: var(--surface-soft);
        color: var(--ink);
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.92em;
      }}
      .cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .card {{ padding: 18px; }}
      .card strong {{ display: block; margin-bottom: 4px; }}
      .card span {{ color: var(--muted); }}
      .danger {{
        border-color: rgba(159, 58, 50, 0.22);
        background: #fff8f6;
      }}
      .danger strong {{ color: var(--danger); }}
      .boundary-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }}
      .boundary-grid div {{
        padding: 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
      }}
      @media (max-width: 760px) {{
        .status-grid, .cards, .boundary-grid {{ grid-template-columns: 1fr; }}
        main {{ width: min(100% - 24px, 1040px); padding-top: 24px; }}
        header, section {{ padding: 20px; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="label">SAEE 值班安排人工审批入口</p>
        <h1>先确认谁负责值守，再谈正式商用。</h1>
        <p class="lead">{payload['plain_language_status_label']}</p>
        <div class="status-grid" aria-label="当前状态">
          <div class="pill"><span>当前状态</span><strong>等待人工填写</strong></div>
          <div class="pill"><span>需要填写</span><strong>{payload['required_metadata_field_count']} 项人员信息</strong></div>
          <div class="pill"><span>需要审查</span><strong>{payload['required_on_call_evidence_item_count']} 项值班证据</strong></div>
        </div>
      </header>

      <section>
        <h2>人要先确认什么？</h2>
        <ol>
          <li>复制模板：<code>{payload['copy_template_command']}</code></li>
          <li>填写值班负责人、事件负责人、审核人和审核日期。</li>
          <li>逐项确认值班轮换、升级安排和事件指挥证据。</li>
          <li>运行验证：<code>{payload['validator_command']}</code></li>
        </ol>
      </section>

      <section>
        <h2>必须由人填写的字段</h2>
        <ul>{metadata_items}</ul>
      </section>

      <section>
        <h2>必须由人审查的值班证据</h2>
        <div class="cards">{evidence_items}</div>
      </section>

      <section class="danger">
        <h2>到这里必须停下</h2>
        <p>{payload['plain_language_stop_point']}</p>
      </section>

      <section>
        <h2>边界状态</h2>
        <div class="boundary-grid">
          <div><strong>on_call_rotation_available:</strong> false</div>
          <div><strong>on_call_rotation_approved:</strong> false</div>
          <div><strong>on_call_rotation_started:</strong> false</div>
          <div><strong>escalation_schedule_published:</strong> false</div>
          <div><strong>incident_commander_assigned:</strong> false</div>
          <div><strong>support_operations_started:</strong> false</div>
          <div><strong>customer_contacted:</strong> false</div>
          <div><strong>production_ready:</strong> false</div>
          <div><strong>private_core_exposed:</strong> false</div>
          <div><strong>blockers_closed_by_prompt:</strong> 0</div>
        </div>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["on_call_evidence_keys_to_review"])
    content = f"""# SAEE On-call Approval Input Prompt

on_call_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_on_call_evidence_item_count: {payload['required_on_call_evidence_item_count']}
completed_on_call_evidence_item_count: {payload['completed_on_call_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
on_call_rotation_available: false
on_call_rotation_approved: false
on_call_rotation_started: false
escalation_schedule_published: false
incident_commander_assigned: false
support_operations_started: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`on_call_rotation` evidence input before validator use.

## Metadata Fields To Fill

{metadata}

## On-call Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, on-call rotation start,
escalation schedule publication, incident commander assignment, support
operations, customer/vendor contact, blocker closure, launch, and
production-readiness claims require separate approvals.

## Boundary

This prompt does not start on-call rotation, publish escalation schedules,
assign incident commanders, start support operations, contact customers or
vendors, execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, or claim production
readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")


def write_gate() -> None:
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        """# SAEE On-call Approval Input Prompt Recommendation Gate

answer: recommend

recommend_for_human_on_call_input_prompt: true
recommend_for_on_call_approval_by_codex: false
recommend_for_on_call_start: false
recommend_for_escalation_schedule_publication: false
recommend_for_incident_commander_assignment: false
recommend_for_support_operations_start: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_customer_contact: false
recommend_for_vendor_contact: false
recommend_for_production: false

## Reason

The prompt is recommendable as an agent-readable human-input guide because it
narrows the on_call_rotation blocker to concrete fields the human reviewer must
fill before validator use. It is not approval, execution, evidence collection,
on-call start, escalation publication, incident commander assignment, blocker
closure, or production launch.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
on_call_rotation_available: false
on_call_rotation_started: false
escalation_schedule_published: false
incident_commander_assigned: false
support_operations_started: false
production_support_available: false
builder_ready: false
ready_for_evidence_builder: false
blockers_closed_by_prompt: 0
""",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    write_gate()
    print(
        "SAEE_ON_CALL_APPROVAL_INPUT_PROMPT: PASS "
        f"status={payload['status']} "
        f"required_metadata_field_count={payload['required_metadata_field_count']} "
        f"required_on_call_evidence_item_count={payload['required_on_call_evidence_item_count']} "
        f"html_entrypoint={rel(OUTPUT_HTML)} "
        "builder_ready=false blockers_closed_by_prompt=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
