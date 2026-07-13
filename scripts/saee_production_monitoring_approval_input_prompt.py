#!/usr/bin/env python3
"""Build a human input prompt for production-monitoring approval.

This prompt narrows the `production_monitoring` blocker to the exact
human-filled fields needed before the existing approval-input validator can
pass. It does not approve monitoring, deploy monitoring, configure dashboards,
enable metrics export, change log retention, contact customers/vendors, close
blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/operations_evidence"
TEMPLATE = EVIDENCE_DIR / "production_monitoring_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "production_monitoring_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "production_monitoring_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "production_monitoring_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "production_monitoring_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = (
    EVIDENCE_DIR / "production_monitoring_evidence_input.human_filled.local.json"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "monitoring_owner",
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
    "production_monitoring_approved_by_codex",
    "production_monitoring_deployed_by_codex",
    "dashboard_configured_by_codex",
    "metrics_export_enabled_by_codex",
    "log_retention_changed_by_codex",
    "monitoring_vendor_contacted_by_codex",
    "alert_provider_contacted_by_codex",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "production_monitoring_claim_published",
    "production_monitoring_deployed",
    "external_alert_delivery_enabled",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def monitoring_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = monitoring_keys(template)
    slots = template.get("monitoring_evidence_slots", [])
    if not isinstance(slots, list):
        raise SystemExit(
            "SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT: FAIL monitoring_evidence_slots missing"
        )

    payload: dict[str, Any] = {
        "production_monitoring_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_production_monitoring_approval_input_prompt",
        "prompt_scope": "local_human_production_monitoring_input_prompt_only",
        "status": "hold_human_production_monitoring_input_required",
        "target_blocker_id": "production_monitoring",
        "category": "operations",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_production_monitoring_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_production_monitoring_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "local_static_production_monitoring_approval_input_prompt_html": True,
        "browser_readable_production_monitoring_approval_input_prompt": True,
        "plain_language_production_monitoring_approval_input_prompt_v0_2": True,
        "production_monitoring_human_review_step_count": 4,
        "plain_language_status_label": (
            "生产监控还没有人工批准，也没有部署，不能对外说已经有人看护线上状态。"
        ),
        "plain_language_next_action": (
            "请人类负责人确认监控负责人、指标覆盖、SLO 看板、日志保留和演练证据；"
            "确认前不要部署监控、改日志策略或声明正式商用。"
        ),
        "plain_language_stop_point": (
            "填完并验证输入后停止；运行 evidence builder、部署监控、配置看板、"
            "启用指标导出、改变日志保留、联系客户或关闭 blocker 都需要单独批准。"
        ),
        "builder_ready": False,
        "production_monitoring_available": False,
        "production_monitoring_approved": False,
        "production_monitoring_deployed": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_monitoring_evidence_item_count": len(keys),
        "completed_monitoring_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "monitoring_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "monitoring_evidence_slot_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_production_monitoring_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make production-monitoring-approval-input-prompt",
        "check_target": "make check-production-monitoring-approval-input-prompt",
        "next_human_action": (
            "Copy the template, fill all metadata fields, set each monitoring evidence "
            "review key only after human approval, add source notes and monitoring "
            "evidence slot references, then run the validator. Stop before evidence "
            "builder execution or monitoring deployment."
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
        f"<li><code>{field['field_name']}</code></li>"
        for field in payload["metadata_fields_to_fill"]
    )
    evidence_items = "\n".join(
        f"<li><strong>{item['evidence_key']}</strong><span>需要人工确认、来源说明、监控证据槽位、负责人和人工复核。</span></li>"
        for item in payload["monitoring_evidence_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 生产监控人工审批入口</title>
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
      header, section {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.9);
      }}
      header {{
        display: grid;
        gap: 18px;
        padding: 28px;
        box-shadow: 0 20px 54px rgba(20, 22, 19, 0.08);
      }}
      .label {{
        margin: 0;
        color: var(--accent);
        font-size: 13px;
        font-weight: 800;
      }}
      h1 {{
        max-width: 850px;
        margin: 0;
        color: var(--ink);
        font-size: clamp(34px, 5vw, 58px);
        line-height: 1.05;
        letter-spacing: 0;
      }}
      p {{ margin: 0; }}
      .lead {{
        max-width: 780px;
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
      .pill {{ padding: 16px; }}
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
        <p class="label">SAEE 生产监控人工审批入口</p>
        <h1>先确认谁看护线上状态，再谈正式商用。</h1>
        <p class="lead">{payload['plain_language_status_label']}</p>
        <div class="status-grid" aria-label="当前状态">
          <div class="pill"><span>当前状态</span><strong>等待人工填写</strong></div>
          <div class="pill"><span>需要填写</span><strong>{payload['required_metadata_field_count']} 项人员信息</strong></div>
          <div class="pill"><span>需要审查</span><strong>{payload['required_monitoring_evidence_item_count']} 项监控证据</strong></div>
        </div>
      </header>

      <section>
        <h2>人要先确认什么？</h2>
        <ol>
          <li>复制模板：<code>{payload['copy_template_command']}</code></li>
          <li>填写审核人、监控负责人、运维审核人和审核结论。</li>
          <li>逐项确认监控计划、指标覆盖、SLO 看板、日志保留和演练记录。</li>
          <li>运行验证：<code>{payload['validator_command']}</code></li>
        </ol>
      </section>

      <section>
        <h2>必须由人填写的字段</h2>
        <ul>{metadata_items}</ul>
      </section>

      <section>
        <h2>必须由人审查的监控证据</h2>
        <div class="cards">{evidence_items}</div>
      </section>

      <section class="danger">
        <h2>到这里必须停下</h2>
        <p>{payload['plain_language_stop_point']}</p>
      </section>

      <section>
        <h2>边界状态</h2>
        <div class="boundary-grid">
          <div><strong>production_monitoring_available:</strong> false</div>
          <div><strong>production_monitoring_approved:</strong> false</div>
          <div><strong>production_monitoring_deployed:</strong> false</div>
          <div><strong>dashboard_configured_by_codex:</strong> false</div>
          <div><strong>metrics_export_enabled_by_codex:</strong> false</div>
          <div><strong>log_retention_changed_by_codex:</strong> false</div>
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
    evidence_table = render_key_list(payload["monitoring_evidence_keys_to_review"])
    content = f"""# SAEE Production Monitoring Approval Input Prompt

