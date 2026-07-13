#!/usr/bin/env python3
"""Generate a local commercial blocker priority index.

This script reads existing commercial-readiness surfaces and creates a
human-readable priority index. It does not collect evidence, import workbooks,
close blockers, or modify product behavior.
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "commercial_blocker_priority_index"
OUT_JSON = OUT_DIR / "commercial_blocker_priority_index.local.json"
OUT_MD = OUT_DIR / "commercial_blocker_priority_index.md"
OUT_CSV = OUT_DIR / "commercial_blocker_priority_index.csv"
OUT_HTML = OUT_DIR / "commercial_blocker_priority_index.html"
OUT_AUDIT = OUT_DIR / "commercial_blocker_priority_index_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_BLOCKER_PRIORITY_INDEX_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX_V0_1.md"
AGENT_INDEX = ROOT / "agent-index.json"

STATUS_JSON = COMMERCIAL_DIR / "commercial_readiness_status.local.json"
SPRINT_JSON = (
    COMMERCIAL_DIR
    / "commercial_next_evidence_sprint/commercial_next_evidence_sprint.local.json"
)
GAP_JSON = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"

BEGIN_HERE_HTML = (
    "phase_b_product/commercial_readiness/commercial_readiness_begin_here/"
    "commercial_readiness_begin_here.html"
)
REVIEW_BATCH_TEMPLATE = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
REVIEW_BATCH_FILL_CARD = (
    "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_human_fill_card.csv"
)
POST_FILL_CHECK_COMMAND = "python3 scripts/saee_commercial_review_batch_post_fill_check.py"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bool_text(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def str_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return bool_text(value)
    return str(value)


def selected_blocker_map(sprint: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["blocker_id"]: item
        for item in sprint.get("selected_blockers", [])
        if item.get("blocker_id")
    }


def build_priority_rows(
    matrix_rows: list[dict[str, Any]],
    selected_ids: list[str],
    selected_details: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {row["blocker_id"]: row for row in matrix_rows}
    ordered_ids = [blocker_id for blocker_id in selected_ids if blocker_id in by_id]
    ordered_ids.extend(row["blocker_id"] for row in matrix_rows if row["blocker_id"] not in ordered_ids)

    rows: list[dict[str, Any]] = []
    for rank, blocker_id in enumerate(ordered_ids, start=1):
        source = by_id[blocker_id]
        selected = selected_details.get(blocker_id, {})
        if rank == 1 and blocker_id == "support_contact":
            tier = "validators_passed_pending_evidence_builder_request"
            next_action = (
                "Review the passed local validator state and decide whether to "
                "authorize a separate documentation/evidence-builder execution "
                "request. Do not collect evidence or close blockers automatically."
            )
        elif blocker_id in selected_ids:
            tier = "active_sprint_selected"
            next_action = selected.get("recommended_human_action") or source.get("next_required_action")
        else:
            tier = "open_backlog"
            next_action = source.get("next_required_action")

        rows.append(
            {
                "rank": rank,
                "blocker_id": blocker_id,
                "priority_tier": tier,
                "category": source.get("category", ""),
                "status": source.get("status", "open"),
                "owner_review_lane": selected.get("owner_review_lane")
                or source.get("owner_review_lane", ""),
                "local_completion_checks_passed": source.get("local_completion_checks_passed", 0),
                "local_completion_checks_total": source.get("local_completion_checks_total", 0),
                "engineering_implementation_required": bool(source.get("engineering_implementation_required")),
                "external_dependency_required": bool(source.get("external_dependency_required")),
                "human_approval_required": bool(source.get("human_approval_required", True)),
                "requires_separate_execution_request": bool(
                    selected.get(
                        "requires_separate_execution_request",
                        source.get("requires_separate_execution_request", True),
                    )
                ),
                "closure_allowed": False,
                "execution_allowed": False,
                "evidence_collection_allowed": False,
                "required_evidence": selected.get("required_evidence")
                or source.get("required_evidence", ""),
                "recommended_human_action": next_action,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    status = load_json(STATUS_JSON)
    sprint = load_json(SPRINT_JSON)
    gap = load_json(GAP_JSON)
    matrix_rows = gap.get("matrix", [])
    selected_ids = sprint.get("selected_blocker_ids") or [
        item["blocker_id"] for item in sprint.get("selected_blockers", [])
    ]
    selected_details = selected_blocker_map(sprint)
    priority_rows = build_priority_rows(matrix_rows, selected_ids, selected_details)
    selected_sprint_blockers = [row for row in priority_rows if row["blocker_id"] in selected_ids]

    false_boundaries = {
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
    }

    payload: dict[str, Any] = {
        "commercial_blocker_priority_index_v0_1": True,
        "index_type": "local_commercial_blocker_priority_index",
        "index_scope": "human_review_priority_only_no_execution_no_closure",
        "status": status.get("status", "ready_for_separate_evidence_builder_request"),
        "make_target": "make check-commercial-blocker-priority-index",
        "commercial_status": status.get("commercial_status", "hold"),
        "production_launch_status": "hold",
        "production_blocker_count": gap.get("production_blocker_count", 24),
        "open_blocker_count": gap.get("open_blocker_count", 24),
        "missing_value_row_count": status.get("missing_value_row_count", 64),
        "preferred_template_missing_value_row_count": status.get(
            "preferred_template_missing_value_row_count", 10
        ),
        "full_quick_fill_missing_value_row_count": status.get(
            "full_quick_fill_missing_value_row_count", 0
        ),
        "completed_value_row_count": status.get("completed_value_row_count", 64),
        "ready_for_human_fill": status.get("ready_for_human_fill", False),
        "ready_for_safety_preflight": status.get("ready_for_safety_preflight", True),
        "ready_for_workbook_import": status.get("ready_for_workbook_import", True),
        "ready_for_workbook_import_approval": status.get(
            "ready_for_workbook_import_approval", True
        ),
        "selected_blocker_count": sprint.get("selected_blocker_count", len(selected_ids)),
        "selected_blocker_ids": selected_ids,
        "first_priority_blocker_id": priority_rows[0]["blocker_id"] if priority_rows else "",
        "first_priority_tier": priority_rows[0]["priority_tier"] if priority_rows else "",
        "first_priority_reason": (
            "support_contact remains the first commercial blocker to review, but the "
            "local validator inputs are complete and all five validators pass. The "
            "next step is only a separate evidence-builder execution request review, "
            "not more data entry and not blocker closure."
        ),
        "source_status_json": str(STATUS_JSON.relative_to(ROOT)),
        "source_sprint_json": str(SPRINT_JSON.relative_to(ROOT)),
        "source_gap_matrix_json": str(GAP_JSON.relative_to(ROOT)),
        "source_begin_here_html": BEGIN_HERE_HTML,
        "source_review_batch_template_csv": REVIEW_BATCH_TEMPLATE,
        "source_review_batch_fill_card_csv": REVIEW_BATCH_FILL_CARD,
        "post_fill_check_command": POST_FILL_CHECK_COMMAND,
        "human_review_required": True,
        "next_human_action": (
            "Start with support_contact: review whether to authorize a separate "
            "documentation/evidence-builder execution request. Do not collect "
            "evidence or close blockers without a separate explicit request."
        ),
        "priority_rows": priority_rows,
        "selected_sprint_blockers": selected_sprint_blockers,
        "category_counts": gap.get("category_counts", {}),
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    payload.update(false_boundaries)
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_agent_index(payload: dict[str, Any]) -> None:
    if AGENT_INDEX.exists():
        index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
        if not isinstance(index, dict):
            raise SystemExit("SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX: FAIL agent-index must be an object")
    else:
        index = {}
    index["commercial_blocker_priority_index_v0_1"] = payload
    AGENT_INDEX.write_text(
        json.dumps(index, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "rank",
        "blocker_id",
        "priority_tier",
        "category",
        "status",
        "owner_review_lane",
        "local_completion_checks_passed",
        "local_completion_checks_total",
        "engineering_implementation_required",
        "external_dependency_required",
        "human_approval_required",
        "requires_separate_execution_request",
        "closure_allowed",
        "execution_allowed",
        "evidence_collection_allowed",
        "required_evidence",
        "recommended_human_action",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["priority_rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def render_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    visible_rows = rows if limit is None else rows[:limit]
    lines = [
        "| Rank | Blocker | Tier | Lane | Checks | Needs Engineering | Needs External Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in visible_rows:
        checks = f"{row['local_completion_checks_passed']}/{row['local_completion_checks_total']}"
        lines.append(
            "| {rank} | `{blocker}` | `{tier}` | `{lane}` | {checks} | {eng} | {ext} |".format(
                rank=row["rank"],
                blocker=row["blocker_id"],
                tier=row["priority_tier"],
                lane=row["owner_review_lane"],
                checks=checks,
                eng=bool_text(row["engineering_implementation_required"]),
                ext=bool_text(row["external_dependency_required"]),
            )
        )
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any]) -> None:
    rows = payload["priority_rows"]
    selected = payload["selected_sprint_blockers"]
    text = f"""# SAEE 商用阻塞优先级索引 v0.1

