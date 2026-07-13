#!/usr/bin/env python3
"""Create a local launcher for the external customer validation session."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = BASE / "external_customer_validation_local_session_launcher"
SUMMARY_PATH = OUT / "external_customer_validation_local_session_launcher.local.json"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


SUMMARY = {
    "external_customer_validation_local_session_launcher_v0_1": True,
    "status": "local_session_launcher_ready_human_external_session_required",
    "current_goal_blocker": "customer_validated",
    "recommended_path_locked": True,
    "recommended_path_id": "minimum_session_packet",
    "recommended_path_label": "12-question minimum external customer validation session",
    "local_static_launcher": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_local_session_launcher/"
        "external_customer_validation_local_session_launcher.html"
    ),
    "online_experience_preview": "phase_b_product/landing/online-experience.html",
    "primary_action": (
        "phase_b_product/commercial_readiness/current_commercial_primary_action/"
        "current_commercial_primary_action.html"
    ),
    "facilitator": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_facilitator/external_customer_validation_facilitator.html"
    ),
    "facilitator_role": "reference_only_boundary_support",
    "minimum_session_form": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_minimum_session_packet/minimum_session_form.html"
    ),
    "minimum_session_questions": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md"
    ),
    "post_session_processor": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_post_session_processor/"
        "external_customer_validation_post_session_processor.md"
    ),
    "target_human_output": (
        "phase_b_product/commercial_readiness/customer_validation_evidence/"
        "external_customer_validation_session_entry.human_filled.local.json"
    ),
    "suggested_local_server_command": "python3 -m http.server 8876 --bind 127.0.0.1",
    "suggested_local_url": (
        "http://127.0.0.1:8876/phase_b_product/commercial_readiness/"
        "customer_validation_evidence/external_customer_validation_local_session_launcher/"
        "external_customer_validation_local_session_launcher.html"
    ),
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
    "external_model_api_called": False,
    "public_sdk_released": False,
    "blockers_closed_by_launcher": 0,
    "next_human_action": (
        "Use the locked minimum session packet to run one real external customer "
        "or target-user session, save the generated JSON, then run the "
        "post-session processor."
    ),
}


README = """# SAEE External Customer Validation Local Session Launcher v0.1

Status: local_session_launcher_ready_human_external_session_required.

This package is the one-page local entry point for running a real external
customer or target-user validation session. The recommended path is locked to
the 12-question minimum session form. The facilitator is reference-only boundary support.
It also links the current primary action, the online experience preview, and
the post-session processor.

It does not contact customers, run a session, upload data, infer feedback, close
the `customer_validated` blocker, launch the product, or claim production
readiness.

## Human Flow

1. Optionally serve the repo locally:
   `python3 -m http.server 8876 --bind 127.0.0.1`
2. Open the launcher HTML.
3. Show the participant the online experience preview.
4. Open the local minimum-session form and ask the 12 minimum validation
   questions.
