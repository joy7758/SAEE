#!/usr/bin/env python3
"""Build a human input prompt for production restore-policy approval.

This prompt narrows the `production_restore_policy` blocker to the exact
human-filled fields needed before the existing approval-input validator can
pass. It does not approve policy, fill evidence, run restore, touch live data
paths, contact customers/vendors, close blockers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
TEMPLATE = EVIDENCE_DIR / "production_restore_policy_approval_input.template.json"
DRAFT_JSON = EVIDENCE_DIR / "production_restore_policy_draft.local.json"
VALIDATION = EVIDENCE_DIR / "production_restore_policy_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = (
    EVIDENCE_DIR / "production_restore_policy_approval_input.human_filled.local.json"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "data_operations_owner",
    "security_owner",
    "privacy_legal_owner",
    "incident_response_owner",
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
    "policy_approved_by_codex",
    "restore_policy_published_by_codex",
    "live_restore_authorized_by_codex",
    "live_restore_performed",
    "restore_to_live_path_enabled",
    "production_data_path_modified",
    "credentials_restored",
    "private_core_restored",
    "customer_notification_sent_by_codex",
    "codex_contacted_customer",
    "codex_contacted_vendor",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def policy_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("policy_evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit("SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT: FAIL policy_evidence_review missing")
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    draft = read_json(DRAFT_JSON)
    validation = read_json(VALIDATION)
    keys = policy_keys(template)
    slots = template.get("policy_evidence_slots", [])
    if not isinstance(slots, list):
        raise SystemExit("SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT: FAIL policy_evidence_slots missing")

    payload: dict[str, Any] = {
        "production_restore_policy_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_production_restore_policy_approval_input_prompt",
        "prompt_scope": "local_human_restore_policy_approval_input_prompt_only",
        "status": "hold_human_restore_policy_approval_input_required",
        "target_blocker_id": "production_restore_policy",
        "category": "data_ops",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_production_restore_policy_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_policy_draft": rel(DRAFT_JSON),
        "source_validation": rel(VALIDATION),
        "source_production_restore_policy_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "local_static_production_restore_policy_approval_input_prompt_html": True,
        "browser_readable_production_restore_policy_approval_input_prompt": True,
        "plain_language_production_restore_policy_approval_input_prompt_v0_2": True,
        "production_restore_policy_human_review_step_count": 4,
        "plain_language_status_label": (
            "生产恢复策略还没有人工批准，也没有做正式恢复演练，不能对外说已经具备生产恢复能力。"
        ),
        "plain_language_next_action": (
            "请人类负责人确认恢复负责人、恢复范围、备份保留策略、租户恢复边界、"
            "凭据排除规则和事故交接方式；确认前不要运行恢复、导入证据或关闭 blocker。"
        ),
        "plain_language_stop_point": (
            "填完并验证输入后停止；运行 evidence builder、执行恢复、触碰实时数据路径、"
            "联系客户或关闭 blocker 都需要单独批准。"
        ),
        "validation_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "policy_draft_available": draft.get("draft_policy_available") is True,
        "production_restore_policy_available": False,
        "production_restore_policy_approved": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_policy_evidence_item_count": len(keys),
        "completed_policy_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "policy_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_policy_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "policy_evidence_slot_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_production_restore_policy_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make production-restore-policy-approval-input-prompt",
        "check_target": "make check-production-restore-policy-approval-input-prompt",
        "next_human_action": (
            "Copy the template, fill all metadata fields, set each policy evidence "
            "review key only after human approval, add source notes and evidence "
            "slot references, then run the validator. Stop before evidence builder execution."
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
        "| Evidence Key | Review Flag | Source Note | Evidence Slot | Codex May Fill |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in keys:
        key = item["evidence_key"]
        rows.append(
            f"| `{key}` | set true only after human approval | required | required | false |"
        )
    return "\n".join(rows)


def render_metadata_list(fields: list[dict[str, Any]]) -> str:
    return "\n".join(f"- `{field['field_name']}`" for field in fields)


def render_html(payload: dict[str, Any]) -> str:
    metadata_items = "\n".join(
        f"<li><code>{escape(field['field_name'])}</code></li>"
        for field in payload["metadata_fields_to_fill"]
    )
    evidence_items = "\n".join(
        "<li>"
        f"<code>{escape(item['evidence_key'])}</code>"
        "<span>需要人工确认、来源说明和证据槽位。</span>"
        "</li>"
        for item in payload["policy_evidence_keys_to_review"]
    )
    boundary_items = "\n".join(
        f"<li><code>{escape(flag)}</code>: false</li>"
        for flag in [
            "production_restore_policy_available",
            "production_restore_policy_approved",
            "live_restore_authorized_by_codex",
            "live_restore_performed",
            "restore_to_live_path_enabled",
            "production_data_path_modified",
            "credentials_restored",
            "customer_contacted",
            "production_ready",
            "private_core_exposed",
            "blockers_closed_by_prompt",
        ]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 生产恢复策略人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f6f4ef;
        --surface: #ffffff;
        --ink: #111111;
        --muted: #6a6d70;
        --line: #dedbd2;
        --accent: #2f6f66;
        --soft: #eef4f1;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 100%);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.6;
      }}
      main {{
        width: min(960px, calc(100% - 32px));
        margin: 0 auto;
        padding: 48px 0 64px;
      }}
      header, section {{
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: clamp(20px, 4vw, 34px);
        margin-bottom: 18px;
      }}
      .kicker {{
        margin: 0 0 10px;
        color: var(--accent);
        font-size: 13px;
        font-weight: 800;
      }}
      h1, h2 {{ margin: 0; line-height: 1.15; }}
      h1 {{ font-size: clamp(34px, 6vw, 58px); letter-spacing: 0; }}
      h2 {{ font-size: clamp(22px, 3vw, 30px); }}
      p {{ color: var(--muted); margin: 14px 0 0; }}
      ul, ol {{ padding-left: 20px; margin: 16px 0 0; }}
      li {{ margin: 8px 0; }}
      code {{
        background: var(--soft);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 2px 6px;
      }}
      .status {{
        display: inline-flex;
        margin-top: 18px;
        padding: 8px 12px;
        border-radius: 999px;
        background: var(--soft);
        color: var(--accent);
        font-weight: 800;
      }}
      .stop {{
        border-color: #d9c6aa;
        background: #fbf4e8;
      }}
      @media (max-width: 640px) {{
        main {{ width: min(100% - 24px, 960px); padding-top: 24px; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="kicker">SAEE 人工审批入口</p>
        <h1>先确认怎么恢复，再谈正式商用。</h1>
        <p>{escape(payload['plain_language_status_label'])}</p>
        <span class="status">等待人工填写</span>
      </header>
      <section>
        <h2>必须由人填写的字段</h2>
        <p>这些字段需要负责人真实确认，Codex 不能代填。</p>
        <ul>{metadata_items}</ul>
      </section>
      <section>
        <h2>必须由人审查的恢复策略证据</h2>
        <p>每一项都需要人工批准后，才能在输入文件里标记为通过。</p>
        <ul>{evidence_items}</ul>
      </section>
      <section>
        <h2>人工操作顺序</h2>
        <ol>
          <li>复制模板到 human-filled 输入文件。</li>
          <li>由负责人填写元数据和审批结论。</li>
          <li>逐项补充来源说明和证据槽位。</li>
          <li>只运行 validator 检查输入格式，然后停止。</li>
        </ol>
        <p>{escape(payload['plain_language_next_action'])}</p>
      </section>
      <section class="stop">
        <h2>到这里必须停下</h2>
        <p>{escape(payload['plain_language_stop_point'])}</p>
        <ul>{boundary_items}</ul>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["policy_evidence_keys_to_review"])
    content = f"""# SAEE Production Restore Policy Approval Input Prompt

