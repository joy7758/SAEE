#!/usr/bin/env python3
"""Generate the live fill queue for real customer-validation answers.

This helper turns the current answer-sheet preflight result into a practical
question queue. It separates fields that must come from a real customer or
target user from founder/operator confirmations that can be filled only when
factually true. It never infers customer answers, never writes the final session
entry, and never closes the customer_validated blocker.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_live_fill_queue"
SUMMARY = OUT / "customer_validation_live_fill_queue.local.json"
REPORT = OUT / "customer_validation_live_fill_queue.md"
COPY_BLOCK = OUT / "customer_validation_live_fill_queue_copy_block.md"
BOUNDARY = OUT / "customer_validation_live_fill_queue_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_GATE.md"
ANSWER_INPUT = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
PREFLIGHT_SUMMARY = EVIDENCE / "customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json"
ENTRY_TEMPLATE = EVIDENCE / "external_customer_validation_session_entry.template.json"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

CUSTOMER_FIELDS = {
    "participant_role": "你现在负责什么？",
    "team_type": "你所在团队大概是什么类型？",
    "current_evaluation_method": "你现在怎么判断哪个 agent、工作流或策略版本更靠谱？",
    "candidate_count": "你通常要比较几个候选方案？",
    "understanding_score": "听完介绍后，你能否用自己的话说清 SAEE 是做什么的？1-5 分。",
    "trust_score": "你现在对这个结果的可信度是多少？1-5 分。",
    "decision_influence_score": "这个结果会不会影响你部署、暂缓或重测的决定？1-5 分。",
    "repeat_usage_intent_score": "你是否愿意后续重复使用这类评测？1-5 分。",
    "time_to_value_minutes": "你大概花了几分钟理解它是否有用？",
    "willing_to_test_own_candidates": "你愿不愿意用自己的候选方案再测一次？true/false。",
    "top_objection": "你最大的疑问或反对点是什么？",
    "evidence_missing": "还缺什么证据，你才更愿意继续试？",
    "notes": "请记录对方最关键的一句话反馈。",
}

SESSION_FIELDS = {
    "session_id": "给这次真实访谈设置一个唯一编号。",
    "session_date": "记录访谈日期，例如 2026-07-09。",
    "human_reviewer_name": "记录由谁完成访谈和录入。",
    "human_source_context": "说明来源：真实外部客户或目标用户访谈，不能写内部自测。",
    "human_entry_confirmed": "录入人确认这是真实访谈记录后填 true。",
}

BOUNDARY_FIELDS = {
    "no_secrets_collected": "确认没有收集客户秘密。",
    "no_production_data_collected": "确认没有收集生产数据。",
    "no_customer_data_uploaded": "确认没有要求客户上传真实业务数据。",
    "no_private_core_disclosed": "确认没有披露 SAEE 私有核心。",
    "no_production_ready_claim_made": "确认没有声称 SAEE 已生产可用。",
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


def run_preflight() -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/saee_customer_validation_answer_sheet_preflight.py")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def evidence_review_fields() -> list[str]:
    template = read_json(ENTRY_TEMPLATE)
    review = template.get("evidence_review", {})
    return sorted(review) if isinstance(review, dict) else []


def classify_field(field: str) -> tuple[str, str]:
    if field in CUSTOMER_FIELDS:
        return "customer_answer_required", CUSTOMER_FIELDS[field]
    if field in SESSION_FIELDS:
        return "session_metadata_required", SESSION_FIELDS[field]
    if field in BOUNDARY_FIELDS:
        return "boundary_confirmation_required", BOUNDARY_FIELDS[field]
    if field in evidence_review_fields():
        return "human_review_confirmation_required", "如果已经人工核对且真实成立，填 true；否则先留空。"
    return "other_required", "补充该字段的真实值，不要由 Codex 推断。"


def build_payload() -> dict[str, Any]:
    preflight_stdout = run_preflight()
    preflight = read_json(PREFLIGHT_SUMMARY)
    missing_fields = list(preflight.get("missing_fields", []))
    invalid_fields = list(preflight.get("invalid_fields", []))
    records = []
    for field in missing_fields + invalid_fields:
        category, question = classify_field(field)
        records.append(
            {
                "field": field,
                "category": category,
                "question_or_action": question,
                "source_required": "real_customer_or_target_user" if category == "customer_answer_required" else "human_operator_confirmation",
                "codex_may_prefill": False,
            }
        )
    customer_count = sum(1 for item in records if item["category"] == "customer_answer_required")
    status = "ready_for_real_customer_live_fill" if records else "ready_for_pipeline_apply_review"
    return {
        "customer_validation_live_fill_queue_v0_1": True,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "answer_input": rel(ANSWER_INPUT),
        "answer_input_exists": ANSWER_INPUT.exists(),
        "preflight_status": preflight.get("status"),
        "ready_for_apply": preflight.get("ready_for_explicit_apply_request", False),
        "missing_field_count": len(missing_fields),
        "invalid_field_count": len(invalid_fields),
        "queue_item_count": len(records),
        "customer_answer_required_count": customer_count,
        "human_operator_confirmation_required_count": len(records) - customer_count,
        "queue": records,
        "preflight_stdout": preflight_stdout,
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
        "blockers_closed_by_queue": 0,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)
    rows = "\n".join(
        f"| `{item['field']}` | {item['category']} | {item['question_or_action']} | {item['source_required']} |"
        for item in payload["queue"]
    )
    if not rows:
        rows = "| - | - | 当前没有缺失字段；进入 pipeline apply 前仍需人工复核。 | - |"
    REPORT.write_text(
        f"""# SAEE Customer Validation Live Fill Queue v0.1

