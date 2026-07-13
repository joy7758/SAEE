#!/usr/bin/env python3
"""Create the current human action board for external customer validation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = BASE / "external_customer_validation_action_board"
SUMMARY_PATH = OUT / "external_customer_validation_action_board.local.json"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_ACTION_BOARD_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


ACTIONS = [
    {
        "action_id": "ECV-001",
        "title": "筛选一个真实外部目标用户",
        "entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md",
        "human_only": True,
        "codex_executable": False,
    },
    {
        "action_id": "ECV-002",
        "title": "人工发送邀请草稿",
        "entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md",
        "human_only": True,
        "codex_executable": False,
    },
    {
        "action_id": "ECV-003",
        "title": "会前确认同意和边界说明",
        "entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md",
        "human_only": True,
        "codex_executable": False,
    },
    {
        "action_id": "ECV-004",
        "title": "只使用 12 个最小会话问题记录反馈",
        "entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
        "secondary_entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_FILLING_GUIDE.md",
        "human_only": True,
        "codex_executable": False,
    },
    {
        "action_id": "ECV-005",
        "title": "用最小会话表单生成并保存 JSON",
        "entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
        "expected_output": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json",
        "human_only": True,
        "codex_executable": False,
    },
    {
        "action_id": "ECV-006",
        "title": "人工结果存在后再导入并运行 validator",
        "entrypoint": "scripts/saee_external_customer_validation_session_entry_importer.py --apply",
        "secondary_entrypoint": "scripts/saee_customer_validation_approval_input_validator.py",
        "human_only_until_result_exists": True,
        "codex_executable": False,
    },
]


SUMMARY = {
    "external_customer_validation_action_board_v0_1": True,
    "status": "ready_for_human_customer_validation_session_sequence",
    "board_type": "current_goal_customer_validation_human_action_board",
    "current_goal_blocker": "customer_validated",
    "recommended_path_locked": True,
    "recommended_path_id": "minimum_session_packet",
    "recommended_path_label": "12-question minimum external customer validation session",
    "recommended_form": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html",
    "recommended_questions": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md",
    "alternative_paths_reference_only": True,
    "deprecated_default_entrypoint": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.html",
    "action_count": len(ACTIONS),
    "first_action_id": "ECV-001",
    "first_data_entry_action_id": "ECV-005",
    "required_human_output": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json",
    "human_action_required": True,
    "human_session_required": True,
    "human_session_performed": False,
    "human_result_entered": False,
    "ready_for_import_after_human_entry": False,
    "ready_for_validator_after_import": False,
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
    "blockers_closed_by_action_board": 0,
    "actions": ACTIONS,
}


README = """# SAEE External Customer Validation Action Board v0.1

Status: ready_for_human_customer_validation_session_sequence.

This board is the current human action route for the remaining commercial
blocker: `customer_validated`.

Recommended path is locked to the minimum session packet:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`

Use that form to create the required JSON:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

Other customer-validation materials are reference-only unless a separate human
decision reopens them.

It does not contact customers, run a customer session, import evidence, run a
validator, close a blocker, launch product, or claim production readiness. It
only shows the exact files and order a human should use.
"""


def markdown_table() -> str:
    rows = [
        "| Step | Action | Open This | Who Executes |",
        "| --- | --- | --- | --- |",
    ]
    for action in ACTIONS:
        target = action["entrypoint"]
        if "secondary_entrypoint" in action:
            target += f"<br>{action['secondary_entrypoint']}"
        rows.append(
            f"| {action['action_id']} | {action['title']} | `{target}` | Human only |"
        )
    return "\n".join(rows)


BOARD_MD = f"""# SAEE External Customer Validation Action Board

Current blocker: `customer_validated`.

The local human evidence inspection passed, but SAEE still needs at least one
real external customer or target-user validation session before customer
validation can be claimed.

## Recommended Path Locked

Use only the 12-question minimum session packet for the next real customer or
target-user session:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`

This keeps the next human step small: ask the 12 questions, save the generated
JSON, then run the importer and validator only after the human-created JSON
exists. Older interview/workbench routes remain reference-only.

{markdown_table()}

## Required Output

The next required human-created file is:

`phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`

After that file exists, use the existing importer and validator. Do not infer
missing feedback.

## Boundaries

