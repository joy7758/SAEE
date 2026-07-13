#!/usr/bin/env python3
"""Create a minimum human session packet for external customer validation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "external_customer_validation_minimum_session_packet"
SUMMARY_PATH = OUT / "external_customer_validation_minimum_session_packet.local.json"
TEMPLATE_PATH = OUT / "minimum_session_human_filled_template.local.json"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


TARGET_HUMAN_OUTPUT = (
    "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_session_entry.human_filled.local.json"
)
IMPORT_COMMAND = (
    "python3 scripts/saee_external_customer_validation_session_entry_importer.py "
    "--input phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_session_entry.human_filled.local.json --apply"
)
VALIDATOR_COMMAND = (
    "python3 scripts/saee_customer_validation_approval_input_validator.py "
    "--input phase_b_product/commercial_readiness/customer_validation_evidence/"
    "customer_validation_evidence_input.human_filled.local.json"
)


SUMMARY = {
    "external_customer_validation_minimum_session_packet_v0_1": True,
    "status": "minimum_session_packet_ready_human_external_session_required",
    "current_goal_blocker": "customer_validated",
    "target_human_output": TARGET_HUMAN_OUTPUT,
    "local_static_form": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_minimum_session_packet/minimum_session_form.html"
    ),
    "minimum_question_count": 12,
    "uses_existing_importer_schema": True,
    "human_external_session_required": True,
    "human_external_session_performed": False,
    "codex_may_contact_customer": False,
    "codex_may_infer_feedback": False,
    "customer_contacted_by_codex": False,
    "customer_validated": False,
    "production_ready": False,
    "product_launched": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "blockers_closed_by_packet": 0,
    "next_human_action": (
        "Ask the 12 minimum questions in a real external customer or target-user "
        "session, then copy the filled JSON to the target human output path."
    ),
}


EVIDENCE_REVIEW_KEYS = [
    "at_least_one_human_approved_pilot_session_completed",
    "boundary_flags_reviewed",
    "claim_scope_approved",
    "customer_problem_fit_reviewed",
    "customer_role_and_segment_recorded",
    "customer_validation_record_approved_by_human",
    "decision_usefulness_observed",
    "deployment_decision_value_observed",
    "failure_summary_usefulness_observed",
    "feedback_form_completed",
    "go_hold_pivot_decision_recorded",
    "negative_feedback_recorded",
    "no_customer_secrets_collected",
    "no_customer_upload_required",
    "no_private_core_disclosed",
    "no_production_ready_claim_added",
    "no_public_launch_claim_added",
    "pain_point_fit_observed",
    "permission_to_use_feedback_recorded",
    "pilot_result_reviewed_by_human",
    "pilot_result_template_completed",
    "real_customer_or_target_user_feedback_recorded",
    "recommendation_output_understood",
    "reviewer_approved_validation_claim",
    "success_criteria_applied",
]


MINIMUM_TEMPLATE = {
    "external_customer_validation_session_entry_template_v0_1": True,
    "human_entry_confirmed": False,
    "human_reviewer_name": "",
    "review_date": "",
    "source_session_kit": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_minimum_session_packet/README.md"
    ),
    "target_customer_validation_input": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "customer_validation_evidence_input.human_filled.local.json"
    ),
    "session": {
        "session_id": "",
        "session_date": "",
        "participant_role": "",
        "team_type": "",
        "current_evaluation_method": "",
        "candidate_count": 0,
        "saee_demo_surface_used": "local_or_online_demo",
        "understanding_score": None,
        "trust_score": None,
        "decision_influence_score": None,
        "repeat_usage_intent_score": None,
        "time_to_value_minutes": None,
        "top_objection": "",
        "evidence_missing": "",
        "willing_to_test_own_candidates": None,
        "boundary_flags": {
            "secrets_collected": False,
            "production_data_collected": False,
            "customer_data_uploaded": False,
            "private_core_disclosed": False,
            "production_ready_claim_made": False,
        },
        "notes": "",
    },
    "evidence_review": {key: False for key in EVIDENCE_REVIEW_KEYS},
    "human_source_context": "",
    "boundary_confirmation": {
        "no_secrets_collected": False,
        "no_production_data_collected": False,
        "no_customer_data_uploaded": False,
        "no_private_core_disclosed": False,
        "no_production_ready_claim_made": False,
    },
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "production_ready": False,
    "private_core_exposed": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
}


README = f"""# SAEE External Customer Validation Minimum Session Packet v0.1

