#!/usr/bin/env python3
"""Generate the minimum human-input workspace for production_restore_policy.

This workspace turns the production-restore-policy blocker into a human-owned
field inventory that can later feed the existing local approval-input
validator. It does not approve policy, run restore, touch live data paths,
restore credentials, contact customers or vendors, run evidence builders, close
blockers, or claim production readiness.
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
EVIDENCE_DIR = COMMERCIAL_DIR / "data_operations_evidence"
OUT_DIR = EVIDENCE_DIR / "production_restore_policy_minimum_human_input_workspace"
OUT_JSON = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.local.json"
OUT_MD = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.md"
OUT_CSV = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.csv"
OUT_HTML = OUT_DIR / "production_restore_policy_minimum_human_input_workspace.html"
OUT_AUDIT = OUT_DIR / "production_restore_policy_minimum_human_input_workspace_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE_GATE.md"

PROMPT_JSON = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.local.json"
TEMPLATE_JSON = EVIDENCE_DIR / "production_restore_policy_approval_input.template.json"
VALIDATION_JSON = EVIDENCE_DIR / "production_restore_policy_approval_input_validation.local.json"
REVIEW_PACKET_JSON = EVIDENCE_DIR / "production_restore_policy_review_packet.local.json"
DRAFT_JSON = EVIDENCE_DIR / "production_restore_policy_draft.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "data_operations_owner",
    "security_owner",
    "privacy_legal_owner",
    "incident_response_owner",
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
        "production_restore_policy_approved": False,
        "production_restore_policy_available": False,
        "production_restore_policy_claim_published": False,
        "production_restore_policy_effective_for_customers": False,
        "restore_policy_published_by_codex": False,
        "policy_approved_by_codex": False,
        "restore_tested": False,
        "restore_to_live_path_enabled": False,
        "live_restore_performed": False,
        "live_restore_authorized_by_codex": False,
        "production_data_path_modified": False,
        "customer_notification_sent_by_codex": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "public_sdk_released": False,
    }


def policy_keys(template: dict[str, Any]) -> list[str]:
    keys = list(template.get("policy_evidence_review", {}).keys())
    if keys:
        return keys
    return [slot["evidence_key"] for slot in template.get("policy_evidence_slots", [])]


def field_rows(template: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in METADATA_FIELDS:
        rows.append(
            {
                "field_id": f"production_restore_policy_approval_input.{field}",
                "group": "metadata",
                "required": True,
                "where_to_fill": "production_restore_policy_approval_input.human_filled.local.json",
                "human_instruction": "由人填写真实恢复策略审批信息；Codex 不能代填。",
            }
        )
    for key in policy_keys(template):
        rows.extend(
            [
                {
                    "field_id": f"production_restore_policy_approval_input.policy_evidence_review.{key}",
                    "group": "policy_evidence_review",
                    "required": True,
                    "where_to_fill": "production_restore_policy_approval_input.human_filled.local.json",
                    "human_instruction": "只有人工确认真实恢复策略证据存在且已审查时才设为 true。",
                },
                {
                    "field_id": f"production_restore_policy_approval_input.source_notes_by_key.{key}",
                    "group": "source_note",
                    "required": True,
                    "where_to_fill": "production_restore_policy_approval_input.human_filled.local.json",
                    "human_instruction": "填写可追溯来源说明；不要写密钥、客户数据、账号或私人凭据。",
                },
                {
                    "field_id": f"production_restore_policy_approval_input.policy_evidence_slots[{key}].evidence_reference",
                    "group": "policy_evidence_slot",
                    "required": True,
                    "where_to_fill": "production_restore_policy_approval_input.human_filled.local.json",
                    "human_instruction": "填写人工审查材料、政策记录或演练记录引用。",
                },
                {
                    "field_id": f"production_restore_policy_approval_input.policy_evidence_slots[{key}].owner_named",
                    "group": "policy_evidence_slot",
                    "required": True,
                    "where_to_fill": "production_restore_policy_approval_input.human_filled.local.json",
                    "human_instruction": "对应负责人已明确时才设为 true。",
                },
                {
                    "field_id": f"production_restore_policy_approval_input.policy_evidence_slots[{key}].reviewed_by_human",
                    "group": "policy_evidence_slot",
                    "required": True,
                    "where_to_fill": "production_restore_policy_approval_input.human_filled.local.json",
                    "human_instruction": "对应材料已由人审过时才设为 true。",
                },
            ]
        )
    return rows


def build_payload() -> dict[str, Any]:
    prompt = load_json(PROMPT_JSON)
    template = load_json(TEMPLATE_JSON)
    validation = load_json(VALIDATION_JSON)
    review_packet = load_json(REVIEW_PACKET_JSON)
    draft = load_json(DRAFT_JSON)
    rows = field_rows(template)
    evidence_count = len(policy_keys(template))
    payload: dict[str, Any] = {
        "production_restore_policy_minimum_human_input_workspace_v0_1": True,
        "workspace_type": "minimum_production_restore_policy_human_input_workspace",
        "workspace_scope": "human_field_inventory_only_no_values_no_submit_no_execution",
        "status": "hold_minimum_human_input_required",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "target_blocker_id": "production_restore_policy",
        "source_prompt_json": rel(PROMPT_JSON),
        "source_template_json": rel(TEMPLATE_JSON),
        "source_validation_json": rel(VALIDATION_JSON),
        "source_review_packet_json": rel(REVIEW_PACKET_JSON),
        "source_draft_json": rel(DRAFT_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "minimum_required_field_count": len(rows),
        "minimum_required_human_value_count": len(rows),
        "filled_value_count": 0,
        "blank_value_count": len(rows),
        "metadata_field_count": len(METADATA_FIELDS),
        "production_restore_policy_evidence_key_count": evidence_count,
        "policy_evidence_review_field_count": evidence_count,
        "source_note_field_count": evidence_count,
        "policy_evidence_slot_field_count": evidence_count * 3,
        "field_rows": rows,
        "prompt_status": prompt.get("status", "hold_human_restore_policy_approval_input_required"),
        "validator_status": validation.get("validation_status", "hold"),
        "review_packet_status": review_packet.get("packet_status", "draft_ready_for_human_review"),
        "draft_status": draft.get("draft_status", "draft_not_approved"),
        "human_review_required": True,
        "human_input_required": True,
        "next_human_action": (
            "Copy production_restore_policy_approval_input.template.json to the "
            "human_filled path, fill only human-approved metadata, policy evidence "
            "flags, source notes, and evidence-slot references, then run the local "
            "validator. Do not approve policy, run restore, touch live data paths, "
            "contact customers or vendors, run the evidence builder, or close blockers."
        ),
        "copy_commands": [
            (
                "cp phase_b_product/commercial_readiness/data_operations_evidence/"
                "production_restore_policy_approval_input.template.json "
                "phase_b_product/commercial_readiness/data_operations_evidence/"
                "production_restore_policy_approval_input.human_filled.local.json"
            )
        ],
        "post_fill_validation_commands": [
            (
                "python3 scripts/saee_production_restore_policy_approval_input_validator.py "
                "--input phase_b_product/commercial_readiness/data_operations_evidence/"
                "production_restore_policy_approval_input.human_filled.local.json"
            )
        ],
        "separate_execution_only_after_human_approval": [
            (
                "python3 scripts/saee_production_restore_policy_evidence_builder.py "
                "--input phase_b_product/commercial_readiness/data_operations_evidence/"
                "production_restore_policy_approval_input.human_filled.local.json"
            )
        ],
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    payload.update(false_boundary())
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = ["field_id", "group", "required", "where_to_fill", "human_instruction"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload["field_rows"])


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Production Restore Policy Minimum Human Input Workspace v0.1",
        "",
        "`production_restore_policy_minimum_human_input_workspace_v0_1: true`",
        "",
        "## 目的",
        "",
        "这个工作台只回答一个问题：为了让 `production_restore_policy` 进入本地 validator，",
        "人类最少需要补齐哪些恢复策略审批字段。它不批准策略，不执行恢复，不触碰实时数据路径，",
        "不运行 evidence builder，也不关闭 blocker。",
        "",
        "## 当前状态",
        "",
        f"- status: {payload['status']}",
        "- target_blocker_id: production_restore_policy",
        f"- minimum_required_field_count: {payload['minimum_required_field_count']}",
        f"- blank_value_count: {payload['blank_value_count']}",
        f"- metadata_field_count: {payload['metadata_field_count']}",
        f"- production_restore_policy_evidence_key_count: {payload['production_restore_policy_evidence_key_count']}",
        f"- policy_evidence_slot_field_count: {payload['policy_evidence_slot_field_count']}",
        "- production_restore_policy_approved: false",
        "- production_restore_policy_available: false",
        "- live_restore_performed: false",
        "- production_data_path_modified: false",
        "- blocker_closure_authorized: false",
        "- production_ready: false",
        "- product_launched: false",
        "- customer_validated: false",
        "",
        "## 人需要填写的字段",
        "",
        "| 字段 | 分组 | 填到哪里 | 人工说明 |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["field_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['field_id']}`",
                    row["group"],
                    f"`{row['where_to_fill']}`",
                    row["human_instruction"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 推荐流程",
            "",
            "1. 人类复制模板到 `production_restore_policy_approval_input.human_filled.local.json`。",
            "2. 人类只填写已审批的元数据、策略证据标记、来源说明和证据槽引用。",
            "3. 人类运行本地 validator。",
            "4. 如果 validator 通过，仍需单独批准才能运行 evidence builder。",
            "",
            "## 禁止事项",
            "",
            "- Codex 不得代填人工值。",
            "- 不得从这个工作台执行恢复、触碰实时数据路径或恢复凭据。",
            "- 不得联系客户、供应商或法律/安全审查人。",
            "- 不得关闭 blocker、发布产品或声明生产可用。",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{html.escape(row['field_id'])}</code></td>"
        f"<td>{html.escape(row['group'])}</td>"
        f"<td><code>{html.escape(row['where_to_fill'])}</code></td>"
        f"<td>{html.escape(row['human_instruction'])}</td>"
        "</tr>"
        for row in payload["field_rows"]
    )
    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 生产恢复策略人工填写工作台</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f6f2;
        --surface: #ffffff;
        --text: #1f241f;
        --muted: #66706a;
        --line: #deded8;
        --accent: #147a64;
        --accent-soft: #e8f3ef;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text);
        background: linear-gradient(135deg, #ffffff 0%, var(--bg) 70%, var(--accent-soft) 100%);
        line-height: 1.6;
      }}
      main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 44px 0 64px; }}
      header, section {{ border: 1px solid var(--line); border-radius: 10px; background: var(--surface); padding: 24px; margin-bottom: 18px; }}
      h1 {{ margin: 0; font-size: clamp(30px, 4vw, 52px); line-height: 1.06; letter-spacing: 0; }}
      h2 {{ margin: 0 0 12px; font-size: 24px; }}
      p {{ margin: 8px 0 0; color: var(--muted); }}
      .badge {{ display: inline-flex; padding: 6px 10px; border-radius: 999px; color: var(--accent); background: var(--accent-soft); font-weight: 800; font-size: 13px; margin-bottom: 14px; }}
      .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
      .card {{ border: 1px solid var(--line); border-radius: 8px; padding: 16px; background: #fbfbf9; }}
      .card strong {{ display: block; font-size: 24px; }}
      .card span {{ color: var(--muted); font-size: 13px; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }}
      th, td {{ border-bottom: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }}
      th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
      code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
      .warning {{ border-color: #d7c79a; background: #fff9e8; }}
      @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} table {{ display: block; overflow-x: auto; }} }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <div class="badge">生产恢复策略 · 人工填写</div>
        <h1>先让人补齐恢复策略证据，不让 Codex 猜。</h1>
        <p>这个页面只是给人看的字段清单。它不会保存表单，不会执行恢复，不会运行 builder，不会关闭 blocker。</p>
        <div class="grid">
          <div class="card"><strong>{payload['minimum_required_field_count']}</strong><span>需要人工填写的字段</span></div>
          <div class="card"><strong>{payload['blank_value_count']}</strong><span>当前空值</span></div>
          <div class="card"><strong>0</strong><span>已关闭 blocker</span></div>
          <div class="card"><strong>否</strong><span>生产可用</span></div>
        </div>
      </header>
      <section class="warning">
        <h2>停止线</h2>
        <p>填完后只运行本地 validator。运行 evidence builder、执行恢复、触碰实时数据路径、联系客户或声明生产恢复能力，都需要单独人工批准。</p>
      </section>
      <section>
        <h2>字段清单</h2>
        <table>
          <thead><tr><th>字段</th><th>分组</th><th>写入位置</th><th>说明</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </section>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_audit(payload: dict[str, Any]) -> None:
    OUT_AUDIT.write_text(
        "\n".join(
            [
                "# Production Restore Policy Minimum Human Input Workspace Boundary Audit",
                "",
                "production_restore_policy_minimum_human_input_workspace_v0_1: true",
                "boundary_decision: pass",
                f"status: {payload['status']}",
                f"minimum_required_field_count: {payload['minimum_required_field_count']}",
                f"blank_value_count: {payload['blank_value_count']}",
                "production_restore_policy_approved: false",
                "production_restore_policy_available: false",
                "restore_to_live_path_enabled: false",
                "live_restore_performed: false",
                "production_data_path_modified: false",
                "credentials_restored: false",
                "private_core_restored: false",
                "values_saved_by_workspace: false",
                "form_submission_enabled: false",
                "validator_inputs_exported: false",
                "validators_run: false",
                "blocker_closure_authorized: false",
                "runtime_modified: false",
                "backend_modified: false",
                "kernel_modified: false",
                "api_schema_modified: false",
                "private_core_exposed: false",
                "customer_contacted: false",
                "external_calls_made: false",
                "product_launched: false",
                "production_ready: false",
                "customer_validated: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_readme_and_gate(payload: dict[str, Any]) -> None:
    readme = [
        "# Production Restore Policy Minimum Human Input Workspace",
        "",
        "This directory contains a local, human-fillable field inventory for the",
        "`production_restore_policy` commercial blocker. It is documentation and",
        "local validation preparation only.",
        "",
        f"- status: {payload['status']}",
        f"- minimum_required_field_count: {payload['minimum_required_field_count']}",
        f"- blank_value_count: {payload['blank_value_count']}",
        "- production_restore_policy_approved: false",
        "- production_restore_policy_available: false",
        "- live_restore_performed: false",
        "- production_ready: false",
    ]
    OUT_README.write_text("\n".join(readme) + "\n", encoding="utf-8")
    TOP_DOC.write_text(
        "\n".join(
            [
                "# SAEE Production Restore Policy Minimum Human Input Workspace v0.1",
                "",
                "production_restore_policy_minimum_human_input_workspace_v0_1: true",
                f"status: {payload['status']}",
                "target_blocker_id: production_restore_policy",
                f"minimum_required_field_count: {payload['minimum_required_field_count']}",
                f"blank_value_count: {payload['blank_value_count']}",
                "production_restore_policy_approved: false",
                "production_restore_policy_available: false",
                "live_restore_performed: false",
                "production_data_path_modified: false",
                "blocker_closure_authorized: false",
                "production_ready: false",
                "",
                "This is a human input workspace only. It does not approve policy, run",
                "restore, touch live data paths, execute evidence builders, contact",
                "customers/vendors, close blockers, launch product, or claim production",
                "readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Production Restore Policy Minimum Human Input Workspace Gate",
                "",
                "answer: hold_minimum_human_input_required",
                "reason: The production restore policy blocker has a local minimum",
                "human input workspace, but no human values have been entered and no",
                "restore policy has been approved.",
                "",
                "boundary:",
                "  production_restore_policy_approved: false",
                "  production_restore_policy_available: false",
                "  live_restore_performed: false",
                "  production_data_path_modified: false",
                "  blocker_closure_authorized: false",
                "  runtime_modified: false",
                "  backend_modified: false",
                "  kernel_modified: false",
                "  api_schema_modified: false",
                "  private_core_exposed: false",
                "  product_launched: false",
                "  production_ready: false",
                "",
                "next_action: Human data-operations, security, privacy/legal, and",
                "incident-response owners fill the local approval input, then run the",
                "validator. Evidence builder execution still needs separate approval.",
            ]
        )
        + "\n",
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
    write_readme_and_gate(payload)
    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_MINIMUM_HUMAN_INPUT_WORKSPACE: PASS "
        f"status={payload['status']} fields={payload['minimum_required_field_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
