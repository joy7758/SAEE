#!/usr/bin/env python3
"""Build a human input prompt for privacy/legal and DPA approval evidence.

This prompt narrows the `privacy_legal_review` and
`data_processing_agreement` blockers to the exact human-filled fields needed
before the existing privacy/legal + DPA evidence builder can be considered by
a later, separate execution request. It does not perform legal review, create
or approve a DPA, contact legal counsel, process customer data, close
blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
)
TEMPLATE = EVIDENCE_DIR / "privacy_legal_dpa_evidence_input.template.json"
BUILDER_OUTPUT = EVIDENCE_DIR / "privacy_legal_dpa_evidence_builder_output.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "privacy_legal_dpa_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "privacy_legal_dpa_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "privacy_legal_dpa_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = (
    EVIDENCE_DIR / "privacy_legal_dpa_evidence_input.human_filled.local.json"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "legal_owner",
    "privacy_owner",
    "dpa_owner",
    "review_record_reference",
    "decision_summary",
]

PRIVACY_LEGAL_KEYS = [
    "privacy_notice_approved",
    "terms_of_service_approved",
    "data_inventory_reviewed",
    "retention_policy_approved",
    "subprocessor_inventory_reviewed",
    "customer_data_processing_approved",
    "legal_reviewer_recorded",
]

DPA_KEYS = [
    "dpa_terms_approved",
    "controller_processor_roles_defined",
    "subprocessor_terms_approved",
    "breach_notice_terms_approved",
    "deletion_or_return_terms_approved",
    "customer_dpa_template_available",
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
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "codex_performed_legal_review",
    "codex_contacted_legal_counsel",
    "codex_created_dpa",
    "codex_approved_dpa",
    "codex_processed_customer_data",
    "codex_inferred_missing_evidence",
    "privacy_legal_review_completed_by_codex",
    "data_processing_agreement_completed_by_codex",
    "legal_review_claim_published",
    "dpa_availability_claim_published",
    "customer_data_processing_claim_published",
    "legal_review_execution_authorized",
    "legal_counsel_contacted",
    "customer_data_processed",
    "customer_data_processing_started",
    "dpa_sent_to_customer",
    "terms_published",
    "privacy_notice_published",
    "production_security_enabled",
    "vulnerability_management_operational",
    "security_vendor_contacted",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def review_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    keys = list(review)
    expected = set(PRIVACY_LEGAL_KEYS + DPA_KEYS)
    if set(keys) != expected:
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT: FAIL evidence_review keys changed"
        )
    return PRIVACY_LEGAL_KEYS + DPA_KEYS


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    builder = read_json(BUILDER_OUTPUT)
    keys = review_keys(template)
    artifacts = template.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT: FAIL review_artifacts missing"
        )

    payload: dict[str, Any] = {
        "privacy_legal_dpa_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_privacy_legal_dpa_approval_input_prompt",
        "prompt_scope": "local_human_privacy_legal_dpa_input_prompt_only",
        "status": "hold_human_privacy_legal_dpa_input_required",
        "target_blocker_ids": ["privacy_legal_review", "data_processing_agreement"],
        "category": "privacy_security_legal",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_privacy_legal_dpa_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_builder_output": rel(BUILDER_OUTPUT),
        "source_privacy_legal_dpa_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "local_static_privacy_legal_dpa_approval_input_prompt_html": True,
        "browser_readable_privacy_legal_dpa_approval_input_prompt": True,
        "plain_language_privacy_legal_dpa_approval_input_prompt_v0_2": True,
        "privacy_legal_dpa_human_review_step_count": 5,
        "plain_language_status_label": "隐私法律审查和 DPA 还没有完成，也不能声称可以正式处理客户数据。",
        "plain_language_next_action": (
            "先由人类填写法律、隐私、DPA 负责人、审查记录和 13 项证据，再另行请求证据构建。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不做法律审查、不创建或发送 DPA、"
            "不联系法律顾问、不处理客户数据、不关闭 blocker。"
        ),
        "builder_status": builder.get("status", "hold"),
        "builder_ready": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_available": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_privacy_legal_evidence_item_count": len(PRIVACY_LEGAL_KEYS),
        "required_dpa_evidence_item_count": len(DPA_KEYS),
        "required_total_evidence_item_count": len(keys),
        "completed_privacy_legal_evidence_item_count": 0,
        "completed_dpa_evidence_item_count": 0,
        "completed_total_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "privacy_legal_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "review_artifact_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in PRIVACY_LEGAL_KEYS
        ],
        "dpa_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "review_artifact_required": True,
                "owner_named_required": True,
                "reviewed_by_human_required": True,
                "codex_may_fill": False,
            }
            for key in DPA_KEYS
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "builder_command_after_separate_approval": (
            "python3 scripts/saee_privacy_legal_dpa_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make privacy-legal-dpa-approval-input-prompt",
        "check_target": "make check-privacy-legal-dpa-approval-input-prompt",
        "next_human_action": (
            "Copy the template, fill all metadata fields, approve each privacy/legal "
            "and DPA evidence key only with source-backed human review, add source "
            "notes and artifact references, then request separate evidence-builder "
            "execution. Stop before legal/DPA completion or production claims."
        ),
        "human_review_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_prompt"] = 0
    return payload


def render_key_table(title: str, items: list[dict[str, Any]]) -> str:
    rows = [
        f"## {title}",
        "",
        "| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        key = item["evidence_key"]
        rows.append(
            f"| `{key}` | set true only after human approval | required | required | required | required | false |"
        )
    return "\n".join(rows)


def render_metadata_list(fields: list[dict[str, Any]]) -> str:
    return "\n".join(f"- `{field['field_name']}`" for field in fields)


def render_html(payload: dict[str, Any]) -> str:
    metadata_items = "\n".join(
        f"<li><code>{item['field_name']}</code><span>必须由人类填写。</span></li>"
        for item in payload["metadata_fields_to_fill"]
    )
    privacy_items = "\n".join(
        f"<li><code>{item['evidence_key']}</code><span>需要来源说明、审查材料和负责人。</span></li>"
        for item in payload["privacy_legal_keys_to_review"]
    )
    dpa_items = "\n".join(
        f"<li><code>{item['evidence_key']}</code><span>需要来源说明、审查材料和负责人。</span></li>"
        for item in payload["dpa_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 隐私法律与 DPA 人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f9ff;
        --surface: #ffffff;
        --surface-soft: #eef2ff;
        --text: #202124;
        --muted: #667085;
        --line: #e3e8f2;
        --accent: #3157ff;
        --accent-deep: #101828;
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
        padding: 48px 0 64px;
      }}
      header, section {{
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
        box-shadow: 0 18px 44px rgba(16, 24, 40, 0.07);
      }}
      header {{ padding: 28px; }}
      section {{ padding: 24px; }}
      .eyebrow {{
        margin: 0 0 10px;
        color: var(--accent);
        font-size: 13px;
        font-weight: 800;
      }}
      h1 {{
        max-width: 820px;
        margin: 0;
        font-size: clamp(32px, 5vw, 58px);
        line-height: 1.08;
        letter-spacing: 0;
      }}
      h2 {{
        margin: 0 0 14px;
        font-size: 22px;
      }}
      .lead {{
        max-width: 820px;
        margin: 18px 0 0;
        color: var(--muted);
        font-size: 18px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(300px, 0.8fr);
        gap: 18px;
        margin-top: 18px;
      }}
      ol, ul {{
        margin: 0;
        padding-left: 20px;
      }}
      li + li {{ margin-top: 10px; }}
      code {{
        padding: 2px 6px;
        border-radius: 6px;
        background: var(--surface-soft);
        color: var(--accent-deep);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.92em;
      }}
      .command {{
        overflow-x: auto;
        padding: 14px;
        border-radius: 10px;
        background: #101828;
        color: #ffffff;
        font-size: 13px;
      }}
      .status, .mini-list {{
        display: grid;
        gap: 8px;
        padding: 0;
        list-style: none;
      }}
      .status li {{
        display: flex;
        justify-content: space-between;
        gap: 14px;
        padding: 10px 0;
        border-bottom: 1px solid var(--line);
      }}
      .status li:last-child {{ border-bottom: 0; }}
      .mini-list li {{
        display: grid;
        grid-template-columns: minmax(220px, 0.7fr) 1fr;
        gap: 12px;
        padding: 10px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #fbfcff;
      }}
      .note {{
        margin-top: 18px;
        padding: 16px;
        border-radius: 10px;
        background: #eef2ff;
        color: var(--accent-deep);
        font-weight: 700;
      }}
      @media (max-width: 760px) {{
        main {{ width: min(100% - 24px, 1080px); padding-top: 24px; }}
        header, section {{ padding: 18px; }}
        .grid {{ grid-template-columns: 1fr; }}
        .mini-list li {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="eyebrow">SAEE 隐私法律与 DPA 人工审批入口</p>
        <h1>先补齐隐私、法律和 DPA 证据，再谈正式商用。</h1>
        <p class="lead">
          这个页面只告诉人类该填哪些本地证据。它不会替你做法律审查，
          不会创建或发送 DPA，也不会处理任何客户数据。
        </p>
        <p class="note">{payload['plain_language_status_label']}</p>
      </header>

      <div class="grid">
        <section>
          <h2>人类要做的 5 步</h2>
          <ol>
            <li>复制本地模板。</li>
            <li>填写法律、隐私、DPA 负责人和审查记录。</li>
            <li>逐项确认 7 个隐私法律证据。</li>
            <li>逐项确认 6 个 DPA 证据。</li>
            <li>停在人工审批记录处，等待单独执行批准。</li>
          </ol>
        </section>

        <section>
          <h2>当前状态</h2>
          <ul class="status">
            <li><span>隐私法律审查完成</span><code>false</code></li>
            <li><span>DPA 可用</span><code>false</code></li>
            <li><span>Codex 执行法律审查</span><code>false</code></li>
            <li><span>客户数据已处理</span><code>false</code></li>
            <li><span>生产可用</span><code>false</code></li>
            <li><span>关闭 blocker</span><code>0</code></li>
          </ul>
        </section>
      </div>

      <div class="grid">
        <section>
          <h2>复制模板</h2>
          <div class="command">{payload['copy_template_command']}</div>
          <h2 style="margin-top: 22px;">单独批准后才可运行</h2>
          <div class="command">{payload['builder_command_after_separate_approval']}</div>
        </section>

        <section>
          <h2>不能越过的边界</h2>
          <ul>
            <li>不做法律审查或隐私合规判断。</li>
            <li>不创建、批准或发送 DPA。</li>
            <li>不联系法律顾问、客户或供应商。</li>
            <li>不处理客户数据，不发布条款或隐私声明。</li>
            <li>不声称已完成法律审查或生产可用。</li>
          </ul>
        </section>
      </div>

      <section style="margin-top: 18px;">
        <h2>必须填写的元数据</h2>
        <ul class="mini-list">{metadata_items}</ul>
      </section>

      <section style="margin-top: 18px;">
        <h2>必须审查的 7 个隐私法律证据项</h2>
        <ul class="mini-list">{privacy_items}</ul>
      </section>

      <section style="margin-top: 18px;">
        <h2>必须审查的 6 个 DPA 证据项</h2>
        <ul class="mini-list">{dpa_items}</ul>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    privacy_table = render_key_table(
        "Privacy Legal Evidence Keys",
        payload["privacy_legal_keys_to_review"],
    )
    dpa_table = render_key_table("DPA Evidence Keys", payload["dpa_keys_to_review"])
    content = f"""# SAEE Privacy Legal + DPA Approval Input Prompt

