#!/usr/bin/env python3
"""Build a human input prompt for formal-security-review approval.

This prompt narrows the `formal_security_review` blocker to the exact
human-filled fields needed before the existing approval-input validator can
pass. It does not perform or approve a security review, contact reviewers or
vendors, run penetration tests, inspect private core, close blockers, launch
product, or claim production readiness.
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
TEMPLATE = EVIDENCE_DIR / "formal_security_review_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "formal_security_review_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = (
    EVIDENCE_DIR / "formal_security_review_evidence_input.human_filled.local.json"
)

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "security_review_owner",
    "report_reference",
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
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "formal_security_review_approved_by_codex",
    "formal_security_review_completed_by_codex",
    "formal_security_review_report_approved_by_codex",
    "dependency_review_completed_by_codex",
    "private_core_inspected_by_codex",
    "penetration_test_run_by_codex",
    "codex_performed_security_review",
    "codex_contacted_security_reviewer",
    "codex_contacted_vendor",
    "codex_ran_penetration_test",
    "codex_inspected_private_core",
    "codex_inferred_missing_evidence",
    "security_review_claim_published",
    "security_review_execution_authorized",
    "production_security_claim_published",
    "security_vendor_contacted",
    "legal_counsel_contacted",
    "customer_data_processed",
    "customer_data_processing_started",
    "dpa_sent_to_customer",
    "terms_published",
    "privacy_notice_published",
    "production_security_enabled",
    "vulnerability_management_operational",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def review_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    return sorted(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = review_keys(template)
    artifacts = template.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        raise SystemExit(
            "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT: FAIL review_artifacts missing"
        )

    payload: dict[str, Any] = {
        "formal_security_review_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_formal_security_review_approval_input_prompt",
        "prompt_scope": "local_human_formal_security_review_input_prompt_only",
        "status": "hold_human_formal_security_review_input_required",
        "target_blocker_id": "formal_security_review",
        "category": "privacy_security",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_formal_security_review_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "source_formal_security_review_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "local_static_formal_security_review_approval_input_prompt_html": True,
        "browser_readable_formal_security_review_approval_input_prompt": True,
        "plain_language_formal_security_review_approval_input_prompt_v0_2": True,
        "formal_security_review_human_review_step_count": 5,
        "plain_language_status_label": "正式安全审查还没有完成，也不能声称安全已审。",
        "plain_language_next_action": (
            "先由人类填写审查负责人、报告引用、审查结论和 7 项安全审查证据，再运行本地验证。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不联系审查方、不跑渗透测试、"
            "不查看私有核心、不关闭 blocker。"
        ),
        "validation_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "formal_security_review_available": False,
        "formal_security_review_approved": False,
        "formal_security_review_completed": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_formal_security_review_evidence_item_count": len(keys),
        "completed_formal_security_review_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "formal_security_review_keys_to_review": [
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
        "validator_command": (
            "python3 scripts/saee_formal_security_review_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make formal-security-review-approval-input-prompt",
        "check_target": "make check-formal-security-review-approval-input-prompt",
        "next_human_action": (
            "Copy the template, fill all metadata fields, set each formal security "
            "review key only after human approval, add source notes and review "
            "artifact references, then run the validator. Stop before evidence "
            "builder execution or security-review claims."
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
        "| Evidence Key | Review Flag | Source Note | Artifact | Owner Named | Reviewed By Human | Codex May Fill |",
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
        f"<li><code>{item['field_name']}</code><span>必须由人类填写。</span></li>"
        for item in payload["metadata_fields_to_fill"]
    )
    review_items = "\n".join(
        f"<li><code>{item['evidence_key']}</code><span>需要审查记录、来源说明和负责人。</span></li>"
        for item in payload["formal_security_review_keys_to_review"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 正式安全审查人工审批入口</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f7f2;
        --surface: #ffffff;
        --surface-soft: #eef1eb;
        --text: #1f211d;
        --muted: #66706a;
        --line: #dfe3dc;
        --accent: #10a37f;
        --accent-deep: #10221d;
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
        box-shadow: 0 18px 44px rgba(17, 21, 18, 0.06);
      }}
      header {{ padding: 28px; }}
      section {{ padding: 24px; }}
      .eyebrow {{
        margin: 0 0 10px;
        color: #0a7f64;
        font-size: 13px;
        font-weight: 800;
      }}
      h1 {{
        max-width: 760px;
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
        max-width: 760px;
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
        background: #111512;
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
        grid-template-columns: minmax(210px, 0.7fr) 1fr;
        gap: 12px;
        padding: 10px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #fbfcf9;
      }}
      .note {{
        margin-top: 18px;
        padding: 16px;
        border-radius: 10px;
        background: #e5f4ef;
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
        <p class="eyebrow">SAEE 正式安全审查人工审批入口</p>
        <h1>先完成安全审查，再谈正式商用。</h1>
        <p class="lead">
          这个页面只告诉人类该填哪些本地证据。它不会替你做安全审查，
          不会跑渗透测试，也不会查看或公开私有核心。
        </p>
        <p class="note">{payload['plain_language_status_label']}</p>
      </header>

      <div class="grid">
        <section>
          <h2>人类要做的 5 步</h2>
          <ol>
            <li>复制本地模板。</li>
            <li>填写审查负责人、日期、报告引用和结论摘要。</li>
            <li>逐项确认 7 个安全审查证据键。</li>
            <li>每项都要有来源说明、审查材料和负责人。</li>
            <li>运行本地验证后停下，等待单独批准。</li>
          </ol>
        </section>

        <section>
          <h2>当前状态</h2>
          <ul class="status">
            <li><span>正式安全审查完成</span><code>false</code></li>
            <li><span>Codex 执行安全审查</span><code>false</code></li>
            <li><span>渗透测试已运行</span><code>false</code></li>
            <li><span>私有核心已查看</span><code>false</code></li>
            <li><span>生产可用</span><code>false</code></li>
            <li><span>关闭 blocker</span><code>0</code></li>
          </ul>
        </section>
      </div>

      <div class="grid">
        <section>
          <h2>复制模板</h2>
          <div class="command">{payload['copy_template_command']}</div>
          <h2 style="margin-top: 22px;">人工填写后验证</h2>
          <div class="command">{payload['validator_command']}</div>
        </section>

        <section>
          <h2>不能越过的边界</h2>
          <ul>
            <li>不联系安全审查方或供应商。</li>
            <li>不运行扫描、渗透测试或外部安全服务。</li>
            <li>不检查、不公开、不复制私有核心。</li>
            <li>不声称安全审查完成或生产可用。</li>
          </ul>
        </section>
      </div>

      <section style="margin-top: 18px;">
        <h2>必须填写的元数据</h2>
        <ul class="mini-list">{metadata_items}</ul>
      </section>

      <section style="margin-top: 18px;">
        <h2>必须审查的 7 个证据项</h2>
        <ul class="mini-list">{review_items}</ul>
      </section>
    </main>
  </body>
</html>
"""


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_list(payload["formal_security_review_keys_to_review"])
    content = f"""# SAEE Formal Security Review Approval Input Prompt

formal_security_review_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_id: {payload['target_blocker_id']}
source_formal_security_review_approval_input_prompt_html: {payload['source_formal_security_review_approval_input_prompt_html']}
local_static_formal_security_review_approval_input_prompt_html: true
browser_readable_formal_security_review_approval_input_prompt: true
plain_language_formal_security_review_approval_input_prompt_v0_2: true
formal_security_review_human_review_step_count: {payload['formal_security_review_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_formal_security_review_evidence_item_count: {payload['required_formal_security_review_evidence_item_count']}
completed_formal_security_review_evidence_item_count: {payload['completed_formal_security_review_evidence_item_count']}
builder_ready: false
formal_security_review_available: false
formal_security_review_approved: false
formal_security_review_completed: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
`formal_security_review` approval input before validator use.

## Metadata Fields To Fill

{metadata}

## Formal Security Review Keys To Review

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

After validation, stop. Evidence-builder execution, security-review completion
claims, report approval, penetration testing, reviewer/vendor contact, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not perform or approve a security review, fill evidence,
contact reviewers or vendors, run penetration tests, inspect private core,
execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, process customer data,
or claim production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Formal Security Review Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_formal_security_review_input_prompt: true
recommend_for_security_review_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_security_review_execution: false
recommend_for_private_core_inspection: false
recommend_for_penetration_test: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the
`formal_security_review` approval template. It makes the required metadata and
review evidence keys explicit without performing or approving a security review.

## Boundary

- target_blocker_id: {payload['target_blocker_id']}
- builder_ready: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- formal_security_review_available: false
- formal_security_review_approved: false
- formal_security_review_completed: false
- private_core_inspected_by_codex: false
- penetration_test_run_by_codex: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print(f"target_blocker_id={payload['target_blocker_id']}")
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "formal_security_review_keys="
        + ",".join(
            item["evidence_key"] for item in payload["formal_security_review_keys_to_review"]
        )
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(f"html_entrypoint={rel(OUTPUT_HTML)}")
    print("boundary=human_input_only_no_security_review_no_private_core_inspection_no_blocker_closure")


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
