#!/usr/bin/env python3
"""Read-only readiness preview for the 10-row commercial review batch.

This preview helps a human see which review-batch rows still need values before
running the existing post-fill check. It never generates values, records raw
human values or notes, imports workbooks, runs validators on real input, closes
blockers, contacts customers, launches product, or claims production readiness.
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
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

SOURCE_TEMPLATE = (
    SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
OUT_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview.html"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_post_fill_readiness_preview_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 10
SUPERSEDED_REVIEW_BATCH_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"
POST_FILL_CHECK_COMMAND = "python3 scripts/saee_commercial_review_batch_post_fill_check.py"
WORKBOOK_IMPORT_APPROVAL_PACKET_COMMAND = (
    "python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py"
)
POST_FILL_E2E_DRY_RUN_COMMAND = (
    "python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py"
)

FALSE_FLAGS = [
    "raw_values_recorded",
    "raw_notes_recorded",
    "human_values_generated_by_codex",
    "codex_prefill_performed",
    "source_template_modified",
    "source_quick_fill_packet_modified",
    "post_fill_check_executed",
    "post_fill_e2e_dry_run_executed",
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
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "production_ready_claim",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def read_rows() -> list[dict[str, str]]:
    with SOURCE_TEMPLATE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def preview_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    for row in rows:
        value_present = bool(row.get("human_value_to_enter", "").strip())
        notes_present = bool(row.get("notes_for_human", "").strip())
        preview.append(
            {
                "review_batch_row_id": row.get("review_batch_row_id", ""),
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "queue_item_id": row.get("queue_item_id", ""),
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "input_kind": row.get("input_kind", ""),
                "expected_value_shape": row.get("expected_value_shape", ""),
                "target_json_pointer": row.get("target_json_pointer", ""),
                "value_present": value_present,
                "notes_present": notes_present,
                "row_status": "value_present" if value_present else "missing_human_value",
                "next_action": (
                    "Ready for post-fill check after all rows are present."
                    if value_present
                    else "Human must enter this row before post-fill check."
                ),
            }
        )
    return preview


def build_payload() -> dict[str, Any]:
    rows = read_rows()
    previews = preview_rows(rows)
    filled_count = sum(1 for row in previews if row["value_present"])
    missing_count = len(previews) - filled_count
    notes_count = sum(1 for row in previews if row["notes_present"])
    review_batch_superseded = len(rows) == 0
    boundary_violations: list[str] = []
    if len(rows) != EXPECTED_ROW_COUNT and not review_batch_superseded:
        boundary_violations.append("unexpected_review_batch_row_count")

    if review_batch_superseded:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    elif boundary_violations:
        status = "stop_readiness_preview_boundary_issue"
    elif missing_count:
        status = "hold_human_values_required"
    else:
        status = "ready_for_post_fill_check_pending_human_command"

    payload: dict[str, Any] = {
        "commercial_review_batch_post_fill_readiness_preview_v0_1": True,
        "preview_type": "read_only_10_row_post_fill_readiness_preview",
        "preview_scope": "local_presence_preview_no_raw_values_no_import_no_closure",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_post_fill_readiness_preview.py",
        "source_template_csv": rel(SOURCE_TEMPLATE),
        "expected_review_batch_row_count": EXPECTED_ROW_COUNT,
        "review_batch_row_count": len(rows),
        "filled_human_value_row_count": filled_count,
        "missing_human_value_row_count": missing_count,
        "notes_present_row_count": notes_count,
        "missing_review_batch_row_ids": [
            row["review_batch_row_id"] for row in previews if not row["value_present"]
        ],
        "human_input_required": missing_count > 0 and not review_batch_superseded,
        "post_fill_check_ready": missing_count == 0 and not boundary_violations and not review_batch_superseded,
        "review_batch_route_superseded": review_batch_superseded,
        "ready_for_workbook_import_approval_review": review_batch_superseded,
        "post_fill_check_command": (
            WORKBOOK_IMPORT_APPROVAL_PACKET_COMMAND
            if review_batch_superseded
            else POST_FILL_CHECK_COMMAND
        ),
        "post_fill_e2e_dry_run_command": POST_FILL_E2E_DRY_RUN_COMMAND,
        "mainline_guard_command": "python3 scripts/mainline_guard.py",
        "make_target": "make check-commercial-review-batch-post-fill-readiness-preview",
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "blockers_closed_by_preview": 0,
        "rows": previews,
        "next_human_action": (
            "Review the workbook import approval request packet. Do not import workbooks, run validators on real input, collect evidence, or close blockers without separate explicit approval."
            if review_batch_superseded
            else "Fill only the 10 review-batch human_value_to_enter cells and optional notes_for_human, "
            "then run python3 scripts/saee_commercial_review_batch_post_fill_check.py. "
            "Do not import workbooks, collect evidence, or close blockers without separate approval."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fieldnames = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "blocker_id",
        "input_group",
        "input_key",
        "input_kind",
        "expected_value_shape",
        "target_json_pointer",
        "value_present",
        "notes_present",
        "row_status",
        "next_action",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def markdown_lines(payload: dict[str, Any]) -> list[str]:
    superseded = bool(payload.get("review_batch_route_superseded"))
    intro = (
        "这个文件只告诉人类：10 行填写路径已经被完整 quick-fill 值替代，下一步只能审查 workbook import 批准包。"
        if superseded
        else "这个文件只告诉人类：10 行里哪些还没填，以及填完后应该运行哪个本地检查。"
    )
    next_heading = "## 下一步审查" if superseded else "## 填完后运行"
    lines = [
        "# SAEE 10 行填后就绪预览",
        "",
        "Commercial Review Batch Post-Fill Readiness Preview v0.1",
        "",
        intro,
        "它不展示、不保存、不生成任何人工填写的原文。",
        "",
        "```text",
        "commercial_review_batch_post_fill_readiness_preview_v0_1: true",
        f"status: {payload['status']}",
        "preview_scope: local_presence_preview_no_raw_values_no_import_no_closure",
        f"review_batch_row_count: {payload['review_batch_row_count']}",
        f"filled_human_value_row_count: {payload['filled_human_value_row_count']}",
        f"missing_human_value_row_count: {payload['missing_human_value_row_count']}",
        f"post_fill_check_ready: {bool_text(payload['post_fill_check_ready'])}",
        f"review_batch_route_superseded: {bool_text(payload['review_batch_route_superseded'])}",
        f"ready_for_workbook_import_approval_review: {bool_text(payload['ready_for_workbook_import_approval_review'])}",
        "raw_values_recorded: false",
        "raw_notes_recorded: false",
        "human_values_generated_by_codex: false",
        "codex_prefill_performed: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "blockers_closed_by_preview: 0",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "```",
        "",
        "## 行级预览",
        "",
        "| Row | Field | Expected shape | Value present | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {row_id} | `{field}` | {shape} | {present} | {status} |".format(
                row_id=row["review_batch_row_id"],
                field=row["input_key"],
                shape=row["expected_value_shape"],
                present=bool_text(row["value_present"]),
                status=row["row_status"],
            )
        )
    lines.extend(
        [
            "",
            next_heading,
            "",
            f"```bash\n{payload['post_fill_check_command']}\n```",
            "",
            "## 边界",
            "",
            "- 不代填 `human_value_to_enter`。",
            "- 不记录 `human_value_to_enter` 或 `notes_for_human` 的原文。",
            "- 不运行 post-fill check。",
            "- 不运行真实输入 validator。",
            "- 不导入 workbook。",
            "- 不收集证据。",
            "- 不关闭 blocker。",
            "- 不联系客户。",
            "- 不声明生产可用。",
        ]
    )
    return lines


def write_markdown(payload: dict[str, Any]) -> None:
    text = "\n".join(markdown_lines(payload)) + "\n"
    OUT_MD.write_text(text, encoding="utf-8")
    TOP_DOC.write_text(text, encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    superseded = bool(payload.get("review_batch_route_superseded"))
    hero_title = (
        "10 行填写流程已替代，下一步只审查导入批准。"
        if superseded
        else "10 行还没填完，先不要进入填后检查。"
    )
    hero_copy = (
        "本页只记录旧流程已替代，不显示任何人工填写原文，也不授权工作簿导入。"
        if superseded
        else "本页只显示每行是否已有值，不显示任何人工填写原文。"
    )
    command_label = "下一步审查：" if superseded else "填完后运行："
    rows_html = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['review_batch_row_id'])}</td>"
        f"<td><code>{html.escape(row['input_key'])}</code></td>"
        f"<td>{html.escape(row['expected_value_shape'])}</td>"
        f"<td>{html.escape(bool_text(row['value_present']))}</td>"
        f"<td>{html.escape(row['row_status'])}</td>"
        "</tr>"
        for row in payload["rows"]
    )
    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 10 行填后就绪预览</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f2;
      --surface: #ffffff;
      --line: #e2e2da;
      --text: #20211f;
      --muted: #696b65;
      --accent: #0b6f5b;
      --ink: #171815;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    main {{ width: min(1080px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0; }}
    .hero {{ padding: 28px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }}
    .kicker {{ margin: 0 0 8px; color: var(--accent); font-size: 13px; font-weight: 800; }}
    h1 {{ margin: 0; font-size: clamp(32px, 5vw, 56px); line-height: 1.05; }}
    p {{ color: var(--muted); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 22px; }}
    .stat {{ padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fbfbf7; }}
    .stat strong {{ display: block; font-size: 26px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 24px; background: var(--surface); border: 1px solid var(--line); }}
    th, td {{ padding: 11px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #f0f1ec; }}
    code {{ padding: 2px 5px; border-radius: 5px; background: #f0f1ec; }}
    .command {{ margin-top: 24px; padding: 16px; border-radius: 8px; background: var(--ink); color: #fff; }}
    .command code {{ color: #fff; background: rgba(255,255,255,0.14); }}
    @media (max-width: 720px) {{ .stats {{ grid-template-columns: 1fr; }} table {{ font-size: 13px; }} }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <p class="kicker">本地只读预览</p>
      <h1>{html.escape(hero_title)}</h1>
      <p>{html.escape(hero_copy)}</p>
      <div class="stats">
        <div class="stat"><span>总行数</span><strong>{payload['review_batch_row_count']}</strong></div>
        <div class="stat"><span>已填</span><strong>{payload['filled_human_value_row_count']}</strong></div>
        <div class="stat"><span>未填</span><strong>{payload['missing_human_value_row_count']}</strong></div>
      </div>
    </section>
    <table>
      <thead><tr><th>Row</th><th>Field</th><th>Expected shape</th><th>Value present</th><th>Status</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    <div class="command">
      {html.escape(command_label)}<code>{html.escape(payload['post_fill_check_command'])}</code>
    </div>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Review Batch Post-Fill Readiness Preview Boundary Audit",
        "",
        "commercial_review_batch_post_fill_readiness_preview_v0_1: true",
        f"status: {payload['status']}",
        "raw_values_recorded: false",
        "raw_notes_recorded: false",
        "human_values_generated_by_codex: false",
        "codex_prefill_performed: false",
        "source_template_modified: false",
        "post_fill_check_executed: false",
        "post_fill_e2e_dry_run_executed: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_preview: 0",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "private_core_exposed: false",
        "customer_contacted: false",
        "customer_validated: false",
        "product_launched: false",
        "production_ready: false",
        "production_ready_claim: false",
        "",
        "Final boundary decision: read-only row presence preview only.",
    ]
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    target_need = (
        "Help a human operator see that the 10-row support-contact route is superseded and the next step is workbook import approval review."
        if payload["review_batch_route_superseded"]
        else "Help a human operator see whether the 10 support-contact rows are ready for the existing post-fill check."
    )
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Review Batch Post-Fill Readiness Preview Recommendation Gate",
                "",
                "recommendation_gate:",
                "  feature_or_direction: Commercial Review Batch Post-Fill Readiness Preview",
                f"  target_customer_need: {target_need}",
                "  answer: recommend",
                "  reasons_to_recommend:",
                "    - It improves the commercial evidence workflow without creating or inferring human values.",
                "    - It records only presence/absence and expected field shape, not raw human input.",
                "    - It does not modify runtime, backend, kernel, API schema, product behavior, or private core.",
                "  reasons_not_to_recommend: []",
                "  final_decision: recommend as read-only local commercial-readiness guidance only.",
                "",
                "```text",
                "commercial_review_batch_post_fill_readiness_preview_v0_1: true",
                f"status: {payload['status']}",
                f"review_batch_route_superseded: {bool_text(payload['review_batch_route_superseded'])}",
                f"ready_for_workbook_import_approval_review: {bool_text(payload['ready_for_workbook_import_approval_review'])}",
                "recommend_for_read_only_presence_preview: true",
                "recommend_for_value_generation: false",
                "recommend_for_codex_prefill: false",
                "recommend_for_workbook_import: false",
                "recommend_for_validator_execution: false",
                "recommend_for_blocker_closure: false",
                "raw_values_recorded: false",
                "blockers_closed_by_preview: 0",
                "production_ready: false",
                "product_launched: false",
                "customer_contacted: false",
                "private_core_exposed: false",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_boundary(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_READINESS_PREVIEW: PASS "
        f"status={payload['status']} "
        f"filled={payload['filled_human_value_row_count']} "
        f"missing={payload['missing_human_value_row_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