privacy_legal_dpa_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_ids: privacy_legal_review,data_processing_agreement
source_privacy_legal_dpa_approval_input_prompt_html: {payload['source_privacy_legal_dpa_approval_input_prompt_html']}
local_static_privacy_legal_dpa_approval_input_prompt_html: true
browser_readable_privacy_legal_dpa_approval_input_prompt: true
plain_language_privacy_legal_dpa_approval_input_prompt_v0_2: true
privacy_legal_dpa_human_review_step_count: {payload['privacy_legal_dpa_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_privacy_legal_evidence_item_count: {payload['required_privacy_legal_evidence_item_count']}
required_dpa_evidence_item_count: {payload['required_dpa_evidence_item_count']}
required_total_evidence_item_count: {payload['required_total_evidence_item_count']}
completed_total_evidence_item_count: {payload['completed_total_evidence_item_count']}
builder_ready: false
privacy_legal_review_completed: false
data_processing_agreement_available: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives human legal and privacy reviewers the shortest safe path for
filling the `privacy_legal_review` and `data_processing_agreement` input before
any separate evidence-builder request.

It is a prompt only. It does not perform legal review, create or approve a DPA,
contact legal counsel, send a DPA, process customer data, publish terms,
publish a privacy notice, close blockers, or claim production readiness.

## Metadata Fields To Fill

{metadata}

{privacy_table}

{dpa_table}

## Commands

Copy the template:

```bash
{payload['copy_template_command']}
```

Builder command, only after a separate explicit execution request:

```bash
{payload['builder_command_after_separate_approval']}
```

## Boundary

- builder_ready: false
- privacy_legal_review_completed: false
- data_processing_agreement_available: false
- legal_review_execution_authorized: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- legal_counsel_contacted: false
- customer_data_processed: false
- dpa_sent_to_customer: false
- codex_performed_legal_review: false
- codex_created_dpa: false
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(
        content.replace(
            "# SAEE Privacy Legal + DPA Approval Input Prompt",
            "# SAEE Privacy Legal + DPA Approval Input Prompt v0.1",
            1,
        ),
        encoding="utf-8",
    )
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        """# SAEE Privacy Legal + DPA Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_privacy_legal_dpa_input_prompt: true
recommend_for_legal_review_execution_by_codex: false
recommend_for_dpa_creation_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_customer_data_processing: false
recommend_for_production: false

## Reason

Potential buyers need privacy, legal, and DPA evidence before production
commercial use. A human-fillable input prompt is recommendable because it
clarifies the required evidence without doing legal work, contacting counsel,
processing customer data, creating a DPA, closing blockers, or claiming
production readiness.

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- legal_counsel_contacted: false
- customer_data_processed: false
- dpa_sent_to_customer: false
- codex_performed_legal_review: false
- codex_created_dpa: false
- blockers_closed_by_prompt: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    print("SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"required_metadata_field_count={payload['required_metadata_field_count']}")
    print(f"required_total_evidence_item_count={payload['required_total_evidence_item_count']}")
    print(f"copy_template_command={payload['copy_template_command']}")
    print(
        "builder_command_after_separate_approval="
        f"{payload['builder_command_after_separate_approval']}"
    )
    print(f"html_entrypoint={rel(OUTPUT_HTML)}")


if __name__ == "__main__":
    main()
