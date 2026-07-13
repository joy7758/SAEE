#!/usr/bin/env python3
"""Build a one-page local facilitator for the external customer validation session."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = BASE / "external_customer_validation_facilitator"
SUMMARY_PATH = OUT / "external_customer_validation_facilitator.local.json"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_FACILITATOR_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


SUMMARY = {
    "external_customer_validation_facilitator_v0_1": True,
    "status": "local_static_facilitator_ready_human_session_required",
    "facilitator_type": "human_external_customer_validation_session_facilitator",
    "current_goal_blocker": "customer_validated",
    "human_session_required": True,
    "human_session_performed": False,
    "human_result_entered": False,
    "required_human_output": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json",
    "codex_may_contact_customer": False,
    "codex_may_run_external_session": False,
    "codex_may_infer_customer_feedback": False,
    "customer_contacted_by_codex": False,
    "customer_validated": False,
    "production_ready": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "external_model_api_called": False,
    "backend_call_required": False,
    "runtime_execution_required": False,
    "blockers_closed_by_facilitator": 0,
    "entrypoints": {
        "facilitator_html": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.html",
        "facilitator_md": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.md",
        "workbench": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html",
        "screening": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md",
        "invitation": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md",
        "consent": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md",
        "interview_script": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_interview_script.md",
        "feedback_form": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_feedback_form.template.md",
    },
}


README = """# SAEE External Customer Validation Facilitator v0.1

Status: local_static_facilitator_ready_human_session_required.

This folder contains a local one-page facilitator for a human-run external
customer or target-user validation session. It combines the existing screening,
invitation, consent, interview, and result-entry links into one simple route.

It does not contact anyone, run the session, call a backend, execute SAEE
runtime, import evidence, close blockers, or claim customer validation.
"""


FACILITATOR_MD = """# SAEE External Customer Validation Facilitator

Current blocker: `customer_validated`.

Use this page when a human is ready to run one real external customer or
target-user session. Internal founder review is not enough.

## Session Flow

1. Screen the participant:
   `external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md`
2. Send the invitation manually:
   `external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md`
3. Read consent and boundary text before the session:
   `external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md`
4. Run the interview:
   `external_customer_validation_interview_script.md`
5. Record feedback:
   `external_customer_validation_feedback_form.template.md`
6. Enter the result:
   `external_customer_validation_session_entry_workbench.html`
7. Save the output as:
   `external_customer_validation_session_entry.human_filled.local.json`

