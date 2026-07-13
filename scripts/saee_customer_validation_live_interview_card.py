#!/usr/bin/env python3
"""Generate the 13-question live interview card for customer validation.

This card extracts only the fields that must be answered by a real customer or
target user from the live fill queue. It is a human interview aid, not customer
evidence. It does not contact customers, infer answers, write the final answer
sheet, or close the customer_validated blocker.
"""

from __future__ import annotations

import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
QUEUE_SUMMARY = EVIDENCE / "customer_validation_live_fill_queue/customer_validation_live_fill_queue.local.json"
OUT = EVIDENCE / "customer_validation_live_interview_card"
SUMMARY = OUT / "customer_validation_live_interview_card.local.json"
REPORT = OUT / "customer_validation_live_interview_card.md"
HTML = OUT / "customer_validation_live_interview_card.html"
ANSWER_BLOCK = OUT / "customer_validation_live_interview_answer_block.md"
BOUNDARY = OUT / "customer_validation_live_interview_card_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_GATE.md"
ANSWER_INPUT = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
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


def refresh_queue() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/saee_customer_validation_live_fill_queue.py")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def ordered_customer_items(queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = [
        "participant_role",
        "team_type",
        "current_evaluation_method",
        "candidate_count",
        "understanding_score",
        "trust_score",
        "decision_influence_score",
        "repeat_usage_intent_score",
        "time_to_value_minutes",
        "willing_to_test_own_candidates",
        "top_objection",
        "evidence_missing",
        "notes",
    ]
    by_field = {
        item["field"]: item
        for item in queue
        if item.get("category") == "customer_answer_required"
    }
    return [by_field[field] for field in priority if field in by_field]


def build_payload() -> dict[str, Any]:
    refresh_queue()
    queue_summary = read_json(QUEUE_SUMMARY)
    items = ordered_customer_items(queue_summary.get("queue", []))
    return {
        "customer_validation_live_interview_card_v0_1": True,
        "status": "ready_for_real_customer_interview",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "source_queue_status": queue_summary.get("status"),
        "source_queue_item_count": queue_summary.get("queue_item_count"),
        "customer_question_count": len(items),
        "interview_questions": items,
        "answer_input": rel(ANSWER_INPUT),
        "answer_input_exists": ANSWER_INPUT.exists(),
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
        "blockers_closed_by_card": 0,
    }


def question_rows(items: list[dict[str, Any]]) -> str:
    rows = []
    for index, item in enumerate(items, 1):
        rows.append(
            f"| {index} | `{item['field']}` | {item['question_or_action']} |"
        )
    return "\n".join(rows)


def answer_block(items: list[dict[str, Any]]) -> str:
    lines = [
        "# Customer-answer block. Paste into customer_validation_answers.human_filled.md after a real customer or target-user interview.",
    ]
    for item in items:
        lines.append(f"{item['field']}:")
    return "\n".join(lines) + "\n"


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)
    rows = question_rows(payload["interview_questions"])
    REPORT.write_text(
        f"""# SAEE Customer Validation Live Interview Card v0.1

Status: `{payload['status']}`.

This card contains only the 13 questions that must be answered by a real
customer or target user. It is meant for a short live conversation. It does not
contact customers, infer answers, write evidence, close blockers, or claim
customer validation.

## Boundary

- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
- blockers_closed_by_card=0

## 13 Customer Questions

| # | Field | Ask this in plain Chinese |
| --- | --- | --- |
{rows}

## Copy Answers Here First

Use:

`{rel(ANSWER_BLOCK)}`

Then merge the answers into:

`{payload['answer_input']}`
""",
        encoding="utf-8",
    )
    ANSWER_BLOCK.write_text(answer_block(payload["interview_questions"]), encoding="utf-8")
    cards = "\n".join(
        f"<li><strong>{index}. {html.escape(item['question_or_action'])}</strong><code>{html.escape(item['field'])}:</code></li>"
        for index, item in enumerate(payload["interview_questions"], 1)
    )
    HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 真实客户 13 问访谈卡</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #202123; background: #f7f7f5; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
    h1 {{ font-size: 34px; line-height: 1.15; margin: 0 0 12px; letter-spacing: 0; }}
    p {{ font-size: 17px; line-height: 1.65; color: #555; }}
    .status {{ display: inline-block; border: 1px solid #d7d7d2; border-radius: 999px; padding: 7px 12px; background: #fff; color: #333; }}
    ol {{ margin: 28px 0; padding: 0; list-style: none; display: grid; gap: 12px; }}
    li {{ background: #fff; border: 1px solid #deded9; border-radius: 8px; padding: 16px; }}
    strong {{ display: block; font-size: 18px; line-height: 1.45; margin-bottom: 10px; }}
    code {{ display: inline-block; background: #f1f1ee; border-radius: 6px; padding: 4px 8px; color: #333; }}
    .boundary {{ border-top: 1px solid #ddd; margin-top: 28px; padding-top: 18px; }}
  </style>
</head>
<body>
  <main>
    <span class="status">只用于真实客户访谈，不是客户验证结论</span>
    <h1>SAEE 真实客户 13 问访谈卡</h1>
    <p>按顺序问完即可。不要让 Codex 代填客户答案；不要收客户秘密、生产数据或私有材料。</p>
    <ol>
      {cards}
    </ol>
    <div class="boundary">
      <p>当前仍然是：customer_validated=false，production_ready=false，product_launched=false，private_core_exposed=false。</p>
    </div>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Live Interview Card Boundary Audit

customer_validation_live_interview_card_v0_1: true
status: {payload['status']}

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
- blockers_closed_by_card: 0
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Customer Validation Live Interview Card Gate

answer: ready_for_real_customer_interview_no_validation_claim

reason: The 13-question card makes the real target-user conversation easier,
but it does not create customer evidence by itself.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_card: 0

next_action: A human must ask these questions to a real external customer or
target user, then copy the answers into the human-filled answer sheet.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_answer_block.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_GATE.md",
        "/scripts/saee_customer_validation_live_interview_card.py",
        "/scripts/saee_customer_validation_live_interview_card_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["customer_validation_live_interview_card_v0_1"] = {
        "name": "SAEE Customer Validation Live Interview Card v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "customer_question_count": payload["customer_question_count"],
        "answer_input_exists": payload["answer_input_exists"],
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
        "blockers_closed_by_card": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "html": rel(HTML),
            "answer_block": rel(ANSWER_BLOCK),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_live_interview_card.py",
            "smoke": "scripts/saee_customer_validation_live_interview_card_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)
    block = f"""## Customer Validation Live Interview Card v0.1

- `customer_validation_live_interview_card_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Customer questions: `{payload['customer_question_count']}`
- HTML card: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.html`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_LIVE_INTERVIEW_CARD: PASS "
        f"questions={payload['customer_question_count']} customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
