#!/usr/bin/env python3
"""Generate a local static workbench for human customer-validation entry.

The workbench is a local-only HTML helper. It lets a human copy structured JSON
after a real external customer or target-user session, but it does not submit,
upload, infer, contact customers, run validators, close blockers, or claim
production readiness.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
WORKBENCH_HTML = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.html"
WORKBENCH_SUMMARY = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.local.json"
WORKBENCH_REPORT = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.md"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_WORKBENCH_GATE.md"


BOUNDARY_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted_by_codex": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_builder_executed": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_workbench": 0,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_review_checkboxes(review: dict[str, Any]) -> str:
    rows = []
    for key in review:
        label = key.replace("_", " ")
        rows.append(
            f'<label class="check"><input type="checkbox" data-review="{html.escape(key)}"> '
            f"<span>{html.escape(label)}</span></label>"
        )
    return "\n".join(rows)


def render_html(template: dict[str, Any]) -> str:
    template_json = json.dumps(template, ensure_ascii=False, indent=2)
    review = template.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    review_checkboxes = render_review_checkboxes(review)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 客户验证录入工作台</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #171717;
      --muted: #66645f;
      --line: #dedbd2;
      --accent: #0f6b57;
      --accent-soft: #e5f1ed;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.55;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }}
    h1 {{ font-size: clamp(28px, 4vw, 48px); line-height: 1.05; margin: 0 0 12px; }}
    h2 {{ font-size: 20px; margin: 0 0 12px; }}
    p {{ margin: 0 0 12px; color: var(--muted); }}
    .notice {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 10px;
      padding: 14px 16px;
      margin-top: 16px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 0.85fr);
      gap: 18px;
      align-items: start;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 18px;
    }}
    .fields {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    label span {{ display: block; font-size: 13px; color: var(--muted); margin-bottom: 4px; }}
    input, textarea, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 11px;
      font: inherit;
      background: #fff;
      color: var(--ink);
    }}
    textarea {{ min-height: 88px; resize: vertical; }}
    .full {{ grid-column: 1 / -1; }}
    .checks {{
      display: grid;
      gap: 8px;
      margin-top: 8px;
    }}
    .check {{
      display: flex;
      gap: 8px;
      align-items: flex-start;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      background: #fff;
    }}
    .check input {{ width: auto; margin-top: 4px; }}
    .check span {{ margin: 0; color: var(--ink); }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 16px 0;
    }}
    button {{
      border: 0;
      border-radius: 999px;
      padding: 10px 14px;
      font: inherit;
      background: var(--ink);
      color: white;
      cursor: pointer;
    }}
    button.secondary {{ background: var(--accent-soft); color: var(--accent); }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #111;
      color: #f6f6f0;
      padding: 14px;
      border-radius: 10px;
      min-height: 360px;
      font-size: 12px;
    }}
    .status {{
      color: var(--warn);
      font-size: 13px;
      margin-top: 8px;
    }}
    @media (max-width: 860px) {{
      .grid, .fields {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>SAEE 客户验证录入工作台</h1>
    <p>把一次真实客户或目标用户访谈结果，整理成 SAEE 现有验证器可以读取的 JSON。</p>
    <div class="notice">
      这个页面只在本地工作，不上传、不提交、不联网。生成 JSON 后，需要人工保存为
      <code>external_customer_validation_session_entry.human_filled.local.json</code>，
      再运行导入器。它不会让 SAEE 变成生产可用，也不会自动关闭客户验证 blocker。
    </div>
  </header>

  <div class="grid">
    <section class="panel">
      <h2>1. 填写访谈信息</h2>
      <div class="fields">
        <label><span>会话编号</span><input id="session_id" placeholder="例如 CV-001"></label>
        <label><span>访谈日期</span><input id="session_date" placeholder="YYYY-MM-DD"></label>
        <label><span>受访者角色</span><input id="participant_role" placeholder="例如 创始人 / 产品负责人 / 技术负责人"></label>
        <label><span>团队类型</span><input id="team_type" placeholder="例如 AI 应用团队 / 策略团队"></label>
        <label class="full"><span>当前怎么评估 agent / workflow / policy</span><textarea id="current_evaluation_method"></textarea></label>
        <label><span>候选方案数量</span><input id="candidate_count" type="number" min="1" value="1"></label>
        <label><span>理解分数 1-5</span><input id="understanding_score" type="number" min="1" max="5"></label>
        <label><span>信任分数 1-5</span><input id="trust_score" type="number" min="1" max="5"></label>
        <label><span>决策影响分数 1-5</span><input id="decision_influence_score" type="number" min="1" max="5"></label>
        <label><span>愿意重复使用分数 1-5</span><input id="repeat_usage_intent_score" type="number" min="1" max="5"></label>
        <label><span>看到价值所需分钟数</span><input id="time_to_value_minutes" type="number" min="0"></label>
        <label><span>是否愿意测试自己的候选方案</span><select id="willing_to_test_own_candidates"><option value="">请选择</option><option value="true">是</option><option value="false">否</option></select></label>
        <label class="full"><span>最大顾虑</span><textarea id="top_objection"></textarea></label>
        <label class="full"><span>还缺什么证据</span><textarea id="evidence_missing"></textarea></label>
        <label class="full"><span>备注</span><textarea id="notes"></textarea></label>
      </div>

      <h2 style="margin-top:20px">2. 人工确认边界</h2>
      <div class="checks">
        <label class="check"><input id="no_secrets_collected" type="checkbox"> <span>没有收集密钥或敏感凭据</span></label>
        <label class="check"><input id="no_production_data_collected" type="checkbox"> <span>没有收集生产数据</span></label>
        <label class="check"><input id="no_customer_data_uploaded" type="checkbox"> <span>没有让客户上传私有数据</span></label>
        <label class="check"><input id="no_private_core_disclosed" type="checkbox"> <span>没有披露 SAEE 私有核心</span></label>
        <label class="check"><input id="no_production_ready_claim_made" type="checkbox"> <span>没有声称 SAEE 已生产可用</span></label>
      </div>

      <h2 style="margin-top:20px">3. 证据 review 勾选</h2>
      <p>只有真实访谈中确实完成的项才能勾选。不要为了通过验证而补造。</p>
      <div class="checks">{review_checkboxes}</div>

      <h2 style="margin-top:20px">4. 人工审核</h2>
      <div class="fields">
        <label><span>审核人</span><input id="human_reviewer_name"></label>
        <label><span>审核日期</span><input id="review_date" placeholder="YYYY-MM-DD"></label>
        <label class="full"><span>证据来源说明</span><textarea id="human_source_context" placeholder="说明这次访谈如何进行，结果来自哪里。"></textarea></label>
        <label class="check full"><input id="human_entry_confirmed" type="checkbox"> <span>我确认这是人工根据真实外部客户或目标用户反馈填写的记录。</span></label>
      </div>
    </section>

    <aside class="panel">
      <h2>生成 JSON</h2>
      <p>点击生成后，复制右侧内容并保存到指定 human-filled 文件。这个页面不会替你写入仓库。</p>
      <div class="actions">
        <button type="button" onclick="generateJson()">生成 JSON</button>
        <button class="secondary" type="button" onclick="copyJson()">复制</button>
        <button class="secondary" type="button" onclick="downloadJson()">下载</button>
      </div>
      <pre id="output"></pre>
      <div id="status" class="status"></div>
    </aside>
  </div>
</main>
<script>
const baseTemplate = {template_json};

function value(id) {{
  return document.getElementById(id).value.trim();
}}
function boolValue(id) {{
  return document.getElementById(id).checked;
}}
function numberValue(id) {{
  const raw = value(id);
  return raw === "" ? null : Number(raw);
}}
function selectBool(id) {{
  const raw = value(id);
  if (raw === "true") return true;
  if (raw === "false") return false;
  return null;
}}
function buildPayload() {{
  const payload = JSON.parse(JSON.stringify(baseTemplate));
  payload.human_entry_confirmed = boolValue("human_entry_confirmed");
  payload.human_reviewer_name = value("human_reviewer_name");
  payload.review_date = value("review_date");
  payload.human_source_context = value("human_source_context");
  payload.session.session_id = value("session_id");
  payload.session.session_date = value("session_date");
  payload.session.participant_role = value("participant_role");
  payload.session.team_type = value("team_type");
  payload.session.current_evaluation_method = value("current_evaluation_method");
  payload.session.candidate_count = numberValue("candidate_count") || 0;
  payload.session.understanding_score = numberValue("understanding_score");
  payload.session.trust_score = numberValue("trust_score");
  payload.session.decision_influence_score = numberValue("decision_influence_score");
  payload.session.repeat_usage_intent_score = numberValue("repeat_usage_intent_score");
  payload.session.time_to_value_minutes = numberValue("time_to_value_minutes");
  payload.session.top_objection = value("top_objection");
  payload.session.evidence_missing = value("evidence_missing");
  payload.session.willing_to_test_own_candidates = selectBool("willing_to_test_own_candidates");
  payload.session.notes = value("notes");
  payload.session.boundary_flags.secrets_collected = !boolValue("no_secrets_collected");
  payload.session.boundary_flags.production_data_collected = !boolValue("no_production_data_collected");
  payload.session.boundary_flags.customer_data_uploaded = !boolValue("no_customer_data_uploaded");
  payload.session.boundary_flags.private_core_disclosed = !boolValue("no_private_core_disclosed");
  payload.session.boundary_flags.production_ready_claim_made = !boolValue("no_production_ready_claim_made");
  payload.boundary_confirmation.no_secrets_collected = boolValue("no_secrets_collected");
  payload.boundary_confirmation.no_production_data_collected = boolValue("no_production_data_collected");
  payload.boundary_confirmation.no_customer_data_uploaded = boolValue("no_customer_data_uploaded");
  payload.boundary_confirmation.no_private_core_disclosed = boolValue("no_private_core_disclosed");
  payload.boundary_confirmation.no_production_ready_claim_made = boolValue("no_production_ready_claim_made");
  document.querySelectorAll("[data-review]").forEach((input) => {{
    payload.evidence_review[input.dataset.review] = input.checked;
  }});
  return payload;
}}
function generateJson() {{
  const output = JSON.stringify(buildPayload(), null, 2);
  document.getElementById("output").textContent = output;
  document.getElementById("status").textContent = "已生成。请人工保存，再运行 importer --apply。";
  return output;
}}
async function copyJson() {{
  const output = generateJson();
  try {{
    await navigator.clipboard.writeText(output);
    document.getElementById("status").textContent = "已复制到剪贴板。";
  }} catch (err) {{
    document.getElementById("status").textContent = "浏览器禁止复制，请手动选择复制。";
  }}
}}
function downloadJson() {{
  const output = generateJson();
  const blob = new Blob([output + "\\n"], {{type: "application/json"}});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "external_customer_validation_session_entry.human_filled.local.json";
  link.click();
  URL.revokeObjectURL(url);
}}
generateJson();
</script>
</body>
</html>
"""


