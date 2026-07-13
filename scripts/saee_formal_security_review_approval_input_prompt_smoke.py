#!/usr/bin/env python3
"""Smoke test for the formal security review approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_formal_security_review_approval_input_prompt.py"
EVIDENCE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
)
OUTPUT_JSON = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "formal_security_review_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path}: {exc}")
    require(isinstance(value, dict), f"{path} must be object")
    return value


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        fail("runner failed")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "formal_security_review_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_formal_security_review_approval_input_prompt",
        "prompt_scope": "local_human_formal_security_review_input_prompt_only",
        "status": "hold_human_formal_security_review_input_required",
        "target_blocker_id": "formal_security_review",
        "category": "privacy_security",
        "validation_status": "pass",
        "builder_ready": False,
        "formal_security_review_available": False,
        "formal_security_review_approved": False,
        "formal_security_review_completed": False,
        "required_metadata_field_count": 5,
        "completed_metadata_field_count": 0,
        "required_formal_security_review_evidence_item_count": 7,
        "completed_formal_security_review_evidence_item_count": 0,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
        "source_formal_security_review_approval_input_prompt_html": (
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
            "formal_security_review_approval_input_prompt.html"
        ),
        "local_static_formal_security_review_approval_input_prompt_html": True,
        "browser_readable_formal_security_review_approval_input_prompt": True,
        "plain_language_formal_security_review_approval_input_prompt_v0_2": True,
        "formal_security_review_human_review_step_count": 5,
        "plain_language_status_label": "正式安全审查还没有完成，也不能声称安全已审。",
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "formal_security_review_approved_by_codex": False,
        "formal_security_review_completed_by_codex": False,
        "formal_security_review_report_approved_by_codex": False,
        "private_core_inspected_by_codex": False,
        "penetration_test_run_by_codex": False,
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "security_review_claim_published": False,
        "production_security_claim_published": False,
        "customer_data_processed": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    metadata = payload.get("metadata_fields_to_fill")
    require(isinstance(metadata, list), "metadata_fields_to_fill must be list")
    require(len(metadata) == 5, "metadata_fields_to_fill must have five fields")
    require(
        all(item.get("human_must_provide") is True for item in metadata),
        "metadata requires human input",
    )
    require(
        all(item.get("codex_may_fill") is False for item in metadata),
        "metadata codex_may_fill false",
    )

    keys = payload.get("formal_security_review_keys_to_review")
    require(isinstance(keys, list), "formal_security_review_keys_to_review must be list")
    require(len(keys) == 7, "formal_security_review_keys_to_review must have seven keys")
    require(
        all(item.get("codex_may_fill") is False for item in keys),
        "security review keys codex_may_fill false",
    )
    require(
        all(item.get("human_source_note_required") is True for item in keys),
        "security review source notes required",
    )
    require(
        all(item.get("review_artifact_required") is True for item in keys),
        "security review artifacts required",
    )
    require(
        all(item.get("owner_named_required") is True for item in keys),
        "security review owner name required",
    )
    require(
        all(item.get("reviewed_by_human_required") is True for item in keys),
        "security review human review required",
    )

    require(
        "formal_security_review_evidence_input.template.json"
        in payload.get("copy_template_command", ""),
        "copy command missing template",
    )
    require(
        "formal_security_review_evidence_input.human_filled.local.json"
        in payload.get("copy_template_command", ""),
        "copy command missing human input",
    )
    require(
        "saee_formal_security_review_approval_input_validator.py"
        in payload.get("validator_command", ""),
        "validator command missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "formal_security_review_approval_input_prompt_v0_1: true",
            "status: hold_human_formal_security_review_input_required",
            "target_blocker_id: formal_security_review",
            "source_formal_security_review_approval_input_prompt_html: phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_prompt.html",
            "local_static_formal_security_review_approval_input_prompt_html: true",
            "browser_readable_formal_security_review_approval_input_prompt: true",
            "plain_language_formal_security_review_approval_input_prompt_v0_2: true",
            "formal_security_review_human_review_step_count: 5",
            "plain_language_status_label: 正式安全审查还没有完成，也不能声称安全已审。",
            "required_metadata_field_count: 5",
            "required_formal_security_review_evidence_item_count: 7",
            "builder_ready: false",
            "formal_security_review_available: false",
            "formal_security_review_approved: false",
            "formal_security_review_completed: false",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "answer: recommend",
        "recommend_for_human_formal_security_review_input_prompt: true",
        "recommend_for_security_review_approval_by_codex: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_security_review_execution: false",
        "recommend_for_private_core_inspection: false",
        "recommend_for_penetration_test: false",
        "recommend_for_blocker_closure: false",
            "recommend_for_production: false",
    ]:
        require(token in gate, f"gate missing {token}")

    for token in [
        "<title>SAEE 正式安全审查人工审批入口</title>",
        "先完成安全审查，再谈正式商用。",
        "正式安全审查还没有完成，也不能声称安全已审。",
        "正式安全审查完成</span><code>false</code>",
        "Codex 执行安全审查</span><code>false</code>",
        "渗透测试已运行</span><code>false</code>",
        "私有核心已查看</span><code>false</code>",
        "生产可用</span><code>false</code>",
        "关闭 blocker</span><code>0</code>",
        "复制模板",
        "人工填写后验证",
        "不能越过的边界",
        "不联系安全审查方或供应商。",
        "不运行扫描、渗透测试或外部安全服务。",
        "不检查、不公开、不复制私有核心。",
        "不声称安全审查完成或生产可用。",
    ]:
        require(token in html, f"html missing {token}")

    forbidden = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "<form",
        "https://",
        "http://",
        "mailto:",
        "正式安全审查完成</span><code>true</code>",
        "Codex 执行安全审查</span><code>true</code>",
        "渗透测试已运行</span><code>true</code>",
        "私有核心已查看</span><code>true</code>",
        "生产可用</span><code>true</code>",
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "formal_security_review_available: true",
        '"formal_security_review_available": true',
        "formal_security_review_approved: true",
        '"formal_security_review_approved": true',
        "formal_security_review_completed: true",
        '"formal_security_review_completed": true',
        "builder_ready: true",
        '"builder_ready": true',
        "private_core_inspected_by_codex: true",
        '"private_core_inspected_by_codex": true',
        "penetration_test_run_by_codex: true",
        '"penetration_test_run_by_codex": true',
        "customer_data_processed: true",
        '"customer_data_processed": true',
        "recommend_for_security_review_approval_by_codex: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_security_review_execution: true",
        "recommend_for_private_core_inspection: true",
        "recommend_for_penetration_test: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    combined = "\n".join([json.dumps(payload), markdown, html, top_doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