- Codex may not contact customers.
- Codex may not run the external session.
- Codex may not infer customer feedback.
- `customer_validated=false` until real evidence is imported and accepted.
- `production_ready=false`.
- `product_launched=false`.
- `private_core_exposed=false`.
"""


BOARD_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 客户验证行动板</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f7f4; color: #171717; }
    main { max-width: 920px; margin: 0 auto; padding: 40px 20px; }
    h1 { font-size: 34px; margin: 0 0 10px; }
    .status { color: #555; line-height: 1.7; }
    .card { background: #fff; border: 1px solid #e4e0d8; border-radius: 8px; padding: 18px; margin: 14px 0; }
    .step { font-weight: 700; color: #0f5b4f; }
    code { background: #f0eee8; padding: 2px 5px; border-radius: 4px; }
    .warn { border-left: 4px solid #b45309; padding-left: 12px; }
  </style>
</head>
<body>
  <main>
    <h1>SAEE 客户验证行动板</h1>
    <p class="status">当前唯一收口目标：<code>customer_validated</code>。这不是自动验证，也不是发布。下面每一步都需要人工执行。</p>
    <section class="card warn"><p>推荐路径已锁定：只使用 <code>external_customer_validation_minimum_session_packet/minimum_session_form.html</code>。其他访谈脚本和旧工作台只作为参考。</p></section>
    <section class="card"><div class="step">ECV-001</div><p>先筛选一个真实外部目标用户。</p><code>PARTICIPANT_SCREENING_CHECKLIST.md</code></section>
    <section class="card"><div class="step">ECV-002</div><p>人工发送邀请草稿。</p><code>INVITATION_MESSAGE_DRAFT.md</code></section>
    <section class="card"><div class="step">ECV-003</div><p>会前确认同意和边界说明。</p><code>CONSENT_AND_BOUNDARY_SCRIPT.md</code></section>
    <section class="card"><div class="step">ECV-004</div><p>只使用 12 个最小会话问题记录反馈。</p><code>MINIMUM_SESSION_QUESTIONS.md</code></section>
    <section class="card"><div class="step">ECV-005</div><p>用最小会话表单生成并保存 JSON。</p><code>minimum_session_form.html</code></section>
    <section class="card"><div class="step">ECV-006</div><p>只有人工结果文件存在后，才运行导入和 validator。</p><code>saee_external_customer_validation_session_entry_importer.py --apply</code></section>
    <section class="card warn"><p>边界：Codex 不联系客户、不运行访谈、不推断反馈、不关闭 blocker、不声明生产可用。</p></section>
  </main>
</body>
</html>
"""


BOUNDARY = """# SAEE External Customer Validation Action Board Boundary Audit

- Current blocker remains `customer_validated`.
- No customer contacted by Codex.
- No external customer session run by Codex.
- No customer feedback inferred by Codex.
- No evidence imported.
- No validator run on new human customer evidence.
- No blocker closed.
- Recommended path is locked to the minimum session packet.
- Other customer-validation routes remain reference-only.
- No product launched.
- No production-ready claim added.
- No customer-validation claim added.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.

Final decision: boundary safe. This board only clarifies human order of
operations for the already prepared customer-validation route.
"""


GATE_TEXT = """# SAEE External Customer Validation Action Board Gate

answer: ready_for_human_customer_validation_session_sequence

reason: The local evidence inspection is complete, and the current goal blocker
is `customer_validated`. The board locks the next step to the 12-question
minimum session packet so the human path is small, importer-compatible, and not
mixed with older reference-only routes.

boundary:

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- codex_may_run_external_session: false
- codex_may_infer_customer_feedback: false
- private_core_exposed: false
- blockers_closed_by_action_board: 0
- recommended_path_locked: true
- recommended_path_id: minimum_session_packet

next_action: Human performs ECV-001 through ECV-005 with
`external_customer_validation_minimum_session_packet/minimum_session_form.html`
and creates
`external_customer_validation_session_entry.human_filled.local.json`. Import and
validator use come only after that real human-created file exists.
"""


STATUS_BLOCK = """## External Customer Validation Action Board v0.1

- `external_customer_validation_action_board_v0_1=true`
- Status: `ready_for_human_customer_validation_session_sequence`.
- Purpose: provide one ordered human-only route for the current blocker,
  `customer_validated`, from participant screening through session-entry JSON.
- Recommended path is locked to the 12-question minimum session packet:
  `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_form.html`.
- Alternative customer-validation routes are reference-only unless reopened by a
  separate human decision.
- First action: `ECV-001` screen one real external customer or target user.
- Required human output:
  `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
- Boundary: `customer_validated=false`, `production_ready=false`,
  `product_launched=false`, `customer_contacted_by_codex=false`,
  `private_core_exposed=false`, and `blockers_closed_by_action_board=0`.
"""


LLMS_PATHS = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/README.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.html",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/BOUNDARY_AUDIT.md",
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
    data["external_customer_validation_action_board_v0_1"] = SUMMARY
    AGENT_INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    write(SUMMARY_PATH, json.dumps(SUMMARY, indent=2, ensure_ascii=False))
    write(OUT / "README.md", README)
    write(OUT / "external_customer_validation_action_board.md", BOARD_MD)
    write(OUT / "external_customer_validation_action_board.html", BOARD_HTML)
    write(OUT / "BOUNDARY_AUDIT.md", BOUNDARY)
    write(GATE, GATE_TEXT)
    update_llms()
    update_agent_index()
    for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        append_once(ROOT / name, "external_customer_validation_action_board_v0_1=true", STATUS_BLOCK)
    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_ACTION_BOARD: READY")


if __name__ == "__main__":
    main()