def build_summary(template: dict[str, Any]) -> dict[str, Any]:
    review = template.get("evidence_review", {})
    return {
        "external_customer_validation_session_entry_workbench_v0_1": True,
        "status": "local_static_human_entry_workbench_ready",
        "workbench_type": "local_static_manual_entry_helper",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_template": rel(ENTRY_TEMPLATE),
        "workbench_html": rel(WORKBENCH_HTML),
        "target_human_filled_file": rel(
            EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
        ),
        "html_has_form": True,
        "download_json_helper": True,
        "copy_json_helper": True,
        "review_checkbox_count": len(review) if isinstance(review, dict) else 0,
        "human_action_required": True,
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        **BOUNDARY_FLAGS,
    }


def render_report(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Entry Workbench

Status: `{summary['status']}`.

This is a local static helper for a human reviewer. It converts one real
external customer or target-user session into a JSON shape that can later be
saved and imported by the existing session-entry importer.

It does not contact customers, upload data, call external services, run
validators, execute evidence builders, close blockers, launch the product, or
claim production readiness.

```yaml
external_customer_validation_session_entry_workbench_v0_1: true
status: {summary['status']}
workbench_html: {summary['workbench_html']}
review_checkbox_count: {summary['review_checkbox_count']}
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_workbench: 0
```

## How To Use

1. Open `{summary['workbench_html']}` locally in a browser.
2. Fill it after a real external customer or target-user session.
3. Download or copy the generated JSON.
4. Save it as `external_customer_validation_session_entry.human_filled.local.json`.
5. Run `python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply`.

The importer and later validators still do not authorize a public customer
validation claim by themselves.
"""


def render_boundary(summary: dict[str, Any]) -> str:
    lines = [
        "# SAEE External Customer Validation Session Entry Workbench Boundary Audit",
        "",
        f"Final boundary decision: {summary['status']}.",
        "",
        "- Local static HTML only: true",
        "- External calls made: false",
        "- External model API called: false",
        "- Customer contacted by Codex: false",
        "- Runtime modified: false",
        "- Backend modified: false",
        "- Kernel modified: false",
        "- API schema modified: false",
        "- Private core exposed: false",
        "- Customer validated: false",
        "- Production ready: false",
        "- Product launched: false",
        "- Evidence builder executed: false",
        "- Blockers closed by workbench: 0",
        "",
    ]
    return "\n".join(lines)


def render_gate(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Entry Workbench Gate

answer: {summary['status']}

reason: A local static workbench is available to reduce human JSON-entry
errors for one real external customer or target-user validation session. It is
not a customer contact tool, not an upload tool, not a validator, and not a
commercial readiness claim.

boundary:
customer_validated: false
production_ready: false
product_launched: false
customer_contacted_by_codex: false
private_core_exposed: false
external_calls_made: false
evidence_builder_executed: false
blockers_closed_by_workbench: 0

next_action: Human uses the local workbench only after a real external customer
or target-user session, then saves the generated JSON for the existing importer.
"""


def main() -> None:
    template = read_json(ENTRY_TEMPLATE)
    summary = build_summary(template)
    WORKBENCH_HTML.write_text(render_html(template), encoding="utf-8")
    write_json(WORKBENCH_SUMMARY, summary)
    WORKBENCH_REPORT.write_text(render_report(summary), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary(summary), encoding="utf-8")
    GATE.write_text(render_gate(summary), encoding="utf-8")
    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_ENTRY_WORKBENCH: PASS "
        "status=local_static_human_entry_workbench_ready "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
