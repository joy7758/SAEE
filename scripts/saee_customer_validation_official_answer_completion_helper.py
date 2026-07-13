#!/usr/bin/env python3
"""Create a local completion guide for the official customer answer sheet.

This helper reduces the final manual mapping step from the 13-question live
interview to the official customer-validation answer sheet. It does not fill
customer answers, write official evidence, contact customers, run validators on
real input, or claim customer validation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_official_answer_completion_helper"
SUMMARY = OUT / "customer_validation_official_answer_completion_helper.local.json"
REPORT = OUT / "customer_validation_official_answer_completion_helper.md"
FIELD_CHECKLIST = OUT / "official_answer_sheet_field_checklist.md"
COPY_TEMPLATE = OUT / "official_answer_sheet_blank_copy_block.md"
HTML = OUT / "official_answer_sheet_completion.html"
BOUNDARY = OUT / "customer_validation_official_answer_completion_helper_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_GATE.md"
ANSWER_TEMPLATE = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.template.md"
OFFICIAL_ANSWER = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
STAGER_SUMMARY = EVIDENCE / "customer_validation_interview_answer_stager/customer_validation_interview_answer_stager.local.json"
STAGED_DRAFT = EVIDENCE / "customer_validation_interview_answer_stager/customer_validation_answers.staged_from_interview.local.md"
ANSWER_INTAKE = ROOT / "scripts/saee_customer_validation_answer_intake_helper.py"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]


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


def parse_answer_template() -> tuple[list[str], list[str], list[str]]:
    if not ANSWER_TEMPLATE.is_file():
        raise SystemExit(f"missing answer template: {rel(ANSWER_TEMPLATE)}")
    base_fields: list[str] = []
    boundary_fields: list[str] = []
    review_fields: list[str] = []
    section = "base"
    for raw in ANSWER_TEMPLATE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# Boundary confirmations"):
            section = "boundary"
            continue
        if line.startswith("# Evidence review confirmations"):
            section = "review"
            continue
        if line.startswith("#") or ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if section == "boundary":
            boundary_fields.append(key)
        elif section == "review":
            review_fields.append(key)
        else:
            base_fields.append(key)
    return base_fields, boundary_fields, review_fields


def stager_status() -> dict[str, Any]:
    if not STAGER_SUMMARY.is_file():
        return {
            "status": "missing",
            "staged_draft_written": False,
            "answered_customer_field_count": 0,
            "missing_customer_field_count": 13,
        }
    return read_json(STAGER_SUMMARY)


def build_payload() -> dict[str, Any]:
    base_fields, boundary_fields, review_fields = parse_answer_template()
    stager = stager_status()
    official_exists = OFFICIAL_ANSWER.exists()
    status = (
        "ready_for_human_official_answer_sheet_completion"
        if not official_exists
        else "official_answer_sheet_present_review_with_answer_intake_helper"
    )
    return {
        "customer_validation_official_answer_completion_helper_v0_1": True,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "source_answer_template": rel(ANSWER_TEMPLATE),
        "target_official_answer_sheet": rel(OFFICIAL_ANSWER),
        "official_answer_sheet_exists": official_exists,
        "stager_summary": rel(STAGER_SUMMARY),
        "stager_status": stager.get("status"),
        "staged_draft_written": bool(stager.get("staged_draft_written", False)) and STAGED_DRAFT.exists(),
        "base_field_count": len(base_fields),
        "boundary_confirmation_field_count": len(boundary_fields),
        "evidence_review_field_count": len(review_fields),
        "total_official_answer_field_count": len(base_fields) + len(boundary_fields) + len(review_fields),
        "customer_answer_fields_from_interview": 13,
        "local_static_official_answer_completion_html": True,
        "browser_only_text_generation": True,
        "html_writes_files": False,
        "html_network_calls": False,
        "codex_generated_customer_answers": False,
        "official_answer_sheet_written_by_codex": False,
        "target_session_entry_written": False,
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
        "blockers_closed_by_helper": 0,
    }


def render_field_checklist(base: list[str], boundary: list[str], review: list[str], payload: dict[str, Any]) -> str:
    def section(title: str, fields: list[str]) -> list[str]:
        lines = [f"## {title}", ""]
        lines.extend(f"- [ ] `{field}`" for field in fields)
        lines.append("")
        return lines

    lines = [
        "# Official Customer Validation Answer Sheet Field Checklist",
        "",
        "Use this checklist only after a real external customer or target-user session.",
        "Codex must not invent or prefill customer answers.",
        "",
        f"- Target answer sheet: `{payload['target_official_answer_sheet']}`",
        f"- Source template: `{payload['source_answer_template']}`",
        f"- Staged draft available: `{str(payload['staged_draft_written']).lower()}`",
        "",
    ]
    lines += section("Session and customer fields", base)
    lines += section("Boundary confirmations", boundary)
    lines += section("Evidence review confirmations", review)
    lines += [
        "## Required Next Command After Human Completion",
        "",
        "```bash",
        "python3 scripts/saee_customer_validation_answer_intake_helper.py --apply",
        "python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply",
        "python3 scripts/mainline_guard.py",
        "make check",
        "```",
        "",
    ]
    return "\n".join(lines)


def render_html(base: list[str], boundary: list[str], review: list[str], payload: dict[str, Any]) -> str:
    def field_html(field: str, field_type: str) -> str:
        label = field.replace("_", " ")
        if field_type == "review":
            return (
                f'<label><span>{label}</span>'
                f'<select data-field="{field}"><option value="true">true - 已人工确认</option>'
                '<option value="">未确认</option><option value="false">false - 不成立</option></select></label>'
            )
        if field_type == "boundary":
            return (
                f'<label><span>{label}</span>'
                f'<select data-field="{field}"><option value="">请选择</option>'
                '<option value="true">true - 事实成立</option><option value="false">false - 不成立</option></select></label>'
            )
        if field.endswith("_score") or field in {"candidate_count", "time_to_value_minutes"}:
            return f'<label><span>{label}</span><input data-field="{field}" type="number" min="0" /></label>'
        if field == "willing_to_test_own_candidates" or field == "human_entry_confirmed":
            return (
                f'<label><span>{label}</span><select data-field="{field}">'
                '<option value="">请选择</option><option value="true">true - 是</option>'
                '<option value="false">false - 否</option></select></label>'
            )
        if field in {"top_objection", "evidence_missing", "notes", "human_source_context"}:
            return f'<label><span>{label}</span><textarea data-field="{field}" rows="3"></textarea></label>'
        return f'<label><span>{label}</span><input data-field="{field}" type="text" /></label>'

    base_inputs = "\n".join(field_html(field, "base") for field in base)
    boundary_inputs = "\n".join(field_html(field, "boundary") for field in boundary)
    review_inputs = "\n".join(field_html(field, "review") for field in review)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SAEE 客户验证官方答案表完成页</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f4ef;
      --panel: #fffefa;
      --ink: #191816;
      --muted: #6f6a61;
      --line: #ddd6ca;
      --accent: #2354d8;
      --soft: #e9eefc;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: linear-gradient(180deg, #fbfaf7 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      line-height: 1.55;
    }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 56px; }}
    header {{ display: grid; gap: 12px; margin-bottom: 22px; }}
    h1 {{ font-size: clamp(28px, 4vw, 48px); line-height: 1.08; margin: 0; letter-spacing: 0; }}
    h2 {{ font-size: 20px; margin: 0 0 12px; }}
    p {{ margin: 0; color: var(--muted); }}
    .status {{
      display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;
    }}
    .pill {{
      border: 1px solid var(--line); background: var(--panel); border-radius: 999px;
      padding: 8px 12px; font-size: 13px; color: var(--muted);
    }}
    .layout {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 420px); gap: 18px; align-items: start; }}
    section, aside {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px;
      box-shadow: 0 12px 30px rgba(35, 31, 24, 0.06);
    }}
    .grid {{ display: grid; gap: 12px; }}
    label {{ display: grid; gap: 6px; }}
    label span {{ font-size: 13px; color: var(--muted); }}
    input, textarea, select {{
      width: 100%; border: 1px solid var(--line); border-radius: 8px; background: #fff;
      padding: 10px 11px; font: inherit; color: var(--ink);
    }}
    textarea {{ resize: vertical; }}
    .group {{ margin-bottom: 20px; }}
    button {{
      width: 100%; border: 0; border-radius: 8px; background: var(--accent); color: white;
      font: inherit; font-weight: 650; padding: 12px 14px; cursor: pointer;
    }}
    pre {{
      white-space: pre-wrap; overflow-wrap: anywhere; min-height: 380px; margin: 14px 0 0;
      background: #111318; color: #f5f3ed; border-radius: 8px; padding: 14px; font-size: 13px;
    }}
    .note {{ background: var(--soft); border-color: #cbd6f8; }}
    @media (max-width: 900px) {{ .layout {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <p>SAEE 客户验证</p>
    <h1>官方答案表完成页</h1>
    <p>用于真实客户或目标用户访谈之后，把答案整理成可复制的 key: value 文本。此页面只在浏览器里生成文本，不写文件、不联网、不代表客户验证已完成。</p>
    <div class="status">
      <span class="pill">当前阻塞：customer_validated</span>
      <span class="pill">客户验证：false</span>
      <span class="pill">生产可用：false</span>
      <span class="pill">不暴露私有核心</span>
    </div>
  </header>
  <div class="layout">
    <section>
      <div class="group">
        <h2>一、会话和客户答案</h2>
        <div class="grid">{base_inputs}</div>
      </div>
      <div class="group">
        <h2>二、边界确认</h2>
        <p>只有事实成立时才选 true。</p>
        <div class="grid">{boundary_inputs}</div>
      </div>
      <div class="group">
        <h2>三、证据复核确认</h2>
        <p>默认是 true，但仍需人工确认。</p>
        <div class="grid">{review_inputs}</div>
      </div>
    </section>
    <aside>
      <section class="note">
        <h2>下一步</h2>
        <p>1. 填完左侧字段。</p>
        <p>2. 点击生成文本。</p>
        <p>3. 人工复制到：</p>
        <p><code>{payload["target_official_answer_sheet"]}</code></p>
        <p>4. 再运行 answer intake 和 evidence pipeline。</p>
      </section>
      <button type="button" id="generate">生成可复制答案文本</button>
      <pre id="output">点击按钮后，这里会生成 key: value 文本。</pre>
    </aside>
  </div>
</main>
<script>
  const button = document.getElementById('generate');
  const output = document.getElementById('output');
  button.addEventListener('click', () => {{
    const rows = ['# SAEE Customer Validation Human Answer Sheet', '', 'Only fill this after a real external customer or target-user session.'];
    document.querySelectorAll('[data-field]').forEach((el) => {{
      const key = el.getAttribute('data-field');
      const value = (el.value || '').trim();
      rows.push(`${{key}}: ${{value}}`);
    }});
    rows.push('', '# Generated locally in browser. Review manually before using as official evidence.');
    output.textContent = rows.join('\\n');
  }});
</script>
</body>
</html>
"""


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base_fields, boundary_fields, review_fields = parse_answer_template()
    write_json(SUMMARY, payload)
    FIELD_CHECKLIST.write_text(render_field_checklist(base_fields, boundary_fields, review_fields, payload), encoding="utf-8")
    COPY_TEMPLATE.write_text(
        "# Copy this block into the official answer sheet only after a real customer session.\n\n"
        + ANSWER_TEMPLATE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    HTML.write_text(render_html(base_fields, boundary_fields, review_fields, payload), encoding="utf-8")
    REPORT.write_text(
        f"""# SAEE Customer Validation Official Answer Completion Helper v0.1

Status: `{payload['status']}`.

This helper records the final manual completion path for the official customer
validation answer sheet. It does not create customer answers, write official
evidence, contact customers, run external services, close `customer_validated`,
or claim production readiness.

## What It Solves

The 13-question live interview captures customer-facing answers, but the
official answer sheet also requires session metadata, factual boundary
confirmations, and human evidence-review confirmations. This helper makes those
remaining fields explicit.

## Current State

- current_goal_blocker: `customer_validated`
- official_answer_sheet_exists: `{str(payload['official_answer_sheet_exists']).lower()}`
- stager_status: `{payload['stager_status']}`
- staged_draft_written: `{str(payload['staged_draft_written']).lower()}`
- total_official_answer_field_count: `{payload['total_official_answer_field_count']}`
- browser_completion_page: `{rel(HTML)}`
- codex_generated_customer_answers: false
- official_answer_sheet_written_by_codex: false
- local_static_official_answer_completion_html: true
- browser_only_text_generation: true
- html_writes_files: false
- html_network_calls: false
- target_session_entry_written: false
- customer_validated=false
- production_ready=false
- private_core_exposed=false
- blockers_closed_by_helper=0

## Human Next Step

1. Complete `{payload['target_official_answer_sheet']}` from a real external
   customer or target-user session.
2. Use `{rel(FIELD_CHECKLIST)}` to verify all required fields.
3. Run `python3 scripts/saee_customer_validation_answer_intake_helper.py --apply`.
4. Run `python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply`.
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Official Answer Completion Helper Boundary Audit

customer_validation_official_answer_completion_helper_v0_1: true
status: {payload['status']}

- current_goal_blocker: customer_validated
- codex_generated_customer_answers: false
- official_answer_sheet_written_by_codex: false
- target_session_entry_written: false
- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- external_model_api_called: false
- blockers_closed_by_helper: 0
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Customer Validation Official Answer Completion Helper Gate

answer: conditional_internal_helper_only

reason: Recommend this helper only for reducing manual friction after a real
external customer or target-user session. It is not customer validation itself.

boundary:
  codex_generated_customer_answers: false
  official_answer_sheet_written_by_codex: false
  customer_validated: false
  production_ready: false
  product_launched: false
  private_core_exposed: false
  blockers_closed_by_helper: 0

next_action: Human completes the official answer sheet, then explicitly runs the
answer intake and evidence pipeline commands.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/official_answer_sheet_field_checklist.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/official_answer_sheet_blank_copy_block.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/official_answer_sheet_completion.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_GATE.md",
        "/scripts/saee_customer_validation_official_answer_completion_helper.py",
        "/scripts/saee_customer_validation_official_answer_completion_helper_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["customer_validation_official_answer_completion_helper_v0_1"] = {
        "name": "SAEE Customer Validation Official Answer Completion Helper v0.1",
        **{key: payload[key] for key in [
            "status",
            "current_goal_blocker",
            "source_answer_template",
            "target_official_answer_sheet",
            "official_answer_sheet_exists",
            "stager_status",
            "staged_draft_written",
            "total_official_answer_field_count",
            "local_static_official_answer_completion_html",
            "browser_only_text_generation",
            "html_writes_files",
            "html_network_calls",
            "codex_generated_customer_answers",
            "official_answer_sheet_written_by_codex",
            "target_session_entry_written",
            "customer_validated",
            "production_ready",
            "product_launched",
            "customer_contacted_by_codex",
            "private_core_exposed",
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
            "external_calls_made",
            "blockers_closed_by_helper",
        ]},
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "field_checklist": rel(FIELD_CHECKLIST),
            "copy_template": rel(COPY_TEMPLATE),
            "html": rel(HTML),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_official_answer_completion_helper.py",
            "smoke": "scripts/saee_customer_validation_official_answer_completion_helper_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Customer Validation Official Answer Completion Helper v0.1

- `customer_validation_official_answer_completion_helper_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Field checklist: `{rel(FIELD_CHECKLIST)}`
- Browser completion page: `{rel(HTML)}`
- Target official answer sheet: `{payload['target_official_answer_sheet']}`
- `codex_generated_customer_answers=false`; `official_answer_sheet_written_by_codex=false`.
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_OFFICIAL_ANSWER_COMPLETION_HELPER: PASS "
        f"status={payload['status']} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
