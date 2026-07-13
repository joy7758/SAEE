#!/usr/bin/env python3
"""Build a human input prompt for operations on-call rotation approval.

This prompt narrows the `on_call_rotation` operations blocker to the exact
human-filled fields needed before the approval-input validator can pass. It
does not approve on-call rotation, publish schedules, assign incident
commanders, execute the evidence builder, contact customers/vendors, close
blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
TEMPLATE = EVIDENCE_DIR / "operations_on_call_rotation_evidence_input.template.json"
VALIDATION = (
    EVIDENCE_DIR / "operations_on_call_rotation_approval_input_validation.local.json"
)
OUTPUT_JSON = (
    EVIDENCE_DIR / "operations_on_call_rotation_approval_input_prompt.local.json"
)
OUTPUT_MD = EVIDENCE_DIR / "operations_on_call_rotation_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "operations_on_call_rotation_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = (
    EVIDENCE_DIR / "operations_on_call_rotation_evidence_input.human_filled.local.json"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "on_call_rotation_owner",
    "operations_reviewer_name",
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
    "on_call_rotation_approved_by_codex",
    "on_call_rotation_started_by_codex",
    "escalation_schedule_published_by_codex",
    "incident_commander_assigned_by_codex",
    "on_call_vendor_contacted_by_codex",
    "monitoring_vendor_contacted_by_codex",
    "alert_provider_contacted_by_codex",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "production_on_call_rotation_claim_published",
    "on_call_rotation_started",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT: FAIL "
            f"{rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT: FAIL "
            f"{rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def on_call_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT: FAIL "
            "evidence_review missing"
        )
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = on_call_keys(template)
    slots = template.get("on_call_rotation_evidence_slots", [])
    if not isinstance(slots, list):
        raise SystemExit(
            "SAEE_OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT: FAIL "
            "on_call_rotation_evidence_slots missing"
        )

    payload: dict[str, Any] = {
        "operations_on_call_rotation_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_operations_on_call_rotation_approval_input_prompt",
        "prompt_scope": "local_human_operations_on_call_rotation_input_prompt_only",
        "status": "hold_human_operations_on_call_rotation_input_required",
        "target_blocker_id": "on_call_rotation",
        "category": "operations",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_operations_on_call_rotation_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_operations_on_call_rotation_approval_input_prompt_html": rel(OUTPUT_HTML),
        "local_static_operations_on_call_rotation_approval_input_prompt_html": True,
        "browser_readable_operations_on_call_rotation_approval_input_prompt": True,
        "plain_language_operations_on_call_rotation_approval_input_prompt_v0_2": True,
        "operations_on_call_rotation_human_review_step_count": 4,
        "plain_language_status_label": (
            "运维值班轮转还没有人工批准，也没有启动，不能对外说已经有人正式接警和升级。"
        ),
        "plain_language_next_action": (
            "请人类负责人确认值班负责人、排班方式、升级时间表和事故负责人；"
            "确认前不要启动值班、发布升级表或关闭 blocker。"
        ),
        "plain_language_stop_point": (
            "填完并验证输入后停止；运行 evidence builder、启动值班轮转、发布升级表、"
            "指定事故负责人、联系供应商或关闭 blocker 都需要单独批准。"
        ),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "on_call_rotation_available": False,
        "on_call_rotation_approved": False,
        "on_call_rotation_started": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_on_call_rotation_evidence_item_count": len(keys),
        "completed_on_call_rotation_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "on_call_rotation_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "on_call_rotation_evidence_slot_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_operations_on_call_rotation_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make operations-on-call-rotation-approval-input-prompt",
        "check_target": "make check-operations-on-call-rotation-approval-input-prompt",
        "next_human_action": (
            "Copy the template, fill all metadata fields, set each on-call "
            "rotation review key only after human approval, add source notes "
            "and on-call rotation evidence slot references, then run the "
            "validator. Stop before evidence builder execution or on-call "
            "activation."
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


def render_key_list(keys: list[dict[str, Any]]) -> str:
    rows = [
        "| Evidence Key | Review Flag | Source Note | Evidence Slot | Owner Named | Reviewed By Human | Codex May Fill |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in keys:
        key = item["evidence_key"]
        rows.append(
            f"| `{key}` | set true only after human approval | required | required | required | required | false |"
        )
    return "\n".join(rows)


def render_metadata_list(fields: list[dict[str, Any]]) -> str:
    return "\n".join(f"- `{field['field_name']}`" for field in fields)


def render_html(payload: dict[str, Any]) -> str:
    metadata_items = "\n".join(
        f"<li><code>{escape(item['field_name'])}</code></li>"
        for item in payload["metadata_fields_to_fill"]
    )
    evidence_items = "\n".join(
        f"<li><strong>{escape(item['evidence_key'])}</strong><span>需要人工确认、来源说明、证据槽位、负责人和人工复核。</span></li>"
        for item in payload["on_call_rotation_evidence_keys_to_review"]
    )
    boundary_flags = [
        "on_call_rotation_available",
        "on_call_rotation_approved",
        "on_call_rotation_started",
        "on_call_rotation_started_by_codex",
        "escalation_schedule_published_by_codex",
        "incident_commander_assigned_by_codex",
        "on_call_vendor_contacted_by_codex",
        "customer_contacted",
        "production_ready",
        "private_core_exposed",
        "blockers_closed_by_prompt",
    ]
    boundary_items = "\n".join(
        f"<li><strong>{escape(flag)}:</strong> {escape(str(payload[flag]).lower() if isinstance(payload[flag], bool) else str(payload[flag]))}</li>"
        for flag in boundary_flags
    )
    copy_command = escape(payload["copy_template_command"])
    validator_command = escape(payload["validator_command"])
    status = escape(payload["plain_language_status_label"])
    next_action = escape(payload["plain_language_next_action"])
    stop_point = escape(payload["plain_language_stop_point"])
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 运维值班轮转人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f8fb;
        --surface: #ffffff;
        --line: #e3e7ef;
        --text: #111827;
        --muted: #667085;
        --accent: #3457d5;
        --soft: #eef2ff;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #fff 0%, var(--bg) 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.6;
      }}
      main {{
        width: min(980px, calc(100% - 32px));
        margin: 0 auto;
        padding: 56px 0;
      }}
      h1 {{
        max-width: 760px;
        margin: 0;
        font-size: clamp(34px, 5vw, 60px);
        line-height: 1.08;
        letter-spacing: 0;
      }}
      h2 {{ margin: 0 0 14px; font-size: 22px; }}
      p {{ color: var(--muted); }}
      code {{
        padding: 2px 6px;
        border-radius: 6px;
        background: var(--soft);
        color: var(--accent);
        font-size: 0.92em;
      }}
      .lead {{ max-width: 720px; font-size: 18px; }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 28px;
      }}
      section {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.92);
        padding: 22px;
        box-shadow: 0 16px 36px rgba(17, 24, 39, 0.06);
      }}
      ul, ol {{ margin: 0; padding-left: 20px; }}
      li + li {{ margin-top: 8px; }}
      .evidence-list {{ padding-left: 0; list-style: none; }}
      .evidence-list li {{
        display: grid;
        gap: 3px;
        padding: 12px 0;
        border-bottom: 1px solid var(--line);
      }}
      .evidence-list li:last-child {{ border-bottom: 0; }}
      .evidence-list span {{ color: var(--muted); }}
      .status {{
        display: inline-flex;
        margin: 18px 0 0;
        padding: 8px 12px;
        border-radius: 999px;
        background: var(--soft);
        color: var(--accent);
        font-weight: 800;
      }}
      .full {{ grid-column: 1 / -1; }}
      @media (max-width: 720px) {{
        main {{ padding: 36px 0; }}
        .grid {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <p class="status">等待人工填写</p>
      <h1>先确认谁值班、谁升级，再谈正式商用。</h1>
      <p class="lead">{status}</p>
      <div class="grid">
        <section>
          <h2>人要先确认什么？</h2>
          <ol>
            <li>谁负责运维值班轮转。</li>
            <li>排班怎么覆盖工作日和非工作日。</li>
            <li>升级时间表和升级路径是否清楚。</li>
            <li>事故负责人是否已经明确。</li>
          </ol>
        </section>
        <section>
          <h2>必须由人填写的字段</h2>
          <ul>{metadata_items}</ul>
        </section>
        <section class="full">
          <h2>必须由人审查的值班证据</h2>
          <ul class="evidence-list">{evidence_items}</ul>
        </section>
        <section>
          <h2>下一步人工动作</h2>
          <p>{next_action}</p>
          <p><code>{copy_command}</code></p>
          <p><code>{validator_command}</code></p>
        </section>
        <section>
          <h2>到这里必须停下</h2>
          <p>{stop_point}</p>
        </section>
        <section class="full">
          <h2>边界状态</h2>
          <ul>{boundary_items}</ul>
        </section>
      </div>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["on_call_rotation_evidence_keys_to_review"])
    content = f"""# SAEE Operations On-call Rotation Approval Input Prompt