Status: `{payload['status']}`.

This file turns the current customer-validation answer preflight into a live
question queue. It does not contact customers, infer answers, write final
session evidence, close blockers, or claim customer validation.

## Current State

- current_goal_blocker: `customer_validated`
- answer_input_exists: `{payload['answer_input_exists']}`
- preflight_status: `{payload['preflight_status']}`
- missing_field_count: `{payload['missing_field_count']}`
- invalid_field_count: `{payload['invalid_field_count']}`
- customer_answer_required_count: `{payload['customer_answer_required_count']}`
- human_operator_confirmation_required_count: `{payload['human_operator_confirmation_required_count']}`
- customer_validated=false
- production_ready=false
- private_core_exposed=false

## Queue

| Field | Category | Question / Action | Source Required |
| --- | --- | --- | --- |
{rows}

## After Filling

Save the completed answers to:

`{payload['answer_input']}`

Then run:

```bash
python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py --apply
```
""",
        encoding="utf-8",
    )
    copy_lines = [
        "# Copy this into customer_validation_answers.human_filled.md after a real customer or target-user session.",
    ]
    for item in payload["queue"]:
        copy_lines.append(f"{item['field']}:")
    COPY_BLOCK.write_text("\n".join(copy_lines) + "\n", encoding="utf-8")
    BOUNDARY.write_text(
        f"""# SAEE Customer Validation Live Fill Queue Boundary Audit

customer_validation_live_fill_queue_v0_1: true
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
- blockers_closed_by_queue: 0
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Customer Validation Live Fill Queue Gate

answer: ready_for_real_customer_live_fill_no_validation_claim

reason: The queue identifies which fields still require real customer or
human-operator input before the existing customer-validation pipeline can be
applied. It does not create customer evidence by itself.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  customer_contacted_by_codex: false
  private_core_exposed: false
  blockers_closed_by_queue: 0

next_action: Conduct a real external customer or target-user session, fill the
listed fields, then run the answer-to-evidence pipeline with explicit apply.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue_copy_block.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_GATE.md",
        "/scripts/saee_customer_validation_live_fill_queue.py",
        "/scripts/saee_customer_validation_live_fill_queue_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["customer_validation_live_fill_queue_v0_1"] = {
        "name": "SAEE Customer Validation Live Fill Queue v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "answer_input_exists": payload["answer_input_exists"],
        "preflight_status": payload["preflight_status"],
        "missing_field_count": payload["missing_field_count"],
        "invalid_field_count": payload["invalid_field_count"],
        "queue_item_count": payload["queue_item_count"],
        "customer_answer_required_count": payload["customer_answer_required_count"],
        "human_operator_confirmation_required_count": payload["human_operator_confirmation_required_count"],
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
        "blockers_closed_by_queue": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "report": rel(REPORT),
            "copy_block": rel(COPY_BLOCK),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_live_fill_queue.py",
            "smoke": "scripts/saee_customer_validation_live_fill_queue_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)
    block = f"""## Customer Validation Live Fill Queue v0.1

- `customer_validation_live_fill_queue_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Queue items: `{payload['queue_item_count']}`
- Customer-answer items: `{payload['customer_answer_required_count']}`
- Output: `phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue.md`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE: PASS "
        f"status={payload['status']} queue_items={payload['queue_item_count']} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