production_restore_policy_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_policy_evidence_item_count: {payload['required_policy_evidence_item_count']}
completed_policy_evidence_item_count: {payload['completed_policy_evidence_item_count']}
builder_ready: false
production_restore_policy_available: false
production_restore_policy_approved: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`production_restore_policy` approval input before validator use.

## Metadata Fields To Fill

{metadata}

## Policy Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, restore-policy publication,
live restore, blocker closure, launch, and production-readiness claims require
separate approvals.

## Boundary

This prompt does not approve policy, fill evidence, run restore, touch live data
paths, contact customers or vendors, execute the evidence builder, close
blockers, launch product, modify runtime/backend/kernel/API schema, expose
private core, or claim production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Production Restore Policy Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_restore_policy_input_prompt: true
recommend_for_policy_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_restore_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`production_restore_policy` approval template. It makes the required metadata
and policy evidence keys explicit without approving policy or executing restore.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_restore_policy_available: false
- production_restore_policy_approved: false
- live_restore_performed: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print("metadata_fields=" + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"]))
    print(
        "policy_evidence_keys="
        + ",".join(item["evidence_key"] for item in payload["policy_evidence_keys_to_review"])
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(f"html_entrypoint={payload['source_production_restore_policy_approval_input_prompt_html']}")
    print("boundary=human_input_only_no_policy_approval_no_restore_no_blocker_closure")


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
