#!/usr/bin/env python3
"""Build a human input prompt for customer-validation approval evidence.

This prompt narrows the `pilot_results` and `customer_validated` blockers to
the exact human-filled fields needed before the existing customer-validation
approval input validator and evidence builder can be considered. It does not
contact customers, run pilot sessions, infer missing results, collect customer
data, publish validation claims, close blockers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
TEMPLATE = EVIDENCE_DIR / "customer_validation_evidence_input.template.json"
VALIDATION_OUTPUT = EVIDENCE_DIR / "customer_validation_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "customer_validation_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "customer_validation_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "customer_validation_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "customer_validation_evidence_input.human_filled.local.json"

SESSION_TEXT_FIELDS = [
    "session_id",
    "session_date",
    "participant_role",
    "team_type",
    "current_evaluation_method",
]
SESSION_SCORE_FIELDS = [
    "understanding_score",
    "trust_score",
    "decision_influence_score",
    "repeat_usage_intent_score",
]
SESSION_BOOLEAN_FIELDS = [
    "willing_to_test_own_candidates",
]
SESSION_BOUNDARY_FALSE_KEYS = [
    "secrets_collected",
    "production_data_collected",
    "customer_data_uploaded",
    "private_core_disclosed",
    "production_ready_claim_made",
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
    "automated_customer_contact",
    "unsolicited_customer_contact",
    "customer_data_collected",
    "customer_data_processing_started",
    "customer_secrets_collected",
    "user_upload_enabled",
    "product_market_fit_claimed",
    "revenue_validated",
    "production_readiness_claimed",
    "public_validation_claim_published",
    "testimonial_published",
    "case_study_published",
    "paid_pilot_completed",
    "customer_contacted_by_codex",
    "codex_contacted_customer",
    "codex_executed_pilot",
    "codex_inferred_missing_results",
    "codex_collected_customer_data",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evidence_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT: FAIL evidence_review missing"
        )
    return list(review)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION_OUTPUT)
    keys = evidence_keys(template)
    sessions = template.get("sessions", [])
    if not isinstance(sessions, list):
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT: FAIL sessions missing"
        )

    payload: dict[str, Any] = {
        "customer_validation_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_customer_validation_approval_input_prompt",
        "prompt_scope": "local_human_customer_validation_input_prompt_only",
        "status": "hold_human_customer_validation_input_required",
        "target_blocker_ids": ["pilot_results", "customer_validated"],
        "category": "customer_validation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_customer_validation_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validator_output": rel(VALIDATION_OUTPUT),
        "source_customer_validation_approval_input_prompt_html": rel(OUTPUT_HTML),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "local_static_customer_validation_approval_input_prompt_html": True,
        "browser_readable_customer_validation_approval_input_prompt": True,
        "plain_language_customer_validation_approval_input_prompt_v0_2": True,
        "customer_validation_human_review_step_count": 5,
        "plain_language_status_label": "客户验证还没有完成，也不能对外声称已验证。",
        "plain_language_next_action": (
            "先由人类填写真实试用/访谈记录、评分、来源说明和边界确认，再运行本地验证。"
        ),
        "plain_language_stop_point": (
            "只到本地证据准备为止；没有单独批准，不联系客户、不执行试点、不收集客户数据、"
            "不发布客户验证结论。"
        ),
        "validator_status": validation.get("validation_status", "hold"),
        "builder_ready": False,
        "pilot_results_recorded": False,
        "customer_validation_approved": False,
        "required_review_key_count": len(keys),
        "completed_review_key_count": 0,
        "required_session_text_field_count": len(SESSION_TEXT_FIELDS),
        "required_session_score_field_count": len(SESSION_SCORE_FIELDS),
        "required_session_boundary_false_key_count": len(SESSION_BOUNDARY_FALSE_KEYS),
        "completed_session_count": 0,
        "review_keys_to_set_after_human_approval": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_must_provide_source_context": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "session_text_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in SESSION_TEXT_FIELDS
        ],
        "session_score_fields_to_fill": [
            {
                "field_name": field,
                "required_range": "1-5",
                "human_must_provide": True,
                "codex_may_fill": False,
            }
            for field in SESSION_SCORE_FIELDS
        ],
        "session_boolean_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in SESSION_BOOLEAN_FIELDS
        ],
        "session_boundary_flags_must_remain_false": SESSION_BOUNDARY_FALSE_KEYS,
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command_after_human_fill": (
            "python3 scripts/saee_customer_validation_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "builder_command_after_separate_approval": (
            "python3 scripts/saee_customer_validation_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make customer-validation-approval-input-prompt",
        "check_target": "make check-customer-validation-approval-input-prompt",
        "next_human_action": (
            "Copy the template, fill at least one real human-approved pilot session, "
            "set evidence_review keys only from real pilot/customer evidence, then run "
            "the validator. Stop before any customer-validation claim or evidence-builder "
            "execution unless a separate request explicitly approves it."
        ),
        "human_review_required": True,
        "separate_validator_run_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_validator": False,
        "ready_for_evidence_builder": False,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_prompt"] = 0
    return payload


def render_table(title: str, items: list[dict[str, Any]], columns: list[str]) -> str:
    rows = [f"## {title}", ""]
    rows.append("| " + " | ".join(columns) + " |")
    rows.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for item in items:
        rows.append("| " + " | ".join(str(item.get(col, "")) for col in columns) + " |")
    return "\n".join(rows)


def render_html(payload: dict[str, Any]) -> str:
    review_items = "\n".join(
        f"<li><code>{item['evidence_key']}</code><span>必须有人类确认的真实试用或访谈证据。</span></li>"
        for item in payload["review_keys_to_set_after_human_approval"][:8]
    )
    text_fields = "\n".join(
        f"<li><code>{item['field_name']}</code><span>由人类填写。</span></li>"
        for item in payload["session_text_fields_to_fill"]
    )
    score_fields = "\n".join(
        f"<li><code>{item['field_name']}</code><span>填写 1 到 5 分。</span></li>"
        for item in payload["session_score_fields_to_fill"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 客户验证人工审批入口</title>
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
      header {{
        padding: 28px;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
        box-shadow: 0 18px 44px rgba(17, 21, 18, 0.06);
      }}
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
      .lead {{
        max-width: 740px;
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
      section {{
        padding: 24px;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
      }}
      h2 {{
        margin: 0 0 14px;
        font-size: 22px;
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
      .status {{
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
      .mini-list {{
        display: grid;
        gap: 8px;
        padding: 0;
        list-style: none;
      }}
      .mini-list li {{
        display: grid;
        grid-template-columns: minmax(170px, 0.7fr) 1fr;
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
        <p class="eyebrow">SAEE 客户验证人工审批入口</p>
        <h1>先拿到真实试用反馈，再谈客户验证。</h1>
        <p class="lead">
          这个页面只告诉人类该填哪些本地证据。它不会联系客户，不会执行试点，
          也不会把 SAEE 标记为客户已验证。
        </p>
        <p class="note">{payload['plain_language_status_label']}</p>
      </header>

      <div class="grid">
        <section>
          <h2>人类要做的 5 步</h2>
          <ol>
            <li>复制本地模板。</li>
            <li>填写真实试用或访谈记录，不能让 Codex 猜。</li>
            <li>给理解度、信任度、决策影响、再次使用意愿打 1 到 5 分。</li>
            <li>确认没有收集生产数据、客户机密或私有核心信息。</li>
            <li>运行本地验证后停下，等待单独批准。</li>
          </ol>
        </section>

        <section>
          <h2>当前状态</h2>
          <ul class="status">
            <li><span>客户验证完成</span><code>false</code></li>
            <li><span>Codex 联系客户</span><code>false</code></li>
            <li><span>试点已执行</span><code>false</code></li>
            <li><span>客户数据已收集</span><code>false</code></li>
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
          <div class="command">{payload['validator_command_after_human_fill']}</div>
        </section>

        <section>
          <h2>不能越过的边界</h2>
          <ul>
            <li>不联系客户，不自动发邮件，不安排试点。</li>
            <li>不收集客户生产数据、密钥、隐私数据或私有核心信息。</li>
            <li>不发布客户案例、评价、验证结论或生产可用声明。</li>
            <li>不运行 evidence builder，除非之后有单独明确批准。</li>
          </ul>
        </section>
      </div>

      <section style="margin-top: 18px;">
        <h2>必须填写的客户验证字段</h2>
        <ul class="mini-list">
          {text_fields}
          {score_fields}
        </ul>
      </section>

      <section style="margin-top: 18px;">
        <h2>证据审查键示例</h2>
        <p class="lead" style="font-size: 15px; margin-bottom: 14px;">
          下面只展示前 8 个键。完整 25 个键在 Markdown 和 JSON 文件里。
        </p>
        <ul class="mini-list">{review_items}</ul>
      </section>
    </main>
  </body>
</html>
"""


