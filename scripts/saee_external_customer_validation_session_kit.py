#!/usr/bin/env python3
"""Build a human-run external customer validation session kit.

The kit translates the existing first-user feedback form and pilot result
template into a short Chinese interview script, a fillable feedback form, and a
field map for the existing customer-validation evidence JSON. It does not
contact customers, run pilots, collect data, execute evidence builders, close
blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
VALIDATION_DIR = ROOT / "phase_b_product/validation"
NEXT_ACTION = EVIDENCE_DIR / "external_customer_validation_next_action.local.json"
FEEDBACK_FORM = VALIDATION_DIR / "FIRST_USER_FEEDBACK_FORM.md"
PILOT_TEMPLATE = VALIDATION_DIR / "PILOT_RESULT_TEMPLATE.json"
CUSTOMER_TEMPLATE = EVIDENCE_DIR / "customer_validation_evidence_input.template.json"

OUTPUT_JSON = EVIDENCE_DIR / "external_customer_validation_session_kit.local.json"
OUTPUT_MD = EVIDENCE_DIR / "external_customer_validation_session_kit.md"
INTERVIEW_SCRIPT = EVIDENCE_DIR / "external_customer_validation_interview_script.md"
FEEDBACK_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_feedback_form.template.md"
FIELD_MAP = EVIDENCE_DIR / "external_customer_validation_field_mapping.csv"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_session_kit_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT_GATE.md"


FALSE_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "customer_contacted_by_codex": False,
    "automated_customer_contact": False,
    "customer_data_collected_by_codex": False,
    "customer_secrets_collected": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_builder_executed": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_session_kit": 0,
}


FIELD_MAPPING = [
    ("session_id", "会话编号", "由人工生成，例如 EXT-20260709-001"),
    ("session_date", "会话日期", "真实访谈或演示日期"),
    ("participant_role", "参与者角色", "例如 AI 平台负责人、产品负责人、工程负责人"),
    ("team_type", "团队类型", "例如 AI 平台团队、业务产品团队、研发团队"),
    ("current_evaluation_method", "当前评测方式", "现在如何比较 agent / workflow / policy"),
    ("candidate_count", "候选方案数量", "本次讨论中的 agent / 工作流 / 策略版本数量"),
    ("understanding_score", "理解分 1-5", "是否理解 SAEE 帮他做什么决策"),
    ("trust_score", "信任分 1-5", "是否愿意把结果带入部署评审"),
    ("decision_influence_score", "决策影响分 1-5", "是否影响部署/暂缓/重测判断"),
    ("repeat_usage_intent_score", "复用意愿分 1-5", "是否愿意用自己的候选方案继续测试"),
    ("time_to_value_minutes", "理解耗时", "从开始演示到理解价值的大概分钟数"),
    ("top_objection", "最大顾虑", "一句话记录最大阻碍"),
    ("evidence_missing", "缺失证据", "对方还需要什么证据才会信任"),
    ("willing_to_test_own_candidates", "是否愿意测自己的候选方案", "true/false"),
    ("notes", "备注", "只写摘要，不写秘密、源码、凭证、生产数据"),
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT: "
            f"FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT: "
            f"FAIL JSON root must be object: {rel(path)}"
        )
    return payload


def build_payload() -> dict[str, Any]:
    next_action = read_json(NEXT_ACTION)
    pilot_template = read_json(PILOT_TEMPLATE)
    customer_template = read_json(CUSTOMER_TEMPLATE)
    if next_action.get("current_goal_blocker") != "customer_validated":
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT: "
            "FAIL next action must target customer_validated"
        )
    sessions = customer_template.get("sessions", [])
    if not isinstance(sessions, list) or not sessions:
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT: "
            "FAIL customer validation template must contain sessions"
        )
    return {
        "external_customer_validation_session_kit_v0_1": True,
        "status": "ready_for_human_external_customer_validation_session",
        "kit_type": "manual_external_customer_validation_session_kit",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_external_customer_validation_session_kit.py",
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "source_next_action": rel(NEXT_ACTION),
        "source_first_user_feedback_form": rel(FEEDBACK_FORM),
        "source_pilot_result_template": rel(PILOT_TEMPLATE),
        "source_customer_validation_template": rel(CUSTOMER_TEMPLATE),
        "session_kit_ready": True,
        "interview_script_ready": True,
        "feedback_form_ready": True,
        "field_mapping_ready": True,
        "required_real_external_sessions_min": 1,
        "target_session_count": 1,
        "pilot_template_available": pilot_template.get("pilot_result_template_v0_1") is True,
        "customer_validation_template_available": customer_template.get("customer_validation_evidence_input_v0_1") is True,
        "existing_next_action_status": next_action.get("status"),
        "human_action_required": True,
        "codex_may_contact_customer": False,
        "codex_may_run_external_pilot": False,
        "codex_may_collect_customer_data": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_run_validator_after_human_filled_input": True,
        "customer_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "session_fields": [row[0] for row in FIELD_MAPPING],
        "field_mapping_count": len(FIELD_MAPPING),
        "next_human_action": (
            "Use the interview script and feedback form with one real external "
            "customer or target user, then transfer the answers into the existing "
            "customer-validation evidence template."
        ),
        **FALSE_FLAGS,
    }


def render_session_kit(payload: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Kit v0.1

Status: {payload['status']}.

This kit helps a human run one external customer or target-user validation
session for SAEE. It is not a validation result. It does not contact anyone,
execute a pilot, collect customer data through Codex, close blockers, launch
product, or claim production readiness.

## What To Use

- Interview script: `{rel(INTERVIEW_SCRIPT)}`
- Feedback form: `{rel(FEEDBACK_TEMPLATE)}`
- Field map: `{rel(FIELD_MAP)}`
- Existing evidence template: `{payload['source_customer_validation_template']}`

## Current State

```yaml
external_customer_validation_session_kit_v0_1: true
status: {payload['status']}
current_goal_blocker: customer_validated
remaining_blocker_count: 1
required_real_external_sessions_min: 1
session_kit_ready: true
customer_validated: false
production_ready: false
product_launched: false
customer_contacted_by_codex: false
private_core_exposed: false
blockers_closed_by_session_kit: 0
```

## Human Procedure

1. Human selects one real external customer or target user.
2. Human opens the SAEE demo or screenshots locally.
3. Human uses the interview script and feedback form.
4. Human records only summary feedback and scores. Do not collect secrets,
   source code, credentials, production data, or private workflow internals.
5. Human transfers the result into the existing customer-validation evidence
   JSON template.
6. Only after that, run the existing validator.

## Stop Rules

- Stop if the participant wants to upload production or secret data.
- Stop if private core details would need to be disclosed.
- Stop if anyone asks to claim SAEE is production-ready.
- Stop before publishing testimonials, case studies, or customer-validation
  claims.
"""