operations_on_call_rotation_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_on_call_rotation_evidence_item_count: {payload['required_on_call_rotation_evidence_item_count']}
completed_on_call_rotation_evidence_item_count: {payload['completed_on_call_rotation_evidence_item_count']}
builder_ready: false
on_call_rotation_available: false
on_call_rotation_approved: false
on_call_rotation_started: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`on_call_rotation` operations approval input before validator use.

## Metadata Fields To Fill

{metadata}

## On-call Rotation Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, on-call activation,
escalation schedule publication, incident commander assignment, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve on-call rotation, fill evidence, publish
escalation schedules, assign incident commanders, touch live operations paths,
contact customers or vendors, execute the evidence builder, close blockers,
launch product, modify runtime/backend/kernel/API schema, expose private core,
or claim production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Operations On-call Rotation Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_operations_on_call_rotation_input_prompt: true
recommend_for_on_call_rotation_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_on_call_activation: false
recommend_for_escalation_schedule_publication: false
recommend_for_incident_commander_assignment: false
recommend_for_vendor_contact: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`on_call_rotation` operations approval template. It makes the required metadata
and on-call rotation evidence keys explicit without approving or starting
on-call operations.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- on_call_rotation_available: false
- on_call_rotation_approved: false
- on_call_rotation_started: false
- on_call_rotation_started_by_codex: false
- escalation_schedule_published_by_codex: false
- incident_commander_assigned_by_codex: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_OPERATIONS_ON_CALL_ROTATION_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "on_call_rotation_evidence_keys="
        + ",".join(
            item["evidence_key"]
            for item in payload["on_call_rotation_evidence_keys_to_review"]
        )
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(f"html_entrypoint={rel(OUTPUT_HTML)}")
    print("boundary=human_input_only_no_on_call_approval_no_activation_no_blocker_closure")


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
