#!/usr/bin/env python3
"""Build the SAEE commercial human action board.

The board turns the existing production blocker dependency plan and evidence
collection packet into a human-action view. It does not execute work, collect
evidence, contact customers/vendors, close blockers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_human_action_board"
OUTPUT_JSON = OUTPUT_DIR / "commercial_human_action_board.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_human_action_board.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_human_action_board.csv"
OUTPUT_HTML = OUTPUT_DIR / "commercial_human_action_board.html"
OUTPUT_BOUNDARY = OUTPUT_DIR / "commercial_human_action_board_boundary_audit.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_HUMAN_ACTION_BOARD_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_HUMAN_ACTION_BOARD_RECOMMENDATION_GATE.md"

DEPENDENCY_PLAN_PATH = (
    ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
)
EVIDENCE_PACKET_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet/commercial_production_evidence_collection_packet.local.json"
)
DASHBOARD_PATH = (
    ROOT / "phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.local.json"
)
ACTIVE_HUMAN_INPUT_BOARD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_active_human_input_board.local.json"
)

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
    "blockers_closed_by_board",
    "customer_data_collected",
    "customer_data_processed",
    "payment_collected",
    "revenue_validated",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
]

BLOCKER_LABELS = {
    "support_contact": "支持联系人",
    "production_monitoring": "生产监控",
    "formal_security_review": "正式安全审查",
    "production_restore_policy": "生产恢复方案",
    "pricing_page": "价格页",
    "oauth_oidc": "企业登录",
    "production_identity_provider": "生产身份系统",
    "rbac": "权限分级",
    "tenant_storage_isolation": "租户数据隔离",
    "external_alert_delivery": "外部告警送达",
    "on_call_rotation": "值班安排",
    "restore_tested": "恢复演练",
    "customer_support": "客户支持流程",
    "data_processing_agreement": "数据处理协议",
    "privacy_legal_review": "隐私和法务审查",
    "sla": "服务承诺",
    "vulnerability_management": "漏洞管理",
    "invoice_process": "开票流程",
    "payment_provider": "支付服务商",
    "refund_policy": "退款政策",
    "tax_review": "税务审查",
    "tenant_billing_isolation": "租户账单隔离",
    "customer_validated": "客户验证",
    "pilot_results": "试点结果",
}

LANE_LABELS = {
    "commercial_finance_legal": "商业、财务与法务",
    "customer_validation": "客户验证",
    "data_operations": "数据与恢复",
    "engineering_data_security": "工程与数据安全",
    "engineering_security": "工程安全",
    "operations_engineering": "运维工程",
    "security_legal_privacy": "安全、法务与隐私",
    "support_operations": "支持运营",
}

PHASE_LABELS = {
    "phase_1_identity_and_tenant_boundary": "身份与租户边界",
    "phase_2_data_and_operations_resilience": "数据与运营韧性",
    "phase_3_support_security_legal": "支持、安全与法务",
    "phase_4_commercial_packaging_and_billing": "商业包装与收费",
    "phase_5_customer_validation_and_launch_review": "客户验证与发布审查",
}


def label_for(mapping: dict[str, str], value: Any) -> str:
    raw = str(value)
    label = mapping.get(raw)
    if not label:
        return raw
    return f"{label}（{raw}）"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def owner_lane_title(lane: str) -> str:
    return lane.replace("_", " ")


def dependency_state(blocker: dict[str, Any], closed_blockers: set[str]) -> str:
    dependencies = blocker.get("depends_on_blockers", [])
    if not dependencies:
        return "ready_for_human_review"
    if all(dep in closed_blockers for dep in dependencies):
        return "ready_for_human_review"
    return "blocked_by_open_dependencies"


def build_evidence_samples(queue: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    samples: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        blocker_id = str(row.get("blocker_id", ""))
        item = {
            "collection_record_id": row.get("collection_record_id", ""),
            "evidence_key": row.get("evidence_key", ""),
            "evidence_file_type": row.get("evidence_file_type", ""),
            "collection_status": row.get("collection_status", ""),
            "owner_review_lane": row.get("owner_review_lane", ""),
            "external_dependency_required": row.get("external_dependency_required") is True,
            "engineering_implementation_required": row.get("engineering_implementation_required") is True,
            "manual_collection_required": row.get("manual_collection_required") is True,
        }
        samples.setdefault(blocker_id, []).append(item)
    return {key: value[:3] for key, value in samples.items()}


def build_action_rows(
    dependency_plan: dict[str, Any],
    evidence_packet: dict[str, Any],
) -> list[dict[str, Any]]:
    closed_blockers: set[str] = set()
    sample_by_blocker = build_evidence_samples(evidence_packet.get("evidence_collection_queue", []))
    phase_order = {
        phase.get("phase_id"): index
        for index, phase in enumerate(dependency_plan.get("phases", []), start=1)
    }
    rows: list[dict[str, Any]] = []
    for blocker in dependency_plan.get("blockers", []):
        blocker_id = str(blocker.get("blocker_id", ""))
        evidence_samples = sample_by_blocker.get(blocker_id, [])
        depends_on = blocker.get("depends_on_blockers", [])
        rows.append(
            {
                "blocker_id": blocker_id,
                "phase_id": blocker.get("phase_id", ""),
                "phase_order": phase_order.get(blocker.get("phase_id"), 99),
                "category": blocker.get("category", ""),
                "status": blocker.get("status", "open"),
                "dependency_state": dependency_state(blocker, closed_blockers),
                "depends_on_blockers": depends_on,
                "unblocks_blockers": blocker.get("unblocks_blockers", []),
                "owner_review_lane": blocker.get("owner_review_lane", ""),
                "required_evidence": blocker.get("required_evidence", ""),
                "evidence_sample_count": len(evidence_samples),
                "first_evidence_items": evidence_samples,
                "external_dependency_required": blocker.get("external_dependency_required") is True,
                "engineering_implementation_required": blocker.get("engineering_implementation_required") is True,
                "requires_human_approval": True,
                "requires_separate_execution_request": True,
                "execution_allowed_by_board": False,
                "closure_allowed_by_board": False,
                "default_decision": "hold",
                "next_human_action": (
                    "Assign a human owner, collect or review the listed production evidence "
                    "in a separate approved request, then rerun commercial go/no-go."
                ),
                "must_not_touch": [
                    "runtime",
                    "backend",
                    "kernel",
                    "api_schema",
                    "private_core",
                    "customer_data_without_approval",
                    "payment_collection",
                    "customer_contact_without_approval",
                ],
            }
        )
    return sorted(rows, key=lambda row: (row["phase_order"], row["blocker_id"]))


def build_lane_summary(action_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lanes: dict[str, dict[str, Any]] = {}
    for row in action_rows:
        lane = str(row["owner_review_lane"])
        item = lanes.setdefault(
            lane,
            {
                "owner_review_lane": lane,
                "title": owner_lane_title(lane),
                "blocker_count": 0,
                "ready_for_human_review_count": 0,
                "blocked_by_dependency_count": 0,
                "external_dependency_count": 0,
                "engineering_implementation_count": 0,
                "blocker_ids": [],
            },
        )
        item["blocker_count"] += 1
        item["blocker_ids"].append(row["blocker_id"])
        if row["dependency_state"] == "ready_for_human_review":
            item["ready_for_human_review_count"] += 1
        else:
            item["blocked_by_dependency_count"] += 1
        if row["external_dependency_required"]:
            item["external_dependency_count"] += 1
        if row["engineering_implementation_required"]:
            item["engineering_implementation_count"] += 1
    return sorted(lanes.values(), key=lambda row: row["owner_review_lane"])


def build_active_sprint_rows(
    action_rows: list[dict[str, Any]],
    active_board: dict[str, Any],
) -> list[dict[str, Any]]:
    action_by_blocker = {str(row["blocker_id"]): row for row in action_rows}
    rows: list[dict[str, Any]] = []
    for sprint_row in active_board.get("board_rows", []):
        blocker_id = str(sprint_row.get("blocker_id", ""))
        action_row = action_by_blocker.get(blocker_id)
        if not action_row:
            continue
        rows.append(
            {
                "blocker_id": blocker_id,
                "dependency_state": action_row.get("dependency_state"),
                "owner_review_lane": action_row.get("owner_review_lane"),
                "phase_id": action_row.get("phase_id"),
                "quick_fill_row_count": int(sprint_row.get("quick_fill_row_count", 0)),
                "missing_value_row_count": int(sprint_row.get("missing_value_row_count", 0)),
                "completed_value_row_count": int(
                    sprint_row.get("completed_value_row_count", 0)
                ),
                "input_groups": sprint_row.get("input_groups", []),
                "execution_allowed_by_board": False,
                "evidence_collection_authorized": False,
                "closure_allowed_by_board": False,
                "default_decision": "hold",
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["dependency_state"] != "ready_for_human_review",
            row["missing_value_row_count"],
            row["blocker_id"],
        ),
    )


def build_board() -> dict[str, Any]:
    dependency_plan = read_json(DEPENDENCY_PLAN_PATH)
    evidence_packet = read_json(EVIDENCE_PACKET_PATH)
    dashboard = read_json(DASHBOARD_PATH)
    active_board = read_json(ACTIVE_HUMAN_INPUT_BOARD_PATH)
    action_rows = build_action_rows(dependency_plan, evidence_packet)
    ready_rows = [row for row in action_rows if row["dependency_state"] == "ready_for_human_review"]
    blocked_rows = [row for row in action_rows if row["dependency_state"] == "blocked_by_open_dependencies"]
    active_sprint_rows = build_active_sprint_rows(action_rows, active_board)
    active_sprint_ready_rows = [
        row for row in active_sprint_rows if row["dependency_state"] == "ready_for_human_review"
    ]
    board: dict[str, Any] = {
        "board_type": "saee_commercial_human_action_board",
        "board_version": "0.1",
        "board_status": "hold_human_action_required",
        "board_scope": "local_commercial_human_action_review",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_human_action_board.py",
        "source_dependency_plan": rel(DEPENDENCY_PLAN_PATH),
        "source_evidence_packet": rel(EVIDENCE_PACKET_PATH),
        "source_dashboard": rel(DASHBOARD_PATH),
        "source_active_human_input_board": rel(ACTIVE_HUMAN_INPUT_BOARD_PATH),
        "source_human_action_board_html": rel(OUTPUT_HTML),
        "local_static_human_action_board_html": True,
        "browser_readable_human_action_board": True,
        "commercial_status": dashboard.get("commercial_status", "hold"),
        "production_launch_status": dashboard.get("production_launch_status", "hold"),
        "production_blocker_count": int(dashboard.get("production_blocker_count", 24)),
        "open_blocker_count": int(dashboard.get("open_blocker_count", 24)),
        "ready_for_human_review_blocker_count": len(ready_rows),
        "blocked_by_dependency_blocker_count": len(blocked_rows),
        "active_sprint_blocker_count": len(active_sprint_rows),
        "active_sprint_ready_action_count": len(active_sprint_ready_rows),
        "active_sprint_missing_value_row_count": int(
            active_board.get("missing_value_row_count", 0)
        ),
        "owner_review_lane_count": len(build_lane_summary(action_rows)),
        "total_required_evidence_item_count": int(
            dashboard.get("total_required_evidence_item_count", 149)
        ),
        "total_local_public_shell_present_count": int(
            dashboard.get("total_local_public_shell_present_count", 37)
        ),
        "total_missing_production_evidence_count": int(
            dashboard.get("total_missing_production_evidence_count", 112)
        ),
        "blockers_closed_by_board": 0,
        "blockers_ready_to_close": [],
        "human_review_required": True,
        "manual_collection_required": True,
        "separate_execution_approval_required": True,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "customer_data_collected": False,
        "customer_data_processed": False,
        "payment_collected": False,
        "revenue_validated": False,
        "production_claim_added": False,
        "launch_claim_added": False,
        "customer_validation_claim_added": False,
        "owner_lane_summary": build_lane_summary(action_rows),
        "active_sprint_action_rows": active_sprint_rows,
        "action_rows": action_rows,
        "next_human_action": (
            "Review ready_for_human_review rows, assign human owners, and open "
            "separate approved evidence-collection or implementation requests."
        ),
    }
    return board


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(board: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "blocker_id",
        "phase_id",
        "category",
        "dependency_state",
        "owner_review_lane",
        "depends_on_blockers",
        "external_dependency_required",
        "engineering_implementation_required",
        "evidence_sample_count",
        "execution_allowed_by_board",
        "closure_allowed_by_board",
        "default_decision",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in board["action_rows"]:
            writer.writerow(
                {
                    **{field: row.get(field, "") for field in fields},
                    "depends_on_blockers": ";".join(row.get("depends_on_blockers", [])),
                }
            )


def html_escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def write_html(board: dict[str, Any]) -> None:
    lane_cards = []
    for lane in board["owner_lane_summary"]:
        lane_cards.append(
            f"""
            <article class="lane-card">
              <h3>{html_escape(label_for(LANE_LABELS, lane["owner_review_lane"]))}</h3>
              <p><strong>{lane["blocker_count"]}</strong> 个阻塞项</p>
              <p>可审查：{lane["ready_for_human_review_count"]}；被依赖卡住：{lane["blocked_by_dependency_count"]}</p>
            </article>
            """
        )

    sprint_rows = []
    for row in board["active_sprint_action_rows"]:
        sprint_rows.append(
            f"""
            <tr>
              <td><strong>{html_escape(label_for(BLOCKER_LABELS, row["blocker_id"]))}</strong></td>
              <td>{html_escape(label_for(LANE_LABELS, row["owner_review_lane"]))}</td>
              <td>{html_escape(row["missing_value_row_count"])}</td>
              <td>{'可审查' if row["dependency_state"] == "ready_for_human_review" else '被依赖卡住'}</td>
              <td>{bool_text(row["execution_allowed_by_board"])}</td>
              <td>{bool_text(row["closure_allowed_by_board"])}</td>
            </tr>
            """
        )

    action_rows = []
    for row in board["action_rows"]:
        sample_ids = ", ".join(
            html_escape(item["collection_record_id"])
            for item in row["first_evidence_items"]
        )
        action_rows.append(
            f"""
            <tr>
              <td>{html_escape(label_for(BLOCKER_LABELS, row["blocker_id"]))}</td>
              <td>{html_escape(label_for(PHASE_LABELS, row["phase_id"]))}</td>
              <td>{'可审查' if row["dependency_state"] == "ready_for_human_review" else '被依赖卡住'}</td>
              <td>{html_escape(label_for(LANE_LABELS, row["owner_review_lane"]))}</td>
              <td>{sample_ids}</td>
              <td>{html_escape(row["default_decision"])}</td>
            </tr>
            """
        )

    boundary_items = [
        ("production_ready", board["production_ready"]),
        ("product_launched", board["product_launched"]),
        ("customer_validated", board["customer_validated"]),
        ("execution_authorized", board["execution_authorized"]),
        ("evidence_collection_authorized", board["evidence_collection_authorized"]),
        ("blockers_closed_by_board", board["blockers_closed_by_board"]),
        ("runtime_modified", board["runtime_modified"]),
        ("backend_modified", board["backend_modified"]),
        ("kernel_modified", board["kernel_modified"]),
        ("api_schema_modified", board["api_schema_modified"]),
        ("private_core_exposed", board["private_core_exposed"]),
    ]
    boundary_html = "\n".join(
        f"<li><strong>{html_escape(key)}:</strong> {html_escape(bool_text(value) if isinstance(value, bool) else value)}</li>"
        for key, value in boundary_items
    )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 商用人工动作板</title>
  <style>
    :root {{
      --bg: #f8f7f2;
      --text: #171717;
      --muted: #5f675f;
      --line: #dedbd2;
      --card: #fffdf8;
      --accent: #10a37f;
      --accent-soft: #e5f3ed;
      --warn: #8a5a10;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 8% 4%, rgba(16, 163, 127, 0.14), transparent 28rem),
        linear-gradient(135deg, #fffdf8 0%, var(--bg) 62%, #edf4ef 100%);
      color: var(--text);
      line-height: 1.55;
    }}
    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 42px 0 56px;
    }}
    .hero {{
      display: grid;
      gap: 22px;
      padding: 34px 0 22px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      color: var(--accent);
      font-weight: 700;
      letter-spacing: 0;
    }}
    h1 {{
      max-width: 760px;
      margin: 0;
      font-size: clamp(32px, 6vw, 72px);
      line-height: 1.02;
      letter-spacing: 0;
    }}
    .hero p {{
      max-width: 760px;
      margin: 0;
      color: var(--muted);
      font-size: 18px;
    }}
    .stats, .lanes {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 28px 0;
    }}
    .stat, .lane-card, section {{
      background: rgba(255, 253, 248, 0.86);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 18px;
      box-shadow: 0 18px 45px rgba(23, 23, 23, 0.06);
    }}
    .stat strong {{
      display: block;
      font-size: 34px;
      line-height: 1;
      color: var(--accent);
    }}
    .stat span, .lane-card p {{
      color: var(--muted);
      font-size: 14px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    h3 {{ margin: 0 0 8px; font-size: 16px; }}
    section {{ margin: 26px 0; overflow-x: auto; }}
    table {{
      width: 100%;
      min-width: 760px;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 700;
      background: rgba(229, 243, 237, 0.55);
    }}
    .notice {{
      background: var(--accent-soft);
      border: 1px solid rgba(16, 163, 127, 0.28);
    }}
    .warning {{
      background: #fff6df;
      border-color: #ead59a;
      color: var(--warn);
    }}
    ul {{ margin: 10px 0 0; padding-left: 20px; }}
    code {{
      background: rgba(23, 23, 23, 0.06);
      border-radius: 6px;
      padding: 2px 6px;
    }}
  </style>
</head>
<body>
  <main>
    <header class="hero">
      <div class="eyebrow">SAEE 商用准备</div>
      <h1>先把能人工处理的阻塞项排清楚。</h1>
      <p>这个页面把当前 24 个正式商用阻塞项放在一张人工动作板里。它只帮助人审和分派，不执行任务、不收集证据、不关闭阻塞项。</p>
    </header>

    <div class="stats">
      <div class="stat"><strong>{board['open_blocker_count']}</strong><span>仍未关闭的商用阻塞项</span></div>
      <div class="stat"><strong>{board['ready_for_human_review_blocker_count']}</strong><span>现在可以进入人工审查</span></div>
      <div class="stat"><strong>{board['active_sprint_blocker_count']}</strong><span>当前 sprint 优先处理项</span></div>
      <div class="stat"><strong>{board['active_sprint_missing_value_row_count']}</strong><span>当前缺少的人工填写值</span></div>
    </div>

    <section class="notice">
      <h2>人现在该做什么</h2>
      <p>先看“当前 sprint”的 5 项，给每项指定真人负责人。需要收集证据或改系统时，必须另开一个明确批准的请求。</p>
      <p>建议优先处理：支持联系人、生产监控、正式安全审查、生产恢复方案、价格页。</p>
    </section>

    <section>
      <h2>当前 sprint：先处理这 5 项</h2>
      <table>
        <thead>
          <tr>
            <th>阻塞项</th>
            <th>负责人方向</th>
            <th>缺少人工值</th>
            <th>依赖状态</th>
            <th>允许执行</th>
            <th>允许关闭</th>
          </tr>
        </thead>
        <tbody>{''.join(sprint_rows)}</tbody>
      </table>
    </section>

    <section>
      <h2>负责人方向</h2>
      <div class="lanes">{''.join(lane_cards)}</div>
    </section>

    <section>
      <h2>全部 24 个阻塞项</h2>
      <table>
        <thead>
          <tr>
            <th>阻塞项</th>
            <th>阶段</th>
            <th>依赖状态</th>
            <th>负责人方向</th>
            <th>证据样例</th>
            <th>默认决策</th>
          </tr>
        </thead>
        <tbody>{''.join(action_rows)}</tbody>
      </table>
    </section>

    <section class="warning">
      <h2>边界</h2>
      <p>这个页面不是正式商用批准，也不是执行授权。</p>
      <ul>{boundary_html}</ul>
    </section>
  </main>
</body>
</html>
"""
    OUTPUT_HTML.write_text(html_text, encoding="utf-8")