def render_interview_script() -> str:
    return """# SAEE External Customer Validation Interview Script

Use this script manually with one real external customer or target user.

## Opening

我们想验证一个问题：SAEE 是否能帮助你在上线前判断多个 AI agent、工作流或策略版本哪个更稳定、更值得部署。

本次不会收集你的源码、密钥、生产数据或客户数据。你可以只基于虚构或脱敏场景回答。

## Context Questions

1. 你的角色是什么？
2. 你的团队现在是否在使用 AI agent、自动化工作流或策略决策系统？
3. 你现在如何比较不同版本是否稳定？
4. 你最担心的上线风险是什么？

## Demo Questions

1. 你能否看懂 SAEE 给出的推荐对象、排名、信心和失败摘要？
2. 你是否理解“单次表现好”和“长期稳定”之间的区别？
3. 如果这是你的候选方案，SAEE 的结果会影响你部署、暂缓或重测的决定吗？
4. 哪个输出最有价值：推荐对象、排名、失败摘要、生存曲线、部署建议？
5. 你还需要什么证据才会信任这个结果？

## Score Questions

请给 1-5 分：

- 理解分：你是否理解 SAEE 帮你判断什么？
- 信任分：你是否愿意把结果带入部署评审？
- 决策影响分：它是否会影响上线/暂缓/重测？
- 复用意愿分：你是否愿意用自己的候选方案再测一次？

## Closing

1. 你最大的顾虑是什么？
2. 你是否愿意之后用一个脱敏候选方案继续测试？
3. 这更像你会自己本地用、线上试用、API 调用，还是私有部署？
"""


