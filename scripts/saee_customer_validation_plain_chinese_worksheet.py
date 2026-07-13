#!/usr/bin/env python3
"""Generate a plain-Chinese worksheet for real customer validation.

The worksheet lowers the human entry barrier for the remaining
customer_validated blocker. It is a documentation/input surface only: it does
not contact customers, fill answers, write the final session-entry JSON, close
blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "customer_validation_plain_chinese_worksheet"
SUMMARY = OUT / "customer_validation_plain_chinese_worksheet.local.json"
WORKSHEET = OUT / "customer_validation_plain_chinese_worksheet.md"
FIELD_MAP = OUT / "customer_validation_plain_chinese_field_map.md"
OUTPUT_GUIDE = OUT / "customer_validation_plain_chinese_output_guide.md"
BOUNDARY = OUT / "customer_validation_plain_chinese_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_PLAIN_CHINESE_WORKSHEET_GATE.md"
ANSWER_TEMPLATE = EVIDENCE_DIR / "customer_validation_answer_intake_helper/customer_validation_answers.template.md"
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
    ("session_id", "这次访谈编号是什么？", "例如 ECV-001"),
    ("session_date", "访谈日期是哪一天？", "格式 YYYY-MM-DD"),
    ("human_reviewer_name", "谁负责记录和确认这次访谈？", "填写你的名字"),
    ("participant_role", "对方是什么角色？", "例如 AI 产品负责人、算法工程师、创始人、运营负责人"),
    ("team_type", "对方属于哪类团队？", "例如 初创团队、企业研发团队、个人开发者"),
    ("current_evaluation_method", "他们现在怎么判断哪个 agent / 工作流 / 策略更可靠？", "写一句话即可"),
    ("candidate_count", "他们通常需要比较几个候选方案？", "填写数字，必须大于 0"),
    ("understanding_score", "听完 SAEE 后，对方是否理解它解决什么问题？", "1-5 分，5 表示非常理解"),
    ("trust_score", "对方是否信任这个评测和推荐结果？", "1-5 分"),
    ("decision_influence_score", "这个结果是否会影响对方部署、暂缓或重测的决定？", "1-5 分"),
    ("repeat_usage_intent_score", "对方是否愿意之后继续使用或复测？", "1-5 分"),
    ("time_to_value_minutes", "对方从开始体验到理解价值大约用了几分钟？", "填写分钟数"),
    ("willing_to_test_own_candidates", "对方是否愿意用自己的候选方案再测一次？", "true/false"),
    ("top_objection", "对方最大的疑问或反对意见是什么？", "写一句话"),
    ("evidence_missing", "对方觉得还缺什么证据才更愿意采用？", "写一句话"),
    ("notes", "这次访谈最关键的一句话反馈是什么？", "写一句话"),
    ("human_source_context", "这条记录来自什么真实场景？", "例如 真实目标用户访谈，不是内部自评"),
    ("human_entry_confirmed", "你是否确认以上内容来自真实外部客户或目标用户会话？", "true/false"),
]

BOUNDARY_ROWS = [
    ("no_secrets_collected", "是否确认没有收集密码、密钥、客户秘密？"),
    ("no_production_data_collected", "是否确认没有收集生产数据？"),
    ("no_customer_data_uploaded", "是否确认没有要求客户上传真实业务数据？"),
    ("no_private_core_disclosed", "是否确认没有披露 SAEE 私有核心？"),
    ("no_production_ready_claim_made", "是否确认没有声称 SAEE 已生产可用？"),
]

EVIDENCE_REVIEW_ROWS = [
    ("real_customer_or_target_user_feedback_recorded", "确实记录了真实外部客户或目标用户反馈"),
    ("customer_role_and_segment_recorded", "记录了对方角色和团队类型"),
    ("customer_problem_fit_reviewed", "确认对方问题和 SAEE 适配场景有关"),
    ("recommendation_output_understood", "对方理解 SAEE 输出的推荐/排序含义"),
    ("decision_usefulness_observed", "观察到 SAEE 对部署/暂缓/重测决策有帮助"),
    ("deployment_decision_value_observed", "观察到部署前决策价值"),
    ("failure_summary_usefulness_observed", "观察到失败摘要有帮助"),
    ("pain_point_fit_observed", "观察到对方确有长期稳定性评测痛点"),
    ("feedback_form_completed", "访谈记录已填写完整"),
    ("negative_feedback_recorded", "负面反馈或疑问也已记录"),
    ("top_objection", "最大疑问已记录在 top_objection 字段"),
    ("evidence_missing", "缺失证据已记录在 evidence_missing 字段"),
    ("boundary_flags_reviewed", "已复核边界标记"),
    ("claim_scope_approved", "已确认没有扩大产品能力声明"),
    ("no_customer_secrets_collected", "未收集客户秘密"),
    ("no_customer_upload_required", "未要求客户上传真实业务数据"),
    ("no_private_core_disclosed", "未披露私有核心"),
    ("no_production_ready_claim_added", "未新增生产可用声明"),
    ("no_public_launch_claim_added", "未新增公开发布声明"),
    ("pilot_result_template_completed", "会话结果模板已完成"),
    ("pilot_result_reviewed_by_human", "会话结果已由人复核"),
    ("success_criteria_applied", "已按成功标准评估"),
    ("go_hold_pivot_decision_recorded", "已记录 go/hold/pivot 判断"),
    ("permission_to_use_feedback_recorded", "已记录是否允许使用反馈"),
    ("customer_validation_record_approved_by_human", "最终记录已由人确认"),
    ("reviewer_approved_validation_claim", "审查者确认可以如何表述验证结论"),
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
        "customer_validation_plain_chinese_worksheet_v0_1": True,
        "worksheet_type": "plain_chinese_real_customer_validation_worksheet",
        "status": "ready_for_real_external_customer_interview_input",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "question_count": len(QUESTION_ROWS),
        "boundary_confirmation_count": len(BOUNDARY_ROWS),
        "evidence_review_count": len(EVIDENCE_REVIEW_ROWS),
        "answer_template": rel(ANSWER_TEMPLATE),
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


def worksheet_table() -> str:
    rows = [
        "| 字段 | 要问人的话 | 填写建议 |",
        "| --- | --- | --- |",
    ]
    rows.extend(f"| `{field}` | {question} | {hint} |" for field, question, hint in QUESTION_ROWS)
    return "\n".join(rows)


def boundary_table() -> str:
    rows = [
        "| 字段 | 必须确认的边界 | 填写方式 |",
        "| --- | --- | --- |",
    ]
    rows.extend(f"| `{field}` | {question} | 只有事实成立才填 `true` |" for field, question in BOUNDARY_ROWS)
    return "\n".join(rows)


def review_table() -> str:
    rows = [
        "| 字段 | 人工复核项 | 填写方式 |",
        "| --- | --- | --- |",
    ]
    rows.extend(f"| `{field}` | {label} | 复核通过填 `true` |" for field, label in EVIDENCE_REVIEW_ROWS)
    return "\n".join(rows)


def answer_stub() -> str:
    lines = [
        "```text",
        "# Copy these lines into customer_validation_answers.human_filled.md after the real session.",
    ]
    for field, _question, _hint in QUESTION_ROWS:
        lines.append(f"{field}:")
    for field, _question in BOUNDARY_ROWS:
        lines.append(f"{field}:")
    for field, _label in EVIDENCE_REVIEW_ROWS:
        if field not in {"top_objection", "evidence_missing"}:
            lines.append(f"{field}: true")
    lines.append("```")
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)

    WORKSHEET.write_text(
        f"""# SAEE 真实客户验证中文填写表 v0.1