def write_markdown(board: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Human Action Board",
        "",
        "Status: hold_human_action_required.",
        "",
        "This board converts the current commercial blocker dependency plan and",
        "production evidence collection queue into a human-owner action view.",
        "It does not execute work, collect evidence, close blockers, contact",
        "customers/vendors, launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- production_blocker_count: {board['production_blocker_count']}",
        f"- open_blocker_count: {board['open_blocker_count']}",
        f"- ready_for_human_review_blocker_count: {board['ready_for_human_review_blocker_count']}",
        f"- blocked_by_dependency_blocker_count: {board['blocked_by_dependency_blocker_count']}",
        f"- active_sprint_blocker_count: {board['active_sprint_blocker_count']}",
        f"- active_sprint_ready_action_count: {board['active_sprint_ready_action_count']}",
        f"- active_sprint_missing_value_row_count: {board['active_sprint_missing_value_row_count']}",
        f"- owner_review_lane_count: {board['owner_review_lane_count']}",
        f"- total_required_evidence_item_count: {board['total_required_evidence_item_count']}",
        f"- total_missing_production_evidence_count: {board['total_missing_production_evidence_count']}",
        f"- blockers_closed_by_board: {board['blockers_closed_by_board']}",
        f"- execution_authorized: {str(board['execution_authorized']).lower()}",
        f"- evidence_collection_authorized: {str(board['evidence_collection_authorized']).lower()}",
        f"- production_ready: {str(board['production_ready']).lower()}",
        f"- local_static_human_action_board_html: {str(board['local_static_human_action_board_html']).lower()}",
        f"- browser_readable_human_action_board: {str(board['browser_readable_human_action_board']).lower()}",
        f"- source_human_action_board_html: {board['source_human_action_board_html']}",
        "",
        "## Owner Lane Summary",
        "",
        "| Owner lane | Blockers | Ready | Blocked | External dep | Engineering impl |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for lane in board["owner_lane_summary"]:
        lines.append(
            "| {owner_review_lane} | {blocker_count} | {ready_for_human_review_count} | "
            "{blocked_by_dependency_count} | {external_dependency_count} | "
            "{engineering_implementation_count} |".format(**lane)
        )
    lines.extend(
        [
            "",
            "## Active Sprint Ready Actions",
            "",
            "These rows come from the current commercial sprint quick-fill board.",
            "They are listed separately so a human can see the immediate sprint",
            "scope before opening any separate execution or evidence request.",
            "",
            "| Blocker | Dependency state | Owner lane | Missing quick-fill values | Execution allowed | Closure allowed |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in board["active_sprint_action_rows"]:
        lines.append(
            f"| {row['blocker_id']} | {row['dependency_state']} | "
            f"{row['owner_review_lane']} | {row['missing_value_row_count']} | "
            f"{str(row['execution_allowed_by_board']).lower()} | "
            f"{str(row['closure_allowed_by_board']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Action Rows",
            "",
            "| Blocker | Phase | Dependency state | Owner lane | First evidence items |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in board["action_rows"]:
        samples = ", ".join(item["collection_record_id"] for item in row["first_evidence_items"])
        lines.append(
            f"| {row['blocker_id']} | {row['phase_id']} | {row['dependency_state']} | "
            f"{row['owner_review_lane']} | {samples} |"
        )
    lines.extend(
        [
            "",
            "## Next Human Action",
            "",
            board["next_human_action"],
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary_audit(board: dict[str, Any]) -> None:
    lines = [
        "# Commercial Human Action Board Boundary Audit",
        "",
        "- runtime_modified: false",
        "- backend_modified: false",
        "- kernel_modified: false",
        "- api_schema_modified: false",
        "- private_core_exposed: false",
        "- product_launched: false",
        "- production_ready: false",
        "- customer_validated: false",
        "- customer_contacted: false",
        "- public_sdk_released: false",
        "- external_calls_made: false",
        "- external_model_api_called: false",
        "- external_ai_assistant_tested: false",
        "- task_candidates_executed: false",
        "- development_permission_granted: false",
        "- execution_authorized: false",
        "- evidence_collection_authorized: false",
        "- blockers_closed_by_board: 0",
        "",
        "Final boundary decision: local human-action planning only.",
    ]
    OUTPUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme() -> None:
    README_PATH.write_text(
        "\n".join(
            [
                "# Commercial Human Action Board",
                "",
                "Status: local human-action board, hold, no execution.",
                "",
                "This directory contains a generated owner-lane action board over",
                "the current 24 commercial production blockers. It is intended to",
                "help humans decide what evidence or implementation request to open",
                "next.",
                "",
                "It does not authorize execution, evidence collection, customer",
                "contact, vendor contact, product launch, production-ready claims,",
                "customer-validation claims, or blocker closure.",
                "",
                "Files:",
                "",
                "- `commercial_human_action_board.local.json`",
                "- `commercial_human_action_board.html`",
                "- `commercial_human_action_board.md`",
                "- `commercial_human_action_board.csv`",
                "- `commercial_human_action_board_boundary_audit.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_doc(board: dict[str, Any]) -> None:
    DOC_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Human Action Board v0.1",
                "",
                "commercial_human_action_board_v0_1: true",
                "board_scope: local_commercial_human_action_review",
                "status: hold_human_action_required",
                f"production_blocker_count: {board['production_blocker_count']}",
                f"open_blocker_count: {board['open_blocker_count']}",
                f"ready_for_human_review_blocker_count: {board['ready_for_human_review_blocker_count']}",
                f"blocked_by_dependency_blocker_count: {board['blocked_by_dependency_blocker_count']}",
                f"active_sprint_blocker_count: {board['active_sprint_blocker_count']}",
                f"active_sprint_ready_action_count: {board['active_sprint_ready_action_count']}",
                f"active_sprint_missing_value_row_count: {board['active_sprint_missing_value_row_count']}",
                f"blockers_closed_by_board: {board['blockers_closed_by_board']}",
                "local_static_human_action_board_html: true",
                "browser_readable_human_action_board: true",
                f"source_human_action_board_html: {board['source_human_action_board_html']}",
                "execution_authorized: false",
                "evidence_collection_authorized: false",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "",
                "## Purpose",
                "",
                "This board converts the existing dependency plan and production",
                "evidence queue into a human-owner action surface. It helps humans",
                "see which blockers are ready for review and which remain blocked by",
                "open dependencies.",
                "",
                "## Boundary",
                "",
                "The board is planning-only. It does not execute tasks, collect",
                "evidence, contact customers or vendors, close blockers, modify",
                "runtime/backend/kernel/API schema/private core, launch product, or",
                "claim production readiness.",
                "",
                "## Browser-Readable Entry",
                "",
                f"`{board['source_human_action_board_html']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_gate(board: dict[str, Any]) -> None:
    GATE_PATH.write_text(
        "\n".join(
            [
                "# SAEE Commercial Human Action Board Recommendation Gate",
                "",
                "answer: conditional",
                "",
                "recommend_for_human_action_triage: true",
                "recommend_for_owner_lane_assignment: true",
                "recommend_for_automatic_execution: false",
                "recommend_for_evidence_collection_authorization: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_product_launch: false",
                "recommend_for_production_readiness_claim: false",
                "",
                "## Reason",
                "",
                "The board is useful for assigning human owners and opening separate",
                "approved evidence or implementation requests. It does not grant",
                "execution permission and does not close blockers.",
                "",
                "## Current Evidence",
                "",
                f"- production_blocker_count: {board['production_blocker_count']}",
                f"- ready_for_human_review_blocker_count: {board['ready_for_human_review_blocker_count']}",
                f"- active_sprint_blocker_count: {board['active_sprint_blocker_count']}",
                f"- active_sprint_ready_action_count: {board['active_sprint_ready_action_count']}",
                f"- active_sprint_missing_value_row_count: {board['active_sprint_missing_value_row_count']}",
                f"- blockers_closed_by_board: {board['blockers_closed_by_board']}",
                "- production_ready: false",
                "- customer_validated: false",
                "- private_core_exposed: false",
                "- local_static_human_action_board_html: true",
                f"- source_human_action_board_html: {board['source_human_action_board_html']}",
                "",
                "## Next Action",
                "",
                "Human owners may use the board to choose a blocker and then create a",
                "separate, explicit execution or evidence-intake request.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_outputs(board: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_JSON, board)
    write_csv(board)
    write_html(board)
    write_markdown(board)
    write_boundary_audit(board)
    write_readme()
    write_doc(board)
    write_gate(board)


def main() -> int:
    board = build_board()
    for flag in BOUNDARY_FALSE_FLAGS:
        if board.get(flag) not in (False, 0):
            raise SystemExit(f"SAEE_COMMERCIAL_HUMAN_ACTION_BOARD: FAIL {flag}")
    write_outputs(board)
    print(
        "SAEE_COMMERCIAL_HUMAN_ACTION_BOARD: PASS "
        f"open_blockers={board['open_blocker_count']} "
        f"ready_for_human_review={board['ready_for_human_review_blocker_count']} "
        f"blockers_closed_by_board={board['blockers_closed_by_board']} "
        f"production_ready={str(board['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