5. Generate JSON from the minimum-session form.
6. Save the JSON as
   `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
7. Run the post-session processor and existing validation commands.
"""


LAUNCHER_MD = """# SAEE 外部客户验证本地会话启动器

当前阻塞点：`customer_validated`。

这个启动器把人工会话当天需要打开的材料放在一个顺序里。Codex 不会联系客户，不会替你执行访谈，也不会把本地准备状态说成客户验证完成。

## 推荐顺序

1. 打开当前商用首要动作页，确认目标仍然是获取真实外部客户或目标用户反馈。
2. 给受访者展示 `online-experience.html`，只展示体验，不收集生产数据。
3. 打开最小会话填写页，逐条问 12 个问题并记录答案。
4. 需要边界提醒时，再查看 facilitator 页面；它只是参考，不是主入口。
5. 把 JSON 保存到目标路径。
6. 运行 post-session processor。

## 不能声称

- 不能声称客户验证已经完成。
- 不能声称 SAEE 已生产可用。
- 不能声称 Codex 已联系客户。
- 不能声称私有核心已公开。
"""


HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 客户验证会话启动器</title>
  <style>
    :root {
      --bg: #f4f1eb;
      --panel: #fffdf8;
      --ink: #171717;
      --muted: #665f55;
      --line: #ddd5c8;
      --accent: #0f6b5b;
      --accent-soft: #e5f1ed;
      --warn: #8a5a00;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% 0%, rgba(15,107,91,.14), transparent 30%),
        linear-gradient(180deg, #fbfaf6 0%, var(--bg) 100%);
      color: var(--ink);
      line-height: 1.65;
    }
    main { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 42px 0 56px; }
    .pill { display: inline-flex; padding: 7px 11px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-weight: 750; font-size: 13px; }
    h1 { font-size: clamp(34px, 6vw, 64px); line-height: 1; margin: 18px 0 14px; letter-spacing: 0; max-width: 840px; }
    h2 { font-size: 22px; margin: 0 0 10px; }
    p { margin: 0 0 12px; color: var(--muted); }
    code { background: #efe9de; padding: 2px 6px; border-radius: 6px; }
    .hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 22px; align-items: stretch; margin-top: 28px; }
    .panel { background: rgba(255,253,248,.88); border: 1px solid var(--line); border-radius: 12px; padding: 22px; box-shadow: 0 18px 58px rgba(28,23,15,.07); }
    .steps { display: grid; gap: 12px; counter-reset: step; }
    .step { position: relative; padding: 16px 16px 16px 56px; border: 1px solid var(--line); border-radius: 10px; background: white; }
    .step::before {
      counter-increment: step;
      content: counter(step);
      position: absolute;
      left: 16px; top: 16px;
      width: 28px; height: 28px; border-radius: 999px;
      background: var(--ink); color: white;
      display: grid; place-items: center; font-weight: 800; font-size: 13px;
    }
    .step strong { display: block; margin-bottom: 4px; }
    a.button { display: inline-flex; align-items: center; justify-content: center; min-height: 42px; padding: 10px 16px; border-radius: 999px; text-decoration: none; background: var(--ink); color: white; font-weight: 750; margin: 4px 8px 8px 0; }
    a.button.secondary { background: var(--accent-soft); color: var(--accent); }
    .status { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .status div { border: 1px solid var(--line); border-radius: 10px; background: white; padding: 12px; }
    .status strong { display: block; font-size: 13px; color: var(--muted); }
    .status span { font-size: 18px; font-weight: 800; }
    .warn { border-left: 4px solid var(--warn); padding-left: 12px; }
    @media (max-width: 900px) { .hero, .status { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<main>
  <span class="pill">本地入口 · 人工执行 · 不联网</span>
  <h1>把一次真实客户验证会话跑顺。</h1>
  <p>这个页面只告诉你当天怎么做：展示体验、提 12 个问题、生成 JSON、再跑本地处理器。它不代表客户验证完成。</p>

  <section class="hero">
    <div class="panel">
      <h2>今天按这个顺序走</h2>
      <div class="steps">
        <div class="step"><strong>确认当前目标</strong><p>当前唯一商用阻塞点是 `customer_validated`。先打开首要动作页确认边界。</p><a class="button secondary" href="../../current_commercial_primary_action/current_commercial_primary_action.html">打开首要动作页</a></div>
        <div class="step"><strong>展示线上体验页</strong><p>给受访者看 SAEE 怎么帮助比较多个 agent、工作流或策略版本。不要收集生产数据。</p><a class="button secondary" href="../../../landing/online-experience.html">打开体验页</a></div>
        <div class="step"><strong>填写 12 个最小问题</strong><p>这是锁定的推荐路径。边问边填，结束后生成 importer 可读 JSON。</p><a class="button" href="../external_customer_validation_minimum_session_packet/minimum_session_form.html">打开 12 问填写页</a><a class="button secondary" href="../external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md">查看问题清单</a></div>
        <div class="step"><strong>必要时查看边界参考</strong><p>facilitator 只用于提醒边界：不承诺生产可用，不披露私有核心，不收集敏感资料。</p><a class="button secondary" href="../external_customer_validation_facilitator/external_customer_validation_facilitator.html">打开边界参考页</a></div>
        <div class="step"><strong>保存并处理结果</strong><p>把 JSON 保存为指定文件名，然后运行 post-session processor。</p><a class="button secondary" href="../external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.md">查看处理说明</a></div>
      </div>
    </div>
    <aside class="panel">
      <h2>状态不要越界</h2>
      <div class="status">
        <div><strong>customer_validated</strong><span>false</span></div>
        <div><strong>production_ready</strong><span>false</span></div>
        <div><strong>product_launched</strong><span>false</span></div>
        <div><strong>private_core_exposed</strong><span>false</span></div>
      </div>
      <p class="warn" style="margin-top:16px">目标输出文件：<br><code>phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json</code></p>
      <p>可选本地服务命令：</p>
      <p><code>python3 -m http.server 8876 --bind 127.0.0.1</code></p>
      <p>会后运行：</p>
      <p><code>python3 scripts/saee_external_customer_validation_post_session_processor.py</code></p>
      <p><code>python3 scripts/mainline_guard.py</code></p>
      <p><code>make check</code></p>
    </aside>
  </section>
</main>
</body>
</html>
"""


BOUNDARY = """# SAEE External Customer Validation Local Session Launcher Boundary Audit

- Only local documentation and launcher materials were created.
- No customer session was performed by Codex.
- No customer was contacted by Codex.
- No external calls were made.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer validation claimed.
- No production-ready claim added.
- No blocker closed.

Final decision: boundary safe. The launcher lowers human execution friction, but
it does not satisfy `customer_validated` by itself.
"""


GATE_TEXT = """# SAEE External Customer Validation Local Session Launcher Gate

answer: local_session_launcher_ready_human_external_session_required

reason: The current commercial blocker is `customer_validated`. This launcher
locks the recommended path to the minimum-session form, and keeps the current
primary action, online experience preview, facilitator boundary reference, and
post-session processor in one local human flow.

boundary:

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blockers_closed_by_launcher: 0
- recommended_path_locked: true
- recommended_path_id: minimum_session_packet

next_action: Human uses the minimum-session form to run one real external
customer or target-user session, saves the generated JSON to the target path,
then runs the post-session processor.
"""


README_BLOCK = """## External Customer Validation Local Session Launcher

External Customer Validation Local Session Launcher v0.1 records
`status=local_session_launcher_ready_human_external_session_required`. It
provides one local Chinese entry page for the customer-validation day. The
recommended path is locked to the 12-question minimum session form; the
facilitator is reference-only boundary support. It also links current primary
action, online experience preview, target JSON path, and post-session
processor. It does not contact
customers, run the session, infer feedback, close blockers, claim customer
validation, claim production readiness, or expose private core.
"""


AGENT_READABLE_BLOCK = """0. For the local customer validation session launcher, inspect `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.html` and `external_customer_validation_local_session_launcher.local.json`. This is the current local human session-day entry point for the `customer_validated` blocker. The recommended path is locked to the 12-question minimum session form; the facilitator is reference-only boundary support. It does not contact customers, run sessions, infer feedback, close blockers, claim customer validation, or claim production readiness.
"""


LLMS_LINES = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/README.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.html",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/BOUNDARY_AUDIT.md",
    "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER_GATE.md",
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
    data["external_customer_validation_local_session_launcher_v0_1"] = {
        "status": SUMMARY["status"],
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "local_static_launcher": SUMMARY["local_static_launcher"],
        "online_experience_preview": SUMMARY["online_experience_preview"],
        "minimum_session_form": SUMMARY["minimum_session_form"],
        "minimum_session_questions": SUMMARY["minimum_session_questions"],
        "facilitator": SUMMARY["facilitator"],
        "facilitator_role": "reference_only_boundary_support",
        "target_human_output": SUMMARY["target_human_output"],
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
        "blockers_closed_by_launcher": 0,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    write_json(SUMMARY_PATH, SUMMARY)
    write(OUT / "README.md", README)
    write(OUT / "external_customer_validation_local_session_launcher.md", LAUNCHER_MD)
    write(OUT / "external_customer_validation_local_session_launcher.html", HTML)
    write(OUT / "BOUNDARY_AUDIT.md", BOUNDARY)
    write(GATE, GATE_TEXT)

    marker = "SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER"
    insert_after_marker(ROOT / "README.md", marker, README_BLOCK)
    insert_after_marker(
        ROOT / "PROJECT_STATUS.md",
        marker,
        "External Customer Validation Local Session Launcher（外部客户验证本地会话启动器）:\n"
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "ROADMAP.md",
        marker,
        "External Customer Validation Local Session Launcher v0.1 is a status/reference entry only. "
        + README_BLOCK,
    )
    insert_after_marker(
        ROOT / "CHANGELOG.md",
        marker,
        "- Added External Customer Validation Local Session Launcher v0.1. " + README_BLOCK,
    )
    insert_after_marker(ROOT / "agent-readable.md", marker, AGENT_READABLE_BLOCK)
    append_unique_llms()
    update_agent_index()
    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_LOCAL_SESSION_LAUNCHER: generated")


if __name__ == "__main__":
    main()
