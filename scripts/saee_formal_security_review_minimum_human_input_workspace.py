#!/usr/bin/env python3
"""Generate the minimum human-input workspace for formal_security_review.

This workspace reduces the formal-security-review commercial blocker to the
smallest human-owned field inventory needed before the existing local validator
can be useful. It does not perform or approve a security review, contact
reviewers or vendors, run penetration tests, inspect private core, run evidence
builders, close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "privacy_security_legal_evidence"
OUT_DIR = EVIDENCE_DIR / "formal_security_review_minimum_human_input_workspace"
OUT_JSON = OUT_DIR / "formal_security_review_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "formal_security_review_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "formal_security_review_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "formal_security_review_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "formal_security_review_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"

PROMPT_JSON = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.local.json"
TEMPLATE_JSON = EVIDENCE_DIR / "formal_security_review_evidence_input.template.json"
VALIDATION_JSON = EVIDENCE_DIR / "formal_security_review_approval_input_validation.local.json"
SCOPE_DRAFT_JSON = EVIDENCE_DIR / "formal_security_review_scope_draft.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "security_review_owner",
    "report_reference",
    "decision_summary",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def false_boundary() -> dict[str, bool]:
    return {
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "workbook_import_authorized": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "development_permission_granted": False,
        "production_ready_claim": False,
        "customer_validation_claim": False,
        "human_values_generated_by_codex": False,
        "human_input_filled_by_codex": False,
        "validator_inputs_exported": False,
        "validators_run": False,
        "values_saved_by_workspace": False,
        "form_submission_enabled": False,
        "formal_security_review_approved": False,
        "formal_security_review_completed": False,
        "formal_security_review_report_approved": False,
        "formal_security_review_available": False,
        "formal_security_review_claim_published": False,
        "security_review_claim_published": False,
        "production_security_claim_published": False,
        "production_security_enabled": False,
        "dependency_review_completed": False,
        "vulnerability_management_operational": False,
        "private_core_inspected_by_codex": False,
        "penetration_test_run_by_codex": False,
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
    }


def field_rows(template: dict[str, Any]) -> list[dict[str, Any]]:
    evidence_keys = list(template.get("evidence_review", {}).keys())
    rows: list[dict[str, Any]] = []
    for field in METADATA_FIELDS:
        rows.append(
            {
                "field_id": f"formal_security_review_evidence_input.{field}",
                "group": "metadata",
                "required": True,
                "where_to_fill": "formal_security_review_evidence_input.human_filled.local.json",
                "human_instruction": "由人填写真实安全审查信息；Codex 不能代填。",
            }
        )
    for key in evidence_keys:
        rows.extend(
            [
                {
                    "field_id": f"formal_security_review_evidence_input.evidence_review.{key}",
                    "group": "evidence_review",
                    "required": True,
                    "where_to_fill": "formal_security_review_evidence_input.human_filled.local.json",
                    "human_instruction": "只有人工确认真实安全审查证据存在时才设为 true。",
                },
                {
                    "field_id": f"formal_security_review_evidence_input.source_notes_by_key.{key}",
                    "group": "source_note",
                    "required": True,
                    "where_to_fill": "formal_security_review_evidence_input.human_filled.local.json",
                    "human_instruction": "填写可追溯来源说明；不要写密钥、账号、客户数据或私人凭据。",
                },
                {
                    "field_id": f"formal_security_review_evidence_input.review_artifacts[{key}].artifact_reference",
                    "group": "review_artifact",
                    "required": True,
                    "where_to_fill": "formal_security_review_evidence_input.human_filled.local.json",
                    "human_instruction": "填写人工审查报告、范围记录或审批材料引用。",
                },
                {
                    "field_id": f"formal_security_review_evidence_input.review_artifacts[{key}].owner_named",
                    "group": "review_artifact",
                    "required": True,
                    "where_to_fill": "formal_security_review_evidence_input.human_filled.local.json",
                    "human_instruction": "对应负责人已明确时才设为 true。",
                },
                {
                    "field_id": f"formal_security_review_evidence_input.review_artifacts[{key}].reviewed_by_human",
                    "group": "review_artifact",
                    "required": True,
                    "where_to_fill": "formal_security_review_evidence_input.human_filled.local.json",
                    "human_instruction": "对应材料已由人审过时才设为 true。",
                },
            ]
        )
    return rows


def build_payload() -> dict[str, Any]:
    prompt = load_json(PROMPT_JSON)
    template = load_json(TEMPLATE_JSON)
    validation = load_json(VALIDATION_JSON)
    scope_draft = load_json(SCOPE_DRAFT_JSON)
    rows = field_rows(template)
    evidence_count = len(template.get("evidence_review", {}))
    payload: dict[str, Any] = {
        "formal_security_review_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_formal_security_review_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "formal_security_review",
        "source_prompt_json": rel(PROMPT_JSON),
        "source_template_json": rel(TEMPLATE_JSON),
        "source_validation_json": rel(VALIDATION_JSON),
        "source_scope_draft_json": rel(SCOPE_DRAFT_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "minimum_required_field_count": len(rows),
        "minimum_required_human_value_count": len(rows),
        "filled_value_count": 0,
        "blank_value_count": len(rows),
        "metadata_field_count": len(METADATA_FIELDS),
        "formal_security_review_evidence_key_count": evidence_count,
        "evidence_review_field_count": evidence_count,
        "source_note_field_count": evidence_count,
        "review_artifact_field_count": evidence_count * 3,
        "field_rows": rows,
        "prompt_status": prompt.get("status", "hold_human_formal_security_review_input_required"),
        "validator_status": validation.get("validation_status", "hold"),
        "scope_draft_status": scope_draft.get("draft_status", "draft_not_approved"),
        "human_review_required": True,
        "human_input_required": True,
        "next_human_action": (
            "Copy formal_security_review_evidence_input.template.json to the "
            "human_filled path, fill only human-approved metadata, evidence flags, "
            "source notes, and review-artifact references, then run the local "
            "validator. Do not perform a security review, contact reviewers, run "
            "penetration tests, inspect private core, or close blockers."
        ),
        "copy_commands": [
            (
                "cp phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
                "formal_security_review_evidence_input.template.json "
                "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
                "formal_security_review_evidence_input.human_filled.local.json"
            )
        ],
        "post_fill_validation_commands": [
            (
                "python3 scripts/saee_formal_security_review_approval_input_validator.py "
                "--input phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
                "formal_security_review_evidence_input.human_filled.local.json"
            )
        ],
        "separate_execution_only_after_human_approval": [
            (
                "python3 scripts/saee_formal_security_review_evidence_builder.py "
                "--input phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
                "formal_security_review_evidence_input.human_filled.local.json"
            )
        ],
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    payload.update(false_boundary())
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_csv(payload: dict[str, Any]) -> None:
    fields = ["field_id", "group", "required", "where_to_fill", "human_instruction"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload["field_rows"])


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Formal Security Review Minimum Human Input Workspace v0.1",
        "",
        "`formal_security_review_minimum_human_input_workspace_v0_1: true`",
        "",
        "## 目的",
        "",
        "这个工作台只回答一个问题：为了让 `formal_security_review` 进入本地 validator，",
        "人类最少需要补哪些字段。它不执行安全审查、不批准安全报告、不联系审查方、",
        "不跑渗透测试、不查看私有核心、不运行 evidence builder、不关闭 blocker。",
        "",
        "## 状态",
        "",
        f"- `status: {payload['status']}`",
        f"- `target_blocker_id: {payload['target_blocker_id']}`",
        f"- `minimum_required_field_count: {payload['minimum_required_field_count']}`",
        f"- `filled_value_count: {payload['filled_value_count']}`",
        f"- `blank_value_count: {payload['blank_value_count']}`",
        "- `formal_security_review_completed: false`",
        "- `formal_security_review_approved: false`",
        "- `private_core_exposed: false`",
        "- `production_ready: false`",
        "- `product_launched: false`",
        "",
        "## 最小字段清单",
        "",
        "| 字段 | 分组 | 必填 | 填到哪里 | 人工说明 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["field_rows"]:
        lines.append(
            "| `{field_id}` | {group} | {required} | `{where}` | {instruction} |".format(
                field_id=row["field_id"],
                group=row["group"],
                required=str(row["required"]).lower(),
                where=row["where_to_fill"],
                instruction=row["human_instruction"],
            )
        )
    lines.extend(
        [
            "",
            "## 复制模板",
            "",
            "```bash",
            *payload["copy_commands"],
            "```",
            "",
            "## 人工填写后再运行",
            "",
            "```bash",
            *payload["post_fill_validation_commands"],
            "```",
            "",
            "## 仍需单独批准",
            "",
            "```bash",
            *payload["separate_execution_only_after_human_approval"],
            "```",
            "",
            "## 明确边界",
            "",
            "- `values_saved_by_workspace: false`",
            "- `form_submission_enabled: false`",
            "- `validator_inputs_exported: false`",
            "- `validators_run: false`",
            "- `evidence_collection_authorized: false`",
            "- `blocker_closure_authorized: false`",
            "- `formal_security_review_completed: false`",
            "- `formal_security_review_approved: false`",
            "- `private_core_inspected_by_codex: false`",
            "- `penetration_test_run_by_codex: false`",
            "- `customer_contacted: false`",
            "- `production_ready: false`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "<tr><td><code>{field}</code></td><td>{group}</td><td>{where}</td><td>{note}</td></tr>".format(
            field=html.escape(row["field_id"]),
            group=html.escape(row["group"]),
            where=html.escape(row["where_to_fill"]),
            note=html.escape(row["human_instruction"]),
        )
        for row in payload["field_rows"]
    )
    copy_commands = "<br>".join(html.escape(cmd) for cmd in payload["copy_commands"])
    validation_commands = "<br>".join(
        html.escape(cmd) for cmd in payload["post_fill_validation_commands"]
    )
    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE formal_security_review 最小人工输入工作台</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f6f2;
        --card: #ffffff;
        --ink: #101513;
        --text: #343832;
        --muted: #626861;
        --line: #deddd5;
        --accent: #147a64;
        --soft: #e8f3ef;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.65;
      }}
      main {{ width: min(1160px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0 72px; }}
      h1 {{ margin: 0; color: var(--ink); font-size: clamp(34px, 5vw, 58px); line-height: 1.08; letter-spacing: 0; }}
      h2 {{ margin: 0 0 14px; color: var(--ink); }}
      p {{ margin: 16px 0 0; }}
      .hero {{ display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 24px; align-items: start; }}
      .card, table {{ border: 1px solid var(--line); border-radius: 10px; background: var(--card); box-shadow: 0 18px 48px rgba(16, 21, 19, 0.06); }}
      .card {{ padding: 22px; }}
      .status {{ display: inline-flex; margin-top: 22px; padding: 8px 12px; border-radius: 999px; color: #0f5f50; background: var(--soft); font-weight: 800; }}
      code {{ padding: 2px 6px; border-radius: 6px; background: #eef1ed; color: var(--ink); word-break: break-word; }}
      table {{ width: 100%; margin-top: 28px; border-collapse: separate; border-spacing: 0; overflow: hidden; }}
      th, td {{ padding: 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
      th {{ color: var(--ink); background: #eef1ed; }}
      tr:last-child td {{ border-bottom: 0; }}
      .commands {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }}
      .boundary {{ margin-top: 24px; background: #101513; color: #f7f6f2; }}
      .boundary h2 {{ color: #ffffff; }}
      .boundary code {{ background: rgba(255,255,255,0.1); color: #ffffff; }}
      @media (max-width: 840px) {{ .hero, .commands {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div>
          <h1>只看正式安全审查最少要人填什么。</h1>
          <p>这个页面不保存输入，也不提交表单。它只是把安全审查 blocker 的最小人工字段列清楚。</p>
          <span class="status">状态：{html.escape(payload['status'])}</span>
        </div>
        <aside class="card">
          <h2>当前边界</h2>
          <p><code>formal_security_review_completed: false</code></p>
          <p><code>formal_security_review_approved: false</code></p>
          <p><code>private_core_exposed: false</code></p>
          <p><code>production_ready: false</code></p>
        </aside>
      </section>

      <table>
        <thead><tr><th>字段</th><th>分组</th><th>填到哪里</th><th>说明</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>

      <section class="commands">
        <article class="card">
          <h2>先复制模板</h2>
          <p><code>{copy_commands}</code></p>
        </article>
        <article class="card">
          <h2>人工填完后再跑</h2>
          <p><code>{validation_commands}</code></p>
        </article>
      </section>

      <section class="card boundary">
        <h2>禁止越界</h2>
        <p>本工作台不执行安全审查、不批准报告、不联系审查方、不跑渗透测试、不查看私有核心、不运行 evidence builder、不导入工作簿、不关闭 blocker、不声明生产可用。</p>
      </section>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_audit(payload: dict[str, Any]) -> None:
    lines = [
        "# Formal Security Review Minimum Human Input Workspace Boundary Audit",
        "",
        "Boundary decision: pass_hold.",
        "",
        "- Only minimum human-input field inventory created.",
        "- No formal security review performed by Codex.",
        "- No security report approved by Codex.",
        "- No values saved by workspace.",
        "- No form submission enabled.",
        "- No validator inputs exported.",
        "- No validators run.",
        "- No evidence builder run.",
        "- No workbook import authorized.",
        "- No blocker closure authorized.",
        "- No reviewer or vendor contacted.",
        "- No penetration test run.",
        "- No private core inspected.",
        "- No runtime modified.",
        "- No backend modified.",
        "- No kernel modified.",
        "- No API schema modified.",
        "- No private core exposed.",
        "- No production-ready claim added.",
        "",
        "Machine flags:",
        "",
    ]
    for key, value in sorted(false_boundary().items()):
        lines.append(f"- `{key}: {str(value).lower()}`")
    lines.extend(
        [
            f"- `minimum_required_field_count: {payload['minimum_required_field_count']}`",
            f"- `blank_value_count: {payload['blank_value_count']}`",
        ]
    )
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(payload: dict[str, Any]) -> None:
    OUT_README.write_text(
        f"""# Formal Security Review Minimum Human Input Workspace