用途：把一次真实外部客户或目标用户访谈，整理成可导入的
`customer_validation_answers.human_filled.md`。

这不是内部自评表。只有真实外部客户或目标用户看过 SAEE、听懂用途并给出反馈后，才能填写。

## 访谈主问题

{worksheet_table()}

## 边界确认

{boundary_table()}

## 人工复核项

{review_table()}

## 可复制的答卷骨架

{answer_stub()}
""",
        encoding="utf-8",
    )

    FIELD_MAP.write_text(
        f"""# SAEE Customer Validation Plain Chinese Field Map

This file maps plain Chinese interview questions to the machine-readable answer
sheet fields. It is for human entry only and does not create customer
validation evidence by itself.

## Main Fields

{worksheet_table()}

## Boundary Fields

{boundary_table()}

## Evidence Review Fields

{review_table()}
""",
        encoding="utf-8",
    )

    OUTPUT_GUIDE.write_text(
        f"""# How To Produce The Human-Filled Answer Sheet

1. Run a real external customer or target-user conversation.
2. Use `{rel(WORKSHEET)}` as the Chinese interview worksheet.
3. Copy the answer skeleton into `{payload['target_human_answer_input']}`.
4. Fill every value from the real conversation.
5. Run:

```bash
python3 scripts/saee_customer_validation_answer_sheet_preflight.py
python3 scripts/saee_customer_validation_answer_sheet_preflight_smoke.py
```

Only when the preflight reports `ready_for_explicit_apply_request=true` should
you request a separate apply/import run.
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        f"""# SAEE Plain Chinese Customer Validation Worksheet Boundary Audit

customer_validation_plain_chinese_worksheet_v0_1: true
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
- blockers_closed_by_worksheet: 0

This worksheet lowers human entry friction only. It must not be used as a
claim that customer validation is complete.
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Plain Chinese Customer Validation Worksheet Gate

answer: ready_for_real_external_customer_interview_input

reason: A simpler Chinese worksheet can help a human collect real external customer or target-user evidence, but it does not perform the interview, contact customers, infer answers, close blockers, or claim production readiness.

boundary:
  customer_validated: false
  production_ready: false
  product_launched: false
  private_core_exposed: false
  blockers_closed_by_worksheet: 0

next_action: Use the worksheet in a real external session, then fill customer_validation_answers.human_filled.md and run the answer-sheet preflight.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_worksheet.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_worksheet.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_field_map.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_output_guide.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_PLAIN_CHINESE_WORKSHEET_GATE.md",
        "/scripts/saee_customer_validation_plain_chinese_worksheet.py",
        "/scripts/saee_customer_validation_plain_chinese_worksheet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["customer_validation_plain_chinese_worksheet_v0_1"] = {
        "name": "SAEE Plain Chinese Customer Validation Worksheet v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "question_count": payload["question_count"],
        "boundary_confirmation_count": payload["boundary_confirmation_count"],
        "evidence_review_count": payload["evidence_review_count"],
        "target_human_answer_input": payload["target_human_answer_input"],
        "current_preflight_status": payload["current_preflight_status"],
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
        "blockers_closed_by_worksheet": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "worksheet": rel(WORKSHEET),
            "field_map": rel(FIELD_MAP),
            "output_guide": rel(OUTPUT_GUIDE),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_plain_chinese_worksheet.py",
            "smoke": "scripts/saee_customer_validation_plain_chinese_worksheet_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Plain Chinese Customer Validation Worksheet v0.1

- `customer_validation_plain_chinese_worksheet_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Worksheet: `{rel(WORKSHEET)}`
- Target human answer input: `{payload['target_human_answer_input']}`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_PLAIN_CHINESE_WORKSHEET_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_CUSTOMER_VALIDATION_PLAIN_CHINESE_WORKSHEET: PASS "
        f"status={payload['status']} questions={payload['question_count']} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
