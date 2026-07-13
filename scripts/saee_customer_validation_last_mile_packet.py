#!/usr/bin/env python3
"""Generate the last-mile customer validation handoff packet.

This packet compresses the remaining `customer_validated` blocker into one
human-readable question list, one compatible blank entry draft, and the exact
local commands to run after a real external customer or target-user session.
It does not contact customers, run sessions, infer feedback, or claim customer
validation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "customer_validation_last_mile_packet"
SUMMARY = OUT / "customer_validation_last_mile_packet.local.json"
PACKET_MD = OUT / "customer_validation_last_mile_packet.md"
QUESTIONS_MD = OUT / "customer_validation_required_questions.md"
BLANK_DRAFT = OUT / "external_customer_validation_session_entry.blank_draft.local.json"
BOUNDARY = OUT / "customer_validation_last_mile_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
MINIMUM_SESSION_FORM = (
    EVIDENCE_DIR / "external_customer_validation_minimum_session_packet/minimum_session_form.html"
)
MINIMUM_SESSION_QUESTIONS = (
    EVIDENCE_DIR / "external_customer_validation_minimum_session_packet/MINIMUM_SESSION_QUESTIONS.md"
)
REFERENCE_WORKBENCH = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.html"
TARGET_HUMAN_OUTPUT = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
POST_PROCESSOR = ROOT / "scripts/saee_external_customer_validation_post_session_processor.py"
NEXT_ACTION = EVIDENCE_DIR / "external_customer_validation_next_action.local.json"
CONVERGENCE = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit.local.json"

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


QUESTIONS = [
    ("session_id", "这次访谈的内部编号是什么？例如 ECV-001。"),
    ("session_date", "访谈日期是什么？格式 YYYY-MM-DD。"),
    ("human_reviewer_name", "谁完成并确认了这次访谈记录？"),
    ("participant_role", "对方是什么角色？例如 创始人、AI 产品负责人、算法工程师、运营负责人。"),
    ("team_type", "对方团队类型是什么？例如 初创团队、企业研发团队、个人开发者。"),
    ("current_evaluation_method", "对方现在如何评估 AI agent、工作流或策略版本？"),
    ("candidate_count", "对方通常需要比较几个 agent / workflow / policy 候选方案？"),
    ("understanding_score", "对方是否理解 SAEE 的用途？1-5 分。"),
    ("trust_score", "对方是否信任这个评测/推荐结果？1-5 分。"),
    ("decision_influence_score", "SAEE 是否会影响对方部署/暂缓/重测决策？1-5 分。"),
    ("repeat_usage_intent_score", "对方是否愿意之后继续使用或复测？1-5 分。"),
    ("time_to_value_minutes", "对方从开始体验到理解价值大约用了多少分钟？"),
    ("willing_to_test_own_candidates", "对方是否愿意用自己的候选方案再测一次？true/false。"),
    ("top_objection", "对方最大的疑问或反对意见是什么？"),
    ("evidence_missing", "对方认为还缺什么证据才更愿意采用？"),
    ("notes", "一句话记录对方最关键反馈。"),
]


def build_blank_draft(template: dict[str, Any]) -> dict[str, Any]:
    draft = json.loads(json.dumps(template, ensure_ascii=False))
    draft["human_entry_confirmed"] = False
    draft["human_reviewer_name"] = ""
    draft["human_source_context"] = (
        "Fill only after one real external customer or target-user validation session."
    )
    draft["review_date"] = ""
    draft["session"]["session_id"] = ""
    draft["session"]["session_date"] = ""
    draft["session"]["participant_role"] = ""
    draft["session"]["team_type"] = ""
    draft["session"]["current_evaluation_method"] = ""
    draft["session"]["candidate_count"] = 0
    draft["session"]["understanding_score"] = None
    draft["session"]["trust_score"] = None
    draft["session"]["decision_influence_score"] = None
    draft["session"]["repeat_usage_intent_score"] = None
    draft["session"]["time_to_value_minutes"] = None
    draft["session"]["willing_to_test_own_candidates"] = None
    draft["session"]["top_objection"] = ""
    draft["session"]["evidence_missing"] = ""
    draft["session"]["notes"] = ""
    return draft


def build_payload(template: dict[str, Any]) -> dict[str, Any]:
    next_action = read_json(NEXT_ACTION)
    convergence = read_json(CONVERGENCE)
    return {
        "customer_validation_last_mile_packet_v0_1": True,
        "packet_type": "human_external_customer_validation_last_mile_handoff",
        "status": "ready_for_real_external_customer_session_entry",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "recommended_form": rel(MINIMUM_SESSION_FORM),
        "recommended_questions": rel(MINIMUM_SESSION_QUESTIONS),
        "source_template": rel(TEMPLATE),
        "source_next_action": rel(NEXT_ACTION),
        "source_convergence_audit": rel(CONVERGENCE),
        "reference_result_entry_workbench": rel(REFERENCE_WORKBENCH),
        "target_human_output": rel(TARGET_HUMAN_OUTPUT),
        "post_session_processor_command": "python3 scripts/saee_external_customer_validation_post_session_processor.py",
        "required_question_count": len(QUESTIONS),
        "required_review_checkbox_count": len(template.get("evidence_review", {})),
        "required_boundary_confirmation_count": len(template.get("boundary_confirmation", {})),
        "current_actionable_blockers_after_local_human_evidence": convergence.get(
            "current_actionable_blockers_after_local_human_evidence"
        ),
        "human_session_entry_exists": TARGET_HUMAN_OUTPUT.exists(),
        "ready_for_post_session_processor": TARGET_HUMAN_OUTPUT.exists(),
        "codex_may_contact_customer": False,
        "codex_may_run_external_session": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_run_post_session_processor_after_human_file_exists": True,
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
        "blockers_closed_by_last_mile_packet": 0,
        "next_action_status": next_action.get("status"),
    }


def write_outputs(payload: dict[str, Any], template: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY, payload)
    write_json(BLANK_DRAFT, build_blank_draft(template))

    questions = ["# SAEE Customer Validation Required Questions", ""]
    questions.append("Use these questions only during a real external customer or target-user session.")
    questions.append("Do not answer them from internal self-review.")
    questions.append("")
    for index, (field, question) in enumerate(QUESTIONS, start=1):
        questions.append(f"{index}. `{field}` - {question}")
    questions.append("")
    questions.append("Boundary confirmations must remain true only if the session actually avoided secrets, production data, uploads, private-core disclosure, and production-ready claims.")
    QUESTIONS_MD.write_text("\n".join(questions) + "\n", encoding="utf-8")

    packet = f"""# SAEE Customer Validation Last-Mile Packet v0.1