`commercial_blocker_priority_index_v0_1: true`

## 当前结论

SAEE 仍然不能正式商用。当前状态是 `status: {payload['status']}`，
`commercial_status: {payload['commercial_status']}`，`production_ready: false`。

这个索引只回答一个问题：人下一步应该先看哪个商用阻塞项。它不会填证据、
不会导入工作簿、不会联系客户、不会关闭 blocker，也不会改变产品行为。

## 当前计数

- `production_blocker_count: {payload['production_blocker_count']}`
- `open_blocker_count: {payload['open_blocker_count']}`
- `missing_value_row_count: {payload['missing_value_row_count']}`
- `preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}`
- `selected_blocker_count: {payload['selected_blocker_count']}`
- `first_priority_blocker_id: {payload['first_priority_blocker_id']}`
- `first_priority_tier: {payload['first_priority_tier']}`

## 第一优先动作

先处理 `support_contact` 的工作簿导入审批。原因：人工 quick-fill 值已经齐全，
现在需要人明确决定是否允许把这些已确认值导入商用准备工作簿。

人工入口：

- Begin-here 页面：`{payload['source_begin_here_html']}`
- 已完成 quick-fill 缺失值：`{payload['missing_value_row_count']}`
- 工作簿导入仍需单独批准：`workbook_import_authorized: false`
- 本地检查命令仍可用于状态验证：`{payload['post_fill_check_command']}`

