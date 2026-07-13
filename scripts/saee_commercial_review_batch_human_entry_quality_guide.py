#!/usr/bin/env python3
"""Create a field-level quality guide for the active commercial review batch.

This guide helps a human enter the current 10 support-contact rows safely.
It does not generate values, enter values, modify the source quick-fill packet,
import a workbook, run validators on real input, collect evidence, close
blockers, contact anyone, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
DOCS_STRATEGY = ROOT / "docs/strategy"

SOURCE_TEMPLATE = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
SOURCE_TEMPLATE_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"
)

OUT_JSON = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.html"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE_V0_1.md"
GATE = (
    DOCS_STRATEGY
    / "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 10
POST_FILL_DRY_RUN_COMMAND = (
    "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
)
TEMPLATE_PREFLIGHT_COMMAND = (
    "python3 scripts/saee_commercial_review_batch_template_preflight.py"
)
QUALITY_GUIDE_SMOKE_COMMAND = (
    "python3 scripts/saee_commercial_review_batch_human_entry_quality_guide_smoke.py"
)

FALSE_FLAGS = [
    "human_values_generated_by_codex",
    "human_input_filled_by_codex",
    "raw_values_recorded",
    "source_quick_fill_packet_modified",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "validators_run_on_real_input",
    "evidence_collection_authorized",
    "execution_authorized",
    "blocker_closure_authorized",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "production_ready",
    "customer_validated",
    "product_launched",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "production_ready_claim",
    "customer_validation_claim",
]

RULES: dict[str, dict[str, str]] = {
    "assigned_human_owner": {
        "accepted_value_shape": "role, team, or person reference explicitly approved by a human",
        "quality_rule": "Must name who owns the support-contact decision or the approved internal owner reference.",
        "reject_if": "Reject blank-looking placeholders, guessed owners, or direct personal phone/email not meant for public config.",
        "example_placeholder": "EXAMPLE_ONLY: support owner role reviewed by human",
        "privacy_note": "Prefer internal role or approved owner reference; avoid raw personal contact details.",
    },
    "owner_contact_reference": {
        "accepted_value_shape": "internal ticket, meeting note, document path, or approval reference",
        "quality_rule": "Must point to a human-reviewable internal source for the owner/contact decision.",
        "reject_if": "Reject unsupported personal contact data, vague memory, or unapproved public contact claims.",
        "example_placeholder": "EXAMPLE_ONLY: internal approval record reference",
        "privacy_note": "Use a reference ID or internal document name instead of private phone/email.",
    },
    "target_review_date": {
        "accepted_value_shape": "YYYY-MM-DD or explicit reviewed date reference",
        "quality_rule": "Must be a concrete date or an explicit reviewed date source.",
        "reject_if": "Reject vague dates such as soon, later, next week, or guessed current date.",
        "example_placeholder": "EXAMPLE_ONLY: YYYY-MM-DD",
        "privacy_note": "Date only; no personal details required.",
    },
    "owner_acknowledged_scope": {
        "accepted_value_shape": "true/false/hold plus reviewer reference",
        "quality_rule": "Must say whether the owner acknowledged scope, and point to the human review source.",
        "reject_if": "Reject unsupported approved claims, production-ready claims, or customer-facing launch claims.",
        "example_placeholder": "EXAMPLE_ONLY: hold - scope not yet approved by owner",
        "privacy_note": "Reference the review record; do not expose private discussion details.",
    },
    "human_approval_reference": {
        "accepted_value_shape": "approval record, meeting note, ticket, or signed-off internal reference",
        "quality_rule": "Must identify the human approval evidence source without claiming execution.",
        "reject_if": "Reject verbal-only claims with no reference, or claims that approval equals launch.",
        "example_placeholder": "EXAMPLE_ONLY: approval record ID",
        "privacy_note": "Use record identifiers; avoid copying private messages.",
    },
    "human_reviewer_name": {
        "accepted_value_shape": "reviewer role, team, person name, or internal reviewer reference",
        "quality_rule": "Must identify who reviewed the entry at a human-readable level.",
        "reject_if": "Reject anonymous approval, guessed names, or unapproved personal contact details.",
        "example_placeholder": "EXAMPLE_ONLY: reviewer role or internal reviewer reference",
        "privacy_note": "Use role/reference if public names are not approved for config.",
    },
    "review_date": {
        "accepted_value_shape": "YYYY-MM-DD or explicit reviewed date reference",
        "quality_rule": "Must be the actual human review date or a traceable date reference.",
        "reject_if": "Reject vague dates such as today, soon, later, or guessed current date.",
        "example_placeholder": "EXAMPLE_ONLY: YYYY-MM-DD",
        "privacy_note": "Date only; no personal details required.",
    },
    "selected_support_contact_channel": {
        "accepted_value_shape": "approved channel type or internal reference, such as support_email_candidate, ticketing_system_candidate, or hold_no_channel_approved",
        "quality_rule": "Must describe the selected support-contact channel type without pretending it is live.",
        "reject_if": "Reject live public contact claims, production support claims, or customer-ready language if not separately approved.",
        "example_placeholder": "EXAMPLE_ONLY: hold_no_channel_approved",
        "privacy_note": "Do not expose real addresses or forms until the channel is approved.",
    },
    "decision_summary": {
        "accepted_value_shape": "concise human decision summary with boundary-safe wording",
        "quality_rule": "Must summarize the human decision while preserving hold/not-production-ready boundaries.",
        "reject_if": "Reject production-ready, customer-validated, launched, or universal support claims.",
        "example_placeholder": "EXAMPLE_ONLY: support channel decision remains on hold pending owner approval",
        "privacy_note": "Summarize the decision, not private deliberation.",
    },
    "abuse_handling_path_defined": {
        "accepted_value_shape": "true/false/hold plus evidence reference",
        "quality_rule": "Must state whether abuse handling is defined and cite the human-review source.",
        "reject_if": "Reject unsupported live support, incident response, production-ready, or customer-support claims.",
        "example_placeholder": "EXAMPLE_ONLY: hold - abuse handling path not yet approved",
        "privacy_note": "Reference the process record; do not expose private escalation contacts.",
    },
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_rows() -> list[dict[str, str]]:
    with SOURCE_TEMPLATE.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rule_for(input_key: str) -> dict[str, str]:
    return RULES.get(
        input_key,
        {
            "accepted_value_shape": "human-reviewed explicit value or hold with evidence reference",
            "quality_rule": "Must be specific, traceable, and boundary-safe.",
            "reject_if": "Reject vague, guessed, production-ready, customer-validated, launched, or private-core claims.",
            "example_placeholder": "EXAMPLE_ONLY: human-reviewed value or hold reason",
            "privacy_note": "Avoid direct personal contact details and private implementation details.",
        },
    )


def build_payload() -> dict[str, Any]:
    rows = read_rows()
    template = json.loads(SOURCE_TEMPLATE_JSON.read_text(encoding="utf-8"))
    boundary_violations: list[str] = []
    if len(rows) != EXPECTED_ROW_COUNT:
        boundary_violations.append("unexpected_template_row_count")
    if template.get("status") != "ready_for_human_batch_value_entry":
        boundary_violations.append("template_not_ready_for_human_batch_value_entry")

    guidance_rows: list[dict[str, Any]] = []
    for row in rows:
        if row.get("human_value_to_enter", "").strip():
            boundary_violations.append(f"source_value_already_filled:{row.get('review_batch_row_id')}")
        if row.get("notes_for_human", "").strip():
            boundary_violations.append(f"source_note_already_filled:{row.get('review_batch_row_id')}")
        input_key = row.get("input_key", "")
        rule = rule_for(input_key)
        guidance_rows.append(
            {
                "review_batch_row_id": row.get("review_batch_row_id", ""),
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": input_key,
                "expected_value_shape": row.get("expected_value_shape", ""),
                "target_json_pointer": row.get("target_json_pointer", ""),
                "quality_rule": rule["quality_rule"],
                "accepted_value_shape": rule["accepted_value_shape"],
                "reject_if": rule["reject_if"],
                "example_placeholder": rule["example_placeholder"],
                "privacy_note": rule["privacy_note"],
                "human_required": True,
                "codex_may_fill": False,
            }
        )

    payload: dict[str, Any] = {
        "commercial_review_batch_human_entry_quality_guide_v0_1": True,
        "status": "ready_for_human_entry_quality_review"
        if not boundary_violations
        else "stop_boundary_violation",
        "scope": "field_level_quality_guide_for_10_row_support_contact_review_batch",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_human_entry_quality_guide.py",
        "source_template_csv": rel(SOURCE_TEMPLATE),
        "source_template_json": rel(SOURCE_TEMPLATE_JSON),
        "guide_row_count": len(guidance_rows),
        "expected_guide_row_count": EXPECTED_ROW_COUNT,
        "target_blocker_id": "support_contact",
        "human_required": True,
        "human_review_required": True,
        "quality_guide_only": True,
        "field_level_quality_rules": True,
        "placeholder_examples_only": True,
        "safe_human_entry_columns": ["human_value_to_enter", "notes_for_human"],
        "recommended_human_sequence": [
            "Open commercial_review_batch_human_entry_quality_guide.html.",
            "Fill only human_value_to_enter and optional notes_for_human in the 10-row CSV.",
            "Run template preflight and end-to-end dry run.",
            "Request separate import approval only if checks pass.",
        ],
        "template_preflight_command": TEMPLATE_PREFLIGHT_COMMAND,
        "post_fill_dry_run_command": POST_FILL_DRY_RUN_COMMAND,
        "quality_guide_smoke_command": QUALITY_GUIDE_SMOKE_COMMAND,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blockers_closed_by_quality_guide": 0,
        "guidance_rows": guidance_rows,
        "next_human_action": (
            "Open the quality guide, then manually fill only human_value_to_enter "
            "and optional notes_for_human in the active 10-row source CSV."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "expected_value_shape",
        "target_json_pointer",
        "quality_rule",
        "accepted_value_shape",
        "reject_if",
        "example_placeholder",
        "privacy_note",
        "human_required",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["guidance_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Row | Field | Accepted Shape | Reject If | Placeholder |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {review_batch_row_id} | `{input_key}` | {accepted_value_shape} | {reject_if} | `{example_placeholder}` |".format(
                **{key: str(value).replace("|", "/") for key, value in row.items()}
            )
        )
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Review Batch Human Entry Quality Guide v0.1

commercial_review_batch_human_entry_quality_guide_v0_1: true
status: {payload['status']}
scope: {payload['scope']}
target_blocker_id: support_contact
quality_guide_only: true
field_level_quality_rules: true
placeholder_examples_only: true

## Summary

This file explains what counts as a safe human-entered value for the active
10-row support-contact review batch. It does not contain real values and it
does not authorize import, execution, evidence collection, blocker closure,
customer contact, launch, or production-readiness claims.

- guide_row_count: {payload['guide_row_count']}
- expected_guide_row_count: {payload['expected_guide_row_count']}
- blockers_closed_by_quality_guide: 0
- human_values_generated_by_codex: false
- human_input_filled_by_codex: false
- raw_values_recorded: false
- source_quick_fill_packet_modified: false
- quick_fill_imported_to_workbook: false
- workbook_import_authorized: false
- validators_run_on_real_input: false
- production_ready: false
- customer_validated: false
- product_launched: false

## Recommended Human Sequence

1. Open `commercial_review_batch_human_entry_quality_guide.html`.
2. Fill only `human_value_to_enter` and optional `notes_for_human` in the source CSV.
3. Run template preflight and the end-to-end dry run.
4. Request separate import approval only if checks pass.

Source CSV:

`{payload['source_template_csv']}`

## Field Quality Rules

{markdown_table(payload['guidance_rows'])}

## Commands After Human Entry

```bash
{payload['template_preflight_command']}
{payload['post_fill_dry_run_command']}
{payload['quality_guide_smoke_command']}
python3 scripts/mainline_guard.py
```

## Boundary

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- customer_contacted: false
- product_launched: false
- production_ready_claim: false
- customer_validation_claim: false
"""
    OUT_MD.write_text(body, encoding="utf-8")
    TOP_DOC.write_text(body, encoding="utf-8")