## Import Only After Real Human Result Exists

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply
python3 scripts/saee_customer_validation_approval_input_validator.py
python3 scripts/mainline_guard.py
make check
```

## Boundary

- Codex may not contact the participant.
- Codex may not run the external session.
- Codex may not infer feedback.
- No production data, customer data, secrets, or private workflow internals.
- No production-ready claim.
- No customer-validation claim until evidence is imported and accepted.
"""


FACILITATOR_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 外部客户验证主持页</title>
  <style>
    :root {
      --bg: #f7f5f0;
      --panel: #fffdf8;
      --ink: #171717;
      --muted: #64615b;
      --line: #ded8cc;
      --accent: #0e5f52;
      --accent-soft: #e7f1ed;
      --hold: #8a5a00;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at 20% 0%, #eef4ee 0, transparent 28%),
                  radial-gradient(circle at 90% 10%, #efe8d6 0, transparent 26%),
                  var(--bg);
      color: var(--ink);
      line-height: 1.65;
    }
    main { max-width: 1040px; margin: 0 auto; padding: 42px 20px 60px; }
    header { max-width: 760px; margin-bottom: 26px; }
    h1 { font-size: clamp(30px, 5vw, 56px); line-height: 1.04; margin: 0 0 14px; letter-spacing: 0; }
    h2 { margin: 0 0 8px; font-size: 20px; }
    p { margin: 0 0 12px; color: var(--muted); }
    .pill { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-weight: 700; font-size: 13px; margin-bottom: 18px; }
    .grid { display: grid; grid-template-columns: 1fr 330px; gap: 18px; align-items: start; }
    .card { background: rgba(255,253,248,.9); border: 1px solid var(--line); border-radius: 10px; padding: 18px; box-shadow: 0 18px 60px rgba(29, 25, 15, .06); }
    .steps { display: grid; gap: 12px; }
    .step { display: grid; grid-template-columns: 54px 1fr; gap: 12px; padding: 14px; border: 1px solid var(--line); border-radius: 10px; background: #fff; }
    .num { width: 38px; height: 38px; border-radius: 50%; background: var(--ink); color: white; display: grid; place-items: center; font-weight: 800; }
    a { color: var(--accent); font-weight: 700; text-decoration: none; }
    code { background: #f0ece4; padding: 2px 5px; border-radius: 5px; overflow-wrap: anywhere; }
    .side { position: sticky; top: 18px; }
    .warn { border-left: 4px solid var(--hold); padding-left: 12px; }
    @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } .side { position: static; } }
  </style>
</head>
<body>
<main>
  <header>
    <div class="pill">当前 blocker：customer_validated</div>
    <h1>一次真实外部客户验证，按这页走。</h1>
    <p>这页只帮人工主持访谈。它不会联系客户、不会上传数据、不会运行 SAEE、不会让产品变成生产可用。</p>
  </header>
  <div class="grid">
    <section class="card">
      <h2>人工执行顺序</h2>
      <div class="steps">
        <div class="step"><div class="num">1</div><div><strong>筛选参与者</strong><p>确认对方是真实外部客户或目标用户，不是内部自评。</p><a href="../external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md">打开筛选清单</a></div></div>
        <div class="step"><div class="num">2</div><div><strong>人工发送邀请</strong><p>只发给一个合适对象；Codex 不发送。</p><a href="../external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md">打开邀请草稿</a></div></div>
        <div class="step"><div class="num">3</div><div><strong>说明同意和边界</strong><p>会前说清楚：不收源码、密钥、生产数据或客户数据。</p><a href="../external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md">打开同意脚本</a></div></div>
        <div class="step"><div class="num">4</div><div><strong>运行访谈</strong><p>让对方判断 SAEE 是否能影响部署、暂缓或重测决策。</p><a href="../external_customer_validation_interview_script.md">打开访谈脚本</a></div></div>
        <div class="step"><div class="num">5</div><div><strong>记录反馈</strong><p>记录摘要和评分，不记录敏感内容。</p><a href="../external_customer_validation_feedback_form.template.md">打开反馈表</a></div></div>
        <div class="step"><div class="num">6</div><div><strong>保存 JSON</strong><p>保存为 <code>external_customer_validation_session_entry.human_filled.local.json</code>。</p><a href="../external_customer_validation_session_entry_workbench.html">打开录入工作台</a></div></div>
      </div>
    </section>
    <aside class="card side">
      <h2>不要越界</h2>
      <div class="warn">
        <p>不要声称客户验证已完成，直到真实访谈结果被导入并通过现有 validator。</p>
        <p>不要声称生产可用。不要暴露 private core。</p>
      </div>
      <h2 style="margin-top:18px">结果文件</h2>
      <p><code>phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json</code></p>
      <h2 style="margin-top:18px">之后再运行</h2>
      <p><code>python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply</code></p>
      <p><code>python3 scripts/saee_customer_validation_approval_input_validator.py</code></p>
    </aside>
  </div>
</main>
</body>
</html>
"""


BOUNDARY = """# SAEE External Customer Validation Facilitator Boundary Audit

- Local static facilitator only.
- No customer contacted by Codex.
- No external customer session run by Codex.
- No customer feedback inferred by Codex.
- No backend call required.
- No runtime execution required.
- No evidence imported.
- No validator run on new human evidence.
- No blocker closed.
- No product launched.
- No production-ready claim added.
- No customer-validation claim added.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.

Final decision: boundary safe. The facilitator reduces human execution friction
but does not replace real external customer validation.
"""


GATE_TEXT = """# SAEE External Customer Validation Facilitator Gate

answer: local_static_facilitator_ready_human_session_required

reason: The current commercial blocker is `customer_validated`. The facilitator
puts the existing screening, invitation, consent, interview, feedback, and
entry-workbench materials into one local human-run page.

boundary:

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- codex_may_run_external_session: false
- codex_may_infer_customer_feedback: false
- backend_call_required: false
- runtime_execution_required: false
- private_core_exposed: false
- blockers_closed_by_facilitator: 0

next_action: Human opens the facilitator page and performs one real external
customer or target-user session, then saves the required human-filled JSON.
"""


STATUS_BLOCK = """## External Customer Validation Facilitator v0.1

- `external_customer_validation_facilitator_v0_1=true`
- Status: `local_static_facilitator_ready_human_session_required`.
- Purpose: one local Chinese page that links the participant screening,
  invitation, consent, interview, feedback form, and session-entry workbench for
  the remaining `customer_validated` blocker.
- Browser entrypoint:
  `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.html`.
- Boundary: `customer_validated=false`, `production_ready=false`,
  `product_launched=false`, `customer_contacted_by_codex=false`,
  `backend_call_required=false`, `runtime_execution_required=false`,
  `private_core_exposed=false`, and `blockers_closed_by_facilitator=0`.
"""


LLMS_PATHS = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/README.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.html",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/BOUNDARY_AUDIT.md",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


def update_llms() -> None:
    text = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
    missing = [p for p in LLMS_PATHS if p not in text]
    if missing:
        LLMS.write_text(text.rstrip() + "\n" + "\n".join(missing) + "\n", encoding="utf-8")


def update_agent_index() -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8")) if AGENT_INDEX.exists() else {}
    data["external_customer_validation_facilitator_v0_1"] = SUMMARY
    AGENT_INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    write(SUMMARY_PATH, json.dumps(SUMMARY, indent=2, ensure_ascii=False))
    write(OUT / "README.md", README)
    write(OUT / "external_customer_validation_facilitator.md", FACILITATOR_MD)
    write(OUT / "external_customer_validation_facilitator.html", FACILITATOR_HTML)
    write(OUT / "BOUNDARY_AUDIT.md", BOUNDARY)
    write(GATE, GATE_TEXT)
    update_llms()
    update_agent_index()
    for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        append_once(ROOT / name, "external_customer_validation_facilitator_v0_1=true", STATUS_BLOCK)
    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_FACILITATOR: READY")


if __name__ == "__main__":
    main()