This directory contains a local, browser-readable workspace for the minimum
human inputs required before the `formal_security_review` blocker can move to
local validation.

- `formal_security_review_minimum_human_input_workspace_v0_1: true`
- `status: {payload['status']}`
- `minimum_required_field_count: {payload['minimum_required_field_count']}`
- `blank_value_count: {payload['blank_value_count']}`
- `values_saved_by_workspace: false`
- `formal_security_review_completed: false`
- `formal_security_review_approved: false`
- `private_core_exposed: false`
- `production_ready: false`

It does not save values, submit forms, call external services, perform security
review, contact reviewers/vendors, run penetration tests, inspect private core,
import workbooks, run evidence builders, or close blockers.
""",
        encoding="utf-8",
    )


def write_top_docs(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        f"""# SAEE Formal Security Review Minimum Human Input Workspace v0.1

formal_security_review_minimum_human_input_workspace_v0_1: true
status: {payload['status']}
target_blocker_id: formal_security_review
minimum_required_field_count: {payload['minimum_required_field_count']}
blank_value_count: {payload['blank_value_count']}
formal_security_review_completed: false
formal_security_review_approved: false
private_core_inspected_by_codex: false
penetration_test_run_by_codex: false
private_core_exposed: false
production_ready: false
product_launched: false
customer_validated: false