## 当前 5 个已选 sprint 阻塞

{render_table(selected)}

## 全部 24 个开放阻塞的处理顺序

{render_table(rows)}

## 边界

- `workbook_import_authorized: false`
- `evidence_collection_authorized: false`
- `execution_authorized: false`
- `blocker_closure_authorized: false`
- `production_ready: false`
- `product_launched: false`
- `customer_validated: false`
- `customer_contacted: false`
- `runtime_modified: false`
- `backend_modified: false`
- `kernel_modified: false`
- `api_schema_modified: false`
- `private_core_exposed: false`
"""
    OUT_MD.write_text(text, encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    top_rows = payload["selected_sprint_blockers"]
    all_rows = payload["priority_rows"]

    def tr(row: dict[str, Any]) -> str:
        checks = f"{row['local_completion_checks_passed']}/{row['local_completion_checks_total']}"
        return (
            "<tr>"
            f"<td>{row['rank']}</td>"
            f"<td>{html.escape(row['blocker_id'])}</td>"
            f"<td>{html.escape(row['priority_tier'])}</td>"
            f"<td>{html.escape(row['owner_review_lane'])}</td>"
            f"<td>{html.escape(checks)}</td>"
            f"<td>{html.escape(bool_text(row['external_dependency_required']))}</td>"
            "</tr>"
        )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 商用阻塞优先级索引</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #202124; background: #f7f7f4; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 48px 20px; }}
    h1 {{ font-size: 40px; line-height: 1.1; margin: 0 0 12px; }}
    h2 {{ margin-top: 36px; }}
    p, li {{ line-height: 1.7; }}
    .status {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 28px 0; }}
    .card {{ background: white; border: 1px solid #e4e1da; border-radius: 14px; padding: 18px; box-shadow: 0 12px 40px rgba(15, 17, 21, 0.06); }}
    .label {{ color: #6f6f68; font-size: 13px; }}
    .value {{ font-size: 24px; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #e4e1da; border-radius: 14px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #eeeae3; text-align: left; }}
    th {{ background: #f0efea; }}
    code {{ background: #efede8; padding: 2px 5px; border-radius: 5px; }}
    .boundary {{ border-left: 4px solid #2b5fd9; padding-left: 16px; }}
  </style>
</head>
<body>
<main>
  <h1>SAEE 商用阻塞优先级索引</h1>
  <p>本页只告诉人工审查下一步先处理什么。它不执行任务，不导入工作簿，不关闭 blocker，也不声明 SAEE 已可正式商用。</p>
  <section class="status">
    <div class="card"><div class="label">当前状态</div><div class="value">{html.escape(payload['status'])}</div></div>
    <div class="card"><div class="label">开放阻塞</div><div class="value">{payload['open_blocker_count']}</div></div>
    <div class="card"><div class="label">缺失人工值</div><div class="value">{payload['missing_value_row_count']}</div></div>
    <div class="card"><div class="label">第一优先</div><div class="value">support_contact</div></div>
  </section>
  <section class="boundary">
    <p><strong>第一步：</strong>打开 <code>{html.escape(payload['source_begin_here_html'])}</code>，审查已完成的人工 quick-fill 值，并决定是否另行批准工作簿导入。</p>
    <p><strong>边界：</strong><code>production_ready=false</code>，<code>workbook_import_authorized=false</code>，<code>blocker_closure_authorized=false</code>。</p>
  </section>
  <h2>当前 5 个 sprint 阻塞</h2>
  <table><thead><tr><th>Rank</th><th>Blocker</th><th>Tier</th><th>Lane</th><th>Checks</th><th>External</th></tr></thead><tbody>
    {''.join(tr(row) for row in top_rows)}
  </tbody></table>
  <h2>全部 24 个开放阻塞</h2>
  <table><thead><tr><th>Rank</th><th>Blocker</th><th>Tier</th><th>Lane</th><th>Checks</th><th>External</th></tr></thead><tbody>
    {''.join(tr(row) for row in all_rows)}
  </tbody></table>
</main>
</body>
</html>
"""
    OUT_HTML.write_text(html_text, encoding="utf-8")


