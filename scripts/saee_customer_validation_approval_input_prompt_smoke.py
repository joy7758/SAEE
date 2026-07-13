#!/usr/bin/env python3
"""Smoke check for the customer validation approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/saee_customer_validation_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
PROMPT_JSON = EVIDENCE_DIR / "customer_validation_approval_input_prompt.local.json"
PROMPT_MD = EVIDENCE_DIR / "customer_validation_approval_input_prompt.md"
PROMPT_HTML = EVIDENCE_DIR / "customer_validation_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: "
            + message
        )


def main() -> None:
    require(SCRIPT.exists(), "prompt script missing")
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, text=True)
    for path in [PROMPT_JSON, PROMPT_MD, PROMPT_HTML, TOP_DOC, GATE]:
        require(path.exists(), f"{path} missing")

    prompt = json.loads(PROMPT_JSON.read_text(encoding="utf-8"))
    expected = {
        "customer_validation_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_customer_validation_approval_input_prompt",
        "prompt_scope": "local_human_customer_validation_input_prompt_only",
        "status": "hold_human_customer_validation_input_required",
        "target_blocker_ids": ["pilot_results", "customer_validated"],
        "category": "customer_validation",
        "source_customer_validation_approval_input_prompt_html": "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html",
        "local_static_customer_validation_approval_input_prompt_html": True,
        "browser_readable_customer_validation_approval_input_prompt": True,
        "plain_language_customer_validation_approval_input_prompt_v0_2": True,
        "customer_validation_human_review_step_count": 5,
        "plain_language_status_label": "客户验证还没有完成，也不能对外声称已验证。",
        "builder_ready": False,
        "pilot_results_recorded": False,
        "customer_validation_approved": False,
        "required_review_key_count": 25,
        "completed_review_key_count": 0,
        "required_session_text_field_count": 5,
        "required_session_score_field_count": 4,
        "required_session_boundary_false_key_count": 5,
        "completed_session_count": 0,
        "human_review_required": True,
        "separate_validator_run_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_validator": False,
        "ready_for_evidence_builder": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "codex_contacted_customer": False,
        "codex_executed_pilot": False,
        "codex_inferred_missing_results": False,
        "codex_collected_customer_data": False,
        "automated_customer_contact": False,
        "customer_data_collected": False,
        "customer_secrets_collected": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"prompt {key} must be {value}")

    require(
        len(prompt.get("review_keys_to_set_after_human_approval", [])) == 25,
        "review key count changed",
    )
    require(
        len(prompt.get("session_text_fields_to_fill", [])) == 5,
        "session text field count changed",
    )
    require(
        len(prompt.get("session_score_fields_to_fill", [])) == 4,
        "session score field count changed",
    )
    for item in prompt["review_keys_to_set_after_human_approval"]:
        require(item.get("codex_may_fill") is False, "review keys codex_may_fill false")
        require(
            item.get("set_evidence_review_to_true_only_after_human_approval") is True,
            "review keys require human approval",
        )

    prompt_html = PROMPT_HTML.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [PROMPT_MD, TOP_DOC, GATE]
    )
    for token in [
        "customer_validation_approval_input_prompt_v0_1: true",
        "status: hold_human_customer_validation_input_required",
        "target_blocker_ids: pilot_results,customer_validated",
        "source_customer_validation_approval_input_prompt_html: phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html",
        "local_static_customer_validation_approval_input_prompt_html: true",
        "browser_readable_customer_validation_approval_input_prompt: true",
        "plain_language_customer_validation_approval_input_prompt_v0_2: true",
        "customer_validation_human_review_step_count: 5",
        "plain_language_status_label: 客户验证还没有完成，也不能对外声称已验证。",
        "required_review_key_count: 25",
        "required_session_text_field_count: 5",
        "required_session_score_field_count: 4",
        "required_session_boundary_false_key_count: 5",
        "completed_session_count: 0",
        "builder_ready: false",
        "pilot_results_recorded: false",
        "customer_validation_approved: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_customer_validation_input_prompt: true",
        "recommend_for_customer_contact: false",
        "recommend_for_pilot_execution: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_customer_validation_approval: false",
        "recommend_for_customer_validation_claim: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_testimonial_publication: false",
        "recommend_for_case_study_publication: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    for token in [
        "<title>SAEE 客户验证人工审批入口</title>",
        "先拿到真实试用反馈，再谈客户验证。",
        "客户验证还没有完成，也不能对外声称已验证。",
        "客户验证完成</span><code>false</code>",
        "Codex 联系客户</span><code>false</code>",
        "试点已执行</span><code>false</code>",
        "客户数据已收集</span><code>false</code>",
        "生产可用</span><code>false</code>",
        "关闭 blocker</span><code>0</code>",
        "复制本地模板",
        "人工填写后验证",
        "不能越过的边界",
        "不联系客户，不自动发邮件，不安排试点。",
    ]:
        require(token in prompt_html, "missing HTML token: " + token)

    for token in [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "builder_ready: true",
        '"builder_ready": true',
        "customer_contacted: true",
        "codex_contacted_customer: true",
        "codex_executed_pilot: true",
        "customer_data_collected: true",
        "public_validation_claim_published: true",
        "testimonial_published: true",
        "case_study_published: true",
        "recommend_for_customer_contact: true",
        "recommend_for_pilot_execution: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_customer_validation_approval: true",
        "recommend_for_customer_validation_claim: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_testimonial_publication: true",
        "recommend_for_case_study_publication: true",
    ]:
        require(token not in combined, "forbidden true claim present: " + token)

    for token in [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "<form",
        "https://",
        "http://",
        "mailto:",
        "客户验证完成</span><code>true</code>",
        "Codex 联系客户</span><code>true</code>",
        "试点已执行</span><code>true</code>",
        "客户数据已收集</span><code>true</code>",
        "生产可用</span><code>true</code>",
    ]:
        require(token not in prompt_html, "forbidden HTML token present: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_V0_1.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.html",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md",
        "/scripts/saee_customer_validation_approval_input_prompt.py",
        "/scripts/saee_customer_validation_approval_input_prompt_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("customer_validation_approval_input_prompt_v0_1", {})
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_CUSTOMER_VALIDATION_APPROVAL_INPUT_PROMPT_SMOKE: PASS "
        "status=hold_human_customer_validation_input_required "
        "builder_ready=false blockers_closed_by_prompt=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