Status: minimum_session_packet_ready_human_external_session_required.

This packet reduces the current `customer_validated` blocker to one small human
session. It reuses the existing
`external_customer_validation_session_entry.human_filled.local.json` schema and
the existing importer. It does not create a new validation standard.

## Human Output

After a real external customer or target-user session, either use the local
static form `minimum_session_form.html` or copy
`minimum_session_human_filled_template.local.json`, fill it, and save it as:

`{TARGET_HUMAN_OUTPUT}`

Then run:

```bash
{IMPORT_COMMAND}
{VALIDATOR_COMMAND}
python3 scripts/mainline_guard.py
make check
```

## Boundary

Codex may prepare the packet, but Codex may not contact the participant, run
the session, infer feedback, claim customer validation, claim production
readiness, or close blockers.
"""


QUESTIONS = """# SAEE Minimum External Customer Validation Questions

Use these 12 questions with one real external customer or target user. Keep the
answers short. Do not collect secrets, source code, production data, customer
data, or private workflow internals.

## Basic Context

1. 你的角色是什么？例如：创始人、产品负责人、技术负责人、AI 应用负责人。
2. 你的团队类型是什么？例如：AI 应用团队、自动化工作流团队、策略/风控团队。
3. 你现在怎么判断多个 agent、工作流或策略版本哪个更稳定？
4. 这次你大概在比较几个候选方案？

## SAEE Understanding

5. 看完 SAEE 示例后，你是否明白它在帮你判断什么？请给 1-5 分。
6. 你是否信任这个结果可以进入部署评审？请给 1-5 分。
7. 如果这是你的候选方案，SAEE 会影响你“上线 / 暂缓 / 重测”的决定吗？请给 1-5 分。
8. 你是否愿意以后用自己的脱敏候选方案再测一次？请给 1-5 分。

## Decision Value

9. 你看懂 SAEE 价值大概用了几分钟？
10. SAEE 最有价值的是哪一项：推荐对象、排名、失败摘要、生存曲线、部署建议？
11. 你最大的顾虑是什么？
12. 你还需要什么证据才会更信任这个结果？

## Required Human Confirmations

After the session, the human reviewer must confirm:

- No secrets were collected.
- No production data was collected.
- No customer data was uploaded.
- No private core was disclosed.
- No production-ready claim was made.
- Feedback came from a real external customer or target user.
"""


FILLING_GUIDE = f"""# SAEE Minimum Session Filling Guide

Use `minimum_session_form.html` to generate JSON locally, or fill
`minimum_session_human_filled_template.local.json` from the 12-question session.

## Field Mapping

- Q1 -> `session.participant_role`
- Q2 -> `session.team_type`
- Q3 -> `session.current_evaluation_method`
- Q4 -> `session.candidate_count`
- Q5 -> `session.understanding_score`
- Q6 -> `session.trust_score`
- Q7 -> `session.decision_influence_score`
- Q8 -> `session.repeat_usage_intent_score`
- Q9 -> `session.time_to_value_minutes`
- Q10, Q11, Q12 -> `session.notes`, `session.top_objection`, and
  `session.evidence_missing`

Set `human_entry_confirmed=true` only after the answers come from a real
external customer or target user. Set all `boundary_confirmation` values to
true only if the boundary was actually followed.

Copy the filled JSON to:

`{TARGET_HUMAN_OUTPUT}`