This is a human-input field inventory only. It does not authorize a security
review, reviewer/vendor contact, penetration test, private-core inspection,
evidence collection, workbook import, blocker closure, or production readiness.

Artifacts:
- `phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_minimum_human_input_workspace/formal_security_review_minimum_human_input_workspace.local.json`
- `phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_minimum_human_input_workspace/formal_security_review_minimum_human_input_workspace.html`
- `scripts/saee_formal_security_review_minimum_human_input_workspace.py`
- `scripts/saee_formal_security_review_minimum_human_input_workspace_smoke.py`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Formal Security Review Minimum Human Input Workspace Gate

answer: hold_minimum_human_input_required
reason: The workspace identifies the minimum human-filled fields for the `formal_security_review` blocker, but no values were entered and no evidence was collected.

boundary:
- formal_security_review_completed: false
- formal_security_review_approved: false
- values_saved_by_workspace: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- private_core_inspected_by_codex: false
- penetration_test_run_by_codex: false
- security_vendor_contacted: false
- legal_counsel_contacted: false
- customer_contacted: false
- private_core_exposed: false
- production_ready: false
- product_launched: false
- customer_validated: false

next_action: A human may copy the listed template, fill human-approved values locally, and then run the listed validator. Do not perform security review, contact reviewers/vendors, run penetration tests, inspect private core, or close blockers without a separate explicit request.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_readme(payload)
    write_top_docs(payload)
    print(
        "SAEE_FORMAL_SECURITY_REVIEW_MINIMUM_HUMAN_INPUT_WORKSPACE: PASS "
        f"status={payload['status']} "
        f"fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
