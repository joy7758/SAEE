#!/usr/bin/env python3
"""Build a local completion queue for missing commercial sprint human inputs.

This queue makes the current human-input blocker explicit: which required
workbook rows are still blank, where they came from, and which later template
pointer each row maps to. It does not fill values, transfer values, write
human-filled templates, run validators on real input, collect evidence, execute
builders, contact anyone, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
WORKBOOK_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook.local.json"
VALIDATION_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.local.json"
TRANSFER_MAP_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.local.json"
RESOLVER_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.csv"
OUT_HTML = SPRINT_DIR / "commercial_sprint_human_input_completion_queue.html"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_completion_queue_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 65
EXPECTED_REQUIRED_ROW_COUNT = 64
EXPECTED_BLOCKERS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]

BLOCKER_LABELS = {
    "support_contact": "支持联系方式",
    "pricing_page": "定价页面",
    "formal_security_review": "正式安全审查",
    "production_restore_policy": "生产恢复策略",
    "production_monitoring": "生产监控",
}

LANE_LABELS = {
    "support_operations": "支持运营",
    "commercial_finance_legal": "商业 / 财务 / 法务",
    "security_legal_privacy": "安全 / 法务 / 隐私",
    "data_operations": "数据运营",
    "operations_engineering": "运维工程",
}

FALSE_FLAGS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "task_candidates_executed",
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "human_input_filled_by_codex",
    "validators_run_on_real_input",
    "values_transferred",
    "human_filled_templates_written",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    workbook = load_json(WORKBOOK_JSON)
    validation = load_json(VALIDATION_JSON)
    transfer_map = load_json(TRANSFER_MAP_JSON)
    resolver = load_json(RESOLVER_JSON)
    workbook_rows = read_csv_rows(WORKBOOK_CSV)

    if len(workbook_rows) != EXPECTED_ROW_COUNT:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE: "
            f"FAIL expected {EXPECTED_ROW_COUNT} workbook rows, found {len(workbook_rows)}"
        )
    if validation.get("required_row_count") != EXPECTED_REQUIRED_ROW_COUNT:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE: "
            "FAIL unexpected required_row_count"
        )
    if resolver.get("all_pointers_resolved") is not True:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE: "
            "FAIL transfer resolver pointers are not fully resolved"
        )

    map_by_row = {
        row["workbook_row_id"]: row for row in transfer_map.get("mapping_rows", [])
    }
    validation_by_row = {
        row["workbook_row_id"]: row for row in validation.get("rows", [])
    }
    missing_rows = [
        row
        for row in workbook_rows
        if row.get("minimum_required", "").strip().lower() == "true"
        and not row.get("human_value_placeholder", "").strip()
    ]

    queue_items: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    target_counts: Counter[str] = Counter()
    lane_counts: Counter[str] = Counter()

    for index, row in enumerate(missing_rows, start=1):
        mapped = map_by_row[row["workbook_row_id"]]
        checked = validation_by_row[row["workbook_row_id"]]
        blocker_id = row["blocker_id"]
        target = row["human_filled_input_target"]
        lane = row["owner_review_lane"]
        blocker_counts[blocker_id] += 1
        target_counts[target] += 1
        lane_counts[lane] += 1
        queue_items.append(
            {
                "queue_item_id": f"HIQ-{index:03d}",
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": blocker_id,
                "owner_review_lane": lane,
                "input_group": row["input_group"],
                "input_key": row["input_key"],
                "input_kind": row["input_kind"],
                "minimum_required": True,
                "human_value_present": False,
                "row_complete": False,
                "completion_status": checked.get("status", "missing_human_input"),
                "human_fill_source": rel(WORKBOOK_CSV),
                "human_fill_column": "human_value_placeholder",
                "source_path": row["source_path"],
                "source_prompt": row["source_prompt"],
                "human_filled_input_target": target,
                "target_json_pointer": mapped["target_json_pointer"],
                "pointer_resolved": True,
                "value_transferred": False,
                "template_written": False,
                "recommended_human_action": (
                    "Fill this row's human_value_placeholder cell in the workbook CSV "
                    "with a real human-provided value, then rerun the workbook validator."
                ),
            }
        )

    queue_count = len(queue_items)
    status = "hold_human_input_required" if queue_count else "ready_for_template_transfer"
    payload: dict[str, Any] = {
        "commercial_sprint_human_input_completion_queue_v0_1": True,
        "queue_type": "local_missing_human_input_completion_queue",
        "queue_scope": "missing_required_human_values_only_no_value_transfer",
        "status": status,
        "source_workbook_csv": rel(WORKBOOK_CSV),
        "source_workbook_json": rel(WORKBOOK_JSON),
        "source_validation_json": rel(VALIDATION_JSON),
        "source_transfer_map_json": rel(TRANSFER_MAP_JSON),
        "source_resolver_json": rel(RESOLVER_JSON),
        "source_completion_queue_html": rel(OUT_HTML),
        "local_static_completion_queue_html": True,
        "browser_readable_completion_queue": True,
        "completion_queue_visual_palette": "commercial-clean-slate-mint-v1",
        "local_browser_completion_csv_builder": True,
        "browser_only_completion_csv_text_generation": True,
        "completion_csv_builder_writes_files": False,
        "completion_csv_builder_network_calls": False,
        "completion_csv_builder_imports_workbook": False,
        "grouped_by_blocker": True,
        "grouped_by_owner_review_lane": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_completion_queue.py",
        "selected_blocker_count": workbook.get("selected_blocker_count", 5),
        "selected_blocker_ids": workbook.get("selected_blocker_ids", EXPECTED_BLOCKERS),
        "workbook_row_count": len(workbook_rows),
        "required_row_count": validation.get("required_row_count", EXPECTED_REQUIRED_ROW_COUNT),
        "completed_required_row_count": validation.get("completed_required_row_count", 0),
        "missing_required_row_count": validation.get("missing_required_row_count", queue_count),
        "queue_item_count": queue_count,
        "target_template_count": transfer_map.get("target_template_count", 5),
        "all_pointers_resolved": resolver.get("all_pointers_resolved") is True,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "human_input_required": queue_count > 0,
        "human_review_required": True,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_completion_queue": 0,
        "boundary_violation_count": 0,
        "boundary_violations": [],
        "blocker_missing_counts": dict(sorted(blocker_counts.items())),
        "target_missing_counts": dict(sorted(target_counts.items())),
        "owner_lane_missing_counts": dict(sorted(lane_counts.items())),
        "queue_items": queue_items,
        "next_human_action": (
            "Fill the listed human_value_placeholder cells in "
            f"{rel(WORKBOOK_CSV)}, then run "
            "python3 scripts/saee_commercial_sprint_human_input_workbook_validator.py."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "human_fill_source",
        "human_fill_column",
        "human_filled_input_target",
        "target_json_pointer",
        "source_path",
        "completion_status",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["queue_items"]:
            writer.writerow({field: row[field] for field in fields})


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Completion Queue",
        "",
        "commercial_sprint_human_input_completion_queue_v0_1: true",
        f"status: {payload['status']}",
        f"queue_scope: {payload['queue_scope']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"required_row_count: {payload['required_row_count']}",
        f"completed_required_row_count: {payload['completed_required_row_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"queue_item_count: {payload['queue_item_count']}",
        f"source_completion_queue_html: {payload['source_completion_queue_html']}",
        f"local_static_completion_queue_html: {str(payload['local_static_completion_queue_html']).lower()}",
        f"browser_readable_completion_queue: {str(payload['browser_readable_completion_queue']).lower()}",
        f"completion_queue_visual_palette: {payload['completion_queue_visual_palette']}",
        f"local_browser_completion_csv_builder: {str(payload['local_browser_completion_csv_builder']).lower()}",
        f"browser_only_completion_csv_text_generation: {str(payload['browser_only_completion_csv_text_generation']).lower()}",
        f"completion_csv_builder_writes_files: {str(payload['completion_csv_builder_writes_files']).lower()}",
        f"completion_csv_builder_network_calls: {str(payload['completion_csv_builder_network_calls']).lower()}",
        f"completion_csv_builder_imports_workbook: {str(payload['completion_csv_builder_imports_workbook']).lower()}",
        f"grouped_by_blocker: {str(payload['grouped_by_blocker']).lower()}",
        f"grouped_by_owner_review_lane: {str(payload['grouped_by_owner_review_lane']).lower()}",
        f"target_template_count: {payload['target_template_count']}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"ready_for_existing_local_validators: {str(payload['ready_for_existing_local_validators']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_completion_queue: {payload['blockers_closed_by_completion_queue']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
        "",
        "## Purpose",
        "",
        "This queue lists the missing required human-input rows blocking the",
        "current commercial evidence sprint. It is a local coordination surface",
        "only and does not fill, copy, infer, or transfer any values.",
        "The browser page can generate CSV text from human-entered fields, but it",
        "does not save files, call a network, write the repository, or import the",
        "workbook.",
        "",
        "## Missing Required Inputs by Blocker",
        "",
        "| Blocker | Missing required inputs |",
        "| --- | ---: |",
    ]
    for blocker, count in payload["blocker_missing_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Missing Required Inputs by Target Template",
            "",
            "| Target template | Missing required inputs |",
            "| --- | ---: |",
        ]
    )
    for target, count in payload["target_missing_counts"].items():
        lines.append(f"| `{target}` | {count} |")
    lines.extend(
        [
            "",
            "## Queue",
            "",
            "| Queue ID | Workbook Row | Blocker | Input | Target Pointer |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in payload["queue_items"]:
        lines.append(
            "| {queue_item_id} | `{workbook_row_id}` | `{blocker_id}` | "
            "`{input_group}.{input_key}` | `{target_json_pointer}` |".format(**item)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No values were filled by Codex. No values were transferred. No",
            "human-filled templates were written. No validators were run on real input.",
            "No evidence was collected, no builder was executed, and no blocker was",
            "closed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    blocker_rows = "\n".join(
        "<tr>"
        f"<td><strong>{esc(BLOCKER_LABELS.get(blocker, blocker))}</strong><span>{esc(blocker)}</span></td>"
        f"<td>{count}</td>"
        "</tr>"
        for blocker, count in payload["blocker_missing_counts"].items()
    )
    lane_rows = "\n".join(
        "<tr>"
        f"<td><strong>{esc(LANE_LABELS.get(lane, lane))}</strong><span>{esc(lane)}</span></td>"
        f"<td>{count}</td>"
        "</tr>"
        for lane, count in payload["owner_lane_missing_counts"].items()
    )
    target_rows = "\n".join(
        "<tr>"
        f"<td><code>{esc(target)}</code></td>"
        f"<td>{count}</td>"
        "</tr>"
        for target, count in payload["target_missing_counts"].items()
    )
    queue_rows = "\n".join(
        "<tr>"
        f"<td>{esc(item['queue_item_id'])}</td>"
        f"<td><strong>{esc(BLOCKER_LABELS.get(item['blocker_id'], item['blocker_id']))}</strong><span>{esc(item['blocker_id'])}</span></td>"
        f"<td>{esc(LANE_LABELS.get(item['owner_review_lane'], item['owner_review_lane']))}</td>"
        f"<td><code>{esc(item['input_group'])}.{esc(item['input_key'])}</code></td>"
        f"<td><code>{esc(item['target_json_pointer'])}</code></td>"
        f"<td><textarea data-value-for=\"{esc(item['queue_item_id'])}\" aria-label=\"{esc(item['queue_item_id'])} 人工值\" placeholder=\"人类填写真实值，Codex 不代填\"></textarea></td>"
        f"<td><textarea data-note-for=\"{esc(item['queue_item_id'])}\" aria-label=\"{esc(item['queue_item_id'])} 备注\" placeholder=\"可选：记录来源或说明\"></textarea></td>"
        "</tr>"
        for item in payload["queue_items"]
    )
    boundary_items = [
        "Codex 不填写任何人工值。",
        "不把值写入模板，不转移值，不导入 workbook。",
        "本页可以在浏览器里生成 CSV 文本，但不会保存文件。",
        "不对真实输入运行 validator。",
        "不收集证据，不执行 evidence builder。",
        "不关闭 blocker，不声明生产可用。",
        "不联系客户或供应商，不发布产品。",
        "不修改 runtime、backend、kernel、API schema 或 private core。",
    ]
    boundary_html = "\n".join(f"<li>{esc(item)}</li>" for item in boundary_items)
    rows_json = json.dumps(payload["queue_items"], ensure_ascii=False).replace("</", "<\\/")
    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 商业化人工补证据队列</title>
  <style>
    :root {{
      color-scheme: light;
      --palette-name: commercial-clean-slate-mint-v1;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --panel-soft: #f0f3f1;
      --text: #111311;
      --muted: #626a65;
      --border: #dddfdb;
      --accent: #148c72;
      --accent-strong: #0f725e;
      --accent-soft: #eaf5f1;
      --danger-soft: #f6ebe8;
      --shadow: 0 18px 45px rgba(16, 18, 17, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: radial-gradient(circle at 20% 0%, rgba(20, 140, 114, 0.1) 0, rgba(20, 140, 114, 0) 34%), var(--bg);
      color: var(--text);
      line-height: 1.65;
    }}
    main {{
      width: min(1180px, calc(100% - 40px));
      margin: 0 auto;
      padding: 48px 0 64px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.4fr 0.8fr;
      gap: 24px;
      align-items: stretch;
      margin-bottom: 24px;
    }}
    .panel {{
      background: rgba(255,255,255,0.92);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 24px;
    }}
    h1 {{
      margin: 0 0 14px;
      font-size: clamp(32px, 5vw, 56px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    p {{ margin: 0 0 14px; color: var(--muted); }}
    .status {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: var(--danger-soft);
      color: #8e3c33;
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 16px;
    }}
    .status::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #9a3d34;
    }}
    .facts {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .fact {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      background: var(--panel-soft);
    }}
    .fact strong {{
      display: block;
      font-size: 26px;
      line-height: 1.1;
      margin-bottom: 6px;
    }}
    .fact span {{ color: var(--muted); font-size: 13px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 20px;
      margin: 20px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      border-radius: 14px;
      background: var(--panel);
      border: 1px solid var(--border);
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{
      color: var(--muted);
      background: #f8fafc;
      font-weight: 700;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    td span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 2px;
    }}
    code {{
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      color: var(--accent-strong);
      word-break: break-all;
    }}
    .next {{
      background: var(--accent-soft);
      border-color: #cfe5de;
    }}
    .boundary {{
      background: #111318;
      color: white;
      border-color: #111318;
    }}
    .boundary p, .boundary li {{ color: #d7dce5; }}
    .boundary ul {{
      margin: 0;
      padding-left: 20px;
    }}
    .queue-table {{
      max-height: 720px;
      overflow: auto;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: var(--panel);
    }}
    .queue-table table {{ border: 0; border-radius: 0; }}
    textarea {{
      width: min(260px, 100%);
      min-height: 76px;
      resize: vertical;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 10px;
      color: var(--text);
      background: #ffffff;
      font: inherit;
      line-height: 1.45;
    }}
    textarea:focus {{
      outline: 2px solid rgba(20, 140, 114, 0.22);
      border-color: var(--accent);
    }}
    .tools {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 14px 0;
    }}
    button {{
      min-height: 40px;
      border: 0;
      border-radius: 10px;
      padding: 0 14px;
      color: white;
      background: #111318;
      font-weight: 800;
      cursor: pointer;
    }}
    button.secondary {{
      color: var(--text);
      background: var(--panel-soft);
      border: 1px solid var(--border);
    }}
    .csv-output {{
      width: 100%;
      min-height: 220px;
      margin-top: 10px;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      white-space: pre;
    }}
    .meta {{
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }}
    .meta div {{
      padding: 10px 12px;
      border-radius: 12px;
      background: #f8fafc;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 820px) {{
      main {{ width: min(100% - 24px, 1180px); padding-top: 28px; }}
      .hero, .grid, .facts {{ grid-template-columns: 1fr; }}
      .panel {{ padding: 18px; border-radius: 14px; }}
      th, td {{ padding: 10px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="panel">
        <div class="status">暂停：等待人工补证据</div>
        <h1>SAEE 商业化人工补证据队列</h1>
        <p>这页只告诉人类还缺哪些必填值。它不替你编值、不写模板、不跑真实验证，也不关闭任何商业化 blocker。</p>
        <div class="meta">
          <div>状态标记：<code>commercial_sprint_human_input_completion_queue_v0_1=true</code></div>
          <div>填写位置：<code>{esc(payload['source_workbook_csv'])}</code> 的 <code>human_value_placeholder</code> 列</div>
          <div>下一步：人类填写真实值后，再运行 workbook validator。</div>
          <div>本页工具：本地生成 CSV 文本；不联网、不保存文件、不写入仓库、不导入 workbook。</div>
        </div>
      </div>
      <aside class="panel">
        <h2>当前数值</h2>
        <div class="facts">
          <div class="fact"><strong>{payload['missing_required_row_count']}</strong><span>缺失必填值</span></div>
          <div class="fact"><strong>{payload['selected_blocker_count']}</strong><span>本轮 blocker</span></div>
          <div class="fact"><strong>{payload['target_template_count']}</strong><span>目标模板</span></div>
          <div class="fact"><strong>{payload['blockers_closed_by_completion_queue']}</strong><span>已关闭 blocker</span></div>
        </div>
      </aside>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>按 blocker 看</h2>
        <table>
          <thead><tr><th>Blocker</th><th>缺失值</th></tr></thead>
          <tbody>{blocker_rows}</tbody>
        </table>
      </div>
      <div class="panel">
        <h2>按负责人线看</h2>
        <table>
          <thead><tr><th>负责人线</th><th>缺失值</th></tr></thead>
          <tbody>{lane_rows}</tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>会写入哪些目标模板</h2>
      <table>
        <thead><tr><th>目标模板</th><th>缺失值</th></tr></thead>
        <tbody>{target_rows}</tbody>
      </table>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>64 个待人工填写项</h2>
      <p>可以先在本页录入，点击“生成 CSV 文本”后复制结果，再由人类决定是否回填到 workbook CSV。页面不会保存或发送任何内容。</p>
      <div class="tools">
        <button type="button" id="build-csv">生成 CSV 文本</button>
        <button type="button" class="secondary" id="clear-inputs">清空页面输入</button>
      </div>
      <textarea class="csv-output" id="csv-output" readonly placeholder="点击“生成 CSV 文本”后，这里会出现 64 行 CSV 文本。"></textarea>
      <div class="queue-table">
        <table>
          <thead><tr><th>编号</th><th>Blocker</th><th>负责人线</th><th>字段</th><th>目标 JSON 指针</th><th>人工值</th><th>备注</th></tr></thead>
          <tbody>{queue_rows}</tbody>
        </table>
      </div>
    </section>

    <section class="panel next" style="margin-top: 20px;">
      <h2>人工下一步</h2>
      <p>{esc(payload['next_human_action'])}</p>
    </section>

    <section class="panel boundary" style="margin-top: 20px;">
      <h2>边界</h2>
      <ul>{boundary_html}</ul>
    </section>
  </main>
  <script type="application/json" id="completion-queue-json">{rows_json}</script>
  <script>
    (function () {{
      const rows = JSON.parse(document.getElementById("completion-queue-json").textContent);
      const output = document.getElementById("csv-output");
      const csvColumns = [
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "human_value_placeholder",
        "notes_for_human"
      ];
      function csvCell(value) {{
        const text = String(value || "");
        if (/[",\\n\\r]/.test(text)) {{
          return '"' + text.replace(/"/g, '""') + '"';
        }}
        return text;
      }}
      function valueFor(row, suffix) {{
        const field = document.querySelector(`[data-${{suffix}}-for="${{row.queue_item_id}}"]`);
        return field ? field.value.trim() : "";
      }}
      function buildCsv() {{
        const lines = [csvColumns.join(",")];
        rows.forEach((row) => {{
          const values = {{
            queue_item_id: row.queue_item_id,
            workbook_row_id: row.workbook_row_id,
            blocker_id: row.blocker_id,
            owner_review_lane: row.owner_review_lane,
            input_group: row.input_group,
            input_key: row.input_key,
            input_kind: row.input_kind,
            human_value_placeholder: valueFor(row, "value"),
            notes_for_human: valueFor(row, "note")
          }};
          lines.push(csvColumns.map((column) => csvCell(values[column])).join(","));
        }});
        output.value = lines.join("\\n");
      }}
      function clearInputs() {{
        document.querySelectorAll("textarea[data-value-for], textarea[data-note-for]").forEach((field) => {{
          field.value = "";
        }});
        output.value = "";
      }}
      document.getElementById("build-csv").addEventListener("click", buildCsv);
      document.getElementById("clear-inputs").addEventListener("click", clearInputs);
    }})();
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(html_doc, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Completion Queue Boundary Audit",
        "",
        "commercial_sprint_human_input_completion_queue_v0_1: true",
        f"status: {payload['status']}",
        f"queue_scope: {payload['queue_scope']}",
        f"queue_item_count: {payload['queue_item_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"source_completion_queue_html: {payload['source_completion_queue_html']}",
        f"local_static_completion_queue_html: {str(payload['local_static_completion_queue_html']).lower()}",
        f"browser_readable_completion_queue: {str(payload['browser_readable_completion_queue']).lower()}",
        f"completion_queue_visual_palette: {payload['completion_queue_visual_palette']}",
        f"local_browser_completion_csv_builder: {str(payload['local_browser_completion_csv_builder']).lower()}",
        f"browser_only_completion_csv_text_generation: {str(payload['browser_only_completion_csv_text_generation']).lower()}",
        f"completion_csv_builder_writes_files: {str(payload['completion_csv_builder_writes_files']).lower()}",
        f"completion_csv_builder_network_calls: {str(payload['completion_csv_builder_network_calls']).lower()}",
        f"completion_csv_builder_imports_workbook: {str(payload['completion_csv_builder_imports_workbook']).lower()}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blocker_closure_authorized: {str(payload['blocker_closure_authorized']).lower()}",
        f"blockers_closed_by_completion_queue: {payload['blockers_closed_by_completion_queue']}",
        f"runtime_modified: {str(payload['runtime_modified']).lower()}",
        f"backend_modified: {str(payload['backend_modified']).lower()}",
        f"kernel_modified: {str(payload['kernel_modified']).lower()}",
        f"api_schema_modified: {str(payload['api_schema_modified']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        "",
        "This queue is local and read-only with respect to product behavior. It",
        "does not authorize evidence collection, execution, blocker closure,",
        "customer or vendor contact, launch, or production-readiness claims.",
        "The browser CSV builder generates text only in the local browser. It",
        "does not save files, call network services, write the repository, or",
        "import the workbook.",
    ]
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Completion Queue v0.1",
        "",
        "commercial_sprint_human_input_completion_queue_v0_1: true",
        f"status: {payload['status']}",
        f"queue_scope: {payload['queue_scope']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"queue_item_count: {payload['queue_item_count']}",
        f"source_completion_queue_html: {payload['source_completion_queue_html']}",
        f"local_static_completion_queue_html: {str(payload['local_static_completion_queue_html']).lower()}",
        f"browser_readable_completion_queue: {str(payload['browser_readable_completion_queue']).lower()}",
        f"completion_queue_visual_palette: {payload['completion_queue_visual_palette']}",
        f"local_browser_completion_csv_builder: {str(payload['local_browser_completion_csv_builder']).lower()}",
        f"browser_only_completion_csv_text_generation: {str(payload['browser_only_completion_csv_text_generation']).lower()}",
        f"completion_csv_builder_writes_files: {str(payload['completion_csv_builder_writes_files']).lower()}",
        f"completion_csv_builder_network_calls: {str(payload['completion_csv_builder_network_calls']).lower()}",
        f"completion_csv_builder_imports_workbook: {str(payload['completion_csv_builder_imports_workbook']).lower()}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_completion_queue: {payload['blockers_closed_by_completion_queue']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        "",
        "## Role",
        "",
        "This is the current missing-input queue for the commercial evidence",
        "sprint. It turns the workbook validation hold into an operator-readable",
        "list of required cells that a human must fill.",
        "",
        "## Non-Execution Boundary",
        "",
        "The queue does not fill values, transfer values, write human-filled",
        "templates, run validators on real input, collect evidence, execute",
        "builders, close blockers, contact customers or vendors, launch product,",
        "or claim production readiness.",
        "Its browser CSV builder is local text generation only and does not save",
        "files, call network services, write the repository, or import the",
        "workbook.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Completion Queue Recommendation Gate",
        "",
        "commercial_sprint_human_input_completion_queue_v0_1: true",
        "answer: recommend",
        "recommend_for_missing_input_coordination: true",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
        "",
        "## Reason",
        "",
        "A potential buyer-facing commercialization workflow needs the team to",
        "close real production evidence gaps. This queue is recommendable only as",
        "a coordination layer because it identifies missing required human inputs",
        "without fabricating evidence or changing product behavior.",
        "",
        "## Status",
        "",
        f"status: {payload['status']}",
        f"queue_scope: {payload['queue_scope']}",
        f"queue_item_count: {payload['queue_item_count']}",
        f"source_completion_queue_html: {payload['source_completion_queue_html']}",
        f"local_static_completion_queue_html: {str(payload['local_static_completion_queue_html']).lower()}",
        f"browser_readable_completion_queue: {str(payload['browser_readable_completion_queue']).lower()}",
        f"completion_queue_visual_palette: {payload['completion_queue_visual_palette']}",
        f"local_browser_completion_csv_builder: {str(payload['local_browser_completion_csv_builder']).lower()}",
        f"browser_only_completion_csv_text_generation: {str(payload['browser_only_completion_csv_text_generation']).lower()}",
        f"completion_csv_builder_writes_files: {str(payload['completion_csv_builder_writes_files']).lower()}",
        f"completion_csv_builder_network_calls: {str(payload['completion_csv_builder_network_calls']).lower()}",
        f"completion_csv_builder_imports_workbook: {str(payload['completion_csv_builder_imports_workbook']).lower()}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_completion_queue: {payload['blockers_closed_by_completion_queue']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        "",
        "## Boundary",
        "",
        "This gate does not approve value transfer, evidence collection, builder",
        "execution, blocker closure, launch, or production-readiness claims.",
        "The browser CSV builder is recommendable only as a local human-entry",
        "convenience layer; it does not save files, call network services, write",
        "the repository, or import the workbook.",
    ]
    GATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_COMPLETION_QUEUE: PASS "
        f"status={payload['status']} "
        f"queue_item_count={payload['queue_item_count']} "
        f"missing_required_row_count={payload['missing_required_row_count']} "
        f"values_transferred={str(payload['values_transferred']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