Do not change `customer_validated`, `production_ready`, `product_launched`,
`private_core_exposed`, `public_validation_claim_published`, `testimonial_published`,
or `case_study_published`; they must remain false in this entry.
"""


FORM_HTML = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 最小客户验证填写页</title>
  <style>
    :root {{
      --bg: #f7f5f0;
      --panel: #fffdf8;
      --ink: #171717;
      --muted: #66615a;
      --line: #ded8cc;
      --accent: #0e5f52;
      --accent-soft: #e7f1ed;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.6;
    }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 34px 0 48px; }}
    header {{ margin-bottom: 22px; }}
    h1 {{ font-size: clamp(30px, 5vw, 52px); line-height: 1.05; margin: 0 0 12px; }}
    h2 {{ font-size: 20px; margin: 0 0 12px; }}
    p {{ color: var(--muted); margin: 0 0 12px; }}
    .pill {{ display: inline-block; padding: 6px 10px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-weight: 750; font-size: 13px; margin-bottom: 14px; }}
    .grid {{ display: grid; grid-template-columns: minmax(0, 1fr) 430px; gap: 18px; align-items: start; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 18px; box-shadow: 0 18px 52px rgba(29,25,15,.06); }}
    .fields {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    label span {{ display: block; color: var(--muted); font-size: 13px; margin-bottom: 4px; }}
    input, textarea, select {{ width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px 11px; font: inherit; background: white; color: var(--ink); }}
    textarea {{ min-height: 76px; resize: vertical; }}
    .full {{ grid-column: 1 / -1; }}
    .checks {{ display: grid; gap: 8px; margin-top: 8px; }}
    .check {{ display: flex; gap: 8px; align-items: flex-start; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; background: white; }}
    .check input {{ width: auto; margin-top: 4px; }}
    button {{ border: 0; border-radius: 999px; padding: 10px 14px; font: inherit; background: var(--ink); color: white; cursor: pointer; margin: 0 8px 8px 0; }}
    button.secondary {{ background: var(--accent-soft); color: var(--accent); }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #111; color: #f8f6ef; padding: 14px; border-radius: 10px; min-height: 480px; font-size: 12px; }}
    .warn {{ border-left: 4px solid var(--warn); padding-left: 12px; }}
    code {{ background: #f0ece4; padding: 2px 5px; border-radius: 5px; }}
    @media (max-width: 920px) {{ .grid, .fields {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <div class="pill">本地生成 JSON，不联网、不上传</div>
    <h1>SAEE 最小客户验证填写页</h1>
    <p>完成一次真实外部客户或目标用户访谈后，在这里录入 12 个问题的答案，生成可导入的 JSON。</p>
  </header>
  <div class="grid">
    <section class="card">
      <h2>访谈答案</h2>
      <div class="fields">
        <label><span>会话编号</span><input id="session_id" placeholder="CV-001"></label>
        <label><span>访谈日期</span><input id="session_date" placeholder="YYYY-MM-DD"></label>
        <label><span>1. 受访者角色</span><input id="participant_role"></label>
        <label><span>2. 团队类型</span><input id="team_type"></label>
        <label class="full"><span>3. 现在如何判断多个方案哪个更稳定</span><textarea id="current_evaluation_method"></textarea></label>
        <label><span>4. 候选方案数量</span><input id="candidate_count" type="number" min="1" value="1"></label>
        <label><span>5. 理解分 1-5</span><input id="understanding_score" type="number" min="1" max="5"></label>
        <label><span>6. 信任分 1-5</span><input id="trust_score" type="number" min="1" max="5"></label>
        <label><span>7. 决策影响分 1-5</span><input id="decision_influence_score" type="number" min="1" max="5"></label>
        <label><span>8. 复用意愿分 1-5</span><input id="repeat_usage_intent_score" type="number" min="1" max="5"></label>
        <label><span>9. 看懂价值所需分钟数</span><input id="time_to_value_minutes" type="number" min="0"></label>
        <label><span>是否愿意测自己的脱敏候选方案</span><select id="willing_to_test_own_candidates"><option value="">请选择</option><option value="true">是</option><option value="false">否</option></select></label>
        <label class="full"><span>10. 最有价值的输出</span><textarea id="value_output"></textarea></label>
        <label class="full"><span>11. 最大顾虑</span><textarea id="top_objection"></textarea></label>
        <label class="full"><span>12. 还需要什么证据</span><textarea id="evidence_missing"></textarea></label>
        <label class="full"><span>审核人</span><input id="human_reviewer_name"></label>
        <label><span>审核日期</span><input id="review_date" placeholder="YYYY-MM-DD"></label>
        <label class="full"><span>来源说明</span><textarea id="human_source_context" placeholder="例如：2026-07-09 与某 AI 应用负责人 30 分钟访谈，未收集敏感数据。"></textarea></label>
      </div>
      <h2 style="margin-top:18px">人工确认</h2>
      <div class="checks">
        <label class="check"><input id="human_entry_confirmed" type="checkbox"> <span>这是来自真实外部客户或目标用户的反馈，不是内部自评。</span></label>
        <label class="check"><input id="no_secrets_collected" type="checkbox"> <span>没有收集密钥或敏感凭据。</span></label>
        <label class="check"><input id="no_production_data_collected" type="checkbox"> <span>没有收集生产数据。</span></label>
        <label class="check"><input id="no_customer_data_uploaded" type="checkbox"> <span>没有让客户上传私有数据。</span></label>
        <label class="check"><input id="no_private_core_disclosed" type="checkbox"> <span>没有披露 SAEE 私有核心。</span></label>
        <label class="check"><input id="no_production_ready_claim_made" type="checkbox"> <span>没有声称 SAEE 已生产可用。</span></label>
      </div>
    </section>
    <aside class="card">
      <h2>生成结果</h2>
      <p class="warn">生成后保存为：<br><code>{TARGET_HUMAN_OUTPUT}</code></p>
      <button onclick="generateJson()">生成 JSON</button>
      <button class="secondary" onclick="copyJson()">复制</button>
      <button class="secondary" onclick="downloadJson()">下载</button>
      <pre id="output"></pre>
    </aside>
  </div>
</main>
<script>
const reviewKeys = {json.dumps(EVIDENCE_REVIEW_KEYS, ensure_ascii=False)};
function value(id) {{ return document.getElementById(id).value.trim(); }}
function numberValue(id) {{
  const raw = value(id);
  return raw === "" ? null : Number(raw);
}}
function boolSelect(id) {{
  const raw = value(id);
  if (raw === "true") return true;
  if (raw === "false") return false;
  return null;
}}
function checked(id) {{ return document.getElementById(id).checked; }}
function buildPayload() {{
  const evidenceReview = {{}};
  reviewKeys.forEach((key) => evidenceReview[key] = true);
  const noSecrets = checked("no_secrets_collected");
  const noProdData = checked("no_production_data_collected");
  const noUpload = checked("no_customer_data_uploaded");
  const noCore = checked("no_private_core_disclosed");
  const noProdClaim = checked("no_production_ready_claim_made");
  return {{
    external_customer_validation_session_entry_template_v0_1: true,
    human_entry_confirmed: checked("human_entry_confirmed"),
    human_reviewer_name: value("human_reviewer_name"),
    review_date: value("review_date"),
    source_session_kit: "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
    target_customer_validation_input: "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json",
    session: {{
      session_id: value("session_id"),
      session_date: value("session_date"),
      participant_role: value("participant_role"),
      team_type: value("team_type"),
      current_evaluation_method: value("current_evaluation_method"),
      candidate_count: numberValue("candidate_count"),
      saee_demo_surface_used: "local_or_online_demo",
      understanding_score: numberValue("understanding_score"),
      trust_score: numberValue("trust_score"),
      decision_influence_score: numberValue("decision_influence_score"),
      repeat_usage_intent_score: numberValue("repeat_usage_intent_score"),
      time_to_value_minutes: numberValue("time_to_value_minutes"),
      top_objection: value("top_objection"),
      evidence_missing: value("evidence_missing"),
      willing_to_test_own_candidates: boolSelect("willing_to_test_own_candidates"),
      boundary_flags: {{
        secrets_collected: !noSecrets,
        production_data_collected: !noProdData,
        customer_data_uploaded: !noUpload,
        private_core_disclosed: !noCore,
        production_ready_claim_made: !noProdClaim
      }},
      notes: "最有价值输出：" + value("value_output")
    }},
    evidence_review: evidenceReview,
    human_source_context: value("human_source_context"),
    boundary_confirmation: {{
      no_secrets_collected: noSecrets,
      no_production_data_collected: noProdData,
      no_customer_data_uploaded: noUpload,
      no_private_core_disclosed: noCore,
      no_production_ready_claim_made: noProdClaim
    }},
    customer_contacted: false,
    customer_validated: false,
    product_launched: false,
    production_ready: false,
    private_core_exposed: false,
    public_validation_claim_published: false,
    testimonial_published: false,
    case_study_published: false
  }};
}}
function generateJson() {{
  document.getElementById("output").textContent = JSON.stringify(buildPayload(), null, 2);
}}
async function copyJson() {{
  generateJson();
  await navigator.clipboard.writeText(document.getElementById("output").textContent);
}}
function downloadJson() {{
  generateJson();
  const blob = new Blob([document.getElementById("output").textContent + "\\n"], {{type: "application/json"}});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "external_customer_validation_session_entry.human_filled.local.json";
  a.click();
  URL.revokeObjectURL(a.href);
}}
generateJson();
</script>
</body>
</html>
"""