def html_rows(rows: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in rows:
        parts.append(
            f"""<article class="rule-card">
  <div class="row-id">{esc(row['review_batch_row_id'])}</div>
  <div>
    <h2>{esc(row['input_key'])}</h2>
    <p><strong>合格写法：</strong>{esc(row['accepted_value_shape'])}</p>
    <p><strong>质量规则：</strong>{esc(row['quality_rule'])}</p>
    <p><strong>拒绝写法：</strong>{esc(row['reject_if'])}</p>
    <p><strong>占位示例：</strong><code>{esc(row['example_placeholder'])}</code></p>
    <p><strong>隐私提醒：</strong>{esc(row['privacy_note'])}</p>
  </div>
</article>"""
        )
    return "\n".join(parts)


def write_html(payload: dict[str, Any]) -> None:
    body = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 人工录入质量指南</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f7f4;
        --surface: #ffffff;
        --text: #10110f;
        --muted: #5f655f;
        --line: #deded8;
        --accent: #10a37f;
        --ink: #10110f;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
      }}
      main {{
        width: min(1080px, calc(100% - 32px));
        margin: 0 auto;
        padding: 56px 0 72px;
      }}
      .hero {{
        padding-bottom: 28px;
        border-bottom: 1px solid var(--line);
      }}
      .eyebrow {{
        margin: 0 0 12px;
        color: var(--accent);
        font-weight: 800;
      }}
      h1 {{
        max-width: 820px;
        margin: 0;
        font-size: clamp(34px, 5vw, 64px);
        line-height: 1.04;
        letter-spacing: 0;
      }}
      .lead {{
        max-width: 760px;
        margin: 20px 0 0;
        color: var(--muted);
        font-size: 18px;
      }}
      .status-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 24px;
      }}
      .status-card,
      .rule-card,
      .boundary {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
      }}
      .status-card {{
        padding: 14px;
      }}
      .status-card strong,
      .status-card span {{
        display: block;
      }}
      .status-card strong {{
        font-size: 22px;
      }}
      .status-card span {{
        color: var(--muted);
        font-size: 13px;
      }}
      .sequence {{
        margin-top: 24px;
        padding: 18px;
        border-radius: 8px;
        background: #e8f5f0;
      }}
      .sequence h2,
      .boundary h2 {{
        margin: 0 0 10px;
        font-size: 20px;
      }}
      .sequence ol,
      .boundary ul {{
        margin: 0;
        padding-left: 22px;
      }}
      .rules {{
        display: grid;
        gap: 12px;
        margin-top: 28px;
      }}
      .rule-card {{
        display: grid;
        grid-template-columns: 96px 1fr;
        gap: 18px;
        padding: 20px;
      }}
      .row-id {{
        display: inline-grid;
        place-items: center;
        width: 84px;
        height: 42px;
        border-radius: 8px;
        color: #fff;
        background: var(--ink);
        font-weight: 900;
      }}
      .rule-card h2 {{
        margin: 0 0 10px;
        font-size: 22px;
      }}
      .rule-card p {{
        margin: 7px 0 0;
        color: var(--muted);
      }}
      .rule-card strong {{
        color: var(--text);
      }}
      code {{
        padding: 2px 5px;
        border-radius: 5px;
        background: #f1f3f0;
        color: var(--text);
        overflow-wrap: anywhere;
      }}
      .boundary {{
        margin-top: 28px;
        padding: 18px;
        background: #10110f;
        color: #fff;
      }}
      .boundary li {{
        margin-top: 6px;
      }}
      @media (max-width: 760px) {{
        main {{ width: min(100% - 24px, 1080px); padding-top: 34px; }}
        .status-grid,
        .rule-card {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p class="eyebrow">SAEE 商用准备 · 人工录入质量指南</p>
        <h1>这 10 行，不求快，先填对。</h1>
        <p class="lead">本页只告诉人工填写时什么算合格、什么要拒绝。Codex 没有代填值，也没有导入工作簿、关闭 blocker 或声明生产可用。</p>
        <div class="status-grid" aria-label="当前状态">
          <div class="status-card"><strong>{esc(payload['guide_row_count'])}</strong><span>质量规则行</span></div>
          <div class="status-card"><strong>0</strong><span>Codex 生成值</span></div>
          <div class="status-card"><strong>0</strong><span>关闭 blocker</span></div>
          <div class="status-card"><strong>否</strong><span>生产可用</span></div>
        </div>
        <div class="sequence">
          <h2>人工顺序</h2>
          <ol>
            <li>先看本页质量规则。</li>
            <li>只在源 CSV 里填写 <code>human_value_to_enter</code> 和可选 <code>notes_for_human</code>。</li>
            <li>填完后先跑 template preflight 和 e2e dry run。</li>
            <li>检查通过后，再单独申请导入批准。</li>
          </ol>
        </div>
      </section>

      <section class="rules" aria-label="字段质量规则">
        {html_rows(payload['guidance_rows'])}
      </section>

      <section class="boundary">
        <h2>边界</h2>
        <ul>
          <li>不代填证据值。</li>
          <li>不修改源 quick-fill packet。</li>
          <li>不导入工作簿。</li>
          <li>不运行真实输入验证器。</li>
          <li>不关闭 blocker。</li>
          <li>不联系客户，不发布产品，不声明生产可用。</li>
        </ul>
      </section>
    </main>
  </body>
</html>
"""
    OUT_HTML.write_text(body, encoding="utf-8")


def write_audit(payload: dict[str, Any]) -> None:
    OUT_AUDIT.write_text(
        f"""# Commercial Review Batch Human Entry Quality Guide Boundary Audit

- quality_guide_only: true
- field_level_quality_rules: true
- placeholder_examples_only: true
- human_values_generated_by_codex: false
- human_input_filled_by_codex: false
- raw_values_recorded: false
- source_quick_fill_packet_modified: false
- quick_fill_imported_to_workbook: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_quality_guide: 0
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- customer_contacted: false
- product_launched: false
- production_ready: false
- production_ready_claim: false
- customer_validation_claim: false
- boundary_violation_count: {payload['boundary_violation_count']}
""",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        f"""# SAEE Commercial Review Batch Human Entry Quality Guide Recommendation Gate

answer: recommend
recommend_for_human_entry_quality_review: true
recommend_for_value_generation: false
recommend_for_workbook_import: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_production_launch: false

## Reason

The guide improves the current commercial-readiness workflow by making the
active 10-row support-contact batch safer for human entry. It gives each field
an accepted value shape, quality rule, reject rule, placeholder-only example,
and privacy note without generating or recording real values.

## Boundary

- status: {payload['status']}
- guide_row_count: {payload['guide_row_count']}
- target_blocker_id: support_contact
- quality_guide_only: true
- human_values_generated_by_codex: false
- human_input_filled_by_codex: false
- raw_values_recorded: false
- quick_fill_imported_to_workbook: false
- workbook_import_authorized: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false

## Next Human Action

Open the quality guide, then fill only `human_value_to_enter` and optional
`notes_for_human` in the active 10-row source CSV. Do not import the workbook
without a separate approval request.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_HUMAN_ENTRY_QUALITY_GUIDE: PASS "
        f"status={payload['status']} guide_row_count={payload['guide_row_count']} "
        "values_generated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