production_monitoring_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_monitoring_evidence_item_count: {payload['required_monitoring_evidence_item_count']}
completed_monitoring_evidence_item_count: {payload['completed_monitoring_evidence_item_count']}
builder_ready: false
production_monitoring_available: false
production_monitoring_approved: false
production_monitoring_deployed: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`production_monitoring` approval input before validator use.

## Metadata Fields To Fill

{metadata}

## Monitoring Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, monitoring deployment,
dashboard configuration, metrics export, log-retention change, blocker closure,
launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve monitoring, fill evidence, deploy monitoring,
configure dashboards, enable metrics export, change log retention, touch live
operations paths, contact customers or vendors, execute the evidence builder,
close blockers, launch product, modify runtime/backend/kernel/API schema,
expose private core, or claim production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Production Monitoring Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_production_monitoring_input_prompt: true
recommend_for_monitoring_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_monitoring_deployment: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`production_monitoring` approval template. It makes the required metadata and
monitoring evidence keys explicit without approving or deploying monitoring.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_monitoring_available: false
- production_monitoring_approved: false
- production_monitoring_deployed: false
- dashboard_configured_by_codex: false
- metrics_export_enabled_by_codex: false
- log_retention_changed_by_codex: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_PRODUCTION_MONITORING_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "monitoring_evidence_keys="
        + ",".join(
            item["evidence_key"] for item in payload["monitoring_evidence_keys_to_review"]
        )
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(f"html_entrypoint={rel(OUTPUT_HTML)}")
    print("boundary=human_input_only_no_monitoring_approval_no_deployment_no_blocker_closure")


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