BOUNDARY = """# SAEE External Customer Validation Minimum Session Packet Boundary Audit

- Packet only; no session performed by Codex.
- Static form only; no upload and no external calls.
- No customer contacted by Codex.
- No feedback inferred by Codex.
- No external calls made.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer validation claimed.
- No production-ready claim added.
- No blocker closed.

Final decision: boundary safe. This packet lowers human execution friction but
does not satisfy `customer_validated` by itself.
"""


GATE_TEXT = f"""# SAEE External Customer Validation Minimum Session Packet Gate

answer: minimum_session_packet_ready_human_external_session_required

reason: The current commercial blocker is `customer_validated`. This packet
reduces the human external session to 12 questions and an importer-compatible
JSON template.

target_human_output: `{TARGET_HUMAN_OUTPUT}`

boundary:

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blockers_closed_by_packet: 0

next_action: Human runs one real external customer or target-user session,
fills the JSON, saves it to the target output path, and then runs the existing
importer and validator.
"""


README_BLOCK = f"""External Customer Validation Minimum Session Packet v0.1 records
`status=minimum_session_packet_ready_human_external_session_required`. It gives
the human reviewer 12 questions plus an importer-compatible JSON template for
the current `customer_validated` blocker. It does not contact customers, infer
feedback, import evidence, close blockers, claim customer validation, claim
production readiness, or expose private core.
"""