def render_markdown(payload: dict[str, Any]) -> str:
    key_table = render_table(
        "Evidence Review Keys",
        payload["review_keys_to_set_after_human_approval"],
        [
            "evidence_key",
            "set_evidence_review_to_true_only_after_human_approval",
            "human_must_provide_source_context",
            "codex_may_fill",
        ],
    )
    text_table = render_table(
        "Session Text Fields",
        payload["session_text_fields_to_fill"],
        ["field_name", "human_must_provide", "codex_may_fill"],
    )
    score_table = render_table(
        "Session Score Fields",
        payload["session_score_fields_to_fill"],
        ["field_name", "required_range", "human_must_provide", "codex_may_fill"],
    )
    boundary_flags = "\n".join(
        f"- `{flag}` must remain `false`"
        for flag in payload["session_boundary_flags_must_remain_false"]
    )
    return f"""# SAEE Customer Validation Approval Input Prompt v0.1

customer_validation_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_ids: pilot_results,customer_validated
source_customer_validation_approval_input_prompt_html: {payload['source_customer_validation_approval_input_prompt_html']}
local_static_customer_validation_approval_input_prompt_html: true
browser_readable_customer_validation_approval_input_prompt: true
plain_language_customer_validation_approval_input_prompt_v0_2: true
customer_validation_human_review_step_count: {payload['customer_validation_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
required_review_key_count: {payload['required_review_key_count']}
completed_review_key_count: 0
required_session_text_field_count: {payload['required_session_text_field_count']}
required_session_score_field_count: {payload['required_session_score_field_count']}
required_session_boundary_false_key_count: {payload['required_session_boundary_false_key_count']}
completed_session_count: 0
builder_ready: false
pilot_results_recorded: false
customer_validation_approved: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Purpose

This prompt gives human reviewers the shortest safe path for filling the local
customer-validation input before any separate validator run or evidence-builder
request.

It is a prompt only. It does not contact customers, run pilot sessions, infer
missing results, collect customer data, publish validation claims, create
testimonials or case studies, close blockers, or claim production readiness.

## Human Procedure

1. Copy the template:

```bash
{payload['copy_template_command']}
```

2. Fill at least one real human-approved pilot session in
   `{rel(HUMAN_FILLED_INPUT)}`.
3. Set `evidence_review` keys to `true` only when backed by real human-reviewed
   pilot/customer evidence.
4. Keep every boundary flag false unless the review must stop.
5. Run the validator:

```bash
{payload['validator_command_after_human_fill']}
```

6. Run the evidence builder only after a separate explicit execution request:

```bash
{payload['builder_command_after_separate_approval']}
```

{key_table}

{text_table}

{score_table}

## Boundary Flags

{boundary_flags}

## Boundary

- builder_ready: false
- pilot_results_recorded: false
- customer_validation_approved: false
- customer_validation_claim_published: false
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
- customer_contacted: false
- automated_customer_contact: false
- customer_data_collected: false
- customer_secrets_collected: false
- public_validation_claim_published: false
- testimonial_published: false
- case_study_published: false
"""