def write_audit(payload: dict[str, Any]) -> None:
    text = f"""# SAEE 商用阻塞优先级索引边界审计

- `commercial_blocker_priority_index_v0_1: true`
- `index_scope: {payload['index_scope']}`
- `status: {payload['status']}`
- `production_ready: false`
- `product_launched: false`
- `customer_validated: false`
- `customer_contacted: false`
- `workbook_import_authorized: false`
- `evidence_collection_authorized: false`
- `execution_authorized: false`
- `blocker_closure_authorized: false`
- `runtime_modified: false`
- `backend_modified: false`
- `kernel_modified: false`
- `api_schema_modified: false`
- `private_core_exposed: false`

本审计确认：本次只生成本地优先级索引，没有填人工值，没有生成证据，
没有运行导入，没有关闭 blocker，没有联系客户，没有发布产品，没有修改
SAEE 运行时、后端、内核、API schema 或私有核心。
"""
    OUT_AUDIT.write_text(text, encoding="utf-8")


def write_readme(payload: dict[str, Any]) -> None:
    text = f"""# Commercial Blocker Priority Index

This folder contains the local commercial blocker priority index.

- `commercial_blocker_priority_index_v0_1=true`
- `status={payload['status']}`
- `production_blocker_count={payload['production_blocker_count']}`
- `open_blocker_count={payload['open_blocker_count']}`
- `missing_value_row_count={payload['missing_value_row_count']}`
- `first_priority_blocker_id={payload['first_priority_blocker_id']}`
- `production_ready=false`
- `workbook_import_authorized=false`
- `blocker_closure_authorized=false`

This is a human-review routing surface only. Human values are complete and
local validators pass, but evidence-builder execution, workbook import, and
blocker closure still require separate explicit approval. This surface does
not execute commercial tasks, collect evidence, import workbooks, close
blockers, contact customers, or claim production readiness.
"""
    OUT_README.write_text(text, encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    text = f"""# Commercial Blocker Priority Index v0.1

- `commercial_blocker_priority_index_v0_1=true`
- `status={payload['status']}`
- `commercial_status={payload['commercial_status']}`
- `production_blocker_count={payload['production_blocker_count']}`
- `open_blocker_count={payload['open_blocker_count']}`
- `missing_value_row_count={payload['missing_value_row_count']}`
- `preferred_template_missing_value_row_count={payload['preferred_template_missing_value_row_count']}`
- `selected_blocker_count={payload['selected_blocker_count']}`
- `first_priority_blocker_id={payload['first_priority_blocker_id']}`
- `first_priority_tier={payload['first_priority_tier']}`
- `production_ready=false`
- `product_launched=false`
- `customer_validated=false`
- `workbook_import_authorized=false`
- `evidence_collection_authorized=false`
- `blocker_closure_authorized=false`

This file records a local, agent-readable ordering of commercial blockers for
human review. It is not a launch decision and does not grant execution.

Entrypoints:

- `phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.local.json`
- `phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.md`
- `phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.csv`
- `phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.html`
- `phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index_boundary_audit.md`
"""
    TOP_DOC.write_text(text, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    text = f"""# SAEE Commercial Blocker Priority Index Gate

answer: conditional

reason:
The index is recommended as a local human-review routing surface because it
clarifies the next commercial blocker to inspect without executing tasks or
changing SAEE behavior.

recommend_for_human_review_routing: true
recommend_for_product_launch: false
recommend_for_evidence_collection: false
recommend_for_workbook_import_execution: false
recommend_for_blocker_closure: false
recommend_for_production_readiness_claim: false

status: {payload['status']}
first_priority_blocker_id: {payload['first_priority_blocker_id']}
production_blocker_count: {payload['production_blocker_count']}
open_blocker_count: {payload['open_blocker_count']}
missing_value_row_count: {payload['missing_value_row_count']}
preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}

boundary:
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
production_ready: false
product_launched: false
customer_contacted: false
workbook_import_authorized: false
blocker_closure_authorized: false

next_action:
Human review starts with `support_contact` evidence-builder request review.
Any evidence collection, workbook import, or blocker closure still requires a
separate explicit human-approved request.
"""
    GATE.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(payload)
    update_agent_index(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    write_readme(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_BLOCKER_PRIORITY_INDEX: PASS "
        f"status={payload['status']} "
        f"open_blockers={payload['open_blocker_count']} "
        f"first_priority={payload['first_priority_blocker_id']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