Status: `{payload['status']}`.

Current blocker: `customer_validated`.

This packet is the shortest path from a real external customer or target-user
session to the existing local post-session processor. It does not run the
session, contact customers, infer feedback, close blockers, launch SAEE, or
claim production readiness.

## Use This Order

1. Run one real external customer or target-user session.
2. Ask the 12 minimum questions in:

`{payload['recommended_questions']}`

3. Open the locked minimum-session form:

`{payload['recommended_form']}`

4. Save the generated JSON exactly here:

`{payload['target_human_output']}`

5. Then run:

```bash
{payload['post_session_processor_command']}
python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py
python3 scripts/mainline_guard.py
```

## Current State

```yaml
customer_validation_last_mile_packet_v0_1: true
status: {payload['status']}
recommended_path_locked: true
recommended_path_id: minimum_session_packet
human_session_entry_exists: {str(payload['human_session_entry_exists']).lower()}
ready_for_post_session_processor: {str(payload['ready_for_post_session_processor']).lower()}
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_last_mile_packet: 0
```
"""
    PACKET_MD.write_text(packet, encoding="utf-8")

    boundary = f"""# SAEE Customer Validation Last-Mile Boundary Audit

customer_validation_last_mile_packet_v0_1: true
status: {payload['status']}

- codex_may_contact_customer: false
- codex_may_run_external_session: false
- codex_may_infer_customer_feedback: false
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
- blockers_closed_by_last_mile_packet: 0
"""
    BOUNDARY.write_text(boundary, encoding="utf-8")

    gate = f"""# SAEE Customer Validation Last-Mile Packet Gate

answer: ready_for_real_external_customer_session_entry

reason: The remaining current blocker is `customer_validated`; this packet gives
the human reviewer one compatible question list and output path for the existing
post-session processor.

boundary:
  recommended_path_locked: true
  recommended_path_id: minimum_session_packet
  customer_validated: false
  production_ready: false
  product_launched: false
  private_core_exposed: false
  blockers_closed_by_last_mile_packet: 0

next_action: Human must run a real external customer or target-user session and
save `{payload['target_human_output']}` before Codex runs the post-session processor.
"""
    GATE.write_text(gate, encoding="utf-8")

    for line in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_packet.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_packet.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_required_questions.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/external_customer_validation_session_entry.blank_draft.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_boundary_audit.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_GATE.md",
        "/scripts/saee_customer_validation_last_mile_packet.py",
        "/scripts/saee_customer_validation_last_mile_packet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["customer_validation_last_mile_packet_v0_1"] = {
        "name": "SAEE Customer Validation Last-Mile Packet v0.1",
        "status": payload["status"],
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "recommended_form": payload["recommended_form"],
        "recommended_questions": payload["recommended_questions"],
        "reference_result_entry_workbench": payload["reference_result_entry_workbench"],
        "target_human_output": payload["target_human_output"],
        "post_session_processor_command": payload["post_session_processor_command"],
        "required_question_count": payload["required_question_count"],
        "required_review_checkbox_count": payload["required_review_checkbox_count"],
        "required_boundary_confirmation_count": payload["required_boundary_confirmation_count"],
        "human_session_entry_exists": payload["human_session_entry_exists"],
        "ready_for_post_session_processor": payload["ready_for_post_session_processor"],
        "codex_may_contact_customer": False,
        "codex_may_run_external_session": False,
        "codex_may_infer_customer_feedback": False,
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
        "blockers_closed_by_last_mile_packet": 0,
        "entrypoints": {
            "summary": rel(SUMMARY),
            "packet": rel(PACKET_MD),
            "questions": rel(QUESTIONS_MD),
            "blank_draft": rel(BLANK_DRAFT),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_customer_validation_last_mile_packet.py",
            "smoke": "scripts/saee_customer_validation_last_mile_packet_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Customer Validation Last-Mile Packet v0.1

- `customer_validation_last_mile_packet_v0_1`
- Status: `{payload['status']}`
- Current blocker: `customer_validated`
- Required human output: `{payload['target_human_output']}`
- Recommended form: `{payload['recommended_form']}`
- Recommended questions: `{payload['recommended_questions']}`
- Reference-only legacy workbench: `{payload['reference_result_entry_workbench']}`
- `customer_validated=false`; `production_ready=false`; `private_core_exposed=false`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET_V0_1", block)


def main() -> None:
    template = read_json(TEMPLATE)
    payload = build_payload(template)
    write_outputs(payload, template)
    print(
        "SAEE_CUSTOMER_VALIDATION_LAST_MILE_PACKET: PASS "
        f"status={payload['status']} "
        f"questions={payload['required_question_count']} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
