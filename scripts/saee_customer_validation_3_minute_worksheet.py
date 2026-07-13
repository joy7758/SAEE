#!/usr/bin/env python3
"""Generate a 3-minute Chinese worksheet for real customer validation.

This is a short interview capture surface for the remaining customer_validated
blocker. It lowers first-contact friction only. It does not contact customers,
create final validation evidence, write the final session-entry JSON, close
blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "customer_validation_3_minute_worksheet"
SUMMARY = OUT / "customer_validation_3_minute_worksheet.local.json"
WORKSHEET = OUT / "customer_validation_3_minute_worksheet.md"
FIELD_MAP = OUT / "customer_validation_3_minute_field_map.md"
OUTPUT_GUIDE = OUT / "customer_validation_3_minute_output_guide.md"
BOUNDARY = OUT / "customer_validation_3_minute_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_GATE.md"
ANSWER_INPUT = EVIDENCE_DIR / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"
PREFLIGHT = EVIDENCE_DIR / "customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json"
TARGET_ENTRY = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

QUESTION_ROWS = [
    ("participant_role", "你现在负责什么？", "例如 产品负责人 / 算法工程师 / 创始人 / 运营负责人"),
    ("current_evaluation_method", "你现在怎么判断哪个 agent、工作流或策略更靠谱？", "一句话即可"),
    ("candidate_count", "你通常要比较几个候选方案？", "填写数字，例如 3"),
    ("understanding_score", "听完后，你能否用自己的话说清 SAEE 是做什么的？", "1-5 分，5 表示非常清楚"),
    ("decision_influence_score", "这个结果会不会影响你部署、暂缓或重测的决定？", "1-5 分"),
    ("willing_to_test_own_candidates", "你愿不愿意用自己的候选方案再测一次？", "true/false"),
    ("top_objection", "你最大的疑问是什么？", "一句话"),
    ("evidence_missing", "还缺什么证据，你才更愿意继续试？", "一句话"),
]

BOUNDARY_ROWS = [
    ("no_private_core_disclosed", "没有披露 SAEE 私有核心"),
    ("no_production_ready_claim_made", "没有声称 SAEE 已生产可用"),
    ("no_customer_data_uploaded", "没有要求客户上传真实业务数据"),
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


def build_payload() -> dict[str, Any]:
    preflight = read_json(PREFLIGHT)
    return {
        "customer_validation_3_minute_worksheet_v0_1": True,
        "worksheet_type": "plain_chinese_3_minute_customer_validation_capture",
        "status": "ready_for_short_real_external_customer_interview_input",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "minimum_question_count": len(QUESTION_ROWS),
        "boundary_confirmation_count": len(BOUNDARY_ROWS),
        "required_full_answer_sheet_missing_field_count": preflight.get("missing_field_count"),
        "full_answer_sheet_still_required": True,
        "target_human_answer_input": rel(ANSWER_INPUT),
        "target_session_entry": rel(TARGET_ENTRY),
        "current_preflight_status": preflight.get("status"),
        "ready_for_explicit_apply_request": False,
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
        "blockers_closed_by_worksheet": 0,
    }


def question_table() -> str:
    rows = ["| 字段 | 直接问对方的话 | 怎么填 |", "| --- | --- | --- |"]
    rows.extend(f"| `{field}` | {question} | {hint} |" for field, question, hint in QUESTION_ROWS)
    return "\n".join(rows)


def boundary_table() -> str:
    rows = ["| 字段 | 必须确认 | 怎么填 |", "| --- | --- | --- |"]
    rows.extend(f"| `{field}` | {label} | 成立才填 `true` |" for field, label in BOUNDARY_ROWS)
    return "\n".join(rows)


def answer_stub() -> str:
    lines = [
        "```text",
        "# Short capture only. Copy into customer_validation_answers.human_filled.md, then complete the remaining full-answer fields.",
    ]
    for field, _question, _hint in QUESTION_ROWS:
        lines.append(f"{field}:")
    for field, _label in BOUNDARY_ROWS:
        lines.append(f"{field}:")
    lines.append("human_source_context: real external customer or target-user short interview")
    lines.append("human_entry_confirmed:")
    lines.append("```")
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)

    WORKSHEET.write_text(
        f"""# SAEE 3 分钟真实客户验证最小表 v0.1

用途：当你只有几分钟和真实外部客户或目标用户交流时，先用这张表判断：

- 对方是否听懂 SAEE；
- 对方是否真的有“多个 agent / 工作流 / 策略版本，部署前不知道哪个更稳”的问题；
- 对方是否愿意继续用自己的候选方案试一次。