def render_feedback_template() -> str:
    return """# SAEE External Customer Validation Feedback Form Template

Do not record secrets, source code, credentials, production data, customer data,
or private workflow internals.

```text
session_id:
session_date:
participant_role:
team_type:
current_evaluation_method:
candidate_count:
saee_demo_surface_used:

understanding_score: 1-5
trust_score: 1-5
decision_influence_score: 1-5
repeat_usage_intent_score: 1-5
time_to_value_minutes:

top_objection:
evidence_missing:
willing_to_test_own_candidates: true/false
notes:
```

Boundary flags must remain false:

```yaml
secrets_collected: false
production_data_collected: false
customer_data_uploaded: false
private_core_disclosed: false
production_ready_claim_made: false
```

After human review, transfer the answers into:

`phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.human_filled.local.json`
"""


def render_boundary(payload: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Kit Boundary Audit

Final boundary decision: ready for human session preparation only.

- Runtime modified: {str(payload['runtime_modified']).lower()}
- Backend modified: {str(payload['backend_modified']).lower()}
- Kernel modified: {str(payload['kernel_modified']).lower()}
- API schema modified: {str(payload['api_schema_modified']).lower()}
- Private core exposed: {str(payload['private_core_exposed']).lower()}
- Product launched: {str(payload['product_launched']).lower()}
- Production ready: {str(payload['production_ready']).lower()}
- Customer validated: {str(payload['customer_validated']).lower()}
- Customer contacted by Codex: {str(payload['customer_contacted_by_codex']).lower()}
- Codex may contact customer: {str(payload['codex_may_contact_customer']).lower()}
- Codex may run external pilot: {str(payload['codex_may_run_external_pilot']).lower()}
- Codex may collect customer data: {str(payload['codex_may_collect_customer_data']).lower()}
- Evidence builder executed: {str(payload['evidence_builder_executed']).lower()}
- Blockers closed by session kit: {payload['blockers_closed_by_session_kit']}
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Session Kit Gate

answer: ready_for_human_external_customer_validation_session

reason: The remaining commercial blocker is `customer_validated`. This kit makes
one external customer or target-user validation session executable by a human
while preserving all no-contact, no-claim, no-production boundaries for Codex.

status: {payload['status']}
current_goal_blocker: customer_validated
required_real_external_sessions_min: 1
session_kit_ready: true
interview_script_ready: true
feedback_form_ready: true
field_mapping_ready: true

boundary:
codex_may_contact_customer: false
codex_may_run_external_pilot: false
codex_may_collect_customer_data: false
codex_may_infer_customer_feedback: false
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_session_kit: 0

next_action: Human runs one external customer or target-user session and fills
the existing customer-validation evidence template.
"""


def write_outputs(payload: dict[str, Any]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_session_kit(payload), encoding="utf-8")
    INTERVIEW_SCRIPT.write_text(render_interview_script(), encoding="utf-8")
    FEEDBACK_TEMPLATE.write_text(render_feedback_template(), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary(payload), encoding="utf-8")
    GATE.write_text(render_gate(payload), encoding="utf-8")
    with FIELD_MAP.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["json_field", "human_question", "fill_guidance"])
        writer.writerows(FIELD_MAPPING)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT: PASS "
        "status=ready_for_human_external_customer_validation_session "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
