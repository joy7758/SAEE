#!/usr/bin/env python3
"""Generate a one-page human run card for customer validation.

This card consolidates existing customer-validation surfaces into one human
path. It does not add a new validation method, contact customers, fill answers,
import evidence, write the final session-entry JSON, close blockers, or claim
production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_one_page_run_card"
SUMMARY = OUT / "customer_validation_one_page_run_card.local.json"
CARD = OUT / "customer_validation_one_page_run_card.md"
HTML = OUT / "customer_validation_one_page_run_card.html"
BOUNDARY = OUT / "customer_validation_one_page_run_card_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

REFERENCES = {
    "screening": EVIDENCE
    / "external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md",
    "invitation": EVIDENCE
    / "external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md",
    "consent": EVIDENCE
    / "external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md",
    "short_worksheet": EVIDENCE
    / "customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.md",
    "full_worksheet": EVIDENCE
    / "customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_worksheet.md",
    "answer_template": EVIDENCE
    / "customer_validation_answer_intake_helper/customer_validation_answers.template.md",
    "answer_target": EVIDENCE
    / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md",
    "preflight": EVIDENCE
    / "customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json",
    "converter": ROOT / "scripts/saee_customer_validation_answer_to_session_entry_converter.py",
    "pipeline": ROOT / "scripts/saee_customer_validation_answer_to_evidence_pipeline.py",
    "workbench": EVIDENCE / "external_customer_validation_session_entry_workbench.html",
    "target_entry": EVIDENCE / "external_customer_validation_session_entry.human_filled.local.json",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def replace_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def build_payload() -> dict[str, Any]:
    preflight = read_json(REFERENCES["preflight"])
    return {
        "customer_validation_one_page_run_card_v0_1": True,
        "card_type": "one_page_human_customer_validation_navigation",
        "status": "ready_for_human_external_customer_validation_run",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "uses_existing_materials_only": True,
        "new_questions_added": False,
        "human_execution_required": True,
        "human_answer_input_exists": REFERENCES["answer_target"].exists(),
        "target_session_entry_exists": REFERENCES["target_entry"].exists(),
        "current_preflight_status": preflight.get("status"),
        "ready_for_explicit_apply_request": False,
        "step_count": 6,
        "browser_readable_card_available": True,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
        "blockers_closed_by_run_card": 0,
        "entrypoints": {key: rel(path) for key, path in REFERENCES.items()},
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)

    CARD.write_text(
        f"""# SAEE 真实客户验证一页执行卡 v0.1

当前唯一不能由 Codex 代办的正式商用阻塞点是：`customer_validated`。

这张卡只把现有材料串成一条人工路径，不新增问题，不自动联系客户，
不导入结果，不关闭 blocker，也不声明 SAEE 已生产可用。

## 6 步人工路径

| 步骤 | 人要做什么 | 打开哪个文件 |
| --- | --- | --- |
| 1 | 先确认对方是不是目标用户 | `{rel(REFERENCES["screening"])}` |
| 2 | 人工发送邀请，不由 Codex 联系 | `{rel(REFERENCES["invitation"])}` |
| 3 | 会前说明边界：不收秘密、不收生产数据、不披露私有核心、不承诺生产可用 | `{rel(REFERENCES["consent"])}` |
| 4 | 如果时间很短，先问 3 分钟最小表 | `{rel(REFERENCES["short_worksheet"])}` |
| 5 | 会后补完整中文答卷，并保存为目标答卷文件 | `{rel(REFERENCES["full_worksheet"])}` -> `{rel(REFERENCES["answer_target"])}` |
| 6 | 跑一条本地 pipeline：它会先 preflight，再转换 JSON，再进入后处理 | `python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply` |

## 完整录入入口

如果要直接整理最终 session-entry JSON，也可以打开：

`{rel(REFERENCES["workbench"])}`

目标输出路径必须是：

`{rel(REFERENCES["target_entry"])}`

## 当前状态

- current_preflight_status: `{payload["current_preflight_status"]}`
- human_answer_input_exists: `{payload["human_answer_input_exists"]}`
- target_session_entry_exists: `{payload["target_session_entry_exists"]}`
- customer_validated: false
- production_ready: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_run_card: 0
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Customer Validation One-Page Run Card Boundary Audit

- Only one human navigation card was generated in Markdown and local static HTML.
- Existing customer-validation materials were referenced, not replaced.
- No customer was contacted by Codex.
- No external calls were made.
- No answers were filled by Codex.
- No final session-entry JSON was written.
- No customer-validation claim was made.
- No production-ready claim was made.
- No runtime, backend, kernel, API schema, landing interaction, or private core was modified.