这不是完整客户验证证据。它只能作为第一次真实访谈记录，不能直接把
`customer_validated` 改成 `true`。

## 3 分钟问题

{question_table()}

## 边界确认

{boundary_table()}

## 可复制的短答骨架

{answer_stub()}
""",
        encoding="utf-8",
    )

    FIELD_MAP.write_text(
        f"""# SAEE 3-Minute Customer Validation Field Map

This file maps the short Chinese interview questions to the larger customer
validation answer sheet. It is a friction-reduction surface only.

## Short Questions

{question_table()}

## Boundary Confirmations

{boundary_table()}

## Important Gap

The full answer sheet is still required before any import or customer
validation claim. Current preflight status: `{payload["current_preflight_status"]}`.
""",
        encoding="utf-8",
    )

    OUTPUT_GUIDE.write_text(
        f"""# SAEE 3-Minute Customer Validation Output Guide

After a real short interview:

1. Copy the short answer skeleton into `{rel(ANSWER_INPUT)}`.
2. Fill the remaining fields from the full answer template.
3. Run `python3 scripts/saee_customer_validation_answer_sheet_preflight.py`.
4. Continue only if preflight says `ready_for_explicit_apply_request=true`.

This short worksheet does not write `{rel(TARGET_ENTRY)}` and does not close
`customer_validated`.

customer_validation_3_minute_worksheet_v0_1: true
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_worksheet: 0
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE 3-Minute Customer Validation Boundary Audit

- Only a short human interview capture worksheet was generated.
- No customer was contacted by Codex.
- No external call was made.
- No customer data was collected.
- No final session-entry JSON was written.
- No customer validation claim was made.
- No production-ready claim was made.
- No runtime, backend, kernel, API schema, landing interaction, or private core was modified.

customer_validation_3_minute_worksheet_v0_1: true
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_worksheet: 0
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Customer Validation 3-Minute Worksheet Gate

answer: ready_for_short_real_external_customer_interview_input

reason: A short Chinese worksheet now exists to help a human capture the first
few minutes of real external customer or target-user feedback. It does not
replace the full customer-validation answer sheet and does not close the
`customer_validated` blocker.

boundary:
- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- blockers_closed_by_worksheet: 0

next_action: Use this only in a real external customer or target-user
conversation, then complete the full answer sheet before preflight/import.
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_field_map.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_output_guide.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_GATE.md",
        "/scripts/saee_customer_validation_3_minute_worksheet.py",
        "/scripts/saee_customer_validation_3_minute_worksheet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    agent_index = read_json(AGENT_INDEX)
    agent_index["customer_validation_3_minute_worksheet_v0_1"] = {
        "name": "SAEE 3-Minute Customer Validation Worksheet v0.1",
        "status": payload["status"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "minimum_question_count": payload["minimum_question_count"],
        "boundary_confirmation_count": payload["boundary_confirmation_count"],
        "required_full_answer_sheet_missing_field_count": payload[
            "required_full_answer_sheet_missing_field_count"
        ],
        "full_answer_sheet_still_required": payload["full_answer_sheet_still_required"],
        "target_human_answer_input": payload["target_human_answer_input"],
        "current_preflight_status": payload["current_preflight_status"],
        "ready_for_explicit_apply_request": payload["ready_for_explicit_apply_request"],
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
        "blockers_closed_by_worksheet": payload["blockers_closed_by_worksheet"],
        "entrypoints": {
            "summary": rel(SUMMARY),
            "worksheet": rel(WORKSHEET),
            "field_map": rel(FIELD_MAP),
            "output_guide": rel(OUTPUT_GUIDE),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_3_minute_worksheet.py",
            "smoke": "scripts/saee_customer_validation_3_minute_worksheet_smoke.py",
        },
    }
    write_json(AGENT_INDEX, agent_index)

    status_block = f"""## SAEE 3-Minute Customer Validation Worksheet v0.1

- `customer_validation_3_minute_worksheet_v0_1`
- Status: `{payload["status"]}`
- Current blocker: `customer_validated`
- Worksheet: `{rel(WORKSHEET)}`
- Full answer sheet still required: `{payload["full_answer_sheet_still_required"]}`
- `customer_validated=false`
- `production_ready=false`
- `private_core_exposed=false`
- `blockers_closed_by_worksheet=0`
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET_V0_1", status_block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_3_MINUTE_WORKSHEET: PASS "
        f"status={payload['status']} questions={payload['minimum_question_count']} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