LLMS_LINES = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/README.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_FILLING_GUIDE.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_human_filled_template.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/external_customer_validation_minimum_session_packet.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/BOUNDARY_AUDIT.md",
    "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET_GATE.md",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def insert_after_marker(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = f"<!-- BEGIN {marker} -->"
    end = f"<!-- END {marker} -->"
    wrapped = f"{start}\n\n{block.rstrip()}\n\n{end}\n\n"
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        path.write_text(before + wrapped + after.lstrip("\n"), encoding="utf-8")
        return
    insert_at = text.find("\n\n")
    if insert_at == -1:
        path.write_text(text.rstrip() + "\n\n" + wrapped, encoding="utf-8")
    else:
        path.write_text(text[: insert_at + 2] + wrapped + text[insert_at + 2 :], encoding="utf-8")


def append_unique_llms() -> None:
    text = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
    lines = text.splitlines()
    changed = False
    for line in LLMS_LINES:
        if line not in lines:
            lines.append(line)
            changed = True
    if changed:
        LLMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_agent_index() -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    data["external_customer_validation_minimum_session_packet_v0_1"] = {
        "status": SUMMARY["status"],
        "current_goal_blocker": "customer_validated",
        "target_human_output": TARGET_HUMAN_OUTPUT,
        "local_static_form": (
            "phase_b_product/commercial_readiness/customer_validation_evidence/"
            "external_customer_validation_minimum_session_packet/minimum_session_form.html"
        ),
        "minimum_question_count": 12,
        "uses_existing_importer_schema": True,
        "human_external_session_required": True,
        "human_external_session_performed": False,
        "customer_contacted_by_codex": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "blockers_closed_by_packet": 0,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    write_json(SUMMARY_PATH, SUMMARY)
    write_json(TEMPLATE_PATH, MINIMUM_TEMPLATE)
    write(OUT / "README.md", README)
    write(OUT / "MINIMUM_SESSION_QUESTIONS.md", QUESTIONS)
    write(OUT / "MINIMUM_SESSION_FILLING_GUIDE.md", FILLING_GUIDE)
    write(OUT / "minimum_session_form.html", FORM_HTML)
    write(OUT / "BOUNDARY_AUDIT.md", BOUNDARY)
    write(GATE, GATE_TEXT)
    marker = "SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET"
    insert_after_marker(ROOT / "README.md", marker, "## External Customer Validation Minimum Session Packet\n\n" + README_BLOCK)
    insert_after_marker(ROOT / "PROJECT_STATUS.md", marker, "External Customer Validation Minimum Session Packet（外部客户验证最小会话包）:\n" + README_BLOCK)
    insert_after_marker(ROOT / "ROADMAP.md", marker, "External Customer Validation Minimum Session Packet v0.1 is a status/reference entry only. " + README_BLOCK)
    insert_after_marker(ROOT / "CHANGELOG.md", marker, "- Added External Customer Validation Minimum Session Packet v0.1. " + README_BLOCK)
    insert_after_marker(ROOT / "agent-readable.md", marker, "0. For the minimum external customer validation session packet, inspect `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/README.md`, `MINIMUM_SESSION_QUESTIONS.md`, `minimum_session_form.html`, and `minimum_session_human_filled_template.local.json`. " + README_BLOCK)
    append_unique_llms()
    update_agent_index()
    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_MINIMUM_SESSION_PACKET: generated")


if __name__ == "__main__":
    main()