customer_validation_one_page_run_card_v0_1: true
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_run_card: 0
""",
        encoding="utf-8",
    )

    HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 真实客户验证一页执行卡</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --surface: #ffffff;
      --text: #1f2937;
      --muted: #5f6b7a;
      --line: #dfe5ef;
      --accent: #2458d3;
      --soft: #eef3ff;
      --warn: #fff7ed;
      --warn-line: #fed7aa;
      --radius: 14px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
    }}
    main {{
      width: min(1040px, calc(100% - 32px));
      margin: 0 auto;
      padding: 36px 0 52px;
    }}
    .hero {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 18px 48px rgba(31, 41, 55, 0.08);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: clamp(28px, 4vw, 46px);
      line-height: 1.08;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    p {{ margin: 8px 0; color: var(--muted); }}
    .status {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 22px;
    }}
    .status div {{
      background: var(--soft);
      border: 1px solid #d7e2ff;
      border-radius: 12px;
      padding: 12px;
      font-size: 14px;
    }}
    .status strong {{
      display: block;
      color: var(--accent);
      font-size: 16px;
      margin-bottom: 2px;
    }}
    .steps {{
      display: grid;
      gap: 12px;
      margin-top: 16px;
    }}
    .step {{
      display: grid;
      grid-template-columns: 48px 1fr;
      gap: 14px;
      align-items: start;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 16px;
    }}
    .num {{
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      border-radius: 999px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
    }}
    .step h3 {{
      margin: 0 0 4px;
      font-size: 17px;
      letter-spacing: 0;
    }}
    code {{
      display: inline-block;
      max-width: 100%;
      padding: 2px 6px;
      border-radius: 6px;
      background: #f1f5f9;
      color: #334155;
      overflow-wrap: anywhere;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
    }}
    .path {{
      margin-top: 8px;
      color: var(--muted);
    }}
    .warning {{
      background: var(--warn);
      border: 1px solid var(--warn-line);
      border-radius: var(--radius);
      padding: 16px;
      margin-top: 20px;
    }}
    .actions {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 16px;
    }}
    .action {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 16px;
    }}
    @media (max-width: 760px) {{
      main {{ width: min(100% - 20px, 1040px); padding-top: 18px; }}
      .hero {{ padding: 22px; }}
      .status, .actions {{ grid-template-columns: 1fr; }}
      .step {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>真实客户验证，一页走完</h1>
      <p>现在不能由 Codex 代办的正式商用阻塞点只剩：让一个真实外部客户或目标用户试懂、说出反馈，并由你人工保存记录。</p>
      <p>这张卡只是本地导航，不联系客户、不填答案、不导入结果、不关闭 blocker。</p>
      <div class="status" aria-label="当前边界状态">
        <div><strong>false</strong>customer_validated</div>
        <div><strong>false</strong>production_ready</div>
        <div><strong>false</strong>product_launched</div>
        <div><strong>false</strong>private_core_exposed</div>
      </div>
    </section>

    <h2>按这 6 步做</h2>
    <section class="steps">
      <article class="step">
        <div class="num">1</div>
        <div><h3>先确认对方是不是目标用户</h3><p>适合找正在比较多个 agent、工作流或策略版本的人。</p><p class="path"><code>{rel(REFERENCES["screening"])}</code></p></div>
      </article>
      <article class="step">
        <div class="num">2</div>
        <div><h3>你人工发送邀请</h3><p>不要让 Codex 联系客户。邀请只说明体验和反馈，不承诺生产可用。</p><p class="path"><code>{rel(REFERENCES["invitation"])}</code></p></div>
      </article>
      <article class="step">
        <div class="num">3</div>
        <div><h3>会前讲清边界</h3><p>不收秘密、不收生产数据、不披露私有核心、不说已经正式上线。</p><p class="path"><code>{rel(REFERENCES["consent"])}</code></p></div>
      </article>
      <article class="step">
        <div class="num">4</div>
        <div><h3>时间短就先问 3 分钟表</h3><p>只问对方是否听懂、是否有痛点、是否愿意再用自己的候选方案试一次。</p><p class="path"><code>{rel(REFERENCES["short_worksheet"])}</code></p></div>
      </article>
      <article class="step">
        <div class="num">5</div>
        <div><h3>会后补完整中文答卷</h3><p>把真实反馈保存到人工答卷文件，不要自己编反馈。</p><p class="path"><code>{rel(REFERENCES["full_worksheet"])}</code></p><p class="path"><code>{rel(REFERENCES["answer_target"])}</code></p></div>
      </article>
      <article class="step">
        <div class="num">6</div>
        <div><h3>最后跑本地 pipeline</h3><p>只有真实人工答卷完整且边界安全时，才运行 <code>--apply</code>。它会先 preflight，再转换 JSON，再进入后处理。</p><p class="path"><code>python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply</code></p></div>
      </article>
    </section>

    <section class="actions">
      <div class="action">
        <h2>最终 JSON 录入入口</h2>
        <p>如果要直接整理 session-entry JSON，打开本地工作台：</p>
        <p><code>{rel(REFERENCES["workbench"])}</code></p>
      </div>
      <div class="action">
        <h2>必须保存到这里</h2>
        <p>后续 importer 只认这个人工填写结果文件：</p>
        <p><code>{rel(REFERENCES["target_entry"])}</code></p>
      </div>
    </section>

    <section class="warning">
      <strong>不能声称：</strong>
      <p>当前仍不能说 SAEE 已客户验证、已生产可用、已发布、已联系客户、或已经关闭商用 blocker。真实外部会话完成并通过后续审查前，这些状态都保持 false。</p>
    </section>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Customer Validation One-Page Run Card Gate

answer: ready_for_human_external_customer_validation_run

reason: The remaining `customer_validated` blocker already has many local
materials. This card reduces navigation friction by linking the existing
screening, invitation, consent, short worksheet, full worksheet, answer target,
preflight, and workbench into one human-only execution path.

boundary:
- uses_existing_materials_only: true
- new_questions_added: false
- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- blockers_closed_by_run_card: 0

next_action: A human must run a real external customer or target-user
conversation, fill the answer target, and rerun preflight.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_GATE.md",
        "/scripts/saee_customer_validation_one_page_run_card.py",
        "/scripts/saee_customer_validation_one_page_run_card_smoke.py",
    ]:
        ensure_line(LLMS, line)

    agent_index = read_json(AGENT_INDEX)
    agent_index["customer_validation_one_page_run_card_v0_1"] = {
        "name": "SAEE Customer Validation One-Page Run Card v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "uses_existing_materials_only": payload["uses_existing_materials_only"],
        "new_questions_added": payload["new_questions_added"],
        "human_execution_required": payload["human_execution_required"],
        "human_answer_input_exists": payload["human_answer_input_exists"],
        "target_session_entry_exists": payload["target_session_entry_exists"],
        "current_preflight_status": payload["current_preflight_status"],
        "ready_for_explicit_apply_request": payload["ready_for_explicit_apply_request"],
        "step_count": payload["step_count"],
        "browser_readable_card_available": payload["browser_readable_card_available"],
        "customer_validated": payload["customer_validated"],
        "production_ready": payload["production_ready"],
        "product_launched": payload["product_launched"],
        "customer_contacted_by_codex": payload["customer_contacted_by_codex"],
        "private_core_exposed": payload["private_core_exposed"],
        "runtime_modified": payload["runtime_modified"],
        "backend_modified": payload["backend_modified"],
        "kernel_modified": payload["kernel_modified"],
        "api_schema_modified": payload["api_schema_modified"],
        "external_calls_made": payload["external_calls_made"],
        "blockers_closed_by_run_card": payload["blockers_closed_by_run_card"],
        "entrypoints": {
            "summary": rel(SUMMARY),
            "card": rel(CARD),
            "html": rel(HTML),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_one_page_run_card.py",
            "smoke": "scripts/saee_customer_validation_one_page_run_card_smoke.py",
        },
        "referenced_materials": payload["entrypoints"],
    }
    write_json(AGENT_INDEX, agent_index)

    status_block = f"""## SAEE Customer Validation One-Page Run Card v0.1

- `customer_validation_one_page_run_card_v0_1`
- Status: `{payload["status"]}`
- Current blocker: `customer_validated`
- Card: `{rel(CARD)}`
- Browser card: `{rel(HTML)}`
- Human execution required: `{payload["human_execution_required"]}`
- `customer_validated=false`
- `production_ready=false`
- `private_core_exposed=false`
- `blockers_closed_by_run_card=0`
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD_V0_1", status_block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_ONE_PAGE_RUN_CARD: PASS "
        f"status={payload['status']} steps={payload['step_count']} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