def write_docs(payload: dict[str, Any]) -> None:
    write_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    TOP_DOC.write_text(
        f"""# SAEE Customer Validation Approval Input Prompt v0.1

customer_validation_approval_input_prompt_v0_1: true
prompt_scope: local_human_customer_validation_input_prompt_only
status: {payload['status']}
target_blocker_ids: pilot_results,customer_validated
source_customer_validation_approval_input_prompt_html: {payload['source_customer_validation_approval_input_prompt_html']}
local_static_customer_validation_approval_input_prompt_html: true
browser_readable_customer_validation_approval_input_prompt: true
plain_language_customer_validation_approval_input_prompt_v0_2: true
customer_validation_human_review_step_count: {payload['customer_validation_human_review_step_count']}
plain_language_status_label: {payload['plain_language_status_label']}
required_review_key_count: {payload['required_review_key_count']}
required_session_text_field_count: {payload['required_session_text_field_count']}
required_session_score_field_count: {payload['required_session_score_field_count']}
required_session_boundary_false_key_count: {payload['required_session_boundary_false_key_count']}
completed_session_count: 0
builder_ready: false
pilot_results_recorded: false
customer_validation_approved: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt tells a human reviewer exactly how to fill the local customer
validation input before running the existing approval input validator and
before requesting evidence-builder execution.

## Boundary

Prompt only. It does not contact customers, run pilot sessions, infer missing
results, collect customer data, publish validation claims, create testimonials
or case studies, close blockers, modify runtime/backend/kernel/API schema or
private core, launch product, or claim production readiness.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json`
- prompt JSON: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.local.json`
- prompt markdown: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.md`
- prompt HTML: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html`
- validator output: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.local.json`
- script: `scripts/saee_customer_validation_approval_input_prompt.py`
- smoke: `scripts/saee_customer_validation_approval_input_prompt_smoke.py`
""",
        encoding="utf-8",
    )
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        """# SAEE Customer Validation Approval Input Prompt Recommendation Gate

answer: conditional

recommend_for_human_customer_validation_input_prompt: true
recommend_for_customer_contact: false
recommend_for_pilot_execution: false
recommend_for_evidence_builder_execution: false
recommend_for_customer_validation_approval: false
recommend_for_customer_validation_claim: false
recommend_for_blocker_closure: false
recommend_for_product_market_fit_claim: false
recommend_for_testimonial_publication: false
recommend_for_case_study_publication: false
recommend_for_production_launch: false
recommend_for_production_readiness_claim: false

## Reason

The prompt is useful because it converts the customer-validation evidence
template into a human-fillable checklist. It is not customer outreach, pilot
execution, customer-validation approval, evidence-builder execution, or blocker
closure.

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
automated_customer_contact: false
customer_data_collected: false
customer_secrets_collected: false
codex_contacted_customer: false
codex_executed_pilot: false
codex_inferred_missing_results: false
codex_collected_customer_data: false
public_validation_claim_published: false
testimonial_published: false
case_study_published: false
blockers_closed_by_prompt: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_docs(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT: READY "
        f"status={payload['status']} "
        "builder_ready=false blockers_closed_by_prompt=0 production_ready=false "
        f"html_entrypoint={rel(OUTPUT_HTML)}"
    )


if __name__ == "__main__":
    main()
